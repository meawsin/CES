# views/add_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.student_model import Student
from datetime import datetime, date # Import date as well

class AddStudentForm(tk.Toplevel):
    def __init__(self, parent_window, student_controller, refresh_callback, student_to_edit=None):
        super().__init__(parent_window)
        self.student_controller = student_controller
        self.refresh_callback = refresh_callback
        self.student_to_edit = student_to_edit
        self.config(bg="#f0f0f0")

        if self.student_to_edit:
            self.title("Edit Student Information")
        else:
            self.title("Add New Student")

        self.transient(parent_window)
        self.grab_set()

        # Create widgets first so geometry can be calculated accurately
        self.create_widgets()

        if self.student_to_edit:
            self.load_student_data()

        self.entries['name'].focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Force update to calculate actual widget sizes before centering
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

        # Set the geometry (size and position)
        self.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")


    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.grid(row=0, column=0, sticky="nsew")

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

        # Fields that should be disabled in EDIT mode
        self.disabled_edit_fields = ["student_id", "email", "password", "enrollment_date", "gender"]

        self.entries = {}
        for i, (text, attr) in enumerate(fields):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[attr] = entry

            if self.student_to_edit and attr in self.disabled_edit_fields:
                entry.config(state="disabled")

        # Allow the column containing entries to expand
        form_frame.grid_columnconfigure(1, weight=1)

        # Save Button styling
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745")
        self.style.map("FormSave.TButton", background=[('active', '#218838')])

        save_button = ttk.Button(form_frame, text="Save", command=self.save_student, style="FormSave.TButton")
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def load_student_data(self):
        """Loads existing student data into the form fields for editing."""
        if self.student_to_edit:
            # Attributes from the Student model. Ensure these match your model exactly.
            student_attributes_to_load = [
                "student_id", "name", "email", "password", "contact_no", "dob",
                "gender", "session", "batch", "enrollment_date", "department",
                "cgpa", "behavioral_records", "profile_picture"
            ]

            for attr in student_attributes_to_load:
                entry = self.entries.get(attr)
                if not entry:
                    print(f"Warning: No entry widget found for attribute: {attr}")
                    continue

                value = getattr(self.student_to_edit, attr, None) # Safely get attribute value

                # Debugging: Show raw value before processing
                print(f"Loading '{attr}': Raw Value='{value}' (Type: {type(value)})")

                # Temporarily enable entry if it's meant to be disabled in edit mode
                # so that values can be inserted.
                is_disabled_field = (attr in self.disabled_edit_fields)
                if is_disabled_field:
                    entry.config(state="normal") # Enable to insert

                entry.delete(0, tk.END) # Clear existing content

                if value is not None:
                    if attr in ("dob", "enrollment_date"):
                        if isinstance(value, (datetime, date)):
                            entry.insert(0, value.strftime("%Y-%m-%d"))
                        else:
                            entry.insert(0, str(value)) # Fallback if not a date object but has value
                    elif attr == "cgpa":
                        # Ensure CGPA is formatted to two decimal places
                        entry.insert(0, f"{value:.2f}")
                    elif attr == "password":
                        entry.insert(0, "****") # Always mask password
                    else:
                        entry.insert(0, str(value))
                else:
                    entry.insert(0, "") # Insert empty string if value is None

                # Restore disabled state if it's a disabled field
                if is_disabled_field:
                    entry.config(state="disabled")

            # Final debugging print
            print("--- Loaded Student Data for Edit (After Fill) ---")
            for attr, entry in self.entries.items():
                print(f"{attr}: '{entry.get()}' (State: {entry.cget('state')})")
            print("------------------------------------")


    def save_student(self):
        """Collects data from form and saves/updates student in DB."""
        data = {attr: self.entries[attr].get().strip() for attr in self.entries} # Get data from widgets

        try:
            student_id = self.student_to_edit.student_id if self.student_to_edit else (int(data['student_id']) if data['student_id'] else None)

            # For disabled fields in edit mode, use original values from self.student_to_edit
            # For add mode, get values directly from `data`
            if self.student_to_edit:
                email = self.student_to_edit.email
                password_to_save = self.student_to_edit.password
                enrollment_date = self.student_to_edit.enrollment_date
                gender = self.student_to_edit.gender
            else: # Add mode
                email = data['email']
                password_to_save = data['password']
                enrollment_date = datetime.strptime(data['enrollment_date'], "%Y-%m-%d").date() if data['enrollment_date'] else None
                gender = data['gender']


            contact_no = data['contact_no'] if data['contact_no'] else None
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            session = data['session'] if data['session'] else None
            batch = data['batch'] if data['batch'] else None
            cgpa = float(data['cgpa']) if data['cgpa'] else None
            behavioral_records = data['behavioral_records'] if data['behavioral_records'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            # Essential fields validation
            if not data['name'] or not email or not password_to_save or not data['department'] or not enrollment_date:
                 messagebox.showerror("Validation Error", "Name, Email, Password, Department, and Enrollment Date are required.")
                 return

            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input format: {e}. Please check date/number fields.")
            return

        new_student = Student(
            student_id=student_id,
            name=data['name'],
            email=email,
            password=password_to_save,
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
            self.on_closing()
        else:
            messagebox.showerror("Error", f"Failed to {action} student. Please check the input or database connection (e.g., duplicate Student ID/Email).")

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()
