# views/assign_course_faculty_form.py
import customtkinter as ctk
from tkinter import messagebox, ttk

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class AssignCourseFacultyForm(ctk.CTkToplevel):
    def __init__(self, parent_window, course_controller, faculty_controller, selected_course_code, refresh_callback):
        super().__init__(parent_window)
        self.course_controller = course_controller
        self.faculty_controller = faculty_controller
        self.selected_course_code = selected_course_code
        self.refresh_callback = refresh_callback # Callback to refresh the parent treeview (e.g., in CourseSetupPage)

        self.title(f"Manage Faculty for {self.selected_course_code}")

        # Robust Toplevel setup
        self.transient(parent_window)
        self.grab_set()

        self.geometry("900x650")
        self.minsize(700, 400)

        self.create_widgets()
        self.load_faculty_lists()

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
        # Main card frame
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Title
        title_text = f"Manage Faculty for {self.selected_course_code}"
        ctk.CTkLabel(card, text=title_text, font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        
        # Main frame
        main_frame = ctk.CTkFrame(card, fg_color=WHITE)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1) # Available list column
        main_frame.columnconfigure(1, weight=0) # Buttons column (fixed size)
        main_frame.columnconfigure(2, weight=1) # Assigned list column
        main_frame.rowconfigure(1, weight=1) # Lists row (expands)

        # Column Headers
        ctk.CTkLabel(main_frame, text="Available Faculty", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=0, pady=5)
        ctk.CTkLabel(main_frame, text="Assigned Faculty", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=0, column=2, pady=5)

        # Search bar for available faculty
        self.available_faculty_search = ctk.CTkEntry(main_frame, width=200, placeholder_text="Search...")
        self.available_faculty_search.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 2))
        self.available_faculty_search.bind("<KeyRelease>", lambda e: self.filter_faculty_tree('available'))

        # Search bar for assigned faculty
        self.assigned_faculty_search = ctk.CTkEntry(main_frame, width=200, placeholder_text="Search...")
        self.assigned_faculty_search.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 2))
        self.assigned_faculty_search.bind("<KeyRelease>", lambda e: self.filter_faculty_tree('assigned'))

        # Available Faculty List with treeview
        available_frame = ctk.CTkFrame(main_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        available_frame.grid(row=2, column=0, sticky="nsew", padx=5)
        available_frame.grid_columnconfigure(0, weight=1)
        available_frame.grid_rowconfigure(0, weight=1)
        
        self.available_faculty_tree = ttk.Treeview(available_frame, columns=("ID", "Name", "Email"), show="headings", height=10)
        self.available_faculty_tree.heading("ID", text="Faculty ID")
        self.available_faculty_tree.heading("Name", text="Name")
        self.available_faculty_tree.heading("Email", text="Email")
        self.available_faculty_tree.column("ID", width=100, anchor="center")
        self.available_faculty_tree.column("Name", width=150)
        self.available_faculty_tree.column("Email", width=200)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        available_scrollbar = ctk.CTkScrollbar(available_frame, orientation="vertical", command=self.available_faculty_tree.yview)
        self.available_faculty_tree.configure(yscrollcommand=available_scrollbar.set)
        self.available_faculty_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        available_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        # Assign/Unassign Buttons (in a central frame)
        button_frame = ctk.CTkFrame(main_frame, fg_color=WHITE)
        button_frame.grid(row=2, column=1, padx=10, sticky="nsew")
        button_frame.rowconfigure(0, weight=1) # Push buttons to center vertically
        button_frame.rowconfigure(1, weight=0)
        button_frame.rowconfigure(2, weight=0)
        button_frame.rowconfigure(3, weight=1)

        ctk.CTkButton(button_frame, text="Assign >>", command=self.assign_faculty,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=1, column=0, pady=10)
        ctk.CTkButton(button_frame, text="<< Unassign", command=self.unassign_faculty,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).grid(row=2, column=0, pady=10)

        # Assigned Faculty List with treeview
        assigned_frame = ctk.CTkFrame(main_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        assigned_frame.grid(row=2, column=2, sticky="nsew", padx=5)
        assigned_frame.grid_columnconfigure(0, weight=1)
        assigned_frame.grid_rowconfigure(0, weight=1)
        
        self.assigned_faculty_tree = ttk.Treeview(assigned_frame, columns=("ID", "Name", "Email"), show="headings", height=10)
        self.assigned_faculty_tree.heading("ID", text="Faculty ID")
        self.assigned_faculty_tree.heading("Name", text="Name")
        self.assigned_faculty_tree.heading("Email", text="Email")
        self.assigned_faculty_tree.column("ID", width=100, anchor="center")
        self.assigned_faculty_tree.column("Name", width=150)
        self.assigned_faculty_tree.column("Email", width=200)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        assigned_scrollbar = ctk.CTkScrollbar(assigned_frame, orientation="vertical", command=self.assigned_faculty_tree.yview)
        self.assigned_faculty_tree.configure(yscrollcommand=assigned_scrollbar.set)
        self.assigned_faculty_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        assigned_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        # Done button at the bottom of the Toplevel
        ctk.CTkButton(self, text="Done", command=self.on_closing,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 19, "bold"), height=45, corner_radius=10).pack(pady=10, fill="x", padx=15)

    def load_faculty_lists(self):
        # Clear existing entries
        for i in self.available_faculty_tree.get_children():
            self.available_faculty_tree.delete(i)
        for i in self.assigned_faculty_tree.get_children():
            self.assigned_faculty_tree.delete(i)

        all_faculty = self.faculty_controller.get_all_faculty()
        assigned_faculty_for_course = self.course_controller.get_assigned_faculty_for_course(self.selected_course_code)

        assigned_ids = {f['faculty_id'] for f in assigned_faculty_for_course}

        print(f"DEBUG: Loading faculty lists for course {self.selected_course_code}")
        print(f"DEBUG: All faculty: {[f.faculty_id for f in all_faculty]}")
        print(f"DEBUG: Assigned faculty IDs: {assigned_ids}")

        # Store faculty data for later use
        self.available_faculty = []
        self.assigned_faculty = []

        for faculty in all_faculty:
            if faculty.faculty_id in assigned_ids:
                self.assigned_faculty.append(faculty)
                self.assigned_faculty_tree.insert("", "end", iid=faculty.faculty_id, values=(faculty.faculty_id, faculty.name, faculty.email))
            else:
                self.available_faculty.append(faculty)
                self.available_faculty_tree.insert("", "end", iid=faculty.faculty_id, values=(faculty.faculty_id, faculty.name, faculty.email))

    def assign_faculty(self):
        selected_item = self.available_faculty_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select faculty to assign.")
            return
        
        faculty_id = int(selected_item)
        faculty_name = self.available_faculty_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to assign faculty ID {faculty_id} to course {self.selected_course_code}")
        success = self.course_controller.assign_faculty_to_course(self.selected_course_code, faculty_id)
        if success:
            self.load_faculty_lists()
            self.refresh_callback()
            messagebox.showinfo("Success", f"Faculty {faculty_name} (ID: {faculty_id}) has been successfully assigned to the course.")
        else:
            messagebox.showerror("Error", f"Failed to assign faculty {faculty_name} (ID: {faculty_id}). Might already be assigned or a database error occurred.")
            print(f"DEBUG: Assignment failed for faculty ID {faculty_id}.")

    def unassign_faculty(self):
        selected_item = self.assigned_faculty_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select faculty to unassign.")
            return
        
        faculty_id = int(selected_item)
        faculty_name = self.assigned_faculty_tree.item(selected_item)['values'][1]
        
        print(f"DEBUG: Attempting to unassign faculty ID {faculty_id} from course {self.selected_course_code}")
        if messagebox.askyesno("Confirm Unassign", f"Are you sure you want to unassign {faculty_name} (ID: {faculty_id})?"):
            success = self.course_controller.unassign_faculty_from_course(self.selected_course_code, faculty_id)
            if success:
                print(f"DEBUG: Unassignment successful for faculty ID {faculty_id}.")
                self.load_faculty_lists()
                self.refresh_callback()
                messagebox.showinfo("Success", f"Faculty {faculty_name} (ID: {faculty_id}) has been successfully unassigned from the course.")
            else:
                messagebox.showerror("Error", f"Failed to unassign {faculty_name} (ID: {faculty_id}). A database error might have occurred.")
                print(f"DEBUG: Unassignment failed for faculty ID {faculty_id}.")

    def on_closing(self):
        """Handle the window closing event."""
        self.destroy()

    def filter_faculty_tree(self, which):
        # which: 'available' or 'assigned'
        if which == 'available':
            search = self.available_faculty_search.get().lower()
            tree = self.available_faculty_tree
            data = [(faculty.faculty_id, faculty.name, faculty.email) for faculty in self.available_faculty]
        else:
            search = self.assigned_faculty_search.get().lower()
            tree = self.assigned_faculty_tree
            data = [(faculty.faculty_id, faculty.name, faculty.email) for faculty in self.assigned_faculty]
        tree.delete(*tree.get_children())
        for row in data:
            if any(search in str(col).lower() for col in row):
                tree.insert("", "end", values=row)

