# views/add_student_form.py
import customtkinter as ctk
from models.student_model import Student
from datetime import datetime, date
from controllers.student_controller import StudentController
from tkcalendar import Calendar
from tkinter import messagebox

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#b1b1b1"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AddStudentForm(ctk.CTkToplevel):
    def __init__(self, parent_window, student_controller, refresh_callback, student_to_edit=None):
        super().__init__(parent_window)
        self.student_controller = student_controller
        self.refresh_callback = refresh_callback
        self.student_to_edit = student_to_edit
        self.title("Edit Student Information" if self.student_to_edit else "Add New Student")
        self.geometry("700x800")
        self.configure(fg_color=WHITE)
        self.all_departments = self._get_predefined_departments()
        self.all_sessions = self._generate_sessions()
        self.genders = ["", "male", "female"]
        self.create_widgets()
        if self.student_to_edit:
            self.load_student_data()
        self.entries['name'].focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Always on top, focused, and centered
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _get_predefined_departments(self):
        return ["", "BBA Gen", "Marketing", "Management", "AIS", "ICT", "CSE", "ES", "MCJ", "English", "Law"]
    def _generate_sessions(self):
        current_year = datetime.now().year
        return [f"{start_year}-{str(start_year+1)[-2:]}" for start_year in range(2016, current_year + 1)]
    def field_state(self, key):
        if key == "profile_picture":
            return "normal"  # Always editable
        if self.student_to_edit:
            if key in ["cgpa", "behavioral_records", "session", "batch"]:
                return "normal"
            else:
                return "readonly"
        else:
            if key == "student_id" or key == "batch":
                return "readonly"
            return "normal"
    def field_style(self, key):
        # Returns a dict of style options for readonly vs editable
        if self.field_state(key) == "readonly":
            return {"fg_color": "#f0f0f0"}  # Light grey for readonly
        return {"fg_color": "#ffffff"}      # White for editable
    def create_widgets(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=False)
        ctk.CTkLabel(card, text=self.title(), font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        form_frame = ctk.CTkFrame(card, fg_color=WHITE)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.entries = {}
        self.comboboxes = {}
        row = 0
        def add_field(label, key, show=None):
            ctk.CTkLabel(form_frame, text=label, font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
            entry = ctk.CTkEntry(form_frame, width=280, font=("Arial", 17), show=show, **self.field_style(key))
            entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
            entry.configure(state=self.field_state(key))
            self.entries[key] = entry
        def add_combo(label, key, values):
            ctk.CTkLabel(form_frame, text=label, font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
            combo = ctk.CTkComboBox(form_frame, values=values, font=("Arial", 17), width=280, state=self.field_state(key), **self.field_style(key))
            combo.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
            self.entries[key] = combo
        add_field("Student ID:", "student_id"); row += 1
        add_field("Name:", "name"); row += 1
        add_field("Email:", "email"); row += 1
        add_field("Password:", "password", show="*"); row += 1
        add_field("Contact No:", "contact_no"); row += 1
        # Date of Birth
        ctk.CTkLabel(form_frame, text="Date of Birth (YYYY-MM-DD):", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        dob_entry = ctk.CTkEntry(form_frame, width=200, font=("Arial", 17), **self.field_style("dob"))
        dob_entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        dob_entry.configure(state=self.field_state("dob"))
        self.entries['dob'] = dob_entry
        cal_btn1 = ctk.CTkButton(form_frame, text="\U0001F4C5", width=40, height=32, font=("Arial", 17), command=lambda: self._open_calendar_picker(dob_entry))
        cal_btn1.grid(row=row, column=2, padx=5)
        self.entries['dob_cal_button'] = cal_btn1
        row += 1
        add_combo("Gender:", "gender", self.genders); row += 1
        add_combo("Session:", "session", self.all_sessions); row += 1
        add_combo("Department:", "department", self.all_departments); row += 1
        add_field("Batch:", "batch"); row += 1
        # Enrollment Date
        ctk.CTkLabel(form_frame, text="Enrollment Date (YYYY-MM-DD):", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        enroll_entry = ctk.CTkEntry(form_frame, width=200, font=("Arial", 17), **self.field_style("enrollment_date"))
        enroll_entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        enroll_entry.configure(state=self.field_state("enrollment_date"))
        self.entries['enrollment_date'] = enroll_entry
        cal_btn2 = ctk.CTkButton(form_frame, text="\U0001F4C5", width=40, height=32, font=("Arial", 17), command=lambda: self._open_calendar_picker(enroll_entry))
        cal_btn2.grid(row=row, column=2, padx=5)
        self.entries['enrollment_date_cal_button'] = cal_btn2
        row += 1
        add_field("CGPA (e.g., 3.50):", "cgpa"); row += 1
        add_field("Behavioral Records:", "behavioral_records"); row += 1
        add_field("Profile Picture URL:", "profile_picture"); row += 1
        # Place Save button right after the last field, not at the bottom of the window
        ctk.CTkButton(card, text="Save", command=self.save_student, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=(10, 18), anchor="center")
        form_frame.grid_columnconfigure(1, weight=1)
        self.geometry("700x900")
        self.resizable(False, False)
    def _open_calendar_picker(self, target_entry):
        calendar_window = ctk.CTkToplevel(self)
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
        cal = Calendar(calendar_window, selectmode='day', date_pattern='y-mm-dd', year=initial_date.year if initial_date else datetime.now().year, month=initial_date.month if initial_date else datetime.now().month, day=initial_date.day if initial_date else datetime.now().day)
        cal.pack(pady=10)
        ctk.CTkButton(calendar_window, text="Select Date", command=lambda: on_date_select(cal.get_date()), font=("Arial", 17), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE).pack(pady=5)
        def on_date_select(selected_date_str):
            target_entry.configure(state="normal")
            target_entry.delete(0, "end")
            target_entry.insert(0, selected_date_str)
            calendar_window.destroy()
    def load_student_data(self):
        if self.student_to_edit:
            for attr in ["student_id", "name", "email", "password", "contact_no", "dob", "gender", "session", "department", "batch", "enrollment_date", "cgpa", "behavioral_records", "profile_picture"]:
                entry = self.entries.get(attr)
                value = getattr(self.student_to_edit, attr, None)
                if entry and value is not None:
                    # Handle password field
                    if attr == "password":
                        entry.configure(state="normal")
                        entry.delete(0, "end")
                        entry.insert(0, "****")
                        if self.field_state(attr) == "readonly":
                            entry.configure(state="readonly")
                    # Handle CTkComboBox
                    elif hasattr(entry, 'set') and not hasattr(entry, 'delete'):
                        entry.set(str(value))
                    # Handle CTkEntry
                    elif hasattr(entry, 'delete'):
                        entry.configure(state="normal")
                        entry.delete(0, "end")
                        entry.insert(0, str(value))
                        if self.field_state(attr) == "readonly":
                            entry.configure(state="readonly")
    def save_student(self):
        data = {attr: entry.get().strip() for attr, entry in self.entries.items() if not attr.endswith('_cal_button')}
        try:
            student_id = self.student_to_edit.student_id if self.student_to_edit else (int(data['student_id']) if data['student_id'] else None)
            if not data['name'] or not data['email'] or not data['password']:
                messagebox.showerror("Validation Error", "Name, Email, and Password are required.")
                return
            password_to_save = data['password']
            if self.student_to_edit and data['password'] == "****":
                password_to_save = self.student_to_edit.password
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for Student ID: {e}.")
            return
        new_student = Student(
            student_id=student_id,
            name=data['name'],
            email=data['email'],
            password=password_to_save,
            contact_no=data['contact_no'],
            dob=data['dob'],
            gender=data['gender'],
            session=data['session'],
            department=data['department'],
            batch=data['batch'],
            enrollment_date=data['enrollment_date'],
            cgpa=data['cgpa'],
            behavioral_records=data['behavioral_records'],
            profile_picture=data['profile_picture']
        )
        if self.student_to_edit:
            success = self.student_controller.update_student(new_student)
            action = "updated"
        else:
            success = self.student_controller.add_student(new_student)
            action = "added"
        if success:
            self.on_closing()
            messagebox.showinfo("Success", f"Student {action} successfully!")
            self.refresh_callback()
        else:
            messagebox.showerror("Error", f"Failed to {action} student. Please check the input or database connection.")
    def on_closing(self):
        self.destroy()
