# views/assign_course_faculty_form.py
import tkinter as tk
from tkinter import ttk, messagebox

class AssignCourseFacultyForm(tk.Toplevel):
    def __init__(self, parent_window, course_controller, faculty_controller, selected_course_code, refresh_callback):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.faculty_controller = faculty_controller
        self.selected_course_code = selected_course_code
        self.refresh_callback = refresh_callback # Callback to refresh the parent treeview (e.g., in CourseSetupPage)

        self.title(f"Manage Faculty for {self.selected_course_code}")

        # Robust Toplevel setup
        self.transient(parent_window)
        self.grab_set()

        self.create_widgets()
        self.load_faculty_lists()

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
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1) # Available list column
        main_frame.columnconfigure(1, weight=0) # Buttons column (fixed size)
        main_frame.columnconfigure(2, weight=1) # Assigned list column
        main_frame.rowconfigure(1, weight=1) # Lists row (expands)

        # Column Headers
        ttk.Label(main_frame, text="Available Faculty", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(main_frame, text="Assigned Faculty", font=("Arial", 12, "bold")).grid(row=0, column=2, pady=5)

        # Available Faculty List (Treeview)
        self.available_faculty_tree = ttk.Treeview(main_frame, columns=("ID", "Name"), show="headings")
        self.available_faculty_tree.heading("ID", text="ID")
        self.available_faculty_tree.heading("Name", text="Name")
        self.available_faculty_tree.column("ID", width=70, anchor="center")
        self.available_faculty_tree.column("Name", width=200)
        self.available_faculty_tree.grid(row=1, column=0, sticky="nsew", padx=5)
        available_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.available_faculty_tree.yview)
        self.available_faculty_tree.configure(yscrollcommand=available_scrollbar.set)
        available_scrollbar.grid(row=1, column=0, sticky="nse", rowspan=1, pady=0, padx=0) # Place scrollbar within column 0, span 1 row

        # Assign/Unassign Buttons (in a central frame)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        button_frame.rowconfigure(0, weight=1) # Push buttons to center vertically
        button_frame.rowconfigure(1, weight=0)
        button_frame.rowconfigure(2, weight=0)
        button_frame.rowconfigure(3, weight=1)

        # Use global "General.TButton" style
        ttk.Button(button_frame, text="Assign >>", command=self.assign_faculty, style="General.TButton").grid(row=1, column=0, pady=10)
        ttk.Button(button_frame, text="<< Unassign", command=self.unassign_faculty, style="General.TButton").grid(row=2, column=0, pady=10)

        # Assigned Faculty List (Treeview)
        self.assigned_faculty_tree = ttk.Treeview(main_frame, columns=("ID", "Name"), show="headings")
        self.assigned_faculty_tree.heading("ID", text="ID")
        self.assigned_faculty_tree.heading("Name", text="Name")
        self.assigned_faculty_tree.column("ID", width=70, anchor="center")
        self.assigned_faculty_tree.column("Name", width=200)
        self.assigned_faculty_tree.grid(row=1, column=2, sticky="nsew", padx=5)
        assigned_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.assigned_faculty_tree.yview)
        self.assigned_faculty_tree.configure(yscrollcommand=assigned_scrollbar.set)
        assigned_scrollbar.grid(row=1, column=2, sticky="nse", rowspan=1, pady=0, padx=0) # Place scrollbar within column 2, span 1 row

        # Done button at the bottom of the Toplevel
        # Use FormSave.TButton for primary action (closing the form after work)
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])
        ttk.Button(self, text="Done", command=self.on_closing, style="FormSave.TButton").pack(pady=10, fill="x", padx=15)


    def load_faculty_lists(self):
        # Clear existing entries
        for i in self.available_faculty_tree.get_children():
            self.available_faculty_tree.delete(i)
        for i in self.assigned_faculty_tree.get_children():
            self.assigned_faculty_tree.delete(i)

        all_faculty = self.faculty_controller.get_all_faculty()
        assigned_faculty_for_course = self.course_controller.get_assigned_faculty_for_course(self.selected_course_code)

        assigned_ids = {f['faculty_id'] for f in assigned_faculty_for_course}

        print(f"DEBUG: Loading faculty lists for course {self.selected_course_code}")
        print(f"DEBUG: All faculty: {[f.faculty_id for f in all_faculty]}")
        print(f"DEBUG: Assigned faculty IDs: {assigned_ids}")


        for faculty in all_faculty:
            if faculty.faculty_id in assigned_ids:
                self.assigned_faculty_tree.insert("", "end", iid=f"assigned_{faculty.faculty_id}", values=(faculty.faculty_id, faculty.name))
            else:
                self.available_faculty_tree.insert("", "end", iid=f"available_{faculty.faculty_id}", values=(faculty.faculty_id, faculty.name))

    def assign_faculty(self):
        selected_items = self.available_faculty_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select faculty to assign.")
            return

        for item_iid in selected_items:
            faculty_id = int(self.available_faculty_tree.item(item_iid)['values'][0])
            print(f"DEBUG: Attempting to assign faculty ID {faculty_id} to course {self.selected_course_code}")
            success = self.course_controller.assign_faculty_to_course(self.selected_course_code, faculty_id)
            if not success:
                messagebox.showerror("Error", f"Failed to assign faculty ID {faculty_id}. Might already be assigned or a database error occurred.")
                print(f"DEBUG: Assignment failed for faculty ID {faculty_id}.")
        self.load_faculty_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def unassign_faculty(self):
        selected_items = self.assigned_faculty_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select faculty to unassign.")
            return

        for item_iid in selected_items:
            faculty_id = int(self.assigned_faculty_tree.item(item_iid)['values'][0])
            print(f"DEBUG: Attempting to unassign faculty ID {faculty_id} from course {self.selected_course_code}")
            if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign faculty ID {faculty_id}?"):
                success = self.course_controller.unassign_faculty_from_course(self.selected_course_code, faculty_id)
                if success:
                    print(f"DEBUG: Unassignment successful for faculty ID {faculty_id}.")
                else:
                    messagebox.showerror("Error", f"Failed to unassign faculty ID {faculty_id}. A database error might have occurred.")
                    print(f"DEBUG: Unassignment failed for faculty ID {faculty_id}.")
        self.load_faculty_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

