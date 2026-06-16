import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-1293847')
    
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database Configuration
    # Defaults to local SQLite database in parent folder of app
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'app.db')}"
    )
    # Correct URL prefix if it comes from environments like Heroku
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI API Credentials
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # API Integration flags
    SCHEDULER_API_ENABLED = True
    
    # Notification Credentials
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
    EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER')
    EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT', 587))
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
