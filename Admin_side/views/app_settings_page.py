# views/app_settings_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.app_settings_controller import AppSettingsController
from models.app_settings_model import AppSettings

class AppSettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.app_settings_controller = AppSettingsController()

        self.admin_user = self.parent_controller.get_current_user()
        if not self.admin_user:
            messagebox.showerror("Error", "Admin not logged in. Cannot access settings.")
            self.destroy()
            return

        self.configure(bg="#ecf0f1")
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Application Settings", font=("Arial", 18, "bold"), background="#ecf0f1", foreground="#34495e")
        title_label.pack(pady=10)

        settings_frame = ttk.LabelFrame(self, text="Personalize Your App", padding="20")
        settings_frame.pack(pady=10, padx=20, fill="x")

        # Font Size
        ttk.Label(settings_frame, text="Font Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.font_size_combo = ttk.Combobox(settings_frame, values=["small", "medium", "large"], state="readonly")
        self.font_size_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.font_size_combo.set("medium") # Default value

        # Theme
        ttk.Label(settings_frame, text="Theme:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.theme_combo = ttk.Combobox(settings_frame, values=["light", "dark"], state="readonly")
        self.theme_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.theme_combo.set("light") # Default value

        # Auto Logout Minutes
        ttk.Label(settings_frame, text="Auto Logout (minutes):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.auto_logout_entry = ttk.Entry(settings_frame, width=10)
        self.auto_logout_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.auto_logout_entry.insert(0, "30") # Default value

        settings_frame.grid_columnconfigure(1, weight=1) # Allow entry/combo to expand

        save_button = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings)
        save_button.grid(row=3, column=0, columnspan=2, pady=20)

    def load_settings(self):
        current_settings = self.app_settings_controller.get_admin_settings(self.admin_user.admin_id)
        if current_settings:
            self.font_size_combo.set(current_settings.font_size)
            self.theme_combo.set(current_settings.theme)
            self.auto_logout_entry.delete(0, tk.END)
            self.auto_logout_entry.insert(0, str(current_settings.auto_logout_minutes))
        else:
            # If no settings found, apply DB defaults or initial UI defaults
            # (which are already set in create_widgets)
            messagebox.showinfo("Settings", "No personalized settings found. Using defaults.")


    def save_settings(self):
        font_size = self.font_size_combo.get()
        theme = self.theme_combo.get()
        auto_logout_minutes_str = self.auto_logout_entry.get().strip()

        if not font_size or not theme or not auto_logout_minutes_str:
            messagebox.showerror("Validation Error", "All fields are required.")
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
            font_size=font_size,
            theme=theme,
            auto_logout_minutes=auto_logout_minutes
        )

        success, message = self.app_settings_controller.save_admin_settings(new_settings)

        if success:
            messagebox.showinfo("Success", message)
            # In a real app, you'd apply theme/font changes here
            # self.parent_controller.apply_theme(theme)
        else:
            messagebox.showerror("Error", message)