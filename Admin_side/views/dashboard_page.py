# Admin_side/views/dashboard_page.py (Updated for CustomTkinter and Dashboard Enhancements)
import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.student_controller import StudentController
from controllers.admin_calendar_event_controller import AdminCalendarEventController
from controllers.faculty_request_controller import FacultyRequestController
from controllers.complaint_controller import ComplaintController
# Import sub-pages (will be updated to CustomTkinter in subsequent steps)
from views.hr_students_page import HRStudentsPage
from views.hr_faculty_page import HRFacultyPage
from views.hr_admins_page import HRAdminsPage
from views.course_setup_page import CourseSetupPage
from views.evaluation_templates_page import EvaluationTemplatesPage
from views.reports_page import ReportsPage
from views.complaints_page import ComplaintsPage
from views.faculty_requests_page import FacultyRequestsPage
from views.app_settings_page import AppSettingsPage
from datetime import datetime, date, timedelta
import calendar
from tkcalendar import Calendar # Required for the "Add Meeting" date picker (tkcalendar is not ctk)

# --- Color Palette ---
BLUE = "#1976d2"
DARK_BLUE = "#1565c0"
LIGHT_BLUE = "#e3f2fd"
GREY = "#f5f6fa"
DARK_GREY = "#34495e"
WHITE = "#ffffff"
CARD_BORDER = "#b0bec5"
RED = "#e74c3c"

