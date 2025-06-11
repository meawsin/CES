# models/app_settings_model.py
from datetime import datetime

class AppSettings:
    def __init__(self, admin_id, font_size, theme, auto_logout_minutes, created_at=None, updated_at=None):
        self.admin_id = admin_id
        self.font_size = font_size
        self.theme = theme
        self.auto_logout_minutes = auto_logout_minutes
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an AppSettings object."""
        if not row:
            return None
        return AppSettings(
            admin_id=row['admin_id'],
            font_size=row['font_size'],
            theme=row['theme'],
            auto_logout_minutes=row['auto_logout_minutes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the AppSettings object to a dictionary."""
        return {
            "admin_id": self.admin_id,
            "font_size": self.font_size,
            "theme": self.theme,
            "auto_logout_minutes": self.auto_logout_minutes,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }