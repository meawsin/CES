# Admin_side/views/app_settings_page.py

import customtkinter as ctk # Changed from tkinter as tk and tkinter.ttk
from tkinter import messagebox # messagebox is still from standard tkinter
from controllers.app_settings_controller import AppSettingsController
from models.app_settings_model import AppSettings

class AppSettingsPage(ctk.CTkFrame): # Changed from tk.Frame
    """
    A CustomTkinter frame for managing application settings, including auto-logout duration and theme.
    """
    def __init__(self, parent, controller):
        super().__init__(parent) # Changed from tk.Frame.__init__
        self.parent_controller = controller # Reference to the main application controller
        self.app_settings_controller = AppSettingsController()

        # Ensure an admin user is logged in to access settings
        self.admin_user = self.parent_controller.get_current_user()
        if not self.admin_user:
            messagebox.showerror("Error", "Admin not logged in. Cannot access settings.")
            self.destroy() # Close the page if no admin is logged in
            return

        # CustomTkinter frames handle their own background based on theme
        # self.configure(bg="#ECF0F1") # Removed

        self.create_widgets() # Build the UI elements
        self.load_settings() # Load existing settings into the UI

    def create_widgets(self):
        """
        Creates and lays out the widgets for the application settings page.
        """
        title_label = ctk.CTkLabel(self, text="Application Settings",
                                   font=ctk.CTkFont(family="Arial", size=18, weight="bold")) # Changed from ttk.Label
        title_label.pack(pady=10)

        # Frame to group settings inputs
        settings_frame = ctk.CTkFrame(self, corner_radius=10) # Changed from ttk.LabelFrame
        settings_frame.pack(pady=10, padx=20, fill="x")

        # Auto Logout Minutes Input
        ctk.CTkLabel(settings_frame, text="Auto Logout (minutes):", font=ctk.CTkFont(family="Arial", size=20)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.auto_logout_entry = ctk.CTkEntry(settings_frame, width=100) # Changed from ttk.Entry
        self.auto_logout_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.auto_logout_entry.insert(0, "30") # Default value shown in the entry field

        settings_frame.grid_columnconfigure(1, weight=1) # Allow the entry field to expand

        # Save Settings Button
        save_button = ctk.CTkButton(
            settings_frame,
            text="Save Settings",
            command=self.save_settings,
            font=ctk.CTkFont(family="Arial", size=20)
        )  # Changed from ttk.Button
        save_button.grid(row=1, column=0, columnspan=2, pady=20)

    def load_settings(self):
        current_settings = self.app_settings_controller.get_admin_settings(self.admin_user.admin_id)
        if current_settings:
            # If settings exist, populate the entry with the saved value
            self.auto_logout_entry.delete(0, ctk.END) # Changed from tk.END
            self.auto_logout_entry.insert(0, str(current_settings.auto_logout_minutes))
        else:
            # If no personalized settings exist, inform the user (defaults are already in place in widgets)
            messagebox.showinfo("Settings", "No personalized settings found. Using defaults.")

    def save_settings(self):
        """
        Validates the input for auto-logout minutes and saves it to the database.
        Notifies the main application controller to update the auto-logout interval.
        """
        auto_logout_minutes_str = self.auto_logout_entry.get().strip()
        if not auto_logout_minutes_str:
            messagebox.showerror("Validation Error", "Auto logout minutes is required.")
            return
        try:
            auto_logout_minutes = int(auto_logout_minutes_str)
            if auto_logout_minutes <= 0:
                raise ValueError("Minutes must be a positive number.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid auto logout minutes: {e}")
            return
        new_settings = AppSettings(
            admin_id=self.admin_user.admin_id,
            auto_logout_minutes=auto_logout_minutes
        )
        success, message = self.app_settings_controller.save_admin_settings(new_settings)
        if success:
            messagebox.showinfo("Success", message)
            self.parent_controller.update_auto_logout_interval()
        else:
            messagebox.showerror("Error", message)

