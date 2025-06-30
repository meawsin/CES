# Admin_side/views/app_settings_page.py

import customtkinter as ctk
from controllers.app_settings_controller import AppSettingsController
from models.app_settings_model import AppSettings

class AppSettingsPage(ctk.CTkFrame):
    """
    A customtkinter frame for managing application settings, specifically auto-logout duration.
    """
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent_controller = controller # Reference to the main application controller
        self.app_settings_controller = AppSettingsController()

        # Ensure an admin user is logged in to access settings
        self.admin_user = self.parent_controller.get_current_user()
        if not self.admin_user:
            ctk.CTkMessagebox.show_error("Error", "Admin not logged in. Cannot access settings.")
            self.destroy() # Close the page if no admin is logged in
            return

        self.create_widgets() # Build the UI elements
        self.load_settings() # Load existing settings into the UI

    def create_widgets(self):
        """
        Creates and lays out the widgets for the application settings page.
        """
        title_label = ctk.CTkLabel(self, text="Application Settings", font=("Arial", 22, "bold"))
        title_label.pack(pady=18)

        # Frame to group settings inputs
        settings_frame = ctk.CTkFrame(self, corner_radius=12)
        settings_frame.pack(pady=10, padx=24, fill="x") # Pack with padding and expand horizontally

        # Auto Logout Minutes Input
        ctk.CTkLabel(settings_frame, text="Auto Logout (minutes):", font=("Arial", 16)).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.auto_logout_entry = ctk.CTkEntry(settings_frame, width=80, font=("Arial", 16))
        self.auto_logout_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.auto_logout_entry.insert(0, "30") # Default value shown in the entry field
        settings_frame.grid_columnconfigure(1, weight=1) # Allow the entry field to expand

        # Theme Selection
        ctk.CTkLabel(settings_frame, text="Application Theme:", font=("Arial", 16)).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        
        # Theme radio buttons frame
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        
        self.theme_var = ctk.StringVar(value="light")  # Default to light theme
        
        ctk.CTkRadioButton(theme_frame, text="Light Mode", variable=self.theme_var, value="light", command=self.on_theme_change).pack(side="left", padx=(0, 18))
        
        ctk.CTkRadioButton(theme_frame, text="Dark Mode", variable=self.theme_var, value="dark", command=self.on_theme_change).pack(side="left")

        # Save Settings Button
        save_button = ctk.CTkButton(settings_frame, text="Save Settings", command=self.save_settings, font=("Arial", 16, "bold"), height=40)
        save_button.grid(row=2, column=0, columnspan=2, pady=24, sticky="ew")

    def load_settings(self):
        """
        Loads the current auto-logout settings for the logged-in admin
        and populates the input field.
        """
        current_settings = self.app_settings_controller.get_admin_settings(self.admin_user.admin_id)
        if current_settings:
            # If settings exist, populate the entry with the saved value
            self.auto_logout_entry.delete(0, ctk.CTk.END)
            self.auto_logout_entry.insert(0, str(current_settings.auto_logout_minutes))
        else:
            # If no personalized settings exist, inform the user (defaults are already in place in widgets)
            ctk.CTkMessagebox.show_info("Settings", "No personalized settings found. Using defaults.")


    def save_settings(self):
        """
        Validates the input for auto-logout minutes and saves it to the database.
        Notifies the main application controller to update the auto-logout interval.
        """
        auto_logout_minutes_str = self.auto_logout_entry.get().strip()

        # Input validation
        if not auto_logout_minutes_str:
            ctk.CTkMessagebox.show_error("Validation Error", "Auto logout minutes is required.")
            return

        try:
            auto_logout_minutes = int(auto_logout_minutes_str)
            if auto_logout_minutes <= 0:
                raise ValueError("Minutes must be a positive number.")
        except ValueError as e:
            ctk.CTkMessagebox.show_error("Input Error", f"Invalid auto logout minutes: {e}")
            return

        # Create an AppSettings object with the new value
        new_settings = AppSettings(
            admin_id=self.admin_user.admin_id,
            auto_logout_minutes=auto_logout_minutes
        )

        # Save settings via the controller
        success, message = self.app_settings_controller.save_admin_settings(new_settings)

        if success:
            ctk.CTkMessagebox.show_info("Success", message)
            # Notify the main application controller to update its internal auto-logout interval
            self.parent_controller.update_auto_logout_interval()
        else:
            ctk.CTkMessagebox.show_error("Error", message)

    def on_theme_change(self):
        """Handle theme change"""
        theme = self.theme_var.get()
        # Apply theme to the main application
        if hasattr(self.parent_controller, 'apply_theme'):
            self.parent_controller.apply_theme(theme)
        else:
            # Fallback: just show a message
            ctk.CTkMessagebox.show_info("Theme Changed", f"Application theme changed to {theme} mode.")

