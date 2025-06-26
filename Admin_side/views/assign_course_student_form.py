# views/assign_course_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox

class AssignCourseStudentForm(tk.Toplevel):
    def __init__(self, parent_window, course_controller, student_controller, selected_course_code, refresh_callback):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.student_controller = student_controller # Added to use student_controller methods
        self.selected_course_code = selected_course_code
        self.refresh_callback = refresh_callback

        self.title(f"Manage Students/Batches for {self.selected_course_code}")

        # Robust Toplevel setup
        self.transient(parent_window)
        self.grab_set()

        self.create_widgets()
        self.load_lists()

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

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0) # Buttons column
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Tabbed interface for individual students vs. batches
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self._create_student_tab()
        self._create_batch_tab()

        # Done button at the bottom of the Toplevel
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])
        ttk.Button(self, text="Done", command=self.on_closing, style="FormSave.TButton").pack(pady=10, fill="x", padx=15)


    def _create_student_tab(self):
        self.student_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.student_tab, text="Individual Students")

        self.student_tab.columnconfigure(0, weight=1)
        self.student_tab.columnconfigure(1, weight=0) # Buttons column
        self.student_tab.columnconfigure(2, weight=1)
        self.student_tab.rowconfigure(1, weight=1)

        ttk.Label(self.student_tab, text="Available Students", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(self.student_tab, text="Assigned Students", font=("Arial", 10, "bold")).grid(row=0, column=2, pady=5)

        # Available Students List
        self.available_students_tree = ttk.Treeview(self.student_tab, columns=("ID", "Name", "Batch"), show="headings")
        self.available_students_tree.heading("ID", text="ID")
        self.available_students_tree.heading("Name", text="Name")
        self.available_students_tree.heading("Batch", text="Batch")
        self.available_students_tree.column("ID", width=70, anchor="center")
        self.available_students_tree.column("Name", width=150)
        self.available_students_tree.column("Batch", width=100)
        self.available_students_tree.grid(row=1, column=0, sticky="nsew", padx=5)
        available_scrollbar = ttk.Scrollbar(self.student_tab, orient="vertical", command=self.available_students_tree.yview)
        self.available_students_tree.configure(yscrollcommand=available_scrollbar.set)
        available_scrollbar.grid(row=1, column=0, sticky="nse", rowspan=1, pady=0, padx=0)


        # Assign/Unassign Buttons
        button_frame = ttk.Frame(self.student_tab)
        button_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=0)
        button_frame.rowconfigure(2, weight=0)
        button_frame.rowconfigure(3, weight=1)
        ttk.Button(button_frame, text="Assign >>", command=self.assign_student, style="General.TButton").grid(row=1, column=0, pady=10)
        ttk.Button(button_frame, text="<< Unassign", command=self.unassign_student, style="General.TButton").grid(row=2, column=0, pady=10)

        # Assigned Students List
        self.assigned_students_tree = ttk.Treeview(self.student_tab, columns=("ID", "Name", "Batch"), show="headings")
        self.assigned_students_tree.heading("ID", text="ID")
        self.assigned_students_tree.heading("Name", text="Name")
        self.assigned_students_tree.heading("Batch", text="Batch")
        self.assigned_students_tree.column("ID", width=70, anchor="center")
        self.assigned_students_tree.column("Name", width=150)
        self.assigned_students_tree.column("Batch", width=100)
        self.assigned_students_tree.grid(row=1, column=2, sticky="nsew", padx=5)
        assigned_scrollbar = ttk.Scrollbar(self.student_tab, orient="vertical", command=self.assigned_students_tree.yview)
        self.assigned_students_tree.configure(yscrollcommand=assigned_scrollbar.set)
        assigned_scrollbar.grid(row=1, column=2, sticky="nse", rowspan=1, pady=0, padx=0)

    def _create_batch_tab(self):
        self.batch_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.batch_tab, text="Assign by Batch")

        self.batch_tab.columnconfigure(0, weight=1)
        self.batch_tab.columnconfigure(1, weight=0) # Buttons column
        self.batch_tab.columnconfigure(2, weight=1)
        self.batch_tab.rowconfigure(1, weight=1)

        ttk.Label(self.batch_tab, text="Available Batches", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(self.batch_tab, text="Assigned Batches", font=("Arial", 10, "bold")).grid(row=0, column=2, pady=5)

        # Available Batches List
        self.available_batches_tree = ttk.Treeview(self.batch_tab, columns=("Batch Name", "Department"), show="headings")
        self.available_batches_tree.heading("Batch Name", text="Batch Name")
        self.available_batches_tree.heading("Department", text="Department")
        self.available_batches_tree.column("Batch Name", width=150)
        self.available_batches_tree.column("Department", width=150)
        self.available_batches_tree.grid(row=1, column=0, sticky="nsew", padx=5)
        available_batch_scrollbar = ttk.Scrollbar(self.batch_tab, orient="vertical", command=self.available_batches_tree.yview)
        self.available_batches_tree.configure(yscrollcommand=available_batch_scrollbar.set)
        available_batch_scrollbar.grid(row=1, column=0, sticky="nse", rowspan=1, pady=0, padx=0)


        # Assign/Unassign Buttons
        batch_button_frame = ttk.Frame(self.batch_tab)
        batch_button_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        batch_button_frame.rowconfigure(0, weight=1)
        batch_button_frame.rowconfigure(1, weight=0)
        batch_button_frame.rowconfigure(2, weight=0)
        batch_button_frame.rowconfigure(3, weight=1)
        ttk.Button(batch_button_frame, text="Assign Batch >>", command=self.assign_batch, style="General.TButton").grid(row=1, column=0, pady=10)
        ttk.Button(batch_button_frame, text="<< Unassign Batch", command=self.unassign_batch, style="General.TButton").grid(row=2, column=0, pady=10)

        # Assigned Batches List
        self.assigned_batches_tree = ttk.Treeview(self.batch_tab, columns=("Batch Name", "Department"), show="headings")
        self.assigned_batches_tree.heading("Batch Name", text="Batch Name")
        self.assigned_batches_tree.heading("Department", text="Department")
        self.assigned_batches_tree.column("Batch Name", width=150)
        self.assigned_batches_tree.column("Department", width=150)
        self.assigned_batches_tree.grid(row=1, column=2, sticky="nsew", padx=5)
        assigned_batch_scrollbar = ttk.Scrollbar(self.batch_tab, orient="vertical", command=self.assigned_batches_tree.yview)
        self.assigned_batches_tree.configure(yscrollcommand=assigned_batch_scrollbar.set)
        assigned_batch_scrollbar.grid(row=1, column=2, sticky="nse", rowspan=1, pady=0, padx=0)


    def load_lists(self):
        self._load_student_lists()
        self._load_batch_lists()

    def _load_student_lists(self):
        for i in self.available_students_tree.get_children():
            self.available_students_tree.delete(i)
        for i in self.assigned_students_tree.get_children():
            self.assigned_students_tree.delete(i)

        all_students = self.student_controller.get_all_students()
        assigned_to_course = self.course_controller.get_assigned_students_batches_for_course(self.selected_course_code)

        # Extract student_ids assigned individually
        assigned_student_ids = {item['student_id'] for item in assigned_to_course if item['student_id'] is not None}
        # Extract batches assigned directly (where student_id is NULL)
        assigned_only_batches = {item['batch'] for item in assigned_to_course if item['student_id'] is None and item['batch'] is not None}

        print(f"DEBUG: Selected Course: {self.selected_course_code}")
        print(f"DEBUG: Assigned Individual Student IDs: {assigned_student_ids}")
        print(f"DEBUG: Assigned Only Batches: {assigned_only_batches}")
        print(f"DEBUG: Total students in DB: {len(all_students)}")


        for student in all_students:
            if student.student_id in assigned_student_ids:
                self.assigned_students_tree.insert("", "end", iid=f"assigned_s_{student.student_id}", values=(student.student_id, student.name, student.batch))
            else:
                self.available_students_tree.insert("", "end", iid=f"available_s_{student.student_id}", values=(student.student_id, student.name, student.batch))

    def _load_batch_lists(self):
        for i in self.available_batches_tree.get_children():
            self.available_batches_tree.delete(i)
        for i in self.assigned_batches_tree.get_children():
            self.assigned_batches_tree.delete(i)

        # Get all unique batches from students table using the new method
        all_batches_data = self.student_controller.get_unique_batches_with_departments()
        
        assigned_to_course = self.course_controller.get_assigned_students_batches_for_course(self.selected_course_code)
        # Filter for batch assignments that are NOT linked to a specific student_id
        assigned_batches_to_course = {item['batch'] for item in assigned_to_course if item['batch'] and item['student_id'] is None}

        print(f"DEBUG: All unique batches from students: {all_batches_data}")
        print(f"DEBUG: Batches assigned to course {self.selected_course_code}: {assigned_batches_to_course}")

        for batch_data in all_batches_data:
            batch_name = batch_data['batch']
            department = batch_data['department']
            if batch_name in assigned_batches_to_course:
                self.assigned_batches_tree.insert("", "end", iid=f"assigned_b_{batch_name}", values=(batch_name, department))
            else:
                self.available_batches_tree.insert("", "end", iid=f"available_b_{batch_name}", values=(batch_name, department))

        # Default to batch tab if there are batches to assign
        if all_batches_data and not assigned_batches_to_course: # If there are available batches and none assigned
             self.notebook.select(self.batch_tab) # Select batch tab by default

    def assign_student(self):
        selected_items = self.available_students_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select students to assign.")
            return
        
        for item_iid in selected_items:
            student_id = int(self.available_students_tree.item(item_iid)['values'][0])
            print(f"DEBUG: Attempting to assign student ID {student_id} to course {self.selected_course_code}")
            success = self.course_controller.assign_student_to_course(self.selected_course_code, student_id)
            if not success:
                messagebox.showerror("Error", f"Failed to assign student ID {student_id}. It might already be assigned or a database error occurred.")
                print(f"DEBUG: Assignment failed for student ID {student_id}.")
        self.load_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def unassign_student(self):
        selected_items = self.assigned_students_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select students to unassign.")
            return
        
        for item_iid in selected_items:
            student_id = int(self.assigned_students_tree.item(item_iid)['values'][0])
            print(f"DEBUG: Attempting to unassign student ID {student_id} from course {self.selected_course_code}")
            if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign student ID {student_id}?"):
                success = self.course_controller.unassign_student_from_course(self.selected_course_code, student_id)
                if success:
                    print(f"DEBUG: Unassignment successful for student ID {student_id}.")
                else:
                    messagebox.showerror("Error", f"Failed to unassign student ID {student_id}. A database error might have occurred.")
                    print(f"DEBUG: Unassignment failed for student ID {student_id}.")
        self.load_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def assign_batch(self):
        selected_items = self.available_batches_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select batches to assign.")
            return
        
        for item_iid in selected_items:
            batch_name = self.available_batches_tree.item(item_iid)['values'][0]
            print(f"DEBUG: Attempting to assign batch '{batch_name}' to course {self.selected_course_code}")
            success = self.course_controller.assign_batch_to_course(self.selected_course_code, batch_name)
            if not success:
                messagebox.showerror("Error", f"Failed to assign batch '{batch_name}'. It might already be assigned or a database error occurred.")
                print(f"DEBUG: Assignment failed for batch '{batch_name}'.")
        self.load_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def unassign_batch(self):
        selected_items = self.assigned_batches_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select batches to unassign.")
            return
        
        for item_iid in selected_items:
            batch_name = self.assigned_batches_tree.item(item_iid)['values'][0]
            print(f"DEBUG: Attempting to unassign batch '{batch_name}' from course {self.selected_course_code}")
            if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign batch '{batch_name}'?"):
                success = self.course_controller.unassign_batch_from_course(self.selected_course_code, batch_name)
                if success:
                    print(f"DEBUG: Unassignment successful for batch '{batch_name}'.")
                else:
                    messagebox.showerror("Error", f"Failed to unassign batch '{batch_name}'. A database error might have occurred.")
                    print(f"DEBUG: Unassignment failed for batch '{batch_name}'.")
        self.load_lists() # Reload both lists to reflect changes
        self.refresh_callback() # Refresh parent page's treeview if needed

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

