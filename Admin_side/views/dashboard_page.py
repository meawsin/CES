# Admin_side/views/dashboard_page.py (Updated for CustomTkinter and Dashboard Enhancements)
import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from controllers.evaluation_template_controller import EvaluationTemplateController
from controllers.student_controller import StudentController
from controllers.admin_calendar_event_controller import AdminCalendarEventController
from controllers.faculty_request_controller import FacultyRequestController
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
        self.admin_user = admin_user

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

        self.sub_pages = {}
        # Initialize sub-pages, including HR tabview, but don't show them yet
        self._initialize_sub_pages() 

        self.current_calendar_year = datetime.now().year
        self.current_calendar_month = datetime.now().month

        self.show_home_content()

        self.update_user_info(admin_user)

        self.update_dashboard_data()
        self.update_clock()


    def create_sidebar(self):
        """
        Creates the navigation sidebar on the left side of the dashboard.
        """
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.user_info_label = ctk.CTkLabel(self.sidebar_frame, text="", font=("Arial", 20, "bold"), text_color=self._get_text_color())
        self.user_info_label.pack(pady=32, fill="x")
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
            btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command, font=("Arial", 18, "bold"), height=48, width=220, corner_radius=10, text_color=self._get_text_color())
            btn.pack(fill="x", pady=8, padx=18)
            self.nav_buttons.append(btn)
        logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", command=self.handle_logout, font=("Arial", 18, "bold"), fg_color="#E74C3C", hover_color="#C0392B", height=48, width=220, corner_radius=10)
        logout_button.pack(fill="x", pady=32, padx=18, side="bottom")

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
        Creates the home content frame if it doesn't exist.
        """
        if "HomeContent" not in self.sub_pages:
            self.sub_pages["HomeContent"] = self._create_home_content()
        self.show_sub_page(self.sub_pages["HomeContent"])
        self.update_dashboard_data()

    def _create_home_content(self):
        """
        Creates and lays out the widgets for the dashboard's home content area.
        Includes info cards, real-time clock, and an interactive calendar.
        """
        home_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        home_frame.grid_rowconfigure(0, weight=0)
        home_frame.grid_rowconfigure(1, weight=0)
        home_frame.grid_rowconfigure(2, weight=1)
        home_frame.grid_columnconfigure(0, weight=1)
        home_frame.grid_columnconfigure(1, weight=1)
        home_frame.grid_columnconfigure(2, weight=1)

        # Title and Real-time Clock section
        title_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 24), sticky="ew")
        title_frame.columnconfigure(0, weight=1)

        home_label = ctk.CTkLabel(title_frame, text="Admin Dashboard", font=("Arial", 28, "bold"), text_color=self._get_text_color())
        home_label.pack(side="left", pady=12, padx=16)

        self.clock_label = ctk.CTkLabel(title_frame, text="", font=("Arial", 20, "bold"), text_color=self._get_text_color())
        self.clock_label.pack(side="right", pady=12, padx=16)

        # Information Cards section
        self.info_cards_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
        self.info_cards_frame.grid(row=1, column=0, columnspan=3, pady=16, sticky="ew")
        self.info_cards_frame.columnconfigure(0, weight=1)
        self.info_cards_frame.columnconfigure(1, weight=1)
        self.info_cards_frame.columnconfigure(2, weight=1)

        self.running_evals_card = self._create_info_card(self.info_cards_frame, "Running Evaluations", "0")
        self.running_evals_card.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")

        self.total_batches_card = self._create_info_card(self.info_cards_frame, "Total Batches", "0")
        self.total_batches_card.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

        self.pending_requests_card = self._create_info_card(self.info_cards_frame, "Pending Requests", "0")
        self.pending_requests_card.grid(row=0, column=2, padx=14, pady=14, sticky="nsew")

        # Calendar Section (Resizable)
        calendar_wrapper_frame = ctk.CTkFrame(home_frame, corner_radius=12)
        calendar_wrapper_frame.grid(row=2, column=0, columnspan=3, padx=14, pady=24, sticky="nsew")
        calendar_wrapper_frame.grid_rowconfigure(1, weight=1)
        calendar_wrapper_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(calendar_wrapper_frame, text="Calendar & Events", font=("Arial", 20, "bold"), text_color=self._get_text_color()).pack(anchor="nw", padx=18, pady=12)

        calendar_frame = ctk.CTkFrame(calendar_wrapper_frame, fg_color="transparent")
        calendar_frame.pack(fill="both", expand=True, padx=12, pady=8)

        # Calendar Header (Month/Year Navigation and Add Event Button)
        calendar_nav_frame = ctk.CTkFrame(calendar_frame, fg_color="transparent")
        calendar_nav_frame.pack(pady=8, fill="x")
        calendar_nav_frame.columnconfigure(0, weight=1)

        ctk.CTkButton(calendar_nav_frame, text="< Prev", command=self.prev_month, width=100, font=("Arial", 16, "bold"), text_color=self._get_text_color()).pack(side="left", padx=8)
        self.month_year_label = ctk.CTkLabel(calendar_nav_frame, text="", font=("Arial", 18, "bold"), text_color=self._get_text_color())
        self.month_year_label.pack(side="left", expand=True, fill="x", anchor="center")
        ctk.CTkButton(calendar_nav_frame, text="Next >", command=self.next_month, width=100, font=("Arial", 16, "bold"), text_color=self._get_text_color()).pack(side="right", padx=8)
        ctk.CTkButton(calendar_nav_frame, text="Add Meeting", command=self.open_add_event_form, font=("Arial", 16, "bold"), text_color=self._get_text_color()).pack(side="right", padx=8)

        # Calendar Grid itself
        self.calendar_grid_frame = ctk.CTkFrame(calendar_frame, border_width=1, corner_radius=10)
        self.calendar_grid_frame.pack(pady=10, fill="both", expand=True)

        # Event Details display area for selected day
        event_details_wrapper_frame = ctk.CTkFrame(calendar_frame, corner_radius=10)
        event_details_wrapper_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(event_details_wrapper_frame, text="Selected Day Events", font=("Arial", 16, "bold"), text_color=self._get_text_color()).pack(anchor="nw", padx=10, pady=5)

        self.event_details_text = ctk.CTkTextbox(event_details_wrapper_frame, wrap="word", height=5, font=("Arial", 14), activate_scrollbars=True)
        self.event_details_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.event_details_text.configure(state="disabled")

        self.draw_calendar()

        return home_frame

    def _create_info_card(self, parent, title, value):
        """
        Helper method to create a standardized information card for the dashboard.
        :param parent: The parent widget.
        :param title: The title of the card.
        :param value: The main value to display (e.g., a count).
        :return: The created card frame.
        """
        card_frame = ctk.CTkFrame(parent, corner_radius=10)
        card_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(card_frame, text=title, font=ctk.CTkFont(family="Arial", size=12, weight="bold")).grid(row=0, column=0, pady=(10, 0))
        value_label = ctk.CTkLabel(card_frame, text=value,
                                   font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                                   text_color="#2980b9")
        value_label.grid(row=1, column=0, pady=10)

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

        pending_requests_count = self.faculty_request_controller.get_all_faculty_requests(status='pending')
        self.pending_requests_card.value_label.configure(text=str(len(pending_requests_count)))

        self.draw_calendar()

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
        Draws the calendar grid for the current month and populates it with events.
        Highlights the current day and indicates days with events.
        """
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(self.current_calendar_year, self.current_calendar_month)
        self.month_year_label.configure(text=datetime(self.current_calendar_year, self.current_calendar_month, 1).strftime("%B %Y"))

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            color = "#001f4d" if ctk.get_appearance_mode() == "Light" else "white"
            if day_name in ["Fri", "Sat"]:
                color = "red"
            ctk.CTkLabel(self.calendar_grid_frame, text=day_name, font=("Arial", 16, "bold"), text_color=color).grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.calendar_grid_frame.grid_columnconfigure(i, weight=1)

        all_month_events = self._get_events_for_calendar_view()
        events_by_date = {}
        for event in all_month_events:
            if hasattr(event.event_date, 'day'):
                event_day = event.event_date.day
                if event_day not in events_by_date:
                    events_by_date[event_day] = []
                events_by_date[event_day].append(event)
            else:
                print(f"Warning: Event date format unexpected for event '{event.title}': {event.event_date}")


        row_offset = 1
        for week in month_days:
            for col_idx, day_num in enumerate(week):
                day_color = self._get_text_color()
                if col_idx in [4, 5]:  # Friday (4) and Saturday (5)
                    day_color = "red"
                day_frame = ctk.CTkFrame(self.calendar_grid_frame, border_width=1, corner_radius=5)
                day_frame.grid(row=row_offset, column=col_idx, sticky="nsew", padx=2, pady=2)
                day_frame.grid_rowconfigure(0, weight=1)
                day_frame.grid_rowconfigure(1, weight=1)
                day_frame.grid_columnconfigure(0, weight=1)

                if day_num != 0:
                    day_label = ctk.CTkLabel(day_frame, text=str(day_num), font=("Arial", 16, "bold"), text_color=day_color)
                    day_label.grid(row=0, column=0, sticky="ne")

                    current_day_date = date(self.current_calendar_year, self.current_calendar_month, day_num)
                    if current_day_date == date.today():
                        day_frame.configure(border_color="blue", border_width=2)

                    if day_num in events_by_date:
                        event_indicator = ctk.CTkLabel(day_frame, text="•", font=("Arial", 18, "bold"), text_color="red")
                        event_indicator.grid(row=0, column=0, sticky="nw", padx=(2,0), pady=(0,2))

                        day_frame.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        day_label.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        event_indicator.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                else:
                    day_frame.configure(fg_color="transparent", border_width=0)

            self.calendar_grid_frame.grid_rowconfigure(row_offset, weight=1)
            row_offset += 1

        self.event_details_text.configure(state="normal")
        self.event_details_text.delete("1.0", ctk.END)
        self.event_details_text.configure(state="disabled")


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
        """
        Displays the details of events for a selected day in the text area below the calendar.
        :param selected_date: The datetime.date object of the selected day.
        :param events: A list of event objects for that day.
        """
        self.event_details_text.configure(state="normal")
        self.event_details_text.delete("1.0", ctk.END)

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

        self.event_details_text.configure(state="disabled")


    def open_add_event_form(self):
        """
        Opens a new CTkToplevel window (form) to allow the admin to add a new calendar event.
        Includes a date picker (tkcalendar) for easy date selection.
        """
        add_event_window = ctk.CTkToplevel(self.parent_controller.get_root_window())
        add_event_window.title("Add New Calendar Event")
        add_event_window.transient(self.parent_controller.get_root_window())
        add_event_window.grab_set()
        add_event_window.geometry("500x400")

        form_frame = ctk.CTkFrame(add_event_window, padding="20")
        form_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Event Title:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        title_entry = ctk.CTkEntry(form_frame, width=300)
        title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        description_text = ctk.CTkTextbox(form_frame, wrap="word", height=5, width=30)
        description_text.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Event Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        date_entry = ctk.CTkEntry(form_frame, width=200)
        date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        def _open_calendar_picker(target_entry):
            cal_win = ctk.CTkToplevel(add_event_window)
            cal_win.title("Select Date")
            cal_win.transient(add_event_window)
            cal_win.grab_set()

            initial_date = None
            try:
                current_date_str = target_entry.get().strip()
                if current_date_str:
                    initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

            cal = Calendar(cal_win, selectmode='day',
                           date_pattern='y-mm-dd',
                           year=initial_date.year if initial_date else datetime.now().year,
                           month=initial_date.month if initial_date else datetime.now().month,
                           day=initial_date.day if initial_date else datetime.now().day)
            cal.pack(pady=10)

            ctk.Button(cal_win, text="Select Date", command=lambda: on_date_select(cal.get_date())).pack(pady=5)

            def on_date_select(selected_date_str):
                target_entry.delete(0, ctk.END)
                target_entry.insert(0, selected_date_str)
                cal_win.destroy()
            
            cal_win.update_idletasks()
            center_x = add_event_window.winfo_x() + add_event_window.winfo_width() // 2 - cal_win.winfo_width() // 2
            center_y = add_event_window.winfo_y() + add_event_window.winfo_height() // 2 - cal_win.winfo_height() // 2
            cal_win.geometry(f"+{int(center_x)}+{int(center_y)}")

            cal_win.protocol("WM_DELETE_WINDOW", cal_win.destroy)

        ctk.CTkButton(form_frame, text="📅", width=40, command=lambda: _open_calendar_picker(date_entry)).grid(row=2, column=2, padx=(5,0), sticky="e")


        def save_event():
            title = title_entry.get().strip()
            description = description_text.get("1.0", ctk.END).strip()
            event_date_str = date_entry.get().strip()

            if not title or not event_date_str:
                messagebox.showerror("Validation Error", "Event Title and Event Date are required.")
                return

            try:
                event_date_obj = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid Date format. Please useYYYY-MM-DD.")
                return
            
            admin_id = self.admin_user.admin_id if self.admin_user else None
            if not admin_id:
                messagebox.showerror("Error", "Admin user not logged in. Cannot add event.")
                return

            from models.admin_calendar_event_model import AdminCalendarEvent
            new_event = AdminCalendarEvent(
                event_id=None,
                title=title,
                description=description,
                event_date=event_date_obj,
                admin_id=admin_id
            )
            
            success = self.admin_calendar_event_controller.add_event(new_event)
            if success:
                messagebox.showinfo("Success", "Event added successfully.")
                add_event_window.destroy()
                self.draw_calendar()
            else:
                messagebox.showerror("Error", "Failed to add event. A database error might have occurred.")

        ctk.CTkButton(form_frame, text="➕ Add Event", command=save_event).grid(row=3, column=0, columnspan=3, pady=20)

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
            self.hr_tabview.set_active_tab("Students")
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

