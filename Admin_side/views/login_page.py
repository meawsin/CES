# views/login_page.py

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller # This is the main application controller
        self.auth_controller = AuthController() # Instantiate the auth controller

        self.configure(bg="#2C3E50") # Dark background for login page

        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the login form to center it
        login_frame = ttk.Frame(self, padding="30 30 30 30", style="Login.TFrame")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        
        title_label = ttk.Label(login_frame, text="Admin Login", font=("Arial", 30, "bold"), background="#ECF0F1", foreground="#34495E")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Email
        email_label = ttk.Label(login_frame, text="Email:", font=("Arial", 24,))
        email_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.email_entry = ttk.Entry(login_frame, width=30, font=("Arial", 24,))
        self.email_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.email_entry.insert(0, "so1ICT@bup.com") # Pre-fill for quick testing

        # Password
        password_label = ttk.Label(login_frame, text="Password:", font=("Arial", 24,))
        password_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ttk.Entry(login_frame, show="*", width=30,font=("Arial", 24,))
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.password_entry.insert(0, "1234") # Pre-fill for quick testing

        # Login Button
        login_button = ttk.Button(login_frame, text="Login", command=self.handle_login, style="Login.TButton")
        # The 'Login.TButton' style is defined in main.py to have white foreground on its blue background.
        login_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Error Message Label
        self.error_label = ttk.Label(login_frame, text="", foreground="red", background="#ECF0F1")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

    def handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self.error_label.config(text="Email and Password cannot be empty.")
            return

        admin_user = self.auth_controller.authenticate_admin(email, password)

        if admin_user:
            self.error_label.config(text="") # Clear any previous error
            self.parent_controller.set_current_user(admin_user)
            messagebox.showinfo("Login Success", f"Welcome, {admin_user.name}!")
            self.parent_controller.show_page("DashboardPage", admin_user) # Navigate to Dashboard
        else:
            self.error_label.config(text="Invalid email or password.")
            messagebox.showerror("Login Failed", "Invalid email or password. Please try again.")

