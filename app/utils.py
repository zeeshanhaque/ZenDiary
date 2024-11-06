from flask import current_app
from .models import User, MoodEntry
from sqlalchemy.sql import func
from nltk import pos_tag, word_tokenize
import random
from werkzeug.utils import secure_filename
import os


emoji_set = {
    1: '😢',
    2: '😐',
    3: '😊',
    4: '😄',
    5: '😍',
}

suggestions_dict = {
    'Poor': ['Consider talking to a friend or family member for support.',
             'Take a short walk in nature.',
             'Try deep breathing exercises.'],
    'Fair': ['Engage in a hobby or activity you enjoy.',
             'Plan a relaxing weekend getaway.',
             'Practice mindfulness meditation.'],
    'Good': ['Maintain your positive habits.',
             'Explore new challenges to stay engaged.',
             'Connect with others for social activities.'],
    'Excellent': ['Celebrate your achievements.',
                  'Set new goals for personal growth.',
                  'Continue prioritizing self-care.']
}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_profile_photo(photo):
    """Helper function to validate and save profile photo."""
    if allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
        filename = secure_filename(photo.filename)
        try:
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return filename
        except Exception as e:
            current_app.logger.error(f"Error saving profile photo: {e}")
            return None
    return None


def calculate_average_mood_for_month(user, year, month):
    """Helper function to calculate average mood for a given month."""
    try:
        mood_entries = MoodEntry.query.filter_by(user_id=user.id).filter(
            func.extract('year', MoodEntry.timestamp) == year,
            func.extract('month', MoodEntry.timestamp) == month
        ).all()
        
        print(f"Found {len(mood_entries)} entries for {month}/{year}")
        
        if mood_entries:
            total_score = sum(int(entry.mood) for entry in mood_entries)
            average_score = round(total_score / len(mood_entries), 1)
            print(f"Calculated average score: {average_score}")
            return average_score
        print("No entries found for the current month")
        return None
    except Exception as e:
        print(f"Error calculating average mood: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    

def filter_nouns(text):
    """Helper function to extract nouns from text."""
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    nouns = [word for word, pos in pos_tags if pos.startswith('N')]
    return nouns


def get_mood_background_color(average_mood):
    if average_mood is None:
        return 'black'
    elif 1 <= average_mood <= 2:
        return 'red'
    elif 2 < average_mood <= 3:
        return 'orange'
    elif 3 < average_mood <= 4:
        return 'yellow'
    elif 4 < average_mood <= 5:
        return 'green'
    return 'black'


def get_mood_class(average_mood):
    if average_mood is None:
        return 'Unknown'
    elif average_mood <= 2:
        return 'Poor'
    elif 2 < average_mood <= 3:
        return 'Fair'
    elif 3 < average_mood <= 4:
        return 'Good'
    elif 4 < average_mood <= 5:
        return 'Excellent'
    

colors = ['#e97e40', '#a5d1e7', '#f4dd65', '#bb3be7', '#88bb55', '#ea4335', '#558069']
widths = [450, 500, 550, 600, 650]

def get_styled_suggestions(mood_class, suggestions_dict):
    suggestions = suggestions_dict.get(mood_class, [])
    styled_suggestions = [
        {
            'text': suggestion,
            'color': random.choice(colors),
            'width': random.choice(widths)
        }
        for suggestion in suggestions
    ]
    return styled_suggestions