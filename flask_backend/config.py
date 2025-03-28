import os
import sys
from dotenv import load_dotenv
import random
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.MONGO_URI = os.getenv('MONGO_URI')
        # self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        # self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
        # self.REDIRECT_URI = os.getenv('REDIRECT_URI')

        self.GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
        self.GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
        self.GITHUB_AUTHORIZATION_ENDPOINT = f"https://github.com/login/oauth/authorize?response_type=code&client_id={self.GITHUB_CLIENT_ID}"
        self.GITHUB_TOKEN_ENDPOINT = "https://github.com/login/oauth/access_token"
        self.GITHUB_USER_ENDPOINT = "https://api.github.com/user"

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        # Email settings
        self.EMAIL_HOST = "smtp.gmail.com"  # Use your email provider's SMTP server
        self.EMAIL_PORT = 587
        # self.EMAIL_PORT = 465
        self.EMAIL_USE_TLS = True
        self.EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        self.EMAIL_FROM = os.getenv("EMAIL_FROM")

project_config = Config()