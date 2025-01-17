import json
from datetime import datetime, timedelta

class DiaryManager:
    def __init__(self, filepath='diary_entries.json'):
        self.filepath = filepath
        self.entries = self.load_entries()

    def load_entries(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_entries(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.entries, f, indent=2)

    def is_valid_date(self, date):
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        return date in [today, yesterday]

    def add_entry(self, date, content):
        if self.is_valid_date(date):
            date_str = date.strftime('%Y-%m-%d')
            self.entries[date_str] = {
                'content': content,
                'summary': '',
                'tone': '',
                'comment': ''
            }
            self.save_entries()
        else:
            raise ValueError("Entries can only be added for today or yesterday.")

    def get_entry(self, date):
        date_str = date.strftime('%Y-%m-%d')
        return self.entries.get(date_str)

    def get_all_entries(self):
        return self.entries

    def update_entry_analysis(self, date, summary, tone, comment=""):
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.entries:
            self.entries[date_str]['summary'] = summary
            self.entries[date_str]['tone'] = tone
            self.entries[date_str]['comment'] = comment
            self.save_entries()
        else:
            raise ValueError("Entry not found for the specified date.")

    def delete_entry(self, date):
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.entries:
            del self.entries[date_str]
            self.save_entries()
        else:
            raise ValueError("Entry not found for the specified date.")

