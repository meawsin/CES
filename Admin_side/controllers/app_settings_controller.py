# controllers/app_settings_controller.py
from database.db_manager import DBManager
from models.app_settings_model import AppSettings

class AppSettingsController:
    def __init__(self):
        self.db = DBManager()

    def get_admin_settings(self, admin_id):
        """Fetches application settings for a specific admin."""
        query = "SELECT * FROM app_settings WHERE admin_id = %s;"
        settings_data = self.db.fetch_data(query, (admin_id,), fetch_one=True)
        if settings_data:
            return AppSettings.from_db_row(settings_data)
        return None # No custom settings found for this admin

    def save_admin_settings(self, settings: AppSettings):
        """Inserts or updates application settings for an admin."""
        # Check if settings already exist for this admin_id
        existing_settings = self.get_admin_settings(settings.admin_id)

        if existing_settings:
            # Update existing settings
            query = """
            UPDATE app_settings SET
                font_size = %s, theme = %s, auto_logout_minutes = %s
            WHERE admin_id = %s;
            """
            params = (settings.font_size, settings.theme, settings.auto_logout_minutes, settings.admin_id)
            success = self.db.execute_query(query, params)
            if success:
                return True, "Settings updated successfully."
            else:
                return False, "Failed to update settings."
        else:
            # Insert new settings
            query = """
            INSERT INTO app_settings (admin_id, font_size, theme, auto_logout_minutes)
            VALUES (%s, %s, %s, %s);
            """
            params = (settings.admin_id, settings.font_size, settings.theme, settings.auto_logout_minutes)
            success = self.db.execute_query(query, params)
            if success:
                return True, "Settings saved successfully."
            else:
                return False, "Failed to save settings."