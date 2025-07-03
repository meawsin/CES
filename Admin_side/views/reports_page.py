# views/reports_page.py

import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.report_controller import ReportController
from controllers.course_controller import CourseController # For filter dropdowns
from controllers.faculty_controller import FacultyController # For filter dropdowns
import json # For pretty printing JSON feedback
from PIL import Image, ImageTk
import os

# Color constants matching the dashboard theme
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"

class ReportsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller
        self.report_controller = ReportController()
        self.course_controller = CourseController()
        self.faculty_controller = FacultyController()

        self.configure(fg_color=GREY)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Allow treeview to expand

        self.current_report_data = None # Store the last generated report
        self.graph_images = {}  # To keep references to PhotoImage objects

        self.create_widgets()
        self.load_filter_options()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="Evaluation Reports", font=("Arial", 28, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=10)

        # Filter Frame
        filter_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=16, border_color=CARD_BORDER, border_width=2)
        filter_frame.pack(pady=10, padx=10, fill="x")

        filter_frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ctk.CTkLabel(filter_frame, text="Course Code:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.course_combo = ctk.CTkOptionMenu(filter_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                             button_color=BLUE, button_hover_color=DARK_BLUE)
        self.course_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Batch:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.batch_combo = ctk.CTkOptionMenu(filter_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                            button_color=BLUE, button_hover_color=DARK_BLUE)
        self.batch_combo.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(filter_frame, text="Faculty:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.faculty_combo = ctk.CTkOptionMenu(filter_frame, font=("Arial", 17), fg_color=WHITE, text_color=DARK_BLUE,
                                              button_color=BLUE, button_hover_color=DARK_BLUE)
        self.faculty_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Template ID:", font=("Arial", 17), text_color=DARK_BLUE).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        self.template_id_entry = ctk.CTkEntry(filter_frame, width=260, font=("Arial", 17))
        self.template_id_entry.grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        row_idx += 1

        ctk.CTkButton(filter_frame, text="Generate Report 📈", command=self.generate_report,
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 19, "bold"), height=45, corner_radius=10).grid(row=row_idx, column=0, columnspan=4, pady=10)

        # Report Display Area
        self.report_notebook = ctk.CTkTabview(self)
        self.report_notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Tab 1: Aggregated Results
        self.aggregated_frame = self.report_notebook.add("Aggregated Results")

        self.summary_label = ctk.CTkLabel(self.aggregated_frame, text="Total Submissions: 0", font=("Arial", 17, "bold"), text_color=BLUE)
        self.summary_label.pack(pady=5, anchor="w")

        # Report list frame with treeview
        report_list_frame = ctk.CTkFrame(self.aggregated_frame, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        report_list_frame.pack(fill="both", expand=True)
        
        self.report_tree = ttk.Treeview(report_list_frame, columns=("Question", "Type", "Details"), show="headings", height=12)
        self.report_tree.heading("Question", text="Question")
        self.report_tree.heading("Type", text="Type")
        self.report_tree.heading("Details", text="Details/Comments")
        self.report_tree.column("Question", width=250)
        self.report_tree.column("Type", width=80, anchor="center")
        self.report_tree.column("Details", width=500)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        
        report_scrollbar_y = ctk.CTkScrollbar(report_list_frame, orientation="vertical", command=self.report_tree.yview)
        report_scrollbar_x = ctk.CTkScrollbar(report_list_frame, orientation="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=report_scrollbar_y.set, xscrollcommand=report_scrollbar_x.set)
        self.report_tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        report_scrollbar_y.pack(side="right", fill="y", pady=10)
        report_scrollbar_x.pack(side="bottom", fill="x", pady=(0, 10))

        # Tab 2: Raw JSON View (for detailed inspection of a selected question)
        self.raw_json_frame = self.report_notebook.add("Raw Question Data")
        self.raw_json_text = ctk.CTkTextbox(self.raw_json_frame, font=("Courier New", 12))
        self.raw_json_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 3: Graphs
        self.graphs_frame = self.report_notebook.add("Graphs")
        self.graph_canvas_frame = ctk.CTkFrame(self.graphs_frame, fg_color=GREY)
        self.graph_canvas_frame.pack(fill="both", expand=True)

        # Bind treeview selection to display raw JSON
        self.report_tree.bind("<<TreeviewSelect>>", self.display_raw_json_for_selected)

        # Export Buttons
        export_frame = ctk.CTkFrame(self, fg_color=WHITE)
        export_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(export_frame, text="Export:", font=("Arial", 17), text_color=DARK_BLUE).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Export to CSV", command=lambda: self.export_report("csv"),
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Export to Excel", command=lambda: self.export_report("xlsx"),
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Export to PDF", command=lambda: self.export_report("pdf"),
                     fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE,
                     font=("Arial", 16), height=35, corner_radius=8).pack(side="left", padx=5) # PDF support noted as partial

    def load_filter_options(self):
        # Load courses
        courses = self.course_controller.get_all_courses()
        course_codes = [c.course_code for c in courses]
        self.course_combo.configure(values=[""] + course_codes) # Add empty for "all" option
        self.course_combo.set("")

        # Load batches (from students table)
        batches_query = "SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL ORDER BY batch;"
        batches_data = self.report_controller.db.fetch_data(batches_query, fetch_all=True)
        batches = [b['batch'] for b in batches_data]
        self.batch_combo.configure(values=[""] + batches) # Add empty for "all" option
        self.batch_combo.set("")

        # Load faculty
        faculty_members = self.faculty_controller.get_all_faculty()
        # Store dict: { "Faculty Name (ID)": faculty_id } for easy lookup
        self.faculty_options_map = {"": None}
        faculty_display_names = [""]
        for f in faculty_members:
            display_name = f"{f.name} ({f.faculty_id})"
            self.faculty_options_map[display_name] = f.faculty_id
            faculty_display_names.append(display_name)
        self.faculty_combo.configure(values=faculty_display_names)
        self.faculty_combo.set("")

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
        self.raw_json_text.delete("0.0", "end")

        self.summary_label.configure(text=f"Total Submissions: {report_result['total_submissions']}")

        if report_result['total_submissions'] == 0:
            ctk.CTkMessagebox.show_info("Report", report_result['summary'])
            return

        # Clear previous graphs
        for widget in self.graph_canvas_frame.winfo_children():
            widget.destroy()
        self.graph_images.clear()
        
        # Generate and display graphs
        graph_paths = self.report_controller.generate_question_graphs(self.current_report_data)
        for idx, (question_text, img_path) in enumerate(graph_paths.items()):
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img = img.resize((400, 300), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(img)
                except Exception:
                    photo = ImageTk.PhotoImage(file=img_path)
                self.graph_images[question_text] = photo
                label = ctk.CTkLabel(self.graph_canvas_frame, text=question_text, font=("Arial", 17, "bold"), text_color=DARK_BLUE)
                label.pack(pady=(20 if idx > 0 else 10, 5))
                img_label = ctk.CTkLabel(self.graph_canvas_frame, image=photo, text="")
                img_label.pack(pady=5)

        # Display report data in treeview
        for question_text, q_data in self.current_report_data.items():
            details = ""
            if q_data['type'] in ['rating', 'multiple_choice']:
                # Sort options by count for better readability
                sorted_options = sorted(q_data['data'].items(), key=lambda item: item[1], reverse=True)
                details = ", ".join([f"{opt}: {count}" for opt, count in sorted_options])
                # Show average for rating questions
                if q_data['type'] == 'rating' and 'average' in q_data:
                    details += f" | Average: {q_data['average']}"
            elif q_data['type'] == 'text':
                details = f"{len(q_data['data'].get('comments', []))} comments (click row for full text)"
            
            # Truncate question text if too long
            display_question = question_text[:47] + "..." if len(question_text) > 50 else question_text
            self.report_tree.insert("", "end", iid=question_text, values=(display_question, q_data['type'], details))

    def display_raw_json_for_selected(self, event):
        """Display raw JSON data for the selected question."""
        selected_item_id = self.report_tree.focus()
        if not selected_item_id:
            return

        question_text_selected = self.report_tree.item(selected_item_id)['iid']

        if self.current_report_data and question_text_selected in self.current_report_data:
            q_data = self.current_report_data[question_text_selected]

            self.raw_json_text.delete("0.0", "end")

            if q_data['type'] == 'text':
                comments_list = q_data['data'].get('comments', [])
                self.raw_json_text.insert("0.0", "\n\n".join(comments_list))
            else:
                self.raw_json_text.insert("0.0", json.dumps(q_data['data'], indent=2))

            self.report_notebook.set("Raw Question Data") # Switch to Raw JSON View tab

    def export_report(self, file_type):
        """Export the current report data to the specified file type."""
        if not self.current_report_data:
            ctk.CTkMessagebox.show_warning("No Data", "Please generate a report first.")
            return

        try:
            success = self.report_controller.export_report(self.current_report_data, file_type)
            if success:
                ctk.CTkMessagebox.show_info("Success", f"Report exported successfully to {file_type.upper()} format.")
            else:
                ctk.CTkMessagebox.show_error("Error", f"Failed to export report to {file_type.upper()} format.")
        except Exception as e:
            ctk.CTkMessagebox.show_error("Error", f"Export failed: {str(e)}")

