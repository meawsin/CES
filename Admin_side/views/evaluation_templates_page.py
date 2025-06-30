# views/evaluation_templates_page.py (Restructured and Enhanced)

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.course_controller import CourseController
from controllers.student_controller import StudentController # For fetching sessions
from views.create_edit_template_form import CreateEditTemplateForm
from views.assign_template_form import AssignTemplateForm
import json
from datetime import datetime, date

class EvaluationTemplatesPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.template_controller = EvaluationTemplateController()
        self.course_controller = CourseController()
        self.student_controller = StudentController() # For sessions data

        self.configure(bg="#ECF0F1")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1) # Notebook will expand

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self._create_templates_tab()
        self._create_ongoing_evaluations_tab()
        self._create_past_evaluations_tab()

        # Bind tab change event to refresh data in the selected tab
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Initial load based on default selected tab (usually first)
        self.load_templates() # Load templates tab initially
        
    def _on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "All Templates":
            self.load_templates()
        elif selected_tab == "Ongoing Evaluations":
            self.load_ongoing_evaluations()
        elif selected_tab == "Past Evaluations":
            self.load_past_evaluations()


    # --- Tab 1: All Templates (Existing functionality, slightly reorganized) ---
    def _create_templates_tab(self):
        self.templates_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.templates_frame, text="All Templates")

        title_label = ttk.Label(self.templates_frame, text="Manage All Evaluation Templates", font=("Arial", 16, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.pack(pady=10)

        button_frame = ttk.Frame(self.templates_frame, padding="10")
        button_frame.pack(pady=5, fill="x")
        
        ttk.Button(button_frame, text="Create New", command=self.open_create_template_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit", command=self.open_edit_template_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_selected_template, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Assign Template", command=self.open_assign_template_form, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="View Details", command=self.view_template_details, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_templates, style="General.TButton").pack(side="right", padx=5)

        self.template_tree = ttk.Treeview(self.templates_frame, columns=(
            "ID", "Title", "Assigned Course", "Assigned Batch", "Assigned Session", "Last Date", "Created By Admin ID"
        ), show="headings")

        self.template_tree.heading("ID", text="ID")
        self.template_tree.heading("Title", text="Title")
        self.template_tree.heading("Assigned Course", text="Course")
        self.template_tree.heading("Assigned Batch", text="Batch")
        self.template_tree.heading("Assigned Session", text="Session")
        self.template_tree.heading("Last Date", text="Last Date")
        self.template_tree.heading("Created By Admin ID", text="Admin ID")

        self.template_tree.column("ID", width=60, anchor="center")
        self.template_tree.column("Title", width=200)
        self.template_tree.column("Assigned Course", width=100)
        self.template_tree.column("Assigned Batch", width=100)
        self.template_tree.column("Assigned Session", width=100)
        self.template_tree.column("Last Date", width=90)
        self.template_tree.column("Created By Admin ID", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.templates_frame, orient="vertical", command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)

        self.template_tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_templates(self):
        for i in self.template_tree.get_children():
            self.template_tree.delete(i)

        templates = self.template_controller.get_all_templates()
        self.all_templates_data = templates # Store for internal use

        for template in templates:
            display_course = template.course_code if template.course_code else "N/A"
            display_batch = template.batch if template.batch else "N/A"
            display_session = template.session if template.session else "N/A"
            
            # Ensure 'iid' is a string for Treeview compatibility
            self.template_tree.insert("", "end", iid=str(template.id), values=( # IMPORTANT: Convert template.id to str
                template.id, template.title,
                display_course,
                display_batch,
                display_session,
                template.last_date.strftime("%Y-%m-%d") if template.last_date else "N/A",
                template.admin_id
            ))

    def _get_selected_template_id(self):
        """Helper to get the ID of the selected template safely."""
        selected_items = self.template_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a template first.")
            return None
        
        # Access the first selected item's iid (which is the actual ID)
        selected_iid = selected_items[0]
        
        # The 'iid' itself *is* the ID that was passed during insert.
        # No need to call .item(selected_iid)['iid'] as the original traceback shows it's missing.
        # The selected_iid directly represents the ID used when inserting the row.
        return selected_iid # This is the correct fix.


    def open_create_template_form(self):
        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot create template.")
            return

        form_window = tk.Toplevel(self.parent_controller.get_root_window())
        create_edit_form = CreateEditTemplateForm(form_window, self.template_controller, self.load_templates, admin_id=admin_id)
        self.parent_controller.get_root_window().wait_window(form_window)
        self.load_templates() 

    def open_edit_template_form(self):
        template_id_to_edit = self._get_selected_template_id()
        if template_id_to_edit is None:
            return # Message already shown by helper

        template_data = self.template_controller.get_template_by_id(template_id_to_edit)

        if template_data:
            form_window = tk.Toplevel(self.parent_controller.get_root_window())
            create_edit_form = CreateEditTemplateForm(form_window, self.template_controller, self.load_templates, template_to_edit=template_data)
            self.parent_controller.get_root_window().wait_window(form_window)
            self.load_templates() 
        else:
            messagebox.showerror("Error", "Could not retrieve template data for editing.")

    def delete_selected_template(self):
        template_id_to_delete = self._get_selected_template_id()
        if template_id_to_delete is None:
            return # Message already shown by helper

        # Get title from treeview values, as template_data might be for a different type of template
        # Safely get values, then access index
        selected_item_values = self.template_tree.item(template_id_to_delete).get('values', [])
        if len(selected_item_values) > 1: # Ensure title index (1) exists
            template_title_to_delete = selected_item_values[1]
        else:
            template_title_to_delete = f"Template ID {template_id_to_delete}" # Fallback title

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete template: '{template_title_to_delete}' (ID: {template_id_to_delete})?\nThis will also delete associated evaluation responses."):
            if self.template_controller.delete_template(template_id_to_delete):
                messagebox.showinfo("Success", "Template deleted successfully.")
                self.load_templates()
            else:
                messagebox.showerror("Error", "Failed to delete template. Check database or dependencies.")

    def open_assign_template_form(self):
        source_template_id = self._get_selected_template_id()
        if source_template_id is None:
            return # Message already shown by helper

        source_template_data = self.template_controller.get_template_by_id(source_template_id)

        if not source_template_data:
            messagebox.showerror("Error", "Selected source template not found.")
            return

        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot assign template.")
            return

        assign_form_window = tk.Toplevel(self.parent_controller.get_root_window())
        assign_template_form = AssignTemplateForm(
            assign_form_window,
            self.template_controller,
            self.course_controller,
            self.student_controller, # Pass student_controller to fetch sessions
            self.load_templates, 
            source_template_id=source_template_id,
            admin_id=admin_id
        )
        self.parent_controller.get_root_window().wait_window(assign_form_window)
        self.load_templates() 

    def view_template_details(self):
        template_id = self._get_selected_template_id()
        if template_id is None:
            return # Message already shown by helper

        template_data = self.template_controller.get_template_by_id(template_id)

        if template_data:
            details_window = tk.Toplevel(self.parent_controller.get_root_window())
            details_window.title(f"Template Details: {template_data.title}")
            details_window.transient(self.parent_controller.get_root_window())
            details_window.grab_set()
            details_window.geometry("700x550") # Adjusted size for more content
            details_window.lift()

            details_frame = ttk.Frame(details_window, padding="15")
            details_frame.pack(fill="both", expand=True)

            ttk.Label(details_frame, text=f"Title: {template_data.title}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"ID: {template_data.id}").pack(anchor="w", padx=10)
            
            display_course = template_data.course_code if template_data.course_code else "N/A"
            display_batch = template_data.batch if template_data.batch else "N/A"
            display_session = template_data.session if template_data.session else "N/A"

            ttk.Label(details_frame, text=f"Assigned Course: {display_course}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Assigned Batch: {display_batch}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Assigned Session: {display_session}").pack(anchor="w", padx=10)

            ttk.Label(details_frame, text=f"Last Date: {template_data.last_date.strftime('%Y-%m-%d') if template_data.last_date else 'N/A'}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Created by Admin ID: {template_data.admin_id}").pack(anchor="w", padx=10)
            ttk.Label(details_frame, text=f"Updated At: {template_data.updated_at}").pack(anchor="w", padx=10)

            instructions_text = template_data.questions_set.get('instructions', 'No instructions provided.')
            ttk.Label(details_frame, text="Instructions:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            inst_display = tk.Text(details_frame, wrap="word", height=3, width=80)
            inst_display.pack(fill="x", padx=10, pady=2)
            inst_display.insert("1.0", instructions_text)
            inst_display.config(state="disabled")

            ttk.Label(details_frame, text="Questions Set (JSON):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            questions_text = tk.Text(details_frame, wrap="word", height=15, width=80)
            questions_text.pack(fill="both", expand=True)
            questions_only_json = {"questions": template_data.questions_set.get('questions', [])}
            questions_text.insert("1.0", json.dumps(questions_only_json, indent=2))
            questions_text.config(state="disabled")

            # Add Completion Status information
            ttk.Label(details_frame, text="Completion Status:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            
            completion_checked_for = ""
            if template_data.course_code:
                completion_status = self.template_controller.get_template_completion_status(template_data.id, template_data.course_code)
                completion_checked_for = f"course '{template_data.course_code}'"
            elif template_data.batch:
                completion_status = None 
                completion_checked_for = f"batch '{template_data.batch}' (requires associated course for full tracking)"
            elif template_data.session:
                completion_status = None 
                completion_checked_for = f"session '{template_data.session}' (requires associated course for full tracking)"
            else:
                completion_status = None
                completion_checked_for = "this base template (not assigned to a specific context)"


            if completion_status:
                ttk.Label(details_frame, text=f"Total Expected Submissions for {completion_checked_for}: {completion_status['total_expected']}").pack(anchor="w", padx=10)
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
                if template_data.course_code or template_data.batch or template_data.session:
                    ttk.Label(details_frame, text=f"No completion data available for {completion_checked_for} or an error occurred.", foreground="red").pack(anchor="w", padx=10)
                else:
                    ttk.Label(details_frame, text="Completion status is tracked for assigned templates (those linked to a specific context). This is a base template.", foreground="gray").pack(anchor="w", padx=10)

        else:
            messagebox.showerror("Error", "Template not found.")


    # --- Tab 2: Ongoing Evaluations ---
    def _create_ongoing_evaluations_tab(self):
        self.ongoing_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ongoing_frame, text="Ongoing Evaluations")

        title_label = ttk.Label(self.ongoing_frame, text="Currently Active Evaluations", font=("Arial", 16, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.pack(pady=10)

        refresh_button = ttk.Button(self.ongoing_frame, text="Refresh Ongoing", command=self.load_ongoing_evaluations, style="General.TButton")
        refresh_button.pack(pady=5, anchor="e", padx=5)

        self.ongoing_tree = ttk.Treeview(self.ongoing_frame, columns=(
            "ID", "Title", "Assigned Course", "Assigned Batch", "Assigned Session", "Last Date", "Created By Admin ID"
        ), show="headings")

        self.ongoing_tree.heading("ID", text="ID")
        self.ongoing_tree.heading("Title", text="Title")
        self.ongoing_tree.heading("Assigned Course", text="Course")
        self.ongoing_tree.heading("Assigned Batch", text="Batch")
        self.ongoing_tree.heading("Assigned Session", text="Session")
        self.ongoing_tree.heading("Last Date", text="Last Date")
        self.ongoing_tree.heading("Created By Admin ID", text="Admin ID")

        self.ongoing_tree.column("ID", width=60, anchor="center")
        self.ongoing_tree.column("Title", width=200)
        self.ongoing_tree.column("Assigned Course", width=100)
        self.ongoing_tree.column("Assigned Batch", width=100)
        self.ongoing_tree.column("Assigned Session", width=100)
        self.ongoing_tree.column("Last Date", width=90)
        self.ongoing_tree.column("Created By Admin ID", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.ongoing_frame, orient="vertical", command=self.ongoing_tree.yview)
        self.ongoing_tree.configure(yscrollcommand=scrollbar.set)

        self.ongoing_tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_ongoing_evaluations(self):
        for i in self.ongoing_tree.get_children():
            self.ongoing_tree.delete(i)
        
        ongoing_evals = self.template_controller.get_ongoing_evaluations()
        for template in ongoing_evals:
            display_course = template.course_code if template.course_code else "N/A"
            display_batch = template.batch if template.batch else "N/A"
            display_session = template.session if template.session else "N/A"
            
            self.ongoing_tree.insert("", "end", iid=template.id, values=(
                template.id, template.title,
                display_course,
                display_batch,
                display_session,
                template.last_date.strftime("%Y-%m-%d") if template.last_date else "N/A",
                template.admin_id
            ))


    # --- Tab 3: Past Evaluations ---
    def _create_past_evaluations_tab(self):
        self.past_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.past_frame, text="Past Evaluations")

        title_label = ttk.Label(self.past_frame, text="Completed Evaluations (Past Deadlines)", font=("Arial", 16, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.pack(pady=10)

        refresh_button = ttk.Button(self.past_frame, text="Refresh Past", command=self.load_past_evaluations, style="General.TButton")
        refresh_button.pack(pady=5, anchor="e", padx=5)

        self.past_tree = ttk.Treeview(self.past_frame, columns=(
            "ID", "Title", "Assigned Course", "Assigned Batch", "Assigned Session", "Last Date", "Created By Admin ID"
        ), show="headings")

        self.past_tree.heading("ID", text="ID")
        self.past_tree.heading("Title", text="Title")
        self.past_tree.heading("Assigned Course", text="Course")
        self.past_tree.heading("Assigned Batch", text="Batch")
        self.past_tree.heading("Assigned Session", text="Session")
        self.past_tree.heading("Last Date", text="Last Date")
        self.past_tree.heading("Created By Admin ID", text="Admin ID")

        self.past_tree.column("ID", width=60, anchor="center")
        self.past_tree.column("Title", width=200)
        self.past_tree.column("Assigned Course", width=100)
        self.past_tree.column("Assigned Batch", width=100)
        self.past_tree.column("Assigned Session", width=100)
        self.past_tree.column("Last Date", width=90)
        self.past_tree.column("Created By Admin ID", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.past_frame, orient="vertical", command=self.past_tree.yview)
        self.past_tree.configure(yscrollcommand=scrollbar.set)

        self.past_tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_past_evaluations(self):
        for i in self.past_tree.get_children():
            self.past_tree.delete(i)
        
        past_evals = self.template_controller.get_past_evaluations()
        for template in past_evals:
            display_course = template.course_code if template.course_code else "N/A"
            display_batch = template.batch if template.batch else "N/A"
            display_session = template.session if template.session else "N/A"

            self.past_tree.insert("", "end", iid=template.id, values=(
                template.id, template.title,
                display_course,
                display_batch,
                display_session,
                template.last_date.strftime("%Y-%m-%d") if template.last_date else "N/A",
                template.admin_id
            ))

