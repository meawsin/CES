# views/add_faculty_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.faculty_model import Faculty
from datetime import datetime

class AddFacultyForm(tk.Toplevel):
    def __init__(self, parent_window, faculty_controller, refresh_callback, faculty_to_edit=None):
        super().__init__(parent_window)
        self.faculty_controller = faculty_controller
        self.refresh_callback = refresh_callback
        self.faculty_to_edit = faculty_to_edit

        if self.faculty_to_edit:
            self.title("Edit Faculty Information")
        else:
            self.title("Add New Faculty")

        self.create_widgets()
        if self.faculty_to_edit:
            self.load_faculty_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        fields = [
            ("Faculty ID:", "faculty_id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"), # Should be hashed in production!
            ("Contact No:", "contact_no"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("Gender (male/female):", "gender"),
            ("Joining Date (YYYY-MM-DD):", "joining_date"),
            ("Profile Picture URL:", "profile_picture"),
        ]

        self.entries = {}
        for i, (text, attr) in enumerate(fields):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[attr] = entry

            if self.faculty_to_edit and attr == "faculty_id":
                entry.config(state="disabled")

        save_button = ttk.Button(form_frame, text="Save", command=self.save_faculty)
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def load_faculty_data(self):
        """Loads existing faculty data into the form fields for editing."""
        if self.faculty_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.faculty_to_edit, attr)
                if value is not None:
                    if attr in ("dob", "joining_date") and isinstance(value, datetime):
                        entry.insert(0, value.strftime("%Y-%m-%d"))
                    else:
                        entry.insert(0, str(value))
            self.entries['password'].config(state='normal')

    def save_faculty(self):
        """Collects data from form and saves/updates faculty in DB."""
        data = {attr: entry.get().strip() for attr, entry in self.entries.items()}

        try:
            faculty_id = int(data['faculty_id'])
            contact_no = data['contact_no'] if data['contact_no'] else None
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            gender = data['gender'] if data['gender'] else None
            joining_date = datetime.strptime(data['joining_date'], "%Y-%m-%d").date() if data['joining_date'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            if not data['name'] or not data['email'] or not data['password'] or not data['joining_date']:
                 messagebox.showerror("Validation Error", "Name, Email, Password, and Joining Date are required.")
                 return

            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input format: {e}. Please check date/number fields.")
            return

        new_faculty = Faculty(
            faculty_id=faculty_id,
            name=data['name'],
            email=data['email'],
            password=data['password'],
            contact_no=contact_no,
            dob=dob,
            gender=gender,
            joining_date=joining_date,
            profile_picture=profile_picture
        )

        if self.faculty_to_edit:
            new_faculty.faculty_id = self.faculty_to_edit.faculty_id
            success = self.faculty_controller.update_faculty(new_faculty)
            action = "updated"
        else:
            success = self.faculty_controller.add_faculty(new_faculty)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Faculty {action} successfully!")
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", f"Failed to {action} faculty. Please check the input or database connection.")