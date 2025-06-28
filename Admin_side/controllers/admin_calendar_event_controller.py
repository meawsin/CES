from database.db_manager import DBManager
from models.admin_calendar_event_model import AdminCalendarEvent
from datetime import date

class AdminCalendarEventController:
    """
    Controller for managing administrative calendar events in the database.
    """
    def __init__(self):
        self.db = DBManager()

    def get_all_events(self, admin_id=None):
        """
        Fetches all calendar events, optionally filtered by admin_id.
        Events with admin_id NULL are considered general/public events.
        :param admin_id: Optional ID of the admin to filter events for.
        :return: A list of AdminCalendarEvent objects.
        """
        query = "SELECT * FROM admin_calendar_events"
        params = []
        if admin_id:
            # Fetch events created by this admin OR general events (admin_id IS NULL)
            query += " WHERE admin_id = %s OR admin_id IS NULL"
            params.append(admin_id)
        query += " ORDER BY event_date ASC;" # Order by date
        events_data = self.db.fetch_data(query, tuple(params), fetch_all=True)
        if events_data:
            return [AdminCalendarEvent.from_db_row(row) for row in events_data]
        return []

    def get_events_for_month(self, year, month, admin_id=None):
        """
        Fetches calendar events for a specific month, optionally filtered by admin_id.
        :param year: The year of the month to fetch events for.
        :param month: The month (1-12) to fetch events for.
        :param admin_id: Optional ID of the admin to filter events for.
        :return: A list of AdminCalendarEvent objects.
        """
        query = """
        SELECT * FROM admin_calendar_events
        WHERE YEAR(event_date) = %s AND MONTH(event_date) = %s
        """
        params = [year, month]
        if admin_id:
            # Fetch events created by this admin OR general events (admin_id IS NULL)
            query += " AND (admin_id = %s OR admin_id IS NULL)"
            params.append(admin_id)
        query += " ORDER BY event_date ASC;" # Order by date
        events_data = self.db.fetch_data(query, tuple(params), fetch_all=True)
        if events_data:
            return [AdminCalendarEvent.from_db_row(row) for row in events_data]
        return []

    def add_event(self, event: AdminCalendarEvent):
        """
        Adds a new calendar event to the database.
        :param event: An AdminCalendarEvent object to add.
        :return: True on success, False on failure.
        """
        query = """
        INSERT INTO admin_calendar_events (title, description, event_date, admin_id)
        VALUES (%s, %s, %s, %s);
        """
        params = (event.title, event.description, event.event_date, event.admin_id)
        return self.db.execute_query(query, params)

    def update_event(self, event: AdminCalendarEvent):
        """
        Updates an existing calendar event in the database.
        :param event: An AdminCalendarEvent object with updated details.
        :return: True on success, False on failure.
        """
        query = """
        UPDATE admin_calendar_events SET
            title = %s, description = %s, event_date = %s, admin_id = %s
        WHERE event_id = %s;
        """
        params = (event.title, event.description, event.event_date, event.admin_id, event.event_id)
        return self.db.execute_query(query, params)

    def delete_event(self, event_id):
        """
        Deletes a calendar event from the database by its ID.
        :param event_id: The ID of the event to delete.
        :return: True on success, False on failure.
        """
        query = "DELETE FROM admin_calendar_events WHERE event_id = %s;"
        return self.db.execute_query(query, (event_id,))

