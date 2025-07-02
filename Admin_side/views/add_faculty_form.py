# views/add_faculty_form.py
import customtkinter as ctk
from models.faculty_model import Faculty
from datetime import datetime, date
from tkcalendar import Calendar

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AddFacultyForm(ctk.CTkToplevel):
    def __init__(self, parent_window, faculty_controller, refresh_callback, faculty_to_edit=None):
        super().__init__(parent_window)
        self.faculty_controller = faculty_controller
        self.refresh_callback = refresh_callback
        self.faculty_to_edit = faculty_to_edit
        self.title("Edit Faculty Information" if self.faculty_to_edit else "Add New Faculty")
        self.geometry("600x700")
        self.configure(fg_color=GREY)
        self.create_widgets()
        if self.faculty_to_edit:
            self.load_faculty_data()
        self.entries['name'].focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=True)
        ctk.CTkLabel(card, text=self.title(), font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        form_frame = ctk.CTkFrame(card, fg_color=WHITE)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.entries = {}
        row = 0
        def add_field(label, key, show=None, state="normal"):
            ctk.CTkLabel(form_frame, text=label, font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
            entry = ctk.CTkEntry(form_frame, width=280, font=("Arial", 17), show=show)
            entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
            entry.configure(state=state)
            self.entries[key] = entry
        add_field("Faculty ID:", "faculty_id", state="disabled" if self.faculty_to_edit else "normal"); row += 1
        add_field("Name:", "name"); row += 1
        add_field("Email:", "email"); row += 1
        add_field("Password:", "password", show="*"); row += 1
        add_field("Contact No:", "contact_no"); row += 1
        # Date of Birth
        ctk.CTkLabel(form_frame, text="Date of Birth (YYYY-MM-DD):", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        dob_entry = ctk.CTkEntry(form_frame, width=200, font=("Arial", 17))
        dob_entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        self.entries['dob'] = dob_entry
        cal_btn1 = ctk.CTkButton(form_frame, text="📅", width=40, height=32, font=("Arial", 17), command=lambda: self._open_calendar_picker(dob_entry))
        cal_btn1.grid(row=row, column=2, padx=5)
        self.entries['dob_cal_button'] = cal_btn1
        row += 1
        # Gender
        ctk.CTkLabel(form_frame, text="Gender (male/female):", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        gender_entry = ctk.CTkEntry(form_frame, width=120, font=("Arial", 17))
        gender_entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        self.entries['gender'] = gender_entry
        row += 1
        # Joining Date
        ctk.CTkLabel(form_frame, text="Joining Date (YYYY-MM-DD):", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        join_entry = ctk.CTkEntry(form_frame, width=200, font=("Arial", 17))
        join_entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        self.entries['joining_date'] = join_entry
        cal_btn2 = ctk.CTkButton(form_frame, text="📅", width=40, height=32, font=("Arial", 17), command=lambda: self._open_calendar_picker(join_entry))
        cal_btn2.grid(row=row, column=2, padx=5)
        self.entries['joining_date_cal_button'] = cal_btn2
        row += 1
        add_field("Profile Picture URL:", "profile_picture"); row += 1
        ctk.CTkButton(card, text="Save", command=self.save_faculty, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=18)
        form_frame.grid_columnconfigure(1, weight=1)

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
    def load_faculty_data(self):
        if self.faculty_to_edit:
            for attr in ["faculty_id", "name", "email", "password", "contact_no", "dob", "gender", "joining_date", "profile_picture"]:
                entry = self.entries.get(attr)
                if entry:
                    value = getattr(self.faculty_to_edit, attr, None)
                    if value is not None:
                        if attr == "password":
                            entry.delete(0, "end")
                            entry.insert(0, "****")
                        else:
                            entry.delete(0, "end")
                            entry.insert(0, str(value))
    def save_faculty(self):
        data = {attr: entry.get().strip() for attr, entry in self.entries.items() if not attr.endswith('_cal_button')}
        try:
            faculty_id = self.faculty_to_edit.faculty_id if self.faculty_to_edit else (int(data['faculty_id']) if data['faculty_id'] else None)
            if not data['name'] or not data['email'] or not data['password']:
                ctk.CTkMessagebox.show_error("Validation Error", "Name, Email, and Password are required.")
                return
            password_to_save = data['password']
            if self.faculty_to_edit and data['password'] == "****":
                password_to_save = self.faculty_to_edit.password
        except ValueError as e:
            ctk.CTkMessagebox.show_error("Input Error", f"Invalid input for Faculty ID: {e}.")
            return
        new_faculty = Faculty(
            faculty_id=faculty_id,
            name=data['name'],
            email=data['email'],
            password=password_to_save,
            contact_no=data['contact_no'],
            dob=data['dob'],
            gender=data['gender'],
            joining_date=data['joining_date'],
            profile_picture=data['profile_picture']
        )
        if self.faculty_to_edit:
            success = self.faculty_controller.update_faculty(new_faculty)
            action = "updated"
        else:
            success = self.faculty_controller.add_faculty(new_faculty)
            action = "added"
        if success:
            ctk.CTkMessagebox.show_info("Success", f"Faculty {action} successfully!")
            self.refresh_callback()
            self.on_closing()
        else:
            ctk.CTkMessagebox.show_error("Error", f"Failed to {action} faculty. Please check the input or database connection.")
    def on_closing(self):
        self.destroy()

