# Admin_side/controllers/evaluation_template_controller.py
from database.db_manager import DBManager
from models.evaluation_template_model import EvaluationTemplate
from models.evaluation_completion_model import EvaluationCompletion
from models.student_model import Student # To get student names for completion tracking
from models.course_model import Course # To get course names
from datetime import date # Import date for comparison
from datetime import datetime, timedelta # NEW for filtering by date

class EvaluationTemplateController:
    def __init__(self):
        self.db = DBManager()

    # --- Template Management ---
    def get_all_templates(self):
        """Fetches all evaluation templates."""
        query = "SELECT * FROM evaluation_templates ORDER BY title;"
        templates_data = self.db.fetch_data(query, fetch_all=True)
        if templates_data:
            return [EvaluationTemplate.from_db_row(row) for row in templates_data]
        return []

    def get_template_by_id(self, template_id):
        """Fetches a single template by ID."""
        query = "SELECT * FROM evaluation_templates WHERE id = %s;"
        template_data = self.db.fetch_data(query, (template_id,), fetch_one=True)
        if template_data:
            return EvaluationTemplate.from_db_row(template_data)
        return None

    def add_template(self, template: EvaluationTemplate):
        """Inserts a new evaluation template."""
        # 'id' is AUTO_INCREMENT, so omit it in the insert query
        query = """
        INSERT INTO evaluation_templates (title, questions_set, batch, course_code, session, last_date, admin_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            template.title, template.to_dict()['questions_set'], # Ensure JSON string
            template.batch, template.course_code, template.session, template.last_date, template.admin_id
        )
        return self.db.execute_query(query, params)

    def update_template(self, template: EvaluationTemplate):
        """Updates an existing evaluation template."""
        query = """
        UPDATE evaluation_templates SET
            title = %s, questions_set = %s, batch = %s, course_code = %s, session = %s,
            last_date = %s, admin_id = %s
        WHERE id = %s;
        """
        params = (
            template.title, template.to_dict()['questions_set'], # Ensure JSON string
            template.batch, template.course_code, template.session, template.last_date, template.admin_id,
            template.id
        )
        return self.db.execute_query(query, params)

    def delete_template(self, template_id):
        """Deletes an evaluation template."""
        query = "DELETE FROM evaluation_templates WHERE id = %s;"
        return self.db.execute_query(query, (template_id,))

    # --- New method for Dashboard ---
    def get_running_evaluations_count(self, admin_id=None):
        """
        Counts evaluation templates that are currently active (last_date is today or in the future)
        and are assigned to courses or batches relevant to the admin.
        For simplicity, we'll count templates with last_date >= today.
        A more complex logic would involve checking course status or batch active status.
        """
        query = """
        SELECT COUNT(DISTINCT id) AS count
        FROM evaluation_templates
        WHERE last_date >= CURDATE()
        """
        params = []
        if admin_id:
            # If an evaluation template has an admin_id, it's specific to that admin.
            # If admin_id is NULL, it's considered a general template visible to all or relevant to its course/batch.
            # We'll include templates either created by this admin OR general templates not tied to a specific admin.
            query += " AND (admin_id = %s OR admin_id IS NULL OR course_code IS NOT NULL)"
            params.append(admin_id) # The course_code IS NOT NULL part is to capture templates assigned to courses.

        result = self.db.fetch_data(query, tuple(params), fetch_one=True)
        return result['count'] if result else 0

    # --- Template Assignment and Completion Tracking (Existing methods) ---
    def assign_template_to_course_batch_session(self, template_id, course_code=None, batch=None, session=None, last_date=None, admin_id=None):
        """
        Assigns a template to a specific course, batch, or session.
        This effectively creates/updates the evaluation_templates entry for this specific assignment.
        A new template entry is created with the copied questions_set and assignment details.
        """
        source_template = self.get_template_by_id(template_id)
        if not source_template:
            return False, "Source template not found."

        # Construct title based on assignment type
        assignment_title_parts = [f"Assignment: {source_template.title}"]
        if course_code:
            assignment_title_parts.append(f"for Course {course_code}")
        if batch:
            assignment_title_parts.append(f"Batch {batch}")
        if session:
            assignment_title_parts.append(f"Session {session}")
        
        assignment_title = " ".join(assignment_title_parts)

        new_assignment = EvaluationTemplate(
            id=None, # Will be auto-generated by DB
            title=assignment_title,
            questions_set=source_template.questions_set, # Reusing the JSON questions set
            batch=batch,
            course_code=course_code,
            session=session, # Assign the session
            last_date=last_date, # This should be provided for an assignment
            admin_id=admin_id
        )
        success = self.add_template(new_assignment) # Use the add_template logic
        if success:
            return True, "Template assigned successfully."
        else:
            return False, "Failed to assign template."

    def get_template_completion_status(self, template_id, course_code):
        """
        Gets completion status for a specific template/course assignment.
        Returns total assigned students/batches, completed count, and list of non-completers (anonymized).
        """
        template_assignment = self.get_template_by_id(template_id)
        if not template_assignment:
            return None # Template assignment not found

        target_batch = template_assignment.batch
        target_course = template_assignment.course_code
        target_session = template_assignment.session # NEW: Use session if available

        all_relevant_student_ids = set()

        # Logic to find all students expected to complete this evaluation
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

            # Get students from batches assigned to this course
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
        # Note: evaluation_completion table has course_code and template_id.
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
        """Extends the last_date for a given template assignment."""
        query = "UPDATE evaluation_templates SET last_date = %s WHERE id = %s;"
        return self.db.execute_query(query, (new_date, template_id))

    # --- New methods for Ongoing/Past Evaluations sections ---
    def get_ongoing_evaluations(self):
        """Fetches evaluation templates that are currently active (last_date is today or in the future)."""
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
        """Fetches evaluation templates whose last_date has passed."""
        query = """
        SELECT * FROM evaluation_templates
        WHERE last_date < CURDATE() AND (course_code IS NOT NULL OR batch IS NOT NULL OR session IS NOT NULL)
        ORDER BY last_date DESC, title ASC;
        """
        templates_data = self.db.fetch_data(query, fetch_all=True)
        if templates_data:
            return [EvaluationTemplate.from_db_row(row) for row in templates_data]
        return []

