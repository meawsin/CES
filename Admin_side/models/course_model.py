# models/course_model.py
from datetime import datetime

class Course:
    def __init__(self, course_code, name, status, creation_date=None, updated_at=None):
        self.course_code = course_code
        self.name = name
        self.status = status
        self.creation_date = creation_date
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a Course object."""
        if not row:
            return None
        return Course(
            course_code=row['course_code'],
            name=row['name'],
            status=row['status'],
            creation_date=row['creation_date'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the Course object to a dictionary."""
        return {
            "course_code": self.course_code,
            "name": self.name,
            "status": self.status,
            "creation_date": str(self.creation_date) if self.creation_date else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }