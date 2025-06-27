# Admin_side/api/student_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS 
import sys
import os

# Get the path to the 'Admin_side' directory
current_dir = os.path.dirname(__file__)
admin_side_dir = os.path.abspath(os.path.join(current_dir, '..')) 
sys.path.insert(0, admin_side_dir) 

from database.db_manager import DBManager
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.evaluation_template_controller import EvaluationTemplateController
from models.evaluation_completion_model import EvaluationCompletion
from models.evaluation_model import Evaluation
import json
from datetime import datetime

app = Flask(__name__)
CORS(app) 

db_manager = DBManager()
auth_controller = AuthController()
student_controller = StudentController()
evaluation_template_controller = EvaluationTemplateController()

# Connect to the database on app startup
if not db_manager.connect():
    print("FATAL: Could not connect to the database. Exiting API.")
    sys.exit(1)

# --- Helper Function for Auth Token (Basic for now) ---
SESSION_TOKENS = {} 

def generate_session_token(student_id):
    """Generates a simple session token (for demonstration)."""
    token = os.urandom(16).hex() 
    SESSION_TOKENS[token] = student_id
    return token

def get_student_id_from_token(token):
    """Retrieves student_id from a session token."""
    return SESSION_TOKENS.get(token)

# --- API Endpoints ---

@app.route('/api/student/login', methods=['POST'])
def student_login():
    """Handles student login and returns a session token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    student_user = student_controller.authenticate_student(email, password)
    
    if student_user:
        token = generate_session_token(student_user.student_id)
        return jsonify({
            "message": "Login successful.",
            "token": token,
            "student_id": student_user.student_id,
            "student_name": student_user.name
        }), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

@app.route('/api/student/logout', methods=['POST'])
def student_logout():
    """Invalidates a student session token."""
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        if token in SESSION_TOKENS:
            del SESSION_TOKENS[token]
            return jsonify({"message": "Logout successful."}), 200
    return jsonify({"message": "Invalid token or not logged in."}), 401

@app.route('/api/student/evaluations/assigned', methods=['GET'])
def get_assigned_evaluations():
    """Retrieves evaluations assigned to the logged-in student."""
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
    
    student_assigned_courses = {item['course_code'] for item in student_controller.get_courses_for_student(student_id)}

    completed_eval_ids = set()
    completed_records = db_manager.fetch_data(
        "SELECT template_id, course_code FROM evaluation_completion WHERE student_id = %s AND is_completed = TRUE",
        (student_id,), fetch_all=True
    )
    for rec in completed_records:
        # Use a tuple (template_id, course_code) as the key for completion
        completed_eval_ids.add((rec['template_id'], rec['course_code']))

    for eval_temp in all_ongoing:
        is_relevant = False
        
        # Check if the evaluation template applies to the student's context
        if eval_temp.course_code and eval_temp.course_code in student_assigned_courses:
            is_relevant = True
        
        if eval_temp.batch and student_details.batch == eval_temp.batch:
            is_relevant = True
            
        if eval_temp.session and student_details.session == eval_temp.session:
            is_relevant = True

        if is_relevant:
            # Check if this specific assignment (template_id, course_code) has been completed
            # Note: course_code in evaluation_completion is crucial here to distinguish assignments
            is_completed = (eval_temp.id, eval_temp.course_code) in completed_eval_ids

            if not is_completed: 
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
    """Retrieves a specific evaluation template by ID."""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401
    
    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    template = evaluation_template_controller.get_template_by_id(template_id)
    if not template:
        return jsonify({"message": "Evaluation template not found."}), 404
    
    questions_set = template.questions_set
    if not isinstance(questions_set, dict):
        questions_set = json.loads(questions_set) 

    return jsonify({
        "id": template.id,
        "title": template.title,
        "instructions": questions_set.get('instructions', ''),
        "questions": questions_set.get('questions', [])
    }), 200


@app.route('/api/student/evaluations/submit', methods=['POST'])
def submit_evaluation():
    """Submits an evaluation response and marks it as complete."""
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
    comment = data.get('comment') 

    if not all([course_code, template_id, feedback]):
        return jsonify({"message": "Missing required data (course_code, template_id, feedback)."}), 400

    try:
        new_evaluation = Evaluation(
            id=None,
            course_code=course_code,
            template_id=template_id,
            feedback=feedback, 
            comment=comment,
            date=datetime.now()
        )
        eval_success = db_manager.execute_query(
            "INSERT INTO evaluations (course_code, template_id, feedback, comment, date) VALUES (%s, %s, %s, %s, %s)",
            (new_evaluation.course_code, new_evaluation.template_id, json.dumps(new_evaluation.feedback), new_evaluation.comment, new_evaluation.date)
        )

        if not eval_success:
            raise Exception("Failed to save evaluation feedback.")

        existing_completion = db_manager.fetch_data(
            "SELECT id FROM evaluation_completion WHERE template_id = %s AND course_code = %s AND student_id = %s",
            (template_id, course_code, student_id), fetch_one=True
        )

        if existing_completion:
            completion_success = db_manager.execute_query(
                "UPDATE evaluation_completion SET is_completed = TRUE, completion_date = %s WHERE id = %s",
                (datetime.now(), existing_completion['id'])
            )
        else:
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
    """Retrieves faculty assigned to a specific course."""
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
    """Retrieves the logged-in student's profile data."""
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
    """Updates the logged-in student's profile data."""
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
    """Retrieves a list of evaluations completed by the logged-in student."""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Authentication required."}), 401
    
    student_id = get_student_id_from_token(token.split(' ')[1])
    if not student_id:
        return jsonify({"message": "Invalid session token."}), 401

    completed_evals = student_controller.get_completed_evaluations_for_student(student_id)
    return jsonify(completed_evals), 200

@app.route('/api/student/complaints/submit', methods=['POST'])
def submit_complaint_api():
    """Submits a new complaint from the logged-in student."""
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
