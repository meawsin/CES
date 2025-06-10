# views/add_edit_course_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.course_model import Course # Assuming Course model is defined

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

        self.create_widgets()
        if self.course_to_edit:
            self.load_course_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.course_code_entry = ttk.Entry(form_frame, width=30)
        self.course_code_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        if self.course_to_edit:
            self.course_code_entry.config(state="disabled")

        ttk.Label(form_frame, text="Course Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.status_combo = ttk.Combobox(form_frame, values=["ongoing", "finished", "upcoming"], state="readonly")
        self.status_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.status_combo.set("ongoing") # Default value

        save_button = ttk.Button(form_frame, text="Save", command=self.save_course)
        save_button.grid(row=3, column=0, columnspan=2, pady=20)

    def load_course_data(self):
        if self.course_to_edit:
            self.course_code_entry.insert(0, self.course_to_edit.course_code)
            self.name_entry.insert(0, self.course_to_edit.name)
            self.status_combo.set(self.course_to_edit.status)

    def save_course(self):
        course_code = self.course_code_entry.get().strip()
        name = self.name_entry.get().strip()
        status = self.status_combo.get().strip()

        if not course_code or not name or not status:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        new_course = Course(
            course_code=course_code,
            name=name,
            status=status
        )

        if self.course_to_edit:
            success = self.course_controller.update_course(new_course)
            action = "updated"
        else:
            success = self.course_controller.add_course(new_course)
            action = "added"

        if success:
            messagebox.showinfo("Success", f"Course {action} successfully!")
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", f"Failed to {action} course. Course code might already exist.")