# views/assign_template_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.course_controller import CourseController # To fetch courses/batches
from datetime import datetime

class AssignTemplateForm(tk.Toplevel):
    def __init__(self, parent_window, template_controller, course_controller, refresh_callback, source_template_id=None, admin_id=None):
        super().__init__(parent_window)
        self.template_controller = template_controller
        self.course_controller = course_controller
        self.refresh_callback = refresh_callback
        self.source_template_id = source_template_id # The ID of the template whose questions will be reused
        self.admin_id = admin_id

        self.source_template = self.template_controller.get_template_by_id(self.source_template_id)
        if not self.source_template:
            messagebox.showerror("Error", "Source template not found. Cannot proceed with assignment.")
            self.destroy()
            return

        self.title(f"Assign Template: {self.source_template.title}")

        self.create_widgets()
        self.load_course_batch_data() # Populate comboboxes

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Source Template ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text=self.source_template_id, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Source Template Title:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text=self.source_template.title, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Assign to Course (Optional):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.course_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.course_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Assign to Batch (Optional):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.batch_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.batch_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="New Last Date (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.last_date_entry = ttk.Entry(form_frame, width=30)
        self.last_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        # Pre-fill with current last date if editing an existing assignment
        if self.source_template.last_date:
            self.last_date_entry.insert(0, self.source_template.last_date.strftime("%Y-%m-%d"))

        # Option to just extend deadline for THIS template (if it's already an assignment)
        ttk.Label(form_frame, text="OR Extend Deadline for THIS Assignment:").grid(row=5, column=0, columnspan=2, padx=5, pady=(15,5), sticky="w")
        self.extend_date_entry = ttk.Entry(form_frame, width=30)
        self.extend_date_entry.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        self.extend_date_entry.insert(0, self.source_template.last_date.strftime("%Y-%m-%d") if self.source_template.last_date else "")
        ttk.Button(form_frame, text="Extend Deadline", command=self.extend_deadline).grid(row=6, column=1, padx=5, pady=5, sticky="w")


        ttk.Button(form_frame, text="Create New Assignment", command=self.create_new_assignment).grid(row=7, column=0, columnspan=2, pady=20)


    def load_course_batch_data(self):
        courses = self.course_controller.get_all_courses()
        course_codes = [c.course_code for c in courses]
        self.course_combo['values'] = course_codes

        # Get all unique batches from students table
        all_batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        batches_data = self.course_controller.db.fetch_data(all_batches_query, fetch_all=True)
        batches = [b['batch'] for b in batches_data]
        self.batch_combo['values'] = batches

    def create_new_assignment(self):
        course_code = self.course_combo.get().strip()
        batch = self.batch_combo.get().strip()
        last_date_str = self.last_date_entry.get().strip()

        if not last_date_str:
            messagebox.showerror("Validation Error", "Last Date is required for new assignments.")
            return
        if not course_code and not batch:
            messagebox.showerror("Validation Error", "Either Course Code or Batch must be selected for a new assignment.")
            return

        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid Last Date format. Please use YYYY-MM-DD.")
            return

        success, message = self.template_controller.assign_template_to_course_batch(
            template_id=self.source_template_id, # This template's questions will be copied
            course_code=course_code if course_code else None,
            batch=batch if batch else None,
            last_date=last_date,
            admin_id=self.admin_id
        )

        if success:
            messagebox.showinfo("Success", message)
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", message)

    def extend_deadline(self):
        new_date_str = self.extend_date_entry.get().strip()

        if not new_date_str:
            messagebox.showerror("Validation Error", "New deadline date is required.")
            return

        try:
            new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format for extension. Please use YYYY-MM-DD.")
            return

        if messagebox.askyesno("Confirm Extension", f"Are you sure you want to extend the deadline of Template ID {self.source_template_id} to {new_date_str}?"):
            if self.template_controller.extend_template_deadline(self.source_template_id, new_date):
                messagebox.showinfo("Success", "Deadline extended successfully.")
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to extend deadline.")