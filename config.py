import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Use MySQL if provided, otherwise fallback to SQLite for easy development
    mysql_url = os.getenv('DATABASE_URL', '')
    if mysql_url and 'mysql' in mysql_url:
        SQLALCHEMY_DATABASE_URI = mysql_url
    else:
        # Create a local sqlite file if no mysql is found
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.getcwd(), 'data', 'decision_ai.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data', 'uploads')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Groq configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
