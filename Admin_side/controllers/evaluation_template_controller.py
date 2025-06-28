# Admin_side/controllers/evaluation_template_controller.py
from database.db_manager import DBManager
from models.evaluation_template_model import EvaluationTemplate
from models.evaluation_completion_model import EvaluationCompletion
from models.student_model import Student # Used for completion tracking logic
from models.course_model import Course # Used for course information
from models.admin_calendar_event_model import AdminCalendarEvent # NEW: Import for calendar event creation
from controllers.admin_calendar_event_controller import AdminCalendarEventController # NEW: Import for calendar controller
from datetime import date # For date comparisons
from datetime import datetime, timedelta # For date operations

class EvaluationTemplateController:
    """
    Controller for managing evaluation templates and their assignments.
    Now includes integration with AdminCalendarEventController for deadline events.
    """
    def __init__(self):
        self.db = DBManager()
        self.admin_calendar_event_controller = AdminCalendarEventController() # Initialize calendar controller

    # --- Template Management ---
    def get_all_templates(self):
        """
        Fetches all evaluation templates from the database.
        :return: A list of EvaluationTemplate objects.
        """
        query = "SELECT * FROM evaluation_templates ORDER BY title;"
        templates_data = self.db.fetch_data(query, fetch_all=True)
        if templates_data:
            return [EvaluationTemplate.from_db_row(row) for row in templates_data]
        return []

    def get_template_by_id(self, template_id):
        """
        Fetches a single template by its ID.
        :param template_id: The ID of the template to fetch.
        :return: An EvaluationTemplate object if found, None otherwise.
        """
        query = "SELECT * FROM evaluation_templates WHERE id = %s;"
        template_data = self.db.fetch_data(query, (template_id,), fetch_one=True)
        if template_data:
            return EvaluationTemplate.from_db_row(template_data)
        return None

    def add_template(self, template: EvaluationTemplate):
        """
        Inserts a new evaluation template into the database.
        If the template is an assignment (has course_code, batch, or session and last_date),
        a corresponding event is added to the admin calendar.
        :param template: The EvaluationTemplate object to add.
        :return: True on success, False on failure.
        """
        # 'id' is AUTO_INCREMENT, so omit it in the insert query
        query = """
        INSERT INTO evaluation_templates (title, questions_set, batch, course_code, session, last_date, admin_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        # Ensure questions_set is a JSON string for DB storage
        params = (
            template.title, template.to_dict()['questions_set'],
            template.batch, template.course_code, template.session, template.last_date, template.admin_id
        )
        success = self.db.execute_query(query, params)
        if success:
            # NEW: Add an event to the admin calendar for evaluation deadlines
            if template.last_date and (template.course_code or template.batch or template.session):
                event_title = f"Evaluation Deadline: {template.title}"
                event_description_parts = []
                if template.course_code:
                    event_description_parts.append(f"Course: {template.course_code}")
                if template.batch:
                    event_description_parts.append(f"Batch: {template.batch}")
                if template.session:
                    event_description_parts.append(f"Session: {template.session}")
                # Combine parts for a comprehensive description
                event_description = "Deadline for " + ", ".join(event_description_parts) + "." if event_description_parts else "General Evaluation Deadline."

                new_event = AdminCalendarEvent(
                    event_id=None, # Let DB auto-increment
                    title=event_title,
                    description=event_description,
                    event_date=template.last_date,
                    admin_id=template.admin_id # Associate with admin who created it
                )
                # Use the AdminCalendarEventController to add the event
                self.admin_calendar_event_controller.add_event(new_event)
            return True
        return False

    def update_template(self, template: EvaluationTemplate):
        """
        Updates an existing evaluation template in the database.
        Note: Updating a template's last_date will not automatically update
        an existing calendar event. This would require more complex logic
        (e.g., storing event_id in evaluation_templates or searching for events
        based on template_id/title and updating them). For simplicity, this is
        currently a manual process if the event needs updating.
        :param template: The EvaluationTemplate object with updated details.
        :return: True on success, False on failure.
        """
        query = """
        UPDATE evaluation_templates SET
            title = %s, questions_set = %s, batch = %s, course_code = %s, session = %s,
            last_date = %s, admin_id = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
        """
        # Ensure questions_set is a JSON string for DB storage
        params = (
            template.title, template.to_dict()['questions_set'],
            template.batch, template.course_code, template.session, template.last_date, template.admin_id,
            template.id
        )
        success = self.db.execute_query(query, params)
        if success:
            return True
        return False

    def delete_template(self, template_id):
        """
        Deletes an evaluation template from the database.
        Note: This does not automatically delete associated calendar events.
        A more robust solution would add `template_id` to `admin_calendar_events`
        for cascading deletes or manual deletion.
        :param template_id: The ID of the template to delete.
        :return: True on success, False on failure.
        """
        query = "DELETE FROM evaluation_templates WHERE id = %s;"
        success = self.db.execute_query(query, (template_id,))
        if success:
            return True
        return False

    def get_running_evaluations_count(self, admin_id=None):
        """
        Counts evaluation templates that are currently active (last_date is today or in the future)
        and are assigned to courses, batches, or sessions.
        This provides a quick metric for the dashboard.
        :param admin_id: Optional. Filters templates created by a specific admin or general ones.
        :return: The count of running evaluations.
        """
        query = """
        SELECT COUNT(DISTINCT id) AS count
        FROM evaluation_templates
        WHERE last_date >= CURDATE()
        AND (course_code IS NOT NULL OR batch IS NOT NULL OR session IS NOT NULL) -- Only count actual assignments
        """
        params = []
        if admin_id:
            # Include templates created by this admin, OR general templates (NULL admin_id),
            # OR templates assigned to a course/batch/session (which might not have an admin_id but are relevant).
            query += " AND (admin_id = %s OR admin_id IS NULL)" # Simplified for direct admin created or general
            # The previous OR clause (course_code IS NOT NULL) was causing a logical issue here;
            # A template relevant to *any* course should count for an admin if they can view it.
            # We assume "running evaluations" are system-wide unless tied explicitly to an admin's creation.
            # The current structure of EvaluationTemplate.admin_id links the creator.
            # So, if an admin is specified, we get their created ones, or system-wide (NULL admin_id) ones.
            params.append(admin_id)

        result = self.db.fetch_data(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0

    # --- Template Assignment and Completion Tracking (Existing methods) ---
    def assign_template_to_course_batch_session(self, template_id, course_code=None, batch=None, session=None, last_date=None, admin_id=None):
        """
        Assigns a template to a specific course, batch, or session by creating a new
        `evaluation_template` entry with specific assignment details.
        This effectively creates a 'copy' of the template linked to a context.
        :param template_id: The ID of the source template to assign.
        :param course_code: Optional course code for assignment.
        :param batch: Optional batch for assignment.
        :param session: Optional session for assignment.
        :param last_date: The deadline for this evaluation assignment.
        :param admin_id: The ID of the admin performing the assignment.
        :return: A tuple (success_boolean, message_string).
        """
        source_template = self.get_template_by_id(template_id)
        if not source_template:
            return False, "Source template not found."

        # Construct a descriptive title for the new assignment entry
        assignment_title_parts = [f"Assignment: {source_template.title}"]
        if course_code:
            assignment_title_parts.append(f"for Course {course_code}")
        if batch:
            assignment_title_parts.append(f"Batch {batch}")
        if session:
            assignment_title_parts.append(f"Session {session}")
        
        assignment_title = " ".join(assignment_title_parts)

        # Create a new EvaluationTemplate object representing this specific assignment
        new_assignment = EvaluationTemplate(
            id=None, # Will be auto-generated by DB
            title=assignment_title,
            questions_set=source_template.questions_set, # Reusing the JSON questions set from the source template
            batch=batch,
            course_code=course_code,
            session=session,
            last_date=last_date, # This should always be provided for an assignment
            admin_id=admin_id # Store the admin who made the assignment
        )
        # Use the add_template method which now handles calendar event creation
        success = self.add_template(new_assignment)
        if success:
            return True, "Template assigned successfully and event added to calendar."
        else:
            return False, "Failed to assign template. A database error might have occurred."

    def get_template_completion_status(self, template_id, course_code):
        """
        Gets completion status for a specific template/course assignment.
        Returns total expected students/batches, completed count, and list of non-completers (anonymized).
        This is crucial for tracking who has and hasn't completed an evaluation.
        :param template_id: The ID of the evaluation template assignment.
        :param course_code: The course code associated with this specific assignment.
        :return: A dictionary with completion statistics, or None if template not found.
        """
        template_assignment = self.get_template_by_id(template_id)
        if not template_assignment:
            return None # Template assignment not found

        target_batch = template_assignment.batch
        target_course = template_assignment.course_code
        target_session = template_assignment.session

        all_relevant_student_ids = set()

        # Logic to find all students expected to complete this evaluation based on assignment type
        if target_course: # If assigned to a specific course
            # Get individually assigned students to this course
            query_individual = """
            SELECT cs.student_id
            FROM course_student cs
            WHERE cs.course_code = %s AND cs.student_id IS NOT NULL;
            """
            individual_students = self.db.fetch_data(query_individual, (target_course,), fetch_all=True)
            if individual_students:
                for row in individual_students:
                    all_relevant_student_ids.add(row['student_id'])

            # Get students from batches assigned to this course (if any batches were assigned)
            query_batch_course = """
            SELECT s.student_id
            FROM students s
            JOIN course_student cs ON s.batch = cs.batch
            WHERE cs.course_code = %s AND cs.student_id IS NULL; -- Indicates a batch assignment
            """
            batch_students_in_course = self.db.fetch_data(query_batch_course, (target_course,), fetch_all=True)
            if batch_students_in_course:
                for row in batch_students_in_course:
                    all_relevant_student_ids.add(row['student_id'])

        elif target_batch: # If template is only assigned by batch (no specific course code)
            query_batch_only = "SELECT student_id FROM students WHERE batch = %s;"
            students_in_batch = self.db.fetch_data(query_batch_only, (target_batch,), fetch_all=True)
            if students_in_batch:
                for row in students_in_batch:
                    all_relevant_student_ids.add(row['student_id'])

        elif target_session: # If template is only assigned by session (no course/batch)
            query_session_only = "SELECT student_id FROM students WHERE session = %s;"
            students_in_session = self.db.fetch_data(query_session_only, (target_session,), fetch_all=True)
            if students_in_session:
                for row in students_in_session:
                    all_relevant_student_ids.add(row['student_id'])


        total_expected = len(all_relevant_student_ids)

        if total_expected == 0:
            return {
                "total_expected": 0,
                "completed_count": 0,
                "completion_percentage": 0.0,
                "non_completers": []
            }

        completed_student_ids = set()
        # Query for completed evaluations, matching by template_id and course_code (if present in assignment)
        completed_query = """
        SELECT student_id FROM evaluation_completion
        WHERE template_id = %s AND course_code = %s AND is_completed = TRUE;
        """
        # This assumes evaluation_completion records the course_code that the evaluation was completed FOR.
        # If an evaluation assigned to a session *doesn't* have a course_code in completion,
        # this logic needs adjustment. For now, we match existing structure.
        completed_data = self.db.fetch_data(completed_query, (template_id, course_code), fetch_all=True)
        if completed_data:
            for row in completed_data:
                completed_student_ids.add(row['student_id'])

        completed_count = len(completed_student_ids)
        completion_percentage = (completed_count / total_expected) * 100 if total_expected > 0 else 0.0

        non_completer_ids = list(all_relevant_student_ids - completed_student_ids)

        non_completers_info = []
        if non_completer_ids:
            # Fetch names and other relevant details for non-completers for the report
            placeholders = ', '.join(['%s'] * len(non_completer_ids))
            non_completer_query = f"""
            SELECT student_id, batch, department
            FROM students
            WHERE student_id IN ({placeholders});
            """
            info = self.db.fetch_data(non_completer_query, tuple(non_completer_ids), fetch_all=True)
            if info:
                non_completers_info = info


        return {
            "total_expected": total_expected,
            "completed_count": completed_count,
            "completion_percentage": completion_percentage,
            "non_completers": non_completers_info # List of dicts {student_id, batch, department}
        }

    def extend_template_deadline(self, template_id, new_date):
        """
        Extends the last_date for a given template assignment.
        :param template_id: The ID of the template assignment.
        :param new_date: The new deadline date.
        :return: True on success, False on failure.
        """
        query = "UPDATE evaluation_templates SET last_date = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s;"
        return self.db.execute_query(query, (new_date, template_id))

    # --- New methods for Ongoing/Past Evaluations sections ---
    def get_ongoing_evaluations(self):
        """
        Fetches evaluation templates that are currently active (last_date is today or in the future).
        These are typically assignments linked to a course, batch, or session.
        :return: A list of EvaluationTemplate objects representing ongoing evaluations.
        """
        query = """
        SELECT * FROM evaluation_templates
        WHERE last_date >= CURDATE() AND (course_code IS NOT NULL OR batch IS NOT NULL OR session IS NOT NULL)
        ORDER BY last_date ASC, title ASC;
        """
        templates_data = self.db.fetch_data(query, fetch_all=True)
        if templates_data:
            return [EvaluationTemplate.from_db_row(row) for row in templates_data]
        return []

    def get_past_evaluations(self):
        """
        Fetches evaluation templates whose last_date has passed.
        These are typically assignments linked to a course, batch, or session.
        :return: A list of EvaluationTemplate objects representing past evaluations.
        """
        query = """
        SELECT * FROM evaluation_templates
        WHERE last_date < CURDATE() AND (course_code IS NOT NULL OR batch IS NOT NULL OR session IS NOT NULL)
        ORDER BY last_date DESC, title ASC;
        """
        templates_data = self.db.fetch_data(query, fetch_all=True)
        if templates_data:
            return [EvaluationTemplate.from_db_row(row) for row in templates_data]
        return []

