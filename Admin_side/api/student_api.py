# Admin_side/api/student_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json # Ensure json is imported
from datetime import datetime # Ensure datetime is imported

# Get the path to the 'Admin_side' directory to set up module imports
current_dir = os.path.dirname(__file__)
admin_side_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, admin_side_dir)

from database.db_manager import DBManager
from controllers.auth_controller import AuthController # Potentially unused for student API directly, but part of context
from controllers.student_controller import StudentController
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.faculty_request_controller import FacultyRequestController # NEW: Import FacultyRequestController
from models.evaluation_completion_model import EvaluationCompletion
from models.evaluation_model import Evaluation


app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for frontend interaction

db_manager = DBManager()
auth_controller = AuthController() # Still keeping this, though it's primarily for admin auth
student_controller = StudentController()
evaluation_template_controller = EvaluationTemplateController()
faculty_request_controller = FacultyRequestController() # NEW: Initialize faculty request controller


# Connect to the database on app startup
if not db_manager.connect():
    print("FATAL: Could not connect to the database. Exiting API.")
    sys.exit(1) # Exit if database connection fails

# --- Helper Function for Auth Token (Basic for now) ---
SESSION_TOKENS = {} # In-memory store for session tokens, for demonstration purposes

def generate_session_token(student_id):
    """
    Generates a simple session token for a student.
    In a production environment, use more robust token generation (e.g., JWTs)
    and persistent storage (e.g., database, Redis).
    :param student_id: The ID of the student.
    :return: A hexadecimal string token.
    """
    token = os.urandom(16).hex() # Generates a random 32-character hex string
    SESSION_TOKENS[token] = student_id # Store token -> student_id mapping
    return token

def get_student_id_from_token(token):
    """
    Retrieves the student_id associated with a given session token.
    :param token: The session token.
    :return: The student_id if found, None otherwise.
    """
    return SESSION_TOKENS.get(token)

# --- API Endpoints ---

@app.route('/api/student/login', methods=['POST'])
def student_login():
    """
    Handles student login using student ID and password.
    Returns a session token upon successful authentication.
    """
    data = request.get_json()
    student_id = data.get('student_id') # NEW: Expect student_id instead of email
    password = data.get('password')

    if not student_id or not password:
        return jsonify({"message": "Student ID and password are required."}), 400

    # Attempt to authenticate student using the student ID
    # Note: student_controller.authenticate_student might still expect email depending on its implementation.
    # We need to ensure student_controller.authenticate_student can handle student_id.
    # Assuming student_controller.authenticate_student will be updated or already checks by student_id/password.
    # For now, let's pass student_id to it.
    try:
        # Convert student_id to integer for backend logic if it's stored as int
        student_id_int = int(student_id)
    except ValueError:
        return jsonify({"message": "Invalid Student ID format."}), 400


    student_user = student_controller.authenticate_student(student_id=student_id_int, password=password)

    if student_user:
        token = generate_session_token(student_user.student_id)
        return jsonify({
            "message": "Login successful.",
            "token": token,
            "student_id": student_user.student_id,
            "student_name": student_user.name
        }), 200
    else:
        return jsonify({"message": "Invalid student ID or password."}), 401

@app.route('/api/student/logout', methods=['POST'])
def student_logout():
    """
    Invalidates a student session token upon logout.
    """
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1] # Extract the token string
        if token in SESSION_TOKENS:
            del SESSION_TOKENS[token] # Remove token from in-memory store
            return jsonify({"message": "Logout successful."}), 200
    return jsonify({"message": "Invalid token or not logged in."}), 401

