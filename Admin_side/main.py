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

        # Explicitly store a reference to the Tkinter root window for Toplevel parenting
        # This is already correctly done as self.root_window = self
        self.root_window = self

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None

        self.pages = {}
        # Delay initialization of pages slightly, to ensure root is fully ready
        self.after(100, self._initialize_pages) # Call after 100ms
        self.initial_page_shown = False # Flag to ensure page is shown only once after init

        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py.")
            self.destroy()


    def _initialize_pages(self):
        # We instantiate pages here, ensuring self.root_window is fully available
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

        # Now that pages are initialized, show the login page
        if not self.initial_page_shown:
            self.show_page("LoginPage")
            self.initial_page_shown = True


    def show_page(self, page_name, user_data=None):
        page = self.pages.get(page_name)

        if page_name == "DashboardPage":
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first.")
                return

            if "DashboardPage" not in self.pages:
                # IMPORTANT: Ensure DashboardPage receives the correct controller (self, the app root)
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
                page = self.pages["DashboardPage"]
            else:
                page = self.pages["DashboardPage"]
                page.update_user_info(self.current_user) # Update dashboard info on return

        if page:
            page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        self.current_user = user

    def get_current_user(self):
        return self.current_user

    # Method to expose the root Tkinter window
    def get_root_window(self):
        return self.root_window

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db_manager.disconnect()
            self.destroy()

if __name__ == "__main__":
    app = CourseEvaluationApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

