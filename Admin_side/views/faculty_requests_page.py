# Admin_side/views/faculty_requests_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.faculty_request_controller import FacultyRequestController
from controllers.student_controller import StudentController # For fetching student names if needed
from controllers.course_controller import CourseController # For fetching course names if needed
import datetime # For timestamping admin comments

class FacultyRequestsPage(tk.Frame):
    """
    A Tkinter frame for administrators to view and manage student faculty requests.
    Allows filtering by status and updating request details/status.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.faculty_request_controller = FacultyRequestController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_faculty_requests()

    def create_widgets(self):
        """Creates and lays out the widgets for the faculty requests management page."""
        title_label = ttk.Label(self, text="Manage Faculty Requests",
                                font=("Arial", 18, "bold"),
                                background="#ecf0f1",
                                foreground="#34495e")
        title_label.pack(pady=10)

        # Filter and Refresh Frame
        filter_frame = ttk.Frame(self, padding="10")
        filter_frame.pack(pady=5, fill="x")

        ttk.Label(filter_frame, text="Filter by Status:").pack(side="left", padx=5)
        self.status_filter_combo = ttk.Combobox(filter_frame, values=["", "pending", "approved", "rejected"], state="readonly", width=15)
        self.status_filter_combo.set("pending") # Default to show pending requests
        self.status_filter_combo.pack(side="left", padx=5)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.load_faculty_requests)

        ttk.Button(filter_frame, text="🔄 Refresh", command=self.load_faculty_requests, style="General.TButton").pack(side="right", padx=5)


        # Requests Treeview (Table)
        self.tree = ttk.Treeview(self, columns=(
            "ID", "Student Name", "Course", "Requested Faculty", "Status", "Date Submitted", "Details"
        ), show="headings")

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

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action Buttons Frame
        action_frame = ttk.Frame(self, padding="10")
        action_frame.pack(pady=10, fill="x")

        ttk.Button(action_frame, text="👁️ View Details / Update", command=self.view_update_request, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="✅ Mark Approved", command=lambda: self.update_selected_request_status('approved'), style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="❌ Mark Rejected", command=lambda: self.update_selected_request_status('rejected'), style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="⏳ Mark Pending", command=lambda: self.update_selected_request_status('pending'), style="General.TButton").pack(side="left", padx=5)


    def load_faculty_requests(self, event=None):
        """Fetches requests and populates them into the Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        selected_status = self.status_filter_combo.get()
        status_filter = selected_status if selected_status != "" else None
        
        requests = self.faculty_request_controller.get_all_faculty_requests(status=status_filter)

        for req in requests:
            short_details = (req['details'][:70] + "...") if len(req['details']) > 70 else req['details']
            
            course_display = f"{req['course_code']} - {req['course_name']}" if req['course_code'] and req['course_name'] else "N/A"

            self.tree.insert("", "end", iid=req['request_id'], values=(
                req['request_id'],
                req['student_name'] if req['student_name'] else "N/A",
                course_display,
                req['requested_faculty_name'] if req['requested_faculty_name'] else "Any suitable",
                req['status'].replace('_', ' ').title(),
                req['created_at'].strftime("%Y-%m-%d %H:%M"),
                short_details
            ))

    def view_update_request(self):
        """Opens a new Toplevel window to display full details of a selected request and allow updating."""
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a faculty request to view/update.")
            return

        request_id = int(selected_item_id)
        request_data = self.faculty_request_controller.get_faculty_request_by_id(request_id)

        if not request_data:
            messagebox.showerror("Error", "Faculty request not found or could not be retrieved.")
            return

        details_window = tk.Toplevel(self.parent_controller.get_root_window())
        details_window.title(f"Faculty Request Details: {request_data['request_id']}")
        details_window.transient(self.parent_controller.get_root_window())
        details_window.grab_set()
        details_window.geometry("750x700")

        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill="both", expand=True)
        details_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        def add_detail_row(frame, label_text, value_text, row):
            ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=2, padx=5)
            ttk.Label(frame, text=value_text, font=("Arial", 10, "bold")).grid(row=row, column=1, sticky="w", pady=2, padx=5)
            return row + 1

        row_idx = add_detail_row(details_frame, "Request ID:", request_data['request_id'], row_idx)
        row_idx = add_detail_row(details_frame, "Student:", f"{request_data['student_name']} (ID: {request_data['student_id']})", row_idx)
        row_idx = add_detail_row(details_frame, "Course:", f"{request_data['course_name']} ({request_data['course_code']})", row_idx)
        row_idx = add_detail_row(details_frame, "Requested Faculty:", request_data['requested_faculty_name'] if request_data['requested_faculty_name'] else "Any suitable", row_idx)
        row_idx = add_detail_row(details_frame, "Submitted On:", request_data['created_at'].strftime("%Y-%m-%d %H:%M:%S"), row_idx)
        row_idx = add_detail_row(details_frame, "Last Updated:", request_data['updated_at'].strftime("%Y-%m-%d %H:%M:%S"), row_idx)

        ttk.Label(details_frame, text="Current Status:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        self.current_status_label_dialog = ttk.Label(details_frame, text=request_data['status'].replace('_', ' ').upper(), font=("Arial", 10, "bold"), foreground="blue")
        self.current_status_label_dialog.grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Student Details:").grid(row=row_idx, column=0, sticky="nw", pady=5, padx=5)
        details_text = tk.Text(details_frame, wrap="word", height=5, width=60, font=("Arial", 10))
        details_text.grid(row=row_idx, column=1, sticky="nsew", pady=5, padx=5)
        details_text.insert("1.0", request_data['details'])
        details_text.config(state="disabled")
        row_idx += 1

        ttk.Label(details_frame, text="Admin Comments History:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(10,5), padx=5)
        row_idx += 1

        admin_comments_text_display = tk.Text(details_frame, wrap="word", height=8, width=60, font=("Arial", 10))
        admin_comments_text_display.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)
        if 'admin_comment' in request_data and request_data['admin_comment']:
            admin_comments_text_display.insert("1.0", request_data['admin_comment'])
        else:
            admin_comments_text_display.insert("1.0", "No admin comments yet.")
        admin_comments_text_display.config(state="disabled")
        row_idx += 1

        ttk.Label(details_frame, text="Add New Admin Comment / Update Status Comment:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_admin_comment_entry = ttk.Entry(details_frame, width=50)
        self.new_admin_comment_entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1
        
        # Status Change Section
        ttk.Label(details_frame, text="Change Status To:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_status_combo_dialog = ttk.Combobox(details_frame, values=["pending", "approved", "rejected"], state="readonly", width=20)
        self.new_status_combo_dialog.set(request_data['status'])
        self.new_status_combo_dialog.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        ttk.Button(details_frame, text="✅ Update Status & Add Comment", command=lambda: self.update_request_status_from_dialog(
            request_id, admin_comments_text_display, details_window
        ), style="FormSave.TButton").grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        details_window.update_idletasks()
        parent_x = self.parent_controller.get_root_window().winfo_x()
        parent_y = self.parent_controller.get_root_window().winfo_y()
        parent_width = self.parent_controller.get_root_window().winfo_width()
        parent_height = self.parent_controller.get_root_window().winfo_height()

        self_width = details_window.winfo_width()
        self_height = details_window.winfo_height()

        x = parent_x + (parent_width // 2) - (self_width // 2)
        y = parent_y + (parent_height // 2) - (self_height // 2)
        details_window.geometry(f"{self_width}x{self_height}+{int(x)}+{int(y)}")
        details_window.lift()

        details_window.protocol("WM_DELETE_WINDOW", details_window.destroy)

    def update_request_status_from_dialog(self, request_id, comments_text_widget, details_window):
        """
        Updates the status of a request directly from the detail dialog.
        """
        new_status = self.new_status_combo_dialog.get()
        admin_comment_text = self.new_admin_comment_entry.get().strip()

        if not new_status:
            messagebox.showwarning("Input Error", "Please select a new status.")
            return

        admin_user = self.parent_controller.get_current_user()
        if not admin_user:
            messagebox.showerror("Authentication Error", "Admin not logged in. Cannot update request.")
            return
        admin_id = admin_user.admin_id

        success, message = self.faculty_request_controller.update_faculty_request_status(
            request_id, new_status, admin_id, admin_comment_text
        )
        if success:
            messagebox.showinfo("Success", message)
            self.current_status_label_dialog.config(text=new_status.replace('_', ' ').upper())
            self.new_admin_comment_entry.delete(0, tk.END) # Clear comment entry

            # Refresh the comments display in the dialog
            updated_request = self.faculty_request_controller.get_faculty_request_by_id(request_id)
            comments_text_widget.config(state="normal")
            comments_text_widget.delete("1.0", tk.END)
            if 'admin_comment' in updated_request and updated_request['admin_comment']:
                comments_text_widget.insert("1.0", updated_request['admin_comment'])
            else:
                 comments_text_widget.insert("1.0", "No admin comments yet.")
            comments_text_widget.config(state="disabled")

            self.load_faculty_requests() # Refresh the main list in the background
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

