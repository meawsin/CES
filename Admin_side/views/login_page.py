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
        # Enhanced central login card frame with shadow effect
        login_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=self.fixed_frame_fg_color,
                                   border_width=2, border_color="#e0e0e0")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Enhanced Title Label with icon
        title_label = ctk.CTkLabel(login_frame, text="🔐 Admin Login",
                                   font=ctk.CTkFont(family="Arial", size=40, weight="bold"),
                                   text_color="#1565c0")
        title_label.grid(row=0, column=0, columnspan=2, pady=(40, 30), padx=50)

        # Subtitle
        subtitle_label = ctk.CTkLabel(login_frame, text="Course Evaluation System",
                                     font=ctk.CTkFont(family="Arial", size=16),
                                     text_color="#666666")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30), padx=50)

        # Email with enhanced styling
        email_label = ctk.CTkLabel(login_frame, text="Email:",
                                   font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                                   text_color="#2c3e50")
        email_label.grid(row=2, column=0, padx=(50, 10), pady=(15, 8), sticky="w")
        self.email_entry = ctk.CTkEntry(login_frame, width=380, height=50,
                                        font=ctk.CTkFont(family="Arial", size=16),
                                        placeholder_text="Enter your email address",
                                        fg_color="#f8f9fa",
                                        text_color="#2c3e50",
                                        corner_radius=12,
                                        border_width=2,
                                        border_color="#dee2e6")
        self.email_entry.grid(row=3, column=0, columnspan=2, padx=50, pady=(0, 25), sticky="ew")
        self.email_entry.insert(0, "so1ICT@bup.com") # Pre-fill for quick testing

        # Password with enhanced styling
        password_label = ctk.CTkLabel(login_frame, text="Password:",
                                      font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                                      text_color="#2c3e50")
        password_label.grid(row=4, column=0, padx=(50, 10), pady=(15, 8), sticky="w")
        self.password_entry = ctk.CTkEntry(login_frame, show="*", width=380, height=50,
                                           font=ctk.CTkFont(family="Arial", size=16),
                                           placeholder_text="Enter your password",
                                           fg_color="#f8f9fa",
                                           text_color="#2c3e50",
                                           corner_radius=12,
                                           border_width=2,
                                           border_color="#dee2e6")
        self.password_entry.grid(row=5, column=0, columnspan=2, padx=50, pady=(0, 35), sticky="ew")
        self.password_entry.insert(0, "1234") # Pre-fill for quick testing

        # Enhanced Login Button
        login_button = ctk.CTkButton(login_frame, text="Login", command=self.handle_login,
                                     font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                                     height=60, corner_radius=15,
                                     fg_color="#3498db",
                                     hover_color="#2980b9",
                                     text_color="white")
        login_button.grid(row=6, column=0, columnspan=2, padx=50, pady=(0, 25), sticky="ew")

        # Enhanced Error Message Label
        self.error_label = ctk.CTkLabel(login_frame, text="", text_color="#e74c3c",
                                        font=ctk.CTkFont(family="Arial", size=14, weight="bold"))
        self.error_label.grid(row=7, column=0, columnspan=2, pady=(0, 30))

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

