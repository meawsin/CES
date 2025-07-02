# views/hr_faculty_page.py

import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.faculty_controller import FacultyController
from views.add_faculty_form import AddFacultyForm

class HRFacultyPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent_controller = controller
        self.faculty_controller = FacultyController()
        self.configure(fg_color="#ECF0F1")
        self.columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_faculty()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="Manage Faculty", font=("Arial", 40, "bold"), text_color="#1565c0")
        title_label.pack(pady=(18, 8))
        top_bar = ctk.CTkFrame(self, fg_color="#e3f0fa", corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(top_bar, text="Search:", font=("Arial", 15, "bold"), text_color="#1565c0").pack(side="left", padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(top_bar, width=350, font=("Arial", 15), fg_color="white", text_color="#222b3a")
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.filter_faculty)
        ctk.CTkButton(top_bar, text="Add Faculty", command=self.open_add_faculty_form, fg_color="#1565c0", hover_color="#0d47a1", text_color="white", font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Delete Faculty", command=self.delete_selected_faculty, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Refresh List", command=self.load_faculty, fg_color="#1565c0", hover_color="#0d47a1", text_color="white", font=("Arial", 15, "bold"), width=170, height=48).pack(side="right", padx=5, pady=10)

        self.tree = ttk.Treeview(self, columns=(
            "ID", "Name", "Email", "Contact No", "DOB", "Gender", "Joining Date"
        ), show="headings")

        self.tree.heading("ID", text="Faculty ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Contact No", text="Contact No")
        self.tree.heading("DOB", text="DOB")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Joining Date", text="Joining Date")

        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Contact No", width=100)
        self.tree.column("DOB", width=100)
        self.tree.column("Gender", width=80)
        self.tree.column("Joining Date", width=100)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_faculty(self):
        """Fetches and displays all faculty records."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        faculty_members = self.faculty_controller.get_all_faculty()
        self.all_faculty_data = faculty_members

        for faculty in faculty_members:
            # Format date objects for display in Treeview
            dob_str = faculty.dob.strftime("%Y-%m-%d") if faculty.dob else "N/A"
            joining_date_str = faculty.joining_date.strftime("%Y-%m-%d") if faculty.joining_date else "N/A"

            self.tree.insert("", "end", iid=faculty.faculty_id, values=(
                faculty.faculty_id, faculty.name, faculty.email, faculty.contact_no,
                dob_str, faculty.gender, joining_date_str
            ))

    def filter_faculty(self, event=None):
        """Filters faculty displayed in the Treeview based on search input."""
        search_term = self.search_entry.get().strip().lower()

        for i in self.tree.get_children():
            self.tree.delete(i)

        filtered_faculty = [
            f for f in self.all_faculty_data
            if search_term in str(f.faculty_id).lower() or
               search_term in f.name.lower() or
               search_term in f.email.lower()
        ]

        for faculty in filtered_faculty:
            # Format date objects for display in Treeview
            dob_str = faculty.dob.strftime("%Y-%m-%d") if faculty.dob else "N/A"
            joining_date_str = faculty.joining_date.strftime("%Y-%m-%d") if faculty.joining_date else "N/A"

            self.tree.insert("", "end", iid=faculty.faculty_id, values=(
                faculty.faculty_id, faculty.name, faculty.email, faculty.contact_no,
                dob_str, faculty.gender, joining_date_str
            ))

    def open_add_faculty_form(self):
        """Opens a form to add a new faculty member."""
        add_form_window = AddFacultyForm(self.parent_controller.get_root_window(), self.faculty_controller, self.load_faculty)
        self.wait_window_and_refresh(add_form_window)

    def open_edit_faculty_form(self):
        """Opens a form to edit the selected faculty member."""
        # This method is now effectively redundant since the button is removed,
        # but leaving it for now in case you decide to re-enable edit later.
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a faculty member to edit.")
            return

        faculty_id_to_edit = selected_item
        faculty_data = self.faculty_controller.get_faculty_by_id(faculty_id_to_edit)

        if faculty_data:
            edit_form_window = AddFacultyForm(self.parent_controller.get_root_window(), self.faculty_controller, self.load_faculty, faculty_to_edit=faculty_data)
            self.wait_window_and_refresh(edit_form_window)
        else:
            messagebox.showerror("Error", f"Could not retrieve faculty data for editing (ID: {faculty_id_to_edit}). Check if faculty exists or for DB errors.")

    def delete_selected_faculty(self):
        """Deletes the selected faculty member."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a faculty member to delete.")
            return

        faculty_id_to_delete = selected_item
        faculty_name_to_delete = self.tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete faculty: {faculty_name_to_delete} (ID: {faculty_id_to_delete})?"):
            success = self.faculty_controller.delete_faculty(faculty_id_to_delete)
            if success:
                messagebox.showinfo("Success", "Faculty deleted successfully.")
                self.load_faculty()
            else:
                messagebox.showerror("Error", "Failed to delete faculty. This might happen if the faculty is referenced in other tables (e.g., in course_faculty). Please ensure no dependencies exist or manually remove them if necessary, then retry.")

    def wait_window_and_refresh(self, window):
        """Helper method to wait for a Toplevel window to close and then refresh the faculty list."""
        self.parent_controller.get_root_window().wait_window(window)
        self.load_faculty()

