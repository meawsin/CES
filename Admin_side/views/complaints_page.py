# views/complaints_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.complaint_controller import ComplaintController

class ComplaintsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.complaint_controller = ComplaintController()

        self.configure(bg="#ecf0f1")
        self.columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_complaints()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Manage Student Complaints", font=("Arial", 18, "bold"), background="#ecf0f1", foreground="#34495e")
        title_label.pack(pady=10)

        # Filter and Refresh
        filter_frame = ttk.Frame(self, padding="10")
        filter_frame.pack(pady=5, fill="x")

        ttk.Label(filter_frame, text="Status:").pack(side="left", padx=5)
        self.status_filter_combo = ttk.Combobox(filter_frame, values=["", "pending", "in_progress", "resolved"], state="readonly", width=15)
        self.status_filter_combo.set("") # Default to all statuses
        self.status_filter_combo.pack(side="left", padx=5)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.load_complaints)

        ttk.Button(filter_frame, text="Refresh", command=self.load_complaints).pack(side="right", padx=5)


        # Complaints Treeview
        self.tree = ttk.Treeview(self, columns=(
            "ID", "Student Name", "Course", "Issue Type", "Status", "Date", "Details"
        ), show="headings")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Student Name", text="Student Name")
        self.tree.heading("Course", text="Course Code")
        self.tree.heading("Issue Type", text="Issue Type")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Date", text="Date Submitted")
        self.tree.heading("Details", text="Details") # This will be short summary, full in view

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Student Name", width=120)
        self.tree.column("Course", width=100)
        self.tree.column("Issue Type", width=120)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=120)
        self.tree.column("Details", width=300)


        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action Buttons
        action_frame = ttk.Frame(self, padding="10")
        action_frame.pack(pady=10, fill="x")

        ttk.Button(action_frame, text="View Details / Update", command=self.view_update_complaint).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark Pending", command=lambda: self.update_selected_complaint_status('pending')).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark In Progress", command=lambda: self.update_selected_complaint_status('in_progress')).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Mark Resolved", command=lambda: self.update_selected_complaint_status('resolved')).pack(side="left", padx=5)


    def load_complaints(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        selected_status = self.status_filter_combo.get() if self.status_filter_combo.get() != "" else None
        complaints = self.complaint_controller.get_all_complaints(status=selected_status)

        for complaint in complaints:
            # Shorten details for display in treeview
            short_details = (complaint['details'][:70] + "...") if len(complaint['details']) > 70 else complaint['details']
            self.tree.insert("", "end", iid=complaint['id'], values=(
                complaint['id'],
                complaint['student_name'] if complaint['student_name'] else "N/A",
                complaint['course_code'] if complaint['course_code'] else "N/A",
                complaint['issue_type'],
                complaint['status'],
                complaint['created_at'].strftime("%Y-%m-%d"),
                short_details
            ))

    def view_update_complaint(self):
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a complaint to view/update.")
            return

        complaint_id = self.tree.item(selected_item_id)['iid']
        complaint_data = self.complaint_controller.get_complaint_by_id(complaint_id)

        if not complaint_data:
            messagebox.showerror("Error", "Complaint not found.")
            return

        # Create a new top-level window for details/update
        details_window = tk.Toplevel(self.parent_controller)
        details_window.title(f"Complaint Details: {complaint_data['id']}")
        details_window.transient(self.parent_controller)
        details_window.grab_set()
        details_window.geometry("700x550") # Adjust size as needed

        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill="both", expand=True)

        # Display Complaint Details
        row_idx = 0
        ttk.Label(details_frame, text="Complaint ID:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=complaint_data['id']).grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Student:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=complaint_data['student_name'] if complaint_data['student_name'] else "N/A").grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Course:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=f"{complaint_data['course_name']} ({complaint_data['course_code']})" if complaint_data['course_code'] else "N/A").grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Issue Type:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=complaint_data['issue_type']).grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Submitted On:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=complaint_data['created_at'].strftime("%Y-%m-%d %H:%M:%S")).grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Last Updated:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        ttk.Label(details_frame, text=complaint_data['updated_at'].strftime("%Y-%m-%d %H:%M:%S")).grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Current Status:").grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        self.current_status_label = ttk.Label(details_frame, text=complaint_data['status'].upper(), font=("Arial", 10, "bold"), foreground="blue")
        self.current_status_label.grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        row_idx += 1

        ttk.Label(details_frame, text="Details:").grid(row=row_idx, column=0, sticky="nw", pady=5, padx=5)
        details_text = tk.Text(details_frame, wrap="word", height=5, width=60)
        details_text.grid(row=row_idx, column=1, sticky="nsew", pady=5, padx=5)
        details_text.insert("1.0", complaint_data['details'])
        details_text.config(state="disabled") # Make read-only
        row_idx += 1


        # Admin Comments Section (requires the 'admin_comments' column)
        ttk.Label(details_frame, text="Admin Comments:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(10,5), padx=5)
        row_idx += 1

        admin_comments_text = tk.Text(details_frame, wrap="word", height=5, width=60)
        admin_comments_text.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)
        # Assuming complaint_data['admin_comments'] exists
        if 'admin_comments' in complaint_data and complaint_data['admin_comments']:
            admin_comments_text.insert("1.0", complaint_data['admin_comments'])
        admin_comments_text.config(state="disabled") # Make read-only
        row_idx += 1


        ttk.Label(details_frame, text="Add New Comment:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_comment_entry = ttk.Entry(details_frame, width=50)
        self.new_comment_entry.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        ttk.Button(details_frame, text="Add Comment", command=lambda: self.add_comment_to_complaint(complaint_id, details_window, admin_comments_text)).grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        # Status Change Section
        ttk.Label(details_frame, text="Change Status To:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.new_status_combo = ttk.Combobox(details_frame, values=["pending", "in_progress", "resolved"], state="readonly", width=20)
        self.new_status_combo.set(complaint_data['status']) # Current status as default
        self.new_status_combo.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        ttk.Button(details_frame, text="Update Status", command=lambda: self.update_complaint_status_from_dialog(complaint_id, details_window)).grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        details_frame.grid_columnconfigure(1, weight=1) # Allow second column to expand

    def add_comment_to_complaint(self, complaint_id, details_window, comments_text_widget):
        comment = self.new_comment_entry.get().strip()
        if not comment:
            messagebox.showwarning("Input Error", "Please enter a comment.")
            return

        admin_id = self.parent_controller.get_current_user().admin_id if self.parent_controller.get_current_user() else None
        if not admin_id:
            messagebox.showerror("Error", "Admin user not logged in. Cannot add comment.")
            return

        success, message = self.complaint_controller.add_complaint_comment(complaint_id, admin_id, comment)
        if success:
            messagebox.showinfo("Success", message)
            self.new_comment_entry.delete(0, tk.END)
            # Reload complaint data to update comment text area
            updated_complaint = self.complaint_controller.get_complaint_by_id(complaint_id)
            comments_text_widget.config(state="normal")
            comments_text_widget.delete("1.0", tk.END)
            if 'admin_comments' in updated_complaint and updated_complaint['admin_comments']:
                comments_text_widget.insert("1.0", updated_complaint['admin_comments'])
            comments_text_widget.config(state="disabled")
            self.load_complaints() # Refresh main list
        else:
            messagebox.showerror("Error", message)

    def update_complaint_status_from_dialog(self, complaint_id, details_window):
        new_status = self.new_status_combo.get()
        if not new_status:
            messagebox.showwarning("Input Error", "Please select a new status.")
            return

        success, message = self.complaint_controller.update_complaint_status(complaint_id, new_status)
        if success:
            messagebox.showinfo("Success", message)
            self.current_status_label.config(text=new_status.upper())
            self.load_complaints() # Refresh main list
            # details_window.destroy() # Close after successful update if desired
        else:
            messagebox.showerror("Error", message)

    def update_selected_complaint_status(self, status):
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            messagebox.showwarning("No Selection", "Please select a complaint to update status.")
            return

        complaint_id = self.tree.item(selected_item_id)['iid']
        complaint_details = self.tree.item(selected_item_id)['values'][6] # Get short details for confirmation

        if messagebox.askyesno("Confirm Status Change", f"Change status of complaint '{complaint_details}' (ID: {complaint_id}) to '{status}'?"):
            success, message = self.complaint_controller.update_complaint_status(complaint_id, status)
            if success:
                messagebox.showinfo("Success", message)
                self.load_complaints()
            else:
                messagebox.showerror("Error", message)