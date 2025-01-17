import os
import tkinter as tk
from dotenv import load_dotenv
from diary_manager import DiaryManager
from ai_analyzer import AIAnalyzer
from app_ui import DiaryApp
from ttkbootstrap.dialogs import Messagebox  # Changed from tktooltip
import logging

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get the Gemini API key from environment variables
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        # Show warning dialog about missing API key
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        Messagebox.show_warning(
            "API Key Missing", 
            "Please get your API key from https://makersuite.google.com/app/apikey\n"
            "and add it to your .env file as GEMINI_API_KEY=your_key_here"
        )
        return

    try:
        # Initialize components
        diary_manager = DiaryManager()
        ai_analyzer = AIAnalyzer(api_key)

        # Create application
        app = DiaryApp(diary_manager, ai_analyzer)
        
        # Only run mainloop if app window exists and is not destroyed
        if hasattr(app, 'winfo_exists') and app.winfo_exists():
            app.focus_force()
            app.mainloop()
            
    except Exception as e:
        logging.error(f"Application error: {e}")
        try:
            root = tk.Tk()
            root.withdraw()
            Messagebox.show_error(f"Error: {str(e)}")
            root.destroy()
        except:
            pass  # If even showing error fails, just exit

if __name__ == "__main__":
    main()

