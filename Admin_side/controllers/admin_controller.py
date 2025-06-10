# controllers/admin_controller.py
from database.db_manager import DBManager
from models.admin_model import Admin # Assuming Admin model is defined

class AdminController:
    def __init__(self):
        self.db = DBManager()

    def get_all_admins(self):
        """Fetches all admin records from the database."""
        query = "SELECT * FROM admins ORDER BY name;"
        admins_data = self.db.fetch_data(query, fetch_all=True)
        if admins_data:
            return [Admin.from_db_row(row) for row in admins_data]
        return []

    def get_admin_by_id(self, admin_id):
        """Fetches a single admin record by ID."""
        query = "SELECT * FROM admins WHERE admin_id = %s;"
        admin_data = self.db.fetch_data(query, (admin_id,), fetch_one=True)
        if admin_data:
            return Admin.from_db_row(admin_data)
        return None

    def add_admin(self, admin: Admin):
        """Inserts a new admin record into the database."""
        # Note: admin_id is AUTO_INCREMENT in DB, but example populate gives specific IDs
        # We'll include it if provided, otherwise rely on DB
        query = """
        INSERT INTO admins (admin_id, name, email, password, contact_no, can_create_templates, can_view_reports, can_manage_users, can_manage_courses, can_manage_complaints)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            admin.admin_id, admin.name, admin.email, admin.password, admin.contact_no,
            admin.can_create_templates, admin.can_view_reports, admin.can_manage_users,
            admin.can_manage_courses, admin.can_manage_complaints
        )
        return self.db.execute_query(query, params)

    def update_admin(self, admin: Admin):
        """Updates an existing admin record."""
        query = """
        UPDATE admins SET
            name = %s, email = %s, password = %s, contact_no = %s,
            can_create_templates = %s, can_view_reports = %s, can_manage_users = %s,
            can_manage_courses = %s, can_manage_complaints = %s
        WHERE admin_id = %s;
        """
        params = (
            admin.name, admin.email, admin.password, admin.contact_no,
            admin.can_create_templates, admin.can_view_reports, admin.can_manage_users,
            admin.can_manage_courses, admin.can_manage_complaints,
            admin.admin_id
        )
        return self.db.execute_query(query, params)

    def delete_admin(self, admin_id):
        """Deletes an admin record by ID."""
        query = "DELETE FROM admins WHERE admin_id = %s;"
        return self.db.execute_query(query, (admin_id,))