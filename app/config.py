import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configurations
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True')
    MAIL_USE_TLS = False  # Since we're using SSL
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.abspath(os.getenv('UPLOAD_FOLDER'))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS').split(','))