# models/course_faculty_model.py
from datetime import datetime

class CourseFaculty:
    def __init__(self, course_code, faculty_id, created_at=None):
        self.course_code = course_code
        self.faculty_id = faculty_id
        self.created_at = created_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a CourseFaculty object."""
        if not row:
            return None
        return CourseFaculty(
            course_code=row['course_code'],
            faculty_id=row['faculty_id'],
            created_at=row['created_at']
        )

    def to_dict(self):
        """Converts the CourseFaculty object to a dictionary."""
        return {
            "course_code": self.course_code,
            "faculty_id": self.faculty_id,
            "created_at": str(self.created_at) if self.created_at else None
        }