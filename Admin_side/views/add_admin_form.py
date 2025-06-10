# views/add_admin_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.admin_model import Admin # Assuming Admin model is defined

class AddAdminForm(tk.Toplevel):
    def __init__(self, parent_window, admin_controller, refresh_callback, admin_to_edit=None):
        super().__init__(parent_window)
        self.admin_controller = admin_controller
        self.refresh_callback = refresh_callback
        self.admin_to_edit = admin_to_edit

        if self.admin_to_edit:
            self.title("Edit Admin Information")
        else:
            self.title("Add New Admin")

        self.create_widgets()
        if self.admin_to_edit:
            self.load_admin_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Basic Info Fields
        row_idx = 0
        self.entries = {}

        ttk.Label(form_frame, text="Admin ID:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['admin_id'] = ttk.Entry(form_frame, width=30)
        self.entries['admin_id'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        if self.admin_to_edit:
            self.entries['admin_id'].config(state="disabled")
        row_idx += 1

        ttk.Label(form_frame, text="Name:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['name'] = ttk.Entry(form_frame, width=30)
        self.entries['name'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(form_frame, text="Email:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['email'] = ttk.Entry(form_frame, width=30)
        self.entries['email'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(form_frame, text="Password:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['password'] = ttk.Entry(form_frame, width=30, show="*") # Show stars for password
        self.entries['password'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(form_frame, text="Contact No:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['contact_no'] = ttk.Entry(form_frame, width=30)
        self.entries['contact_no'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Permissions Checkboxes
        ttk.Label(form_frame, text="Permissions:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=10, sticky="w")
        row_idx += 1

        self.permission_vars = {
            "can_create_templates": tk.BooleanVar(),
            "can_view_reports": tk.BooleanVar(),
            "can_manage_users": tk.BooleanVar(),
            "can_manage_courses": tk.BooleanVar(),
            "can_manage_complaints": tk.BooleanVar()
        }

        permission_labels = {
            "can_create_templates": "Create Templates",
            "can_view_reports": "View Reports",
            "can_manage_users": "Manage Users",
            "can_manage_courses": "Manage Courses",
            "can_manage_complaints": "Manage Complaints"
        }

        for attr, label_text in permission_labels.items():
            cb = ttk.Checkbutton(form_frame, text=label_text, variable=self.permission_vars[attr])
            cb.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=2, sticky="w")
            row_idx += 1

        # Save Button
        save_button = ttk.Button(form_frame, text="Save", command=self.save_admin)
        save_button.grid(row=row_idx, column=0, columnspan=2, pady=20)

    def load_admin_data(self):
        """Loads existing admin data into the form fields for editing."""
        if self.admin_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.admin_to_edit, attr)
                if value is not None:
                    entry.insert(0, str(value))
            self.entries['password'].config(state='normal') # Allow password to be edited

            for attr, var in self.permission_vars.items():
                value = getattr(self.admin_to_edit, attr)
                var.set(bool(value)) # Convert 0/1 from DB to True/False

    def save_admin(self):
        """Collects data from form and saves/updates admin in DB."""
        data = {attr: entry.get().strip() for attr, entry in self.entries.items()}
        permissions = {attr: var.get() for attr, var in self.permission_vars.items()}

        try:
            admin_id = int(data['admin_id'])
            contact_no = data['contact_no'] if data['contact_no'] else None

            # Essential fields check
            if not data['name'] or not data['email'] or not data['password']:
                 messagebox.showerror("Validation Error", "Name, Email, and Password are required.")
                 return

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for Admin ID: {e}.")
            return

        new_admin = Admin(
            admin_id=admin_id,
            name=data['name'],
            email=data['email'],
            password=data['password'], # REMEMBER TO HASH THIS IN PRODUCTION!
            contact_no=contact_no,
            can_create_templates=permissions['can_create_templates'],
            can_view_reports=permissions['can_view_reports'],
            can_manage_users=permissions['can_manage_users'],
            can_manage_courses=permissions['can_manage_courses'],
            can_manage_complaints=permissions['can_manage_complaints']
        )

        if self.admin_to_edit:
            # For update, ensure admin_id from original object is used (as it's disabled in form)
            new_admin.admin_id = self.admin_to_edit.admin_id
            success = self.admin_controller.update_admin(new_admin)
            action = "updated"
        else:
            success = self.admin_controller.add_admin(new_admin)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Admin {action} successfully!")
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", f"Failed to {action} admin. Please check the input or database connection.")