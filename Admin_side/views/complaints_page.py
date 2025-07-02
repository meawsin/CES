# views/complaints_page.py
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controllers.complaint_controller import ComplaintController

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
DARK_GREY = "#34495e"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"
RED = "#e74c3c"

class ComplaintsPage(ctk.CTkFrame):
    """
    A Tkinter frame for administrators to view and manage student complaints.
    Allows filtering by status and updating complaint details/status.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller # Reference to the main application controller
        self.complaint_controller = ComplaintController() # Controller for complaint-related operations
        self.configure(fg_color=GREY)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_complaints()

    def create_widgets(self):
        """
        Creates and lays out the widgets for the complaints management page.
        """
        title_label = ctk.CTkLabel(self, text="Manage Student Complaints", font=("Arial", 40, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=(18, 8))
        # Top action/filter bar
        top_bar = ctk.CTkFrame(self, fg_color=LIGHT_BLUE, corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(top_bar, text="Filter by Status:", font=("Arial", 15, "bold"), text_color=DARK_BLUE).pack(side="left", padx=(10, 5), pady=10)
        self.status_filter_combo = ctk.CTkComboBox(top_bar, values=["", "pending", "in_progress", "resolved"], width=120, font=("Arial", 15))
        self.status_filter_combo.set("")
        self.status_filter_combo.pack(side="left", padx=5, pady=10)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.load_complaints)
        ctk.CTkButton(top_bar, text="Refresh", command=self.load_complaints, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15, "bold"), width=90).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(top_bar, text="Mark Pending", command=lambda: self.update_selected_complaint_status('pending'), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 15, "bold"), width=120).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Mark In Progress", command=lambda: self.update_selected_complaint_status('in_progress'), fg_color="#f39c12", hover_color="#e67e22", text_color=WHITE, font=("Arial", 15, "bold"), width=120).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Mark Resolved", command=lambda: self.update_selected_complaint_status('resolved'), fg_color="#27ae60", hover_color="#229954", text_color=WHITE, font=("Arial", 15, "bold"), width=120).pack(side="right", padx=5, pady=10)
        # Table area
        table_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 0))
        self.tree = ttk.Treeview(table_frame, columns=(
            "ID", "Student Name", "Course", "Issue Type", "Status", "Date", "Details"
        ), show="headings", height=12)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Student Name", text="Student Name")
        self.tree.heading("Course", text="Course Code")
        self.tree.heading("Issue Type", text="Issue Type")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date", text="Date Submitted")
        self.tree.heading("Details", text="Details")
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Student Name", width=120)
        self.tree.column("Course", width=100)
        self.tree.column("Issue Type", width=120)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=120)
        self.tree.column("Details", width=300)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.show_selected_complaint_details)
        # Details panel below table
        self.details_panel = ctk.CTkFrame(self, fg_color=GREY, corner_radius=10)
        self.details_panel.pack(fill="x", padx=20, pady=(10, 20))

    def load_complaints(self, event=None):
        """
        Fetches complaints from the database based on the selected filter status
        and populates them into the Treeview.
        """
        for i in self.tree.get_children():
            self.tree.delete(i) # Clear existing entries

        selected_status = self.status_filter_combo.get() # Get selected status from combobox
        # If "" (empty string) is selected, pass None to get all statuses
        status_filter = selected_status if selected_status != "" else None
        
        # Fetch complaints using the controller
        complaints = self.complaint_controller.get_all_complaints(status=status_filter)

        for complaint in complaints:
            # Shorten details for display in treeview (full details in detail dialog)
            short_details = (complaint['details'][:70] + "...") if len(complaint['details']) > 70 else complaint['details']
            
            # Insert data into the treeview
            self.tree.insert("", "end", iid=complaint['id'], values=(
                complaint['id'],
                complaint['student_name'] if complaint['student_name'] else "N/A",
                complaint['course_code'] if complaint['course_code'] else "N/A",
                complaint['issue_type'],
                complaint['status'].replace('_', ' ').title(), # Format status for display
                complaint['created_at'].strftime("%Y-%m-%d %H:%M"), # Format date
                short_details
            ))
        self.clear_details_panel()

    def show_selected_complaint_details(self, event=None):
        self.clear_details_panel()
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            return
        complaint_id = int(selected_item_id)
        complaint_data = self.complaint_controller.get_complaint_by_id(complaint_id)
        if not complaint_data:
            return
        ctk.CTkLabel(self.details_panel, text="Details Summary:", font=("Arial", 15, "bold"), text_color=DARK_BLUE).pack(anchor="w", pady=(5, 0), padx=5)
        details_text = ctk.CTkTextbox(self.details_panel, wrap="word", height=3, width=60, font=("Arial", 12), fg_color=WHITE, text_color=DARK_GREY)
        details_text.pack(fill="x", padx=10, pady=(0, 10))
        details_text.insert("1.0", complaint_data.get('details', 'No details available.'))
        details_text.configure(state="disabled")

    def clear_details_panel(self):
        for widget in self.details_panel.winfo_children():
            widget.destroy()

    def update_selected_complaint_status(self, status):
        """
        Updates the status of the selected complaint in the main treeview directly.
        (Called by the quick action buttons: Mark Pending, Mark In Progress, Mark Resolved)
        :param status: The new status to set ('pending', 'in_progress', 'resolved').
        """
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a complaint to update status.")
            return

        complaint_id = int(selected_item_id)
        # Get complaint details for confirmation message (optional, but good UX)
        complaint_details_summary = self.tree.item(selected_item_id)['values'][6]

        if messagebox.askyesno("Confirm Status Change", f"Change status of complaint '{complaint_details_summary}' (ID: {complaint_id}) to '{status.replace('_', ' ').title()}'?"):
            success, message = self.complaint_controller.update_complaint_status(complaint_id, status)
            if success:
                messagebox.showinfo("Success", message)
                self.load_complaints() # Reload complaints to reflect the change
            else:
                messagebox.showerror("Error", message)

