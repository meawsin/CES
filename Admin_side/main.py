# Admin_side/main.py

import customtkinter as ctk
from tkinter import messagebox
from views.login_page import LoginPage
from views.dashboard_page import DashboardPage
from database.db_manager import DBManager
from config import APP_NAME
from datetime import datetime, timedelta
from controllers.app_settings_controller import AppSettingsController

class CourseEvaluationApp(ctk.CTk):
    """
    Main application class for the Course Evaluation System (Admin Side).
    Manages pages, user sessions, database connection, and auto-logout.
    Now uses CustomTkinter for enhanced UI and supports maximized window.
    """
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        # Set the window to maximized state, not fullscreen
        self.state('zoomed')

        self.root_window = self

        # CustomTkinter global theme setup.
        # The login page will use hardcoded colors, so its appearance won't change with this.
        # The dashboard and other pages will respond to this.
        ctk.set_appearance_mode("Light") # Default to Light mode for the main app after login
        ctk.set_default_color_theme("blue") # A default color theme for the main app

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None
        self.app_settings_controller = AppSettingsController()

        self.pages = {}
        self.after(100, self._initialize_pages)
        self.initial_page_shown = False

        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py and ensure MySQL is running.")
            self.destroy()
            return

        self.auto_logout_interval_minutes = 30
        self.last_activity_time = datetime.now()
        self._start_activity_monitoring()
        self._schedule_auto_logout_check()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configure_styles(self):
        """
        CustomTkinter handles its own theming. This method is now empty
        as explicit ttk.Style configurations are no longer needed for CTk widgets.
        """
        pass

    def _initialize_pages(self):
        """
        Initializes and places the login page.
        """
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

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
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first to access the dashboard.")
                return

            if "DashboardPage" not in self.pages:
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
                page = self.pages["DashboardPage"]
            else:
                page = self.pages["DashboardPage"]
                page.update_user_info(self.current_user)
                page.show_home_content()

        if page:
            page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        """
        Sets the current logged-in user and updates auto-logout settings based on user preferences.
        Also applies the user's saved theme.
        :param user: The Admin object of the logged-in user.
        """
        self.current_user = user
        if user:
            settings = self.app_settings_controller.get_admin_settings(user.admin_id)
            if settings:
                self.auto_logout_interval_minutes = settings.auto_logout_minutes
                self.apply_theme(settings.theme) # Apply user's saved theme
            else:
                self.auto_logout_interval_minutes = 30
                self.apply_theme("Light") # Default to light theme if no settings found
            self.last_activity_time = datetime.now()
        else:
            # When logging out, revert to the default theme for the main app, not login page
            self.apply_theme("Light") # Revert to default light for dashboard elements

    def get_current_user(self):
        """
        Returns the currently logged-in Admin user object.
        """
        return self.current_user

    def get_root_window(self):
        """
        Returns a reference to the main CustomTkinter window. Useful for CTkToplevel dialogs.
        """
        return self.root_window

    def on_closing(self):
        """
        Handles the application's close event, prompting the user and disconnecting from the DB.
        """
        if messagebox.askokcancel("Quit Application", "Do you want to quit the Course Evaluation System?"):
            self.db_manager.disconnect()
            self.destroy()

    def _start_activity_monitoring(self):
        self.bind_all("<Any-Key>", self._on_activity)
        self.bind_all("<Motion>", self._on_activity)

    def _on_activity(self, event=None):
        self.last_activity_time = datetime.now()

    def _schedule_auto_logout_check(self):
        self.after(5000, self._check_auto_logout)

    def _check_auto_logout(self):
        if self.current_user:
            inactivity_duration = datetime.now() - self.last_activity_time
            if inactivity_duration > timedelta(minutes=self.auto_logout_interval_minutes):
                messagebox.showwarning("Session Expired", f"You have been inactive for {self.auto_logout_interval_minutes} minutes and have been logged out automatically.")
                self.logout_user()
                return
        self._schedule_auto_logout_check()

    def logout_user(self):
        from controllers.auth_controller import AuthController
        auth_controller = AuthController()
        auth_controller.logout_admin()
        self.set_current_user(None)
        self.show_page("LoginPage")
        
    def update_auto_logout_interval(self):
        if self.current_user:
            settings = self.app_settings_controller.get_admin_settings(self.current_user.admin_id)
            if settings:
                self.auto_logout_interval_minutes = settings.auto_logout_minutes
                self.apply_theme(settings.theme)
                print(f"Auto-logout interval updated to {self.auto_logout_interval_minutes} minutes and theme applied: {settings.theme}.")
            else:
                print("Could not retrieve updated settings for auto-logout.")

    def apply_theme(self, theme_name):
        """
        Applies the specified theme (Light or Dark) to the CustomTkinter application.
        :param theme_name: "Light" or "Dark".
        """
        ctk.set_appearance_mode(theme_name)
        print(f"Applied theme: {theme_name}")


if __name__ == "__main__":
    app = CourseEvaluationApp()
    app.mainloop()

