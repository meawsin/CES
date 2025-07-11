# controllers/student_controller.py
from database.db_manager import DBManager
from models.student_model import Student
from models.faculty_model import Faculty
from models.complaint_model import Complaint # NEW: Import Complaint model
from models.course_model import Course # Import Course model to use in get_courses_by_status
import json # For handling JSON data for complaints etc.

class StudentController:
    def __init__(self):
        self.db = DBManager()

    def get_all_students(self):
        """Fetches all student records from the database."""
        query = "SELECT * FROM students ORDER BY name;"
        students_data = self.db.fetch_data(query, fetch_all=True)
        if students_data:
            return [Student.from_db_row(row) for row in students_data]
        return []

    def get_student_by_id(self, student_id):
        """Fetches a single student record by ID."""
        query = "SELECT * FROM students WHERE student_id = %s;"
        student_data = self.db.fetch_data(query, (student_id,), fetch_one=True)
        if student_data:
            return Student.from_db_row(student_data)
        return None

    def add_student(self, student: Student):
        """Inserts a new student record into the database."""
        query = """
        INSERT INTO students (student_id, name, email, password, contact_no, dob, gender, session, batch, enrollment_date, department, cgpa, behavioral_records, profile_picture)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            student.student_id, student.name, student.email, student.password, student.contact_no,
            student.dob, student.gender, student.session, student.batch, student.enrollment_date,
            student.department, student.cgpa, student.behavioral_records, student.profile_picture
        )
        return self.db.execute_query(query, params)

    def update_student(self, student: Student):
        """Updates an existing student record."""
        # This method is used internally by update_student_profile
        query = """
        UPDATE students SET
            name = %s, email = %s, password = %s, contact_no = %s, dob = %s, gender = %s,
            session = %s, batch = %s, enrollment_date = %s, department = %s, cgpa = %s,
            behavioral_records = %s, profile_picture = %s
        WHERE student_id = %s;
        """
        params = (
            student.name, student.email, student.password, student.contact_no,
            student.dob, student.gender, student.session, student.batch, student.enrollment_date,
            student.department, student.cgpa, student.behavioral_records, student.profile_picture,
            student.student_id
        )
        return self.db.execute_query(query, params)

    def delete_student(self, student_id):
        """Deletes a student record by ID."""
        query = "DELETE FROM students WHERE student_id = %s;"
        return self.db.execute_query(query, (student_id,))

    def get_total_batches_count(self):
        """Counts the total number of unique batches in the system."""
        query = "SELECT COUNT(DISTINCT batch) AS count FROM students WHERE batch IS NOT NULL;"
        result = self.db.fetch_data(query, fetch_one=True)
        return result['count'] if result else 0

    def get_unique_sessions(self):
        """Fetches all unique sessions from the database, ordered descending."""
        query = "SELECT DISTINCT session FROM students WHERE session IS NOT NULL ORDER BY session DESC;"
        sessions_data = self.db.fetch_data(query, fetch_all=True)
        return [row['session'] for row in sessions_data] if sessions_data else []

    def get_unique_departments(self):
        """Fetches all unique department names from the database, ordered alphabetically."""
        query = "SELECT DISTINCT department FROM students WHERE department IS NOT NULL ORDER BY department ASC;"
        departments_data = self.db.fetch_data(query, fetch_all=True)
        return [row['department'] for row in departments_data] if departments_data else []

    def get_unique_batches_with_departments(self):
        """
        Fetches all unique batches and their associated departments from the database.
        Returns a list of dictionaries like [{'batch': 'BICE-22', 'department': 'ICT'}].
        """
        query = "SELECT DISTINCT batch, department FROM students WHERE batch IS NOT NULL ORDER BY batch ASC;"
        batches_data = self.db.fetch_data(query, fetch_all=True)
        return batches_data if batches_data else []

    # --- Student API related methods ---
    def authenticate_student(self, student_id, password): # MODIFIED: Changed parameter to student_id
        """
        Authenticates a student user by student ID and password.
        :param student_id: The student's ID.
        :param password: The student's password.
        :return: A Student object if authentication is successful, None otherwise.
        """
        query = "SELECT * FROM students WHERE student_id = %s AND password = %s;" # MODIFIED: Query uses student_id
        student_data = self.db.fetch_data(query, (student_id, password), fetch_one=True)
        if student_data:
            print(f"Authentication successful for student ID: {student_id}")
            return Student.from_db_row(student_data)
        else:
            print(f"Authentication failed for student ID: {student_id}")
            return None

    def get_courses_for_student(self, student_id):
        """
        Retrieves all courses a student is assigned to, either individually or via batch.
        Returns a list of dictionaries with course_code and course_name.
        """
        query = """
        SELECT DISTINCT c.course_code, c.name
        FROM courses c
        JOIN course_student cs ON c.course_code = cs.course_code
        LEFT JOIN students s ON cs.student_id = s.student_id
        WHERE (cs.student_id = %s) OR (s.student_id = %s AND cs.student_id IS NULL AND s.batch = cs.batch);
        """
        data = self.db.fetch_data(query, (student_id, student_id), fetch_all=True)
        return data if data else []

    def get_faculty_for_course(self, course_code):
        """
        Retrieves all faculty members assigned to a specific course.
        Returns a list of dictionaries with faculty_id and name.
        """
        query = """
        SELECT f.faculty_id, f.name, f.email
        FROM faculty f
        JOIN course_faculty cf ON f.faculty_id = cf.faculty_id
        WHERE cf.course_code = %s;
        """
        data = self.db.fetch_data(query, (course_code,), fetch_all=True)
        return data if data else []

    # --- Profile and Evaluation History Methods for Web App ---
    def get_student_profile_data(self, student_id):
        """Fetches profile data for a specific student."""
        student = self.get_student_by_id(student_id)
        if student:
            # Return a dictionary suitable for JSON serialization
            profile_data = student.to_dict()
            # Remove sensitive data like password before sending to frontend
            profile_data.pop('password', None)
            return profile_data
        return None

    def update_student_profile(self, student_id, update_data):
        """
        Updates editable profile data for a student.
        Expected update_data keys: name, contact_no, profile_picture (optional)
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return False, "Student not found."

        # Update specific fields of the student object
        if 'name' in update_data:
            student.name = update_data['name']
        if 'contact_no' in update_data:
            student.contact_no = update_data['contact_no']
        if 'profile_picture' in update_data:
            student.profile_picture = update_data['profile_picture']
        
        # Call the existing update_student method to persist changes
        success = self.update_student(student)
        if success:
            return True, "Profile updated successfully."
        else:
            return False, "Failed to update profile. Database error."

    def get_completed_evaluations_for_student(self, student_id):
        """
        Fetches a list of evaluations completed by a specific student.
        Includes evaluation details like title, course, and submission date.
        """
        query = """
        SELECT ec.completion_date, et.title, et.course_code, et.id AS template_id, c.name AS course_name
        FROM evaluation_completion ec
        JOIN evaluation_templates et ON ec.template_id = et.id
        LEFT JOIN courses c ON et.course_code = c.course_code
        WHERE ec.student_id = %s AND ec.is_completed = TRUE
        ORDER BY ec.completion_date DESC;
        """
        completed_evals_data = self.db.fetch_data(query, (student_id,), fetch_all=True)
        
        results = []
        if completed_evals_data:
            for row in completed_evals_data:
                results.append({
                    "title": row['title'],
                    "course_code": row['course_code'] if row['course_code'] else "N/A",
                    "course_name": row['course_name'] if row['course_name'] else "N/A",
                    "completion_date": row['completion_date'].strftime("%Y-%m-%d %H:%M") if row['completion_date'] else "N/A",
                    "template_id": row['template_id']
                })
        return results

    def submit_complaint(self, student_id, course_code, issue_type, details):
        """
        Submits a new complaint from a student.
        """
        # Using the Complaint model to ensure data consistency
        new_complaint = Complaint(
            id=None, # Auto-increment
            student_id=student_id,
            course_code=course_code if course_code else None,
            issue_type=issue_type,
            details=details,
            status='pending' # Default status for new complaints
        )
        
        query = """
        INSERT INTO complaints (student_id, course_code, issue_type, details, status)
        VALUES (%s, %s, %s, %s, %s);
        """
        params = (
            new_complaint.student_id, new_complaint.course_code,
            new_complaint.issue_type, new_complaint.details, new_complaint.status
        )
        success = self.db.execute_query(query, params)
        if success:
            return True, "Complaint submitted successfully."
        else:
            return False, "Failed to submit complaint. Database error."

    def get_complaints_for_student(self, student_id):
        """
        Fetches all complaints submitted by a specific student.
        Returns a list of dicts with: issue_type, details, course_code, status.
        """
        query = """
            SELECT issue_type, details, course_code, status
            FROM complaints
            WHERE student_id = %s
            ORDER BY created_at DESC
        """
        data = self.db.fetch_data(query, (student_id,), fetch_all=True)
        return data if data else []

    def get_courses_by_status(self, status):
        """
        Fetches courses based on their status (e.g., 'upcoming').
        :param status: The status to filter by ('ongoing', 'finished', 'upcoming').
        :return: A list of Course objects.
        """
        query = "SELECT * FROM courses WHERE status = %s ORDER BY name;"
        courses_data = self.db.fetch_data(query, (status,), fetch_all=True)
        if courses_data:
            return [Course.from_db_row(row) for row in courses_data]
        return []

    def get_completed_evaluation_details(self, student_id, template_id, course_code):
        """
        Fetches the detailed feedback and comment for a specific completed evaluation.
        Returns the feedback (answers) and general comment for the evaluation.
        """
        # Handle cases where course_code might be "N/A" or null
        if course_code == "N/A" or not course_code:
            # Query without course_code constraint for evaluations that might not have a specific course
            query = """
            SELECT feedback, comment
            FROM evaluations
            WHERE template_id = %s
            ORDER BY date DESC
            LIMIT 1;
            """
            eval_data = self.db.fetch_data(query, (template_id,), fetch_one=True)
        else:
            # Query with course_code constraint
            query = """
            SELECT feedback, comment
            FROM evaluations
            WHERE template_id = %s AND course_code = %s
            ORDER BY date DESC
            LIMIT 1;
            """
            eval_data = self.db.fetch_data(query, (template_id, course_code), fetch_one=True)
        
        if eval_data:
            # Parse the feedback JSON if it's stored as a string
            feedback = eval_data['feedback']
            if isinstance(feedback, str):
                try:
                    import json
                    feedback = json.loads(feedback)
                except json.JSONDecodeError:
                    feedback = {}
            
            return {
                "feedback": feedback,
                "comment": eval_data['comment']
            }
        return None

    def get_all_batches(self):
        """Fetches all unique batch names from the students table."""
        query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL AND batch != '' ORDER BY batch;"
        result = self.db.fetch_data(query, fetch_all=True)
        return [row['batch'] for row in result if row['batch']]
