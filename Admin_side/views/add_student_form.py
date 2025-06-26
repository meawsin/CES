# views/add_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.student_model import Student
from datetime import datetime, date
from controllers.student_controller import StudentController
from tkcalendar import Calendar

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

        self.all_departments = self._get_predefined_departments()
        self.all_sessions = self._generate_sessions()
        self.genders = ["male", "female"]

        self.create_widgets()

        if self.student_to_edit:
            self.load_student_data()

        if self.student_to_edit and self.entries['name'].cget('state') == 'disabled':
            for field in ["contact_no", "dob", "session", "department", "cgpa", "behavioral_records", "profile_picture"]:
                if field in self.entries and self.entries[field].cget('state') == 'normal':
                    self.entries[field].focus_set()
                    break
        else:
            self.entries['name'].focus_set()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_idletasks()

        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()

        self_width = self.winfo_width()
        self_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (self_width // 2)
        y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")

    def _get_predefined_departments(self):
        return [
            "BBA Gen", "Marketing", "Management", "AIS", "ICT",
            "CSE", "ES", "MCJ", "English", "Law"
        ]

    def _generate_sessions(self):
        current_year = datetime.now().year
        sessions = []
        for start_year in range(2016, current_year + 1):
            end_year = start_year + 1
            sessions.append(f"{start_year}-{str(end_year)[-2:]}")
        return sessions

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.grid(row=0, column=0, sticky="nsew")
        
        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)

        fields_config = [
            ("Student ID:", "student_id", "entry"),
            ("Name:", "name", "entry"),
            ("Email:", "email", "entry"),
            ("Password:", "password", "entry"),
            ("Contact No:", "contact_no", "entry"),
            ("Date of Birth (YYYY-MM-DD):", "dob", "date_entry"),
            ("Gender:", "gender", "combo"),
            ("Session:", "session", "combo"),
            ("Department:", "department", "combo"),
            ("Batch:", "batch", "entry"),
            ("Enrollment Date (YYYY-MM-DD):", "enrollment_date", "date_entry"),
            ("CGPA (e.g., 3.50):", "cgpa", "entry"),
            ("Behavioral Records:", "behavioral_records", "entry"),
            ("Profile Picture URL:", "profile_picture", "entry"),
        ]

        self.disabled_edit_fields = ["student_id", "email", "password", "enrollment_date", "gender", "batch"]

        self.entries = {}
        self.comboboxes = {}
        self.string_vars = {}

        for i, (text, attr, widget_type) in enumerate(fields_config):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if widget_type == "entry":
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[attr] = entry
            elif widget_type == "combo":
                self.string_vars[attr] = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=self.string_vars[attr], state="readonly", width=37)
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.comboboxes[attr] = combo
                
                if attr == "gender":
                    combo['values'] = self.genders
                elif attr == "session":
                    combo['values'] = self.all_sessions
                    combo.bind("<<ComboboxSelected>>", self.generate_batch)
                elif attr == "department":
                    combo['values'] = self.all_departments
                    combo.bind("<<ComboboxSelected>>", self.generate_batch)
                
                self.entries[attr] = combo
            elif widget_type == "date_entry":
                date_input_frame = ttk.Frame(form_frame)
                date_input_frame.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                date_input_frame.columnconfigure(0, weight=1)

                date_entry = ttk.Entry(date_input_frame, width=30)
                date_entry.grid(row=0, column=0, sticky="ew")
                self.entries[attr] = date_entry

                cal_button = ttk.Button(date_input_frame, text="📅", width=3, command=lambda e=date_entry: self._open_calendar_picker(e))
                cal_button.grid(row=0, column=1, sticky="e", padx=(5,0))
                self.entries[f"{attr}_cal_button"] = cal_button

            if self.student_to_edit and attr in self.disabled_edit_fields:
                if widget_type == "entry" or widget_type == "date_entry":
                    self.entries[attr].config(state="disabled")
                    if widget_type == "date_entry":
                        if f"{attr}_cal_button" in self.entries:
                            self.entries[f"{attr}_cal_button"].config(state="disabled")
                elif widget_type == "combo":
                    self.comboboxes[attr].config(state="disabled")
            
            if attr == "batch":
                self.entries['batch'].config(state="disabled")

        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])

        save_button = ttk.Button(form_frame, text="Save", command=self.save_student, style="FormSave.TButton")
        save_button.grid(row=len(fields_config), column=0, columnspan=2, pady=20, sticky="ew")

    def _open_calendar_picker(self, target_entry):
        calendar_window = tk.Toplevel(self)
        calendar_window.title("Select Date")
        calendar_window.transient(self)
        calendar_window.grab_set()

        initial_date = None
        try:
            current_date_str = target_entry.get().strip()
            if current_date_str:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

        cal = Calendar(calendar_window, selectmode='day',
                       date_pattern='y-mm-dd',
                       year=initial_date.year if initial_date else datetime.now().year,
                       month=initial_date.month if initial_date else datetime.now().month,
                       day=initial_date.day if initial_date else datetime.now().day)
        cal.pack(pady=10)

        ttk.Button(calendar_window, text="Select Date", command=lambda: on_date_select(cal.get_date())).pack(pady=5)

        def on_date_select(selected_date_str):
            target_entry.config(state="normal")
            target_entry.delete(0, tk.END)
            target_entry.insert(0, selected_date_str)
            
            for attr_name, entry_ref in self.entries.items():
                if entry_ref == target_entry:
                    if attr_name in self.disabled_edit_fields:
                        target_entry.config(state="disabled")
                        if f"{attr_name}_cal_button" in self.entries:
                            self.entries[f"{attr_name}_cal_button"].config(state="disabled")
                    break

            calendar_window.destroy()

        calendar_window.update_idletasks()
        
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        cal_width = calendar_window.winfo_width()
        cal_height = calendar_window.winfo_height()

        cal_x = parent_x + (parent_width // 2) - (cal_width // 2)
        cal_y = parent_y + (parent_height // 2) - (cal_height // 2)

        calendar_window.geometry(f"{cal_width}x{cal_height}+{int(cal_x)}+{int(cal_y)}")
        
        calendar_window.protocol("WM_DELETE_WINDOW", calendar_window.destroy)

    def generate_batch(self, event=None):
        session = self.string_vars['session'].get()
        department = self.string_vars['department'].get()
        
        batch_prefix_map = {
            "BBA Gen": "BBA", "Marketing": "MKT", "Management": "MGT",
            "AIS": "AIS", "ICT": "BICE", "CSE": "BCSE", "ES": "ES",
            "MCJ": "MCJ", "English": "ENG", "Law": "LAW"
        }
        
        if session and department:
            prefix = batch_prefix_map.get(department)
            if prefix:
                try:
                    session_parts = session.split('-')
                    session_end_year_suffix = ""
                    if len(session_parts) == 2 and len(session_parts[1]) == 2:
                        session_end_year_suffix = session_parts[1]
                    elif len(session_parts) == 2 and len(session_parts[0]) == 4 and len(session_parts[1]) == 2:
                        session_end_year_suffix = session_parts[1]
                    
                    if session_end_year_suffix:
                        generated_batch = f"{prefix}-{session_end_year_suffix}"
                        
                        current_batch_state = self.entries['batch'].cget('state')
                        self.entries['batch'].config(state="normal")
                        self.entries['batch'].delete(0, tk.END)
                        self.entries['batch'].insert(0, generated_batch)
                        self.entries['batch'].config(state=current_batch_state)
                    else:
                        self.entries['batch'].config(state="normal")
                        self.entries['batch'].delete(0, tk.END)
                        self.entries['batch'].config(state="disabled")

                except IndexError:
                    self.entries['batch'].config(state="normal")
                    self.entries['batch'].delete(0, tk.END)
                    self.entries['batch'].config(state="disabled")
            else:
                self.entries['batch'].config(state="normal")
                self.entries['batch'].delete(0, tk.END)
                self.entries['batch'].config(state="disabled")
        else:
            self.entries['batch'].config(state="normal")
            self.entries['batch'].delete(0, tk.END)
            self.entries['batch'].config(state="disabled")

    def load_student_data(self):
        if self.student_to_edit:
            student_attributes_to_load = [
                "student_id", "name", "email", "password", "contact_no", "dob",
                "gender", "session", "batch", "enrollment_date", "department",
                "cgpa", "behavioral_records", "profile_picture"
            ]

            for attr in student_attributes_to_load:
                entry_widget = self.entries.get(attr)
                if not entry_widget:
                    continue

                value = getattr(self.student_to_edit, attr, None)

                is_disabled_field_in_edit = (attr in self.disabled_edit_fields)
                
                if is_disabled_field_in_edit:
                    entry_widget.config(state="normal")
                    if attr in ["dob", "enrollment_date"] and f"{attr}_cal_button" in self.entries:
                        self.entries[f"{attr}_cal_button"].config(state="normal")


                if attr in self.comboboxes:
                    if value is not None:
                        self.string_vars[attr].set(str(value))
                    else:
                        self.string_vars[attr].set("")
                else:
                    entry_widget.delete(0, tk.END)
                    if value is not None:
                        if attr in ("dob", "enrollment_date"):
                            if isinstance(value, (datetime, date)):
                                entry_widget.insert(0, value.strftime("%Y-%m-%d"))
                            else:
                                entry_widget.insert(0, str(value))
                        elif attr == "cgpa":
                            try:
                                entry_widget.insert(0, f"{float(value):.2f}")
                            except (ValueError, TypeError):
                                entry_widget.insert(0, str(value))
                        elif attr == "password":
                            entry_widget.insert(0, "****")
                        else:
                            entry_widget.insert(0, str(value))
                    else:
                        entry_widget.insert(0, "")

                if is_disabled_field_in_edit:
                    entry_widget.config(state="disabled")
                    if attr in ["dob", "enrollment_date"] and f"{attr}_cal_button" in self.entries:
                        self.entries[f"{attr}_cal_button"].config(state="disabled")

            if 'session' in self.string_vars and 'department' in self.string_vars and \
               self.string_vars['session'].get() and self.string_vars['department'].get():
                self.generate_batch()


    def save_student(self):
        # Retrieve data from all widgets, including comboboxes via string_vars
        data = {}
        for attr, entry_widget in self.entries.items():
            # Check if attr is a key in string_vars (meaning it's a Combobox)
            if attr in self.string_vars:
                data[attr] = self.string_vars[attr].get().strip()
            # Check if attr corresponds to a calendar button, skip it as it's not a data field
            elif attr.endswith('_cal_button'):
                continue
            else: # It's an Entry
                data[attr] = entry_widget.get().strip()

        # Debugging: Print collected form data
        print("\n--- Data collected from form for save ---")
        for k, v in data.items():
            print(f"  '{k}': '{v}'")
        print("-----------------------------------------")

        try:
            # Handle student_id: For new, convert from string if provided, else None. For edit, use original.
            student_id = self.student_to_edit.student_id if self.student_to_edit else (int(data['student_id']) if data['student_id'] else None)

            # Conditional assignment for non-editable fields based on edit/add mode
            if self.student_to_edit:
                email = self.student_to_edit.email
                password_to_save = self.student_to_edit.password
                enrollment_date = self.student_to_edit.enrollment_date
                gender = self.student_to_edit.gender
                batch = self.student_to_edit.batch
            else: # Add mode - retrieve from form
                email = data['email']
                password_to_save = data['password']
                # Parse date strings for new entries, handling empty strings
                enrollment_date_str = data['enrollment_date']
                enrollment_date = datetime.strptime(enrollment_date_str, "%Y-%m-%d").date() if enrollment_date_str else None
                gender = data['gender']
                batch = data['batch'] # Use generated batch if adding

            # Parse other fields, handling empty strings or non-numeric input
            contact_no = data['contact_no'] if data['contact_no'] else None
            dob_str = data['dob']
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
            session = data['session']
            department = data['department']
            
            cgpa = None
            if data['cgpa']:
                try:
                    cgpa = float(data['cgpa'])
                except ValueError:
                    raise ValueError(f"CGPA value '{data['cgpa']}' is not a valid number.")

            behavioral_records = data['behavioral_records'] if data['behavioral_records'] else None
            profile_picture = data['profile_picture'] if data['profile_picture'] else None

            # Essential fields validation
            if not data['name']:
                 messagebox.showerror("Validation Error", "Name is required.")
                 return
            if not email:
                 messagebox.showerror("Validation Error", "Email is required.")
                 return
            if not password_to_save:
                 messagebox.showerror("Validation Error", "Password is required.")
                 return
            if not department:
                 messagebox.showerror("Validation Error", "Department is required.")
                 return
            if not enrollment_date:
                 messagebox.showerror("Validation Error", "Enrollment Date is required.")
                 return
            if gender and gender.lower() not in ['male', 'female']:
                messagebox.showerror("Validation Error", "Gender must be 'male' or 'female'.")
                return

        except ValueError as e:
            # Provide more specific error messages for clarity
            messagebox.showerror("Input Error", f"Validation or format error: {e}. Please check your entries.")
            return
        except Exception as e:
            # Catch any unexpected errors during data collection/validation
            messagebox.showerror("Error", f"An unexpected error occurred during data processing: {e}")
            print(f"UNHANDLED EXCEPTION IN save_student: {e}") # Debugging print
            import traceback
            traceback.print_exc() # Print full traceback to console
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
            department=department,
            cgpa=cgpa,
            behavioral_records=behavioral_records,
            profile_picture=profile_picture
        )

        # Debugging: Print the Student object being sent to controller
        print("\n--- Student object being sent to controller ---")
        print(new_student.to_dict())
        print("---------------------------------------------")

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
            print(f"DEBUG: Student {action} failed. Database operation returned False or an error occurred in controller/DB.")


    def on_closing(self):
        self.destroy()
