# Admin_side/models/faculty_request_model.py
from datetime import datetime

class FacultyRequest:
    def __init__(self, request_id, student_id, course_code, requested_faculty_name,
                 details, status, admin_comment=None, created_at=None, updated_at=None):
        self.request_id = request_id # AUTO_INCREMENT, so None for new
        self.student_id = student_id
        self.course_code = course_code
        self.requested_faculty_name = requested_faculty_name
        self.details = details
        self.status = status
        self.admin_comment = admin_comment
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a FacultyRequest object."""
        if not row:
            return None
        return FacultyRequest(
            request_id=row['request_id'],
            student_id=row['student_id'],
            course_code=row['course_code'],
            requested_faculty_name=row['requested_faculty_name'],
            details=row['details'],
            status=row['status'],
            admin_comment=row['admin_comment'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the FacultyRequest object to a dictionary."""
        return {
            "request_id": self.request_id,
            "student_id": self.student_id,
            "course_code": self.course_code,
            "requested_faculty_name": self.requested_faculty_name,
            "details": self.details,
            "status": self.status,
            "admin_comment": self.admin_comment,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }

