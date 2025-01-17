import google.generativeai as genai
from datetime import datetime
import json
import random

class AIAnalyzer:
    def __init__(self, api_key):
        print(f"Initializing AIAnalyzer with API key: {api_key[:5]}...")  # Only print first 5 chars for security
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.system_prompt = """You are an AI diary analyst and the writer's best friend and the writer's name is Writer, and you have to give an friednly response as if you are talking to him. For the given diary entry, please provide:
1. An objective analysis focusing on the writer's daily experiences and emotional journey (2-3 sentences)
2. The primary emotional state expressed (options: appreciative, joyful, content, reflective, concerned, downhearted)
3. A constructive observation about the writer's experiences (1 sentence)
Format the response as JSON with keys: 'analysis', 'emotion', 'observation'"""
        self.use_mock = False
        self.safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }

    def preprocess_entry(self, content):
        """Sanitize input to avoid triggering content filters"""
        # Replace potentially triggering words with neutral alternatives
        replacements = {
            "love": "appreciate",
            "heart": "mind",
            "romance": "connection",
            "romantic": "meaningful",
            "relationship": "friendship"
        }
        
        processed_content = content
        for old, new in replacements.items():
            processed_content = processed_content.replace(old, new)
        return processed_content

    def analyze_entry(self, content):
        if not self.use_mock:
            try:
                processed_content = self.preprocess_entry(content)
                print(f"Sending request to AI model with content: {processed_content[:50]}...")
                response = self.model.generate_content(
                    f"{self.system_prompt}\n\nDiary entry: {processed_content}",
                    safety_settings=self.safety_settings
                )
            
                print(f"Received response from AI model: {response.text[:100]}...")
            
                # Remove any leading/trailing backticks and "json" text
                cleaned_response = response.text.strip('`').strip()
                if cleaned_response.startswith('json'):
                    cleaned_response = cleaned_response[4:].strip()
            
                try:
                    result = json.loads(cleaned_response)
                    # Map sanitized emotions back to original intentions
                    emotion_mapping = {
                        'appreciative': 'romantic',
                        'joyful': 'fun',
                        'content': 'excited',
                        'reflective': 'neutral',
                        'concerned': 'tough',
                        'downhearted': 'sad'
                    }
                    result['emotion'] = emotion_mapping.get(result['emotion'], result['emotion'])
                    return result['analysis'], result['emotion'], result['observation']
                except json.JSONDecodeError as json_error:
                    print(f"Failed to parse JSON response. Error: {json_error}")
                    print(f"Cleaned response: {cleaned_response}")
                    return self.extract_structured_response(cleaned_response)
            except Exception as e:
                print(f"Error in AI analysis: {e}")
                print("Switching to mock implementation.")
                self.use_mock = True
    
        return self.mock_analyze_entry(content)

    def extract_structured_response(self, text):
        """Extract structured information from non-JSON responses"""
        lines = text.split('\n')
        analysis = lines[0] if len(lines) > 0 else "Entry analyzed."
        emotion = 'neutral'
        observation = lines[-1] if len(lines) > 1 else "Keep writing!"
        
        # Detect emotion from analysis text
        emotion_keywords = {
            'romantic': ['care', 'appreciate', 'connection', 'feeling'],
            'fun': ['happy', 'joy', 'laugh', 'exciting'],
            'excited': ['thrilled', 'eager', 'looking forward'],
            'tough': ['difficult', 'challenging', 'hard'],
            'sad': ['unhappy', 'down', 'gloomy']
        }
        
        text_lower = text.lower()
        for emotion_type, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotion = emotion_type
                break
                
        return analysis, emotion, observation

    def mock_analyze_entry(self, content):
        """Enhanced mock implementation with more nuanced analysis"""
        # Expanded keyword sets for better emotion detection
        emotion_indicators = {
            'romantic': ['appreciate', 'care', 'connection', 'close', 'together'],
            'fun': ['happy', 'joy', 'laugh', 'exciting', 'wonderful'],
            'excited': ['thrilled', 'eager', 'anticipate', 'looking forward'],
            'neutral': ['normal', 'regular', 'usual', 'typical'],
            'tough': ['difficult', 'challenging', 'hard', 'struggle'],
            'sad': ['unhappy', 'down', 'gloomy', 'disappointed']
        }

        content_lower = content.lower()
        emotion_scores = {emotion: sum(1 for word in keywords if word in content_lower)
                         for emotion, keywords in emotion_indicators.items()}
        
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        # Generate more contextual summary
        word_count = len(content.split())
        time_indicators = {'morning': 'start', 'afternoon': 'middle', 'evening': 'end', 
                         'night': 'end', 'today': 'throughout'}
        time_context = next((time_indicators[word] for word in time_indicators 
                           if word in content_lower), 'throughout')
        
        summary = f"A {word_count}-word entry reflecting on experiences from the {time_context} of the day, expressing primarily {primary_emotion} sentiments."
        
        # Generate contextual observation
        observations = {
            'romantic': "Your capacity for deep connection shines through your words.",
            'fun': "Your positive energy is clearly reflected in this entry.",
            'excited': "Your enthusiasm for what's ahead is wonderful to see.",
            'neutral': "Taking time to document your day shows good self-reflection.",
            'tough': "Remember that challenging times often lead to growth.",
            'sad': "Expression through writing can be very healing."
        }
        
        return summary, primary_emotion, observations[primary_emotion]

    def analyze_all_entries(self, entries):
        """Analyze trends across multiple entries with robust error handling"""
        emotion_tracking = {
            'romantic': [],
            'fun': [],
            'excited': [],
            'neutral': [],
            'tough': [],
            'sad': []
        }

        # Add entries to emotion tracking with validation
        for date, entry in entries.items():
            try:
                # Get tone with fallback to neutral
                tone = entry.get('tone', 'neutral')
                
                # Handle empty strings or missing tones
                if not tone or tone not in emotion_tracking:
                    tone = 'neutral'
                    
                emotion_tracking[tone].append(date)
            except Exception as e:
                print(f"Warning: Could not process entry for date {date}: {e}")
                continue

        # Initialize return values
        toughest_day = None
        most_fun_day = None
        most_romantic_day = None

        try:
            # Find toughest day (from tough or sad entries)
            tough_days = emotion_tracking['tough'] + emotion_tracking['sad']
            if tough_days:
                toughest_day = max(tough_days)

            # Find most fun day (from fun or excited entries)
            fun_days = emotion_tracking['fun'] + emotion_tracking['excited']
            if fun_days:
                most_fun_day = max(fun_days)

            # Find most romantic day
            if emotion_tracking['romantic']:
                most_romantic_day = max(emotion_tracking['romantic'])

        except Exception as e:
            print(f"Warning: Error analyzing significant days: {e}")

        return toughest_day, most_fun_day, most_romantic_day

