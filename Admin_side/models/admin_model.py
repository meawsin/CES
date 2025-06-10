class Admin:
    def __init__(self, admin_id, name, email, password, contact_no,
                 can_create_templates, can_view_reports, can_manage_users,
                 can_manage_courses, can_manage_complaints, created_at=None, updated_at=None):
        self.admin_id = admin_id
        self.name = name
        self.email = email
        self.password = password # In a real app, you'd hash this!
        self.contact_no = contact_no
        self.can_create_templates = can_create_templates
        self.can_view_reports = can_view_reports
        self.can_manage_users = can_manage_users
        self.can_manage_courses = can_manage_courses
        self.can_manage_complaints = can_manage_complaints
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an Admin object."""
        if not row:
            return None
        return Admin(
            admin_id=row['admin_id'],
            name=row['name'],
            email=row['email'],
            password=row['password'],
            contact_no=row['contact_no'],
            can_create_templates=row['can_create_templates'],
            can_view_reports=row['can_view_reports'],
            can_manage_users=row['can_manage_users'],
            can_manage_courses=row['can_manage_courses'],
            can_manage_complaints=row['can_manage_complaints'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the Admin object to a dictionary."""
        return {
            "admin_id": self.admin_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "contact_no": self.contact_no,
            "can_create_templates": self.can_create_templates,
            "can_view_reports": self.can_view_reports,
            "can_manage_users": self.can_manage_users,
            "can_manage_courses": self.can_manage_courses,
            "can_manage_complaints": self.can_manage_complaints,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }