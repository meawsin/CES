# controllers/complaint_controller.py
import datetime
from database.db_manager import DBManager
from models.complaint_model import Complaint
from models.student_model import Student # For getting student names
from models.course_model import Course # For getting course names

class ComplaintController:
    def __init__(self):
        self.db = DBManager()

    def get_all_complaints(self, status=None):
        """Fetches all complaints, optionally filtered by status."""
        query = """
        SELECT c.id, c.student_id, s.name AS student_name, c.course_code, co.name AS course_name,
               c.issue_type, c.details, c.status, c.created_at, c.updated_at
        FROM complaints c
        LEFT JOIN students s ON c.student_id = s.student_id
        LEFT JOIN courses co ON c.course_code = co.course_code
        WHERE 1=1
        """
        params = []
        if status:
            query += " AND c.status = %s"
            params.append(status)
        query += " ORDER BY c.created_at DESC;"

        complaints_data = self.db.fetch_data(query, tuple(params), fetch_all=True)
        return complaints_data if complaints_data else [] # Return list of dicts with joined info

    def get_complaint_by_id(self, complaint_id):
        """Fetches a single complaint by ID."""
        query = """
        SELECT c.id, c.student_id, s.name AS student_name, c.course_code, co.name AS course_name,
               c.issue_type, c.details, c.status, c.created_at, c.updated_at
        FROM complaints c
        LEFT JOIN students s ON c.student_id = s.student_id
        LEFT JOIN courses co ON c.course_code = co.course_code
        WHERE c.id = %s;
        """
        complaint_data = self.db.fetch_data(query, (complaint_id,), fetch_one=True)
        return complaint_data # Returns a dict, not a Complaint object for simplicity here

    def update_complaint_status(self, complaint_id, new_status):
        """Updates the status of a complaint."""
        valid_statuses = ['pending', 'in_progress', 'resolved']
        if new_status not in valid_statuses:
            return False, "Invalid status provided."

        query = "UPDATE complaints SET status = %s WHERE id = %s;"
        success = self.db.execute_query(query, (new_status, complaint_id))
        if success:
            return True, "Complaint status updated successfully."
        else:
            return False, "Failed to update complaint status."

    def add_complaint_comment(self, complaint_id, admin_id, comment_text):
        """
        Adds a comment/update to a complaint.
        NOTE: Your schema doesn't have a dedicated `complaint_log` table.
              For now, we'll store comments as a new 'record' linked to the complaint,
              or update the 'details' field. A dedicated table would be better.
              For now, let's assume we're extending `details` or logging externally.
              Since the requirement mentioned "send comments, updates", a log table is ideal.
              Let's create a simple `complaint_log` table if it doesn't exist,
              otherwise, we need to adapt.

              For this iteration, let's just make a simple text update to `details`
              or add a basic `comments` column to the `complaints` table.
              Given the schema, the `details` column would be the primary place for updates.
              We'll add a new column for comments on the `complaints` table in the database
              if you intend for admins to add multiple discrete comments.
              For now, let's assume `details` gets appended or a new column is needed.

              **Let's refine the schema for `complaints` to have a `admin_comments` TEXT field.**
              If you update your DB: `ALTER TABLE complaints ADD COLUMN admin_comments TEXT DEFAULT NULL;`
              For now, I'll write the function assuming `details` is updated.
        """
        # Option 1: Append to existing 'details' (less ideal for history)
        # current_complaint = self.get_complaint_by_id(complaint_id)
        # if not current_complaint:
        #     return False, "Complaint not found."
        # new_details = f"{current_complaint['details']}\n\n--- Admin Comment by {admin_id} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n{comment_text}"
        # query = "UPDATE complaints SET details = %s WHERE id = %s;"
        # success = self.db.execute_query(query, (new_details, complaint_id))

        # Option 2: Ideal - use a separate `complaint_log` table
        # Requires adding a `complaint_log` table in your DB schema.
        # CREATE TABLE complaint_log (
        #     log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        #     complaint_id BIGINT,
        #     admin_id BIGINT,
        #     comment TEXT NOT NULL,
        #     log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        #     FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
        #     FOREIGN KEY (admin_id) REFERENCES admins(admin_id) ON DELETE SET NULL
        # );
        #
        # If this table exists:
        # query = "INSERT INTO complaint_log (complaint_id, admin_id, comment) VALUES (%s, %s, %s);"
        # success = self.db.execute_query(query, (complaint_id, admin_id, comment_text))
        # if success:
        #     return True, "Comment added successfully."
        # else:
        #     return False, "Failed to add comment."

        # Since we're sticking to the provided schema, let's assume comments are part of updating details
        # OR we'll implement a simple log here for demonstration, implying it would be stored in a new column.
        # For this version, let's just say this function would *prepare* the comment and require a DB update.
        # For simplicity, if you add `admin_comments` TEXT to `complaints` table:
        query = "UPDATE complaints SET admin_comments = CONCAT(IFNULL(admin_comments, ''), '\n\n--- Admin Comment by %s (%s) ---\n%s') WHERE id = %s;"
        success = self.db.execute_query(query, (admin_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment_text, complaint_id))

        if success:
            return True, "Comment added successfully."
        else:
            return False, "Failed to add comment."