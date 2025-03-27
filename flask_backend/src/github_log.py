import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
from urllib.parse import parse_qs
from dotenv import load_dotenv
from config import project_config
from flask_dance.contrib.github import make_github_blueprint

GITHUB_CLIENT_ID = project_config.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = project_config.GITHUB_CLIENT_SECRET
GITHUB_AUTHORIZATION_ENDPOINT = project_config.GITHUB_AUTHORIZATION_ENDPOINT
GITHUB_TOKEN_ENDPOINT = project_config.GITHUB_TOKEN_ENDPOINT
GITHUB_USER_ENDPOINT = project_config.GITHUB_USER_ENDPOINT
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # 允许在 HTTP 上运行 OAuth

github_blueprint = make_github_blueprint(
    client_id=project_config.GITHUB_CLIENT_ID,
    client_secret=project_config.GITHUB_CLIENT_SECRET,
)