# views/complaints_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.complaint_controller import ComplaintController

class ComplaintsPage(tk.Frame):
    """
    A Tkinter frame for administrators to view and manage student complaints.
    Allows filtering by status and updating complaint details/status.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller # Reference to the main application controller
        self.complaint_controller = ComplaintController() # Controller for complaint-related operations

        self.configure(bg="#ecf0f1") # Set background color
        self.columnconfigure(0, weight=1) # Allow the main column to expand

        self.create_widgets() # Build the UI elements
        self.load_complaints() # Load initial complaints data into the treeview

    def create_widgets(self):
        """
        Creates and lays out the widgets for the complaints management page.
        """
        title_label = ttk.Label(self, text="Manage Student Complaints",
                                font=("Arial", 18, "bold"),
                                background="#ecf0f1",
                                foreground="#34495e")
        title_label.pack(pady=10)

        # Filter and Refresh Frame
        filter_frame = ttk.Frame(self, padding="10")
        filter_frame.pack(pady=5, fill="x") # Pack with padding and expand horizontally

        # Status Filter Combobox
        ttk.Label(filter_frame, text="Filter by Status:").pack(side="left", padx=5)
        self.status_filter_combo = ttk.Combobox(filter_frame, values=["", "pending", "in_progress", "resolved"], state="readonly", width=15)
        self.status_filter_combo.set("") # Default to show all statuses
        self.status_filter_combo.pack(side="left", padx=5)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.load_complaints) # Reload complaints on selection

        # Refresh Button
        ttk.Button(filter_frame, text="Refresh", command=self.load_complaints, style="General.TButton").pack(side="right", padx=5)


        # Complaints Treeview (Table)
        self.tree = ttk.Treeview(self, columns=(
            "ID", "Student Name", "Course", "Issue Type", "Status", "Date", "Details"
        ), show="headings") # Display column headings

        # Define column headings and widths
        self.tree.heading("ID", text="ID")
        self.tree.heading("Student Name", text="Student Name")
        self.tree.heading("Course", text="Course Code")
        self.tree.heading("Issue Type", text="Issue Type")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date", text="Date Submitted")
        self.tree.heading("Details", text="Details") # This will show a short summary

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Student Name", width=120)
        self.tree.column("Course", width=100)
        self.tree.column("Issue Type", width=120)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=120)
        self.tree.column("Details", width=300) # Give more space for details summary


        # Add a scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True) # Pack treeview, allow expansion
        scrollbar.pack(side="right", fill="y") # Pack scrollbar next to treeview

        # Action Buttons Frame
        action_frame = ttk.Frame(self, padding="10")
        action_frame.pack(pady=10, fill="x") # Pack with padding and expand horizontally

        # Buttons for managing selected complaints
        ttk.Button(action_frame, text="View Details / Update", command=self.view_update_complaint, style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark Pending", command=lambda: self.update_selected_complaint_status('pending'), style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark In Progress", command=lambda: self.update_selected_complaint_status('in_progress'), style="General.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark Resolved", command=lambda: self.update_selected_complaint_status('resolved'), style="General.TButton").pack(side="left", padx=5)


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

    def view_update_complaint(self):
        """
        Opens a new Toplevel window to display full details of a selected complaint
        and allow updating its status or adding admin comments.
        """
        selected_item_id = self.tree.focus() # Get the ID of the selected item (complaint ID)
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a complaint to view/update.")
            return

        complaint_id = int(selected_item_id) # Convert iid to int (assuming IDs are int)
        complaint_data = self.complaint_controller.get_complaint_by_id(complaint_id)

        if not complaint_data:
            messagebox.showerror("Error", "Complaint not found or could not be retrieved.")
            return

        # Create a new top-level window for details/update
        details_window = tk.Toplevel(self.parent_controller.get_root_window())
        details_window.title(f"Complaint Details: {complaint_data['id']}")
        details_window.transient(self.parent_controller.get_root_window()) # Make transient to root
        details_window.grab_set() # Grab focus
        details_window.geometry("700x650") # Adjust size as needed for details and comments

        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill="both", expand=True)
        details_frame.grid_columnconfigure(1, weight=1) # Allow second column to expand

        # Display Complaint Details
        row_idx = 0
        
        # Helper to display a label and its value
        def add_detail_row(frame, label_text, value_text, row):
            ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=2, padx=5)
            ttk.Label(frame, text=value_text, font=("Arial", 10, "bold")).grid(row=row, column=1, sticky="w", pady=2, padx=5)
            return row + 1

        row_idx = add_detail_row(details_frame, "Complaint ID:", complaint_data['id'], row_idx)
        row_idx = add_detail_row(details_frame, "Student:", complaint_data['student_name'] if complaint_data['student_name'] else "N/A", row_idx)
        row_idx = add_detail_row(details_frame, "Course:", f"{complaint_data['course_name']} ({complaint_data['course_code']})" if complaint_data['course_code'] else "N/A", row_idx)
        row_idx = add_detail_row(details_frame, "Issue Type:", complaint_data['issue_type'], row_idx)
        row_idx = add_detail_row(details_frame, "Submitted On:", complaint_data['created_at'].strftime("%Y-%m-%d %H:%M:%S"), row_idx)
        row_idx = add_detail_row(details_frame, "Last Updated:", complaint_data['updated_at'].strftime("%Y-%m-%d %H:%M:%S"), row_idx)

        ttk.Label(details_frame, text="Current Status:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        self.current_status_label = ttk.Label(details_frame, text=complaint_data['status'].replace('_', ' ').upper(), font=("Arial", 10, "bold"), foreground="blue")
        self.current_status_label.grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        # Complaint Details (original submission)
        ttk.Label(details_frame, text="Complaint Details:").grid(row=row_idx, column=0, sticky="nw", pady=5, padx=5)
        details_text = tk.Text(details_frame, wrap="word", height=5, width=60, font=("Arial", 10))
        details_text.grid(row=row_idx, column=1, sticky="nsew", pady=5, padx=5)
        details_text.insert("1.0", complaint_data['details'])
        details_text.config(state="disabled") # Make read-only
        row_idx += 1

        # Admin Comments Section (NEW or extended)
        ttk.Label(details_frame, text="Admin Comments History:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(10,5), padx=5)
        row_idx += 1

        admin_comments_text_display = tk.Text(details_frame, wrap="word", height=8, width=60, font=("Arial", 10))
        admin_comments_text_display.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)
        if 'admin_comments' in complaint_data and complaint_data['admin_comments']:
            admin_comments_text_display.insert("1.0", complaint_data['admin_comments'])
        else:
            admin_comments_text_display.insert("1.0", "No admin comments yet.")
        admin_comments_text_display.config(state="disabled") # Make read-only
        row_idx += 1

        # Add New Comment Input
        ttk.Label(details_frame, text="Add New Comment:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_comment_entry = ttk.Entry(details_frame, width=50)
        self.new_comment_entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        ttk.Button(details_frame, text="Add Comment", command=lambda: self.add_comment_to_complaint(
            complaint_id, admin_comments_text_display
        ), style="General.TButton").grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        # Status Change Section
        ttk.Label(details_frame, text="Change Status To:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_status_combo = ttk.Combobox(details_frame, values=["pending", "in_progress", "resolved"], state="readonly", width=20)
        self.new_status_combo.set(complaint_data['status']) # Set current status as default selection
        self.new_status_combo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        ttk.Button(details_frame, text="Update Status", command=lambda: self.update_complaint_status_from_dialog(
            complaint_id, details_window
        ), style="FormSave.TButton").grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        # Center the new window
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
        details_window.lift() # Bring to front

        details_window.protocol("WM_DELETE_WINDOW", details_window.destroy) # Handle X button

    def add_comment_to_complaint(self, complaint_id, comments_text_widget):
        """
        Adds a new comment from an admin to a specific complaint.
        The comment is appended to the `admin_comments` field in the database.
        :param complaint_id: The ID of the complaint to add a comment to.
        :param comments_text_widget: The Tkinter Text widget displaying comments history.
        """
        comment = self.new_comment_entry.get().strip()
        if not comment:
            messagebox.showwarning("Input Error", "Please enter a comment before adding.")
            return

        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot add comment.")
            return

        # Call controller to add comment. Controller appends to `admin_comments` field.
        success, message = self.complaint_controller.add_complaint_comment(complaint_id, admin_id, comment)
        if success:
            messagebox.showinfo("Success", message)
            self.new_comment_entry.delete(0, tk.END) # Clear the input field

            # Refresh the comments display in the dialog
            updated_complaint = self.complaint_controller.get_complaint_by_id(complaint_id)
            comments_text_widget.config(state="normal")
            comments_text_widget.delete("1.0", tk.END)
            if 'admin_comments' in updated_complaint and updated_complaint['admin_comments']:
                comments_text_widget.insert("1.0", updated_complaint['admin_comments'])
            else:
                 comments_text_widget.insert("1.0", "No admin comments yet.")
            comments_text_widget.config(state="disabled")

            self.load_complaints() # Refresh the main complaints list in the background
        else:
            messagebox.showerror("Error", message)

    def update_complaint_status_from_dialog(self, complaint_id, details_window):
        """
        Updates the status of a complaint directly from the detail dialog.
        :param complaint_id: The ID of the complaint to update.
        :param details_window: The Toplevel window of the detail dialog (to close if needed).
        """
        new_status = self.new_status_combo.get()
        if not new_status:
            messagebox.showwarning("Input Error", "Please select a new status.")
            return

        success, message = self.complaint_controller.update_complaint_status(complaint_id, new_status)
        if success:
            messagebox.showinfo("Success", message)
            self.current_status_label.config(text=new_status.replace('_', ' ').upper()) # Update status label in dialog
            self.load_complaints() # Refresh the main complaints list
            # details_window.destroy() # Uncomment if you want to close dialog after status update
        else:
            messagebox.showerror("Error", message)

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

