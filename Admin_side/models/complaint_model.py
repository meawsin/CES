# models/complaint_model.py
from datetime import datetime

class Complaint:
    def __init__(self, id, student_id, course_code, issue_type, details, status, created_at=None, updated_at=None):
        self.id = id # AUTO_INCREMENT, so None for new
        self.student_id = student_id
        self.course_code = course_code
        self.issue_type = issue_type
        self.details = details
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a Complaint object."""
        if not row:
            return None
        return Complaint(
            id=row['id'],
            student_id=row['student_id'],
            course_code=row['course_code'],
            issue_type=row['issue_type'],
            details=row['details'],
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the Complaint object to a dictionary."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_code": self.course_code,
            "issue_type": self.issue_type,
            "details": self.details,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }