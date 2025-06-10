# controllers/faculty_controller.py
from database.db_manager import DBManager
from models.faculty_model import Faculty

class FacultyController:
    def __init__(self):
        self.db = DBManager()

    def get_all_faculty(self):
        """Fetches all faculty records from the database."""
        query = "SELECT * FROM faculty ORDER BY name;"
        faculty_data = self.db.fetch_data(query, fetch_all=True)
        if faculty_data:
            return [Faculty.from_db_row(row) for row in faculty_data]
        return []

    def get_faculty_by_id(self, faculty_id):
        """Fetches a single faculty record by ID."""
        query = "SELECT * FROM faculty WHERE faculty_id = %s;"
        faculty_data = self.db.fetch_data(query, (faculty_id,), fetch_one=True)
        if faculty_data:
            return Faculty.from_db_row(faculty_data)
        return None

    def add_faculty(self, faculty: Faculty):
        """Inserts a new faculty record into the database."""
        query = """
        INSERT INTO faculty (faculty_id, name, email, password, contact_no, dob, gender, joining_date, profile_picture)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            faculty.faculty_id, faculty.name, faculty.email, faculty.password,
            faculty.contact_no, faculty.dob, faculty.gender, faculty.joining_date, faculty.profile_picture
        )
        return self.db.execute_query(query, params)

    def update_faculty(self, faculty: Faculty):
        """Updates an existing faculty record."""
        query = """
        UPDATE faculty SET
            name = %s, email = %s, password = %s, contact_no = %s, dob = %s, gender = %s,
            joining_date = %s, profile_picture = %s
        WHERE faculty_id = %s;
        """
        params = (
            faculty.name, faculty.email, faculty.password, faculty.contact_no,
            faculty.dob, faculty.gender, faculty.joining_date, faculty.profile_picture,
            faculty.faculty_id
        )
        return self.db.execute_query(query, params)

    def delete_faculty(self, faculty_id):
        """Deletes a faculty record by ID."""
        query = "DELETE FROM faculty WHERE faculty_id = %s;"
        return self.db.execute_query(query, (faculty_id,))