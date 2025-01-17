import tkinter as tk
from tkinter import END
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, timedelta
import calendar
import logging
# Remove tooltip import and use idlelib's tooltip instead
from idlelib.tooltip import Hovertip

class CalendarWidget(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.date = datetime.now()
        self.callback = None
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 10))

        prev_button = ttk.Button(header_frame, text="<", command=self.prev_month, 
                               bootstyle="info-outline", width=3)
        prev_button.pack(side=LEFT, padx=5)

        self.header = ttk.Label(header_frame, text=self.date.strftime("%B %Y"), 
                              font=("Helvetica", 12, "bold"))
        self.header.pack(side=LEFT, expand=YES)

        next_button = ttk.Button(header_frame, text=">", command=self.next_month, 
                               bootstyle="info-outline", width=3)
        next_button.pack(side=RIGHT, padx=5)

        self.calendar = ttk.Frame(self)
        self.calendar.pack(fill=X)

        self.update_calendar()

    def create_date_button(self, day, week_num, day_num):
        btn = ttk.Button(self.calendar, text=str(day), bootstyle="info-outline",
                        command=lambda d=day: self.on_date_click(d),
                        width=4)
        btn.grid(row=week_num, column=day_num, padx=2, pady=2)
    
        if day == datetime.now().day and self.date.month == datetime.now().month:
            btn.configure(bootstyle="info")
    
        return btn

    def update_calendar(self):
        for widget in self.calendar.winfo_children():
            widget.destroy()

        cal = calendar.monthcalendar(self.date.year, self.date.month)

        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for i, day in enumerate(days):
            ttk.Label(self.calendar, text=day, font=("Roboto", 10)).grid(
                row=0, column=i, padx=2, pady=(0, 5))

        self.date_buttons = {}
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = self.create_date_button(day, week_num, day_num)
                    self.date_buttons[day] = btn

        self.header.config(text=self.date.strftime("%B %Y"))

    def update_tooltips(self, entries):
        # Clear existing tooltips
        if hasattr(self, '_tooltips'):
            for tip in self._tooltips:
                tip.destroy()
        
        self._tooltips = []
        
        for day, btn in self.date_buttons.items():
            date_str = f"{self.date.year}-{self.date.month:02d}-{day:02d}"
            if date_str in entries:
                entry = entries[date_str]
                tooltip_text = f"Mood: {entry['tone']}\n{entry['summary'][:50]}..."
            else:
                tooltip_text = "No entry"
            
            tip = Hovertip(btn, tooltip_text, hover_delay=500)
            self._tooltips.append(tip)

    def prev_month(self):
        self.date = self.date.replace(day=1) - timedelta(days=1)
        self.update_calendar()

    def next_month(self):
        self.date = self.date.replace(day=28) + timedelta(days=5)
        self.date = self.date.replace(day=1)
        self.update_calendar()

    def on_date_click(self, day):
        selected_date = self.date.replace(day=day)
        if self.callback:
            self.callback(selected_date)

    def set_callback(self, callback):
        self.callback = callback

class EntryEditor(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        self.text_area = ttk.Text(self, wrap=WORD, height=8)
        self.text_area.pack(fill=BOTH, expand=YES)
        
        # Add placeholder text
        self.text_area.insert("1.0", "Write your thoughts here...")
        self.text_area.bind("<FocusIn>", self.clear_placeholder)
        self.text_area.bind("<FocusOut>", self.add_placeholder)

    def clear_placeholder(self, event):
        if self.text_area.get("1.0", "end-1c") == "Write your thoughts here...":
            self.text_area.delete("1.0", END)

    def add_placeholder(self, event):
        if not self.text_area.get("1.0", "end-1c").strip():
            self.text_area.insert("1.0", "Write your thoughts here...")

    def get_content(self):
        content = self.text_area.get("1.0", END).strip()
        return "" if content == "Write your thoughts here..." else content

    def set_content(self, content):
        self.text_area.delete("1.0", END)
        self.text_area.insert(END, content)

class EntryDisplay(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # Date header
        self.date_label = ttk.Label(self, text="", font=("Helvetica", 12, "bold"))
        self.date_label.pack(fill=X, pady=(0, 10))

        # Entry content
        content_frame = ttk.LabelFrame(self, text="Content", padding=5)
        content_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        self.content_text = ttk.Text(content_frame, wrap=WORD, height=6, state="disabled")
        self.content_text.pack(fill=BOTH, expand=YES)

        # AI Analysis
        analysis_frame = ttk.LabelFrame(self, text="AI Analysis", padding=5)
        analysis_frame.pack(fill=X)
        
        self.summary_label = ttk.Label(analysis_frame, text="", wraplength=400)
        self.summary_label.pack(fill=X, pady=2)
        
        self.tone_label = ttk.Label(analysis_frame, text="")
        self.tone_label.pack(fill=X, pady=2)

        self.comment_label = ttk.Label(analysis_frame, text="", wraplength=400,
                                     font=("Helvetica", 10, "italic"))
        self.comment_label.pack(fill=X, pady=2)

    def display_entry(self, date, content, summary="", tone="", comment=""):
        self.date_label.config(text=date.strftime("%B %d, %Y"))
        
        self.content_text.config(state="normal")
        self.content_text.delete("1.0", END)
        self.content_text.insert(END, content)
        self.content_text.config(state="disabled")

        self.summary_label.config(text=f"Summary: {summary}")
        self.tone_label.config(text=f"Tone: {tone}")
        self.comment_label.config(text=f"AI Comment: {comment}")

class AnalysisSummary(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        self.toughest_day_label = ttk.Label(self, text="", font=("Helvetica", 11))
        self.toughest_day_label.pack(fill=X, pady=2)

        self.most_fun_day_label = ttk.Label(self, text="", font=("Helvetica", 11))
        self.most_fun_day_label.pack(fill=X, pady=2)

        self.most_romantic_day_label = ttk.Label(self, text="", font=("Helvetica", 11))
        self.most_romantic_day_label.pack(fill=X, pady=2)

    def update_analysis(self, toughest_day, most_fun_day, most_romantic_day):
        self.toughest_day_label.config(text=f"Toughest day: {toughest_day}")
        self.most_fun_day_label.config(text=f"Most fun day: {most_fun_day}")
        self.most_romantic_day_label.config(text=f"Most romantic day: {most_romantic_day}")

class LoginWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login")
        self.geometry("300x150")
        self.resizable(False, False)
        
        self.is_authenticated = False
        self.grab_set()  # Make window modal
        
        # Center the window
        self.center_window()
        
        self.create_widgets()
        
        # Focus on username entry
        self.username_entry.focus_set()

    def center_window(self):
        # Center window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky=W, pady=5)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, sticky=EW, pady=5)

        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=W, pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=EW, pady=5)

        login_button = ttk.Button(main_frame, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Changed from personal credentials to default ones
        if username == "user" and password == "password":
            logging.info("User authenticated successfully")
            self.is_authenticated = True
            self.grab_release()  # Release grab before destroying
            self.destroy()
        else:
            logging.warning("Invalid login attempt")
            Messagebox.show_error("Invalid username or password")

