import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class AnalyticsDashboard(ttk.Toplevel):
    def __init__(self, parent, entries):
        super().__init__(parent)
        self.title("Mood Trends")
        self.geometry("600x400")
        
        # Set minimum size
        self.minsize(400, 300)
        
        # Center the window
        self.center_window()
        
        self.entries = entries
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        # Create main container with padding
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=YES)
        
        # Create and pack the figure
        fig, ax = plt.subplots(figsize=(8, 5))
        self.plot_mood_trends(ax)
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=BOTH, expand=YES)

    def plot_mood_trends(self, ax):
        moods = [entry['tone'] for entry in self.entries.values()]
        mood_counts = {mood: moods.count(mood) for mood in set(moods)}
        
        # Create bar chart
        bars = ax.bar(mood_counts.keys(), mood_counts.values())
        
        # Customize the chart
        ax.set_title("Mood Distribution", pad=20, fontsize=12, fontweight='bold')
        ax.set_xlabel("Mood", labelpad=10)
        ax.set_ylabel("Count", labelpad=10)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        # Adjust layout
        plt.tight_layout()

# Ensure the AnalyticsDashboard class is available for import
if __name__ == "__main__":
    print("AnalyticsDashboard class is defined and ready for use.")

