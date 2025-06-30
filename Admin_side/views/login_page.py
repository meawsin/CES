# views/login_page.py

import customtkinter as ctk
from controllers.auth_controller import AuthController
from tkinter import messagebox

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent_controller = controller # This is the main application controller
        self.auth_controller = AuthController() # Instantiate the auth controller
        self.create_widgets()

    def create_widgets(self):
        # Centered card-like login box
        login_card = ctk.CTkFrame(self, corner_radius=18, width=420, height=420)
        login_card.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(login_card, text="Admin Login", font=("Arial", 32, "bold"))
        title_label.pack(pady=(32, 16))

        self.email_entry = ctk.CTkEntry(login_card, width=320, font=("Arial", 20), placeholder_text="Email")
        self.email_entry.pack(pady=(12, 8))
        self.email_entry.insert(0, "so1ICT@bup.com")

        self.password_entry = ctk.CTkEntry(login_card, show="*", width=320, font=("Arial", 20), placeholder_text="Password")
        self.password_entry.pack(pady=(8, 16))
        self.password_entry.insert(0, "1234")

        login_button = ctk.CTkButton(login_card, text="Login", command=self.handle_login, font=("Arial", 22, "bold"), height=48, width=200)
        login_button.pack(pady=(8, 12))

        self.error_label = ctk.CTkLabel(login_card, text="", text_color="red", font=("Arial", 15))
        self.error_label.pack(pady=(4, 0))

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
            self.error_label.configure(text="") # Clear any previous error
            self.parent_controller.set_current_user(admin_user)
            messagebox.showinfo("Login Success", f"Welcome, {admin_user.name}!")
            self.parent_controller.show_page("DashboardPage", admin_user)
        else:
            self.error_label.configure(text="Invalid email or password.")
            messagebox.showerror("Login Failed", "Invalid email or password. Please try again.")

