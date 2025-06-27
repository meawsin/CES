# views/assign_template_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.course_controller import CourseController # To fetch courses
from controllers.student_controller import StudentController # To fetch sessions
from datetime import datetime, date

# FIX: Removed the circular import line that was here.
# from views.assign_template_form import AssignTemplateForm # THIS LINE WAS REMOVED.

class AssignTemplateForm(tk.Toplevel):
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
            messagebox.showerror("Error", "Source template not found. Cannot proceed with assignment.")
            self.destroy()
            return

        self.title(f"Assign Template: {self.source_template.title}")

        # Standard Toplevel setup order, mimicking add_admin_form.py:
        self.transient(parent_window)
        self.grab_set()

        # Set an initial geometry to allow widgets to pack for update_idletasks
        self.geometry("600x500") 

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

        ttk.Label(form_frame, text="Assign to Session (Optional):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.session_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.session_combo.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Assignment Last Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.last_date_entry = ttk.Entry(form_frame, width=30)
        self.last_date_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        
        if self.source_template.last_date and isinstance(self.source_template.last_date, (datetime, date)):
            self.last_date_entry.insert(0, self.source_template.last_date.strftime("%Y-%m-%d"))
        elif self.source_template.last_date: 
             self.last_date_entry.insert(0, str(self.source_template.last_date))


        form_frame.grid_columnconfigure(1, weight=1) 

        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])
        ttk.Button(form_frame, text="Create New Assignment", command=self.create_new_assignment, style="FormSave.TButton").grid(row=6, column=0, columnspan=2, pady=20)


    def load_course_batch_session_data(self):
        courses = self.course_controller.get_all_courses()
        course_codes = [c.course_code for c in courses]
        self.course_combo['values'] = [""] + course_codes 

        all_batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        batches_data = self.course_controller.db.fetch_data(all_batches_query, fetch_all=True)
        batches = [b['batch'] for b in batches_data]
        self.batch_combo['values'] = [""] + batches 

        sessions = self.student_controller.get_unique_sessions() 
        self.session_combo['values'] = [""] + sessions 


    def create_new_assignment(self):
        try:
            course_code = self.course_combo.get().strip()
            batch = self.batch_combo.get().strip()
            session = self.session_combo.get().strip()
            last_date_str = self.last_date_entry.get().strip()

            if not last_date_str:
                messagebox.showerror("Validation Error", "Assignment Last Date is required.")
                return
            
            if not course_code and not batch and not session:
                messagebox.showerror("Validation Error", "At least one of Course, Batch, or Session must be selected for a new assignment.")
                return

            try:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid Last Date format. Please useYYYY-MM-DD.")
                return

            success, message = self.template_controller.assign_template_to_course_batch_session(
                template_id=self.source_template_id, 
                course_code=course_code if course_code else None,
                batch=batch if batch else None,
                session=session if session else None,
                last_date=last_date,
                admin_id=self.admin_id
            )

            if success:
                messagebox.showinfo("Success", message)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Runtime Error", f"An unexpected error occurred: {e}. Please check console for details.")
            import traceback
            traceback.print_exc() 


    def on_closing(self):
        self.destroy()
