# Admin_side/controllers/faculty_request_controller.py
import datetime
from database.db_manager import DBManager
from models.faculty_request_model import FacultyRequest
from models.student_model import Student # For getting student names
from models.course_model import Course # For getting course names

class FacultyRequestController:
    """
    Controller for managing student requests for faculty.
    """
    def __init__(self):
        self.db = DBManager()

    def submit_faculty_request(self, student_id, course_code, requested_faculty_name, details):
        """
        Submits a new faculty request from a student.
        :param student_id: The ID of the student submitting the request.
        :param course_code: The code of the course the faculty is requested for.
        :param requested_faculty_name: The name of the faculty requested by the student (optional).
        :param details: Additional details from the student about the request.
        :return: A tuple (success_boolean, message_string).
        """
        # Create a FacultyRequest object (ID will be auto-incremented by DB)
        new_request = FacultyRequest(
            request_id=None,
            student_id=student_id,
            course_code=course_code,
            requested_faculty_name=requested_faculty_name,
            details=details,
            status='pending' # Default status for new requests
        )

        query = """
        INSERT INTO faculty_requests (student_id, course_code, requested_faculty_name, details, status)
        VALUES (%s, %s, %s, %s, %s);
        """
        params = (
            new_request.student_id, new_request.course_code,
            new_request.requested_faculty_name, new_request.details, new_request.status
        )
        success = self.db.execute_query(query, params)
        if success:
            return True, "Faculty request submitted successfully."
        else:
            return False, "Failed to submit faculty request. Database error."

    def get_all_faculty_requests(self, status=None):
        """
        Fetches all faculty requests, optionally filtered by status.
        Includes joined data for student name and course name for display.
        :param status: Optional filter for request status ('pending', 'approved', 'rejected').
        :return: A list of dictionaries, each representing a request with joined data.
        """
        query = """
        SELECT fr.request_id, fr.student_id, s.name AS student_name,
               fr.course_code, c.name AS course_name,
               fr.requested_faculty_name, fr.details, fr.status,
               fr.admin_comment, fr.created_at, fr.updated_at
        FROM faculty_requests fr
        LEFT JOIN students s ON fr.student_id = s.student_id
        LEFT JOIN courses c ON fr.course_code = c.course_code
        WHERE 1=1
        """
        params = []
        if status:
            query += " AND fr.status = %s"
            params.append(status)
        query += " ORDER BY fr.created_at DESC;" # Order by most recent requests

        requests_data = self.db.fetch_data(query, tuple(params), fetch_all=True)
        return requests_data if requests_data else [] # Returns list of dicts

    def get_faculty_request_by_id(self, request_id):
        """
        Fetches a single faculty request record by its ID.
        Includes joined data for student name and course name.
        :param request_id: The ID of the request to fetch.
        :return: A dictionary representing the request if found, None otherwise.
        """
        query = """
        SELECT fr.request_id, fr.student_id, s.name AS student_name,
               fr.course_code, c.name AS course_name,
               fr.requested_faculty_name, fr.details, fr.status,
               fr.admin_comment, fr.created_at, fr.updated_at
        FROM faculty_requests fr
        LEFT JOIN students s ON fr.student_id = s.student_id
        LEFT JOIN courses c ON fr.course_code = c.course_code
        WHERE fr.request_id = %s;
        """
        request_data = self.db.fetch_data(query, (request_id,), fetch_one=True)
        return request_data # Returns a dict

    def update_faculty_request_status(self, request_id, new_status, admin_id, admin_comment=None):
        """
        Updates the status of a faculty request and adds/updates an admin comment.
        Validates the new status.
        :param request_id: The ID of the request to update.
        :param new_status: The new status ('pending', 'approved', 'rejected').
        :param admin_id: The ID of the admin making the update.
        :param admin_comment: Optional. Comment from the admin regarding the status change.
        :return: A tuple (success_boolean, message_string).
        """
        valid_statuses = ['pending', 'approved', 'rejected']
        if new_status not in valid_statuses:
            return False, "Invalid status provided."

        # Fetch current comments to append to, or start new if none exist
        current_request = self.get_faculty_request_by_id(request_id)
        if not current_request:
            return False, "Request not found."

        existing_comments = current_request.get('admin_comment', '')
        new_comment_entry = ""
        if admin_comment:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_comment_entry = f"\n\n--- Status '{new_status.upper()}' by Admin {admin_id} ({timestamp}) ---\n{admin_comment}"
        
        updated_comments = (existing_comments if existing_comments else "") + new_comment_entry

        query = """
        UPDATE faculty_requests SET
            status = %s,
            admin_comment = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE request_id = %s;
        """
        success = self.db.execute_query(query, (new_status, updated_comments, request_id))
        if success:
            return True, "Faculty request status and comment updated successfully."
        else:
            return False, "Failed to update faculty request. Database error."

