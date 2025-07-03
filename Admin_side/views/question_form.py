import customtkinter as ctk
from tkinter import messagebox
import json

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class QuestionForm(ctk.CTkToplevel):
    def __init__(self, parent_window, mode, question_data=None, save_callback=None, refresh_callback=None):
        super().__init__(parent_window)
        self.mode = mode
        self.question_data = question_data if question_data else {}
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback

        self.title(f"{'Add' if self.mode == 'add' else 'Edit'} Question")

        # Standard Toplevel setup to match AddAdminForm
        self.transient(parent_window)
        self.grab_set()

        # Match AddAdminForm's exact initial size
        self.geometry("550x550")
        self.configure(fg_color=GREY)

        self.create_widgets()
        if self.mode == "edit":
            self.load_question_data()

        # Set focus to the question text entry
        self.question_text_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Update idletasks to finalize window size before centering
        self.update_idletasks()

        # Center the Toplevel over its parent
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()

        self_width = self.winfo_width()
        self_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (self_width // 2)
        y = parent_y + (parent_height // 2) - (self_height // 2)

        self.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")

    def create_widgets(self):
        # Main card frame
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        card.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Title
        title_text = f"{'Add' if self.mode == 'add' else 'Edit'} Question"
        ctk.CTkLabel(card, text=title_text, font=("Arial", 28, "bold"), text_color=DARK_BLUE).pack(pady=(18, 10))
        
        # Form frame
        form_frame = ctk.CTkFrame(card, fg_color=WHITE)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        form_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        # Question Text
        ctk.CTkLabel(form_frame, text="Question Text:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.question_text_entry = ctk.CTkEntry(form_frame, width=260, font=("Arial", 17))
        self.question_text_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Question Type
        ctk.CTkLabel(form_frame, text="Question Type:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.question_type_combo = ctk.CTkOptionMenu(form_frame, values=["rating", "multiple_choice", "text"], 
                                                    font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                                    button_color=BLUE, button_hover_color=DARK_BLUE)
        self.question_type_combo.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.question_type_combo.set(self.question_data.get('type', 'text'))
        self.question_type_combo.configure(command=self.toggle_options_visibility)
        row_idx += 1

        # Options Section
        ctk.CTkLabel(form_frame, text="Options:", font=("Arial", 17, "bold"), text_color=BLUE).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=10, sticky="w")
        row_idx += 1
        
        self.options_frame = ctk.CTkFrame(form_frame, fg_color=LIGHT_BLUE, corner_radius=8)
        self.options_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.options_frame, text="Comma-separated values", font=("Arial", 14), text_color=DARK_BLUE).pack(pady=(10, 5))
        self.options_text = ctk.CTkTextbox(self.options_frame, height=100, font=("Arial", 14))
        self.options_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Save Button
        ctk.CTkButton(form_frame, text="Save Question", command=self.save_question, 
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, 
                     font=("Arial", 19, "bold"), height=45, corner_radius=10).grid(row=row_idx+1, column=0, columnspan=2, pady=20)

        self.toggle_options_visibility()

    def toggle_options_visibility(self, event=None):
        selected_type = self.question_type_combo.get()
        if selected_type in ["rating", "multiple_choice"]:
            self.options_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        else:
            self.options_frame.grid_forget()

    def load_question_data(self):
        self.question_text_entry.delete(0, "end")
        self.question_text_entry.insert(0, self.question_data.get('text', ''))

        if 'options' in self.question_data and self.question_data['options'] is not None:
            self.options_text.delete("0.0", "end")
            if isinstance(self.question_data['options'], list):
                self.options_text.insert("0.0", ", ".join(map(str, self.question_data['options'])))
            else:
                self.options_text.insert("0.0", str(self.question_data['options']))

        self.toggle_options_visibility()

    def save_question(self):
        q_text = self.question_text_entry.get().strip()
        q_type = self.question_type_combo.get()
        options_str = self.options_text.get("0.0", "end").strip()

        if not q_text:
            ctk.CTkMessagebox.show_error("Validation Error", "Question Text is required.")
            return
        if not q_type:
            ctk.CTkMessagebox.show_error("Validation Error", "Question Type is required.")
            return

        new_question = {
            "text": q_text,
            "type": q_type
        }

        if q_type in ["rating", "multiple_choice"]:
            if not options_str:
                ctk.CTkMessagebox.show_error("Validation Error", f"Options are required for '{q_type}' type questions.")
                return
            parsed_options = [opt.strip() for opt in options_str.split(',') if opt.strip()]
            if not parsed_options:
                ctk.CTkMessagebox.show_error("Validation Error", "Options could not be parsed. Please provide comma-separated values.")
                return
            new_question['options'] = parsed_options

        if self.save_callback:
            self.save_callback(new_question)
        ctk.CTkMessagebox.show_info("Success", f"Question {'added' if self.mode == 'add' else 'updated'} successfully!")
        if self.refresh_callback:
            self.refresh_callback()
        self.on_closing()

    def on_closing(self):
        self.destroy()