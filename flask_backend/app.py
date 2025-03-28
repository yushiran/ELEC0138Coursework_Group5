from flask import Flask, render_template, request, redirect, session, jsonify,url_for
from werkzeug.utils import secure_filename
from pymongo.mongo_client import MongoClient
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_dance.contrib.github import github
import os
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import json
from bson.binary import Binary
import io
import secrets

from config import *

from src.github_log import github_blueprint
from src.gpt import get_gpt_response
from src.file_edit import allowed_file, extract_text_from_file
from src.email import generate_verification_code, send_verification_email, send_password_reset_email
from src.login_limiit import update_login_attempts

load_dotenv()

app = Flask(__name__)
app.secret_key = project_config.SECRET_KEY
app.config['MONGO_URI'] = project_config.MONGO_URI
# app.config['REDIRECT_URI'] = project_config.REDIRECT_URI

app.register_blueprint(github_blueprint, url_prefix="/login")

client = MongoClient(app.config['MONGO_URI'])
bcrypt = Bcrypt(app)

try:
    database = client.get_database("ai_platform")
    login_db = client.get_database("ai_platform").get_collection("login")
    login_sessions_db = client.get_database("ai_platform").get_collection("login_sessions")
    chats_db = client.get_database("ai_platform").get_collection("chats")  # 新增聊天记录集合
    login_verification_db = client.get_database("ai_platform").get_collection("login_verifications")
    verification_db = client.get_database("ai_platform").get_collection("verification_codes")
    login_attempts_db = client.get_database("ai_platform").get_collection("login_attempts")

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

# 添加验证码发送路由
@app.route('/send_login_code', methods=['POST'])
def send_login_code():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 检查账户是否被锁定
        login_attempt = login_attempts_db.find_one({'username': username})
        if login_attempt and login_attempt.get('locked_until'):
            locked_until = login_attempt.get('locked_until')
            if datetime.utcnow() < locked_until:
                # 计算剩余锁定时间
                remaining_time = int((locked_until - datetime.utcnow()).total_seconds() / 60)
                return jsonify({
                    'success': False, 
                    'error': f'账户已被锁定，请在{remaining_time}分钟后再试'
                }), 403
            else:
                # 锁定时间已过，重置登录尝试
                login_attempts_db.update_one(
                    {'username': username},
                    {'$set': {'failed_attempts': 0, 'locked_until': None}}
                )
        
        # 验证用户名和密码
        user = login_db.find_one({'username': username})
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 400
            
        if not bcrypt.check_password_hash(user['password'], password):
            # 增加失败登录次数并可能锁定账户
            update_login_attempts(username, login_attempts_db=login_attempts_db,success=False)
            
            # 再次查询以获取最新的锁定状态
            updated_attempt = login_attempts_db.find_one({'username': username})
            if updated_attempt and updated_attempt.get('locked_until') and datetime.utcnow() < updated_attempt.get('locked_until'):
                # 账户被锁定，返回锁定信息
                remaining_time = int((updated_attempt['locked_until'] - datetime.utcnow()).total_seconds() / 60)
                return jsonify({
                    'success': False, 
                    'error': f'密码错误，账户已被锁定，请在{remaining_time}分钟后再试'
                }), 403
            else:
                # 账户未锁定，返回普通密码错误信息
                return jsonify({'success': False, 'error': '密码错误'}), 400
        
        # 登录成功，重置失败次数
        update_login_attempts(username,login_attempts_db=login_attempts_db, success=True)
        
        # 生成验证码
        verification_code = generate_verification_code()
        
        # 保存验证码到数据库，设置10分钟有效期
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        
        # 创建或更新验证码记录
        login_verification_db.update_one(
            {'username': username},
            {'$set': {
                'verification_code': verification_code,
                'expires_at': expiration_time
            }},
            upsert=True
        )
        
        # 发送验证码邮件
        email = user.get('email')
        if not email:
            return jsonify({'success': False, 'error': '用户没有关联的邮箱地址'}), 400
            
        # 使用用户名作为姓名发送邮件
        if send_verification_email(email, verification_code, username):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '发送邮件失败，请稍后再试'}), 500
            
    except Exception as e:
        print(f"Error in send_login_code: {str(e)}")
        return jsonify({'success': False, 'error': '服务器错误'}), 500

