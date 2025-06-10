# models/evaluation_template_model.py
from datetime import datetime
import json

class EvaluationTemplate:
    def __init__(self, id, title, questions_set, batch=None, course_code=None,
                 last_date=None, admin_id=None, created_at=None, updated_at=None):
        self.id = id # This is AUTO_INCREMENT, so None for new
        self.title = title
        self.questions_set = questions_set # This will be a Python dict, stored as JSON
        self.batch = batch
        self.course_code = course_code
        self.last_date = last_date
        self.admin_id = admin_id
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an EvaluationTemplate object."""
        if not row:
            return None
        return EvaluationTemplate(
            id=row['id'],
            title=row['title'],
            questions_set=json.loads(row['questions_set']) if row['questions_set'] else {}, # Load JSON string to dict
            batch=row['batch'],
            course_code=row['course_code'],
            last_date=row['last_date'],
            admin_id=row['admin_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the EvaluationTemplate object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "questions_set": json.dumps(self.questions_set), # Dump dict to JSON string for DB
            "batch": self.batch,
            "course_code": self.course_code,
            "last_date": str(self.last_date) if self.last_date else None,
            "admin_id": self.admin_id,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }