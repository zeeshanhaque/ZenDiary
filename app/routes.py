from flask import Blueprint, render_template, redirect, request, flash, url_for, send_file, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from io import BytesIO
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from flask_mail import Message
from . import db, mail
from .models import User, MoodEntry
from .forms import RegistrationForm, LoginForm, MoodEntryForm
from .utils import emoji_set, suggestions_dict
from .utils import filter_nouns, calculate_average_mood_for_month, get_mood_class, get_mood_background_color, get_styled_suggestions, save_profile_photo

main = Blueprint('main', __name__)


@main.route("/")
@login_required
def index():
    """Home page route showing recent mood entries."""
    mood_entries = MoodEntry.query.filter_by(user=current_user)\
        .order_by(MoodEntry.timestamp.desc()).all()
    return render_template("index.html", 
                         mood_entries=mood_entries,
                         emoji_set=emoji_set)


@main.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    
    if request.method == "GET":
        session.pop('_flashes', None)
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email_address")
        password1 = request.form.get("password")
        password2 = request.form.get("confirm_password")
        profile_photo = request.files.get("profile_photo")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists.", category="error")
        elif len(username) < 2:
            flash("Username must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            filename = None
            if profile_photo:
                filename = save_profile_photo(profile_photo)
                if not filename:
                    flash("Invalid file type or upload error.", category="error")
                    return redirect(url_for("main.register"))
            
            hashed_password = generate_password_hash(password1, method="sha256")
            new_user = User(username=username, email=email, password=hashed_password, profile_photo=filename)
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for("main.index"))

    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Use check_password_hash to verify the password
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Login unsuccessful. Please check your username and password.", "danger")
    return render_template("login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main.route("/add_entry", methods=["GET", "POST"])
@login_required
def add_entry():
    """Route for adding new mood entries."""
    form = MoodEntryForm()
    if request.method == "POST":
        try:
            indian_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
            new_entry = MoodEntry(
                mood=request.form.get('mood'),
                journal_entry=request.form.get('journal_entry'),
                gratitude=request.form.get('gratitude'),
                agency=request.form.get('agency'),
                user=current_user,
                timestamp=indian_time,
            )
            db.session.add(new_entry)
            db.session.commit()
            flash("Entry added successfully", "success")
            return redirect(url_for("main.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding entry: {str(e)}", "danger")

    return render_template("add_entry.html", form=form)


@main.route('/analytics')
@login_required
def analytics():
    """Route for displaying mood analytics."""
    try:
        mood_entries = MoodEntry.query.filter_by(user=current_user).all()
        
        if not mood_entries:
            flash("No mood entries found. Please add some entries first.", "info")
            return render_template('analytics.html', mood_entries=[], formatted_timestamps=[], average_monthly_mood=None, suggestions=suggestions_dict, emoji_set=emoji_set)

        formatted_timestamps = [entry.timestamp.strftime('%d/%m') for entry in mood_entries]
        
        current_date = datetime.utcnow()
        average_monthly_mood = calculate_average_mood_for_month(current_user, current_date.year, current_date.month)
        
        mood_background_color = get_mood_background_color(average_monthly_mood)
        mood_class = get_mood_class(average_monthly_mood)
        styled_suggestions = get_styled_suggestions(mood_class, suggestions_dict)

        return render_template('analytics.html', mood_entries=mood_entries, formatted_timestamps=formatted_timestamps, average_monthly_mood=average_monthly_mood, mood_background_color=mood_background_color, mood_class=mood_class, suggestions=suggestions_dict, emoji_set=emoji_set, styled_suggestions=styled_suggestions)
    except Exception as e:
        print(f"Error in analytics route: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Error generating analytics: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main.route('/wordcloud')
@login_required
def wordcloud():
    """Route for generating word cloud from gratitude entries."""
    try:
        mood_entries = MoodEntry.query.filter_by(user=current_user).all()
        text = ' '.join(
            ' '.join(filter_nouns(entry.gratitude.lower())) 
            for entry in mood_entries 
            if entry.gratitude
        )
        
        wordcloud = WordCloud(
            width=720,
            height=360,
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0)
        img_bytes.seek(0)
        plt.close()
        
        return send_file(img_bytes, mimetype='image/png')
    except Exception as e:
        flash(f"Error generating word cloud: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main.route('/wordcloud_page')
@login_required
def wordcloud_page():
    """Page for displaying the word cloud."""
    return render_template('wordcloud_page.html')

def send_monthly_report(user, year, month):
    """Helper function to send monthly mood reports via email."""
    try:
        average_mood = calculate_average_mood_for_month(user, year, month)
        if average_mood:
            msg = Message(
                f"Monthly Mood Report - {month}/{year}",
                recipients=[user.email]
            )
            
            msg.body = f"""
            Hello {user.username},

            Here's your mood summary for {month}/{year}:
            Average Mood Score: {average_mood}/5 {emoji_set.get(round(average_mood), '')}

            Keep tracking your moods and emotions!
            Best regards,
            ZenDiary Team
            """
            
            mood_entries = MoodEntry.query.filter_by(user_id=user.id).all()
            if mood_entries:
                text = ' '.join(entry.journal_entry for entry in mood_entries if entry.journal_entry)
                if text:
                    wordcloud = WordCloud(width=720, height=360).generate(text)
                    img_bytes = BytesIO()
                    wordcloud.to_image().save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    msg.attach('wordcloud.png', 'image/png', img_bytes.getvalue())
            
            mail.send(msg)
            return True
    except Exception as e:
        print(f"Error sending monthly report: {str(e)}")
        return False
