from datetime import datetime

class AdminCalendarEvent:
    def __init__(self, event_id, title, description, event_date, admin_id=None, created_at=None, updated_at=None):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.event_date = event_date
        self.admin_id = admin_id
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_db_row(row):
        """Converts a database row (dictionary) to an AdminCalendarEvent object."""
        if not row:
            return None
        return AdminCalendarEvent(
            event_id=row['event_id'],
            title=row['title'],
            description=row['description'],
            event_date=row['event_date'],
            admin_id=row['admin_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Converts the AdminCalendarEvent object to a dictionary."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "event_date": str(self.event_date) if self.event_date else None,
            "admin_id": self.admin_id,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }
