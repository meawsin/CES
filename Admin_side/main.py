# main.py
import tkinter as tk
from tkinter import messagebox
from views.login_page import LoginPage
from views.dashboard_page import DashboardPage
from database.db_manager import DBManager
from config import APP_NAME

class CourseEvaluationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.state('zoomed')

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None

        self.pages = {}
        self._initialize_pages() # This will only initialize LoginPage initially

        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py.")
            self.destroy()

        self.show_page("LoginPage")

    def _initialize_pages(self):
        """Initializes all main application pages that are always present or need initial setup."""
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

        # DashboardPage is NOT initialized here initially.
        # It will be initialized dynamically the first time it's needed.

    def show_page(self, page_name, user_data=None):
        """
        Shows the requested page.
        Dynamically initializes DashboardPage the first time it's accessed.
        """
        page = self.pages.get(page_name)

        if page_name == "DashboardPage":
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first.")
                return

            # Check if DashboardPage has already been created and stored
            if "DashboardPage" not in self.pages:
                # Create DashboardPage instance for the first time
                # Pass self (the app instance) as the controller for the dashboard
                # and the logged-in admin_user
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
                page = self.pages["DashboardPage"] # Set 'page' to the newly created instance
            else:
                # If DashboardPage already exists, just retrieve it and update user info
                page = self.pages["DashboardPage"]
                page.update_user_info(self.current_user) # Update user info in case it changed (e.g., re-login)

        if page:
            page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        self.current_user = user

    def get_current_user(self):
        return self.current_user

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db_manager.disconnect()
            self.destroy()

if __name__ == "__main__":
    app = CourseEvaluationApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()