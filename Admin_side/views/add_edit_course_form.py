# views/add_edit_course_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.course_model import Course # Assuming Course model is defined
from datetime import datetime # Import datetime for potential date handling if needed

class AddEditCourseForm(tk.Toplevel):
    def __init__(self, parent_window, course_controller, refresh_callback, course_to_edit=None):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.refresh_callback = refresh_callback
        self.course_to_edit = course_to_edit

        if self.course_to_edit:
            self.title("Edit Course Information")
        else:
            self.title("Add New Course")

        # Robust Toplevel setup
        self.transient(parent_window)
        self.grab_set()

        # Create widgets first to allow geometry calculation
        self.create_widgets()

        if self.course_to_edit:
            self.load_course_data()
        
        # Set initial focus (e.g., on the course code entry)
        if "course_code" in self.entries and self.entries['course_code'].cget('state') == 'normal':
            self.entries['course_code'].focus_set()
        elif "name" in self.entries and self.entries['name'].cget('state') == 'normal':
            self.entries['name'].focus_set()


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
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Configure columns for a responsive two-column layout
        form_frame.columnconfigure(0, weight=0) # Labels column
        form_frame.columnconfigure(1, weight=1) # Input fields column (expands)

        self.entries = {} # Dictionary to hold references to entry widgets

        # Course Code field
        ttk.Label(form_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entries['course_code'] = ttk.Entry(form_frame, width=30)
        self.entries['course_code'].grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # Do NOT set state="disabled" here directly. Handle it in load_course_data or after widgets are fully created.
        # This allows initial insertion to always work without timing issues.

        # Course Name field
        ttk.Label(form_frame, text="Course Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entries['name'] = ttk.Entry(form_frame, width=30)
        self.entries['name'].grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Status Combobox
        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entries['status'] = ttk.Combobox(form_frame, values=["ongoing", "finished", "upcoming"], state="readonly")
        self.entries['status'].grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.entries['status'].set("ongoing") # Default value

        # Save Button styling - Using global style from main.py
        self.style = ttk.Style()
        self.style.configure("FormSave.TButton", foreground="black", background="#28a745", font=("Arial", 10, "bold"), padding=5)
        self.style.map("FormSave.TButton", background=[('active', '#218838')])

        save_button = ttk.Button(form_frame, text="Save", command=self.save_course, style="FormSave.TButton")
        save_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")

    def load_course_data(self):
        """Loads existing course data into the form fields for editing."""
        if self.course_to_edit:
            print(f"DEBUG: load_course_data called for course: {self.course_to_edit.course_code}")

            course_code_entry = self.entries['course_code']
            
            # Temporarily set to normal, insert, then re-disable after a short delay
            # This is the key change for persistent display in disabled entry.
            course_code_entry.config(state='normal') # Enable to insert
            course_code_entry.delete(0, tk.END)
            course_code_entry.insert(0, self.course_to_edit.course_code)
            
            # Use after_idle to re-disable *after* Tkinter has processed the insert
            self.after_idle(lambda: course_code_entry.config(state='disabled'))


            self.entries['name'].delete(0, tk.END)
            self.entries['name'].insert(0, self.course_to_edit.name)
            self.entries['status'].set(self.course_to_edit.status)

            print(f"DEBUG: After load - Course Code Entry: '{course_code_entry.get()}' (State: {course_code_entry.cget('state')})")
            print(f"DEBUG: Course data loaded - Code: {self.course_to_edit.course_code}, Name: {self.course_to_edit.name}, Status: {self.course_to_edit.status}")


    def save_course(self):
        """Collects data from form and saves/updates course in DB."""
        try:
            course_code_entry = self.entries['course_code']
            
            # If in edit mode and course_code is effectively disabled (by being in course_to_edit context),
            # get original value from self.course_to_edit
            if self.course_to_edit: # We are in edit mode
                course_code = self.course_to_edit.course_code
            else: # We are in add mode
                course_code = course_code_entry.get().strip()

            name = self.entries['name'].get().strip()
            status = self.entries['status'].get().strip()

            print("\n--- Data collected from form for save (Course) ---")
            print(f"  Code: '{course_code}', Name: '{name}', Status: '{status}'")
            print("-------------------------------------------------")

            # Basic validation
            if not course_code:
                messagebox.showerror("Validation Error", "Course Code is required.")
                return
            if not name:
                messagebox.showerror("Validation Error", "Course Name is required.")
                return
            if not status:
                messagebox.showerror("Validation Error", "Status is required.")
                return
            if status not in ["ongoing", "finished", "upcoming"]:
                messagebox.showerror("Validation Error", "Invalid Status selected.")
                return

            new_course = Course(
                course_code=course_code,
                name=name,
                status=status
            )

            print("\n--- Course object being sent to controller ---")
            print(new_course.to_dict())
            print("---------------------------------------------")

            if self.course_to_edit:
                # This line is crucial for UPDATE SQL query to use the correct PK
                # new_course.course_code is already correctly set to self.course_to_edit.course_code above
                success = self.course_controller.update_course(new_course)
                action = "updated"
            else:
                success = self.course_controller.add_course(new_course)
                action = "added"

            if success:
                messagebox.showinfo("Success", f"Course {action} successfully!")
                self.refresh_callback()
                self.on_closing()
            else:
                messagebox.showerror("Error", f"Failed to {action} course. This might be due to a duplicate course code or database issues. Please check logs.")
                print(f"DEBUG: Course {action} failed. Database operation returned False.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during course save: {e}")
            print(f"UNHANDLED EXCEPTION IN save_course: {e}")
            import traceback
            traceback.print_exc()


    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

