# views/create_edit_template_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.evaluation_template_model import EvaluationTemplate
import json
from datetime import datetime

class CreateEditTemplateForm(tk.Toplevel):
    def __init__(self, parent_window, template_controller, refresh_callback, template_to_edit=None, admin_id=None):
        super().__init__(parent_window)
        self.template_controller = template_controller
        self.refresh_callback = refresh_callback
        self.template_to_edit = template_to_edit
        self.admin_id = admin_id # Admin creating/editing the template

        if self.template_to_edit:
            self.title("Edit Evaluation Template")
        else:
            self.title("Create New Evaluation Template")

        self.create_widgets()
        if self.template_to_edit:
            self.load_template_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Basic Info
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(form_frame, width=50)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Questions Set (JSON input)
        ttk.Label(form_frame, text="Questions Set (JSON):").grid(row=1, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")
        self.questions_text = tk.Text(form_frame, wrap="word", height=20, width=70)
        self.questions_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Add a scrollbar to the text widget
        text_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=self.questions_text.yview)
        self.questions_text.config(yscrollcommand=text_scrollbar.set)
        text_scrollbar.grid(row=2, column=2, sticky="ns")

        # Note: Batch, Course_Code, Last_Date, Admin_ID are for assignment, handled in AssignTemplateForm.
        # This form is primarily for creating the *content* of the template.
        # However, the schema allows them to be set directly on template creation.
        # Let's keep them here for initial creation if desired, but they are optional.

        ttk.Label(form_frame, text="Default Batch (Optional):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.batch_entry = ttk.Entry(form_frame, width=30)
        self.batch_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Default Course Code (Optional):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.course_code_entry = ttk.Entry(form_frame, width=30)
        self.course_code_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Default Last Date (YYYY-MM-DD, Optional):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.last_date_entry = ttk.Entry(form_frame, width=30)
        self.last_date_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Make content area expand
        form_frame.grid_rowconfigure(2, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        save_button = ttk.Button(form_frame, text="Save Template", command=self.save_template)
        save_button.grid(row=6, column=0, columnspan=2, pady=20)

    def load_template_data(self):
        if self.template_to_edit:
            self.title_entry.insert(0, self.template_to_edit.title)
            # Display JSON with pretty print
            self.questions_text.insert("1.0", json.dumps(self.template_to_edit.questions_set, indent=2))
            if self.template_to_edit.batch:
                self.batch_entry.insert(0, self.template_to_edit.batch)
            if self.template_to_edit.course_code:
                self.course_code_entry.insert(0, self.template_to_edit.course_code)
            if self.template_to_edit.last_date:
                self.last_date_entry.insert(0, self.template_to_edit.last_date.strftime("%Y-%m-%d"))

    def save_template(self):
        title = self.title_entry.get().strip()
        questions_json_str = self.questions_text.get("1.0", tk.END).strip()
        batch = self.batch_entry.get().strip()
        course_code = self.course_code_entry.get().strip()
        last_date_str = self.last_date_entry.get().strip()

        if not title or not questions_json_str:
            messagebox.showerror("Validation Error", "Title and Questions Set are required.")
            return

        try:
            questions_set = json.loads(questions_json_str)
            if not isinstance(questions_set, dict): # Or check for expected structure, e.g., {'instructions':..., 'questions':[]}
                raise ValueError("Questions Set must be a valid JSON object.")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format for Questions Set: {e}")
            return
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        last_date = None
        if last_date_str:
            try:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid Last Date format. Please use YYYY-MM-DD.")
                return

        admin_id = self.admin_id if self.admin_id else (self.template_to_edit.admin_id if self.template_to_edit else None)
        if not admin_id:
            messagebox.showerror("Error", "Admin ID not found. Please log in again.")
            return

        # Create template object
        new_template = EvaluationTemplate(
            id=None, # For new creation, ID will be auto-incremented
            title=title,
            questions_set=questions_set,
            batch=batch if batch else None,
            course_code=course_code if course_code else None,
            last_date=last_date,
            admin_id=admin_id
        )

        if self.template_to_edit:
            new_template.id = self.template_to_edit.id # Use original ID for update
            success = self.template_controller.update_template(new_template)
            action = "updated"
        else:
            success = self.template_controller.add_template(new_template)
            action = "created"

        if success:
            messagebox.showinfo("Success", f"Template {action} successfully!")
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", f"Failed to {action} template.")