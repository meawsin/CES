# views/add_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.student_model import Student
from datetime import datetime

class AddStudentForm(tk.Toplevel):
    def __init__(self, parent_window, student_controller, refresh_callback, student_to_edit=None):
        super().__init__(parent_window)
        self.student_controller = student_controller
        self.refresh_callback = refresh_callback
        self.student_to_edit = student_to_edit
        self.config(bg="#f0f0f0") # Set background for the Toplevel itself

        if self.student_to_edit:
            self.title("Edit Student Information")
        else:
            self.title("Add New Student")

        # Crucial for Toplevel to manage its child frame correctly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        if self.student_to_edit:
            self.load_student_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        # Change .pack() to .grid() and make it expand
        form_frame.grid(row=0, column=0, sticky="nsew") # Use grid to make it fill the Toplevel

        # Labels and Entry fields for each student attribute
        fields = [
            ("Student ID:", "student_id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"),
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

            if self.student_to_edit and attr == "student_id":
                entry.config(state="disabled")

        # Allow the column containing entries to expand
        form_frame.grid_columnconfigure(1, weight=1)

        # Save Button
        save_button = ttk.Button(form_frame, text="Save", command=self.save_student)
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def load_student_data(self):
        # ... (unchanged) ...
        if self.student_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.student_to_edit, attr)
                if value is not None:
                    if attr in ("dob", "enrollment_date"): # Use strftime only if it's a date object
                        if isinstance(value, datetime.date):
                            entry.insert(0, value.strftime("%Y-%m-%d"))
                        else: # If it's already a string from DB, just insert
                            entry.insert(0, str(value))
                    elif attr == "cgpa":
                         entry.insert(0, f"{value:.2f}")
                    else:
                        entry.insert(0, str(value))
            self.entries['password'].config(state='normal')

    def save_student(self):
        # ... (unchanged) ...
        data = {attr: entry.get().strip() for attr, entry in self.entries.items()}

        try:
            # Handle potential empty student_id for new entries if DB auto-increments
            student_id = int(data['student_id']) if data['student_id'] else None # Allow None for auto-increment

            contact_no = data['contact_no'] if data['contact_no'] else None
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            gender = data['gender'] if data['gender'] else None
            session = data['session'] if data['session'] else None
            batch = data['batch'] if data['batch'] else None
            enrollment_date = datetime.strptime(data['enrollment_date'], "%Y-%m-%d").date() if data['enrollment_date'] else None
            cgpa = float(data['cgpa']) if data['cgpa'] else None
            behavioral_records = data['behavioral_records'] if data['behavioral_records'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            # Essential fields check - student_id is AUTO_INCREMENT, so don't require for add
            if not data['name'] or not data['email'] or not data['password'] or not data['department'] or not enrollment_date: # enrollment_date should be a date object here
                 messagebox.showerror("Validation Error", "Name, Email, Password, Department, and Enrollment Date are required.")
                 return

            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input format: {e}. Please check date/number fields.")
            return

        # Create Student object
        # If student_id is None for new entry, DB will auto-increment.
        # Otherwise, use provided ID for existing entry.
        actual_student_id = self.student_to_edit.student_id if self.student_to_edit else student_id

        new_student = Student(
            student_id=actual_student_id,
            name=data['name'],
            email=data['email'],
            password=data['password'],
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
            success = self.student_controller.update_student(new_student)
            action = "updated"
        else:
            success = self.student_controller.add_student(new_student)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Student {action} successfully!")
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", f"Failed to {action} student. Please check the input or database connection (e.g., duplicate Student ID/Email).")