@app.route('/api/student/evaluations/assigned', methods=['GET'])
def get_assigned_evaluations():
    """
    Retrieves evaluations currently assigned to the logged-in student that are
    pending completion.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    student_details = student_controller.get_student_by_id(student_id)
    if not student_details:
        return jsonify({"message": "Student not found."}), 404

    assigned_evals = []
    all_ongoing = evaluation_template_controller.get_ongoing_evaluations()

    # Get all courses the student is assigned to (individually or by batch)
    student_assigned_courses = {item['course_code'] for item in student_controller.get_courses_for_student(student_id)}

    # Get all evaluations already completed by this student
    completed_eval_ids = set()
    completed_records = db_manager.fetch_data(
        "SELECT template_id, course_code FROM evaluation_completion WHERE student_id = %s AND is_completed = TRUE",
        (student_id,), fetch_all=True
    )
    for rec in completed_records:
        # Use a tuple (template_id, course_code) as the key for completion status,
        # as a template might be assigned to different courses.
        completed_eval_ids.add((rec['template_id'], rec['course_code']))

    for eval_temp in all_ongoing:
        is_relevant = False
        # Check if the evaluation template applies to the student's context
        # It's relevant if:
        # 1. It's assigned to a course the student is in.
        # 2. It's assigned to the student's batch.
        # 3. It's assigned to the student's session.
        if eval_temp.course_code and eval_temp.course_code in student_assigned_courses:
            is_relevant = True
        elif eval_temp.batch and student_details.batch == eval_temp.batch:
            is_relevant = True
        elif eval_temp.session and student_details.session == eval_temp.session:
            is_relevant = True

        if is_relevant:
            # Check if this specific assignment (template_id, course_code) has been completed
            is_completed = (eval_temp.id, eval_temp.course_code) in completed_eval_ids

            if not is_completed:
                # Add to assigned_evals if it's relevant and not yet completed
                assigned_evals.append({
                    "id": eval_temp.id,
                    "title": eval_temp.title,
                    "course_code": eval_temp.course_code,
                    "batch": eval_temp.batch,
                    "session": eval_temp.session,
                    "last_date": eval_temp.last_date.strftime("%Y-%m-%d") if eval_temp.last_date else None
                })

    return jsonify(assigned_evals), 200

@app.route('/api/student/evaluations/template/<int:template_id>', methods=['GET'])
def get_evaluation_template_details(template_id):
    """
    Retrieves the details of a specific evaluation template by its ID.
    Used by the frontend when a student goes to "Take Evaluation".
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    template = evaluation_template_controller.get_template_by_id(template_id)
    if not template:
        return jsonify({"message": "Evaluation template not found."}), 404

    # Ensure questions_set is a dictionary, not a JSON string
    questions_set = template.questions_set
    if not isinstance(questions_set, dict):
        try:
            questions_set = json.loads(questions_set)
        except json.JSONDecodeError:
            return jsonify({"message": "Invalid questions_set format in template."}), 500

    return jsonify({
        "id": template.id,
        "title": template.title,
        "instructions": questions_set.get('instructions', ''),
        "questions": questions_set.get('questions', [])
    }), 200


@app.route('/api/student/evaluations/submit', methods=['POST'])
def submit_evaluation():
    """
    Submits a student's evaluation responses and marks the evaluation as complete.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    data = request.get_json()
    course_code = data.get('course_code')
    template_id = data.get('template_id')
    feedback = data.get('feedback')
    comment = data.get('comment') # General comment

    if not all([template_id, feedback]):
        return jsonify({"message": "Missing required data (template_id, feedback)."}), 400

    # Handle course_code - if it's "N/A" or empty, set to None
    if course_code == "N/A" or not course_code:
        course_code = None

    try:
        # Create an Evaluation object to save the feedback
        new_evaluation = Evaluation(
            id=None, # ID will be auto-incremented by DB
            course_code=course_code,
            template_id=template_id,
            feedback=feedback, # Store feedback as Python dict, will be JSON-dumped by model/query
            comment=comment,
            date=datetime.now() # Record current timestamp
        )
        # Execute query to insert evaluation feedback
        eval_success = db_manager.execute_query(
            "INSERT INTO evaluations (course_code, template_id, feedback, comment, date) VALUES (%s, %s, %s, %s, %s)",
            (new_evaluation.course_code, new_evaluation.template_id, json.dumps(new_evaluation.feedback), new_evaluation.comment, new_evaluation.date)
        )

        if not eval_success:
            raise Exception("Failed to save evaluation feedback.")

        # Mark evaluation as complete in the evaluation_completion table
        # Handle null course_code for batch/session-only evaluations
        if course_code:
        existing_completion = db_manager.fetch_data(
            "SELECT id FROM evaluation_completion WHERE template_id = %s AND course_code = %s AND student_id = %s",
            (template_id, course_code, student_id), fetch_one=True
        )
        else:
            # For evaluations without course_code, use NULL in the query
            existing_completion = db_manager.fetch_data(
                "SELECT id FROM evaluation_completion WHERE template_id = %s AND course_code IS NULL AND student_id = %s",
                (template_id, student_id), fetch_one=True
            )

        if existing_completion:
            # If a completion record already exists, update it to 'completed'
            completion_success = db_manager.execute_query(
                "UPDATE evaluation_completion SET is_completed = TRUE, completion_date = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (datetime.now(), existing_completion['id'])
            )
        else:
            # If no record exists, insert a new one
            completion_success = db_manager.execute_query(
                "INSERT INTO evaluation_completion (template_id, course_code, student_id, is_completed, completion_date) VALUES (%s, %s, %s, TRUE, %s)",
                (template_id, course_code, student_id, datetime.now())
            )

        if not completion_success:
            raise Exception("Failed to mark evaluation as complete.")

        return jsonify({"message": "Evaluation submitted successfully."}), 200

    except Exception as e:
        print(f"Error submitting evaluation: {e}")
        return jsonify({"message": f"Failed to submit evaluation: {str(e)}"}), 500

@app.route('/api/student/courses_faculty/<string:course_code>', methods=['GET'])
def get_course_faculty_api(course_code):
    """
    Retrieves faculty members assigned to a specific course.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    faculty_list = student_controller.get_faculty_for_course(course_code)
    return jsonify(faculty_list), 200

