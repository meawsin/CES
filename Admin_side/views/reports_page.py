# views/reports_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.report_controller import ReportController
from controllers.course_controller import CourseController # For filter dropdowns
from controllers.faculty_controller import FacultyController # For filter dropdowns
import json # For pretty printing JSON feedback

class ReportsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.report_controller = ReportController()
        self.course_controller = CourseController()
        self.faculty_controller = FacultyController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Allow treeview to expand

        self.current_report_data = None # Store the last generated report

        self.create_widgets()
        self.load_filter_options()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Evaluation Reports", font=("Arial", 18, "bold"), background="#ecf0f1", foreground="#34495e")
        title_label.pack(pady=10)

        # Filter Frame
        filter_frame = ttk.LabelFrame(self, text="Filter Options", padding="10")
        filter_frame.pack(pady=10, padx=10, fill="x")

        filter_frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(filter_frame, text="Course Code:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.course_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.course_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(filter_frame, text="Batch:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.batch_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.batch_combo.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ttk.Label(filter_frame, text="Faculty:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.faculty_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.faculty_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(filter_frame, text="Template ID:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.template_id_entry = ttk.Entry(filter_frame, width=30)
        self.template_id_entry.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ttk.Button(filter_frame, text="Generate Report", command=self.generate_report).grid(row=row_idx, column=0, columnspan=4, pady=10)


        # Report Display Area
        self.report_notebook = ttk.Notebook(self)
        self.report_notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Tab 1: Aggregated Results
        self.aggregated_frame = ttk.Frame(self.report_notebook, padding="10")
        self.report_notebook.add(self.aggregated_frame, text="Aggregated Results")

        self.summary_label = ttk.Label(self.aggregated_frame, text="Total Submissions: 0", font=("Arial", 12, "bold"))
        self.summary_label.pack(pady=5, anchor="w")

        self.report_tree = ttk.Treeview(self.aggregated_frame, columns=("Question", "Type", "Details"), show="headings")
        self.report_tree.heading("Question", text="Question")
        self.report_tree.heading("Type", text="Type")
        self.report_tree.heading("Details", text="Details / Comments")
        self.report_tree.column("Question", width=250)
        self.report_tree.column("Type", width=80, anchor="center")
        self.report_tree.column("Details", width=500)

        report_scrollbar_y = ttk.Scrollbar(self.aggregated_frame, orient="vertical", command=self.report_tree.yview)
        report_scrollbar_x = ttk.Scrollbar(self.aggregated_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=report_scrollbar_y.set, xscrollcommand=report_scrollbar_x.set)

        self.report_tree.pack(fill="both", expand=True)
        report_scrollbar_y.pack(side="right", fill="y")
        report_scrollbar_x.pack(side="bottom", fill="x")

        # Tab 2: Raw JSON View (for detailed inspection of a selected question)
        self.raw_json_frame = ttk.Frame(self.report_notebook, padding="10")
        self.report_notebook.add(self.raw_json_frame, text="Raw Question Data")
        self.raw_json_text = tk.Text(self.raw_json_frame, wrap="word", font=("Courier New", 10))
        self.raw_json_text.pack(fill="both", expand=True)
        raw_json_scrollbar_y = ttk.Scrollbar(self.raw_json_frame, orient="vertical", command=self.raw_json_text.yview)
        self.raw_json_text.config(yscrollcommand=raw_json_scrollbar_y.set)
        raw_json_scrollbar_y.pack(side="right", fill="y")

        self.report_tree.bind("<<TreeviewSelect>>", self.display_raw_json_for_selected)


        # Export Buttons
        export_frame = ttk.Frame(self, padding="10")
        export_frame.pack(pady=10, fill="x")
        ttk.Label(export_frame, text="Export:").pack(side="left", padx=5)
        ttk.Button(export_frame, text="Export to CSV", command=lambda: self.export_report("csv")).pack(side="left", padx=5)
        ttk.Button(export_frame, text="Export to Excel", command=lambda: self.export_report("xlsx")).pack(side="left", padx=5)
        ttk.Button(export_frame, text="Export to PDF", command=lambda: self.export_report("pdf")).pack(side="left", padx=5) # PDF support noted as partial

    def load_filter_options(self):
        # Load courses
        courses = self.course_controller.get_all_courses()
        course_codes = [c.course_code for c in courses]
        self.course_combo['values'] = [""] + course_codes # Add empty for "all" option

        # Load batches (from students table)
        batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        batches_data = self.report_controller.db.fetch_data(batches_query, fetch_all=True)
        batches = [b['batch'] for b in batches_data]
        self.batch_combo['values'] = [""] + batches # Add empty for "all" option

        # Load faculty
        faculty_members = self.faculty_controller.get_all_faculty()
        # Store dict: { "Faculty Name (ID)": faculty_id } for easy lookup
        self.faculty_options_map = {"": None}
        faculty_display_names = [""]
        for f in faculty_members:
            display_name = f"{f.name} ({f.faculty_id})"
            self.faculty_options_map[display_name] = f.faculty_id
            faculty_display_names.append(display_name)
        self.faculty_combo['values'] = faculty_display_names

    def generate_report(self):
        course_code = self.course_combo.get() if self.course_combo.get() != "" else None
        batch = self.batch_combo.get() if self.batch_combo.get() != "" else None
        faculty_display_name = self.faculty_combo.get()
        faculty_id = self.faculty_options_map.get(faculty_display_name) # Get ID from map if selected

        template_id_str = self.template_id_entry.get().strip()
        template_id = int(template_id_str) if template_id_str.isdigit() else None

        report_result = self.report_controller.get_aggregated_evaluation_report(
            course_code=course_code,
            batch=batch,
            faculty_id=faculty_id,
            template_id=template_id
        )

        self.current_report_data = report_result['report_data']

        # Clear previous report
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        self.raw_json_text.config(state="normal")
        self.raw_json_text.delete("1.0", tk.END)
        self.raw_json_text.config(state="disabled")

        self.summary_label.config(text=f"Total Submissions: {report_result['total_submissions']}")

        if report_result['total_submissions'] == 0:
            messagebox.showinfo("Report", report_result['summary'])
            return

        for question_text, q_data in self.current_report_data.items():
            details = ""
            if q_data['type'] in ['rating', 'multiple_choice']:
                # Sort options by count for better readability
                sorted_options = sorted(q_data['data'].items(), key=lambda item: item[1], reverse=True)
                details = ", ".join([f"{opt}: {count}" for opt, count in sorted_options])
            elif q_data['type'] == 'text':
                details = f"{len(q_data['data'].get('comments', []))} comments (click row for full text)"

            self.report_tree.insert("", "end", iid=question_text, values=(question_text, q_data['type'], details))

    def display_raw_json_for_selected(self, event):
        selected_item_id = self.report_tree.focus()
        if not selected_item_id:
            return

        question_text_selected = self.report_tree.item(selected_item_id)['iid']

        if self.current_report_data and question_text_selected in self.current_report_data:
            q_data = self.current_report_data[question_text_selected]

            self.raw_json_text.config(state="normal")
            self.raw_json_text.delete("1.0", tk.END)

            if q_data['type'] == 'text':
                comments_list = q_data['data'].get('comments', [])
                self.raw_json_text.insert("1.0", "\n\n".join(comments_list))
            else:
                self.raw_json_text.insert("1.0", json.dumps(q_data['data'], indent=2))

            self.raw_json_text.config(state="disabled")
            self.report_notebook.select(1) # Switch to Raw JSON View tab

    def export_report(self, file_type):
        if not self.current_report_data:
            messagebox.showwarning("Export", "Please generate a report first.")
            return

        summary_message = self.report_controller.export_report_data(self.current_report_data, file_type)
        messagebox.showinfo("Export Status", summary_message)