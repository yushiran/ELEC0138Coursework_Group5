from flask import Flask, render_template, request, redirect, session, jsonify,url_for
from pymongo.mongo_client import MongoClient
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_dance.contrib.github import github
import os
import openai 
from datetime import datetime
from bson.objectid import ObjectId
import json

from config import *

from src.github_log import github_blueprint
from src.gpt import get_gpt_response

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
    chats_db = client.get_database("ai_platform").get_collection("chats")  # 新增聊天记录集合

    
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

@app.route('/login/github/authorized')
def github_authorized_callback():
    print(f"GitHub 授权状态: {github.authorized}")
    if github.authorized:
        print("用户已授权，重定向到 /secured")
        return redirect('/secured')
    print("用户未授权，重定向到 /login")
    return redirect('/login')

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    res = github.get("/user")
    if res.status_code == 401:
        # 令牌失效，强制重新授权
        print("令牌已失效，重新授权")
        session.clear()  # 清除会话数据
        return redirect(url_for("github.login"))  # 重定向回 GitHub 登录

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

        # 如果是通过GitHub登录的用户，可能没有first_name和last_name
        first_name = user_data.get('first_name', 'User')
        last_name = user_data.get('last_name', '')
        
        # GitHub用户可能只有用户名
        if first_name == 'User' and 'email' in user_data:
            # 如果有email，可以显示email的用户名部分
            email = user_data.get('email', '')
            if email:
                first_name = email.split('@')[0]

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


# 修改聊天路由，添加聊天历史存储功能
@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    chat_id = data.get('chat_id', None)

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # 调用 GPT 模型获取回复
        assistant_message = get_gpt_response(user_message, chat_history)
        
        # 更新或创建聊天记录
        now = datetime.utcnow()
        
        if chat_id:
            # 更新现有聊天
            chat = chats_db.find_one({'_id': ObjectId(chat_id)})
            if not chat:
                return jsonify({'error': 'Chat not found'}), 404
                
            # 将新消息添加到聊天记录
            chats_db.update_one(
                {'_id': ObjectId(chat_id)},
                {
                    '$push': {
                        'messages': {
                            '$each': [
                                {'role': 'user', 'content': user_message, 'timestamp': now},
                                {'role': 'assistant', 'content': assistant_message, 'timestamp': now}
                            ]
                        }
                    },
                    '$set': {'updated_at': now}
                }
            )
        else:
            # 创建新聊天
            chat_id = str(ObjectId())
            chats_db.insert_one({
                '_id': ObjectId(chat_id),
                'username': session['username'],
                'messages': [
                    {'role': 'user', 'content': user_message, 'timestamp': now},
                    {'role': 'assistant', 'content': assistant_message, 'timestamp': now}
                ],
                'created_at': now,
                'updated_at': now
            })
            
        return jsonify({
            'message': assistant_message,
            'chat_id': chat_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加获取聊天历史的路由
@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        username = session['username']
        chats = chats_db.find({'username': username}).sort('updated_at', -1)  # 按更新时间降序排序
        
        chat_history = []
        for chat in chats:
            # 获取第一条用户消息作为标题
            first_message = "New Chat"
            if len(chat['messages']) > 0:
                for msg in chat['messages']:
                    if msg['role'] == 'user':
                        first_message = msg['content'][:30] + "..." if len(msg['content']) > 30 else msg['content']
                        break
            
            chat_history.append({
                'chat_id': str(chat['_id']),
                'title': first_message,
                'updated_at': chat['updated_at'].strftime("%Y-%m-%d %H:%M")
            })
            
        return jsonify({'chats': chat_history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加获取特定聊天记录的路由
@app.route('/get_chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        chat = chats_db.find_one({'_id': ObjectId(chat_id), 'username': session['username']})
        if not chat:
            return jsonify({'error': 'Chat not found or unauthorized'}), 404
            
        return jsonify({
            'chat_id': str(chat['_id']),
            'messages': json.loads(json.dumps(chat['messages'], default=str))  # 处理日期序列化
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加创建新聊天的路由
@app.route('/new_chat', methods=['POST'])
def new_chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        now = datetime.utcnow()
        chat_id = str(ObjectId())
        
        chats_db.insert_one({
            '_id': ObjectId(chat_id),
            'username': session['username'],
            'messages': [],
            'created_at': now,
            'updated_at': now
        })
        
        return jsonify({'chat_id': chat_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)