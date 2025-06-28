# views/dashboard_page.py (Updated for Dashboard Enhancements)
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from controllers.evaluation_template_controller import EvaluationTemplateController # For running eval count
from controllers.student_controller import StudentController                 # For total batches count
from controllers.admin_calendar_event_controller import AdminCalendarEventController # For calendar events
from views.hr_students_page import HRStudentsPage # HR Management tab
from views.hr_faculty_page import HRFacultyPage   # HR Management tab
from views.hr_admins_page import HRAdminsPage     # HR Management tab
from views.course_setup_page import CourseSetupPage # Course Management page
from views.evaluation_templates_page import EvaluationTemplatesPage # Evaluation Templates page
from views.reports_page import ReportsPage       # Reports page
from views.complaints_page import ComplaintsPage # Complaints page
# from views.comparison_page import ComparisonPage # Removed as per request
from views.app_settings_page import AppSettingsPage # App Settings page
from datetime import datetime, date, timedelta # For clock and calendar
import calendar # For calendar grid logic
from tkcalendar import Calendar # Required for the "Add Meeting" date picker

class DashboardPage(tk.Frame):
    """
    The main dashboard page for the admin interface.
    Displays quick stats, a calendar, and manages navigation to sub-pages.
    """
    def __init__(self, parent, controller, admin_user=None):
        tk.Frame.__init__(self, parent)
        self.parent_controller = controller # Reference to the main application controller
        self.auth_controller = AuthController() # Authentication controller
        self.evaluation_template_controller = EvaluationTemplateController() # For running evaluations count and eval deadlines
        self.student_controller = StudentController()                 # For total batches count
        self.admin_calendar_event_controller = AdminCalendarEventController() # For admin-specific calendar events
        self.admin_user = admin_user # The logged-in admin user object

        self.configure(bg="#ecf0f1") # Set background color for the dashboard

        # Configure grid layout for sidebar and content area
        self.grid_rowconfigure(0, weight=1) # Main row (for sidebar and content) expands vertically
        self.grid_columnconfigure(0, weight=0) # Sidebar column (fixed width)
        self.grid_columnconfigure(1, weight=1) # Content area column expands horizontally

        self.create_sidebar() # Create the navigation sidebar
        self.create_content_area() # Create the main content display area

        self.sub_pages = {} # Dictionary to hold instances of sub-pages
        self._initialize_sub_pages() # Initialize all sub-pages but don't show them yet

        # Initialize current calendar view to today's month/year
        self.current_calendar_year = datetime.now().year
        self.current_calendar_month = datetime.now().month

        self.show_home_content() # Default to showing the home content on dashboard load

        self.update_user_info(admin_user) # Populate user info and set permissions

        # Start updating dashboard data (stats, calendar) and the real-time clock
        self.update_dashboard_data()
        self.update_clock()


    def create_sidebar(self):
        """
        Creates the navigation sidebar on the left side of the dashboard.
        """
        self.sidebar_frame = tk.Frame(self, bg="#34495e", width=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) # Prevent frame from shrinking to fit content

        # Label to display current user's name
        self.user_info_label = ttk.Label(self.sidebar_frame, text="",
                                         font=("Arial", 14, "bold"), foreground="white", background="#34495e",
                                         anchor="center")
        self.user_info_label.pack(pady=20, fill="x")

        # Configuration for sidebar navigation buttons
        nav_buttons_config = [
            ("Home", self.show_home_content),
            ("HR Management", self.show_hr_management_wrapper),
            ("Course Setup", self.show_course_setup),
            ("Evaluation", self.show_evaluation_templates),
            ("Reports", self.show_reports),
            ("Complaints", self.show_complaints),
            # ("Comparison", self.show_comparison), # Removed as per user request
            ("Application settings", self.show_app_settings),
        ]

        self.nav_buttons = [] # List to keep track of navigation buttons
        for text, command in nav_buttons_config:
            btn = ttk.Button(self.sidebar_frame, text=text, command=command, style="Sidebar.TButton")
            btn.pack(fill="x", pady=5, padx=10) # Pack buttons with padding
            self.nav_buttons.append(btn)

        # Logout button at the bottom of the sidebar
        logout_button = ttk.Button(self.sidebar_frame, text="Logout", command=self.handle_logout, style="Sidebar.Logout.TButton")
        logout_button.pack(fill="x", pady=20, padx=10, side="bottom")

        # Apply specific styles for sidebar buttons (defined in main.py)
        # Note: These styles are configured in the main app's _configure_styles method
        self.style = ttk.Style() # Re-access the global style object


    def create_content_area(self):
        """
        Creates the main content frame where different sub-pages will be displayed.
        """
        self.content_frame = tk.Frame(self, bg="#ecf0f1")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20) # Place in grid, allow expanding
        self.content_frame.grid_rowconfigure(0, weight=1) # Allow row 0 to expand
        self.content_frame.grid_columnconfigure(0, weight=1) # Allow column 0 to expand

    def _initialize_sub_pages(self):
        """
        Initializes instances of all sub-pages and stores them in `self.sub_pages`.
        These pages are created once and then hidden/shown as needed.
        """
        # HR Management uses a Notebook (tabbed interface)
        self.hr_notebook = ttk.Notebook(self.content_frame)
        self.sub_pages["HRManagementWrapper"] = self.hr_notebook

        self.hr_students_tab = HRStudentsPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_faculty_tab = HRFacultyPage(parent=self.hr_notebook, controller=self.parent_controller)
        self.hr_admins_tab = HRAdminsPage(parent=self.hr_notebook, controller=self.parent_controller)

        self.hr_notebook.add(self.hr_students_tab, text="Students")
        self.hr_notebook.add(self.hr_faculty_tab, text="Faculty")
        self.hr_notebook.add(self.hr_admins_tab, text="Admins")

        # Other main sub-pages
        self.sub_pages["CourseSetupPage"] = CourseSetupPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["EvaluationTemplatesPage"] = EvaluationTemplatesPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ReportsPage"] = ReportsPage(parent=self.content_frame, controller=self.parent_controller)
        self.sub_pages["ComplaintsPage"] = ComplaintsPage(parent=self.content_frame, controller=self.parent_controller)
        # self.sub_pages["ComparisonPage"] = ComparisonPage(parent=self.content_frame, controller=self.parent_controller) # Removed
        self.sub_pages["AppSettingsPage"] = AppSettingsPage(parent=self.content_frame, controller=self.parent_controller)


    def show_sub_page(self, page_widget):
        """
        Hides all current content in `self.content_frame` and displays the specified page_widget.
        :param page_widget: The Tkinter widget (Frame/Notebook) to display.
        """
        # Hide all widgets currently packed/gridded in the content frame
        for widget in self.content_frame.winfo_children():
            widget.grid_forget() # Use grid_forget as pages are gridded

        if page_widget:
            # Grid the new page widget and bring it to the front
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
            # Update the user info label in the sidebar
            self.user_info_label.config(text=f"Welcome,\n{self.admin_user.name}")
            self._update_navigation_permissions() # Update button states based on permissions
            self.update_dashboard_data() # Refresh dashboard data pertinent to the new user


    def _update_navigation_permissions(self):
        """
        Sets the enabled/disabled state of navigation buttons based on the
        current admin user's permissions.
        """
        if not self.admin_user: # If no user is logged in, disable all
            for btn in self.nav_buttons:
                btn.config(state="disabled")
            self.hr_notebook.tab(0, state='disabled')
            self.hr_notebook.tab(1, state='disabled')
            self.hr_notebook.tab(2, state='disabled')
            return

        # Iterate through navigation buttons and set their state
        for btn in self.nav_buttons:
            text = btn.cget("text")
            # Check permissions based on the button's text (name)
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
            elif text in ["Application settings", "Home"]: # These pages are generally accessible
                btn.config(state="normal")
            # "Comparison" is removed, so no need to handle its state

        # Also update the state of individual tabs within the HR Management notebook
        self.hr_notebook.tab(0, state='normal' if self.admin_user.can_manage_users else 'disabled') # Students tab
        self.hr_notebook.tab(1, state='normal' if self.admin_user.can_manage_users else 'disabled') # Faculty tab
        self.hr_notebook.tab(2, state='normal' if self.admin_user.can_manage_users else 'disabled') # Admins tab


    # --- Navigation Command Methods ---
    # These methods are called when a sidebar button is clicked.

    def show_home_content(self):
        """
        Displays the main dashboard home content (info cards, calendar).
        Creates the home content frame if it doesn't exist.
        """
        # Create HomeContent dynamically if it doesn't exist yet
        if "HomeContent" not in self.sub_pages:
            self.sub_pages["HomeContent"] = self._create_home_content()
        self.show_sub_page(self.sub_pages["HomeContent"])
        self.update_dashboard_data() # Refresh data when home is shown (e.g., event data)

    def _create_home_content(self):
        """
        Creates and lays out the widgets for the dashboard's home content area.
        Includes info cards, real-time clock, and an interactive calendar.
        """
        home_frame = ttk.Frame(self.content_frame, padding="20", style="HomeFrame.TFrame")
        home_frame.grid_rowconfigure(0, weight=0) # Title row (fixed height)
        home_frame.grid_rowconfigure(1, weight=0) # Info cards row (fixed height)
        home_frame.grid_rowconfigure(2, weight=1) # Calendar row (expands)
        home_frame.grid_columnconfigure(0, weight=1) # Allows columns to expand
        home_frame.grid_columnconfigure(1, weight=1)
        home_frame.grid_columnconfigure(2, weight=1)


        # Title and Real-time Clock section
        title_frame = ttk.Frame(home_frame, style="HomeFrame.TFrame")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        title_frame.columnconfigure(0, weight=1) # For clock label to push right

        home_label = ttk.Label(title_frame, text="Admin Dashboard",
                               font=("Arial", 20, "bold"), foreground="#34495e", background="#ecf0f1")
        home_label.pack(side="left", pady=10, padx=10)

        self.clock_label = ttk.Label(title_frame, text="", font=("Arial", 14), background="#ecf0f1", foreground="#34495e")
        self.clock_label.pack(side="right", pady=10, padx=10)


        # Information Cards section
        self.info_cards_frame = ttk.Frame(home_frame, style="HomeFrame.TFrame")
        self.info_cards_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        self.info_cards_frame.columnconfigure(0, weight=1) # Makes cards expand evenly
        self.info_cards_frame.columnconfigure(1, weight=1)
        self.info_cards_frame.columnconfigure(2, weight=1) # Placeholder for more cards

        # Running Evaluations Card
        self.running_evals_card = self._create_info_card(self.info_cards_frame, "Running Evaluations", "0")
        self.running_evals_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Total Batches Card
        self.total_batches_card = self._create_info_card(self.info_cards_frame, "Total Batches", "0")
        self.total_batches_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Calendar Section
        calendar_frame = ttk.LabelFrame(home_frame, text="Calendar & Events", padding="15", style="Calendar.TLabelframe")
        calendar_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")
        calendar_frame.grid_rowconfigure(1, weight=1) # Calendar grid area row (expands)
        calendar_frame.grid_columnconfigure(0, weight=1) # Calendar grid area column (expands)

        # Calendar Header (Month/Year Navigation and Add Event Button)
        calendar_nav_frame = ttk.Frame(calendar_frame)
        calendar_nav_frame.pack(pady=5, fill="x")
        calendar_nav_frame.columnconfigure(0, weight=1) # Center month label

        ttk.Button(calendar_nav_frame, text="< Prev", command=self.prev_month).pack(side="left", padx=5)
        self.month_year_label = ttk.Label(calendar_nav_frame, text="", font=("Arial", 14, "bold"), background="#ecf0f1", foreground="#34495e")
        self.month_year_label.pack(side="left", expand=True, fill="x", anchor="center")
        ttk.Button(calendar_nav_frame, text="Next >", command=self.next_month).pack(side="right", padx=5)
        ttk.Button(calendar_nav_frame, text="Add Meeting", command=self.open_add_event_form, style="General.TButton").pack(side="right", padx=5) # NEW: Add Meeting button


        # Calendar Grid itself
        self.calendar_grid_frame = ttk.Frame(calendar_frame, borderwidth=1, relief="solid")
        self.calendar_grid_frame.pack(pady=10, fill="both", expand=True)

        # Event Details display area for selected day
        self.event_details_frame = ttk.LabelFrame(calendar_frame, text="Selected Day Events", padding="10")
        self.event_details_frame.pack(pady=10, fill="x")
        self.event_details_text = tk.Text(self.event_details_frame, wrap="word", height=5, state="disabled", font=("Arial", 10))
        self.event_details_text.pack(fill="both", expand=True)
        # Add a scrollbar to event_details_text
        event_details_scrollbar = ttk.Scrollbar(self.event_details_frame, orient="vertical", command=self.event_details_text.yview)
        self.event_details_text.config(yscrollcommand=event_details_scrollbar.set)
        event_details_scrollbar.pack(side="right", fill="y")


        self.draw_calendar() # Initial drawing of the calendar

        return home_frame # Return the created home frame

    def _create_info_card(self, parent, title, value):
        """
        Helper method to create a standardized information card for the dashboard.
        :param parent: The parent widget.
        :param title: The title of the card.
        :param value: The main value to display (e.g., a count).
        :return: The created card frame.
        """
        card_frame = ttk.LabelFrame(parent, text=title, padding="15", style="Card.TLabelframe")
        card_frame.columnconfigure(0, weight=1) # Center content horizontally

        value_label = ttk.Label(card_frame, text=value, font=("Arial", 28, "bold"), foreground="#2980b9", background="#ecf0f1")
        value_label.grid(row=0, column=0, pady=10)

        card_frame.value_label = value_label # Store reference to the value label for updates
        return card_frame

    def update_dashboard_data(self):
        """
        Fetches and updates dynamic data displayed on the dashboard (e.g., counts, calendar events).
        Schedules itself to run periodically.
        """
        if not self.admin_user:
            # Cannot fetch user-specific data without admin_user, try again later
            self.after(5000, self.update_dashboard_data)
            return

        # Update Running Evaluations Count
        running_evals_count = self.evaluation_template_controller.get_running_evaluations_count(self.admin_user.admin_id)
        self.running_evals_card.value_label.config(text=str(running_evals_count))

        # Update Total Batches Count
        total_batches_count = self.student_controller.get_total_batches_count()
        self.total_batches_card.value_label.config(text=str(total_batches_count))

        # Redraw calendar to ensure events are up-to-date
        self.draw_calendar()

        # Schedule the next update (every 1 minute)
        self.after(60000, self.update_dashboard_data)


    def update_clock(self):
        """
        Updates the real-time clock displayed on the dashboard header.
        Schedules itself to run every second.
        """
        current_time = datetime.now().strftime("%I:%M:%S %p") # e.g., 01:23:45 PM
        current_date = datetime.now().strftime("%A, %B %d, %Y") # e.g., Wednesday, June 26, 2025
        self.clock_label.config(text=f"{current_date}\n{current_time}")
        self.after(1000, self.update_clock)


    # --- Calendar Methods ---
    def draw_calendar(self):
        """
        Draws the calendar grid for the current month and populates it with events.
        Highlights the current day and indicates days with events.
        """
        # Clear existing calendar grid widgets
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(self.current_calendar_year, self.current_calendar_month)
        self.month_year_label.config(text=datetime(self.current_calendar_year, self.current_calendar_month, 1).strftime("%B %Y"))

        # Day Headers (Mon, Tue, etc.)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            ttk.Label(self.calendar_grid_frame, text=day_name, font=("Arial", 10, "bold"),
                      background="#bdc3c7", foreground="#2c3e50", anchor="center").grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            self.calendar_grid_frame.grid_columnconfigure(i, weight=1) # Make columns expand evenly

        # Get all relevant events for the current month (eval deadlines and admin events)
        all_month_events = self._get_events_for_calendar_view()
        # Organize events into a dictionary for quick lookup by day number
        events_by_date = {}
        for event in all_month_events:
            # Check if event_date is a datetime.date object or similar. If it's a string, it needs parsing.
            if hasattr(event.event_date, 'day'):
                event_day = event.event_date.day
                if event_day not in events_by_date:
                    events_by_date[event_day] = []
                events_by_date[event_day].append(event)
            else:
                print(f"Warning: Event date format unexpected for event '{event.title}': {event.event_date}")


        # Populate days in Month
        row_offset = 1 # Start after day headers (row 0)
        for week in month_days:
            for col_idx, day_num in enumerate(week):
                day_frame = ttk.Frame(self.calendar_grid_frame, relief="raised", borderwidth=1, style="CalendarDay.TFrame")
                day_frame.grid(row=row_offset, column=col_idx, sticky="nsew", padx=1, pady=1)
                day_frame.grid_rowconfigure(0, weight=1) # For day number
                day_frame.grid_rowconfigure(1, weight=1) # For events (if needed)
                day_frame.grid_columnconfigure(0, weight=1) # For content inside day cell

                if day_num != 0: # If it's a valid day in the month (0 means padding day)
                    # Display day number
                    day_label = ttk.Label(day_frame, text=str(day_num), font=("Arial", 10, "bold"),
                                          background="#ecf0f1", foreground="#34495e", anchor="ne", padding=(0,0,2,2)) # Pad to push to top-right
                    day_label.grid(row=0, column=0, sticky="ne")

                    current_day_date = date(self.current_calendar_year, self.current_calendar_month, day_num)
                    if current_day_date == date.today():
                        day_frame.config(style="CurrentDay.TFrame") # Highlight current day

                    # Add event indicator if events exist for this day
                    if day_num in events_by_date:
                        event_indicator = ttk.Label(day_frame, text="•", font=("Arial", 16, "bold"), foreground="red", background="#ecf0f1")
                        event_indicator.grid(row=0, column=0, sticky="nw", padx=(2,0), pady=(0,2)) # Place dot top-left

                        # Bind click event to show event details for this day
                        day_frame.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        day_label.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                        event_indicator.bind("<Button-1>", lambda e, d=current_day_date, evs=events_by_date[day_num]: self.show_day_events(d, evs))
                else: # Placeholder for days outside the current month
                    day_frame.config(relief="flat", borderwidth=0, style="EmptyDay.TFrame")

            self.calendar_grid_frame.grid_rowconfigure(row_offset, weight=1) # Make rows expand evenly
            row_offset += 1

        # Clear event details text area when month changes or redraws
        self.event_details_text.config(state="normal")
        self.event_details_text.delete("1.0", tk.END)
        self.event_details_text.config(state="disabled")

        # Re-apply styles for calendar frames (just in case)
        self.style.configure("Calendar.TLabelframe", background="#ecf0f1", foreground="#34495e", font=("Arial", 12, "bold"))
        self.style.configure("Calendar.TLabelframe.Label", background="#ecf0f1", foreground="#34495e") # Ensure label background matches frame
        self.style.configure("CalendarDay.TFrame", background="#ecf0f1")
        self.style.configure("CurrentDay.TFrame", background="#e0f7fa", bordercolor="#2196f3", relief="solid", borderwidth=2)
        self.style.configure("EmptyDay.TFrame", background="#f8f9fa")

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
            # Check if template has a last_date and falls within the current calendar month/year
            if template.last_date and template.last_date.year == self.current_calendar_year and template.last_date.month == self.current_calendar_month:
                # Create a simple "PseudoEvent" object to hold necessary info for display
                # This makes it consistent with AdminCalendarEvent objects
                class PseudoEvent:
                    def __init__(self, title, date, description):
                        self.title = title
                        self.event_date = date
                        self.description = description
                
                # Construct a descriptive title and description for the evaluation deadline event
                event_title = f"Eval Deadline: {template.title}"
                event_description_parts = []
                if template.course_code:
                    event_description_parts.append(f"Course: {template.course_code}")
                if template.batch:
                    event_description_parts.append(f"Batch: {template.batch}")
                if template.session:
                    event_description_parts.append(f"Session: {template.session}")
                
                # If there are specific assignment details, add them to the description
                event_description = "Deadline for " + ", ".join(event_description_parts) + "." if event_description_parts else "General Evaluation Deadline."

                all_events.append(PseudoEvent(event_title, template.last_date, event_description))

        # 2. Fetch Admin Calendar Events for the current month
        admin_id = self.admin_user.admin_id if self.admin_user else None
        admin_events = self.admin_calendar_event_controller.get_events_for_month(self.current_calendar_year, self.current_calendar_month, admin_id)
        all_events.extend(admin_events) # Add these to the combined list

        return all_events


    def show_day_events(self, selected_date, events):
        """
        Displays the details of events for a selected day in the text area below the calendar.
        :param selected_date: The datetime.date object of the selected day.
        :param events: A list of event objects for that day.
        """
        self.event_details_text.config(state="normal") # Enable text widget for editing
        self.event_details_text.delete("1.0", tk.END) # Clear previous content

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

        self.event_details_text.config(state="disabled") # Disable text widget to make it read-only


    def open_add_event_form(self):
        """
        Opens a new Toplevel window (form) to allow the admin to add a new calendar event.
        Includes a date picker (tkcalendar) for easy date selection.
        """
        add_event_window = tk.Toplevel(self.parent_controller.get_root_window())
        add_event_window.title("Add New Calendar Event")
        add_event_window.transient(self.parent_controller.get_root_window()) # Make it transient to the root
        add_event_window.grab_set() # Grab focus, preventing interaction with other windows

        form_frame = ttk.Frame(add_event_window, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Event Title Input
        ttk.Label(form_frame, text="Event Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        title_entry = ttk.Entry(form_frame, width=40)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Description Input (Text area)
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        description_text = tk.Text(form_frame, wrap="word", height=5, width=30)
        description_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Event Date Input with Calendar Picker Button
        ttk.Label(form_frame, text="Event Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        date_entry = ttk.Entry(form_frame, width=30)
        date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Helper function to open the calendar picker for the date entry
        def _open_calendar_picker(target_entry):
            cal_win = tk.Toplevel(add_event_window)
            cal_win.title("Select Date")
            cal_win.transient(add_event_window) # Make it transient to the event form
            cal_win.grab_set() # Grab focus for the calendar picker

            # Determine initial date for calendar (today or existing entry value)
            initial_date = None
            try:
                current_date_str = target_entry.get().strip()
                if current_date_str:
                    initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass # If current date in entry is invalid, use today's date

            # Create the Calendar widget
            cal = Calendar(cal_win, selectmode='day',
                           date_pattern='y-mm-dd', # Format for selected date
                           year=initial_date.year if initial_date else datetime.now().year,
                           month=initial_date.month if initial_date else datetime.now().month,
                           day=initial_date.day if initial_date else datetime.now().day)
            cal.pack(pady=10)

            # Button to confirm date selection
            ttk.Button(cal_win, text="Select Date", command=lambda: on_date_select(cal.get_date())).pack(pady=5)

            def on_date_select(selected_date_str):
                # Populate the target entry with the selected date and close the calendar
                target_entry.delete(0, tk.END)
                target_entry.insert(0, selected_date_str)
                cal_win.destroy()
            
            # Center the calendar window over its parent form
            cal_win.update_idletasks() # Ensure sizes are calculated
            center_x = add_event_window.winfo_x() + add_event_window.winfo_width() // 2 - cal_win.winfo_width() // 2
            center_y = add_event_window.winfo_y() + add_event_window.winfo_height() // 2 - cal_win.winfo_height() // 2
            cal_win.geometry(f"+{int(center_x)}+{int(center_y)}")

            cal_win.protocol("WM_DELETE_WINDOW", cal_win.destroy) # Handle X button

        # Calendar button next to date entry
        ttk.Button(form_frame, text="📅", width=3, command=lambda: _open_calendar_picker(date_entry)).grid(row=2, column=2, padx=(5,0), sticky="e")


        def save_event():
            """
            Collects data from the add event form, validates it, and saves it
            to the database via the AdminCalendarEventController.
            """
            title = title_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            event_date_str = date_entry.get().strip()

            # Validation
            if not title or not event_date_str:
                messagebox.showerror("Validation Error", "Event Title and Event Date are required.")
                return

            try:
                event_date_obj = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid Date format. Please use YYYY-MM-DD.")
                return
            
            # Ensure admin is logged in to associate the event
            admin_id = self.admin_user.admin_id if self.admin_user else None
            if not admin_id:
                messagebox.showerror("Error", "Admin user not logged in. Cannot add event.")
                return

            # Create an AdminCalendarEvent object
            from models.admin_calendar_event_model import AdminCalendarEvent # Import locally to avoid circular dependencies
            new_event = AdminCalendarEvent(
                event_id=None, # Let DB auto-increment
                title=title,
                description=description,
                event_date=event_date_obj,
                admin_id=admin_id
            )
            
            # Add event to database
            success = self.admin_calendar_event_controller.add_event(new_event)
            if success:
                messagebox.showinfo("Success", "Event added successfully.")
                add_event_window.destroy() # Close the form
                self.draw_calendar() # Refresh the calendar to show the new event
            else:
                messagebox.showerror("Error", "Failed to add event. A database error might have occurred.")

        # Save Event Button for the form
        ttk.Button(form_frame, text="Add Event", command=save_event, style="FormSave.TButton").grid(row=3, column=0, columnspan=3, pady=20)

        # Center the add event window over the root window
        add_event_window.update_idletasks() # Ensure sizes are calculated
        center_x = self.parent_controller.get_root_window().winfo_x() + self.parent_controller.get_root_window().winfo_width() // 2 - add_event_window.winfo_width() // 2
        center_y = self.parent_controller.get_root_window().winfo_y() + self.parent_controller.get_root_window().winfo_height() // 2 - add_event_window.winfo_height() // 2
        add_event_window.geometry(f"+{int(center_x)}+{int(center_y)}")

        add_event_window.protocol("WM_DELETE_WINDOW", add_event_window.destroy) # Handle X button
        self.parent_controller.get_root_window().wait_window(add_event_window) # Wait for this window to close


    def prev_month(self):
        """Navigates the calendar to the previous month."""
        self.current_calendar_month -= 1
        if self.current_calendar_month < 1:
            self.current_calendar_month = 12
            self.current_calendar_year -= 1
        self.draw_calendar() # Redraw calendar with new month/year

    def next_month(self):
        """Navigates the calendar to the next month."""
        self.current_calendar_month += 1
        if self.current_calendar_month > 12:
            self.current_calendar_month = 1
            self.current_calendar_year += 1
        self.draw_calendar() # Redraw calendar with new month/year


    def show_hr_management_wrapper(self):
        """
        Displays the HR Management section, defaulting to the Students tab.
        """
        if self.admin_user and self.admin_user.can_manage_users:
            self.show_sub_page(self.hr_notebook) # Show the HR notebook (tabbed interface)
            self.hr_notebook.select(self.hr_students_tab) # Default to the Students tab
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

    def show_comparison(self):
        """
        Informs the user that the comparison feature has been removed.
        """
        messagebox.showinfo("Feature Removed", "The comparison feature has been removed as per request.")
        # Original logic (now commented out):
        # if self.admin_user and self.admin_user.can_view_reports:
        #     self.show_sub_page(self.sub_pages["ComparisonPage"])
        # else:
        #     messagebox.showwarning("Permission Denied", "You do not have permission to view reports for comparison.")

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
            self.parent_controller.logout_user() # Call the main app's logout method

