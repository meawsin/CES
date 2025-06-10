# views/dashboard_page.py (Updated)
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from views.hr_students_page import HRStudentsPage
from views.hr_faculty_page import HRFacultyPage # NEW
from views.hr_admins_page import HRAdminsPage   # NEW

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller, admin_user=None):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.auth_controller = AuthController()
        self.admin_user = admin_user

        self.configure(bg="#ecf0f1") # Light background for dashboard

        # Main layout: Sidebar (left) and Content Area (right)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Sidebar column
        self.grid_columnconfigure(1, weight=1) # Content column

        self.create_sidebar()
        self.create_content_area()

        # Initialize sub-pages that can be loaded into the content area
        self.sub_pages = {}
        self._initialize_sub_pages()

        self.show_home_content() # Default content on dashboard load

        self.update_user_info(admin_user) # Set initial user info

    def create_sidebar(self):
        # Sidebar Frame
        self.sidebar_frame = tk.Frame(self, bg="#34495e", width=250) # Dark blue sidebar
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) # Prevent sidebar from resizing to content

        # User Info
        self.user_info_label = ttk.Label(self.sidebar_frame, text="",
                                         font=("Arial", 14, "bold"), foreground="white", background="#34495e",
                                         anchor="center")
        self.user_info_label.pack(pady=20, fill="x")

        # Navigation Buttons
        nav_buttons_config = [
            ("Home", self.show_home_content),
            # HR Management will now open a nested frame
            ("HR Management", self.show_hr_management_wrapper), # Changed to a wrapper method
            ("Course Setup", self.show_course_setup),
            ("Evaluation", self.show_evaluation),
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

        # Logout Button at the bottom
        logout_button = ttk.Button(self.sidebar_frame, text="Logout", command=self.handle_logout, style="Sidebar.Logout.TButton")
        logout_button.pack(fill="x", pady=20, padx=10, side="bottom")

        # Style for sidebar buttons
        self.style = ttk.Style()
        self.style.configure("Sidebar.TButton", font=("Arial", 12), background="#34495e", foreground="white", relief="flat", borderwidth=0)
        self.style.map("Sidebar.TButton", background=[('active', '#2c3e50')])
        self.style.configure("Sidebar.Logout.TButton", font=("Arial", 12, "bold"), background="#e74c3c", foreground="white", relief="flat", borderwidth=0)
        self.style.map("Sidebar.Logout.TButton", background=[('active', '#c0392b')])


    def create_content_area(self):
        # Content Frame
        self.content_frame = tk.Frame(self, bg="#ecf0f1")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _initialize_sub_pages(self):
        """Initializes sub-pages that will be shown in the content area."""
        # Home Content (simple frame for now)
        self.sub_pages["HomeContent"] = self._create_home_content()

        # HR Management Tabbed Interface (Notebook)
        self.hr_notebook = ttk.Notebook(self.content_frame)
        self.sub_pages["HRManagementWrapper"] = self.hr_notebook # Store the notebook itself

        # HR Management Tabs
        self.hr_students_tab = HRStudentsPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_faculty_tab = HRFacultyPage(parent=self.hr_notebook, controller=self.parent_controller) # NEW
        self.hr_admins_tab = HRAdminsPage(parent=self.hr_notebook, controller=self.parent_controller)     # NEW

        self.hr_notebook.add(self.hr_students_tab, text="Students")
        self.hr_notebook.add(self.hr_faculty_tab, text="Faculty")
        self.hr_notebook.add(self.hr_admins_tab, text="Admins")


        # Add other sub-pages here as they are developed (e.g., Course Setup Page)
        # self.sub_pages["CourseSetupPage"] = CourseSetupPage(parent=self.content_frame, controller=self.parent_controller)


    def show_sub_page(self, page_widget):
        """Hides current sub-page and shows the selected one."""
        # Ensure all existing sub-page widgets are forgotten from the content_frame's grid
        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

        # Place the new page_widget
        if page_widget:
            page_widget.grid(row=0, column=0, sticky="nsew")
            page_widget.tkraise()
        else:
            messagebox.showerror("Error", "Selected content not available or not properly initialized.")


    def update_user_info(self, admin_user):
        """Updates user info displayed on the dashboard."""
        self.admin_user = admin_user
        if self.admin_user:
            self.user_info_label.config(text=f"Welcome,\n{self.admin_user.name}")
            self._update_navigation_permissions()

    def _update_navigation_permissions(self):
        """Enables/disables sidebar buttons and HR tabs based on admin permissions."""
        if not self.admin_user:
            return

        # Enable/disable main navigation buttons (you'll expand this for all)
        # For simplicity, let's assume if an admin can manage users, they can access HR Management.
        # This logic needs to be more granular per menu item later.
        for i, btn in enumerate(self.nav_buttons):
            # Example: Assuming index 1 is "HR Management"
            if btn.cget("text") == "HR Management" and not self.admin_user.can_manage_users:
                btn.config(state="disabled")
            elif btn.cget("text") == "Reports" and not self.admin_user.can_view_reports:
                btn.config(state="disabled")
            elif btn.cget("text") == "Evaluation" and not self.admin_user.can_create_templates:
                 btn.config(state="disabled")
            elif btn.cget("text") == "Complaints" and not self.admin_user.can_manage_complaints:
                 btn.config(state="disabled")
            elif btn.cget("text") == "Course Setup" and not self.admin_user.can_manage_courses:
                 btn.config(state="disabled")
            else:
                btn.config(state="normal") # Default to normal if no specific restriction


        # Enable/disable specific HR Management tabs based on permissions
        # Find the index of the tabs within the notebook and enable/disable
        # For example, Students (index 0), Faculty (index 1), Admins (index 2)
        # Note: self.hr_notebook.tab(tab_id, state='disabled'/'normal')
        if not self.admin_user.can_manage_users:
            self.hr_notebook.tab(0, state='disabled') # Students tab
            self.hr_notebook.tab(1, state='disabled') # Faculty tab
            self.hr_notebook.tab(2, state='disabled') # Admins tab
        else:
            self.hr_notebook.tab(0, state='normal')
            self.hr_notebook.tab(1, state='normal')
            self.hr_notebook.tab(2, state='normal')

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
        """Shows the HR Management Notebook with its tabs."""
        self.show_sub_page(self.hr_notebook)
        # Select the default tab (e.g., Students tab)
        self.hr_notebook.select(self.hr_students_tab)


    def show_course_setup(self):
        if self.admin_user and self.admin_user.can_manage_courses:
            messagebox.showinfo("Navigation", "Course Setup functionality coming soon!")
            # self.show_sub_page(self.sub_pages["CourseSetupPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage courses.")


    def show_evaluation(self):
        if self.admin_user and self.admin_user.can_create_templates:
            messagebox.showinfo("Navigation", "Evaluation functionality coming soon!")
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
        # Comparison usually requires viewing reports, so linking to that permission
        if self.admin_user and self.admin_user.can_view_reports:
            messagebox.showinfo("Navigation", "Comparison functionality coming soon!")
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports for comparison.")

    def show_app_settings(self):
        # App settings are usually accessible to all admins or a specific role
        messagebox.showinfo("Navigation", "Application Settings functionality coming soon!")

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.auth_controller.logout_admin()
            self.parent_controller.set_current_user(None) # Clear current user
            # Reset dashboard state (optional, or just let login page overwrite)
            self.grid_forget() # Hide dashboard
            self.parent_controller.show_page("LoginPage")