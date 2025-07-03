# Admin_side/views/course_setup_page.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.course_controller import CourseController
from controllers.faculty_controller import FacultyController
from controllers.student_controller import StudentController
from views.add_edit_course_form import AddEditCourseForm
from views.assign_course_faculty_form import AssignCourseFacultyForm
from views.assign_course_student_form import AssignCourseStudentForm

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class CourseSetupPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller
        self.course_controller = CourseController()
        self.faculty_controller = FacultyController()
        self.student_controller = StudentController()

        self.configure(fg_color=GREY)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Create all tab frames and their widgets first.
        self._create_assignments_overview_tab() # New tab added
        self._create_manage_courses_tab()
        self._create_assign_faculty_tab()
        self._create_assign_students_tab()

        # 2. Then, load data into comboboxes which depend on all widgets being created.
        self.load_course_combos() # Loads combos for assign faculty/students tabs
        self._populate_overview_comboboxes() # Loads combos for the new overview tab

        # Select Course Overview tab by default and load its data
        self.notebook.set("Course Overview")
        self.load_assignments_overview()

        # Initial load of the first tab's data
        self.load_courses()

    # --- Manage Courses Tab ---
    def _create_manage_courses_tab(self):
        self.manage_courses_frame = self.notebook.add("Manage Courses")

        title_label = ctk.CTkLabel(self.manage_courses_frame, text="Manage Courses", font=("Arial", 28, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self.manage_courses_frame, fg_color=WHITE)
        button_frame.pack(pady=5, fill="x")
        
        ctk.CTkButton(button_frame, text="Add Course", command=self.open_add_course_form,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Edit Course", command=self.open_edit_course_form,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Delete Course", command=self.delete_selected_course,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Refresh List", command=self.load_courses,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="right", padx=5)

        # Course list frame with treeview
        course_list_frame = ctk.CTkFrame(self.manage_courses_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        course_list_frame.pack(pady=10, fill="both", expand=True)
        
        self.course_tree = ttk.Treeview(course_list_frame, columns=("Code", "Name", "Status"), show="headings", height=12)
        self.course_tree.heading("Code", text="Course Code")
        self.course_tree.heading("Name", text="Course Name")
        self.course_tree.heading("Status", text="Status")
        self.course_tree.column("Code", width=120, anchor="center")
        self.course_tree.column("Name", width=300)
        self.course_tree.column("Status", width=100, anchor="center")

        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        course_scrollbar = ctk.CTkScrollbar(course_list_frame, orientation="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scrollbar.set)
        self.course_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        course_scrollbar.pack(side="right", fill="y", pady=10)

    def load_courses(self):
        """Loads all courses into the treeview."""
        for i in self.course_tree.get_children():
            self.course_tree.delete(i)
        courses = self.course_controller.get_all_courses()
        
        # Store course data for later use
        self.courses_data = {}
        
        for course in courses:
            self.course_tree.insert("", "end", iid=course.course_code, values=(course.course_code, course.name, course.status))
            self.courses_data[course.course_code] = course

    def open_add_course_form(self):
        """Opens the form to add a new course."""
        add_form_window = AddEditCourseForm(self.parent_controller.get_root_window(), self.course_controller, self.load_courses)
        self.wait_window_and_refresh(add_form_window, self.load_courses)
        self.load_course_combos() # Refresh combos after add

    def open_edit_course_form(self):
        """Opens the form to edit the selected course."""
        selected_item = self.course_tree.focus()
        if not selected_item:
            ctk.CTkMessagebox.show_warning("No Selection", "Please select a course to edit.")
            return

        course_code_to_edit = selected_item
        course_data = self.course_controller.get_course_by_code(course_code_to_edit)

        if course_data:
            edit_form_window = AddEditCourseForm(self.parent_controller.get_root_window(), self.course_controller, self.load_courses, course_to_edit=course_data)
            self.wait_window_and_refresh(edit_form_window, self.load_courses)
        else:
            ctk.CTkMessagebox.show_error("Error", f"Could not retrieve course data for editing (Code: {course_code_to_edit}). Check if course exists or for DB errors.")

    def delete_selected_course(self):
        """Deletes the selected course."""
        selected_item = self.course_tree.focus()
        if not selected_item:
            ctk.CTkMessagebox.show_warning("No Selection", "Please select a course to delete.")
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
        self.assign_faculty_frame = self.notebook.add("Assign Faculty to Courses")

        title_label = ctk.CTkLabel(self.assign_faculty_frame, text="Assign Faculty to Courses", font=("Arial", 28, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Course selection
        course_select_frame = ctk.CTkFrame(self.assign_faculty_frame, fg_color=WHITE)
        course_select_frame.pack(pady=5)
        ctk.CTkLabel(course_select_frame, text="Select Course:", font=("Arial", 17), text_color=DARK_BLUE).pack(side="left", padx=5)
        self.course_combo_faculty = ctk.CTkOptionMenu(course_select_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                                     button_color=BLUE, button_hover_color=DARK_BLUE)
        self.course_combo_faculty.pack(side="left", padx=5)
        self.course_combo_faculty.set("Select a course...")
        self.course_combo_faculty.configure(command=self._on_faculty_course_selected)

        # Dual-list frame
        dual_list_frame = ctk.CTkFrame(self.assign_faculty_frame, fg_color=WHITE)
        dual_list_frame.pack(pady=10, fill="both", expand=True)
        dual_list_frame.columnconfigure(0, weight=1)
        dual_list_frame.columnconfigure(1, weight=0)
        dual_list_frame.columnconfigure(2, weight=1)
        dual_list_frame.rowconfigure(1, weight=1)

        # Available Faculty
        available_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        available_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=5)
        ctk.CTkLabel(available_frame, text="Available Faculty", font=("Arial", 16, "bold"), text_color=DARK_BLUE).pack(pady=(10, 0))
        self.faculty_search_var = ctk.StringVar()
        faculty_search_entry = ctk.CTkEntry(available_frame, textvariable=self.faculty_search_var, placeholder_text="Search...", font=("Arial", 13))
        faculty_search_entry.pack(padx=10, pady=5, fill="x")
        faculty_search_entry.bind('<KeyRelease>', self._filter_available_faculty)
        self.available_faculty_tree = ttk.Treeview(available_frame, columns=("ID", "Name", "Email"), show="headings", height=12)
        self.available_faculty_tree.heading("ID", text="Faculty ID")
        self.available_faculty_tree.heading("Name", text="Name")
        self.available_faculty_tree.heading("Email", text="Email")
        self.available_faculty_tree.column("ID", width=100, anchor="center")
        self.available_faculty_tree.column("Name", width=150)
        self.available_faculty_tree.column("Email", width=200)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        available_scrollbar = ctk.CTkScrollbar(available_frame, orientation="vertical", command=self.available_faculty_tree.yview)
        self.available_faculty_tree.configure(yscrollcommand=available_scrollbar.set)
        self.available_faculty_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        available_scrollbar.pack(side="right", fill="y", pady=10)
        self.available_faculty_empty_label = ctk.CTkLabel(available_frame, text="Select a course to view available faculty.", font=("Arial", 15), text_color=DARK_BLUE)
        self.available_faculty_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        self.available_faculty_tree.lower()

        # Assign/Unassign buttons
        button_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE)
        button_frame.grid(row=1, column=1, sticky="ns", pady=5)
        button_frame.rowconfigure((0, 1, 2), weight=1)
        self.assign_faculty_btn = ctk.CTkButton(button_frame, text="Assign →", command=self._assign_selected_faculty,
                                                fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15), width=120)
        self.assign_faculty_btn.grid(row=0, column=0, pady=10)
        self.unassign_faculty_btn = ctk.CTkButton(button_frame, text="← Unassign", command=self._unassign_selected_faculty,
                                                  fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15), width=120)
        self.unassign_faculty_btn.grid(row=1, column=0, pady=10)

        # Assigned Faculty
        assigned_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(10, 0), pady=5)
        ctk.CTkLabel(assigned_frame, text="Assigned Faculty", font=("Arial", 16, "bold"), text_color=DARK_BLUE).pack(pady=(10, 0))
        self.assigned_faculty_search_var = ctk.StringVar()
        assigned_search_entry = ctk.CTkEntry(assigned_frame, textvariable=self.assigned_faculty_search_var, placeholder_text="Search...", font=("Arial", 13))
        assigned_search_entry.pack(padx=10, pady=5, fill="x")
        assigned_search_entry.bind('<KeyRelease>', self._filter_assigned_faculty)
        self.assigned_faculty_tree = ttk.Treeview(assigned_frame, columns=("ID", "Name", "Email"), show="headings", height=12)
        self.assigned_faculty_tree.heading("ID", text="Faculty ID")
        self.assigned_faculty_tree.heading("Name", text="Name")
        self.assigned_faculty_tree.heading("Email", text="Email")
        self.assigned_faculty_tree.column("ID", width=100, anchor="center")
        self.assigned_faculty_tree.column("Name", width=150)
        self.assigned_faculty_tree.column("Email", width=200)
        assigned_scrollbar = ctk.CTkScrollbar(assigned_frame, orientation="vertical", command=self.assigned_faculty_tree.yview)
        self.assigned_faculty_tree.configure(yscrollcommand=assigned_scrollbar.set)
        self.assigned_faculty_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        assigned_scrollbar.pack(side="right", fill="y", pady=10)
        self.assigned_faculty_empty_label = ctk.CTkLabel(assigned_frame, text="Select a course to view assigned faculty.", font=("Arial", 15), text_color=DARK_BLUE)
        self.assigned_faculty_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        self.assigned_faculty_tree.lower()

    def _on_faculty_course_selected(self, event=None):
        selected_course_code = self.course_combo_faculty.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            self._clear_faculty_lists()
            self.available_faculty_empty_label.configure(text="Select a course to view available faculty.")
            self.available_faculty_empty_label.lift()
            self.available_faculty_tree.lower()
            self.assigned_faculty_empty_label.configure(text="Select a course to view assigned faculty.")
            self.assigned_faculty_empty_label.lift()
            self.assigned_faculty_tree.lower()
            return
        self._refresh_faculty_lists(selected_course_code)

    def _refresh_faculty_lists(self, course_code):
        # Get all faculty and assigned faculty for this course
        all_faculty = self.faculty_controller.get_all_faculty()
        assigned_faculty = self.course_controller.get_assigned_faculty_for_course(course_code)
        assigned_ids = {f['faculty_id'] for f in assigned_faculty}
        self._all_faculty_data = all_faculty
        self._assigned_faculty_data = [f for f in all_faculty if f.faculty_id in assigned_ids]
        self._available_faculty_data = [f for f in all_faculty if f.faculty_id not in assigned_ids]
        self._populate_faculty_tree(self.available_faculty_tree, self._available_faculty_data)
        self._populate_faculty_tree(self.assigned_faculty_tree, self._assigned_faculty_data)
        # Show/hide empty labels
        if not self._available_faculty_data:
            self.available_faculty_empty_label.configure(text="No available faculty.")
            self.available_faculty_empty_label.lift()
            self.available_faculty_tree.lower()
        else:
            self.available_faculty_empty_label.lower()
            self.available_faculty_tree.lift()
        if not self._assigned_faculty_data:
            self.assigned_faculty_empty_label.configure(text="No faculty assigned to this course.")
            self.assigned_faculty_empty_label.lift()
            self.assigned_faculty_tree.lower()
        else:
            self.assigned_faculty_empty_label.lower()
            self.assigned_faculty_tree.lift()

    def _clear_faculty_lists(self):
        for tree in [self.available_faculty_tree, self.assigned_faculty_tree]:
            for i in tree.get_children():
                tree.delete(i)
        self._all_faculty_data = []
        self._assigned_faculty_data = []
        self._available_faculty_data = []

    def _populate_faculty_tree(self, tree, data):
        tree.delete(*tree.get_children())
        for faculty in data:
            tree.insert("", "end", values=(faculty.faculty_id, faculty.name, faculty.email))

    def _filter_available_faculty(self, event=None):
        query = self.faculty_search_var.get().lower()
        filtered = [f for f in self._available_faculty_data if query in f.name.lower() or query in f.email.lower() or query in str(f.faculty_id).lower()]
        self._populate_faculty_tree(self.available_faculty_tree, filtered)
        if not filtered:
            self.available_faculty_empty_label.configure(text="No available faculty match your search.")
            self.available_faculty_empty_label.lift()
            self.available_faculty_tree.lower()
        else:
            self.available_faculty_empty_label.lower()
            self.available_faculty_tree.lift()

    def _filter_assigned_faculty(self, event=None):
        query = self.assigned_faculty_search_var.get().lower()
        filtered = [f for f in self._assigned_faculty_data if query in f.name.lower() or query in f.email.lower() or query in str(f.faculty_id).lower()]
        self._populate_faculty_tree(self.assigned_faculty_tree, filtered)
        if not filtered:
            self.assigned_faculty_empty_label.configure(text="No assigned faculty match your search.")
            self.assigned_faculty_empty_label.lift()
            self.assigned_faculty_tree.lower()
        else:
            self.assigned_faculty_empty_label.lower()
            self.assigned_faculty_tree.lift()

    def _assign_selected_faculty(self):
        selected_course_code = self.course_combo_faculty.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            messagebox.showwarning("No Selection", "Please select a course first.")
            return
        selected = self.available_faculty_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select faculty to assign.")
            return
        for item in selected:
            values = self.available_faculty_tree.item(item)['values']
            faculty_id = values[0]
            self.course_controller.assign_faculty_to_course(selected_course_code, faculty_id)
        self._refresh_faculty_lists(selected_course_code)
        messagebox.showinfo("Success", "Faculty assigned successfully.")

    def _unassign_selected_faculty(self):
        selected_course_code = self.course_combo_faculty.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            messagebox.showwarning("No Selection", "Please select a course first.")
            return
        selected = self.assigned_faculty_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select faculty to unassign.")
            return
        for item in selected:
            values = self.assigned_faculty_tree.item(item)['values']
            faculty_id = values[0]
            self.course_controller.unassign_faculty_from_course(selected_course_code, faculty_id)
        self._refresh_faculty_lists(selected_course_code)
        messagebox.showinfo("Success", "Faculty unassigned successfully.")

    # --- Assign Students Tab ---
    def _create_assign_students_tab(self):
        self.assign_students_frame = self.notebook.add("Assign Students/Batches to Courses")

        title_label = ctk.CTkLabel(self.assign_students_frame, text="Assign Students/Batches to Courses", font=("Arial", 28, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Course selection
        course_select_frame = ctk.CTkFrame(self.assign_students_frame, fg_color=WHITE)
        course_select_frame.pack(pady=5)
        ctk.CTkLabel(course_select_frame, text="Select Course:", font=("Arial", 17), text_color=DARK_BLUE).pack(side="left", padx=5)
        self.course_combo_student = ctk.CTkOptionMenu(course_select_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                                     button_color=BLUE, button_hover_color=DARK_BLUE)
        self.course_combo_student.pack(side="left", padx=5)
        self.course_combo_student.set("Select a course...")
        self.course_combo_student.configure(command=self._on_student_course_selected)

        # Dual-list frame
        dual_list_frame = ctk.CTkFrame(self.assign_students_frame, fg_color=WHITE)
        dual_list_frame.pack(pady=10, fill="both", expand=True)
        dual_list_frame.columnconfigure(0, weight=1)
        dual_list_frame.columnconfigure(1, weight=0)
        dual_list_frame.columnconfigure(2, weight=1)
        dual_list_frame.rowconfigure(1, weight=1)

        # Available Students/Batches
        available_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        available_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=5)
        ctk.CTkLabel(available_frame, text="Available Students/Batches", font=("Arial", 16, "bold"), text_color=DARK_BLUE).pack(pady=(10, 0))
        self.student_search_var = ctk.StringVar()
        student_search_entry = ctk.CTkEntry(available_frame, textvariable=self.student_search_var, placeholder_text="Search...", font=("Arial", 13))
        student_search_entry.pack(padx=10, pady=5, fill="x")
        student_search_entry.bind('<KeyRelease>', self._filter_available_students)
        self.available_students_tree = ttk.Treeview(available_frame, columns=("Type", "ID/Name", "Details"), show="headings", height=12)
        self.available_students_tree.heading("Type", text="Type")
        self.available_students_tree.heading("ID/Name", text="ID/Name")
        self.available_students_tree.heading("Details", text="Details")
        self.available_students_tree.column("Type", width=100, anchor="center")
        self.available_students_tree.column("ID/Name", width=150)
        self.available_students_tree.column("Details", width=200)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        available_scrollbar = ctk.CTkScrollbar(available_frame, orientation="vertical", command=self.available_students_tree.yview)
        self.available_students_tree.configure(yscrollcommand=available_scrollbar.set)
        self.available_students_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        available_scrollbar.pack(side="right", fill="y", pady=10)
        self.available_students_empty_label = ctk.CTkLabel(available_frame, text="Select a course to view available students/batches.", font=("Arial", 15), text_color=DARK_BLUE)
        self.available_students_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        self.available_students_tree.lower()

        # Assign/Unassign buttons
        button_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE)
        button_frame.grid(row=1, column=1, sticky="ns", pady=5)
        button_frame.rowconfigure((0, 1, 2), weight=1)
        self.assign_students_btn = ctk.CTkButton(button_frame, text="Assign →", command=self._assign_selected_students,
                                                fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15), width=120)
        self.assign_students_btn.grid(row=0, column=0, pady=10)
        self.unassign_students_btn = ctk.CTkButton(button_frame, text="← Unassign", command=self._unassign_selected_students,
                                                  fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15), width=120)
        self.unassign_students_btn.grid(row=1, column=0, pady=10)

        # Assigned Students/Batches
        assigned_frame = ctk.CTkFrame(dual_list_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(10, 0), pady=5)
        ctk.CTkLabel(assigned_frame, text="Assigned Students/Batches", font=("Arial", 16, "bold"), text_color=DARK_BLUE).pack(pady=(10, 0))
        self.assigned_students_search_var = ctk.StringVar()
        assigned_search_entry = ctk.CTkEntry(assigned_frame, textvariable=self.assigned_students_search_var, placeholder_text="Search...", font=("Arial", 13))
        assigned_search_entry.pack(padx=10, pady=5, fill="x")
        assigned_search_entry.bind('<KeyRelease>', self._filter_assigned_students)
        self.assigned_students_tree = ttk.Treeview(assigned_frame, columns=("Type", "ID/Name", "Details"), show="headings", height=12)
        self.assigned_students_tree.heading("Type", text="Type")
        self.assigned_students_tree.heading("ID/Name", text="ID/Name")
        self.assigned_students_tree.heading("Details", text="Details")
        self.assigned_students_tree.column("Type", width=100, anchor="center")
        self.assigned_students_tree.column("ID/Name", width=150)
        self.assigned_students_tree.column("Details", width=200)
        assigned_scrollbar = ctk.CTkScrollbar(assigned_frame, orientation="vertical", command=self.assigned_students_tree.yview)
        self.assigned_students_tree.configure(yscrollcommand=assigned_scrollbar.set)
        self.assigned_students_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        assigned_scrollbar.pack(side="right", fill="y", pady=10)
        self.assigned_students_empty_label = ctk.CTkLabel(assigned_frame, text="Select a course to view assigned students/batches.", font=("Arial", 15), text_color=DARK_BLUE)
        self.assigned_students_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        self.assigned_students_tree.lower()

    def _on_student_course_selected(self, event=None):
        selected_course_code = self.course_combo_student.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            self._clear_student_lists()
            self.available_students_empty_label.configure(text="Select a course to view available students/batches.")
            self.available_students_empty_label.lift()
            self.available_students_tree.lower()
            self.assigned_students_empty_label.configure(text="Select a course to view assigned students/batches.")
            self.assigned_students_empty_label.lift()
            self.assigned_students_tree.lower()
            return
        self._refresh_student_lists(selected_course_code)

    def _refresh_student_lists(self, course_code):
        # Get all students, batches, and assigned for this course
        all_students = self.student_controller.get_all_students()
        all_batches = self.student_controller.get_all_batches()
        assigned = self.course_controller.get_assigned_students_batches_for_course(course_code)
        assigned_students = set()
        assigned_batches = set()
        for item in assigned:
            if item['student_id']:
                assigned_students.add(item['student_id'])
            elif item['batch']:
                assigned_batches.add(item['batch'])
        self._all_students_data = all_students
        self._all_batches_data = all_batches
        self._assigned_students_data = [s for s in all_students if s.student_id in assigned_students]
        self._assigned_batches_data = [b for b in all_batches if b in assigned_batches]
        self._available_students_data = [s for s in all_students if s.student_id not in assigned_students]
        self._available_batches_data = [b for b in all_batches if b not in assigned_batches]
        # Merge for treeview display
        self._available_combined = ([{"type": "Student", "id": s.student_id, "name": s.name, "details": s.department} for s in self._available_students_data] +
                                    [{"type": "Batch", "id": b, "name": b, "details": "Batch Assignment"} for b in self._available_batches_data])
        self._assigned_combined = ([{"type": "Student", "id": s.student_id, "name": s.name, "details": s.department} for s in self._assigned_students_data] +
                                   [{"type": "Batch", "id": b, "name": b, "details": "Batch Assignment"} for b in self._assigned_batches_data])
        self._populate_students_tree(self.available_students_tree, self._available_combined)
        self._populate_students_tree(self.assigned_students_tree, self._assigned_combined)
        # Show/hide empty labels
        if not self._available_combined:
            self.available_students_empty_label.configure(text="No available students or batches.")
            self.available_students_empty_label.lift()
            self.available_students_tree.lower()
        else:
            self.available_students_empty_label.lower()
            self.available_students_tree.lift()
        if not self._assigned_combined:
            self.assigned_students_empty_label.configure(text="No students or batches assigned to this course.")
            self.assigned_students_empty_label.lift()
            self.assigned_students_tree.lower()
        else:
            self.assigned_students_empty_label.lower()
            self.assigned_students_tree.lift()

    def _clear_student_lists(self):
        for tree in [self.available_students_tree, self.assigned_students_tree]:
            for i in tree.get_children():
                tree.delete(i)
        self._all_students_data = []
        self._all_batches_data = []
        self._assigned_students_data = []
        self._assigned_batches_data = []
        self._available_students_data = []
        self._available_batches_data = []
        self._available_combined = []
        self._assigned_combined = []

    def _populate_students_tree(self, tree, data):
        tree.delete(*tree.get_children())
        for item in data:
            tree.insert("", "end", values=(item["type"], item["id"], item["details"]))

    def _filter_available_students(self, event=None):
        query = self.student_search_var.get().lower()
        filtered = [item for item in self._available_combined if query in item["name"].lower() or query in str(item["id"]).lower() or query in item["details"].lower()]
        self._populate_students_tree(self.available_students_tree, filtered)
        if not filtered:
            self.available_students_empty_label.configure(text="No available students or batches match your search.")
            self.available_students_empty_label.lift()
            self.available_students_tree.lower()
        else:
            self.available_students_empty_label.lower()
            self.available_students_tree.lift()

    def _filter_assigned_students(self, event=None):
        query = self.assigned_students_search_var.get().lower()
        filtered = [item for item in self._assigned_combined if query in item["name"].lower() or query in str(item["id"]).lower() or query in item["details"].lower()]
        self._populate_students_tree(self.assigned_students_tree, filtered)
        if not filtered:
            self.assigned_students_empty_label.configure(text="No assigned students or batches match your search.")
            self.assigned_students_empty_label.lift()
            self.assigned_students_tree.lower()
        else:
            self.assigned_students_empty_label.lower()
            self.assigned_students_tree.lift()

    def _assign_selected_students(self):
        selected_course_code = self.course_combo_student.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            messagebox.showwarning("No Selection", "Please select a course first.")
            return
        selected = self.available_students_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select students or batches to assign.")
            return
        for item in selected:
            values = self.available_students_tree.item(item)['values']
            if values[0] == "Student":
                self.course_controller.assign_student_to_course(selected_course_code, values[1])
            elif values[0] == "Batch":
                self.course_controller.assign_batch_to_course(selected_course_code, values[1])
        self._refresh_student_lists(selected_course_code)
        messagebox.showinfo("Success", "Assignment successful.")

    def _unassign_selected_students(self):
        selected_course_code = self.course_combo_student.get()
        if selected_course_code == "Select a course..." or not selected_course_code:
            messagebox.showwarning("No Selection", "Please select a course first.")
            return
        selected = self.assigned_students_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select students or batches to unassign.")
            return
        for item in selected:
            values = self.assigned_students_tree.item(item)['values']
            if values[0] == "Student":
                self.course_controller.unassign_student_from_course(selected_course_code, values[1])
            elif values[0] == "Batch":
                self.course_controller.unassign_batch_from_course(selected_course_code, values[1])
        self._refresh_student_lists(selected_course_code)
        messagebox.showinfo("Success", "Unassignment successful.")

    # --- Assignments Overview Tab ---
    def _create_assignments_overview_tab(self):
        self.overview_frame = self.notebook.add("Course Overview")

        title_label = ctk.CTkLabel(self.overview_frame, text="Course Assignments Overview", font=("Arial", 28, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Filter controls
        filter_frame = ctk.CTkFrame(self.overview_frame, fg_color=WHITE)
        filter_frame.pack(pady=5, fill="x", padx=10)
        
        ctk.CTkLabel(filter_frame, text="Filter by Course:", font=("Arial", 17), text_color=DARK_BLUE).pack(side="left", padx=5)
        self.overview_course_combo = ctk.CTkOptionMenu(filter_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                                      button_color=BLUE, button_hover_color=DARK_BLUE)
        self.overview_course_combo.pack(side="left", padx=5)
        self.overview_course_combo.configure(command=self.load_assignments_overview)

        ctk.CTkButton(filter_frame, text="Show All", command=self.load_assignments_overview,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="right", padx=5)

        # Overview list frame with treeview
        overview_list_frame = ctk.CTkFrame(self.overview_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        overview_list_frame.pack(pady=10, fill="both", expand=True, padx=10)
        
        self.overview_tree = ttk.Treeview(overview_list_frame, columns=("Code", "Faculty Count", "Student Count", "Batch Count"), show="headings", height=12)
        self.overview_tree.heading("Code", text="Course Code")
        self.overview_tree.heading("Faculty Count", text="Faculty Count")
        self.overview_tree.heading("Student Count", text="Student Count")
        self.overview_tree.heading("Batch Count", text="Batch Count")
        self.overview_tree.column("Code", width=150, anchor="center")
        self.overview_tree.column("Faculty Count", width=150, anchor="center")
        self.overview_tree.column("Student Count", width=150, anchor="center")
        self.overview_tree.column("Batch Count", width=150, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        overview_scrollbar = ctk.CTkScrollbar(overview_list_frame, orientation="vertical", command=self.overview_tree.yview)
        self.overview_tree.configure(yscrollcommand=overview_scrollbar.set)
        self.overview_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        overview_scrollbar.pack(side="right", fill="y", pady=10)

    def _populate_overview_comboboxes(self):
        """Populates the overview tab comboboxes."""
        courses = self.course_controller.get_all_courses()
        course_codes = [course.course_code for course in courses]
        
        if hasattr(self, 'overview_course_combo'):
            self.overview_course_combo.configure(values=["All Courses"] + course_codes)
            self.overview_course_combo.set("All Courses")

    def load_assignments_overview(self, event=None):
        """Loads the assignments overview for the selected course or all courses."""
        for i in self.overview_tree.get_children():
            self.overview_tree.delete(i)

        selected_course = self.overview_course_combo.get()
        
        if selected_course == "All Courses":
            courses = self.course_controller.get_all_courses()
        else:
            course = self.course_controller.get_course_by_code(selected_course)
            courses = [course] if course else []
        
        for course in courses:
            # Get counts for this course
            faculty_count = len(self.course_controller.get_assigned_faculty_for_course(course.course_code))
            assigned_data = self.course_controller.get_assigned_students_batches_for_course(course.course_code)
            
            student_count = sum(1 for item in assigned_data if item['student_id'])
            batch_count = sum(1 for item in assigned_data if item['batch'] and not item['student_id'])
            
            self.overview_tree.insert("", "end", values=(course.course_code, faculty_count, student_count, batch_count))

    def load_course_combos(self):
        """Loads available course codes into comboboxes for assignment tabs."""
        courses = self.course_controller.get_all_courses()
        self.course_codes = [course.course_code for course in courses]
        if hasattr(self, 'course_combo_faculty'):
            self.course_combo_faculty.configure(values=["Select a course..."] + self.course_codes)
            self.course_combo_faculty.set("Select a course...")
        if hasattr(self, 'course_combo_student'):
            self.course_combo_student.configure(values=["Select a course..."] + self.course_codes)
            self.course_combo_student.set("Select a course...")