# views/hr_students_page.py

import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controllers.student_controller import StudentController
from views.add_student_form import AddStudentForm

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
DARK_GREY = "#34495e"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"
RED = "#e74c3c"

class HRStudentsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller
        self.student_controller = StudentController()
        self.configure(fg_color=GREY)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="Manage Students", font=("Arial", 40, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=(18, 8))
        # Top bar: search and actions
        top_bar = ctk.CTkFrame(self, fg_color=LIGHT_BLUE, corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(top_bar, text="Search:", font=("Arial", 15, "bold"), text_color=DARK_BLUE).pack(side="left", padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(top_bar, width=350, font=("Arial", 15), fg_color=WHITE, text_color=DARK_GREY)
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.filter_students)
        ctk.CTkButton(top_bar, text="Add Student", command=self.open_add_student_form, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Edit Student", command=self.open_edit_student_form, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Delete Student", command=self.delete_selected_student, fg_color=RED, hover_color="#c0392b", text_color=WHITE, font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Refresh List", command=self.load_students, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        # Table area
        table_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tree = ttk.Treeview(table_frame, columns=(
            "ID", "Name", "Email", "Contact No", "DOB", "Gender",
            "Session", "Batch", "Enroll Date", "Department", "CGPA", "Behavioral Records"
        ), show="headings", height=12)
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Contact No", text="Contact No")
        self.tree.heading("DOB", text="DOB")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Session", text="Session")
        self.tree.heading("Batch", text="Batch")
        self.tree.heading("Enroll Date", text="Enroll Date")
        self.tree.heading("Department", text="Department")
        self.tree.heading("CGPA", text="CGPA")
        self.tree.heading("Behavioral Records", text="Behavioral Records")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Contact No", width=100)
        self.tree.column("DOB", width=100)
        self.tree.column("Gender", width=80)
        self.tree.column("Session", width=100)
        self.tree.column("Batch", width=100)
        self.tree.column("Enroll Date", width=100)
        self.tree.column("Department", width=120)
        self.tree.column("CGPA", width=60, anchor="center")
        self.tree.column("Behavioral Records", width=220)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def load_students(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        students = self.student_controller.get_all_students()
        self.all_students_data = students
        for student in students:
            dob_str = student.dob.strftime("%Y-%m-%d") if student.dob else "N/A"
            enroll_date_str = student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "N/A"
            behavioral_str = student.behavioral_records if student.behavioral_records else ""
            self.tree.insert("", "end", iid=student.student_id, values=(
                student.student_id, student.name, student.email, student.contact_no,
                dob_str, student.gender, student.session, student.batch,
                enroll_date_str, student.department, student.cgpa, behavioral_str
            ))

    def filter_students(self, event=None):
        search_term = self.search_entry.get().strip().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        filtered_students = [
            s for s in self.all_students_data
            if search_term in str(s.student_id).lower() or
               search_term in s.name.lower() or
               search_term in s.email.lower() or
               (s.department and search_term in s.department.lower()) or
               (s.behavioral_records and search_term in s.behavioral_records.lower())
        ]
        for student in filtered_students:
            dob_str = student.dob.strftime("%Y-%m-%d") if student.dob else "N/A"
            enroll_date_str = student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "N/A"
            behavioral_str = student.behavioral_records if student.behavioral_records else ""
            self.tree.insert("", "end", iid=student.student_id, values=(
                student.student_id, student.name, student.email, student.contact_no,
                dob_str, student.gender, student.session, student.batch,
                enroll_date_str, student.department, student.cgpa, behavioral_str
            ))

    def open_add_student_form(self):
        add_form_window = AddStudentForm(self.parent_controller.get_root_window(), self.student_controller, self.load_students)
        self.wait_window_and_refresh(add_form_window)

    def open_edit_student_form(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a student to edit.")
            return
        student_id_to_edit = selected_item
        student_data = self.student_controller.get_student_by_id(student_id_to_edit)
        if student_data:
            edit_form_window = AddStudentForm(self.parent_controller.get_root_window(), self.student_controller, self.load_students, student_to_edit=student_data)
            self.wait_window_and_refresh(edit_form_window)
        else:
            messagebox.showerror("Error", f"Could not retrieve student data for editing (ID: {student_id_to_edit}). This student might not exist in the database or there was a DB connection error.")

    def delete_selected_student(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a student to delete.")
            return
        student_id_to_delete = selected_item
        student_name_to_delete = self.tree.item(selected_item)['values'][1]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student: {student_name_to_delete} (ID: {student_id_to_delete})?"):
            success = self.student_controller.delete_student(student_id_to_delete)
            if success:
                messagebox.showinfo("Success", "Student deleted successfully.")
                self.load_students()
            else:
                messagebox.showerror("Error", "Failed to delete student. This might happen if the student is referenced in other tables (e.g., in course_student, evaluation_completion, or complaints). Please ensure no dependencies exist or manually remove them if necessary, then retry.")

    def wait_window_and_refresh(self, window):
        self.parent_controller.get_root_window().wait_window(window)
        self.load_students()

