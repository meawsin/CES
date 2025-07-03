# views/assign_course_student_form.py
import customtkinter as ctk
from tkinter import messagebox, ttk

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AssignCourseStudentForm(ctk.CTkToplevel):
    def __init__(self, parent_window, course_controller, student_controller, selected_course_code, refresh_callback):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.student_controller = student_controller # Added to use student_controller methods
        self.selected_course_code = selected_course_code
        self.refresh_callback = refresh_callback

        self.title(f"Manage Students/Batches for {self.selected_course_code}")

        # Robust Toplevel setup
        self.transient(parent_window)
        self.grab_set()

        self.geometry("900x650")
        self.minsize(700, 400)

        self.create_widgets()
        self.load_lists()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Crucial step: Update idletasks to ensure the window has finalized its size
        self.update_idletasks()

        # Recalculate position to center the Toplevel over its parent
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()

        self_width = self.winfo_width()
        self_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (self_width // 2)
        y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")

    def create_widgets(self):
        # Main card frame
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Title
        title_text = f"Manage Students/Batches for {self.selected_course_code}"
        ctk.CTkLabel(card, text=title_text, font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        
        # Total students label
        self.total_students_label = ctk.CTkLabel(card, text="Total Students Assigned: 0", font=("Arial", 18, "bold"), text_color=BLUE)
        self.total_students_label.pack(pady=(0, 10))
        
        # Main frame
        main_frame = ctk.CTkFrame(card, fg_color=WHITE)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0) # Buttons column
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Tabbed interface for individual students vs. batches
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self._create_student_tab()
        self._create_batch_tab()

        # Done button at the bottom of the Toplevel
        ctk.CTkButton(self, text="Done", command=self.on_closing,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=10, fill="x", padx=15)

    def _create_student_tab(self):
        self.student_tab = self.notebook.add("Individual Students")

        self.student_tab.columnconfigure(0, weight=1)
        self.student_tab.columnconfigure(1, weight=0) # Buttons column
        self.student_tab.columnconfigure(2, weight=1)
        self.student_tab.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.student_tab, text="Available Students", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=0, pady=5)
        ctk.CTkLabel(self.student_tab, text="Assigned Students", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=2, pady=5)

        # Search bar for available students
        self.available_students_search = ctk.CTkEntry(self.student_tab, width=200, placeholder_text="Search...")
        self.available_students_search.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 2))
        self.available_students_search.bind("<KeyRelease>", lambda e: self.filter_students_tree('available'))

        # Search bar for assigned students
        self.assigned_students_search = ctk.CTkEntry(self.student_tab, width=200, placeholder_text="Search...")
        self.assigned_students_search.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 2))
        self.assigned_students_search.bind("<KeyRelease>", lambda e: self.filter_students_tree('assigned'))

        # Available Students List with treeview
        available_frame = ctk.CTkFrame(self.student_tab, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        available_frame.grid(row=2, column=0, sticky="nsew", padx=5)
        available_frame.grid_columnconfigure(0, weight=1)
        available_frame.grid_rowconfigure(0, weight=1)
        
        self.available_students_tree = ttk.Treeview(available_frame, columns=("ID", "Name", "Batch"), show="headings", height=10)
        self.available_students_tree.heading("ID", text="Student ID")
        self.available_students_tree.heading("Name", text="Name")
        self.available_students_tree.heading("Batch", text="Batch")
        self.available_students_tree.column("ID", width=100, anchor="center")
        self.available_students_tree.column("Name", width=150)
        self.available_students_tree.column("Batch", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        available_scrollbar = ctk.CTkScrollbar(available_frame, orientation="vertical", command=self.available_students_tree.yview)
        self.available_students_tree.configure(yscrollcommand=available_scrollbar.set)
        self.available_students_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        available_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        # Assign/Unassign Buttons
        button_frame = ctk.CTkFrame(self.student_tab, fg_color=WHITE)
        button_frame.grid(row=2, column=1, padx=10, sticky="nsew")
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=0)
        button_frame.rowconfigure(2, weight=0)
        button_frame.rowconfigure(3, weight=1)
        
        ctk.CTkButton(button_frame, text="Assign >>", command=self.assign_student,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=1, column=0, pady=10)
        ctk.CTkButton(button_frame, text="<< Unassign", command=self.unassign_student,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=2, column=0, pady=10)

        # Assigned Students List with treeview
        assigned_frame = ctk.CTkFrame(self.student_tab, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_frame.grid(row=2, column=2, sticky="nsew", padx=5)
        assigned_frame.grid_columnconfigure(0, weight=1)
        assigned_frame.grid_rowconfigure(0, weight=1)
        
        self.assigned_students_tree = ttk.Treeview(assigned_frame, columns=("ID", "Name", "Batch"), show="headings", height=10)
        self.assigned_students_tree.heading("ID", text="Student ID")
        self.assigned_students_tree.heading("Name", text="Name")
        self.assigned_students_tree.heading("Batch", text="Batch")
        self.assigned_students_tree.column("ID", width=100, anchor="center")
        self.assigned_students_tree.column("Name", width=150)
        self.assigned_students_tree.column("Batch", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        assigned_scrollbar = ctk.CTkScrollbar(assigned_frame, orientation="vertical", command=self.assigned_students_tree.yview)
        self.assigned_students_tree.configure(yscrollcommand=assigned_scrollbar.set)
        self.assigned_students_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        assigned_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

    def _create_batch_tab(self):
        self.batch_tab = self.notebook.add("Assign by Batch")

        self.batch_tab.columnconfigure(0, weight=1)
        self.batch_tab.columnconfigure(1, weight=0) # Buttons column
        self.batch_tab.columnconfigure(2, weight=1)
        self.batch_tab.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.batch_tab, text="Available Batches", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=0, pady=5)
        ctk.CTkLabel(self.batch_tab, text="Assigned Batches", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=2, pady=5)

        # Search bar for available batches
        self.available_batches_search = ctk.CTkEntry(self.batch_tab, width=200, placeholder_text="Search...")
        self.available_batches_search.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 2))
        self.available_batches_search.bind("<KeyRelease>", lambda e: self.filter_batches_tree('available'))

        # Search bar for assigned batches
        self.assigned_batches_search = ctk.CTkEntry(self.batch_tab, width=200, placeholder_text="Search...")
        self.assigned_batches_search.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 2))
        self.assigned_batches_search.bind("<KeyRelease>", lambda e: self.filter_batches_tree('assigned'))

        # Available Batches List with treeview
        available_batch_frame = ctk.CTkFrame(self.batch_tab, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        available_batch_frame.grid(row=2, column=0, sticky="nsew", padx=5)
        available_batch_frame.grid_columnconfigure(0, weight=1)
        available_batch_frame.grid_rowconfigure(0, weight=1)
        
        self.available_batches_tree = ttk.Treeview(available_batch_frame, columns=("Batch", "Student Count"), show="headings", height=10)
        self.available_batches_tree.heading("Batch", text="Batch")
        self.available_batches_tree.heading("Student Count", text="Student Count")
        self.available_batches_tree.column("Batch", width=150, anchor="center")
        self.available_batches_tree.column("Student Count", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        available_batch_scrollbar = ctk.CTkScrollbar(available_batch_frame, orientation="vertical", command=self.available_batches_tree.yview)
        self.available_batches_tree.configure(yscrollcommand=available_batch_scrollbar.set)
        self.available_batches_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        available_batch_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        # Assign/Unassign Buttons
        batch_button_frame = ctk.CTkFrame(self.batch_tab, fg_color=WHITE)
        batch_button_frame.grid(row=2, column=1, padx=10, sticky="nsew")
        batch_button_frame.rowconfigure(0, weight=1)
        batch_button_frame.rowconfigure(1, weight=0)
        batch_button_frame.rowconfigure(2, weight=0)
        batch_button_frame.rowconfigure(3, weight=1)
        
        ctk.CTkButton(batch_button_frame, text="Assign Batch >>", command=self.assign_batch,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=1, column=0, pady=10)
        ctk.CTkButton(batch_button_frame, text="<< Unassign Batch", command=self.unassign_batch,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=2, column=0, pady=10)

        # Assigned Batches List with treeview
        assigned_batch_frame = ctk.CTkFrame(self.batch_tab, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_batch_frame.grid(row=2, column=2, sticky="nsew", padx=5)
        assigned_batch_frame.grid_columnconfigure(0, weight=1)
        assigned_batch_frame.grid_rowconfigure(0, weight=1)
        
        self.assigned_batches_tree = ttk.Treeview(assigned_batch_frame, columns=("Batch", "Student Count"), show="headings", height=10)
        self.assigned_batches_tree.heading("Batch", text="Batch")
        self.assigned_batches_tree.heading("Student Count", text="Student Count")
        self.assigned_batches_tree.column("Batch", width=150, anchor="center")
        self.assigned_batches_tree.column("Student Count", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        assigned_batch_scrollbar = ctk.CTkScrollbar(assigned_batch_frame, orientation="vertical", command=self.assigned_batches_tree.yview)
        self.assigned_batches_tree.configure(yscrollcommand=assigned_batch_scrollbar.set)
        self.assigned_batches_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        assigned_batch_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

    def load_lists(self):
        self._load_student_lists()
        self._load_batch_lists()
        self.update_total_students_count()

    def _load_student_lists(self):
        # Clear existing entries
        for i in self.available_students_tree.get_children():
            self.available_students_tree.delete(i)
        for i in self.assigned_students_tree.get_children():
            self.assigned_students_tree.delete(i)

        all_students = self.student_controller.get_all_students()
        assigned_to_course = self.course_controller.get_assigned_students_batches_for_course(self.selected_course_code)

        # Extract student_ids assigned individually
        assigned_student_ids = {item['student_id'] for item in assigned_to_course if item['student_id'] is not None}
        # Extract batches assigned directly (where student_id is NULL)
        assigned_only_batches = {item['batch'] for item in assigned_to_course if item['student_id'] is None and item['batch'] is not None}

        print(f"DEBUG: Selected Course: {self.selected_course_code}")
        print(f"DEBUG: Assigned Individual Student IDs: {assigned_student_ids}")
        print(f"DEBUG: Assigned Only Batches: {assigned_only_batches}")
        print(f"DEBUG: Total students in DB: {len(all_students)}")

        # Store student data for later use
        self.available_students = []
        self.assigned_students = []

        for student in all_students:
            if student.student_id in assigned_student_ids:
                self.assigned_students.append(student)
                self.assigned_students_tree.insert("", "end", iid=student.student_id, values=(student.student_id, student.name, student.batch))
            else:
                self.available_students.append(student)
                self.available_students_tree.insert("", "end", iid=student.student_id, values=(student.student_id, student.name, student.batch))

    def _load_batch_lists(self):
        # Clear existing entries
        for i in self.available_batches_tree.get_children():
            self.available_batches_tree.delete(i)
        for i in self.assigned_batches_tree.get_children():
            self.assigned_batches_tree.delete(i)

        # Get all unique batches from students
        all_batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        all_batches_data = self.course_controller.db.fetch_data(all_batches_query, fetch_all=True)
        all_batches = [b['batch'] for b in all_batches_data]

        # Get currently assigned batches for this course
        assigned_to_course = self.course_controller.get_assigned_students_batches_for_course(self.selected_course_code)
        assigned_batches = {item['batch'] for item in assigned_to_course if item['batch'] is not None}

        print(f"DEBUG: All batches: {all_batches}")
        print(f"DEBUG: Assigned batches: {assigned_batches}")

        # Store batch data for later use
        self.available_batches = []
        self.assigned_batches = []

        for batch in all_batches:
            # Count students in this batch
            student_count_query = "SELECT COUNT(*) as count FROM students WHERE batch = %s;"
            count_result = self.course_controller.db.fetch_data(student_count_query, (batch,))
            student_count = count_result[0]['count'] if count_result and len(count_result) > 0 else 0

            if batch in assigned_batches:
                self.assigned_batches.append(batch)
                self.assigned_batches_tree.insert("", "end", iid=batch, values=(batch, student_count))
            else:
                self.available_batches.append(batch)
                self.available_batches_tree.insert("", "end", iid=batch, values=(batch, student_count))

    def update_total_students_count(self):
        # Get all assigned batches and their student counts
        assigned_batches = set()
        batch_student_count = 0
        for item in self.assigned_batches_tree.get_children():
            batch = self.assigned_batches_tree.item(item)['values'][0]
            count = self.assigned_batches_tree.item(item)['values'][1]
            assigned_batches.add(batch)
            batch_student_count += int(count)
        # Get all individually assigned students whose batch is not assigned as a batch
        individual_count = 0
        for item in self.assigned_students_tree.get_children():
            student_batch = self.assigned_students_tree.item(item)['values'][2]
            if student_batch not in assigned_batches:
                individual_count += 1
        total = batch_student_count + individual_count
        self.total_students_label.configure(text=f"Total Students Assigned: {total}")

    def assign_student(self):
        selected_item = self.available_students_tree.focus()
        if not selected_item:
            messagebox.show_warning("No Selection", "Please select a student to assign.")
            return
        
        student_id = int(selected_item)
        student_name = self.available_students_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to assign student ID {student_id} to course {self.selected_course_code}")
        success = self.course_controller.assign_student_to_course(self.selected_course_code, student_id)
        if success:
            self._load_student_lists()
            self._load_batch_lists()
            self.update_total_students_count()
            self.refresh_callback()
        else:
            messagebox.show_error("Error", f"Failed to assign student {student_name} (ID: {student_id}). Might already be assigned or a database error occurred.")

    def unassign_student(self):
        selected_item = self.assigned_students_tree.focus()
        if not selected_item:
            messagebox.show_warning("No Selection", "Please select a student to unassign.")
            return
        
        student_id = int(selected_item)
        student_name = self.assigned_students_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to unassign student ID {student_id} from course {self.selected_course_code}")
        if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign {student_name} (ID: {student_id})?"):
            success = self.course_controller.unassign_student_from_course(self.selected_course_code, student_id)
            if success:
                print(f"DEBUG: Unassignment successful for student ID {student_id}.")
                self._load_student_lists()
                self._load_batch_lists()
                self.update_total_students_count()
                self.refresh_callback()
            else:
                messagebox.show_error("Error", f"Failed to unassign {student_name} (ID: {student_id}). A database error might have occurred.")

    def assign_batch(self):
        selected_item = self.available_batches_tree.focus()
        if not selected_item:
            messagebox.show_warning("No Selection", "Please select a batch to assign.")
            return
        
        batch = selected_item
        student_count = self.available_batches_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to assign batch {batch} to course {self.selected_course_code}")
        if messagebox.askyesno("Confirm Batch Assignment", f"Are you sure you want to assign batch {batch} ({student_count} students) to this course?"):
            success = self.course_controller.assign_batch_to_course(self.selected_course_code, batch)
            if success:
                self._load_student_lists()
                self._load_batch_lists()
                self.update_total_students_count()
                self.refresh_callback()
            else:
                messagebox.show_error("Error", f"Failed to assign batch {batch}. Might already be assigned or a database error occurred.")

    def unassign_batch(self):
        selected_item = self.assigned_batches_tree.focus()
        if not selected_item:
            messagebox.show_warning("No Selection", "Please select a batch to unassign.")
            return
        
        batch = selected_item
        student_count = self.assigned_batches_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to unassign batch {batch} from course {self.selected_course_code}")
        if messagebox.askyesno("Confirm Batch Unassignment", f"Are you sure you want to unassign batch {batch} ({student_count} students) from this course?"):
            success = self.course_controller.unassign_batch_from_course(self.selected_course_code, batch)
            if success:
                print(f"DEBUG: Batch unassignment successful for batch {batch}.")
                self._load_student_lists()
                self._load_batch_lists()
                self.update_total_students_count()
                self.refresh_callback()
            else:
                messagebox.show_error("Error", f"Failed to unassign batch {batch}. A database error might have occurred.")

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

    def filter_students_tree(self, which):
        # which: 'available' or 'assigned'
        if which == 'available':
            search = self.available_students_search.get().lower()
            tree = self.available_students_tree
            data = [(student.student_id, student.name, student.batch) for student in self.available_students]
        else:
            search = self.assigned_students_search.get().lower()
            tree = self.assigned_students_tree
            data = [(student.student_id, student.name, student.batch) for student in self.assigned_students]
        tree.delete(*tree.get_children())
        for row in data:
            if any(search in str(col).lower() for col in row):
                tree.insert("", "end", values=row)

    def filter_batches_tree(self, which):
        # which: 'available' or 'assigned'
        if which == 'available':
            search = self.available_batches_search.get().lower()
            tree = self.available_batches_tree
            data = [(batch, self.available_batches_tree.item(batch)['values'][1]) for batch in self.available_batches_tree.get_children()]
        else:
            search = self.assigned_batches_search.get().lower()
            tree = self.assigned_batches_tree
            data = [(batch, self.assigned_batches_tree.item(batch)['values'][1]) for batch in self.assigned_batches_tree.get_children()]
        tree.delete(*tree.get_children())
        for row in data:
            if any(search in str(col).lower() for col in row):
                tree.insert("", "end", values=row)