# 修改登录路由，增加验证码验证
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        verification_code = request.form.get('verification_code')

        # 检查账户是否被锁定
        login_attempt = login_attempts_db.find_one({'username': username})
        if login_attempt and login_attempt.get('locked_until'):
            locked_until = login_attempt.get('locked_until')
            if datetime.utcnow() < locked_until:
                remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60)
                return f"账户已被锁定，请在{remaining_minutes}分钟后再试 <a href='/login'>返回</a>"
        
        if not verification_code:
            return "请输入验证码 <a href='/login'>返回</a>"
            
        # 验证用户名和密码
        user = login_db.find_one({'username': username})
        if not user:
            return "用户不存在 <a href='/login'>返回</a>"
            
        if not bcrypt.check_password_hash(user['password'], password):
            return "密码错误 <a href='/login'>返回</a>"
            
        # 验证验证码
        verification = login_verification_db.find_one({
            'username': username,
            'verification_code': verification_code,
            'expires_at': {'$gt': datetime.utcnow()}  # 验证码未过期
        })
        
        if not verification:
            return "验证码无效或已过期 <a href='/login'>返回</a>"
        
        # 验证通过，重置失败次数
        update_login_attempts(username, login_attempts_db=login_attempts_db,success=True)
            
        # 验证通过，删除验证记录
        login_verification_db.delete_one({'username': username})
        
        # 设置用户会话
        session['username'] = username
        
        # 记录登录会话
        login_sessions_db.insert_one({
            'username': username,
            'login_time': datetime.utcnow()
        })
        
        return redirect('/secured')
        
    # GET 请求返回登录页面
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

# Update your existing register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        verification_code = request.form['verification_code']

        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match. <a href='/register'>Try again</a>"

        # Password security validation
        if len(password) < 8:
            return "Password must be at least 8 characters long. <a href='/register'>Try again</a>"
        
        # Check if password contains both letters and numbers
        if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
            return "Password must contain both letters and numbers. <a href='/register'>Try again</a>"
        
        # Check if password contains at least one uppercase letter
        if not any(c.isupper() for c in password):
            return "Password must contain at least one uppercase letter. <a href='/register'>Try again</a>"

        # Verify the code
        verification_data = verification_db.find_one({
            'email': email,
            'username': username,
            'verification_code': verification_code,
            'expires_at': {'$gt': datetime.utcnow()}  # Code must not be expired
        })
        
        if not verification_data:
            return "Invalid or expired verification code. <a href='/register'>Try again</a>"
        
        # All checks passed, create the account
        users = client.get_database("ai_platform").get_collection("login")
        users.insert_one({
            'email': email,
            'username': username,
            'password': verification_data['password']  # Use the already hashed password
        })
        
        # Remove the verification record
        verification_db.delete_one({'email': email})
        
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/secured')
def secured():
    if 'username' in session:
        users = login_db
        user_data = users.find_one({'username': session['username']})

        username = session['username']
        
        # For GitHub users with email, we can still show part of it
        if 'email' in user_data:
            display_name = user_data.get('email', '') or username
        else:
            display_name = username

        return render_template('secured_page.html', username=display_name)
    else:
        return redirect('/login')
    
@app.route('/logout')
def logout():
    if 'username' in session:
        login_sessions = login_sessions_db
        login_sessions.delete_one({'username': session['username']})

    session.pop('username', None)

    return redirect('/login')

