# controllers/student_controller.py
from database.db_manager import DBManager
from models.student_model import Student

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
        # Ensure student_id is handled (AUTO_INCREMENT or provided)
        # For auto-increment, you might omit student_id in INSERT and let DB assign
        # For the provided schema, student_id is explicitly given in populate, so we'll include it.
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

    # --- NEW METHOD FOR BATCH ASSIGNMENT ---
    def get_unique_batches_with_departments(self):
        """
        Fetches all unique batches and their associated departments from the database.
        Returns a list of dictionaries like [{'batch': 'BICE-22', 'department': 'ICT'}].
        """
        query = "SELECT DISTINCT batch, department FROM students WHERE batch IS NOT NULL ORDER BY batch ASC;"
        batches_data = self.db.fetch_data(query, fetch_all=True)
        return batches_data if batches_data else []
