from flask import Flask, render_template, request, redirect, session, jsonify,url_for
from pymongo.mongo_client import MongoClient
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_dance.contrib.github import github
import os
from config import *

from src.github_log import github_blueprint

load_dotenv()

app = Flask(__name__)
app.secret_key = project_config.SECRET_KEY
app.config['MONGO_URI'] = project_config.MONGO_URI
app.config['REDIRECT_URI'] = project_config.REDIRECT_URI

app.register_blueprint(github_blueprint, url_prefix="/login")


client = MongoClient(app.config['MONGO_URI'])
bcrypt = Bcrypt(app)

try:
    database = client.get_database("ai_platform")
    login_db = client.get_database("ai_platform").get_collection("login")
    login_sessions_db = client.get_database("ai_platform").get_collection("login_sessions")
    
    # Check if the collection is empty
    if login_db.count_documents({}) == 0:
        # Insert initial data
        login_db.insert_one({
            'username': 'admin',
            'password': bcrypt.generate_password_hash('admin123').decode('utf-8')
        })
        print("Initialized the login collection with default admin credentials.")
except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)



@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = login_db.find_one({'username': username})

        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            session['username'] = username
            
            login_sessions = login_sessions_db
            login_sessions.insert_one({'username': username})
            
            return redirect('/secured')
        else:
            return "Invalid username or password. <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    res = github.get("/user")

    if res.ok:
        user_data = res.json()
        username = user_data.get('id')
        email = user_data.get('email', '')

        # Check if the GitHub user already exists in the database
        github_users = client.get_database("ai_platform").get_collection("login")
        existing_user = github_users.find_one({'username': username})

        if not existing_user:
            # If the user does not exist, save GitHub user data to the database
            github_users.insert_one({'username': username, 'email': email})

        session['username'] = username
            
        login_sessions = login_sessions_db
        login_sessions.insert_one({'username': username})

        return redirect('/secured')
    else:
        return "Failed to fetch GitHub user data. <a href='/login'>Try again</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        # email = request.form['email']

        users = client.get_database("ai_platform").get_collection("login")
        existing_user = users.find_one({'username': username})

        if existing_user:
            return "Username already exists. <a href='/register'>Try again</a>"

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users.insert_one({'first_name': first_name, 'last_name': last_name, 'username': username, 'password': hashed_password})
        return redirect('/login')
    return render_template('register.html')

@app.route('/secured')
def secured():
    if 'username' in session:
        users = login_db
        user_data = users.find_one({'username': session['username']})

        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')

        return render_template('secured_page.html', first_name=first_name, last_name=last_name)
    else:
        return redirect('/login')
    
@app.route('/logout')
def logout():
    if 'username' in session:
        login_sessions = login_sessions_db
        login_sessions.delete_one({'username': session['username']})

    session.pop('username', None)

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=5000)