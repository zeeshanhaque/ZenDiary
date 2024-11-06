from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from .config import Config
import os
import nltk
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
scheduler = BackgroundScheduler()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    csrf.init_app(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    mail.init_app(app)

    # Initialize scheduler
    if not scheduler.running:
        scheduler.start()

    # Register blueprints
    from .routes import main
    app.register_blueprint(main, url_prefix='/')

    # Create tables within app context
    with app.app_context():
        db.create_all()

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app