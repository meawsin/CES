# views/login_page.py

import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller
        self.auth_controller = AuthController()

        # Fixed colors for a constant grey-themed login page (Streamlit-like)
        # These will NOT change with ctk.set_appearance_mode()
        self.fixed_bg_color = "#f0f2f5" # Light grey background for the whole page
        self.fixed_frame_fg_color = "#ffffff" # White background for the central login card
        self.fixed_text_color = "#333333" # Dark grey for general text
        self.fixed_entry_fg_color = "#f8f8f8" # Very light grey for entry fields
        self.fixed_entry_text_color = "#333333" # Dark text inside entries
        self.fixed_entry_border_color = "#cccccc" # Light grey border for entries
        self.fixed_button_fg_color = "#4a7d96" # A consistent blue-grey for buttons
        self.fixed_button_hover_color = "#3a6c82" # Darker blue-grey on hover
        self.fixed_button_text_color = "white" # White text on buttons
        self.fixed_error_text_color = "#e74c3c" # Red for errors

        # Set the main frame's background color to a fixed light grey
        self.configure(fg_color=self.fixed_bg_color)
        
        self.create_widgets()

    def create_widgets(self):
        # Central login card frame
        login_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=self.fixed_frame_fg_color,
                                   border_width=1, border_color=self.fixed_entry_border_color) # Added border for card
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title Label
        title_label = ctk.CTkLabel(login_frame, text="Admin Login",
                                   font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
                                   text_color=self.fixed_text_color)
        title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20), padx=40)

        # Email
        email_label = ctk.CTkLabel(login_frame, text="Email:",
                                   font=ctk.CTkFont(family="Arial", size=18),
                                   text_color=self.fixed_text_color)
        email_label.grid(row=1, column=0, padx=(40, 10), pady=(10, 5), sticky="w")
        self.email_entry = ctk.CTkEntry(login_frame, width=350, height=45,
                                        font=ctk.CTkFont(family="Arial", size=16),
                                        placeholder_text="Enter your email",
                                        fg_color=self.fixed_entry_fg_color,
                                        text_color=self.fixed_entry_text_color,
                                        corner_radius=8,
                                        border_width=1,
                                        border_color=self.fixed_entry_border_color)
        self.email_entry.grid(row=2, column=0, columnspan=2, padx=40, pady=(0, 20), sticky="ew")
        self.email_entry.insert(0, "so1ICT@bup.com") # Pre-fill for quick testing

        # Password
        password_label = ctk.CTkLabel(login_frame, text="Password:",
                                      font=ctk.CTkFont(family="Arial", size=18),
                                      text_color=self.fixed_text_color)
        password_label.grid(row=3, column=0, padx=(40, 10), pady=(10, 5), sticky="w")
        self.password_entry = ctk.CTkEntry(login_frame, show="*", width=350, height=45,
                                           font=ctk.CTkFont(family="Arial", size=16),
                                           placeholder_text="Enter your password",
                                           fg_color=self.fixed_entry_fg_color,
                                           text_color=self.fixed_entry_text_color,
                                           corner_radius=8,
                                           border_width=1,
                                           border_color=self.fixed_entry_border_color)
        self.password_entry.grid(row=4, column=0, columnspan=2, padx=40, pady=(0, 30), sticky="ew")
        self.password_entry.insert(0, "1234") # Pre-fill for quick testing

        # Login Button
        login_button = ctk.CTkButton(login_frame, text="Login", command=self.handle_login,
                                     font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                                     height=55, corner_radius=10,
                                     fg_color=self.fixed_button_fg_color,
                                     hover_color=self.fixed_button_hover_color,
                                     text_color=self.fixed_button_text_color)
        login_button.grid(row=5, column=0, columnspan=2, padx=40, pady=(0, 30), sticky="ew")

        # Error Message Label
        self.error_label = ctk.CTkLabel(login_frame, text="", text_color=self.fixed_error_text_color,
                                        font=ctk.CTkFont(family="Arial", size=14))
        self.error_label.grid(row=6, column=0, columnspan=2, pady=(0, 20))

        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

    def handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self.error_label.configure(text="Email and Password cannot be empty.")
            return

        admin_user = self.auth_controller.authenticate_admin(email, password)

        if admin_user:
            self.error_label.configure(text="")
            self.parent_controller.set_current_user(admin_user)
            messagebox.showinfo("Login Success", f"Welcome, {admin_user.name}!")
            self.parent_controller.show_page("DashboardPage", admin_user)
        else:
            self.error_label.configure(text="Invalid email or password.")
            messagebox.showerror("Login Failed", "Invalid email or password. Please try again.")