# --- NEW: Endpoints for Profile, Completed Evaluations, Complaints ---

@app.route('/api/student/profile', methods=['GET'])
def get_student_profile():
    """
    Retrieves the logged-in student's profile data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    profile_data = student_controller.get_student_profile_data(student_id)
    if not profile_data:
        return jsonify({"message": "Student profile not found."}), 404

    return jsonify(profile_data), 200

@app.route('/api/student/profile/update', methods=['PUT'])
def update_student_profile_api():
    """
    Updates the logged-in student's profile data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update."}), 400

    # Only allow updating specific fields
    # Removed 'behavioral_records' from editable fields from frontend; only update what's sent from frontend.
    editable_fields = ['name', 'contact_no', 'profile_picture']
    update_data = {k: v for k, v in data.items() if k in editable_fields}

    if not update_data:
        return jsonify({"message": "No editable fields provided for update."}), 400

    success, message = student_controller.update_student_profile(student_id, update_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 500

@app.route('/api/student/evaluations/completed', methods=['GET'])
def get_completed_evaluations():
    """
    Retrieves a list of evaluations completed by the logged-in student.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    completed_evals = student_controller.get_completed_evaluations_for_student(student_id)
    return jsonify(completed_evals), 200

@app.route('/api/student/evaluations/completed/details', methods=['GET'])
def get_completed_evaluation_details_api():
    """
    Retrieves the full feedback and comment for a specific completed evaluation.
    Requires template_id and optionally course_code as query parameters.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    template_id = request.args.get('template_id', type=int)
    course_code = request.args.get('course_code')

    if not template_id:
        return jsonify({"message": "Missing template_id parameter."}), 400

    # course_code is optional, can be None or "N/A"
    details = student_controller.get_completed_evaluation_details(student_id, template_id, course_code)
    if not details:
        return jsonify({"message": "Completed evaluation details not found."}), 404

    return jsonify(details), 200


@app.route('/api/student/complaints/submit', methods=['POST'])
def submit_complaint_api():
    """
    Submits a new complaint from the logged-in student.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    data = request.get_json()
    course_code = data.get('course_code')
    issue_type = data.get('issue_type')
    details = data.get('details')

    if not all([issue_type, details]):
        return jsonify({"message": "Issue type and details are required for a complaint."}), 400

    success, message = student_controller.submit_complaint(student_id, course_code, issue_type, details)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 500

@app.route('/api/student/complaints/list', methods=['GET'])
def get_student_complaints_list():
    """
    Returns all complaints submitted by the logged-in student.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    complaints = student_controller.get_complaints_for_student(student_id)
    # Each complaint should have: issue_type, details, course_code, status
    return jsonify(complaints), 200

# NEW: Endpoint for submitting faculty requests
@app.route('/api/student/requests/faculty_request', methods=['POST'])
def submit_faculty_request_api():
    """
    Allows a student to submit a request for a new faculty for a course.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    data = request.get_json()
    course_name = data.get('course_name') # Changed from course_code
    requested_faculty_name = data.get('requested_faculty_name')
    details = data.get('details')

    if not all([course_name, details]): # Changed from course_code
        return jsonify({"message": "Course name and request details are required."}), 400

    success, message = faculty_request_controller.submit_faculty_request(
        student_id, course_name, requested_faculty_name, details # Changed from course_code
    )

    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 500

# NEW: Endpoint to get available upcoming courses for student requests
@app.route('/api/student/courses/upcoming', methods=['GET'])
def get_upcoming_courses_api():
    """
    Retrieves a list of courses with 'upcoming' status.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401

    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401
    
    # Using student_controller to get courses which in turn uses CourseController
    upcoming_courses = student_controller.get_courses_by_status(status='upcoming')
    
    # Format for frontend dropdown
    formatted_courses = [{
        'course_code': c.course_code,
        'course_name': c.name
    } for c in upcoming_courses]

    return jsonify(formatted_courses), 200


if __name__ == '__main__':
    # Ensure this runs from the project root if using relative imports
    # Example: python -m Admin_side.api.student_api
    app.run(debug=True, port=5000)
