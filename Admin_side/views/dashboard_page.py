# views/dashboard_page.py (Updated for Iteration 3)
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from views.hr_students_page import HRStudentsPage
from views.hr_faculty_page import HRFacultyPage
from views.hr_admins_page import HRAdminsPage
from views.course_setup_page import CourseSetupPage             # NEW
from views.evaluation_templates_page import EvaluationTemplatesPage # NEW

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller, admin_user=None):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.auth_controller = AuthController()
        self.admin_user = admin_user

        self.configure(bg="#ecf0f1")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

        self.sub_pages = {}
        self._initialize_sub_pages()

        self.show_home_content()

        self.update_user_info(admin_user)

    def create_sidebar(self):
        self.sidebar_frame = tk.Frame(self, bg="#34495e", width=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.user_info_label = ttk.Label(self.sidebar_frame, text="",
                                         font=("Arial", 14, "bold"), foreground="white", background="#34495e",
                                         anchor="center")
        self.user_info_label.pack(pady=20, fill="x")

        nav_buttons_config = [
            ("Home", self.show_home_content),
            ("HR Management", self.show_hr_management_wrapper),
            ("Course Setup", self.show_course_setup),          # Modified
            ("Evaluation", self.show_evaluation_templates),   # Modified
            ("Reports", self.show_reports),
            ("Complaints", self.show_complaints),
            ("Comparison", self.show_comparison),
            ("Application settings", self.show_app_settings),
        ]

        self.nav_buttons = []
        for text, command in nav_buttons_config:
            btn = ttk.Button(self.sidebar_frame, text=text, command=command, style="Sidebar.TButton")
            btn.pack(fill="x", pady=5, padx=10)
            self.nav_buttons.append(btn)

        logout_button = ttk.Button(self.sidebar_frame, text="Logout", command=self.handle_logout, style="Sidebar.Logout.TButton")
        logout_button.pack(fill="x", pady=20, padx=10, side="bottom")

        self.style = ttk.Style()
        self.style.configure("Sidebar.TButton", font=("Arial", 12), background="#34495e", foreground="white", relief="flat", borderwidth=0)
        self.style.map("Sidebar.TButton", background=[('active', '#2c3e50')])
        self.style.configure("Sidebar.Logout.TButton", font=("Arial", 12, "bold"), background="#e74c3c", foreground="white", relief="flat", borderwidth=0)
        self.style.map("Sidebar.Logout.TButton", background=[('active', '#c0392b')])


    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg="#ecf0f1")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _initialize_sub_pages(self):
        self.sub_pages["HomeContent"] = self._create_home_content()

        self.hr_notebook = ttk.Notebook(self.content_frame)
        self.sub_pages["HRManagementWrapper"] = self.hr_notebook

        self.hr_students_tab = HRStudentsPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_faculty_tab = HRFacultyPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_admins_tab = HRAdminsPage(parent=self.hr_notebook, controller=self.parent_controller)

        self.hr_notebook.add(self.hr_students_tab, text="Students")
        self.hr_notebook.add(self.hr_faculty_tab, text="Faculty")
        self.hr_notebook.add(self.hr_admins_tab, text="Admins")

        # NEW: Course Setup Page
        self.sub_pages["CourseSetupPage"] = CourseSetupPage(parent=self.content_frame, controller=self.parent_controller)

        # NEW: Evaluation Templates Page
        self.sub_pages["EvaluationTemplatesPage"] = EvaluationTemplatesPage(parent=self.content_frame, controller=self.parent_controller)

    def show_sub_page(self, page_widget):
        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

        if page_widget:
            page_widget.grid(row=0, column=0, sticky="nsew")
            page_widget.tkraise()
        else:
            messagebox.showerror("Error", "Selected content not available or not properly initialized.")

    def update_user_info(self, admin_user):
        self.admin_user = admin_user
        if self.admin_user:
            self.user_info_label.config(text=f"Welcome,\n{self.admin_user.name}")
            self._update_navigation_permissions()

    def _update_navigation_permissions(self):
        if not self.admin_user:
            return

        # Enable/disable main navigation buttons
        for btn in self.nav_buttons:
            text = btn.cget("text")
            if text == "HR Management":
                btn.config(state="normal" if self.admin_user.can_manage_users else "disabled")
            elif text == "Course Setup":
                btn.config(state="normal" if self.admin_user.can_manage_courses else "disabled")
            elif text == "Evaluation":
                btn.config(state="normal" if self.admin_user.can_create_templates else "disabled")
            elif text == "Reports":
                btn.config(state="normal" if self.admin_user.can_view_reports else "disabled")
            elif text == "Complaints":
                btn.config(state="normal" if self.admin_user.can_manage_complaints else "disabled")
            # For Comparison and App Settings, assume always enabled for any admin for now
            elif text in ["Comparison", "Application settings", "Home"]:
                btn.config(state="normal")


        # Enable/disable specific HR Management tabs based on permissions
        self.hr_notebook.tab(0, state='normal' if self.admin_user.can_manage_users else 'disabled') # Students tab
        self.hr_notebook.tab(1, state='normal' if self.admin_user.can_manage_users else 'disabled') # Faculty tab
        self.hr_notebook.tab(2, state='normal' if self.admin_user.can_manage_users else 'disabled') # Admins tab


    # --- Navigation Command Methods ---
    def show_home_content(self):
        self.show_sub_page(self.sub_pages["HomeContent"])

    def _create_home_content(self):
        home_frame = ttk.Frame(self.content_frame, padding="20")
        home_label = ttk.Label(home_frame, text="Welcome to the Admin Dashboard!",
                               font=("Arial", 20, "bold"), foreground="#34495e")
        home_label.pack(pady=50)
        desc_label = ttk.Label(home_frame, text="Use the navigation bar on the left to manage the system.",
                               font=("Arial", 14), foreground="#34495e")
        desc_label.pack()
        return home_frame

    def show_hr_management_wrapper(self):
        self.show_sub_page(self.hr_notebook)
        self.hr_notebook.select(self.hr_students_tab) # Default to Students tab

    def show_course_setup(self):
        if self.admin_user and self.admin_user.can_manage_courses:
            self.show_sub_page(self.sub_pages["CourseSetupPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage courses.")

    def show_evaluation_templates(self): # Renamed for clarity
        if self.admin_user and self.admin_user.can_create_templates:
            self.show_sub_page(self.sub_pages["EvaluationTemplatesPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to create evaluation templates.")

    def show_reports(self):
        if self.admin_user and self.admin_user.can_view_reports:
            messagebox.showinfo("Navigation", "Reports functionality coming soon!")
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports.")

    def show_complaints(self):
        if self.admin_user and self.admin_user.can_manage_complaints:
            messagebox.showinfo("Navigation", "Complaints functionality coming soon!")
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage complaints.")

    def show_comparison(self):
        if self.admin_user and self.admin_user.can_view_reports: # Comparison depends on reports
            messagebox.showinfo("Navigation", "Comparison functionality coming soon!")
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports for comparison.")

    def show_app_settings(self):
        messagebox.showinfo("Navigation", "Application Settings functionality coming soon!")

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.auth_controller.logout_admin()
            self.parent_controller.set_current_user(None)
            self.grid_forget()
            self.parent_controller.show_page("LoginPage")