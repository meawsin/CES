# views/assign_course_student_form.py
import tkinter as tk
from tkinter import ttk, messagebox

class AssignCourseStudentForm(tk.Toplevel):
    def __init__(self, parent_window, course_controller, student_controller, selected_course_code, refresh_callback):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.student_controller = student_controller
        self.selected_course_code = selected_course_code
        self.refresh_callback = refresh_callback

        self.title(f"Manage Students/Batches for {self.selected_course_code}")
        self.create_widgets()
        self.load_lists()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Tabbed interface for individual students vs. batches
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self._create_student_tab()
        self._create_batch_tab()

        ttk.Button(self, text="Done", command=self.close_form).pack(pady=10)

    def _create_student_tab(self):
        self.student_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.student_tab, text="Individual Students")

        self.student_tab.columnconfigure(0, weight=1)
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
        available_scrollbar.grid(row=1, column=1, sticky="ns")

        # Assign/Unassign Buttons
        button_frame = ttk.Frame(self.student_tab)
        button_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=1)
        button_frame.rowconfigure(2, weight=1)
        button_frame.rowconfigure(3, weight=1)
        ttk.Button(button_frame, text="Assign >>", command=self.assign_student).grid(row=1, column=0, pady=10)
        ttk.Button(button_frame, text="<< Unassign", command=self.unassign_student).grid(row=2, column=0, pady=10)

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
        assigned_scrollbar.grid(row=1, column=3, sticky="ns")

    def _create_batch_tab(self):
        self.batch_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.batch_tab, text="Assign by Batch")

        self.batch_tab.columnconfigure(0, weight=1)
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
        available_batch_scrollbar.grid(row=1, column=1, sticky="ns")

        # Assign/Unassign Buttons
        batch_button_frame = ttk.Frame(self.batch_tab)
        batch_button_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        batch_button_frame.rowconfigure(0, weight=1)
        batch_button_frame.rowconfigure(1, weight=1)
        batch_button_frame.rowconfigure(2, weight=1)
        batch_button_frame.rowconfigure(3, weight=1)
        ttk.Button(batch_button_frame, text="Assign Batch >>", command=self.assign_batch).grid(row=1, column=0, pady=10)
        ttk.Button(batch_button_frame, text="<< Unassign Batch", command=self.unassign_batch).grid(row=2, column=0, pady=10)

        # Assigned Batches List
        self.assigned_batches_tree = ttk.Treeview(self.batch_tab, columns=("Batch Name", "Department"), show="headings")
        self.assigned_batches_tree.heading("Batch Name", text="Batch Name")
        self.assigned_batches_tree.heading("Department", text="Department")
        self.assigned_batches_tree.column("Batch Name", width=150)
        self.assigned_batches_tree.column("Department", width=150)
        self.assigned_batches_tree.grid(row=1, column=2, sticky="nsew", padx=5)
        assigned_batch_scrollbar = ttk.Scrollbar(self.batch_tab, orient="vertical", command=self.assigned_batches_tree.yview)
        self.assigned_batches_tree.configure(yscrollcommand=assigned_batch_scrollbar.set)
        assigned_batch_scrollbar.grid(row=1, column=3, sticky="ns")

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

        assigned_student_ids = {item['student_id'] for item in assigned_to_course if item['student_id']}

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

        # Get all unique batches from students table
        all_batches_query = "SELECT DISTINCT batch, department FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        all_batches_data = self.student_controller.db.fetch_data(all_batches_query, fetch_all=True)

        assigned_batches_to_course = {item['batch'] for item in self.course_controller.get_assigned_students_batches_for_course(self.selected_course_code) if item['batch'] and item['student_id'] is None}

        for batch_data in all_batches_data:
            batch_name = batch_data['batch']
            department = batch_data['department']
            if batch_name in assigned_batches_to_course:
                self.assigned_batches_tree.insert("", "end", iid=f"assigned_b_{batch_name}", values=(batch_name, department))
            else:
                self.available_batches_tree.insert("", "end", iid=f"available_b_{batch_name}", values=(batch_name, department))

    def assign_student(self):
        selected_items = self.available_students_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select students to assign.")
            return
        for item_iid in selected_items:
            student_id = int(self.available_students_tree.item(item_iid)['values'][0])
            if self.course_controller.assign_student_to_course(self.selected_course_code, student_id):
                pass
            else:
                messagebox.showerror("Error", f"Failed to assign student ID {student_id}. Might already be assigned.")
        self.load_lists()
        self.refresh_callback()

    def unassign_student(self):
        selected_items = self.assigned_students_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select students to unassign.")
            return
        for item_iid in selected_items:
            student_id = int(self.assigned_students_tree.item(item_iid)['values'][0])
            if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign student ID {student_id}?"):
                if self.course_controller.unassign_student_from_course(self.selected_course_code, student_id):
                    pass
                else:
                    messagebox.showerror("Error", f"Failed to unassign student ID {student_id}.")
        self.load_lists()
        self.refresh_callback()

    def assign_batch(self):
        selected_items = self.available_batches_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select batches to assign.")
            return
        for item_iid in selected_items:
            batch_name = self.available_batches_tree.item(item_iid)['values'][0]
            if self.course_controller.assign_batch_to_course(self.selected_course_code, batch_name):
                pass
            else:
                messagebox.showerror("Error", f"Failed to assign batch '{batch_name}'. Might already be assigned.")
        self.load_lists()
        self.refresh_callback()

    def unassign_batch(self):
        selected_items = self.assigned_batches_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select batches to unassign.")
            return
        for item_iid in selected_items:
            batch_name = self.assigned_batches_tree.item(item_iid)['values'][0]
            if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign batch '{batch_name}'?"):
                if self.course_controller.unassign_batch_from_course(self.selected_course_code, batch_name):
                    pass
                else:
                    messagebox.showerror("Error", f"Failed to unassign batch '{batch_name}'.")
        self.load_lists()
        self.refresh_callback()

    def close_form(self):
        self.destroy()