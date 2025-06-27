import tkinter as tk
from tkinter import messagebox, ttk # Import ttk
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

        self.root_window = self

        # Initialize ttk Style object globally
        self.style = ttk.Style(self)
        self._configure_styles() # Call method to set up styles

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.db_manager = DBManager()
        self.current_user = None

        self.pages = {}
        self.after(100, self._initialize_pages)
        self.initial_page_shown = False

        if not self.db_manager.connect():
            messagebox.showerror("Database Error", "Could not connect to the database. Please check your config.py.")
            self.destroy()

    def _configure_styles(self):
        """Configures consistent ttk styles for the entire application."""
        # General Button Style (e.g., for Treeview action buttons)
        self.style.configure("General.TButton",
                             font=("Arial", 10),
                             foreground="black", # Ensured black
                             background="#e0e0e0", # Light grey
                             relief="raised",
                             padding=6) # Add padding for better touch/click area
        self.style.map("General.TButton",
                       background=[('active', '#cccccc')], # Darker grey on hover/click
                       foreground=[('disabled', '#808080')]) # Dim text when disabled

        # Save Button Style (for forms like Add/Edit)
        self.style.configure("FormSave.TButton",
                             font=("Arial", 10, "bold"),
                             foreground="black", # Ensured black
                             background="#28a745", # Green
                             relief="raised",
                             padding=8) # More padding for primary action
        self.style.map("FormSave.TButton",
                       background=[('active', '#218838')], # Darker green on hover/click
                       foreground=[('disabled', '#808080')])

        # Sidebar Buttons (from DashboardPage)
        self.style.configure("Sidebar.TButton",
                             font=("Arial", 12),
                             background="#34495e", # Dark blue/grey
                             foreground="white", # White text
                             relief="flat", # Flat appearance
                             borderwidth=0,
                             padding=[10, 10]) # Horizontal, Vertical padding
        self.style.map("Sidebar.TButton",
                       background=[('active', '#2c3e50')], # Slightly darker on hover/click
                       foreground=[('disabled', '#808080')]) # Dim text when disabled

        # Sidebar Logout Button
        self.style.configure("Sidebar.Logout.TButton",
                             font=("Arial", 12, "bold"),
                             background="#e74c3c", # Red
                             foreground="white", # White text
                             relief="flat",
                             borderwidth=0,
                             padding=[10, 10])
        self.style.map("Sidebar.Logout.TButton",
                       background=[('active', '#c0392b')], # Darker red
                       foreground=[('disabled', '#808080')])

        # Login Page Specific Buttons
        self.style.configure("Login.TButton",
                             font=("Arial", 12, "bold"),
                             background="#3498db", # Blue
                             foreground="white", # White text
                             relief="raised",
                             padding=10)
        self.style.map("Login.TButton",
                       background=[('active', '#2980b9')],
                       foreground=[('disabled', '#808080')])

        # LabelFrame Style (for Dashboard cards, Calendar, Filter frames)
        self.style.configure("TLabelframe",
                             background="#ecf0f1", # Same as background for consistency
                             foreground="#34495e", # Dark text for label title
                             font=("Arial", 11, "bold"),
                             relief="flat", # Flat borders
                             padding=[10, 5, 10, 10]) # L, T, R, B padding

        # Treeview Headings
        self.style.configure("Treeview.Heading",
                             font=("Arial", 10, "bold"),
                             background="#bdc3c7", # Light grey header
                             foreground="#2c3e50") # Dark text

        # Treeview Rows
        self.style.configure("Treeview",
                             font=("Arial", 10),
                             rowheight=25, # Increase row height for readability
                             background="#ffffff", # White background
                             foreground="#34495e", # Dark text
                             fieldbackground="#ffffff") # Background of cells
        self.style.map("Treeview",
                       background=[('selected', '#3498db')], # Blue on selection
                       foreground=[('selected', 'white')]) # White text on selection

        # Frame styles
        self.style.configure("HomeFrame.TFrame", background="#ecf0f1")
        self.style.configure("Card.TLabelframe", background="#ecf0f1", relief="flat", borderwidth=0) # Make cards blend
        self.style.configure("Calendar.TLabelframe", background="#ecf0f1", relief="groove", borderwidth=1) # Calendar with a border
        self.style.configure("CalendarDay.TFrame", background="#ecf0f1", relief="flat", borderwidth=1, bordercolor="#cccccc")
        self.style.configure("CurrentDay.TFrame", background="#e0f7fa", bordercolor="#2196f3", relief="solid", borderwidth=2)
        self.style.configure("EmptyDay.TFrame", background="#f8f9fa", relief="flat", borderwidth=0) # Lighter grey for empty days

        # NEW: Style for the buttons in CreateEditTemplateForm's question management section
        self.style.configure("QuestionForm.TButton",
                             font=("Arial", 10),
                             foreground="black", # Ensure black foreground
                             background="#e0e0e0", # Light grey background
                             relief="raised",
                             padding=6)
        self.style.map("QuestionForm.TButton",
                       background=[('active', '#cccccc')],
                       foreground=[('disabled', '#808080')])


    def _initialize_pages(self):
        self.pages["LoginPage"] = LoginPage(parent=self.container, controller=self)
        self.pages["LoginPage"].grid(row=0, column=0, sticky="nsew")

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