# 修改聊天路由，添加文件处理功能
@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_message = request.form.get('message', '')
    chat_id = request.form.get('chat_id', None)
    model = request.form.get('model', 'gpt-4')
    
    file_content = ""
    file_metadata = None
    
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # 读取文件内容
            file_data = file.read()
            
            try:
                # 提取文本内容
                file_content = extract_text_from_file(file_data, file_ext)
                
                # 将文件添加到用户消息
                if user_message:
                    user_message = f"File content:\n{file_content}\n\n{user_message}"
                else:
                    user_message = f"File content:\n{file_content}"
                    
                # 准备文件元数据，以便存入数据库
                file_metadata = {
                    'filename': filename,
                    'content_type': file.content_type,
                    'size': len(file_data),
                    'data': Binary(file_data),
                    'extracted_text': file_content
                }
            except Exception as e:
                print(f"Error processing file: {str(e)}")
                return jsonify({'error': f'Error processing file: {str(e)}'}), 400
    
    if not user_message and not 'file' in request.files:
        return jsonify({'error': 'Message or file is required'}), 400

    try:
        # 查找或创建聊天记录来获取历史消息
        chat_history = []
        if chat_id:
            chat = chats_db.find_one({'_id': ObjectId(chat_id)})
            if chat:
                # 从聊天记录中提取消息，去除时间戳等额外信息
                chat_history = [{'role': msg['role'], 'content': msg['content']} 
                                for msg in chat['messages'] 
                                if msg['role'] in ['user', 'assistant']]
        
        # 调用 GPT 模型获取回复
        assistant_message = get_gpt_response(user_message, chat_history, model)
        
        # 更新或创建聊天记录
        now = datetime.utcnow()
        
        # 准备用户消息对象
        user_msg_obj = {
            'role': 'user', 
            'content': user_message, 
            'timestamp': now
        }
        
        # 如果有文件，添加文件元数据
        if file_metadata:
            user_msg_obj['file'] = file_metadata
        
        # 准备助手消息对象
        assistant_msg_obj = {
            'role': 'assistant',
            'content': assistant_message,
            'timestamp': now
        }
        
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
                            '$each': [user_msg_obj, assistant_msg_obj]
                        }
                    },
                    '$set': {'updated_at': now, 'model': model}
                }
            )
        else:
            # 创建新聊天
            chat_id = str(ObjectId())
            chats_db.insert_one({
                '_id': ObjectId(chat_id),
                'username': session['username'],
                'model': model,
                'messages': [user_msg_obj, assistant_msg_obj],
                'created_at': now,
                'updated_at': now
            })
            
        return jsonify({
            'message': assistant_message,
            'chat_id': chat_id
        })
        
    except Exception as e:
        print(f"Error in /chat route: {str(e)}")
        import traceback
        traceback.print_exc()
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

