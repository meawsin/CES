# models/student_model.py

class Student:
    def __init__(self, student_id, name, email, password, contact_no, dob, gender,
                 session, batch, enrollment_date, department, cgpa,
                 behavioral_records, profile_picture, created_at=None, updated_at=None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password = password # In a real app, hash this!
        self.contact_no = contact_no
        self.dob = dob
        self.gender = gender
        self.session = session
        self.batch = batch
        self.enrollment_date = enrollment_date
        self.department = department
        self.cgpa = cgpa
        self.behavioral_records = behavioral_records
        self.profile_picture = profile_picture
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to a Student object."""
        if not row:
            return None
        return Student(
            student_id=row['student_id'],
            name=row['name'],
            email=row['email'],
            password=row['password'],
            contact_no=row['contact_no'],
            dob=row['dob'],
            gender=row['gender'],
            session=row['session'],
            batch=row['batch'],
            enrollment_date=row['enrollment_date'],
            department=row['department'],
            cgpa=row['cgpa'],
            behavioral_records=row['behavioral_records'],
            profile_picture=row['profile_picture'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the Student object to a dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "contact_no": self.contact_no,
            "dob": str(self.dob) if self.dob else None, # Convert date to string for dictionary
            "gender": self.gender,
            "session": self.session,
            "batch": self.batch,
            "enrollment_date": str(self.enrollment_date) if self.enrollment_date else None,
            "department": self.department,
            "cgpa": float(self.cgpa) if self.cgpa else None,
            "behavioral_records": self.behavioral_records,
            "profile_picture": self.profile_picture,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }