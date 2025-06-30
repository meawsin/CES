# Admin_side/main.py

import customtkinter as ctk
from tkinter import messagebox, ttk # Import ttk for themed widgets
from views.login_page import LoginPage
from views.dashboard_page import DashboardPage
from database.db_manager import DBManager # For database connection management
from config import APP_NAME # Application name from config
from datetime import datetime, timedelta # For auto-logout functionality

class CourseEvaluationApp(ctk.CTk):
    """
    Main application class for the Course Evaluation System (Admin Side).
    Uses customtkinter for modern UI and dark/light mode support.
    Manages pages, user sessions, database connection, and auto-logout.
    """
    def __init__(self):
        super().__init__()
        self.title(APP_NAME) # Set window title
        self.geometry("1200x800") # Set initial window size
        self.minsize(1000, 700)   # Set minimum window size
        self.state('zoomed')      # Start window maximized

        self.root_window = self # Reference to the root Tkinter window

        # Set default appearance mode
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Main container frame where all pages will be displayed
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager() # Database manager instance
        self.current_user = None      # Stores the currently logged-in admin user

        self.pages = {} # Dictionary to hold references to different application pages
        self.after(100, self._initialize_pages) # Initialize pages after a short delay
        self.initial_page_shown = False # Flag to ensure login page is shown once

        # Attempt to connect to the database on startup
        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py and ensure MySQL is running.")
            self.destroy() # Close the application if DB connection fails
            return # Exit init if DB connection fails

        # --- Auto-logout related attributes and setup ---
        self.auto_logout_interval_minutes = 30 # Default auto-logout duration
        self.last_activity_time = datetime.now() # Timestamp of last user activity
        self._start_activity_monitoring() # Start listening for user activity
        self._schedule_auto_logout_check() # Schedule periodic checks for inactivity

        # Initialize theme
        self.current_theme = "light"  # Default theme
        
        # Bind the window closing protocol to our custom handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configure_styles(self):
        """
        Configures consistent ttk styles for the entire application.
        This ensures a uniform look and feel across different widgets.
        Button foregrounds are set for optimal contrast:
        - White text on dark backgrounds (Sidebar, Login buttons)
        - Black text on light backgrounds (General, FormSave buttons)
        """
        # General Button Style (e.g., for Treeview action buttons)
        self.style.configure("General.TButton",
                             font=("Arial", 10),
                             foreground="black", # Black text on light backgrounds
                             background="#E0E0E0", # Light grey
                             relief="raised",
                             padding=6)
        self.style.map("General.TButton",
                       background=[('active', '#CCCCCC')], # Darker grey on hover/click
                       foreground=[('disabled', '#808080')]) # Dim text when disabled

        # Save Button Style (for forms like Add/Edit)
        self.style.configure("FormSave.TButton",
                             font=("Arial", 10, "bold"),
                             foreground="black", # Black text on light backgrounds
                             background="#28A745", # Green
                             relief="raised",
                             padding=8)
        self.style.map("FormSave.TButton",
                       background=[('active', '#218838')], # Darker green on hover/click
                       foreground=[('disabled', '#808080')])

        # Sidebar Buttons (from DashboardPage)
        self.style.configure("Sidebar.TButton",
                             font=("Arial", 12),
                             background="#34495E", # Dark blue/grey
                             foreground="black", # White text on dark background
                             relief="flat", # Flat appearance
                             borderwidth=0,
                             padding=[10, 10])
        self.style.map("Sidebar.TButton",
                       background=[('active', '#2C3E50')], # Slightly darker on hover/click
                       foreground=[('disabled', '#808080')])

        # Sidebar Logout Button
        self.style.configure("Sidebar.Logout.TButton",
                             font=("Arial", 12, "bold"),
                             background="#E74C3C", # Red
                             foreground="black", # White text on dark background
                             relief="flat",
                             borderwidth=0,
                             padding=[10, 10])
        self.style.map("Sidebar.Logout.TButton",
                       background=[('active', '#C0392B')], # Darker red
                       foreground=[('disabled', '#808080')])

        # Login Page Specific Buttons
        self.style.configure("Login.TButton",
                             font=("Arial", 24, "bold"),
                             background="#3498DB", # Blue
                             foreground="black", # White text on dark background
                             relief="raised",
                             padding=10)
        self.style.map("Login.TButton",
                       background=[('active', '#2980B9')],
                       foreground=[('disabled', '#808080')])

        # LabelFrame Style (for Dashboard cards, Calendar, Filter frames)
        self.style.configure("TLabelframe",
                             background="#ECF0F1", # Same as background for consistency
                             foreground="#34495E", # Dark text for label title
                             font=("Arial", 11, "bold"),
                             relief="flat", # Flat borders
                             padding=[10, 5, 10, 10])

        # Treeview Headings
        self.style.configure("Treeview.Heading",
                             font=("Arial", 10, "bold"),
                             background="#BDC3C7", # Light grey header
                             foreground="#2C3E50") # Dark text

        # Treeview Rows
        self.style.configure("Treeview",
                             font=("Arial", 10),
                             rowheight=25, # Increase row height for readability
                             background="#FFFFFF", # White background
                             foreground="#34495E", # Dark text
                             fieldbackground="#FFFFFF") # Background of cells
        self.style.map("Treeview",
                       background=[('selected', '#3498DB')], # Blue on selection
                       foreground=[('selected', 'white')]) # White text on selection

        # Frame styles specific to the dashboard home content
        self.style.configure("HomeFrame.TFrame", background="#ECF0F1")
        self.style.configure("Card.TLabelframe", background="#ECF0F1", relief="flat", borderwidth=0)
        self.style.configure("Calendar.TLabelframe", background="#ECF0F1", relief="groove", borderwidth=1)
        self.style.configure("CalendarDay.TFrame", background="#ECF0F1", relief="flat", borderwidth=1, bordercolor="#CCCCCC")
        self.style.configure("CurrentDay.TFrame", background="#E0F7FA", bordercolor="#2196F3", relief="solid", borderwidth=2)
        self.style.configure("EmptyDay.TFrame", background="#F8F9FA", relief="flat", borderwidth=0)

        # Style for the buttons in CreateEditTemplateForm's question management section
        self.style.configure("QuestionForm.TButton",
                             font=("Arial", 10),
                             foreground="black",
                             background="#E0E0E0",
                             relief="raised",
                             padding=6)
        self.style.map("QuestionForm.TButton",
                       background=[('active', '#CCCCCC')],
                       foreground=[('disabled', '#808080')])


    def _initialize_pages(self):
        """
        Initializes and places the login page.
        """
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

        # Show the login page initially if not already shown
        if not self.initial_page_shown:
            self.show_page("LoginPage")
            self.initial_page_shown = True

    def show_page(self, page_name, user_data=None):
        """
        Raises the requested page to the top. Creates DashboardPage if it doesn't exist.
        :param page_name: The name of the page to show (e.g., "LoginPage", "DashboardPage").
        :param user_data: Optional user data to pass to the page (e.g., admin_user object).
        """
        page = self.pages.get(page_name)

        if page_name == "DashboardPage":
            # Ensure a user is logged in before showing the dashboard
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first to access the dashboard.")
                return

            # Lazily create DashboardPage if it hasn't been created yet
            if "DashboardPage" not in self.pages:
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
                page = self.pages["DashboardPage"]
            else:
                # If dashboard already exists, just update its user info and ensure it's in home view
                page = self.pages["DashboardPage"]
                page.update_user_info(self.current_user)
                page.show_home_content() # Always return to home content when showing dashboard

        if page:
            page.tkraise() # Bring the selected page to the front
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        """
        Sets the current logged-in user and updates auto-logout settings based on user preferences.
        :param user: The Admin object of the logged-in user.
        """
        self.current_user = user
        if user:
            # Dynamically import AppSettingsController here to avoid circular imports
            from controllers.app_settings_controller import AppSettingsController
            settings_controller = AppSettingsController()
            settings = settings_controller.get_admin_settings(user.admin_id)
            if settings:
                self.auto_logout_interval_minutes = settings.auto_logout_minutes
            else:
                self.auto_logout_interval_minutes = 30 # Fallback to default if no settings found
            self.last_activity_time = datetime.now() # Reset activity time on successful login

    def get_current_user(self):
        """
        Returns the currently logged-in Admin user object.
        """
        return self.current_user

    def get_root_window(self):
        """
        Returns a reference to the main Tkinter window. Useful for Toplevel dialogs.
        """
        return self.root_window

    def on_closing(self):
        """
        Handles the application's close event, prompting the user and disconnecting from the DB.
        """
        if messagebox.askokcancel("Quit Application", "Do you want to quit the Course Evaluation System?"):
            self.db_manager.disconnect() # Disconnect from the database
            self.destroy() # Destroy the Tkinter root window

    # --- Auto-logout implementation ---
    def _start_activity_monitoring(self):
        """
        Binds events to detect user activity (keyboard presses, mouse movements)
        and update the last activity timestamp.
        """
        # Bind to any key press and mouse motion events on the entire window
        self.bind_all("<Any-Key>", self._on_activity)
        self.bind_all("<Motion>", self._on_activity)

    def _on_activity(self, event=None):
        """
        Event handler for user activity. Updates the last activity timestamp.
        """
        self.last_activity_time = datetime.now()

    def _schedule_auto_logout_check(self):
        """
        Schedules a periodic check for user inactivity.
        """
        # Check every 5 seconds (5000 milliseconds)
        self.after(5000, self._check_auto_logout)

    def _check_auto_logout(self):
        """
        Checks if the user has been inactive for longer than the auto-logout interval.
        If so, logs out the user.
        """
        if self.current_user: # Only check if a user is currently logged in
            inactivity_duration = datetime.now() - self.last_activity_time
            if inactivity_duration > timedelta(minutes=self.auto_logout_interval_minutes):
                messagebox.showwarning("Session Expired", f"You have been inactive for {self.auto_logout_interval_interval_minutes} minutes and have been logged out automatically.")
                self.logout_user() # Perform the logout
                return # Stop further checks after logout to avoid re-triggering
        
        # Reschedule the next check if still active or no user logged in
        self._schedule_auto_logout_check()

    def logout_user(self):
        """
        Handles the complete logout process: clears user session,
        performs backend logout, and navigates back to the login page.
        """
        if self.current_user:
            # Dynamically import AuthController here to avoid circular imports
            from controllers.auth_controller import AuthController
            auth_controller = AuthController()
            auth_controller.logout_admin() # Perform any backend logout operations (e.g., invalidate token)
            self.set_current_user(None) # Clear the current user in the main app state
            self.show_page("LoginPage") # Navigate back to the login page
        
    def update_auto_logout_interval(self):
        """
        Called by the AppSettingsPage to update the auto-logout interval
        after a user saves new settings.
        """
        if self.current_user:
            from controllers.app_settings_controller import AppSettingsController
            settings_controller = AppSettingsController()
            settings = settings_controller.get_admin_settings(self.current_user.admin_id)
            if settings:
                self.auto_logout_interval_minutes = settings.auto_logout_minutes
                print(f"Auto-logout interval updated to {self.auto_logout_interval_minutes} minutes.")

    def apply_theme(self, theme):
        """
        Applies the selected theme to the application using customtkinter.
        :param theme: 'light' or 'dark'
        """
        if theme == "dark":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        # No need to manually update widget backgrounds; customtkinter handles it.
        for page in self.pages.values():
            if hasattr(page, 'update_theme'):
                page.update_theme(theme)

if __name__ == "__main__":
    # IMPORTANT: To run this application and avoid ModuleNotFoundError,
    # you should execute this script from the project's root directory.
    # For example, if 'Admin_side' is inside 'my_project_root/', navigate to 'my_project_root/'
    # in your terminal and then run: `python Admin_side/main.py`
    app = CourseEvaluationApp()
    app.mainloop()

