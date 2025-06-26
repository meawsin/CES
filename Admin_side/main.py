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

        # NEW: Explicitly store a reference to the Tkinter root window for Toplevel parenting
        self.root_window = self

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None

        self.pages = {}
        self._initialize_pages()

        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py.")
            self.destroy()

        self.show_page("LoginPage")

    def _initialize_pages(self):
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name, user_data=None):
        page = self.pages.get(page_name)

        if page_name == "DashboardPage":
            if not self.current_user:
                messagebox.showwarning("Access Denied", "Please log in first.")
                return

            if "DashboardPage" not in self.pages:
                self.pages["DashboardPage"] = DashboardPage(parent=self.container, controller=self, admin_user=self.current_user)
                self.pages["DashboardPage"].grid(row=0, column=0, sticky="nsew")
                page = self.pages["DashboardPage"]
            else:
                page = self.pages["DashboardPage"]
                page.update_user_info(self.current_user)

        if page:
            page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.")

    def set_current_user(self, user):
        self.current_user = user

    def get_current_user(self):
        return self.current_user

    # NEW: Method to expose the root Tkinter window
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