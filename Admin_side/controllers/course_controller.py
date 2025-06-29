# Admin_side/controllers/course_controller.py
from database.db_manager import DBManager
from models.course_model import Course
from models.faculty_model import Faculty
from models.student_model import Student
from models.course_faculty_model import CourseFaculty
from models.course_student_model import CourseStudent

class CourseController:
    def __init__(self):
        self.db = DBManager()

    # --- Course Management ---
    def get_all_courses(self):
        """Fetches all course records."""
        query = "SELECT * FROM courses ORDER BY name;"
        courses_data = self.db.fetch_data(query, fetch_all=True)
        if courses_data:
            return [Course.from_db_row(row) for row in courses_data]
        return []

    def get_course_by_code(self, course_code):
        """Fetches a single course record by code."""
        query = "SELECT * FROM courses WHERE course_code = %s;"
        course_data = self.db.fetch_data(query, (course_code,), fetch_one=True)
        if course_data:
            return Course.from_db_row(course_data)
        return None

    def add_course(self, course: Course):
        """Inserts a new course record."""
        query = "INSERT INTO courses (course_code, name, status) VALUES (%s, %s, %s);"
        params = (course.course_code, course.name, course.status)
        return self.db.execute_query(query, params)

    def update_course(self, course: Course):
        """Updates an existing course record."""
        query = "UPDATE courses SET name = %s, status = %s WHERE course_code = %s;"
        params = (course.name, course.status, course.course_code)
        return self.db.execute_query(query, params)

    def delete_course(self, course_code):
        """Deletes a course record by code."""
        query = "DELETE FROM courses WHERE course_code = %s;"
        return self.db.execute_query(query, (course_code,))

    # --- Course-Faculty Assignments ---
    def get_assigned_faculty_for_course(self, course_code):
        """Fetches faculty assigned to a specific course."""
        query = """
        SELECT f.faculty_id, f.name, f.email
        FROM faculty f
        JOIN course_faculty cf ON f.faculty_id = cf.faculty_id
        WHERE cf.course_code = %s;
        """
        data = self.db.fetch_data(query, (course_code,), fetch_all=True)
        return data if data else [] # Returns list of dicts with faculty_id, name, email

    def get_courses_assigned_to_faculty(self, faculty_id):
        """Fetches courses assigned to a specific faculty."""
        query = """
        SELECT c.course_code, c.name, c.status
        FROM courses c
        JOIN course_faculty cf ON c.course_code = cf.course_code
        WHERE cf.faculty_id = %s;
        """
        data = self.db.fetch_data(query, (faculty_id,), fetch_all=True)
        return data if data else []

    def assign_faculty_to_course(self, course_code, faculty_id):
        """Assigns a faculty member to a course."""
        # Check if already assigned
        check_query = "SELECT 1 FROM course_faculty WHERE course_code = %s AND faculty_id = %s;"
        if self.db.fetch_data(check_query, (course_code, faculty_id), fetch_one=True):
            return False # Already assigned

        query = "INSERT INTO course_faculty (course_code, faculty_id) VALUES (%s, %s);"
        return self.db.execute_query(query, (course_code, faculty_id))

    def unassign_faculty_from_course(self, course_code, faculty_id):
        """Removes a faculty member assignment from a course."""
        query = "DELETE FROM course_faculty WHERE course_code = %s AND faculty_id = %s;"
        return self.db.execute_query(query, (course_code, faculty_id))

    # --- Course-Student/Batch Assignments ---
    def get_assigned_students_batches_for_course(self, course_code):
        """Fetches students and batches assigned to a specific course."""
        query = """
        SELECT cs.student_id, s.name AS student_name, cs.batch, s.department
        FROM course_student cs
        LEFT JOIN students s ON cs.student_id = s.student_id
        WHERE cs.course_code = %s;
        """
        data = self.db.fetch_data(query, (course_code,), fetch_all=True)
        return data if data else []

    def assign_student_to_course(self, course_code, student_id):
        """Assigns an individual student to a course."""
        # Check if already assigned as individual or part of batch for this course
        check_query = "SELECT 1 FROM course_student WHERE course_code = %s AND student_id = %s;"
        if self.db.fetch_data(check_query, (course_code, student_id), fetch_one=True):
            return False

        query = "INSERT INTO course_student (course_code, student_id) VALUES (%s, %s);"
        return self.db.execute_query(query, (course_code, student_id))

    def assign_batch_to_course(self, course_code, batch):
        """Assigns an entire batch to a course."""
        # Check if already assigned
        check_query = "SELECT 1 FROM course_student WHERE course_code = %s AND batch = %s AND student_id IS NULL;"
        if self.db.fetch_data(check_query, (course_code, batch), fetch_one=True):
            return False

        query = "INSERT INTO course_student (course_code, batch) VALUES (%s, %s);"
        return self.db.execute_query(query, (course_code, batch))

    def unassign_student_from_course(self, course_code, student_id):
        """Removes an individual student assignment from a course."""
        query = "DELETE FROM course_student WHERE course_code = %s AND student_id = %s;"
        return self.db.execute_query(query, (course_code, student_id))

    def unassign_batch_from_course(self, course_code, batch):
        """Removes a batch assignment from a course."""
        query = "DELETE FROM course_student WHERE course_code = %s AND batch = %s AND student_id IS NULL;"
        return self.db.execute_query(query, (course_code, batch))
        
    def get_course_assignments_overview(self, status=None, faculty_id=None, batch=None, department=None):
        """
        Fetches a combined overview of courses, their assigned faculty, and assigned students/batches.
        Can be filtered by course status, faculty, batch, or department.
        """
        # Base query to get course details
        query = """
        SELECT
            c.course_code,
            c.name AS course_name,
            c.status AS course_status
        FROM courses c
        WHERE 1=1
        """
        params = []

        if status and status != "all": # Filter by status unless "all" is selected
            query += " AND c.status = %s"
            params.append(status)

        courses_data = self.db.fetch_data(query, tuple(params), fetch_all=True)

        if not courses_data:
            return []

        overview_list = []
        for course_row in courses_data:
            course_code = course_row['course_code']

            # Get assigned faculty for this course
            assigned_faculty_list = self.get_assigned_faculty_for_course(course_code)
            
            # Filter faculty if faculty_id is provided
            if faculty_id:
                assigned_faculty_list = [f for f in assigned_faculty_list if f['faculty_id'] == faculty_id]
                if not assigned_faculty_list: # If no matching faculty, skip this course for the current filter
                    continue

            # Get assigned students/batches for this course
            assigned_students_batches_list = self.get_assigned_students_batches_for_course(course_code)
            
            # Filter students/batches if batch or department is provided
            if batch:
                assigned_students_batches_list = [item for item in assigned_students_batches_list if item['batch'] == batch]
            if department:
                # Filter by department, checking both individual student's department and if a batch assignment has a matching department
                # This assumes `get_assigned_students_batches_for_course` already returns `department` for both student and batch entries.
                assigned_students_batches_list = [item for item in assigned_students_batches_list if item.get('department') == department]

            # If filters applied and no assignments match, skip this course
            if (faculty_id and not assigned_faculty_list) or ((batch or department) and not assigned_students_batches_list):
                continue
                
            overview_list.append({
                "course_code": course_row['course_code'],
                "course_name": course_row['course_name'],
                "course_status": course_row['course_status'],
                "assigned_faculty": assigned_faculty_list, # List of dicts: {'faculty_id', 'name', 'email'}
                "assigned_students_batches": assigned_students_batches_list # List of dicts: {'student_id', 'student_name', 'batch', 'department'}
            })

        return overview_list