import tkinter as tk
from tkinter import ttk, messagebox
import json

class QuestionForm(tk.Toplevel):
    def __init__(self, parent_window, mode, question_data=None, save_callback=None, refresh_callback=None):
        super().__init__(parent_window)
        self.mode = mode
        self.question_data = question_data if question_data else {}
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback

        self.title(f"{'Add' if self.mode == 'add' else 'Edit'} Question")

        # --- Standard Toplevel setup to match AddAdminForm ---
        self.transient(parent_window)
        self.grab_set()

        # Match AddAdminForm's exact initial size
        self.geometry("550x550")

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
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        form_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        # Question Text
        ttk.Label(form_frame, text="Question Text:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.question_text_entry = ttk.Entry(form_frame, width=30)
        self.question_text_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Question Type
        ttk.Label(form_frame, text="Question Type:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.question_type_combo = ttk.Combobox(form_frame, values=["rating", "multiple_choice", "text"], state="readonly", width=27)
        self.question_type_combo.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.question_type_combo.bind("<<ComboboxSelected>>", self.toggle_options_visibility)
        self.question_type_combo.set(self.question_data.get('type', 'text'))
        row_idx += 1

        # Options Section
        ttk.Label(form_frame, text="Options:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=10, sticky="w")
        row_idx += 1
        self.options_frame = ttk.LabelFrame(form_frame, text="Comma-separated values", padding="10")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_text = tk.Text(self.options_frame, wrap="word", height=5, width=30)
        self.options_text.pack(fill="both", expand=True)

        # Apply FormSave.TButton style from main.py
        save_button = ttk.Button(form_frame, text="Save Question", command=self.save_question, style="FormSave.TButton")
        save_button.grid(row=row_idx+1, column=0, columnspan=2, pady=20)

        self.toggle_options_visibility()

    def toggle_options_visibility(self, event=None):
        selected_type = self.question_type_combo.get()
        if selected_type in ["rating", "multiple_choice"]:
            self.options_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        else:
            self.options_frame.grid_forget()

    def load_question_data(self):
        self.question_text_entry.delete(0, tk.END)
        self.question_text_entry.insert(0, self.question_data.get('text', ''))

        if 'options' in self.question_data and self.question_data['options'] is not None:
            self.options_text.delete("1.0", tk.END)
            if isinstance(self.question_data['options'], list):
                self.options_text.insert("1.0", ", ".join(map(str, self.question_data['options'])))
            else:
                self.options_text.insert("1.0", str(self.question_data['options']))

        self.toggle_options_visibility()

    def save_question(self):
        q_text = self.question_text_entry.get().strip()
        q_type = self.question_type_combo.get()
        options_str = self.options_text.get("1.0", tk.END).strip()

        if not q_text:
            messagebox.showerror("Validation Error", "Question Text is required.")
            return
        if not q_type:
            messagebox.showerror("Validation Error", "Question Type is required.")
            return

        new_question = {
            "text": q_text,
            "type": q_type
        }

        if q_type in ["rating", "multiple_choice"]:
            if not options_str:
                messagebox.showerror("Validation Error", f"Options are required for '{q_type}' type questions.")
                return
            parsed_options = [opt.strip() for opt in options_str.split(',') if opt.strip()]
            if not parsed_options:
                messagebox.showerror("Validation Error", "Options could not be parsed. Please provide comma-separated values.")
                return
            new_question['options'] = parsed_options

        if self.save_callback:
            self.save_callback(new_question)
        messagebox.showinfo("Success", f"Question {'added' if self.mode == 'add' else 'updated'} successfully!")
        if self.refresh_callback:
            self.refresh_callback()
        self.on_closing()

    def on_closing(self):
        self.destroy()