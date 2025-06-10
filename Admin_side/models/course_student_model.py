# models/course_student_model.py
from datetime import datetime

class CourseStudent:
    def __init__(self, course_code, student_id=None, batch=None, created_at=None):
        self.course_code = course_code
        self.student_id = student_id
        self.batch = batch
        self.created_at = created_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a CourseStudent object."""
        if not row:
            return None
        return CourseStudent(
            course_code=row['course_code'],
            student_id=row['student_id'],
            batch=row['batch'],
            created_at=row['created_at']
        )

    def to_dict(self):
        """Converts the CourseStudent object to a dictionary."""
        return {
            "course_code": self.course_code,
            "student_id": self.student_id,
            "batch": self.batch,
            "created_at": str(self.created_at) if self.created_at else None
        }