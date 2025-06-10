# models/faculty_model.py
from datetime import datetime

class Faculty:
    def __init__(self, faculty_id, name, email, password, contact_no, dob, gender,
                 joining_date, profile_picture, created_at=None, updated_at=None):
        self.faculty_id = faculty_id
        self.name = name
        self.email = email
        self.password = password # Remember to hash this in a real application!
        self.contact_no = contact_no
        self.dob = dob
        self.gender = gender
        self.joining_date = joining_date
        self.profile_picture = profile_picture
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a Faculty object."""
        if not row:
            return None
        return Faculty(
            faculty_id=row['faculty_id'],
            name=row['name'],
            email=row['email'],
            password=row['password'],
            contact_no=row['contact_no'],
            dob=row['dob'],
            gender=row['gender'],
            joining_date=row['joining_date'],
            profile_picture=row['profile_picture'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the Faculty object to a dictionary."""
        return {
            "faculty_id": self.faculty_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "contact_no": self.contact_no,
            "dob": str(self.dob) if self.dob else None,
            "gender": self.gender,
            "joining_date": str(self.joining_date) if self.joining_date else None,
            "profile_picture": self.profile_picture,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }