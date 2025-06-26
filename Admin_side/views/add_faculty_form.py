# views/add_faculty_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.faculty_model import Faculty
from datetime import datetime, date # Import date as well
from tkcalendar import Calendar # NEW: Import Calendar widget

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

        # Define fields with their type (entry or date_entry)
        fields_config = [
            ("Faculty ID:", "faculty_id", "entry"),
            ("Name:", "name", "entry"),
            ("Email:", "email", "entry"),
            ("Password:", "password", "entry"),
            ("Contact No:", "contact_no", "entry"),
            ("Date of Birth (YYYY-MM-DD):", "dob", "date_entry"), # Changed to date_entry
            ("Gender (male/female):", "gender", "entry"), # Kept as entry for now, but can be combo later
            ("Joining Date (YYYY-MM-DD):", "joining_date", "date_entry"), # Changed to date_entry
            ("Profile Picture URL:", "profile_picture", "entry"),
        ]

        # Fields that should be disabled in EDIT mode
        self.disabled_edit_fields = ["faculty_id", "email", "password", "gender", "joining_date"]


        self.entries = {} # Store Entry widgets (and their associated calendar buttons)
        
        for i, (text, attr, widget_type) in enumerate(fields_config):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            if widget_type == "entry":
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[attr] = entry
            elif widget_type == "date_entry": # NEW: Date Entry with Calendar Button
                date_input_frame = ttk.Frame(form_frame)
                date_input_frame.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                date_input_frame.columnconfigure(0, weight=1) # Make entry expand

                date_entry = ttk.Entry(date_input_frame, width=30)
                date_entry.grid(row=0, column=0, sticky="ew")
                self.entries[attr] = date_entry # Store reference to the entry

                # Calendar icon button
                cal_button = ttk.Button(date_input_frame, text="📅", width=3, command=lambda e=date_entry: self._open_calendar_picker(e))
                cal_button.grid(row=0, column=1, sticky="e", padx=(5,0)) # Add some padding from entry
                self.entries[f"{attr}_cal_button"] = cal_button # Store ref to button for disabling

            # Apply disabled state for edit mode if specified
            if self.faculty_to_edit and attr in self.disabled_edit_fields:
                if widget_type == "entry" or widget_type == "date_entry":
                    self.entries[attr].config(state="disabled")
                    # If it's a date_entry, also disable the calendar button
                    if widget_type == "date_entry":
                        if f"{attr}_cal_button" in self.entries:
                            self.entries[f"{attr}_cal_button"].config(state="disabled")

        save_button = ttk.Button(form_frame, text="Save", command=self.save_faculty)
        save_button.grid(row=len(fields_config), column=0, columnspan=2, pady=20)

        # Apply a distinct style for save button in forms for clarity
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])
        save_button.config(style="FormSave.TButton")

    def _open_calendar_picker(self, target_entry):
        """Opens a Toplevel window with a calendar for date selection."""
        calendar_window = tk.Toplevel(self) # Parent is the current Toplevel form
        calendar_window.title("Select Date")
        calendar_window.transient(self) # Make it transient to this form
        calendar_window.grab_set() # Grab focus

        # Get initial date for calendar if present in entry
        initial_date = None
        try:
            current_date_str = target_entry.get().strip()
            if current_date_str:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass # Invalid date format, calendar will default to today

        # Create calendar widget
        cal = Calendar(calendar_window, selectmode='day',
                       date_pattern='y-mm-dd',
                       year=initial_date.year if initial_date else datetime.now().year,
                       month=initial_date.month if initial_date else datetime.now().month,
                       day=initial_date.day if initial_date else datetime.now().day)
        cal.pack(pady=10)

        # Button to confirm selection
        ttk.Button(calendar_window, text="Select Date", command=lambda: on_date_select(cal.get_date())).pack(pady=5)

        def on_date_select(selected_date_str):
            # Enable entry to insert
            target_entry.config(state="normal")
            target_entry.delete(0, tk.END)
            target_entry.insert(0, selected_date_str)
            
            # Restore state if it's a disabled field in edit mode
            for attr_name, entry_ref in self.entries.items():
                if entry_ref == target_entry: # Found the widget
                    if attr_name in self.disabled_edit_fields: # Check if it's a disabled field
                        target_entry.config(state="disabled")
                        # Also re-disable the calendar button if the entry is disabled
                        if f"{attr_name}_cal_button" in self.entries:
                            self.entries[f"{attr_name}_cal_button"].config(state="disabled")
                    break

            calendar_window.destroy() # Close calendar window


        # Center the calendar_window over its parent Toplevel form
        calendar_window.update_idletasks() # Ensure calendar window size is calculated
        
        parent_x = self.winfo_x() # X coord of the main form
        parent_y = self.winfo_y() # Y coord of the main form
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        cal_width = calendar_window.winfo_width()
        cal_height = calendar_window.winfo_height()

        cal_x = parent_x + (parent_width // 2) - (cal_width // 2)
        cal_y = parent_y + (parent_height // 2) - (cal_height // 2)

        calendar_window.geometry(f"{cal_width}x{cal_height}+{int(cal_x)}+{int(cal_y)}")
        
        # Handle window close (X button)
        calendar_window.protocol("WM_DELETE_WINDOW", calendar_window.destroy)


    def load_faculty_data(self):
        """Loads existing faculty data into the form fields for editing."""
        if self.faculty_to_edit:
            faculty_attributes_to_load = [
                "faculty_id", "name", "email", "password", "contact_no", "dob",
                "gender", "joining_date", "profile_picture"
            ]

            for attr in faculty_attributes_to_load:
                entry_widget = self.entries.get(attr)
                if not entry_widget:
                    continue

                value = getattr(self.faculty_to_edit, attr, None)

                is_disabled_field_in_edit = (attr in self.disabled_edit_fields)
                
                # Temporarily enable entry/date_entry
                if is_disabled_field_in_edit:
                    entry_widget.config(state="normal")
                    # For date_entry type, also re-enable the calendar button temporarily
                    if attr in ["dob", "joining_date"] and f"{attr}_cal_button" in self.entries:
                        self.entries[f"{attr}_cal_button"].config(state="normal")

                entry_widget.delete(0, tk.END)

                if value is not None:
                    if attr in ("dob", "joining_date"):
                        if isinstance(value, (datetime, date)):
                            entry_widget.insert(0, value.strftime("%Y-%m-%d"))
                        else:
                            entry_widget.insert(0, str(value))
                    elif attr == "password":
                        entry_widget.insert(0, "****")
                    else:
                        entry_widget.insert(0, str(value))
                else:
                    entry_widget.insert(0, "")

                # Restore disabled state
                if is_disabled_field_in_edit:
                    entry_widget.config(state="disabled")
                    # For date_entry type, also re-disable the calendar button
                    if attr in ["dob", "joining_date"] and f"{attr}_cal_button" in self.entries:
                        self.entries[f"{attr}_cal_button"].config(state="disabled")


    def save_faculty(self):
        """Collects data from form and saves/updates faculty in DB."""
        # Retrieve data from all entries (including date entries)
        data = {attr: self.entries[attr].get().strip() for attr in self.entries if attr not in [f"{f}_cal_button" for f in ["dob", "joining_date"]]}

        try:
            # Handle faculty_id: If adding (self.faculty_to_edit is None) and ID is provided, convert to int.
            # If ID field is empty for new faculty, it will be None, allowing AUTO_INCREMENT.
            faculty_id = self.faculty_to_edit.faculty_id if self.faculty_to_edit else (int(data['faculty_id']) if data['faculty_id'] else None)

            # Retrieve values for non-editable fields (email, password, gender, joining_date)
            # based on whether it's an edit or add operation.
            if self.faculty_to_edit:
                email = self.faculty_to_edit.email
                password_to_save = self.faculty_to_edit.password # Use original hashed password
                gender = self.faculty_to_edit.gender
                joining_date = self.faculty_to_edit.joining_date # Use original date object
            else: # Add mode
                email = data['email']
                password_to_save = data['password']
                gender = data['gender']
                # Parse joining_date for new entry, handle empty string
                joining_date = datetime.strptime(data['joining_date'], "%Y-%m-%d").date() if data['joining_date'] else None


            contact_no = data['contact_no'] if data['contact_no'] else None
            # Parse dob for new entry, handle empty string
            dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data['dob'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            # Essential fields validation
            # Check for non-empty string for required fields
            if not data['name'] or not email or not password_to_save or not joining_date:
                 messagebox.showerror("Validation Error", "Name, Email, Password, and Joining Date are required.")
                 return

            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            # Catch specific date parsing errors
            if "time data ''" in str(e) and ("dob" in str(e) or "joining_date" in str(e)):
                 messagebox.showerror("Input Error", "Date of Birth and Joining Date must be in YYYY-MM-DD format, or left empty if optional.")
            else:
                messagebox.showerror("Input Error", f"Invalid input format: {e}. Please check date/number fields.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during data processing: {e}")
            return


        new_faculty = Faculty(
            faculty_id=faculty_id, # Will be None if auto-incremented and left blank
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
            messagebox.showerror("Error", f"Failed to {action} faculty. Please check the input or database connection (e.g., duplicate Faculty ID/Email).")

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

