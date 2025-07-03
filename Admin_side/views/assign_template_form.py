# views/assign_template_form.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.course_controller import CourseController # To fetch courses
from controllers.student_controller import StudentController # To fetch sessions
from datetime import datetime, date

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AssignTemplateForm(ctk.CTkToplevel):
    def __init__(self, parent_window, template_controller, course_controller, student_controller, refresh_callback, source_template_id=None, admin_id=None):
        super().__init__(parent_window)
        self.template_controller = template_controller
        self.course_controller = course_controller
        self.student_controller = student_controller 
        self.refresh_callback = refresh_callback
        self.source_template_id = source_template_id 
        self.admin_id = admin_id

        self.source_template = self.template_controller.get_template_by_id(self.source_template_id)
        if not self.source_template:
            ctk.CTkMessagebox.show_error("Error", "Source template not found. Cannot proceed with assignment.")
            self.destroy()
            return

        self.title(f"Assign Template: {self.source_template.title}")

        # Standard Toplevel setup order, mimicking add_admin_form.py:
        self.transient(parent_window)
        self.grab_set()

        # Set an initial geometry to allow widgets to pack for update_idletasks
        self.geometry("800x600")
        self.configure(fg_color=GREY)

        self.create_widgets() # Create widgets first

        self.update_idletasks() # Crucial step: Update idletasks to ensure the window has finalized its size
        
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

        self.lift() # Bring to front after positioning

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.load_course_batch_session_data() # Populate comboboxes

    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Assign Evaluation Template to Course", font=("Arial", 24, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Course selection frame
        course_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        course_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(course_frame, text="Select Course:", font=("Arial", 17), text_color=DARK_BLUE).pack(side="left", padx=10, pady=10)
        self.course_combo = ctk.CTkOptionMenu(course_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                             button_color=BLUE, button_hover_color=DARK_BLUE)
        self.course_combo.pack(side="left", padx=10, pady=10)
        self.course_combo.configure(command=self.load_assigned_templates)

        # Templates section
        templates_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        templates_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(templates_frame, text="Available Templates:", font=("Arial", 18, "bold"), text_color=DARK_BLUE).pack(pady=10)
        
        # Templates list frame with treeview
        templates_list_frame = ctk.CTkFrame(templates_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        templates_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.templates_tree = ttk.Treeview(templates_list_frame, columns=("ID", "Name", "Status"), show="headings", height=8)
        self.templates_tree.heading("ID", text="Template ID")
        self.templates_tree.heading("Name", text="Template Name")
        self.templates_tree.heading("Status", text="Status")
        self.templates_tree.column("ID", width=100, anchor="center")
        self.templates_tree.column("Name", width=300)
        self.templates_tree.column("Status", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        templates_scrollbar = ctk.CTkScrollbar(templates_list_frame, orientation="vertical", command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=templates_scrollbar.set)
        self.templates_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        templates_scrollbar.pack(side="right", fill="y", pady=10)

        # Assigned templates section
        assigned_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(assigned_frame, text="Currently Assigned Templates:", font=("Arial", 18, "bold"), text_color=DARK_BLUE).pack(pady=10)
        
        # Assigned templates list frame with treeview
        assigned_list_frame = ctk.CTkFrame(assigned_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.assigned_templates_tree = ttk.Treeview(assigned_list_frame, columns=("ID", "Name", "Status"), show="headings", height=8)
        self.assigned_templates_tree.heading("ID", text="Template ID")
        self.assigned_templates_tree.heading("Name", text="Template Name")
        self.assigned_templates_tree.heading("Status", text="Status")
        self.assigned_templates_tree.column("ID", width=100, anchor="center")
        self.assigned_templates_tree.column("Name", width=300)
        self.assigned_templates_tree.column("Status", width=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        assigned_scrollbar = ctk.CTkScrollbar(assigned_list_frame, orientation="vertical", command=self.assigned_templates_tree.yview)
        self.assigned_templates_tree.configure(yscrollcommand=assigned_scrollbar.set)
        self.assigned_templates_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        assigned_scrollbar.pack(side="right", fill="y", pady=10)

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color=WHITE)
        button_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkButton(button_frame, text="Assign Template", command=self.assign_template,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Unassign Template", command=self.unassign_template,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close", command=self.destroy,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="right", padx=5)

    def load_course_batch_session_data(self):
        courses = self.course_controller.get_all_courses()
        course_codes = [c.course_code for c in courses]
        self.course_combo.configure(values=[""] + course_codes)
        self.course_combo.set("")

        all_batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        batches_data = self.course_controller.db.fetch_data(all_batches_query, fetch_all=True)
        batches = [b['batch'] for b in batches_data]
        self.batch_combo.configure(values=[""] + batches)
        self.batch_combo.set("")

        sessions = self.student_controller.get_unique_sessions() 
        self.session_combo.configure(values=[""] + sessions)
        self.session_combo.set("")

    def load_all_templates(self):
        """Load all available templates into the treeview."""
        for i in self.templates_tree.get_children():
            self.templates_tree.delete(i)
        
        templates = self.template_controller.get_all_templates()
        for template in templates:
            self.templates_tree.insert("", "end", iid=template.template_id, values=(template.template_id, template.name, template.status))

    def load_assigned_templates(self, event=None):
        """Load templates assigned to the selected course."""
        for i in self.assigned_templates_tree.get_children():
            self.assigned_templates_tree.delete(i)
        
        selected_course = self.course_combo.get()
        if selected_course:
            assigned_templates = self.template_controller.get_templates_assigned_to_course(selected_course)
            for template in assigned_templates:
                self.assigned_templates_tree.insert("", "end", iid=template.template_id, values=(template.template_id, template.name, template.status))

    def assign_template(self):
        """Assign the selected template to the selected course."""
        selected_course = self.course_combo.get()
        selected_template_item = self.templates_tree.focus()
        
        if not selected_course:
            ctk.CTkMessagebox.show_warning("No Course Selected", "Please select a course.")
            return
        
        if not selected_template_item:
            ctk.CTkMessagebox.show_warning("No Template Selected", "Please select a template to assign.")
        return
            
        template_id = int(selected_template_item)
        template_name = self.templates_tree.item(selected_template_item)['values'][1]

        success = self.template_controller.assign_template_to_course(template_id, selected_course)
        if success:
            ctk.CTkMessagebox.show_info("Success", f"Template '{template_name}' assigned to course '{selected_course}' successfully.")
            self.load_assigned_templates()
            if self.refresh_callback:
                self.refresh_callback()
        else:
            ctk.CTkMessagebox.show_error("Error", "Failed to assign template to course.")

    def unassign_template(self):
        """Unassign the selected template from the selected course."""
        selected_course = self.course_combo.get()
        selected_template_item = self.assigned_templates_tree.focus()
        
        if not selected_course:
            ctk.CTkMessagebox.show_warning("No Course Selected", "Please select a course.")
        return

        if not selected_template_item:
            ctk.CTkMessagebox.show_warning("No Template Selected", "Please select a template to unassign.")
        return

        template_id = int(selected_template_item)
        template_name = self.assigned_templates_tree.item(selected_template_item)['values'][1]

        if ctk.CTkMessagebox.ask_yes_no("Confirm Unassign", f"Are you sure you want to unassign template '{template_name}' from course '{selected_course}'?"):
            success = self.template_controller.unassign_template_from_course(template_id, selected_course)
            if success:
                ctk.CTkMessagebox.show_info("Success", f"Template '{template_name}' unassigned from course '{selected_course}' successfully.")
                self.load_assigned_templates()
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                ctk.CTkMessagebox.show_error("Error", "Failed to unassign template from course.")

    def on_closing(self):
        self.destroy()
