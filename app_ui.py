import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from ui_components import CalendarWidget, EntryEditor, EntryDisplay, AnalysisSummary, LoginWindow
from mood_analytics import AnalyticsDashboard
import logging
import tkinter as tk

class DiaryApp(ttk.Window):
    def __init__(self, diary_manager, ai_analyzer):
        # Initialize the main window first
        super().__init__(themename="darkly")
        self.withdraw()  # Hide main window until login is successful
        
        self.diary_manager = diary_manager
        self.ai_analyzer = ai_analyzer
        self._save_in_progress = False
        self._want_to_close = False
        
        # Handle login
        if self._handle_login():
            self.title("Gen Z Diary")
            self.geometry("1200x800")
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.create_widgets()
            self.create_menu()
            self.deiconify()  # Show window after setup
        else:
            self.destroy()
            return
            
    def _handle_login(self):
        """Handle login and return True if successful"""
        try:
            login_window = LoginWindow(self)
            self.wait_window(login_window)
            return login_window.is_authenticated
        except Exception as e:
            logging.error(f"Login error: {e}")
            return False

    # Remove the login method as it's no longer needed
    # def login(self):
    #     pass

    def create_widgets(self):
        logging.info("Creating main widgets")
        # Main container with padding
        container = ttk.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=YES)

        # Left panel (40% of width)
        left_panel = ttk.Frame(container)
        left_panel.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Right panel (60% of width)
        right_panel = ttk.Frame(container)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(10, 0))

        # Left panel widgets
        logging.info("Creating calendar widget")
        calendar_frame = ttk.LabelFrame(left_panel, text="Calendar", padding=10)
        calendar_frame.pack(fill=X, pady=(0, 10))
        
        self.calendar = CalendarWidget(calendar_frame)
        self.calendar.pack(fill=X)
        self.calendar.set_callback(self.on_date_selected)

        logging.info("Creating entry editor")
        editor_frame = ttk.LabelFrame(left_panel, text="New Entry", padding=10)
        editor_frame.pack(fill=BOTH, expand=YES)
        
        self.entry_editor = EntryEditor(editor_frame)
        self.entry_editor.pack(fill=BOTH, expand=YES, pady=(0, 10))

        save_button = ttk.Button(editor_frame, text="Save Entry", 
                               command=self.save_entry, 
                               bootstyle="success-outline",
                               width=20)
        save_button.pack(pady=(0, 10))

        # Right panel widgets
        logging.info("Creating entry display")
        display_frame = ttk.LabelFrame(right_panel, text="Current Entry", padding=10)
        display_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        self.entry_display = EntryDisplay(display_frame)
        self.entry_display.pack(fill=BOTH, expand=YES)

        logging.info("Creating analysis summary")
        analysis_frame = ttk.LabelFrame(right_panel, text="Analysis", padding=10)
        analysis_frame.pack(fill=X)
        
        self.analysis_summary = AnalysisSummary(analysis_frame)
        self.analysis_summary.pack(fill=X)

        self.update_analysis_summary()
        logging.info("All widgets created successfully")
        
    def create_menu(self):
        logging.info("Creating menu")
        menu_bar = ttk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = ttk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit)

        view_menu = ttk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Analytics", command=self.show_analytics)

        help_menu = ttk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def on_date_selected(self, date):
        logging.info(f"Date selected: {date}")
        entry = self.diary_manager.get_entry(date)
        if entry:
            self.entry_display.display_entry(date, entry['content'], entry['summary'], entry['tone'])
        else:
            self.entry_display.display_entry(date, "No entry for this date.", "", "")

    def save_entry(self):
        if self._save_in_progress:  # Prevent multiple saves
            return
            
        self._save_in_progress = True
        content = self.entry_editor.get_content()
        
        try:
            if not content:
                Messagebox.show_warning("Please enter some content for your diary entry.")
                self._save_in_progress = False
                return

            today = datetime.now().date()
            if self.diary_manager.is_valid_date(today):
                # First save the entry
                self.diary_manager.add_entry(today, content)
                self.update()
                
                # Do AI analysis
                logging.info(f"Analyzing entry: {content[:50]}...")
                try:
                    summary, tone, comment = self.ai_analyzer.analyze_entry(content)
                    logging.info(f"Analysis complete - Summary: {summary[:50]}, Tone: {tone}")
                    
                    # Update entry with analysis
                    self.diary_manager.update_entry_analysis(today, summary, tone, comment)
                    
                    def update_ui():
                        try:
                            # Update UI elements
                            self.entry_display.display_entry(today, content, summary, tone, comment)
                            self.entry_editor.set_content("")
                            self.update_analysis_summary()
                            self.calendar.update_tooltips(self.diary_manager.get_all_entries())
                            Messagebox.show_info("Entry saved and analyzed successfully!")
                        finally:
                            self._save_in_progress = False
                    
                    # Schedule UI update for after current event
                    self.after(100, update_ui)
                    
                except Exception as analysis_error:
                    logging.error(f"Analysis error: {analysis_error}")
                    self._save_in_progress = False
                    Messagebox.show_warning(
                        "Entry saved but analysis failed. Please try refreshing the app."
                    )
            else:
                self._save_in_progress = False
                Messagebox.show_warning("You can only add entries for today or yesterday.")
                
        except Exception as e:
            self._save_in_progress = False
            logging.error(f"Save error: {e}")
            Messagebox.show_error(f"Error saving entry: {str(e)}")

    def update_analysis_summary(self):
        logging.info("Updating analysis summary")
        entries = self.diary_manager.get_all_entries()
        toughest_day, most_fun_day, most_romantic_day = self.ai_analyzer.analyze_all_entries(entries)
        self.analysis_summary.update_analysis(toughest_day, most_fun_day, most_romantic_day)

    def show_about(self):
        Messagebox.show_info("AI Diary\nVersion 1.0\n\nA cool diary app for Aaryash!")

    def show_analytics(self):
        entries = self.diary_manager.get_all_entries()
        AnalyticsDashboard(self, entries)
        
    def on_closing(self):
        """Handle window closing event"""
        if self._save_in_progress:
            Messagebox.show_warning("Please wait for the current operation to complete.")
            return
            
        if not self._want_to_close:
            self._want_to_close = True
            if Messagebox.show_question("Do you want to quit?", "Confirm Exit"):
                try:
                    logging.info("Closing application")
                    self.destroy()  # Changed from quit() to destroy()
                except Exception as e:
                    logging.error(f"Error while closing: {e}")
                    self.destroy()
            else:
                self._want_to_close = False

