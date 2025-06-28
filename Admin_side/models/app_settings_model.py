# Admin_side/models/app_settings_model.py
import dataclasses
from datetime import datetime

@dataclasses.dataclass
class AppSettings:
    """
    Represents application settings specific to an admin user.
    Simplified to only include auto-logout functionality.
    """
    admin_id: int # The ID of the admin user these settings belong to
    auto_logout_minutes: int # Duration in minutes after which inactive users are logged out

    # Timestamps for tracking creation and last update
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def from_db_row(row):
        """
        Converts a database row (dictionary) to an AppSettings object.
        """
        if not row:
            return None
        return AppSettings(
            admin_id=row['admin_id'],
            auto_logout_minutes=row['auto_logout_minutes'],
            created_at=row.get('created_at'), # Use .get() for optional fields
            updated_at=row.get('updated_at')  # Use .get() for optional fields
        )

    def to_dict(self):
        """
        Converts the AppSettings object to a dictionary, suitable for database operations
        or JSON serialization.
        """
        return {
            "admin_id": self.admin_id,
            "auto_logout_minutes": self.auto_logout_minutes,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }

