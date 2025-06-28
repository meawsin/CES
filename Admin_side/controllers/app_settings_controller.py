# Admin_side/controllers/app_settings_controller.py
from database.db_manager import DBManager
from models.app_settings_model import AppSettings

class AppSettingsController:
    """
    Controller for managing application settings in the database.
    Now specifically handles auto-logout settings.
    """
    def __init__(self):
        self.db = DBManager()

    def get_admin_settings(self, admin_id):
        """
        Fetches application settings for a specific admin from the database.
        :param admin_id: The ID of the admin user.
        :return: An AppSettings object if settings are found, None otherwise.
        """
        query = "SELECT * FROM app_settings WHERE admin_id = %s;"
        settings_data = self.db.fetch_data(query, (admin_id,), fetch_one=True)
        if settings_data:
            return AppSettings.from_db_row(settings_data)
        return None # No custom settings found for this admin

    def save_admin_settings(self, settings: AppSettings):
        """
        Inserts a new application settings record or updates an existing one
        for a given admin.
        :param settings: An AppSettings object containing the settings to save.
        :return: A tuple (success_boolean, message_string).
        """
        # Check if settings already exist for this admin_id
        existing_settings = self.get_admin_settings(settings.admin_id)

        if existing_settings:
            # If settings exist, update them
            query = """
            UPDATE app_settings SET
                auto_logout_minutes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE admin_id = %s;
            """
            params = (settings.auto_logout_minutes, settings.admin_id)
            success = self.db.execute_query(query, params)
            if success:
                return True, "Settings updated successfully."
            else:
                return False, "Failed to update settings."
        else:
            # If no settings exist, insert new ones
            query = """
            INSERT INTO app_settings (admin_id, auto_logout_minutes)
            VALUES (%s, %s);
            """
            params = (settings.admin_id, settings.auto_logout_minutes)
            success = self.db.execute_query(query, params)
            if success:
                return True, "Settings saved successfully."
            else:
                return False, "Failed to save settings."

