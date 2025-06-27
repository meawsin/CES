import tkinter as tk
from tkinter import ttk, messagebox
from models.evaluation_template_model import EvaluationTemplate
import json
from datetime import datetime
from views.question_form import QuestionForm

class CreateEditTemplateForm(tk.Toplevel):
    def __init__(self, parent_window, template_controller, refresh_callback, template_to_edit=None, admin_id=None):
        super().__init__(parent_window)
        self.template_controller = template_controller
        self.refresh_callback = refresh_callback
        self.template_to_edit = template_to_edit
        self.admin_id = admin_id

        self.title("Edit Evaluation Template" if self.template_to_edit else "Create New Evaluation Template")

        # Internal list to hold question dictionaries
        self.questions_list = []
        self.instructions = "Please rate the following statements on a scale of 1 to 5, where 1 = Strongly Disagree and 5 = Strongly Agree."
        if self.template_to_edit and 'instructions' in self.template_to_edit.questions_set:
            self.instructions = self.template_to_edit.questions_set['instructions']

        # Match AddAdminForm's initial geometry
        self.geometry("550x550")

        self.create_widgets()

        # Set focus to the title entry
        self.title_entry.focus_set()
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

        # Make window transient and grab focus
        self.transient(parent_window)
        self.grab_set()

        if self.template_to_edit:
            self.load_template_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(3, weight=1)

        row_idx = 0

        # Template Title
        ttk.Label(form_frame, text="Template Title:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Instructions
        ttk.Label(form_frame, text="Instructions:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.instructions_entry = ttk.Entry(form_frame, width=30)
        self.instructions_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.instructions_entry.insert(0, self.instructions)
        row_idx += 1

        # Questions List
        ttk.Label(form_frame, text="Questions:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=10, sticky="w")
        row_idx += 1

        self.questions_tree = ttk.Treeview(form_frame, columns=("Type", "Question Text"), show="headings", style="Treeview")
        self.questions_tree.heading("Type", text="Type")
        self.questions_tree.heading("Question Text", text="Question Text")
        self.questions_tree.column("Type", width=100, anchor="center")
        self.questions_tree.column("Question Text", width=350, anchor="w")
        
        questions_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=self.questions_tree.yview)
        self.questions_tree.configure(yscrollcommand=questions_scrollbar.set)
        
        self.questions_tree.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        questions_scrollbar.grid(row=row_idx, column=2, sticky="ns")
        row_idx += 1

        # Question Management Buttons
        question_button_frame = ttk.Frame(form_frame)
        question_button_frame.grid(row=row_idx, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Button(question_button_frame, text="Add Question", command=self.add_question, style="QuestionForm.TButton").pack(side="left", padx=5)
        ttk.Button(question_button_frame, text="Edit Question", command=self.edit_question, style="QuestionForm.TButton").pack(side="left", padx=5)
        ttk.Button(question_button_frame, text="Remove Question", command=self.remove_question, style="QuestionForm.TButton").pack(side="left", padx=5)
        row_idx += 1

        # Save Button
        save_button = ttk.Button(form_frame, text="Save Template", command=self.save_template, style="FormSave.TButton")
        save_button.grid(row=row_idx, column=0, columnspan=3, pady=20)

    def load_template_data(self):
        if self.template_to_edit:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.template_to_edit.title)
            
            self.instructions_entry.delete(0, tk.END)
            self.instructions_entry.insert(0, self.template_to_edit.questions_set.get('instructions', ''))

            if 'questions' in self.template_to_edit.questions_set:
                self.questions_list = self.template_to_edit.questions_set['questions']
                self._populate_questions_tree()

    def _get_display_question_type(self, type_str):
        if type_str == "rating":
            return "Rating"
        elif type_str == "multiple_choice":
            return "Multiple Choice"
        elif type_str == "text":
            return "Text"
        return type_str

    def _populate_questions_tree(self):
        for i in self.questions_tree.get_children():
            self.questions_tree.delete(i)
        
        for idx, q in enumerate(self.questions_list):
            q_text_display = (q['text'][:50] + "...") if len(q['text']) > 50 else q['text']
            display_type = self._get_display_question_type(q['type'])
            self.questions_tree.insert("", "end", iid=idx, values=(display_type, q_text_display))

    def add_question(self):
        self._open_question_form(mode="add")

    def edit_question(self):
        selected_item_id = self.questions_tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a question to edit.")
            return
        
        question_index = int(selected_item_id)
        question_data = self.questions_list[question_index]
        self._open_question_form(mode="edit", question_data=question_data, question_index=question_index)

    def remove_question(self):
        selected_items = self.questions_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select questions to remove.")
            return

        if messagebox.askyesno("Confirm Removal", "Are you sure you want to remove the selected question(s)?"):
            indices_to_remove = sorted([int(iid) for iid in selected_items], reverse=True)
            for index in indices_to_remove:
                if 0 <= index < len(self.questions_list):
                    del self.questions_list[index]
            self._populate_questions_tree()

    def _open_question_form(self, mode="add", question_data=None, question_index=None):
        self.grab_release()
        question_form = QuestionForm(
            parent_window=self,
            mode=mode,
            question_data=question_data,
            save_callback=lambda new_q_data, idx=question_index: self._save_question_from_form(new_q_data, idx),
            refresh_callback=self._populate_questions_tree
        )
        self.wait_window(question_form)
        self.grab_set()

    def _save_question_from_form(self, question_data, question_index=None):
        if question_index is not None:
            if 0 <= question_index < len(self.questions_list):
                self.questions_list[question_index] = question_data
        else:
            self.questions_list.append(question_data)
        self._populate_questions_tree()

    def save_template(self):
        title = self.title_entry.get().strip()
        instructions = self.instructions_entry.get().strip()
        
        if not title or not self.questions_list:
            messagebox.showerror("Validation Error", "Title is required and at least one question must be added.")
            return

        questions_set_dict = {
            "instructions": instructions,
            "questions": self.questions_list
        }

        batch = None
        course_code = None
        last_date = datetime.strptime("2099-12-31", "%Y-%m-%d")
        admin_id = self.admin_id if self.admin_id else (self.template_to_edit.admin_id if self.template_to_edit else None)

        if not admin_id:
            messagebox.showerror("Error", "Admin ID not found. Please log in again.")
            return

        new_template = EvaluationTemplate(
            id=self.template_to_edit.id if self.template_to_edit else None,
            title=title,
            questions_set=questions_set_dict,
            batch=batch,
            course_code=course_code,
            last_date=last_date,
            admin_id=admin_id
        )

        if self.template_to_edit:
            success = self.template_controller.update_template(new_template)
            action = "updated"
        else:
            success = self.template_controller.add_template(new_template)
            action = "created"

        if success:
            messagebox.showinfo("Success", f"Template {action} successfully!")
            self.refresh_callback()
            self.on_closing()
        else:
            messagebox.showerror("Error", f"Failed to {action} template.")

    def on_closing(self):
        self.destroy()