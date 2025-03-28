# AI-Powered Personal Diary

A modern diary application that leverages Google's Gemini AI to analyze your entries and provide emotional insights. Write and save daily diary entries, view mood trends, and gain valuable emotional feedback through a sleek, dark-themed interface.

## Features

- 📝 Write and save daily diary entries
- 🤖 AI-powered analysis of your entries
- 📅 Calendar view with mood indicators
- 📊 Mood analysis and trends
- 🎨 Modern dark theme interface

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key

## Getting Started

1. Get your Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the API key

2. Set up your environment:
   - Create a `.env` file in the project root
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

3. Default Login Credentials:
   - Username: `user`
   - Password: `password`
   
   You can change these in `ui_components.py`

## Installation

1. Clone the repository
```bash
git clone https://github.com/n0taaryash/SoulScript.git
cd SoulScript
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

4. Set up your API key
Create a `.env` file in the project root with:
```
GEMINI_API_KEY=your_api_key_here
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the main script:
```bash
python main.py
```

3. Login with these credentials:
   - Username: `user`
   - Password: `password`

## Dependencies

- ttkbootstrap
- google-generativeai
- python-dotenv
- matplotlib

## Project Structure

```
SoulScript/
│
├── main.py              # Application entry point
├── app_ui.py           # Main UI components
├── ui_components.py    # Reusable UI widgets
├── diary_manager.py    # Entry management
├── ai_analyzer.py      # AI analysis integration
├── mood_analytics.py   # Analytics visualization
└── diary_entries.json  # Data storage
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Aaryash - [GitHub Profile](https://github.com/n0taaryash)
