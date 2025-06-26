# views/add_faculty_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.faculty_model import Faculty
from datetime import datetime, date # Import date as well

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

        self.transient(parent_window)
        self.grab_set()

        # Create widgets first so geometry can be calculated accurately
        self.create_widgets()

        if self.faculty_to_edit:
            self.load_faculty_data()

        self.entries['name'].focus_set()
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
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        fields = [
            ("Faculty ID:", "faculty_id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"),
            ("Contact No:", "contact_no"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("Gender (male/female):", "gender"),
            ("Joining Date (YYYY-MM-DD):", "joining_date"),
            ("Profile Picture URL:", "profile_picture"),
        ]

        # Fields that should be disabled in EDIT mode
        self.disabled_edit_fields = ["faculty_id", "email", "password", "gender", "joining_date"]


        self.entries = {}
        for i, (text, attr) in enumerate(fields):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[attr] = entry

            if self.faculty_to_edit and attr in self.disabled_edit_fields:
                entry.config(state="disabled")

        save_button = ttk.Button(form_frame, text="Save", command=self.save_faculty)
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

        # Apply a distinct style for save button in forms for clarity
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745") # Greenish save button
        self.style.map("FormSave.TButton", background=[('active', '#218838')])
        save_button.config(style="FormSave.TButton")


    def load_faculty_data(self):
        """Loads existing faculty data into the form fields for editing."""
        if self.faculty_to_edit:
            # Attributes from the Faculty model. Ensure these match your model exactly.
            faculty_attributes_to_load = [
                "faculty_id", "name", "email", "password", "contact_no", "dob",
                "gender", "joining_date", "profile_picture"
            ]

            print("\n--- Starting load_faculty_data for edit form ---")
            for attr in faculty_attributes_to_load:
                entry = self.entries.get(attr)
                if not entry:
                    print(f"Warning: No entry widget found for attribute: {attr}. Skipping.")
                    continue

                value = getattr(self.faculty_to_edit, attr, None) # Safely get attribute value

                print(f"  Attempting to load '{attr}': Raw Value='{value}' (Type: {type(value)})")

                # Temporarily enable entry if it's meant to be disabled in edit mode
                is_disabled_field_in_edit = (attr in self.disabled_edit_fields)
                original_state = entry.cget("state")

                if is_disabled_field_in_edit and original_state == "disabled":
                     entry.config(state="normal") # Enable to insert

                entry.delete(0, tk.END)

                if value is not None:
                    if attr in ("dob", "joining_date"):
                        if isinstance(value, (datetime, date)):
                            entry.insert(0, value.strftime("%Y-%m-%d"))
                        else:
                            entry.insert(0, str(value))
                    elif attr == "password":
                        entry.insert(0, "****") # Always mask password
                    else:
                        entry.insert(0, str(value))
                else:
                    entry.insert(0, "") # Insert empty string if value is None

                # Restore disabled state if it was changed
                if is_disabled_field_in_edit and original_state == "disabled":
                    entry.config(state="disabled")
            
            print("--- Finished load_faculty_data (After Fill) ---")
            for attr, entry in self.entries.items():
                print(f"  '{attr}': '{entry.get()}' (State: {entry.cget('state')})")
            print("------------------------------------")


    def save_faculty(self):
        """Collects data from form and saves/updates faculty in DB."""
        data = {attr: self.entries[attr].get().strip() for attr in self.entries}

        try:
            faculty_id = self.faculty_to_edit.faculty_id if self.faculty_to_edit else (int(data['faculty_id']) if data['faculty_id'] else None)

            if self.faculty_to_edit:
                # Use original values for non-editable fields if editing
                email = self.faculty_to_edit.email
                password_to_save = self.faculty_to_edit.password
                gender = self.faculty_to_edit.gender
                joining_date = self.faculty_to_edit.joining_date
            else: # Add mode
                email = data['email']
                password_to_save = data['password']
                gender = data['gender']
                joining_date = datetime.strptime(data['joining_date'], "%Y-%m-%d").date() if data['joining_date'] else None


            contact_no = data['contact_no'] if data['contact_no'] else None
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            if not data['name'] or not email or not password_to_save or not joining_date:
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
            email=email,
            password=password_to_save,
            contact_no=contact_no,
            dob=dob,
            gender=gender,
            joining_date=joining_date,
            profile_picture=profile_picture
        )

        if self.faculty_to_edit:
            success = self.faculty_controller.update_faculty(new_faculty)
            action = "updated"
        else:
            success = self.faculty_controller.add_faculty(new_faculty)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Faculty {action} successfully!")
            self.refresh_callback()
            self.on_closing()
        else:
            messagebox.showerror("Error", f"Failed to {action} faculty. Please check the input or database connection.")

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