# 更新 get_chat 路由以返回模型信息
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
            'messages': json.loads(json.dumps(chat['messages'], default=str)),  # 处理日期序列化
            'model': chat.get('model', 'gpt-4')  # 添加模型信息
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 修改创建新聊天的路由
@app.route('/new_chat', methods=['POST'])
def new_chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    model = data.get('model', 'gpt-4')  # 默认使用 GPT-4
        
    try:
        now = datetime.utcnow()
        chat_id = str(ObjectId())
        
        chats_db.insert_one({
            '_id': ObjectId(chat_id),
            'username': session['username'],
            'model': model,  # 保存指定的模型
            'messages': [],
            'created_at': now,
            'updated_at': now
        })
        
        return jsonify({'chat_id': chat_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# 添加更新聊天模型的路由
@app.route('/update_chat_model/<chat_id>', methods=['POST'])
def update_chat_model(chat_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    model = data.get('model')
    
    if not model:
        return jsonify({'error': 'Model is required'}), 400

    try:
        # 查找聊天并验证所有权
        chat = chats_db.find_one({'_id': ObjectId(chat_id), 'username': session['username']})
        if not chat:
            return jsonify({'error': 'Chat not found or unauthorized'}), 404
        
        # 更新聊天使用的模型
        chats_db.update_one(
            {'_id': ObjectId(chat_id)},
            {'$set': {'model': model}}
        )
        
        # 添加一条系统消息，表示模型已切换（可选）
        now = datetime.utcnow()
        chats_db.update_one(
            {'_id': ObjectId(chat_id)},
            {
                '$push': {
                    'messages': {
                        'role': 'system',
                        'content': f"Switched to model: {model}",
                        'timestamp': now
                    }
                }
            }
        )
        
        return jsonify({'success': True, 'message': f'Chat model updated to {model}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# 添加文件下载路由
@app.route('/download_file/<chat_id>/<message_index>', methods=['GET'])
def download_file(chat_id, message_index):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        chat = chats_db.find_one({'_id': ObjectId(chat_id), 'username': session['username']})
        if not chat:
            return jsonify({'error': 'Chat not found or unauthorized'}), 404
        
        # 获取指定的消息
        messages = chat.get('messages', [])
        msg_index = int(message_index)
        
        if msg_index < 0 or msg_index >= len(messages):
            return jsonify({'error': 'Message index out of range'}), 404
        
        message = messages[msg_index]
        
        if 'file' not in message:
            return jsonify({'error': 'No file in this message'}), 404
            
        file_data = message['file']
        
        # 发送文件到客户端
        from flask import send_file
        return send_file(
            io.BytesIO(file_data['data']),
            mimetype=file_data['content_type'],
            as_attachment=True,
            download_name=file_data['filename']
        )
    
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/send_verification', methods=['POST'])
def send_verification():
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Invalid request method'})

    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # Validate email
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'})

    # Check if username already exists
    users = client.get_database("ai_platform").get_collection("login")
    existing_user = users.find_one({'username': username})
    if existing_user:
        return jsonify({'success': False, 'error': 'Username already exists'})

    # Check if email already exists
    existing_email = users.find_one({'email': email})
    if existing_email:
        return jsonify({'success': False, 'error': 'Email already registered'})

    # Generate verification code
    verification_code = generate_verification_code()
    
    # Store verification data
    expiration_time = datetime.utcnow() + timedelta(minutes=10)  # Code expires in 10 minutes
    
    # Hash the password for security
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Store or update verification data
    verification_db.update_one(
        {'email': email},
        {
            '$set': {
                'username': username,
                'password': hashed_password,
                'verification_code': verification_code,
                'expires_at': expiration_time
            }
        },
        upsert=True
    )
    
    # Send verification email
    if send_verification_email(email, verification_code, username):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to send verification email'})

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/send_reset_code', methods=['POST'])
def send_reset_code():
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Invalid request method'})

    data = request.json
    email = data.get('email')

    # Validate email
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'})

    # Check if email exists in database
    users = client.get_database("ai_platform").get_collection("login")
    user = users.find_one({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'Email not found'})

    # Generate verification code
    verification_code = generate_verification_code()
    
    # Store verification data
    expiration_time = datetime.utcnow() + timedelta(minutes=10)  # Code expires in 10 minutes
    
    # Create password reset entry in DB
    reset_db = client.get_database("ai_platform").get_collection("password_resets")
    reset_db.update_one(
        {'email': email},
        {
            '$set': {
                'verification_code': verification_code,
                'expires_at': expiration_time
            }
        },
        upsert=True
    )
    
    # Send password reset verification email
    if send_password_reset_email(email, verification_code):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to send verification email'})

@app.route('/verify_reset_code', methods=['POST'])
def verify_reset_code():
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Invalid request method'})

    data = request.json
    email = data.get('email')
    verification_code = data.get('verification_code')

    # Validate inputs
    if not email or not verification_code:
        return jsonify({'success': False, 'error': 'Missing required fields'})

    # Check if verification code is valid
    reset_db = client.get_database("ai_platform").get_collection("password_resets")
    reset_data = reset_db.find_one({
        'email': email,
        'verification_code': verification_code,
        'expires_at': {'$gt': datetime.utcnow()}  # Code must not be expired
    })
    
    if not reset_data:
        return jsonify({'success': False, 'error': 'Invalid or expired verification code'})
    
    return jsonify({'success': True})

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Invalid request method'})

    data = request.json
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verification_code')

    # Validate inputs
    if not email or not password or not verification_code:
        return jsonify({'success': False, 'error': 'Missing required fields'})

    # Verify the code again
    reset_db = client.get_database("ai_platform").get_collection("password_resets")
    reset_data = reset_db.find_one({
        'email': email,
        'verification_code': verification_code,
        'expires_at': {'$gt': datetime.utcnow()}  # Code must not be expired
    })
    
    if not reset_data:
        return jsonify({'success': False, 'error': 'Invalid or expired verification code'})
    
    # Password security validation
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'})
    
    # Check if password contains both letters and numbers
    if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
        return jsonify({'success': False, 'error': 'Password must contain both letters and numbers'})
    
    # Check if password contains at least one uppercase letter
    if not any(c.isupper() for c in password):
        return jsonify({'success': False, 'error': 'Password must contain at least one uppercase letter'})
    
    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Update user's password
    users = client.get_database("ai_platform").get_collection("login")
    update_result = users.update_one(
        {'email': email},
        {'$set': {'password': hashed_password}}
    )
    
    # Remove the reset record
    reset_db.delete_one({'email': email})
    
    if update_result.matched_count > 0:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update password'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)