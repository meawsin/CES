# views/add_admin_form.py
import customtkinter as ctk
from models.admin_model import Admin

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AddAdminForm(ctk.CTkToplevel):
    def __init__(self, parent_window, admin_controller, refresh_callback, admin_to_edit=None):
        super().__init__(parent_window)
        self.admin_controller = admin_controller
        self.refresh_callback = refresh_callback
        self.admin_to_edit = admin_to_edit
        self.title("Edit Admin Information" if self.admin_to_edit else "Add New Admin")
        self.geometry("550x600")
        self.configure(fg_color=GREY)
        self.create_widgets()
        if self.admin_to_edit:
            self.load_admin_data()
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
            entry = ctk.CTkEntry(form_frame, width=260, font=("Arial", 17), show=show)
            entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
            entry.configure(state=state)
            self.entries[key] = entry
        add_field("Admin ID:", "admin_id", state="disabled" if self.admin_to_edit else "normal"); row += 1
        add_field("Name:", "name"); row += 1
        add_field("Email:", "email"); row += 1
        add_field("Password:", "password", show="*"); row += 1
        add_field("Contact No:", "contact_no"); row += 1
        ctk.CTkLabel(form_frame, text="Permissions:", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=row, column=0, columnspan=2, pady=(18, 8), sticky="w")
        row += 1
        self.permission_vars = {
            "can_create_templates": ctk.BooleanVar(),
            "can_view_reports": ctk.BooleanVar(),
            "can_manage_users": ctk.BooleanVar(),
            "can_manage_courses": ctk.BooleanVar(),
            "can_manage_complaints": ctk.BooleanVar()
        }
        permission_labels = {
            "can_create_templates": "Create Templates",
            "can_view_reports": "View Reports",
            "can_manage_users": "Manage Users",
            "can_manage_courses": "Manage Courses",
            "can_manage_complaints": "Manage Complaints"
        }
        for attr, label_text in permission_labels.items():
            cb = ctk.CTkCheckBox(form_frame, text=label_text, variable=self.permission_vars[attr], font=("Arial", 17), text_color=DARK_BLUE)
            cb.grid(row=row, column=0, columnspan=2, sticky="w", pady=2, padx=5)
            row += 1
        form_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(card, text="Save", command=self.save_admin, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=18)

    def load_admin_data(self):
        if self.admin_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.admin_to_edit, attr)
                if value is not None:
                    if attr == "password":
                        entry.delete(0, "end")
                        entry.insert(0, "****")
                    else:
                        entry.delete(0, "end")
                        entry.insert(0, str(value))
            for attr, var in self.permission_vars.items():
                value = getattr(self.admin_to_edit, attr)
                var.set(bool(value))

    def save_admin(self):
        data = {attr: entry.get().strip() for attr, entry in self.entries.items()}
        permissions = {attr: var.get() for attr, var in self.permission_vars.items()}
        try:
            admin_id = self.admin_to_edit.admin_id if self.admin_to_edit else (int(data['admin_id']) if data['admin_id'] else None)
            contact_no = data['contact_no'] if data['contact_no'] else None
            if not data['name'] or not data['email'] or not data['password']:
                 ctk.CTkMessagebox.show_error("Validation Error", "Name, Email, and Password are required.")
                 return
            password_to_save = data['password']
            if self.admin_to_edit and data['password'] == "****":
                password_to_save = self.admin_to_edit.password
        except ValueError as e:
            ctk.CTkMessagebox.show_error("Input Error", f"Invalid input for Admin ID: {e}.")
            return
        new_admin = Admin(
            admin_id=admin_id,
            name=data['name'],
            email=data['email'],
            password=password_to_save,
            contact_no=contact_no,
            can_create_templates=permissions['can_create_templates'],
            can_view_reports=permissions['can_view_reports'],
            can_manage_users=permissions['can_manage_users'],
            can_manage_courses=permissions['can_manage_courses'],
            can_manage_complaints=permissions['can_manage_complaints']
        )
        if self.admin_to_edit:
            success = self.admin_controller.update_admin(new_admin)
            action = "updated"
        else:
            success = self.admin_controller.add_admin(new_admin)
            action = "added"
        if success:
            ctk.CTkMessagebox.show_info("Success", f"Admin {action} successfully!")
            self.refresh_callback()
            self.on_closing()
        else:
            ctk.CTkMessagebox.show_error("Error", f"Failed to {action} admin. Please check the input (e.g., duplicate Admin ID/Email) or database connection.")
    def on_closing(self):
        self.destroy()

