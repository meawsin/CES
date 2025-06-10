# models/evaluation_completion_model.py
from datetime import datetime

class EvaluationCompletion:
    def __init__(self, id, template_id, course_code, student_id, is_completed, completion_date=None, created_at=None, updated_at=None):
        self.id = id # AUTO_INCREMENT, so None for new
        self.template_id = template_id
        self.course_code = course_code
        self.student_id = student_id
        self.is_completed = is_completed
        self.completion_date = completion_date
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an EvaluationCompletion object."""
        if not row:
            return None
        return EvaluationCompletion(
            id=row['id'],
            template_id=row['template_id'],
            course_code=row['course_code'],
            student_id=row['student_id'],
            is_completed=row['is_completed'],
            completion_date=row['completion_date'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the EvaluationCompletion object to a dictionary."""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "course_code": self.course_code,
            "student_id": self.student_id,
            "is_completed": self.is_completed,
            "completion_date": str(self.completion_date) if self.completion_date else None,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }