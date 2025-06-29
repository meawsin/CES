# views/hr_students_page.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.student_controller import StudentController
from views.add_student_form import AddStudentForm # Import the form for adding/editing

class HRStudentsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller # Main app controller
        self.student_controller = StudentController() # Student-specific controller

        self.configure(bg="#ECF0F1")
        self.columnconfigure(0, weight=1) # Allow treeview to expand

        self.create_widgets()
        self.load_students() # Load students on page initialization

    def create_widgets(self):
        # Title
        title_label = ttk.Label(self, text="Manage Students", font=("Arial", 18, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.pack(pady=10)

        # Search/Filter Frame
        search_frame = ttk.Frame(self, padding="10")
        search_frame.pack(pady=5, fill="x")

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_students)

        # Buttons Frame
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(pady=5, fill="x")

        # Use global "General.TButton" style and add icons
        ttk.Button(button_frame, text="Add Student ➕", command=self.open_add_student_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Student ✏️", command=self.open_edit_student_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Student 🗑️", command=self.delete_selected_student, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh List 🔄", command=self.load_students, style="General.TButton").pack(side="right", padx=5)


        # Students Treeview (Table) - Will pick up global Treeview styles
        self.tree = ttk.Treeview(self, columns=(
            "ID", "Name", "Email", "Contact No", "DOB", "Gender",
            "Session", "Batch", "Enroll Date", "Department", "CGPA"
        ), show="headings")

        # Define column headings
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

        # Define column widths (adjust as needed)
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


        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_students(self):
        """Fetches and displays all student records in the Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i) # Clear existing entries

        students = self.student_controller.get_all_students()
        self.all_students_data = students # Store for filtering

        for student in students:
            # Convert date objects to string for display in Treeview
            dob_str = student.dob.strftime("%Y-%m-%d") if student.dob else "N/A"
            enroll_date_str = student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "N/A"

            self.tree.insert("", "end", iid=student.student_id, values=(
                student.student_id, student.name, student.email, student.contact_no,
                dob_str, student.gender, student.session, student.batch,
                enroll_date_str, student.department, student.cgpa
            ))

    def filter_students(self, event=None):
        """Filters students displayed in the Treeview based on search input."""
        search_term = self.search_entry.get().strip().lower()

        for i in self.tree.get_children():
            self.tree.delete(i) # Clear current view

        filtered_students = [
            s for s in self.all_students_data
            if search_term in str(s.student_id).lower() or
               search_term in s.name.lower() or
               search_term in s.email.lower() or
               (s.department and search_term in s.department.lower())
        ]

        for student in filtered_students:
            # Convert date objects to string for display in Treeview
            dob_str = student.dob.strftime("%Y-%m-%d") if student.dob else "N/A"
            enroll_date_str = student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "N/A"

            self.tree.insert("", "end", iid=student.student_id, values=(
                student.student_id, student.name, student.email, student.contact_no,
                dob_str, student.gender, student.session, student.batch,
                enroll_date_str, student.department, student.cgpa
            ))

    def open_add_student_form(self):
        """Opens a form to add a new student."""
        add_form_window = AddStudentForm(self.parent_controller.get_root_window(), self.student_controller, self.load_students)
        self.wait_window_and_refresh(add_form_window) # Use helper to wait and refresh

    def open_edit_student_form(self):
        """Opens a form to edit the selected student."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a student to edit.")
            return

        student_id_to_edit = selected_item # selected_item IS the iid
        student_data = self.student_controller.get_student_by_id(student_id_to_edit)

        if student_data:
            edit_form_window = AddStudentForm(self.parent_controller.get_root_window(), self.student_controller, self.load_students, student_to_edit=student_data)
            self.wait_window_and_refresh(edit_form_window)
        else:
            messagebox.showerror("Error", f"Could not retrieve student data for editing (ID: {student_id_to_edit}). This student might not exist in the database or there was a DB connection error.")


    def delete_selected_student(self):
        """Deletes the selected student from the database and updates the list."""
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
        """Helper method to wait for a Toplevel window to close and then refresh the student list."""
        self.parent_controller.get_root_window().wait_window(window)
        self.load_students()