class DashboardPage(ctk.CTkFrame):
    """
    The main dashboard page for the admin interface.
    Displays quick stats, a calendar, and manages navigation to sub-pages.
    Now uses CustomTkinter for a modern UI.
    """
    def __init__(self, parent, controller, admin_user=None):
        super().__init__(parent)
        self.parent_controller = controller
        self.auth_controller = AuthController()
        self.evaluation_template_controller = EvaluationTemplateController()
        self.student_controller = StudentController()
        self.admin_calendar_event_controller = AdminCalendarEventController()
        self.faculty_request_controller = FacultyRequestController()
        self.complaint_controller = ComplaintController()
        self.admin_user = admin_user

        today = date.today()
        self.current_calendar_year = today.year
        self.current_calendar_month = today.month

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

        self.sub_pages = {}
        # Initialize sub-pages, including HR tabview, and home content eagerly
        self._initialize_sub_pages() 

        self.show_home_content()

        self.update_user_info(admin_user)

        self.update_dashboard_data()
        self.update_clock()


    def create_sidebar(self):
        """
        Creates the navigation sidebar on the left side of the dashboard with enhanced styling.
        """
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#2c3e50")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # User info section with gradient-like effect
        user_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#34495e", corner_radius=12)
        user_frame.pack(pady=20, padx=15, fill="x")
        
        self.user_info_label = ctk.CTkLabel(user_frame, text="", font=("Arial", 18, "bold"), 
                                          text_color="white", wraplength=250)
        self.user_info_label.pack(pady=15, fill="x")
        
        # Navigation buttons with enhanced styling
        nav_buttons_config = [
            ("Home", self.show_home_content),
            ("HR Management", self.show_hr_management_wrapper),
            ("Course Setup", self.show_course_setup),
            ("Evaluation", self.show_evaluation_templates),
            ("Reports", self.show_reports),
            ("Complaints", self.show_complaints),
            ("Faculty Requests", self.show_faculty_requests),
            ("Application Settings", self.show_app_settings),
        ]
        
        self.nav_buttons = []
        for text, command in nav_buttons_config:
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=text, 
                command=command, 
                font=("Arial", 16, "bold"), 
                height=50, 
                width=250, 
                corner_radius=12,
                fg_color="#3498db",
                hover_color="#2980b9",
                text_color="white",
                border_width=0
            )
            btn.pack(fill="x", pady=6, padx=15)
            self.nav_buttons.append(btn)
        
        # Logout button with enhanced styling
        logout_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Logout", 
            command=self.handle_logout, 
            font=("Arial", 16, "bold"), 
            fg_color="#e74c3c", 
            hover_color="#c0392b", 
            height=50, 
            width=250, 
            corner_radius=12,
            text_color="white"
        )
        logout_button.pack(fill="x", pady=20, padx=15, side="bottom")

    def _get_text_color(self):
        # Navy blue for light mode, white for dark mode
        mode = ctk.get_appearance_mode()
        return "#001f4d" if mode == "Light" else "white"

    def create_content_area(self):
        """
        Creates the main content frame where different sub-pages will be displayed.
        """
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _initialize_sub_pages(self):
        """
        Initializes instances of all sub-pages and stores them in `self.sub_pages`.
        These pages are created once and then hidden/shown as needed.
        Ensures robust initialization of CTkTabview and its tabs.
        """
        self.hr_tabview = ctk.CTkTabview(self.content_frame)
        self.sub_pages["HRManagementWrapper"] = self.hr_tabview
        self.hr_students_tab_frame = self.hr_tabview.add("Students")
        self.hr_faculty_tab_frame = self.hr_tabview.add("Faculty")
        self.hr_admins_tab_frame = self.hr_tabview.add("Admins")
        # Do NOT call .pack() on the tab frames themselves!
        self.hr_students_tab = HRStudentsPage(parent=self.hr_students_tab_frame, controller=self.parent_controller)
        self.hr_faculty_tab = HRFacultyPage(parent=self.hr_faculty_tab_frame, controller=self.parent_controller)
        self.hr_admins_tab = HRAdminsPage(parent=self.hr_admins_tab_frame, controller=self.parent_controller)
        # Only pack or grid widgets INSIDE the tab frames, not the frames themselves
        self.hr_students_tab.pack(fill="both", expand=True)
        self.hr_faculty_tab.pack(fill="both", expand=True)
        self.hr_admins_tab.pack(fill="both", expand=True)

        # Other main sub-pages
        self.sub_pages["CourseSetupPage"] = CourseSetupPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["EvaluationTemplatesPage"] = EvaluationTemplatesPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ReportsPage"] = ReportsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ComplaintsPage"] = ComplaintsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["FacultyRequestsPage"] = FacultyRequestsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["AppSettingsPage"] = AppSettingsPage(parent=self.content_frame, controller=self.parent_controller)
        # Eagerly create home content
        self.sub_pages["HomeContent"] = self._create_home_content()


    def show_sub_page(self, page_widget):
        """
        Hides all current content in `self.content_frame` and displays the specified page_widget.
        :param page_widget: The CustomTkinter widget (CTkFrame/CTkTabview) to display.
        """
        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

        if page_widget:
            page_widget.grid(row=0, column=0, sticky="nsew")
            page_widget.tkraise()
        else:
            messagebox.showerror("Error", "Selected content not available or not properly initialized.")

    def update_user_info(self, admin_user):
        """
        Updates the displayed user information and sets permissions for navigation buttons.
        :param admin_user: The Admin object of the currently logged-in user.
        """
        self.admin_user = admin_user
        if self.admin_user:
            self.user_info_label.configure(text=f"Welcome,\n{self.admin_user.name}")
            self._update_navigation_permissions()
            self.update_dashboard_data()


    def _update_navigation_permissions(self):
        """
        Sets the enabled/disabled state of navigation buttons based on the
        current admin user's permissions.
        This version attempts to directly control the visibility/interactivity of tab content
        frames as a workaround for persistent CTkTabview issues.
        """
        if not self.admin_user:
            for btn in self.nav_buttons:
                btn.configure(state="disabled")
            # Do NOT call .pack_forget() on tab frames, just disable tabs if needed
            return
        for btn in self.nav_buttons:
            text = btn.cget("text")
            if "HR Management" in text:
                btn.configure(state="normal" if self.admin_user.can_manage_users else "disabled")
            elif "Course Setup" in text:
                btn.configure(state="normal" if self.admin_user.can_manage_courses else "disabled")
            elif "Evaluation" in text:
                btn.configure(state="normal" if self.admin_user.can_create_templates else "disabled")
            elif "Reports" in text:
                btn.configure(state="normal" if self.admin_user.can_view_reports else "disabled")
            elif "Complaints" in text or "Faculty Requests" in text:
                btn.configure(state="normal" if self.admin_user.can_manage_complaints else "disabled")
            elif "Application settings" in text or "Home" in text:
                btn.configure(state="normal")
        # No .pack_forget() or .pack() on tab frames here


    def show_home_content(self):
        """
        Displays the main dashboard home content (info cards, calendar).
        """
        self.show_sub_page(self.sub_pages["HomeContent"])
        self.update_dashboard_data()

    def _create_home_content(self):
        """
        Creates and lays out the widgets for the dashboard's home content area with enhanced styling.
        Includes info cards, real-time clock, and an interactive calendar.
        """
        home_frame = ctk.CTkFrame(self.content_frame, corner_radius=16, fg_color=GREY)
        home_frame.grid_rowconfigure(0, weight=0)
        home_frame.grid_rowconfigure(1, weight=0)
        home_frame.grid_rowconfigure(2, weight=1)
        home_frame.grid_columnconfigure(0, weight=1)
        home_frame.grid_columnconfigure(1, weight=1)
        home_frame.grid_columnconfigure(2, weight=1)

        # Title and clock
        title_frame = ctk.CTkFrame(home_frame, fg_color=LIGHT_BLUE, corner_radius=12)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(20, 30), padx=20, sticky="ew")
        title_frame.columnconfigure(0, weight=1)
        home_label = ctk.CTkLabel(title_frame, text="Admin Dashboard", font=("Arial", 32, "bold"), text_color=DARK_BLUE)
        home_label.pack(side="left", pady=20, padx=20)
        self.clock_label = ctk.CTkLabel(title_frame, text="", font=("Arial", 18, "bold"), text_color=BLUE)
        self.clock_label.pack(side="right", pady=20, padx=20)

        # Info cards (reduced height)
        self.info_cards_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
        self.info_cards_frame.grid(row=1, column=0, columnspan=3, pady=(10, 5), padx=20, sticky="ew")
        self.info_cards_frame.columnconfigure(0, weight=1)
        self.info_cards_frame.columnconfigure(1, weight=1)
        self.info_cards_frame.columnconfigure(2, weight=1)
        self.running_evals_card = self._create_info_card(self.info_cards_frame, "Running Evaluations", "0")
        self.running_evals_card.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.total_batches_card = self._create_info_card(self.info_cards_frame, "Total Batches", "0")
        self.total_batches_card.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.complaints_card = self._create_info_card(self.info_cards_frame, "Complaints", "0")
        self.complaints_card.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

        # Calendar section
        calendar_wrapper_frame = ctk.CTkFrame(home_frame, corner_radius=16, fg_color=WHITE, border_width=2, border_color=CARD_BORDER)
        calendar_wrapper_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
        calendar_wrapper_frame.grid_rowconfigure(1, weight=1)
        calendar_wrapper_frame.grid_columnconfigure(0, weight=1)
        calendar_frame = ctk.CTkFrame(calendar_wrapper_frame, fg_color="transparent")
        calendar_frame.pack(fill="both", expand=True, padx=15, pady=10)
        calendar_nav_frame = ctk.CTkFrame(calendar_frame, fg_color=LIGHT_BLUE, corner_radius=10)
        calendar_nav_frame.pack(pady=10, fill="x", padx=10)
        calendar_nav_frame.columnconfigure(0, weight=1)
        prev_btn = ctk.CTkButton(calendar_nav_frame, text="< Prev", command=self.prev_month, width=120, font=("Arial", 16, "bold"), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, corner_radius=8)
        prev_btn.pack(side="left", padx=15, pady=15)
        self.month_year_label = ctk.CTkLabel(calendar_nav_frame, text="", font=("Arial", 20, "bold"), text_color=DARK_BLUE)
        self.month_year_label.pack(side="left", expand=True, fill="x", anchor="center")
        next_btn = ctk.CTkButton(calendar_nav_frame, text="Next >", command=self.next_month, width=120, font=("Arial", 16, "bold"), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, corner_radius=8)
        next_btn.pack(side="right", padx=15, pady=15)
        add_event_btn = ctk.CTkButton(calendar_nav_frame, text="Add Event", command=self.open_add_event_form, font=("Arial", 16, "bold"), fg_color="#27ae60", hover_color="#229954", text_color=WHITE, corner_radius=8)
        add_event_btn.pack(side="right", padx=15, pady=15)
        self.calendar_grid_frame = ctk.CTkFrame(calendar_frame, border_width=2, corner_radius=12, fg_color=GREY, border_color=CARD_BORDER)
        self.calendar_grid_frame.pack(pady=15, fill="both", expand=True, padx=10)
        # Event details area (no box, no heading, just a frame)
        self.event_details_frame = ctk.CTkFrame(calendar_frame, fg_color=GREY, corner_radius=0, border_width=0)
        self.event_details_frame.pack(pady=10, fill="x", padx=10)
        self.draw_calendar()
        return home_frame

    def _create_info_card(self, parent, title, value):
        card_frame = ctk.CTkFrame(parent, corner_radius=16, fg_color=WHITE, border_width=2, border_color=CARD_BORDER)
        card_frame.columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(card_frame, text=title, font=ctk.CTkFont(family="Arial", size=14, weight="bold"), text_color=DARK_BLUE)
        title_label.grid(row=0, column=0, pady=(20, 5), padx=20)
        value_label = ctk.CTkLabel(card_frame, text=value, font=ctk.CTkFont(family="Arial", size=36, weight="bold"), text_color=BLUE)
        value_label.grid(row=1, column=0, pady=(5, 20), padx=20)
        card_frame.value_label = value_label
        return card_frame

    def update_dashboard_data(self):
        """
        Fetches and updates dynamic data displayed on the dashboard (e.g., counts, calendar events).
        Schedules itself to run periodically.
        """
        if not self.admin_user:
            self.after(5000, self.update_dashboard_data)
            return

        running_evals_count = self.evaluation_template_controller.get_running_evaluations_count(self.admin_user.admin_id)
        self.running_evals_card.value_label.configure(text=str(running_evals_count))

        total_batches_count = self.student_controller.get_total_batches_count()
        self.total_batches_card.value_label.configure(text=str(total_batches_count))

        # Complaints: count pending or in_progress
        pending_complaints = self.complaint_controller.get_all_complaints(status='pending')
        ongoing_complaints = self.complaint_controller.get_all_complaints(status='in_progress')
        complaints_count = len(pending_complaints) + len(ongoing_complaints)
        self.complaints_card.value_label.configure(text=str(complaints_count))

        self.after(60000, self.update_dashboard_data)


    def update_clock(self):
        """
        Updates the real-time clock displayed on the dashboard header.
        Schedules itself to run every second.
        """
        current_time = datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.clock_label.configure(text=f"{current_date}\n{current_time}")
        self.after(1000, self.update_clock)


    def draw_calendar(self):
        """
        Apple-style calendar with clickable day cells:
        - Entire day cell is clickable
        - Clicking highlights the cell and shows event details below
        - Only one day is selected at a time
        - Today is still a blue circle
        - Selected day gets a light blue border
        """
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        import calendar
        from datetime import date, datetime
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        month_days = cal.monthdayscalendar(self.current_calendar_year, self.current_calendar_month)
        self.month_year_label.configure(text=datetime(self.current_calendar_year, self.current_calendar_month, 1).strftime("%B %Y"))

        # Set soft gray background for the calendar area
        self.calendar_grid_frame.configure(fg_color=GREY)

        # Track selected day (persist across redraws)
        if not hasattr(self, 'selected_calendar_day') or self.selected_calendar_day is None:
            # Default: today if in this month, else first day of month
            today = date.today()
            if today.year == self.current_calendar_year and today.month == self.current_calendar_month:
                self.selected_calendar_day = today.day
            else:
                self.selected_calendar_day = 1

        # Header: Sun-Sat
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day_name in enumerate(day_names):
            color = "#e74c3c" if i in [5, 6] else "#222"
            day_header = ctk.CTkLabel(self.calendar_grid_frame, text=day_name, font=("SF Pro Display", 17, "bold"), text_color=color, fg_color=GREY)
            day_header.grid(row=0, column=i, sticky="nsew", padx=6, pady=(0, 8))
            self.calendar_grid_frame.grid_columnconfigure(i, weight=1)

        all_month_events = self._get_events_for_calendar_view()
        events_by_date = {}
        for event in all_month_events:
            if hasattr(event.event_date, 'day'):
                event_day = event.event_date.day
                if event_day not in events_by_date:
                    events_by_date[event_day] = []
                events_by_date[event_day].append(event)

        row_offset = 1
        self._calendar_day_frames = {}  # For selection highlight
        # All calendar cells same size
        cell_width = 48
        cell_height = 48
        for week in month_days:
            for col_idx, day_num in enumerate(week):
                is_holiday = col_idx in [5, 6]
                is_today = False
                is_selected = (day_num == self.selected_calendar_day)
                cell_bg = "#fff"
                border_color = "#f5f6fa"
                border_width = 0
                if is_holiday:
                    cell_bg = "#fff5f5"
                if day_num != 0:
                    current_day_date = date(self.current_calendar_year, self.current_calendar_month, day_num)
                    if current_day_date == date.today():
                        is_today = True
                    if is_selected:
                        border_color = "#1976d2"
                        border_width = 2
                # Outer frame for spacing
                outer = ctk.CTkFrame(self.calendar_grid_frame, fg_color=GREY)
                outer.grid(row=row_offset, column=col_idx, sticky="nsew", padx=4, pady=4)
                outer.grid_rowconfigure(0, weight=1)
                outer.grid_columnconfigure(0, weight=1)
                # Day cell
                day_frame = ctk.CTkFrame(outer, fg_color=cell_bg, corner_radius=14, border_color=border_color, border_width=border_width, width=cell_width, height=cell_height)
                day_frame.grid(row=0, column=0, sticky="nsew")
                day_frame.grid_propagate(False)
                if day_num != 0:
                    # Add more padding inside the cell
                    inner_pad = 8
                    if is_today:
                        circle = ctk.CTkLabel(day_frame, text=str(day_num), font=("SF Pro Display", 18, "bold"), text_color=WHITE, fg_color=BLUE, width=32, height=32, corner_radius=16)
                        circle.grid(row=0, column=0, pady=(inner_pad,0), padx=inner_pad, sticky="n")
                    else:
                        day_label = ctk.CTkLabel(day_frame, text=str(day_num), font=("SF Pro Display", 18, "bold"), text_color="#222" if not is_holiday else RED, fg_color=cell_bg)
                        day_label.grid(row=0, column=0, pady=(inner_pad,0), padx=inner_pad, sticky="n")
                    # Event dot
                    if day_num in events_by_date:
                        dot = ctk.CTkLabel(day_frame, text="•", font=("Arial", 16), text_color=BLUE, fg_color=cell_bg)
                        dot.grid(row=1, column=0, pady=(0,inner_pad), padx=inner_pad, sticky="n")
                    # Make the whole cell clickable
                    def make_onclick(day):
                        return lambda e: self._on_calendar_day_click(day, events_by_date.get(day, []))
                    day_frame.bind("<Button-1>", make_onclick(day_num))
                    for child in day_frame.winfo_children():
                        child.bind("<Button-1>", make_onclick(day_num))
                    self._calendar_day_frames[day_num] = day_frame
                else:
                    empty = ctk.CTkLabel(day_frame, text="", fg_color=cell_bg)
                    empty.grid(row=0, column=0)
            self.calendar_grid_frame.grid_rowconfigure(row_offset, weight=1)
            row_offset += 1
        # Show details for selected day
        selected_events = events_by_date.get(self.selected_calendar_day, [])
        self.show_day_events(date(self.current_calendar_year, self.current_calendar_month, self.selected_calendar_day), selected_events)

    def _on_calendar_day_click(self, day_num, events):
        self.selected_calendar_day = day_num
        self.draw_calendar()  # Redraw to update highlight and details


    def _get_events_for_calendar_view(self):
        """
        Fetches all relevant events for the current calendar view, combining
        Evaluation Template deadlines and Admin Calendar Events.
        :return: A list of event objects (either AdminCalendarEvent or PseudoEvent).
        """
        all_events = []

        # 1. Fetch Evaluation Template deadlines
        all_templates = self.evaluation_template_controller.get_all_templates()
        for template in all_templates:
            if template.last_date and template.last_date.year == self.current_calendar_year and template.last_date.month == self.current_calendar_month:
                class PseudoEvent:
                    def __init__(self, title, date, description):
                        self.title = title
                        self.event_date = date
                        self.description = description
                
                event_title = f"Eval Deadline: {template.title}"
                event_description_parts = []
                if template.course_code:
                    event_description_parts.append(f"Course: {template.course_code}")
                if template.batch:
                    event_description_parts.append(f"Batch: {template.batch}")
                if template.session:
                    event_description_parts.append(f"Session: {template.session}")
                
                event_description = "Deadline for " + ", ".join(event_description_parts) + "." if event_description_parts else "General Evaluation Deadline."

                all_events.append(PseudoEvent(event_title, template.last_date, event_description))

        # 2. Fetch Admin Calendar Events for the current month
        admin_id = self.admin_user.admin_id if self.admin_user else None
        admin_events = self.admin_calendar_event_controller.get_events_for_month(self.current_calendar_year, self.current_calendar_month, admin_id)
        all_events.extend(admin_events)

        return all_events


    def show_day_events(self, selected_date, events):
        # Clear previous widgets
        for widget in self.event_details_frame.winfo_children():
            widget.destroy()
        if events:
            for event in events:
                title_label = ctk.CTkLabel(self.event_details_frame, text=event.title, font=("Arial", 15, "bold"), text_color=RED, fg_color=GREY)
                title_label.pack(anchor="w", pady=(0, 0), padx=5)
                if event.description:
                    desc_label = ctk.CTkLabel(self.event_details_frame, text=event.description, font=("Arial", 13), text_color=DARK_GREY, fg_color=GREY, wraplength=500, justify="left")
                    desc_label.pack(anchor="w", pady=(0, 8), padx=20)
        else:
            no_event_label = ctk.CTkLabel(self.event_details_frame, text="No events for this day.", font=("Arial", 13, "italic"), text_color=DARK_GREY, fg_color=GREY)
            no_event_label.pack(anchor="w", pady=5, padx=5)


    def open_add_event_form(self):
        """
        Opens a new CTkToplevel window (form) to allow the admin to add a new calendar event.
        Includes a date picker (tkcalendar) for easy date selection with enhanced styling.
        """
        from tkcalendar import Calendar
        add_event_window = ctk.CTkToplevel(self.parent_controller.get_root_window())
        add_event_window.title("Add New Calendar Event")
        add_event_window.transient(self.parent_controller.get_root_window())
        add_event_window.grab_set()
        add_event_window.geometry("480x480")
        form_frame = ctk.CTkFrame(add_event_window, fg_color=GREY, corner_radius=0)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        title_label = ctk.CTkLabel(form_frame, text="Add New Event", font=("Arial", 20, "bold"), text_color=DARK_BLUE)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(form_frame, text="Event Title:", font=("Arial", 14, "bold"), text_color=DARK_BLUE).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        title_entry = ctk.CTkEntry(form_frame, width=300, height=32, font=("Arial", 12), fg_color=WHITE, text_color=DARK_BLUE, border_color=CARD_BORDER, border_width=1, corner_radius=8)
        title_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(form_frame, text="Description:", font=("Arial", 14, "bold"), text_color=DARK_BLUE).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        description_text = ctk.CTkTextbox(form_frame, wrap="word", height=60, width=300, font=("Arial", 12), fg_color=WHITE, text_color=DARK_BLUE, border_color=CARD_BORDER, border_width=1, corner_radius=8)
        description_text.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(form_frame, text="Event Date:", font=("Arial", 14, "bold"), text_color=DARK_BLUE).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        cal = Calendar(form_frame, selectmode='day', date_pattern='y-mm-dd', font=("Arial", 11), selectbackground=BLUE, selectforeground=WHITE, normalbackground=WHITE, normalforeground=DARK_BLUE, weekendbackground=GREY, weekendforeground=RED)
        cal.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        def save_event():
            title = title_entry.get().strip()
            description = description_text.get("1.0", ctk.END).strip()
            event_date_str = cal.get_date()
            if not title or not event_date_str:
                messagebox.showerror("Validation Error", "Event Title and Event Date are required.")
                return
            try:
                event_date_obj = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid Date format. Please use YYYY-MM-DD.")
                return
            admin_id = self.admin_user.admin_id if self.admin_user else None
            if not admin_id:
                messagebox.showerror("Error", "Admin user not logged in. Cannot add event.")
                return
            from models.admin_calendar_event_model import AdminCalendarEvent
            new_event = AdminCalendarEvent(event_id=None, title=title, description=description, event_date=event_date_obj, admin_id=admin_id)
            success = self.admin_calendar_event_controller.add_event(new_event)
            if success:
                messagebox.showinfo("Success", "Event added successfully.")
                add_event_window.destroy()
                self.draw_calendar()
            else:
                messagebox.showerror("Error", "Failed to add event. A database error might have occurred.")
        save_btn = ctk.CTkButton(form_frame, text="Save Event", command=save_event, font=("Arial", 15, "bold"), fg_color="#27ae60", hover_color="#229954", text_color=WHITE, corner_radius=8, height=36)
        save_btn.grid(row=4, column=0, columnspan=3, pady=20, padx=10, sticky="ew")
        add_event_window.update_idletasks()
        center_x = self.parent_controller.get_root_window().winfo_x() + self.parent_controller.get_root_window().winfo_width() // 2 - add_event_window.winfo_width() // 2
        center_y = self.parent_controller.get_root_window().winfo_y() + self.parent_controller.get_root_window().winfo_height() // 2 - add_event_window.winfo_height() // 2
        add_event_window.geometry(f"+{int(center_x)}+{int(center_y)}")
        add_event_window.protocol("WM_DELETE_WINDOW", add_event_window.destroy)
        self.parent_controller.get_root_window().wait_window(add_event_window)


    def prev_month(self):
        """Navigates the calendar to the previous month."""
        self.current_calendar_month -= 1
        if self.current_calendar_month < 1:
            self.current_calendar_month = 12
            self.current_calendar_year -= 1
        self.draw_calendar()

    def next_month(self):
        """Navigates the calendar to the next month."""
        self.current_calendar_month += 1
        if self.current_calendar_month > 12:
            self.current_calendar_month = 1
            self.current_calendar_year += 1
        self.draw_calendar()


    def show_hr_management_wrapper(self):
        """
        Displays the HR Management section, defaulting to the Students tab.
        """
        if self.admin_user and self.admin_user.can_manage_users:
            self.show_sub_page(self.hr_tabview)
            self.hr_tabview.set("Students")
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage users.")


    def show_course_setup(self):
        """
        Displays the Course Setup page if the admin has permission.
        """
        if self.admin_user and self.admin_user.can_manage_courses:
            self.show_sub_page(self.sub_pages["CourseSetupPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage courses.")

    def show_evaluation_templates(self):
        """
        Displays the Evaluation Templates page if the admin has permission.
        """
        if self.admin_user and self.admin_user.can_create_templates:
            self.show_sub_page(self.sub_pages["EvaluationTemplatesPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to create evaluation templates.")

    def show_reports(self):
        """
        Displays the Reports page if the admin has permission.
        """
        if self.admin_user and self.admin_user.can_view_reports:
            self.show_sub_page(self.sub_pages["ReportsPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to view reports.")

    def show_complaints(self):
        """
        Displays the Complaints page if the admin has permission.
        """
        if self.admin_user and self.admin_user.can_manage_complaints:
            self.show_sub_page(self.sub_pages["ComplaintsPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage complaints.")

    def show_faculty_requests(self):
        """
        Displays the Faculty Requests page if the admin has permission.
        """
        if self.admin_user and self.admin_user.can_manage_complaints:
            self.show_sub_page(self.sub_pages["FacultyRequestsPage"])
        else:
            messagebox.showwarning("Permission Denied", "You do not have permission to manage faculty requests.")

    def show_app_settings(self):
        """
        Displays the Application Settings page.
        """
        self.show_sub_page(self.sub_pages["AppSettingsPage"])

    def handle_logout(self):
        """
        Handles the logout process from the dashboard.
        Confirms with the user before logging out.
        """
        if messagebox.askyesno("Logout Confirmation", "Are you sure you want to log out?"):
            self.parent_controller.logout_user()

