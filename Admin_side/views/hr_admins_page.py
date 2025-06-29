# views/hr_admins_page.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.admin_controller import AdminController # Assuming AdminController
from views.add_admin_form import AddAdminForm

class HRAdminsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.admin_controller = AdminController()

        self.configure(bg="#ECF0F1")
        self.columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_admins()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Manage Admins", font=("Arial", 18, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.pack(pady=10)

        search_frame = ttk.Frame(self, padding="10")
        search_frame.pack(pady=5, fill="x")
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_admins)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(pady=5, fill="x")

        # Use global "General.TButton" style and add icons
        ttk.Button(button_frame, text="Add Admin ➕", command=self.open_add_admin_form, style="General.TButton").pack(side="left", padx=5)
        # Edit Admin Button is removed as per previous request
        ttk.Button(button_frame, text="Delete Admin 🗑️", command=self.delete_selected_admin, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh List 🔄", command=self.load_admins, style="General.TButton").pack(side="right", padx=5)

        self.tree = ttk.Treeview(self, columns=(
            "ID", "Name", "Email", "Contact No", "Create Templates", "View Reports",
            "Manage Users", "Manage Courses", "Manage Complaints"
        ), show="headings")

        self.tree.heading("ID", text="Admin ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Contact No", text="Contact No")
        self.tree.heading("Create Templates", text="Create Templates")
        self.tree.heading("View Reports", text="View Reports")
        self.tree.heading("Manage Users", text="Manage Users")
        self.tree.heading("Manage Courses", text="Manage Courses")
        self.tree.heading("Manage Complaints", text="Manage Complaints")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Name", width=120)
        self.tree.column("Email", width=180)
        self.tree.column("Contact No", width=100)
        self.tree.column("Create Templates", width=120, anchor="center")
        self.tree.column("View Reports", width=100, anchor="center")
        self.tree.column("Manage Users", width=100, anchor="center")
        self.tree.column("Manage Courses", width=120, anchor="center")
        self.tree.column("Manage Complaints", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_admins(self):
        """Fetches and displays all admin records."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        admins = self.admin_controller.get_all_admins()
        self.all_admins_data = admins

        for admin in admins:
            self.tree.insert("", "end", iid=admin.admin_id, values=(
                admin.admin_id, admin.name, admin.email, admin.contact_no,
                "Yes" if admin.can_create_templates else "No",
                "Yes" if admin.can_view_reports else "No",
                "Yes" if admin.can_manage_users else "No",
                "Yes" if admin.can_manage_courses else "No",
                "Yes" if admin.can_manage_complaints else "No"
            ))

    def filter_admins(self, event=None):
        """Filters admins displayed in the Treeview based on search input."""
        search_term = self.search_entry.get().strip().lower()

        for i in self.tree.get_children():
            self.tree.delete(i)

        filtered_admins = [
            a for a in self.all_admins_data
            if search_term in str(a.admin_id).lower() or
               search_term in a.name.lower() or
               search_term in a.email.lower()
        ]

        for admin in filtered_admins:
            self.tree.insert("", "end", iid=admin.admin_id, values=(
                admin.admin_id, admin.name, admin.email, admin.contact_no,
                "Yes" if admin.can_create_templates else "No",
                "Yes" if admin.can_view_reports else "No",
                "Yes" if admin.can_manage_users else "No",
                "Yes" if admin.can_manage_courses else "No",
                "Yes" if admin.can_manage_complaints else "No"
            ))

    def open_add_admin_form(self):
        """Opens a form to add a new admin."""
        add_form_window = AddAdminForm(self.parent_controller.get_root_window(), self.admin_controller, self.load_admins)
        self.wait_window_and_refresh(add_form_window) # Use helper to wait and refresh

    def open_edit_admin_form(self):
        """Opens a form to edit the selected admin."""
        # This method is now effectively redundant since the button is removed,
        # but leaving it for now in case you decide to re-enable edit later.
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an admin to edit.")
            return

        admin_id_to_edit = selected_item
        admin_data = self.admin_controller.get_admin_by_id(admin_id_to_edit)

        if admin_data:
            edit_form_window = AddAdminForm(self.parent_controller.get_root_window(), self.admin_controller, self.load_admins, admin_to_edit=admin_data)
            self.wait_window_and_refresh(edit_form_window)
        else:
            messagebox.showerror("Error", f"Could not retrieve admin data for editing (ID: {admin_id_to_edit}). Check if admin exists or for DB errors.")

    def delete_selected_admin(self):
        """Deletes the selected admin."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an admin to delete.")
            return

        admin_id_to_delete = selected_item
        admin_name_to_delete = self.tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete admin: {admin_name_to_delete} (ID: {admin_id_to_delete})?"):
            # Prevent deleting the currently logged-in admin
            if self.parent_controller.get_current_user() and self.parent_controller.get_current_user().admin_id == admin_id_to_delete:
                messagebox.showerror("Error", "Cannot delete the currently logged-in admin account.")
                return

            success = self.admin_controller.delete_admin(admin_id_to_delete)
            if success:
                messagebox.showinfo("Success", "Admin deleted successfully.")
                self.load_admins()
            else:
                messagebox.showerror("Error", "Failed to delete admin. Check database connection or logs.")

    def wait_window_and_refresh(self, window):
        """Helper method to wait for a Toplevel window to close and then refresh the admin list."""
        self.parent_controller.get_root_window().wait_window(window)
        self.load_admins()

