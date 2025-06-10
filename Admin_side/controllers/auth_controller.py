# controllers/auth_controller.py
from database.db_manager import DBManager
from models.admin_model import Admin
# from utils.helpers import hash_password, verify_password # Future use for actual password handling

class AuthController:
    def __init__(self):
        self.db = DBManager()

    def authenticate_admin(self, email, password):
        """
        Authenticates an admin user.
        In a real application, 'password' would be hashed and compared.
        """
        query = "SELECT * FROM admins WHERE email = %s AND password = %s;"

        admin_data = self.db.fetch_data(query, (email, password), fetch_one=True)
        if admin_data:
            print(f"Authentication successful for admin: {email}")
            return Admin.from_db_row(admin_data)
        else:
            print(f"Authentication failed for admin: {email}")
            return None

    def logout_admin(self):
        """Handles admin logout (e.g., clear session data if applicable)."""
        # For a desktop app, this might just mean clearing local state or returning to login
        print("Admin logged out.")
        return True