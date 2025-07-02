# Admin_side/views/faculty_requests_page.py
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controllers.faculty_request_controller import FacultyRequestController
from controllers.student_controller import StudentController # For fetching student names if needed
from controllers.course_controller import CourseController # For fetching course names if needed
import datetime # For timestamping admin comments

BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
DARK_GREY = "#34495e"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"
RED = "#e74c3c"

class FacultyRequestsPage(ctk.CTkFrame):
    """
    A CustomTkinter frame for administrators to view and manage student faculty requests.
    Allows filtering by status and updating request details/status.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent_controller = controller
        self.faculty_request_controller = FacultyRequestController()
        self.configure(fg_color=GREY)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_faculty_requests()

    def create_widgets(self):
        """Creates and lays out the widgets for the faculty requests management page."""
        title_label = ctk.CTkLabel(self, text="Manage Faculty Requests", font=("Arial", 40, "bold"), text_color=DARK_BLUE)
        title_label.pack(pady=(18, 8))
        # Tabs for Pending/Previous Requests
        self.tabview = ctk.CTkSegmentedButton(self, values=["Pending Requests", "Previous Requests"], command=self.on_tab_change)
        self.tabview.pack(fill="x", padx=20, pady=(0, 10))
        # Top action/filter bar
        top_bar = ctk.CTkFrame(self, fg_color=LIGHT_BLUE, corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(top_bar, text="Filter by Status:", font=("Arial", 13, "bold"), text_color=DARK_BLUE).pack(side="left", padx=(10, 5), pady=10)
        self.status_filter_combo = ctk.CTkComboBox(top_bar, values=["", "pending", "approved", "rejected"], width=120, font=("Arial", 13))
        self.status_filter_combo.set("pending")
        self.status_filter_combo.pack(side="left", padx=5, pady=10)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.load_faculty_requests)
        ctk.CTkButton(top_bar, text="Refresh", command=self.load_faculty_requests, fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 13, "bold"), width=90).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(top_bar, text="Mark Approved", command=lambda: self.update_selected_request_status('approved'), fg_color="#27ae60", hover_color="#229954", text_color=WHITE, font=("Arial", 13, "bold"), width=120).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Mark Rejected", command=lambda: self.update_selected_request_status('rejected'), fg_color=RED, hover_color="#c0392b", text_color=WHITE, font=("Arial", 13, "bold"), width=120).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(top_bar, text="Mark Pending", command=lambda: self.update_selected_request_status('pending'), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, font=("Arial", 13, "bold"), width=120).pack(side="right", padx=5, pady=10)
        # Table area
        table_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12, border_color=CARD_BORDER, border_width=1)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 0))
        self.tree = ttk.Treeview(table_frame, columns=(
            "ID", "Student Name", "Course", "Requested Faculty", "Status", "Date Submitted", "Details"
        ), show="headings", height=12)
        self.tree.heading("ID", text="Request ID")
        self.tree.heading("Student Name", text="Student Name")
        self.tree.heading("Course", text="Course (Code - Name)")
        self.tree.heading("Requested Faculty", text="Requested Faculty")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date Submitted", text="Date Submitted")
        self.tree.heading("Details", text="Details Summary")
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Student Name", width=120)
        self.tree.column("Course", width=150)
        self.tree.column("Requested Faculty", width=150)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date Submitted", width=120)
        self.tree.column("Details", width=300)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=32, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), background=LIGHT_BLUE, foreground=DARK_BLUE)
        style.map("Treeview", background=[('selected', DARK_BLUE)])
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.show_selected_request_details)
        # Details panel below table
        self.details_panel = ctk.CTkFrame(self, fg_color=GREY, corner_radius=10)
        self.details_panel.pack(fill="x", padx=20, pady=(10, 20))

    def on_tab_change(self, value):
        if value == "Pending Requests":
            self.status_filter_combo.set("pending")
        else:
            self.status_filter_combo.set("")
        self.load_faculty_requests()

    def load_faculty_requests(self, event=None):
        """Fetches requests and populates them into the Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        selected_status = self.status_filter_combo.get()
        if self.tabview.get() == "Previous Requests":
            status_filter = None
        else:
            status_filter = selected_status if selected_status != "" else None
        
        requests = self.faculty_request_controller.get_all_faculty_requests(status=status_filter)

        for req in requests:
            # For previous requests tab, only show approved/rejected
            if self.tabview.get() == "Previous Requests" and req['status'] not in ["approved", "rejected"]:
                continue
            if self.tabview.get() == "Pending Requests" and req['status'] != "pending":
                continue
            short_details = (req['details'][:70] + "...") if len(req['details']) > 70 else req['details']
            
            # Safely get course_code and course_name, fallback to 'N/A' if missing
            course_code = req.get('course_code', 'N/A')
            course_name = req.get('course_name', 'N/A')
            course_display = f"{course_code} - {course_name}" if course_code != 'N/A' and course_name != 'N/A' else "N/A"

            self.tree.insert("", "end", iid=req['request_id'], values=(
                req['request_id'],
                req['student_name'] if req['student_name'] else "N/A",
                course_display,
                req['requested_faculty_name'] if req['requested_faculty_name'] else "Any suitable",
                req['status'].replace('_', ' ').title(),
                req['created_at'].strftime("%Y-%m-%d %H:%M"),
                short_details
            ))
        self.clear_details_panel()

    def show_selected_request_details(self, event=None):
        self.clear_details_panel()
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            return
        request_id = int(selected_item_id)
        request_data = self.faculty_request_controller.get_faculty_request_by_id(request_id)
        if not request_data:
            return
        # Only show the details summary
        ctk.CTkLabel(self.details_panel, text="Details Summary:", font=("Arial", 13, "bold"), text_color=DARK_BLUE).pack(anchor="w", pady=(5, 0), padx=5)
        details_text = ctk.CTkTextbox(self.details_panel, wrap="word", height=3, width=60, font=("Arial", 12), fg_color=WHITE, text_color=DARK_GREY)
        details_text.pack(fill="x", padx=10, pady=(0, 10))
        details_text.insert("1.0", request_data.get('details', 'No details available.'))
        details_text.configure(state="disabled")

    def clear_details_panel(self):
        for widget in self.details_panel.winfo_children():
            widget.destroy()

    def update_request_status_from_panel(self, request_id, comments_text_widget):
        new_status = self.new_status_combo_dialog.get()
        new_comment = self.new_admin_comment_entry.get().strip()
        if not new_status:
            messagebox.showerror("Validation Error", "Please select a new status.")
            return
        success, message = self.faculty_request_controller.update_request_status_and_comment(request_id, new_status, new_comment)
        if success:
            messagebox.showinfo("Success", message)
            self.current_status_label_dialog.configure(text=new_status.replace('_', ' ').upper())
            self.new_admin_comment_entry.delete(0, ctk.CTk.END)
            updated_request = self.faculty_request_controller.get_faculty_request_by_id(request_id)
            comments_text_widget.configure(state="normal")
            comments_text_widget.delete("1.0", ctk.CTk.END)
            if 'admin_comment' in updated_request and updated_request['admin_comment']:
                comments_text_widget.insert("1.0", updated_request['admin_comment'])
            else:
                comments_text_widget.insert("1.0", "No admin comments yet.")
            comments_text_widget.configure(state="disabled")
            self.load_faculty_requests()
        else:
            messagebox.showerror("Error", message)

    def update_selected_request_status(self, status):
        """
        Updates the status of the selected request in the main treeview directly.
        """
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a request to update status.")
            return

        request_id = int(selected_item_id)
        current_status = self.tree.item(selected_item_id)['values'][4] # Get current status from treeview

        if current_status.lower() == status:
            messagebox.showinfo("No Change", f"Request is already '{status.replace('_', ' ').title()}' status.")
            return

        # Get course and requested faculty name for confirmation message
        course_display = self.tree.item(selected_item_id)['values'][2]
        requested_faculty = self.tree.item(selected_item_id)['values'][3]

        confirmation_message = (f"Change status of request for '{requested_faculty}' for course '{course_display}' "
                                f"(ID: {request_id}) from '{current_status}' to '{status.replace('_', ' ').title()}'?")

        if messagebox.askyesno("Confirm Status Change", confirmation_message):
            admin_user = self.parent_controller.get_current_user()
            if not admin_user:
                messagebox.showerror("Authentication Error", "Admin not logged in. Cannot update request.")
                return
            admin_id = admin_user.admin_id
            
            # Add a basic comment for the quick status change
            quick_comment = f"Status changed to '{status}' via quick action."

            success, message = self.faculty_request_controller.update_faculty_request_status(
                request_id, status, admin_id, quick_comment
            )
            if success:
                messagebox.showinfo("Success", message)
                self.load_faculty_requests()
            else:
                messagebox.showerror("Error", message)

