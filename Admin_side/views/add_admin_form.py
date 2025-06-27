# views/add_admin_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.admin_model import Admin

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

        self.transient(parent_window)
        self.grab_set()

        # Set a temporary fixed size to allow widgets to pack, then calculate center
        self.geometry("550x550") # Initial fixed size for consistent appearance

        self.create_widgets()
        if self.admin_to_edit:
            self.load_admin_data()

        self.entries['name'].focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Bind X button to on_closing

        # Crucial step: Update idletasks to ensure the window has finalized its size
        # based on the content and initial geometry() call, before we try to center it.
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

        # Set the geometry again with the calculated position
        self.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")


    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

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
        self.entries['password'] = ttk.Entry(form_frame, width=30, show="*")
        self.entries['password'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(form_frame, text="Contact No:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.entries['contact_no'] = ttk.Entry(form_frame, width=30)
        self.entries['contact_no'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

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

        form_frame.grid_columnconfigure(1, weight=1)

        # Apply a distinct style for save button in forms for clarity
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745") # Greenish save button
        self.style.map("FormSave.TButton", background=[('active', '#218838')])

        save_button = ttk.Button(form_frame, text="Save", command=self.save_admin, style="FormSave.TButton")
        save_button.grid(row=row_idx, column=0, columnspan=2, pady=20)

    def load_admin_data(self):
        if self.admin_to_edit:
            for attr, entry in self.entries.items():
                value = getattr(self.admin_to_edit, attr)
                if value is not None:
                    if attr == "password":
                        entry.delete(0, tk.END)
                        entry.insert(0, "****")
                    else:
                        entry.delete(0, tk.END)
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
                 messagebox.showerror("Validation Error", "Name, Email, and Password are required.")
                 return

            password_to_save = data['password']
            if self.admin_to_edit and data['password'] == "****":
                password_to_save = self.admin_to_edit.password

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for Admin ID: {e}.")
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
            messagebox.showinfo("Success", f"Admin {action} successfully!")
            self.refresh_callback()
            self.on_closing() # Close the Toplevel window
        else:
            messagebox.showerror("Error", f"Failed to {action} admin. Please check the input (e.g., duplicate Admin ID/Email) or database connection.")

    def on_closing(self):
        self.destroy() # Explicitly destroy the Toplevel window

