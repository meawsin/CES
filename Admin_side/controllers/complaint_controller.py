# controllers/complaint_controller.py
import datetime
from database.db_manager import DBManager
from models.complaint_model import Complaint # Assuming Complaint model is defined
from models.student_model import Student # For getting student names
from models.course_model import Course # For getting course names

class ComplaintController:
    """
    Controller for managing student complaints.
    Handles fetching, updating status, and adding admin comments.
    """
    def __init__(self):
        self.db = DBManager()

    def get_all_complaints(self, status=None):
        """
        Fetches all complaints from the database, optionally filtered by status.
        Includes joined data for student name and course name for display.
        :param status: Optional filter for complaint status ('pending', 'in_progress', 'resolved').
        :return: A list of dictionaries, each representing a complaint with joined data.
        """
        query = """
        SELECT c.id, c.student_id, s.name AS student_name, c.course_code, co.name AS course_name,
               c.issue_type, c.details, c.status, c.created_at, c.updated_at, c.admin_comments
        FROM complaints c
        LEFT JOIN students s ON c.student_id = s.student_id
        LEFT JOIN courses co ON c.course_code = co.course_code
        WHERE 1=1
        """
        params = []
        if status:
            query += " AND c.status = %s"
            params.append(status)
        query += " ORDER BY c.created_at DESC;" # Order by most recent complaints

        complaints_data = self.db.fetch_data(query, tuple(params), fetch_all=True)
        return complaints_data if complaints_data else [] # Returns list of dicts

    def get_complaint_by_id(self, complaint_id):
        """
        Fetches a single complaint record by its ID.
        Includes joined data for student name and course name.
        :param complaint_id: The ID of the complaint to fetch.
        :return: A dictionary representing the complaint if found, None otherwise.
        """
        query = """
        SELECT c.id, c.student_id, s.name AS student_name, c.course_code, co.name AS course_name,
               c.issue_type, c.details, c.status, c.created_at, c.updated_at, c.admin_comments
        FROM complaints c
        LEFT JOIN students s ON c.student_id = s.student_id
        LEFT JOIN courses co ON c.course_code = co.course_code
        WHERE c.id = %s;
        """
        complaint_data = self.db.fetch_data(query, (complaint_id,), fetch_one=True)
        return complaint_data # Returns a dict

    def update_complaint_status(self, complaint_id, new_status):
        """
        Updates the status of a specific complaint.
        Validates the new status against a predefined list.
        :param complaint_id: The ID of the complaint to update.
        :param new_status: The new status ('pending', 'in_progress', 'resolved').
        :return: A tuple (success_boolean, message_string).
        """
        valid_statuses = ['pending', 'in_progress', 'resolved']
        if new_status not in valid_statuses:
            return False, "Invalid status provided."

        query = "UPDATE complaints SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s;"
        success = self.db.execute_query(query, (new_status, complaint_id))
        if success:
            return True, "Complaint status updated successfully."
        else:
            return False, "Failed to update complaint status. Database error."

    def add_complaint_comment(self, complaint_id, admin_id, comment_text):
        """
        Appends a new comment from an admin to the `admin_comments` field of a complaint.
        Each comment is timestamped and includes the admin's ID.
        :param complaint_id: The ID of the complaint to add a comment to.
        :param admin_id: The ID of the admin adding the comment.
        :param comment_text: The content of the comment.
        :return: A tuple (success_boolean, message_string).
        """
        # Fetch current comments to append to, or start new if none exist
        current_complaint = self.get_complaint_by_id(complaint_id)
        if not current_complaint:
            return False, "Complaint not found."

        current_comments = current_complaint.get('admin_comments', '')
        # Format the new comment with timestamp and admin ID
        new_comment_entry = f"\n\n--- Comment by Admin {admin_id} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n{comment_text}"
        
        updated_comments = current_comments + new_comment_entry

        query = "UPDATE complaints SET admin_comments = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s;"
        success = self.db.execute_query(query, (updated_comments, complaint_id))

        if success:
            return True, "Comment added successfully."
        else:
            return False, "Failed to add comment. Database error."

