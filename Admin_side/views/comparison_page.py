# views/comparison_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.report_controller import ReportController # Uses report controller for faculty scores
from controllers.faculty_controller import FacultyController # To get faculty list
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ComparisonPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.report_controller = ReportController()
        self.faculty_controller = FacultyController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Allow graph area to expand

        self.create_widgets()
        self.load_faculty_options()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Faculty Evaluation Comparison", font=("Arial", 18, "bold"), background="#ecf0f1", foreground="#34495e")
        title_label.pack(pady=10)

        # Selection Frame
        selection_frame = ttk.LabelFrame(self, text="Select Faculty for Comparison", padding="10")
        selection_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(selection_frame, text="Faculty 1:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.faculty_combo_1 = ttk.Combobox(selection_frame, state="readonly", width=40)
        self.faculty_combo_1.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(selection_frame, text="Faculty 2:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.faculty_combo_2 = ttk.Combobox(selection_frame, state="readonly", width=40)
        self.faculty_combo_2.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Button(selection_frame, text="Compare", command=self.compare_faculty).grid(row=2, column=0, columnspan=2, pady=10)

        # Comparison Results / Graph Area
        self.results_frame = ttk.LabelFrame(self, text="Comparison Results", padding="10")
        self.results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        self.graph_canvas_frame = tk.Frame(self.results_frame)
        self.graph_canvas_frame.grid(row=0, column=0, sticky="nsew")

    def load_faculty_options(self):
        faculty_members = self.faculty_controller.get_all_faculty()
        self.faculty_options_map = {"": None}
        faculty_display_names = [""]
        for f in faculty_members:
            display_name = f"{f.name} ({f.faculty_id})"
            self.faculty_options_map[display_name] = f.faculty_id
            faculty_display_names.append(display_name)

        self.faculty_combo_1['values'] = faculty_display_names
        self.faculty_combo_2['values'] = faculty_display_names

    def compare_faculty(self):
        faculty1_display_name = self.faculty_combo_1.get()
        faculty2_display_name = self.faculty_combo_2.get()

        faculty1_id = self.faculty_options_map.get(faculty1_display_name)
        faculty2_id = self.faculty_options_map.get(faculty2_display_name)

        if not faculty1_id or not faculty2_id:
            messagebox.showwarning("Selection Error", "Please select two distinct faculty members for comparison.")
            return
        if faculty1_id == faculty2_id:
            messagebox.showwarning("Selection Error", "Please select two DIFFERENT faculty members for comparison.")
            return

        faculty1_scores = self.report_controller.get_faculty_evaluation_scores(faculty1_id)
        faculty2_scores = self.report_controller.get_faculty_evaluation_scores(faculty2_id)

        if not faculty1_scores and not faculty2_scores:
            messagebox.showinfo("No Data", "No evaluation data found for either selected faculty member.")
            self.clear_graph()
            return
        if not faculty1_scores:
            messagebox.showinfo("No Data", f"No evaluation data found for {faculty1_display_name}.")
            self.clear_graph()
            return
        if not faculty2_scores:
            messagebox.showinfo("No Data", f"No evaluation data found for {faculty2_display_name}.")
            self.clear_graph()
            return

        self.plot_comparison_graph(faculty1_display_name, faculty1_scores, faculty2_display_name, faculty2_scores)

    def plot_comparison_graph(self, name1, scores1, name2, scores2):
        self.clear_graph() # Clear any previous graph

        fig, ax = plt.subplots(figsize=(8, 5)) # Adjust figure size

        # Prepare data for plotting
        # Collect average scores and evaluation dates for each faculty
        dates1 = [s['evaluation_date'] for s in scores1]
        avg_ratings1 = [float(s['average_rating']) for s in scores1]

        dates2 = [s['evaluation_date'] for s in scores2]
        avg_ratings2 = [float(s['average_rating']) for s in scores2]

        # Combine dates for consistent x-axis, sort them
        all_dates = sorted(list(set(dates1 + dates2)))
        x_indices = np.arange(len(all_dates))

        # Map dates to their x_indices for plotting
        date_to_idx = {date: idx for idx, date in enumerate(all_dates)}

        # Create rating arrays aligned by common dates
        ratings1_aligned = [None] * len(all_dates)
        for score in scores1:
            ratings1_aligned[date_to_idx[score['evaluation_date']]] = float(score['average_rating'])

        ratings2_aligned = [None] * len(all_dates)
        for score in scores2:
            ratings2_aligned[date_to_idx[score['evaluation_date']]] = float(score['average_rating'])

        # Plotting
        # Convert None to NaN for plotting gaps
        y1 = np.array(ratings1_aligned, dtype=float)
        y1[y1 == None] = np.nan
        y2 = np.array(ratings2_aligned, dtype=float)
        y2[y2 == None] = np.nan

        ax.plot(x_indices, y1, marker='o', linestyle='-', label=name1, color='blue')
        ax.plot(x_indices, y2, marker='x', linestyle='--', label=name2, color='red')

        ax.set_xticks(x_indices)
        ax.set_xticklabels(all_dates, rotation=45, ha='right')
        ax.set_xlabel("Evaluation Date / Course Instance")
        ax.set_ylabel("Average Rating")
        ax.set_title(f"Comparison of Average Ratings: {name1} vs {name2}")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_ylim(0, 5) # Assuming ratings are 1-5

        plt.tight_layout()

        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas_frame)
        canvas_widget = canvas.get_tk_canvas()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()

    def clear_graph(self):
        for widget in self.graph_canvas_frame.winfo_children():
            widget.destroy()
        plt.close('all') # Close matplotlib figures to free memory