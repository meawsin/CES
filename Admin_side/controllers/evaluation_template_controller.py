# controllers/evaluation_template_controller.py
from database.db_manager import DBManager
from models.evaluation_template_model import EvaluationTemplate
from models.evaluation_completion_model import EvaluationCompletion
from models.student_model import Student # To get student names for completion tracking
from models.course_model import Course # To get course names

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
        INSERT INTO evaluation_templates (title, questions_set, batch, course_code, last_date, admin_id)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (
            template.title, template.to_dict()['questions_set'], # Ensure JSON string
            template.batch, template.course_code, template.last_date, template.admin_id
        )
        return self.db.execute_query(query, params)

    def update_template(self, template: EvaluationTemplate):
        """Updates an existing evaluation template."""
        query = """
        UPDATE evaluation_templates SET
            title = %s, questions_set = %s, batch = %s, course_code = %s,
            last_date = %s, admin_id = %s
        WHERE id = %s;
        """
        params = (
            template.title, template.to_dict()['questions_set'], # Ensure JSON string
            template.batch, template.course_code, template.last_date, template.admin_id,
            template.id
        )
        return self.db.execute_query(query, params)

    def delete_template(self, template_id):
        """Deletes an evaluation template."""
        query = "DELETE FROM evaluation_templates WHERE id = %s;"
        return self.db.execute_query(query, (template_id,))

    # --- Template Assignment and Completion Tracking ---
    def assign_template_to_course_batch(self, template_id, course_code, batch, last_date, admin_id):
        """
        Assigns a template to a specific course and batch.
        This effectively creates/updates the evaluation_templates entry for this specific assignment.
        NOTE: This design assumes `evaluation_templates` table holds assignments.
              If a separate `template_assignments` table was used (as suggested previously),
              the logic here would change to insert into that table.
              For now, we'll stick to the current schema where template definition
              and its assignment to a batch/course are linked in one record.
        """
        # Given the schema, this is effectively adding/updating the evaluation_template entry
        # rather than a separate assignment table.
        # So, it's more like editing a template's assignment details.
        # If the template_id implies a unique assignment, we'd update.
        # If it's a new assignment of an existing template, we'd insert a new template entry
        # with the same questions_set but different course/batch/date.

        # Let's assume for this method, we are creating a *new record* in evaluation_templates
        # which represents an assignment of a form for a specific course/batch.
        # This implies that "template_id" for an assignment might be a new auto-incremented ID,
        # even if questions_set is reused.

        # For the provided schema, 'id' is PK. If we insert, it gets a new ID.
        # If the idea is "one template questions_set can be assigned many times",
        # the schema needs 'template_id' (FK to master template) and 'assignment_id' (PK).
        # Currently, 'id' is PK, so each new 'assignment' creates a new 'template' record.

        # Let's clarify the intention:
        # A) One record in `evaluation_templates` is *the* template. It can only be assigned to ONE course/batch.
        # B) One record in `evaluation_templates` defines a specific *instance* of an evaluation (template + assignment).
        # C) There's a master `evaluation_form_definitions` table and `evaluation_templates` is the assignment table.

        # Based on your prompt "can assign same evaluation form for multiple courses, multiple batches"
        # and the schema: `evaluation_templates (id PK, ..., batch, course_code)`,
        # Option B seems implied where each row is an assignment. So reusing a "form" means copying questions_set.

        # Let's implement based on interpretation B: creating a new 'template' record for a new assignment.
        # The 'template_id' passed here would be None for a new assignment, and the `questions_set`
        # would come from a "master" template or be manually entered.

        # Given your schema, `admin_id` creates the template. `batch` and `course_code` define its scope.
        # `last_date` is its deadline.
        # To "assign same evaluation form for multiple courses, multiple batches" means creating new
        # `evaluation_templates` records, each with a different `batch` and/or `course_code`, but the same `questions_set`.

        # For this function, let's assume `template_id` is for an existing questions_set (or `None` for new).
        # We need to fetch the `questions_set` if `template_id` is provided and implies reusing a form.
        # If `template_id` from UI implies "this is a template I want to assign", then we need its questions_set.

        # For now, let's assume `questions_set` is provided directly for the assignment.
        # Admin selects a template (by ID), gets its questions_set, then specifies batch/course/date for a NEW entry.

        # Scenario: Admin wants to assign a template (e.g., ID 1) to Course X, Batch Y.
        # This implies a new entry in evaluation_templates with a new ID, Course X, Batch Y, and template 1's questions.

        # Function signature suggests we're creating a new assignment instance.
        # We need the actual questions_set content to insert.
        # Let's modify this to take `source_template_id` and create a new assignment record.

        # Placeholder logic based on interpretation B:
        # To assign template X to course Y, batch Z with deadline D:
        # 1. Fetch questions_set of template X.
        # 2. Create a NEW `evaluation_templates` record with new `id`, `questions_set` from X, `course_code` Y, `batch` Z, `last_date` D.

        # Let's use a more explicit function name like `create_template_assignment`.
        # This current `assign_template_to_course_batch` needs revision based on the actual UI flow.
        # For simplicity, let's assume `add_template` (above) covers creating a new template record
        # that *is* an assignment, by providing all its details.

        # If the request is to take an EXISTING template (by its ID) and apply it to a new course/batch:
        # 1. Fetch the existing template by `template_id`.
        source_template = self.get_template_by_id(template_id)
        if not source_template:
            return False, "Source template not found."

        # 2. Create a new EvaluationTemplate object with the same questions_set
        #    but new batch, course_code, last_date, and admin_id (and a new auto-incremented ID).
        new_assignment = EvaluationTemplate(
            id=None, # Will be auto-generated by DB
            title=f"Assignment: {source_template.title} for {course_code if course_code else ''} {batch if batch else ''}",
            questions_set=source_template.questions_set, # Reusing the JSON questions set
            batch=batch,
            course_code=course_code,
            last_date=last_date,
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
        # Determine all students expected to complete this template for this course/batch
        # This requires linking evaluation_templates (which has batch/course_code)
        # to students via course_student table.

        # First, find the specific template assignment by ID
        template_assignment = self.get_template_by_id(template_id)
        if not template_assignment:
            return None # Template assignment not found

        target_batch = template_assignment.batch
        target_course = template_assignment.course_code

        # Get all students who are associated with this course and/or batch
        # This query needs to account for students assigned individually OR by batch.
        # Assuming course_student contains unique student-course links or batch-course links.

        all_relevant_student_ids = set()

        if target_course:
            # Students assigned to this course directly
            query_individual = """
            SELECT cs.student_id
            FROM course_student cs
            WHERE cs.course_code = %s AND cs.student_id IS NOT NULL;
            """
            individual_students = self.db.fetch_data(query_individual, (target_course,), fetch_all=True)
            if individual_students:
                for row in individual_students:
                    all_relevant_student_ids.add(row['student_id'])

            # Students in batches assigned to this course
            query_batch = """
            SELECT s.student_id
            FROM students s
            JOIN course_student cs ON s.batch = cs.batch
            WHERE cs.course_code = %s AND cs.student_id IS NULL; -- Batch assignment indicator
            """
            batch_students = self.db.fetch_data(query_batch, (target_course,), fetch_all=True)
            if batch_students:
                for row in batch_students:
                    all_relevant_student_ids.add(row['student_id'])

        elif target_batch: # If template is only assigned by batch (no specific course code)
            query_batch_only = "SELECT student_id FROM students WHERE batch = %s;"
            students_in_batch = self.db.fetch_data(query_batch_only, (target_batch,), fetch_all=True)
            if students_in_batch:
                for row in students_in_batch:
                    all_relevant_student_ids.add(row['student_id'])


        total_expected = len(all_relevant_student_ids)

        if total_expected == 0:
            return {
                "total_expected": 0,
                "completed_count": 0,
                "completion_percentage": 0.0,
                "non_completers": []
            }

        # Get completed students for this template and course
        completed_student_ids = set()
        completed_query = """
        SELECT student_id FROM evaluation_completion
        WHERE template_id = %s AND course_code = %s AND is_completed = TRUE;
        """
        completed_data = self.db.fetch_data(completed_query, (template_id, course_code), fetch_all=True)
        if completed_data:
            for row in completed_data:
                completed_student_ids.add(row['student_id'])

        completed_count = len(completed_student_ids)
        completion_percentage = (completed_count / total_expected) * 100 if total_expected > 0 else 0.0

        # Identify non-completers (their IDs are needed for tracking, but names are anonymized)
        non_completer_ids = list(all_relevant_student_ids - completed_student_ids)

        # Fetch basic info for non-completers (e.g., student ID, batch, department - but NOT name)
        non_completers_info = []
        if non_completer_ids:
            # Create a string of placeholders for IN clause
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