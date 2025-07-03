# views/add_edit_course_form.py
import customtkinter as ctk
from models.course_model import Course # Assuming Course model is defined
from datetime import datetime # Import datetime for potential date handling if needed
from tkinter import messagebox

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AddEditCourseForm(ctk.CTkToplevel):
    def __init__(self, parent_window, course_controller, refresh_callback, course_to_edit=None):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.refresh_callback = refresh_callback
        self.course_to_edit = course_to_edit
        self.title("Edit Course Information" if self.course_to_edit else "Add New Course")
        self.geometry("500x400")
        self.configure(fg_color=GREY)
        self.create_widgets()
        if self.course_to_edit:
            self.load_course_data()
        if "course_code" in self.entries and self.entries['course_code'].cget('state') == 'normal':
            self.entries['course_code'].focus_set()
        elif "name" in self.entries and self.entries['name'].cget('state') == 'normal':
            self.entries['name'].focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Ensure the window stays on top and grabs focus
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)

    def create_widgets(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=True)
        ctk.CTkLabel(card, text=self.title(), font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        form_frame = ctk.CTkFrame(card, fg_color=WHITE)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.entries = {}
        row = 0
        def add_field(label, key, state="normal"):
            ctk.CTkLabel(form_frame, text=label, font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
            entry = ctk.CTkEntry(form_frame, width=260, font=("Arial", 17))
            entry.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
            entry.configure(state=state)
            self.entries[key] = entry
        add_field("Course Code:", "course_code", state="disabled" if self.course_to_edit else "normal"); row += 1
        add_field("Course Name:", "name"); row += 1
        ctk.CTkLabel(form_frame, text="Status:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row, column=0, sticky="w", pady=8, padx=5)
        status_combo = ctk.CTkComboBox(form_frame, values=["ongoing", "finished", "upcoming"], font=("Arial", 17), width=260)
        status_combo.grid(row=row, column=1, sticky="ew", pady=8, padx=5)
        status_combo.set("ongoing")
        self.entries['status'] = status_combo
        row += 1
        ctk.CTkButton(card, text="Save", command=self.save_course, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=18)
        form_frame.grid_columnconfigure(1, weight=1)

    def load_course_data(self):
        """Loads existing course data into the form fields for editing."""
        if self.course_to_edit:
            print(f"DEBUG: load_course_data called for course: {self.course_to_edit.course_code}")

            course_code_entry = self.entries['course_code']
            
            # Insert the course code and make it read-only (not disabled) for better visibility
            course_code_entry.delete(0, "end")
            course_code_entry.insert(0, self.course_to_edit.course_code)
            course_code_entry.configure(state='readonly')  # Read-only instead of disabled for better visibility

            self.entries['name'].delete(0, "end")
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
        self.attributes('-topmost', False)
        self.destroy()

