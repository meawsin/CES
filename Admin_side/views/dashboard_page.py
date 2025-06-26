# views/dashboard_page.py (Updated for Dashboard Enhancements)
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from controllers.evaluation_template_controller import EvaluationTemplateController # NEW
from controllers.student_controller import StudentController                 # NEW
from controllers.admin_calendar_event_controller import AdminCalendarEventController # NEW
from views.hr_students_page import HRStudentsPage
from views.hr_faculty_page import HRFacultyPage
from views.hr_admins_page import HRAdminsPage
from views.course_setup_page import CourseSetupPage
from views.evaluation_templates_page import EvaluationTemplatesPage
from views.reports_page import ReportsPage
from views.complaints_page import ComplaintsPage
from views.comparison_page import ComparisonPage
from views.app_settings_page import AppSettingsPage
from datetime import datetime, date, timedelta # NEW for clock and calendar
import calendar # NEW for calendar logic

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller, admin_user=None):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller
        self.auth_controller = AuthController()
        self.evaluation_template_controller = EvaluationTemplateController() # NEW
        self.student_controller = StudentController()                 # NEW
        self.admin_calendar_event_controller = AdminCalendarEventController() # NEW
        self.admin_user = admin_user

        self.configure(bg="#ecf0f1")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

        self.sub_pages = {}
        self._initialize_sub_pages()

        # Initialize current calendar view to today's month/year
        self.current_calendar_year = datetime.now().year
        self.current_calendar_month = datetime.now().month

        self.show_home_content()

        self.update_user_info(admin_user)

        # Start the real-time clock and dashboard data update
        self.update_dashboard_data()
        self.update_clock()


    def create_sidebar(self):
        self.sidebar_frame = tk.Frame(self, bg="#34495e", width=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.user_info_label = ttk.Label(self.sidebar_frame, text="",
                                         font=("Arial", 14, "bold"), foreground="white", background="#34495e",
                                         anchor="center")
        self.user_info_label.pack(pady=20, fill="x")

        nav_buttons_config = [
            ("Home", self.show_home_content),
            ("HR Management", self.show_hr_management_wrapper),
            ("Course Setup", self.show_course_setup),
            ("Evaluation", self.show_evaluation_templates),
            ("Reports", self.show_reports),
            ("Complaints", self.show_complaints),
            ("Comparison", self.show_comparison),
            ("Application settings", self.show_app_settings),
        ]

        self.nav_buttons = []
        for text, command in nav_buttons_config:
            btn = ttk.Button(self.sidebar_frame, text=text, command=command, style="Sidebar.TButton")
            btn.pack(fill="x", pady=5, padx=10)
            self.nav_buttons.append(btn)

        logout_button = ttk.Button(self.sidebar_frame, text="Logout", command=self.handle_logout, style="Sidebar.Logout.TButton")
        logout_button.pack(fill="x", pady=20, padx=10, side="bottom")

        self.style = ttk.Style()
        self.style.configure("Sidebar.TButton", font=("Arial", 12), background="#34495e", foreground="black", relief="flat", borderwidth=0)
        self.style.map("Sidebar.TButton", background=[('active', '#2c3e50')])
        self.style.configure("Sidebar.Logout.TButton", font=("Arial", 12, "bold"), background="#e74c3c", foreground="black", relief="flat", borderwidth=0)
        self.style.map("Sidebar.Logout.TButton", background=[('active', '#c0392b')])


    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg="#ecf0f1")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _initialize_sub_pages(self):
        # We will dynamically create the HomeContent frame when it's needed
        # self.sub_pages["HomeContent"] = self._create_home_content() # This will be created later

        self.hr_notebook = ttk.Notebook(self.content_frame)
        self.sub_pages["HRManagementWrapper"] = self.hr_notebook

        self.hr_students_tab = HRStudentsPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_faculty_tab = HRFacultyPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_admins_tab = HRAdminsPage(parent=self.hr_notebook, controller=self.parent_controller)

        self.hr_notebook.add(self.hr_students_tab, text="Students")
        self.hr_notebook.add(self.hr_faculty_tab, text="Faculty")
        self.hr_notebook.add(self.hr_admins_tab, text="Admins")

        self.sub_pages["CourseSetupPage"] = CourseSetupPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["EvaluationTemplatesPage"] = EvaluationTemplatesPage(parent=self.content_frame, controller=self.parent_controller)

        self.sub_pages["ReportsPage"] = ReportsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ComplaintsPage"] = ComplaintsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ComparisonPage"] = ComparisonPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["AppSettingsPage"] = AppSettingsPage(parent=self.content_frame, controller=self.parent_controller)


    def show_sub_page(self, page_widget):
        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

        if page_widget:
            page_widget.grid(row=0, column=0, sticky="nsew")
            page_widget.tkraise()
        else:
            messagebox.showerror("Error", "Selected content not available or not properly initialized.")

    def update_user_info(self, admin_user):
        self.admin_user = admin_user
        if self.admin_user:
            self.user_info_label.config(text=f"Welcome,\n{self.admin_user.name}")
            self._update_navigation_permissions()
            self.update_dashboard_data() # Update data when user info changes

    def _update_navigation_permissions(self):
        if not self.admin_user:
            return

        for btn in self.nav_buttons:
            text = btn.cget("text")
            if text == "HR Management":
                btn.config(state="normal" if self.admin_user.can_manage_users else "disabled")
            elif text == "Course Setup":
                btn.config(state="normal" if self.admin_user.can_manage_courses else "disabled")
            elif text == "Evaluation":
                btn.config(state="normal" if self.admin_user.can_create_templates else "disabled")
            elif text == "Reports":
                btn.config(state="normal" if self.admin_user.can_view_reports else "disabled")
            elif text == "Complaints":
                btn.config(state="normal" if self.admin_user.can_manage_complaints else "disabled")
            elif text in ["Comparison", "Application settings", "Home"]:
                btn.config(state="normal")

        self.hr_notebook.tab(0, state='normal' if self.admin_user.can_manage_users else 'disabled') # Students tab
        self.hr_notebook.tab(1, state='normal' if self.admin_user.can_manage_users else 'disabled') # Faculty tab
        self.hr_notebook.tab(2, state='normal' if self.admin_user.can_manage_users else 'disabled') # Admins tab


    # --- Navigation Command Methods ---
    def show_home_content(self):
        # Create HomeContent dynamically if it doesn't exist
        if "HomeContent" not in self.sub_pages:
            self.sub_pages["HomeContent"] = self._create_home_content()
        self.show_sub_page(self.sub_pages["HomeContent"])
        self.update_dashboard_data() # Refresh data when home is shown

    def _create_home_content(self):
        home_frame = ttk.Frame(self.content_frame, padding="20", style="HomeFrame.TFrame")
        home_frame.grid_rowconfigure(0, weight=0) # Title
        home_frame.grid_rowconfigure(1, weight=0) # Info cards
        home_frame.grid_rowconfigure(2, weight=1) # Calendar
        home_frame.grid_columnconfigure(0, weight=1)
        home_frame.grid_columnconfigure(1, weight=1)
        home_frame.grid_columnconfigure(2, weight=1)


        # Title and Real-time Clock
        title_frame = ttk.Frame(home_frame, style="HomeFrame.TFrame")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        title_frame.columnconfigure(0, weight=1) # for clock label

        home_label = ttk.Label(title_frame, text="Admin Dashboard",
                               font=("Arial", 20, "bold"), foreground="#34495e", background="#ecf0f1")
        home_label.pack(side="left", pady=10, padx=10)

        self.clock_label = ttk.Label(title_frame, text="", font=("Arial", 14), background="#ecf0f1", foreground="#34495e")
        self.clock_label.pack(side="right", pady=10, padx=10)


        # Information Cards
        self.info_cards_frame = ttk.Frame(home_frame, style="HomeFrame.TFrame")
        self.info_cards_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        self.info_cards_frame.columnconfigure(0, weight=1)
        self.info_cards_frame.columnconfigure(1, weight=1)
        self.info_cards_frame.columnconfigure(2, weight=1) # For potential third card

        # Running Evaluations Card
        self.running_evals_card = self._create_info_card(self.info_cards_frame, "Running Evaluations", "0")
        self.running_evals_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Total Batches Card
        self.total_batches_card = self._create_info_card(self.info_cards_frame, "Total Batches", "0")
        self.total_batches_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Calendar Section
        calendar_frame = ttk.LabelFrame(home_frame, text="Calendar & Events", padding="15", style="Calendar.TLabelframe")
        calendar_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")
        calendar_frame.grid_rowconfigure(1, weight=1) # Calendar grid area
        calendar_frame.grid_columnconfigure(0, weight=1) # Calendar grid area

        # Calendar Header (Month/Year Navigation)
        calendar_nav_frame = ttk.Frame(calendar_frame)
        calendar_nav_frame.pack(pady=5, fill="x")
        calendar_nav_frame.columnconfigure(0, weight=1) # center month label

        ttk.Button(calendar_nav_frame, text="< Prev", command=self.prev_month).pack(side="left", padx=5)
        self.month_year_label = ttk.Label(calendar_nav_frame, text="", font=("Arial", 14, "bold"), background="#ecf0f1", foreground="#34495e")
        self.month_year_label.pack(side="left", expand=True, fill="x", anchor="center")
        ttk.Button(calendar_nav_frame, text="Next >", command=self.next_month).pack(side="right", padx=5)

        # Calendar Grid
        self.calendar_grid_frame = ttk.Frame(calendar_frame, borderwidth=1, relief="solid")
        self.calendar_grid_frame.pack(pady=10, fill="both", expand=True)

        self.event_details_frame = ttk.LabelFrame(calendar_frame, text="Selected Day Events", padding="10")
        self.event_details_frame.pack(pady=10, fill="x")
        self.event_details_text = tk.Text(self.event_details_frame, wrap="word", height=5, state="disabled", font=("Arial", 10))
        self.event_details_text.pack(fill="both", expand=True)
        # Add a scrollbar to event_details_text
        event_details_scrollbar = ttk.Scrollbar(self.event_details_frame, orient="vertical", command=self.event_details_text.yview)
        self.event_details_text.config(yscrollcommand=event_details_scrollbar.set)
        event_details_scrollbar.pack(side="right", fill="y")


        self.draw_calendar() # Initial calendar draw

        return home_frame

    def _create_info_card(self, parent, title, value):
        card_frame = ttk.LabelFrame(parent, text=title, padding="15", style="Card.TLabelframe")
        card_frame.columnconfigure(0, weight=1) # Center content

        value_label = ttk.Label(card_frame, text=value, font=("Arial", 28, "bold"), foreground="#2980b9", background="#ecf0f1")
        value_label.grid(row=0, column=0, pady=10)

        # Store the value label to update it later
        card_frame.value_label = value_label
        return card_frame

    def update_dashboard_data(self):
        """Fetches and updates dynamic data on the dashboard."""
        if not self.admin_user:
            # Cannot fetch user-specific data without admin_user
            self.after(5000, self.update_dashboard_data) # Try again later
            return

        # Update Running Evaluations
        running_evals_count = self.evaluation_template_controller.get_running_evaluations_count(self.admin_user.admin_id)
        self.running_evals_card.value_label.config(text=str(running_evals_count))

        # Update Total Batches
        total_batches_count = self.student_controller.get_total_batches_count()
        self.total_batches_card.value_label.config(text=str(total_batches_count))

        # Update calendar to show current month's events
        self.draw_calendar()

        # Schedule next update
        self.after(60000, self.update_dashboard_data) # Update every 1 minute


    def update_clock(self):
        """Updates the real-time clock displayed on the dashboard."""
        current_time = datetime.now().strftime("%I:%M:%S %p") # e.g., 01:23:45 PM
        current_date = datetime.now().strftime("%A, %B %d, %Y") # e.g., Wednesday, June 26, 2025
        self.clock_label.config(text=f"{current_date}\n{current_time}")
        self.after(1000, self.update_clock) # Update every 1 second


    # --- Calendar Methods ---
    def draw_calendar(self):
        # Clear existing calendar grid
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(self.current_calendar_year, self.current_calendar_month)
        self.month_year_label.config(text=datetime(self.current_calendar_year, self.current_calendar_month, 1).strftime("%B %Y"))

        # Day Headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            ttk.Label(self.calendar_grid_frame, text=day_name, font=("Arial", 10, "bold"),
                      background="#bdc3c7", foreground="#2c3e50", anchor="center").grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            self.calendar_grid_frame.grid_columnconfigure(i, weight=1) # Make columns expand evenly

        # Get all relevant events for the current month and the next month (for span)
        # This includes evaluation template deadlines and admin calendar events
        all_month_events = self._get_events_for_calendar_view()
        # Transform events into a dictionary for quick lookup by date
        events_by_date = {}
        for event in all_month_events:
            event_day = event.event_date.day
            if event_day not in events_by_date:
                events_by_date[event_day] = []
            events_by_date[event_day].append(event)


        # Days in Month
        row_offset = 1 # Start after day headers
        for week in month_days:
            for col_idx, day_num in enumerate(week):
                day_frame = ttk.Frame(self.calendar_grid_frame, relief="raised", borderwidth=1, style="CalendarDay.TFrame")
                day_frame.grid(row=row_offset, column=col_idx, sticky="nsew", padx=1, pady=1)
                day_frame.grid_rowconfigure(0, weight=1)
                day_frame.grid_rowconfigure(1, weight=1)
                day_frame.grid_columnconfigure(0, weight=1)

                if day_num != 0: # If it's a valid day in the month
                    day_label = ttk.Label(day_frame, text=str(day_num), font=("Arial", 10, "bold"),
                                          background="#ecf0f1", foreground="#34495e", anchor="ne", padding=(0,0,2,2)) # Pad to push to top-right
                    day_label.grid(row=0, column=0, sticky="ne")

                    current_day_date = date(self.current_calendar_year, self.current_calendar_month, day_num)
                    if current_day_date == date.today():
                        day_frame.config(style="CurrentDay.TFrame") # Highlight current day

                    # Add event indicator if events exist for this day
                    if day_num in events_by_date:
                        event_indicator = ttk.Label(day_frame, text="•", font=("Arial", 16, "bold"), foreground="red", background="#ecf0f1")
                        event_indicator.grid(row=0, column=0, sticky="nw", padx=(2,0), pady=(0,2)) # Dot top-left

                        # Bind click to show event details
                        day_frame.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        day_label.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        event_indicator.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                else: # Placeholder for days outside the month
                    day_frame.config(relief="flat", borderwidth=0, style="EmptyDay.TFrame")

            self.calendar_grid_frame.grid_rowconfigure(row_offset, weight=1) # Make rows expand evenly
            row_offset += 1

        # Clear event details when month changes
        self.event_details_text.config(state="normal")
        self.event_details_text.delete("1.0", tk.END)
        self.event_details_text.config(state="disabled")

        # Apply styles for calendar frames
        self.style.configure("Calendar.TLabelframe", background="#ecf0f1", foreground="#34495e", font=("Arial", 12, "bold"))
        self.style.configure("Calendar.TLabelframe.Label", background="#ecf0f1", foreground="#34495e")
        self.style.configure("CalendarDay.TFrame", background="#ecf0f1")
        self.style.configure("CurrentDay.TFrame", background="#e0f7fa", bordercolor="#2196f3", relief="solid", borderwidth=2) # Light blue with darker border
        self.style.configure("EmptyDay.TFrame", background="#f8f9fa") # Lighter grey for empty days

    def _get_events_for_calendar_view(self):
        """
        Fetches all relevant events for the current calendar view:
        - Evaluation Template deadlines
        - Admin Calendar Events
        """
        all_events = []

        # 1. Fetch Evaluation Template deadlines
        # Get templates for current and maybe adjacent months for display.
        # Simplification: Fetch all templates and filter by month in Python for now,
        # or expand the SQL query if performance is an issue with huge number of templates.
        all_templates = self.evaluation_template_controller.get_all_templates()
        for template in all_templates:
            if template.last_date and template.last_date.year == self.current_calendar_year and template.last_date.month == self.current_calendar_month:
                # Create a pseudo-event object for consistency
                class PseudoEvent:
                    def __init__(self, title, date, description):
                        self.title = title
                        self.event_date = date
                        self.description = description
                all_events.append(PseudoEvent(f"Eval: {template.title}", template.last_date, f"Deadline for template ID {template.id}"))

        # 2. Fetch Admin Calendar Events
        admin_id = self.admin_user.admin_id if self.admin_user else None
        admin_events = self.admin_calendar_event_controller.get_events_for_month(self.current_calendar_year, self.current_calendar_month, admin_id)
        all_events.extend(admin_events)

        return all_events


    def show_day_events(self, selected_date, events):
        """Displays events for the selected day."""
        self.event_details_text.config(state="normal")
        self.event_details_text.delete("1.0", tk.END)

        if events:
            event_text = f"Events for {selected_date.strftime('%Y-%m-%d')}:\n"
            for event in events:
                event_text += f"- {event.title}"
                if event.description:
                    event_text += f": {event.description}"
                event_text += "\n"
            self.event_details_text.insert("1.0", event_text)
        else:
            self.event_details_text.insert("1.0", f"No events for {selected_date.strftime('%Y-%m-%d')}.")

        self.event_details_text.config(state="disabled")


    def prev_month(self):
        self.current_calendar_month -= 1
        if self.current_calendar_month < 1:
            self.current_calendar_month = 12
            self.current_calendar_year -= 1
        self.draw_calendar()

    def next_month(self):
        self.current_calendar_month += 1
        if self.current_calendar_month > 12:
            self.current_calendar_month = 1
            self.current_calendar_year += 1
        self.draw_calendar()


    def show_hr_management_wrapper(self):
        self.show_sub_page(self.hr_notebook)
        self.hr_notebook.select(self.hr_students_tab) # Default to Students tab

    def show_course_setup(self):
        if self.admin_user and self.admin_user.can_manage_courses:
            self.show_sub_page(self.sub_pages["CourseSetupPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage courses.")

    def show_evaluation_templates(self):
        if self.admin_user and self.admin_user.can_create_templates:
            self.show_sub_page(self.sub_pages["EvaluationTemplatesPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to create evaluation templates.")

    def show_reports(self):
        if self.admin_user and self.admin_user.can_view_reports:
            self.show_sub_page(self.sub_pages["ReportsPage"]) # Navigate to ReportsPage
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports.")

    def show_complaints(self):
        if self.admin_user and self.admin_user.can_manage_complaints:
            self.show_sub_page(self.sub_pages["ComplaintsPage"]) # Navigate to ComplaintsPage
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage complaints.")

    def show_comparison(self):
        if self.admin_user and self.admin_user.can_view_reports: # Comparison depends on reports access
            self.show_sub_page(self.sub_pages["ComparisonPage"]) # Navigate to ComparisonPage
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports for comparison.")

    def show_app_settings(self):
        self.show_sub_page(self.sub_pages["AppSettingsPage"])

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.auth_controller.logout_admin()
            self.parent_controller.set_current_user(None)
            self.grid_forget()
            self.parent_controller.show_page("LoginPage")

