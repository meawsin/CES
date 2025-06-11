# views/evaluation_templates_page.py (Updated)
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.course_controller import CourseController # For course list
from views.create_edit_template_form import CreateEditTemplateForm
from views.assign_template_form import AssignTemplateForm
import json

class EvaluationTemplatesPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.template_controller = EvaluationTemplateController()
        self.course_controller = CourseController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Ensure treeview expands

        self.create_widgets()
        self.load_templates()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Manage Evaluation Templates", font=("Arial", 18, "bold"), background="#ecf0f1", foreground="#34495e")
        title_label.pack(pady=10)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Create New Template", command=self.open_create_template_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Template", command=self.open_edit_template_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Template", command=self.delete_selected_template).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Assign Template", command=self.open_assign_template_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="View Template Details", command=self.view_template_details).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh List", command=self.load_templates).pack(side="right", padx=5)

        self.template_tree = ttk.Treeview(self, columns=(
            "ID", "Title", "Assigned Course", "Assigned Batch", "Last Date", "Created By Admin ID"
        ), show="headings")

        self.template_tree.heading("ID", text="Template ID")
        self.template_tree.heading("Title", text="Title")
        self.template_tree.heading("Assigned Course", text="Course")
        self.template_tree.heading("Assigned Batch", text="Batch")
        self.template_tree.heading("Last Date", text="Last Date")
        self.template_tree.heading("Created By Admin ID", text="Admin ID")

        self.template_tree.column("ID", width=80, anchor="center")
        self.template_tree.column("Title", width=250)
        self.template_tree.column("Assigned Course", width=120)
        self.template_tree.column("Assigned Batch", width=120)
        self.template_tree.column("Last Date", width=100)
        self.template_tree.column("Created By Admin ID", width=120, anchor="center")


        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)

        self.template_tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_templates(self):
        for i in self.template_tree.get_children():
            self.template_tree.delete(i)

        templates = self.template_controller.get_all_templates()
        self.all_templates_data = templates # Store for internal use

        # Check the provided populate script. The `evaluation_templates` table
        # has a `last_date` of '2025-07-15'. Ensure your database is up-to-date
        # with this or similar entries.
        for template in templates:
            self.template_tree.insert("", "end", iid=template.id, values=(
                template.id, template.title,
                template.course_code if template.course_code else "N/A",
                template.batch if template.batch else "N/A",
                template.last_date.strftime("%Y-%m-%d") if template.last_date else "N/A", # Format date here
                template.admin_id
            ))


    def open_create_template_form(self):
        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot create template.")
            return

        form_window = tk.Toplevel(self.parent_controller)
        form_window.title("Create New Evaluation Template")
        form_window.transient(self.parent_controller)
        form_window.grab_set()
        form_window.geometry("800x600")

        CreateEditTemplateForm(form_window, self.template_controller, self.load_templates, admin_id=admin_id)

    def open_edit_template_form(self):
        selected_item = self.template_tree.focus()
        # ADD THIS CHECK:
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a template to edit.")
            return

        template_id_to_edit = self.template_tree.item(selected_item)['iid']
        template_data = self.template_controller.get_template_by_id(template_id_to_edit)

        if template_data:
            form_window = tk.Toplevel(self.parent_controller)
            form_window.title(f"Edit Evaluation Template (ID: {template_id_to_edit})")
            form_window.transient(self.parent_controller)
            form_window.grab_set()
            form_window.geometry("800x600")

            CreateEditTemplateForm(form_window, self.template_controller, self.load_templates, template_to_edit=template_data)
        else:
            messagebox.showerror("Error", "Could not retrieve template data for editing.")

    def delete_selected_template(self):
        selected_item = self.template_tree.focus()
        # ADD THIS CHECK:
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a template to delete.")
            return

        template_id_to_delete = self.template_tree.item(selected_item)['iid']
        template_title_to_delete = self.template_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete template: '{template_title_to_delete}' (ID: {template_id_to_delete})?\nThis will also delete associated evaluation responses."):
            if self.template_controller.delete_template(template_id_to_delete):
                messagebox.showinfo("Success", "Template deleted successfully.")
                self.load_templates()
            else:
                messagebox.showerror("Error", "Failed to delete template.")

    def open_assign_template_form(self):
        selected_item = self.template_tree.focus()
        # ADD THIS CHECK:
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a base template to assign.")
            return

        source_template_id = self.template_tree.item(selected_item)['iid']
        source_template_data = self.template_controller.get_template_by_id(source_template_id)

        if not source_template_data:
            messagebox.showerror("Error", "Selected source template not found.")
            return

        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot assign template.")
            return

        assign_form_window = tk.Toplevel(self.parent_controller)
        assign_form_window.title(f"Assign Template: {source_template_data.title}")
        assign_form_window.transient(self.parent_controller)
        assign_form_window.grab_set()
        assign_form_window.geometry("600x450")

        AssignTemplateForm(
            assign_form_window,
            self.template_controller,
            self.course_controller,
            self.load_templates,
            source_template_id=source_template_id,
            admin_id=admin_id
        )

    def view_template_details(self):
        selected_item = self.template_tree.focus()
        # ADD THIS CHECK:
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a template to view details.")
            return

        template_id = self.template_tree.item(selected_item)['iid']
        template_data = self.template_controller.get_template_by_id(template_id)

        if template_data:
            details_window = tk.Toplevel(self.parent_controller)
            details_window.title(f"Template Details: {template_data.title}")
            details_window.transient(self.parent_controller)
            details_window.grab_set()
            details_window.geometry("700x500")

            details_frame = ttk.Frame(details_window, padding="15")
            details_frame.pack(fill="both", expand=True)

            ttk.Label(details_frame, text=f"Title: {template_data.title}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"ID: {template_data.id}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Assigned Course: {template_data.course_code if template_data.course_code else 'N/A'}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Assigned Batch: {template_data.batch if template_data.batch else 'N/A'}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Last Date: {template_data.last_date.strftime('%Y-%m-%d') if template_data.last_date else 'N/A'}").pack(anchor="w", padx=10) # Format date
            ttk.Label(details_frame, text=f"Created by Admin ID: {template_data.admin_id}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Created At: {template_data.created_at}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Updated At: {template_data.updated_at}").pack(anchor="w", padx=10)

            ttk.Label(details_frame, text="Questions Set (JSON):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            questions_text = tk.Text(details_frame, wrap="word", height=15, width=80)
            questions_text.pack(fill="both", expand=True)
            questions_text.insert("1.0", json.dumps(template_data.questions_set, indent=2))
            questions_text.config(state="disabled")

            # Add Completion Status information
            ttk.Label(details_frame, text="Completion Status:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            if template_data.course_code: # Only meaningful if assigned to a specific course
                completion_status = self.template_controller.get_template_completion_status(template_data.id, template_data.course_code)
                if completion_status:
                    ttk.Label(details_frame, text=f"Total Expected Submissions: {completion_status['total_expected']}").pack(anchor="w", padx=10)
                    ttk.Label(details_frame, text=f"Completed Submissions: {completion_status['completed_count']}").pack(anchor="w", padx=10)
                    ttk.Label(details_frame, text=f"Completion Percentage: {completion_status['completion_percentage']:.2f}%").pack(anchor="w", padx=10)

                    if completion_status['non_completers']:
                        non_completers_str = "Non-completers (Student ID, Batch, Dept): " + \
                                             ", ".join([f"({s['student_id']}, {s['batch']}, {s['department']})"
                                                        for s in completion_status['non_completers']])
                        non_completers_text = tk.Text(details_frame, wrap="word", height=5, width=80)
                        non_completers_text.pack(fill="x", padx=10, pady=5)
                        non_completers_text.insert("1.0", non_completers_str)
                        non_completers_text.config(state="disabled")
                    else:
                        ttk.Label(details_frame, text="All expected students have completed the evaluation!").pack(anchor="w", padx=10)
                else:
                    ttk.Label(details_frame, text="No completion data available or an error occurred.", foreground="red").pack(anchor="w", padx=10)
            else:
                ttk.Label(details_frame, text="Completion status is tracked per course. This template is not tied to a specific course.", foreground="gray").pack(anchor="w", padx=10)

        else:
            messagebox.showerror("Error", "Template not found.")