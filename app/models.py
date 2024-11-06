from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_photo = db.Column(db.String(255))
    entries = db.relationship('MoodEntry', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class MoodEntry(db.Model):
    __tablename__ = 'mood_entry'

    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(5), nullable=False)
    journal_entry = db.Column(db.Text)
    gratitude = db.Column(db.Text)
    agency = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='entries')

    def __repr__(self):
        return f'<MoodEntry {self.mood} by {self.user.username}>'