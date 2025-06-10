# views/add_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.student_model import Student # Assuming you've created this model
from datetime import datetime

class AddStudentForm(tk.Toplevel):
    def __init__(self, parent_window, student_controller, refresh_callback, student_to_edit=None):
        super().__init__(parent_window)
        self.student_controller = student_controller
        self.refresh_callback = refresh_callback # Callback to refresh the student list
        self.student_to_edit = student_to_edit # Student object if editing

        if self.student_to_edit:
            self.title("Edit Student Information")
        else:
            self.title("Add New Student")

        self.create_widgets()
        if self.student_to_edit:
            self.load_student_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Labels and Entry fields for each student attribute
        # Using a list of (label_text, attribute_name) for brevity
        fields = [
            ("Student ID:", "student_id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"), # Should be hashed in production!
            ("Contact No:", "contact_no"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("Gender (male/female):", "gender"),
            ("Session:", "session"),
            ("Batch:", "batch"),
            ("Enrollment Date (YYYY-MM-DD):", "enrollment_date"),
            ("Department:", "department"),
            ("CGPA (e.g., 3.50):", "cgpa"),
            ("Behavioral Records:", "behavioral_records"),
            ("Profile Picture URL:", "profile_picture"),
        ]

        self.entries = {}
        for i, (text, attr) in enumerate(fields):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[attr] = entry

            # Disable student_id if editing
            if self.student_to_edit and attr == "student_id":
                entry.config(state="disabled")

        # Save Button
        save_button = ttk.Button(form_frame, text="Save", command=self.save_student)
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def load_student_data(self):
        """Loads existing student data into the form fields for editing."""
        if self.student_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.student_to_edit, attr)
                if value is not None:
                    # Special handling for date/decimal types
                    if attr in ("dob", "enrollment_date") and isinstance(value, datetime):
                        entry.insert(0, value.strftime("%Y-%m-%d"))
                    elif attr == "cgpa" and value is not None:
                         entry.insert(0, f"{value:.2f}") # Format CGPA to 2 decimal places
                    else:
                        entry.insert(0, str(value))
            # Re-enable password field if you want it editable (otherwise it's empty)
            self.entries['password'].config(state='normal')


    def save_student(self):
        """Collects data from form and saves/updates student in DB."""
        data = {attr: entry.get().strip() for attr, entry in self.entries.items()}

        # Basic validation and type conversion
        try:
            student_id = int(data['student_id'])
            # Convert empty strings to None for optional fields
            contact_no = data['contact_no'] if data['contact_no'] else None
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            gender = data['gender'] if data['gender'] else None
            session = data['session'] if data['session'] else None
            batch = data['batch'] if data['batch'] else None
            enrollment_date = datetime.strptime(data['enrollment_date'], "%Y-%m-%d").date() if data['enrollment_date'] else None
            cgpa = float(data['cgpa']) if data['cgpa'] else None
            behavioral_records = data['behavioral_records'] if data['behavioral_records'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            # Essential fields check
            if not data['name'] or not data['email'] or not data['password'] or not data['department'] or not data['enrollment_date']:
                messagebox.showerror("Validation Error", "Name, Email, Password, Department, and Enrollment Date are required.")
                return

            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input format: {e}. Please check date/number fields.")
            return

        # Create Student object
        new_student = Student(
            student_id=student_id,
            name=data['name'],
            email=data['email'],
            password=data['password'], # REMEMBER TO HASH THIS IN PRODUCTION!
            contact_no=contact_no,
            dob=dob,
            gender=gender,
            session=session,
            batch=batch,
            enrollment_date=enrollment_date,
            department=data['department'],
            cgpa=cgpa,
            behavioral_records=behavioral_records,
            profile_picture=profile_picture
        )

        if self.student_to_edit:
            # For update, ensure student_id from original object is used
            new_student.student_id = self.student_to_edit.student_id
            success = self.student_controller.update_student(new_student)
            action = "updated"
        else:
            success = self.student_controller.add_student(new_student)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Student {action} successfully!")
            self.refresh_callback() # Refresh the list in HRStudentsPage
            self.destroy() # Close the form window
        else:
            messagebox.showerror("Error", f"Failed to {action} student. Please check the input or database connection.")