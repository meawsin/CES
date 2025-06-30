# Admin_side/views/course_setup_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.course_controller import CourseController
from controllers.faculty_controller import FacultyController
from controllers.student_controller import StudentController
from views.add_edit_course_form import AddEditCourseForm
from views.assign_course_faculty_form import AssignCourseFacultyForm
from views.assign_course_student_form import AssignCourseStudentForm

class CourseSetupPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.course_controller = CourseController()
        self.faculty_controller = FacultyController()
        self.student_controller = StudentController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Create all tab frames and their widgets first.
        self._create_assignments_overview_tab() # New tab added
        self._create_manage_courses_tab()
        self._create_assign_faculty_tab()
        self._create_assign_students_tab()
        

        # 2. Then, load data into comboboxes which depend on all widgets being created.
        self.load_course_combos() # Loads combos for assign faculty/students tabs
        self._populate_overview_comboboxes() # Loads combos for the new overview tab

        # Bind tab change event to refresh data in the selected tab
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Initial load of the first tab's data
        self.load_courses()

    def _on_tab_change(self, event):
        """Refreshes data when a new tab is selected."""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Course Overview":
            self.load_assignments_overview()
        elif selected_tab == "Manage Courses":
            self.load_courses()
        elif selected_tab == "Assign Faculty to Courses":
            self.load_assigned_faculty()
        elif selected_tab == "Assign Students/Batches to Courses":
            self.load_assigned_students_batches()
        

    # --- Manage Courses Tab ---
    def _create_manage_courses_tab(self):
        self.manage_courses_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.manage_courses_frame, text="Manage Courses")

        title_label = ttk.Label(self.manage_courses_frame, text="Manage Courses", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Buttons
        button_frame = ttk.Frame(self.manage_courses_frame)
        button_frame.pack(pady=5, fill="x")
        
        ttk.Button(button_frame, text="Add Course", command=self.open_add_course_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Course", command=self.open_edit_course_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Course", command=self.delete_selected_course, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh List", command=self.load_courses, style="General.TButton").pack(side="right", padx=5)

        # Treeview
        self.course_tree = ttk.Treeview(self.manage_courses_frame, columns=("Code", "Name", "Status"), show="headings")
        self.course_tree.heading("Code", text="Course Code")
        self.course_tree.heading("Name", text="Course Name")
        self.course_tree.heading("Status", text="Status")
        self.course_tree.column("Code", width=120, anchor="center")
        self.course_tree.column("Name", width=300)
        self.course_tree.column("Status", width=100, anchor="center")

        course_scrollbar = ttk.Scrollbar(self.manage_courses_frame, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scrollbar.set)

        self.course_tree.pack(pady=10, fill="both", expand=True)
        course_scrollbar.pack(side="right", fill="y")

    def load_courses(self):
        """Loads all courses into the treeview."""
        for i in self.course_tree.get_children():
            self.course_tree.delete(i)
        courses = self.course_controller.get_all_courses()
        for course in courses:
            self.course_tree.insert("", "end", iid=course.course_code, values=(course.course_code, course.name, course.status))

    def open_add_course_form(self):
        """Opens the form to add a new course."""
        add_form_window = AddEditCourseForm(self.parent_controller.get_root_window(), self.course_controller, self.load_courses)
        self.wait_window_and_refresh(add_form_window, self.load_courses)
        self.load_course_combos() # Refresh combos after add

    def open_edit_course_form(self):
        """Opens the form to edit the selected course."""
        selected_item = self.course_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a course to edit.")
            return

        course_code_to_edit = selected_item
        course_data = self.course_controller.get_course_by_code(course_code_to_edit)

        if course_data:
            edit_form_window = AddEditCourseForm(self.parent_controller.get_root_window(), self.course_controller, self.load_courses, course_to_edit=course_data)
            self.wait_window_and_refresh(edit_form_window, self.load_courses)
        else:
            messagebox.showerror("Error", f"Could not retrieve course data for editing (Code: {course_code_to_edit}). Check if course exists or for DB errors.")

    def delete_selected_course(self):
        """Deletes the selected course."""
        selected_item = self.course_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return

        course_code_to_delete = selected_item
        course_name_to_delete = self.course_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete course: {course_name_to_delete} ({course_code_to_delete})?"):
            success = self.course_controller.delete_course(course_code_to_delete)
            if success:
                messagebox.showinfo("Success", "Course deleted successfully.")
                self.load_courses()
                self.load_course_combos() # Also refresh comboboxes after deletion
            else:
                messagebox.showerror("Error", "Failed to delete course. It might have active assignments or evaluations. Please check dependencies or database logs.")


    def wait_window_and_refresh(self, window, refresh_callback):
        """Helper method to wait for a Toplevel window to close and then call the specific refresh callback."""
        self.parent_controller.get_root_window().wait_window(window)
        refresh_callback() # Call the specific refresh function for the tab


    # --- Assign Faculty Tab ---
    def _create_assign_faculty_tab(self):
        self.assign_faculty_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.assign_faculty_frame, text="Assign Faculty to Courses")

        title_label = ttk.Label(self.assign_faculty_frame, text="Assign Faculty to Courses", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Use a combobox for selecting course
        course_select_frame = ttk.Frame(self.assign_faculty_frame)
        course_select_frame.pack(pady=5)
        ttk.Label(course_select_frame, text="Select Course:").pack(side="left", padx=5)
        self.course_combo_faculty = ttk.Combobox(course_select_frame, state="readonly", width=40)
        self.course_combo_faculty.pack(side="left", padx=5)
        self.course_combo_faculty.bind("<<ComboboxSelected>>", self.load_assigned_faculty)

        ttk.Button(self.assign_faculty_frame, text="Assign/Unassign Faculty", command=self.open_assign_faculty_form, style="General.TButton").pack(pady=10)

        # Treeview for assigned faculty
        self.assigned_faculty_tree = ttk.Treeview(self.assign_faculty_frame, columns=("ID", "Name", "Email"), show="headings")
        self.assigned_faculty_tree.heading("ID", text="Faculty ID")
        self.assigned_faculty_tree.heading("Name", text="Name")
        self.assigned_faculty_tree.heading("Email", text="Email")
        self.assigned_faculty_tree.column("ID", width=100, anchor="center")
        self.assigned_faculty_tree.column("Name", width=150)
        self.assigned_faculty_tree.column("Email", width=200)

        faculty_scrollbar = ttk.Scrollbar(self.assign_faculty_frame, orient="vertical", command=self.assigned_faculty_tree.yview)
        self.assigned_faculty_tree.configure(yscrollcommand=faculty_scrollbar.set)

        self.assigned_faculty_tree.pack(pady=10, fill="both", expand=True)
        faculty_scrollbar.pack(side="right", fill="y")


    def load_course_combos(self):
        """Loads available course codes into comboboxes for assignment tabs."""
        courses = self.course_controller.get_all_courses()
        self.course_codes = [course.course_code for course in courses]

        if hasattr(self, 'course_combo_faculty'):
            self.course_combo_faculty['values'] = self.course_codes
        if hasattr(self, 'course_combo_student'):
            self.course_combo_student['values'] = self.course_codes


    def load_assigned_faculty(self, event=None):
        """Loads assigned faculty for the selected course into the treeview."""
        selected_course_code = self.course_combo_faculty.get()
        for i in self.assigned_faculty_tree.get_children():
            self.assigned_faculty_tree.delete(i)
        if selected_course_code:
            assigned_faculty = self.course_controller.get_assigned_faculty_for_course(selected_course_code)
            for faculty in assigned_faculty:
                self.assigned_faculty_tree.insert("", "end", values=(faculty['faculty_id'], faculty['name'], faculty['email']))

    def open_assign_faculty_form(self):
        """Opens the form to assign/unassign faculty to the selected course."""
        selected_course_code = self.course_combo_faculty.get()
        if not selected_course_code:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return

        assign_form_window = AssignCourseFacultyForm(self.parent_controller.get_root_window(), self.course_controller, self.faculty_controller,
                                selected_course_code, lambda: self.load_assigned_faculty(None)) # Pass specific refresh for this treeview
        self.wait_window_and_refresh(assign_form_window, lambda: self.load_assigned_faculty(None))


    # --- Assign Students/Batches Tab ---
    def _create_assign_students_tab(self):
        self.assign_students_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.assign_students_frame, text="Assign Students/Batches to Courses")

        title_label = ttk.Label(self.assign_students_frame, text="Assign Students/Batches to Courses", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        course_select_frame = ttk.Frame(self.assign_students_frame)
        course_select_frame.pack(pady=5)
        ttk.Label(course_select_frame, text="Select Course:").pack(side="left", padx=5)
        self.course_combo_student = ttk.Combobox(course_select_frame, state="readonly", width=40)
        self.course_combo_student.pack(side="left", padx=5)
        self.course_combo_student.bind("<<ComboboxSelected>>", self.load_assigned_students_batches)

        ttk.Button(self.assign_students_frame, text="Assign/Unassign Students/Batches", command=self.open_assign_student_form, style="General.TButton").pack(pady=10)

        self.assigned_students_tree = ttk.Treeview(self.assign_students_frame, columns=("Student ID", "Student Name", "Batch", "Department"), show="headings")
        self.assigned_students_tree.heading("Student ID", text="Student ID")
        self.assigned_students_tree.heading("Student Name", text="Student Name")
        self.assigned_students_tree.heading("Batch", text="Batch")
        self.assigned_students_tree.heading("Department", text="Department")
        self.assigned_students_tree.column("Student ID", width=100, anchor="center")
        self.assigned_students_tree.column("Student Name", width=150)
        self.assigned_students_tree.column("Batch", width=100)
        self.assigned_students_tree.column("Department", width=120)

        student_scrollbar = ttk.Scrollbar(self.assign_students_frame, orient="vertical", command=self.assigned_students_tree.yview)
        self.assigned_students_tree.configure(yscrollcommand=student_scrollbar.set)

        self.assigned_students_tree.pack(pady=10, fill="both", expand=True)
        student_scrollbar.pack(side="right", fill="y")


    def load_assigned_students_batches(self, event=None):
        """Loads assigned students and batches for the selected course into the treeview."""
        selected_course_code = self.course_combo_student.get()
        for i in self.assigned_students_tree.get_children():
            self.assigned_students_tree.delete(i)
        if selected_course_code:
            assigned_data = self.course_controller.get_assigned_students_batches_for_course(selected_course_code)
            for item in assigned_data:
                if item['student_id']:
                    self.assigned_students_tree.insert("", "end", values=(item['student_id'], item['student_name'], item['batch'], item['department']))
                elif item['batch']:
                    self.assigned_students_tree.insert("", "end", values=("-", "ALL STUDENTS IN", item['batch'], item['department'] if item['department'] else "N/A"))

    def open_assign_student_form(self):
        """Opens the form to assign/unassign students/batches to the selected course."""
        selected_course_code = self.course_combo_student.get()
        if not selected_course_code:
            messagebox.showwarning("No Course Selected", "Please select a course first.")
            return

        assign_form_window = AssignCourseStudentForm(self.parent_controller.get_root_window(), self.course_controller, self.student_controller,
                                selected_course_code, lambda: self.load_assigned_students_batches(None))
        self.wait_window_and_refresh(assign_form_window, lambda: self.load_assigned_students_batches(None))

    # --- NEW: Assignments Overview Tab ---
    def _create_assignments_overview_tab(self):
        self.overview_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.overview_frame, text="Courses Overview")

        title_label = ttk.Label(self.overview_frame, text="Ongoing Course Overview", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Filter Frame
        filter_frame = ttk.Frame(self.overview_frame, padding="10")
        filter_frame.pack(pady=5, fill="x")

        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(filter_frame, text="Course Status:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.overview_status_combo = ttk.Combobox(filter_frame, values=["ongoing", "finished", "upcoming", "all"], state="readonly", width=15)
        self.overview_status_combo.set("ongoing") # Default to ongoing courses
        self.overview_status_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(filter_frame, text="Faculty:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.overview_faculty_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.overview_faculty_combo.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ttk.Label(filter_frame, text="Batch:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.overview_batch_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.overview_batch_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(filter_frame, text="Department:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.overview_department_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.overview_department_combo.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ttk.Button(filter_frame, text="Apply Filters", command=self.load_assignments_overview, style="General.TButton").grid(row=row_idx, column=0, columnspan=4, pady=10)


        # Treeview for displaying combined assignments
        self.overview_tree = ttk.Treeview(self.overview_frame, columns=(
            "Course Code", "Course Name", "Status", "Faculty Name", "Assigned Students/Batches"
        ), show="headings")

        self.overview_tree.heading("Course Code", text="Course Code")
        self.overview_tree.heading("Course Name", text="Course Name")
        self.overview_tree.heading("Status", text="Status")
        self.overview_tree.heading("Faculty Name", text="Assigned Faculty")
        self.overview_tree.heading("Assigned Students/Batches", text="Assigned Students/Batches")

        self.overview_tree.column("Course Code", width=100, anchor="center")
        self.overview_tree.column("Course Name", width=200)
        self.overview_tree.column("Status", width=80, anchor="center")
        self.overview_tree.column("Faculty Name", width=150)
        self.overview_tree.column("Assigned Students/Batches", width=250)

        overview_scrollbar_y = ttk.Scrollbar(self.overview_frame, orient="vertical", command=self.overview_tree.yview)
        self.overview_tree.configure(yscrollcommand=overview_scrollbar_y.set)

        self.overview_tree.pack(pady=10, fill="both", expand=True)
        overview_scrollbar_y.pack(side="right", fill="y")

    def _populate_overview_comboboxes(self):
        """Populates the filter comboboxes for the Assignments Overview tab."""
        # Populate faculty combo
        faculty_members = self.faculty_controller.get_all_faculty()
        self.faculty_options_map_overview = {"": None} # Add "All" option
        faculty_display_names = [""]
        for f in faculty_members:
            display_name = f"{f.name} (ID: {f.faculty_id})"
            self.faculty_options_map_overview[display_name] = f.faculty_id
            faculty_display_names.append(display_name)
        self.overview_faculty_combo['values'] = faculty_display_names

        # Populate batch combo (using student_controller to get unique batches)
        batches_data = self.student_controller.get_unique_batches_with_departments()
        batches = [""] + sorted(list(set([b['batch'] for b in batches_data if b['batch'] is not None])))
        self.overview_batch_combo['values'] = batches

        # Populate department combo (using student_controller to get unique departments)
        departments = [""] + self.student_controller.get_unique_departments()
        self.overview_department_combo['values'] = departments

    def load_assignments_overview(self):
        """Loads combined assignment data into the Assignments Overview treeview based on filters."""
        # Clear existing data
        for i in self.overview_tree.get_children():
            self.overview_tree.delete(i)

        # Get filter values
        course_status = self.overview_status_combo.get()
        course_status = course_status if course_status != "all" else None

        faculty_display_name = self.overview_faculty_combo.get()
        faculty_id = self.faculty_options_map_overview.get(faculty_display_name) if hasattr(self, 'faculty_options_map_overview') else None

        batch = self.overview_batch_combo.get() if self.overview_batch_combo.get() != "" else None
        department = self.overview_department_combo.get() if self.overview_department_combo.get() != "" else None

        # Fetch combined data using the controller method
        assignments_data = self.course_controller.get_course_assignments_overview(
            status=course_status,
            faculty_id=faculty_id,
            batch=batch,
            department=department
        )

        for assignment in assignments_data:
            # Format assigned faculty names for display
            faculty_names_str = ", ".join([f['name'] for f in assignment['assigned_faculty']]) if assignment['assigned_faculty'] else "N/A"
            
            # Format assigned students/batches for display
            assigned_students_batches_str_parts = []
            for item in assignment['assigned_students_batches']:
                if item['student_id']:
                    assigned_students_batches_str_parts.append(f"Student: {item['student_name']} ({item['student_id']}) - {item['department']}")
                elif item['batch']:
                    assigned_students_batches_str_parts.append(f"Batch: {item['batch']} - {item['department']}")
            
            assigned_str = "\n".join(assigned_students_batches_str_parts) if assigned_students_batches_str_parts else "N/A"

            self.overview_tree.insert("", "end", values=(
                assignment['course_code'],
                assignment['course_name'],
                assignment['course_status'].title(),
                faculty_names_str,
                assigned_str
            ))