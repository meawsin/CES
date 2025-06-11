# models/evaluation_model.py
import json
from datetime import datetime

class Evaluation:
    def __init__(self, id, course_code, template_id, feedback, comment=None, date=None):
        self.id = id # AUTO_INCREMENT, so None for new
        self.course_code = course_code
        self.template_id = template_id
        self.feedback = feedback # This will be a Python dict, stored as JSON
        self.comment = comment
        self.date = date

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an Evaluation object."""
        if not row:
            return None
        return Evaluation(
            id=row['id'],
            course_code=row['course_code'],
            template_id=row['template_id'],
            feedback=json.loads(row['feedback']) if row['feedback'] else {}, # Load JSON string to dict
            comment=row['comment'],
            date=row['date']
        )

    def to_dict(self):
        """Converts the Evaluation object to a dictionary."""
        return {
            "id": self.id,
            "course_code": self.course_code,
            "template_id": self.template_id,
            "feedback": json.dumps(self.feedback), # Dump dict to JSON string for DB
            "comment": self.comment,
            "date": str(self.date) if self.date else None
        }