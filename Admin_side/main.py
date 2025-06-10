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
        self.geometry("1200x800") # A good starting size for desktop app
        self.minsize(1000, 700)
        self.state('zoomed') # Start maximized

        # Central frame to hold all pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None # To store the logged-in admin object

        self.pages = {}
        self._initialize_pages()

        # Attempt to connect to DB at startup
        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py.")
            self.destroy() # Close application if DB connection fails

        self.show_page("LoginPage")

    def _initialize_pages(self):
        """Initializes all main application pages."""
        # LoginPage is always accessible directly
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

        # DashboardPage will be initialized only upon successful login
        # We pass self (the app instance) as the controller for the dashboard to manage page switching
        # The dashboard_page itself will manage its internal sub-pages (HR, Course Setup, etc.)

    def show_page(self, page_name, user_data=None):
        """
        Shows the requested page.
        If it's the dashboard, it passes user_data (logged-in admin).
        """
        page = self.pages.get(page_name)

        if page_name == "DashboardPage":
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first.")
                return
            # If dashboard not yet initialized, do it now
            if "DashboardPage" not in self.pages:
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
            else:
                # If already exists, update user info and re-render if necessary
                self.pages["DashboardPage"].update_user_info(self.current_user)


        if page:
            page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        """Sets the currently logged-in user."""
        self.current_user = user

    def get_current_user(self):
        """Returns the currently logged-in user."""
        return self.current_user

    def on_closing(self):
        """Handles application closing, ensuring database connection is closed."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db_manager.disconnect()
            self.destroy()

if __name__ == "__main__":
    app = CourseEvaluationApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle window close button
    app.mainloop()