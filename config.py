import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Key for securely signing the session cookie
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

    # Settings for secure cookies on a deployed server
    SESSION_COOKIE_SECURE = True
    SERVER_NAME = os.environ.get('SERVER_URL')