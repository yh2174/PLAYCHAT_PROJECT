from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import bcrypt
import traceback

# Load environment variables
load_dotenv(Path('./config/.env'))

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 이 줄을 추가하세요
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

PORT = int(os.getenv('PORT', 3000))
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 데이터베이스 디렉토리 설정
DB_DIR = Path('./db')
DB_DIR.mkdir(exist_ok=True)

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect(DB_DIR / 'message_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# 메시지 저장 함수
def save_message(message):
    conn = sqlite3.connect(DB_DIR / 'message_log.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (content) VALUES (?)", (message,))
    print(f"메시지 저장: {message}")
    conn.commit()
    conn.close()

# 메시지 불러오기 함수
def get_messages():
    conn = sqlite3.connect(DB_DIR / 'message_log.db')
    c = conn.cursor()
    c.execute("SELECT content FROM messages ORDER BY timestamp")
    messages = [row[0] for row in c.fetchall()]
    conn.close()
    return messages

# YouTube 검색 API 엔드포인트
@app.route('/api/search', methods=['GET'])
def search():
    try:
        q = request.args.get('q', '')
        response = requests.get('https://www.googleapis.com/youtube/v3/search', params={
            'part': 'snippet',
            'q': q,
            'type': 'video',
            'key': YOUTUBE_API_KEY
        })
        return jsonify(response.json()['items'])
    except Exception as error:
        print('YouTube API 오류:', error)
        return jsonify({'error': 'YouTube API 요청 중 오류가 발생했습니다.'}), 500

# YouTube 비디오 상세 정보 API 엔드포인트
@app.route('/api/videos/<id>', methods=['GET'])
def video_details(id):
    try:
        response = requests.get('https://www.googleapis.com/youtube/v3/videos', params={
            'part': 'snippet',
            'id': id,
            'key': YOUTUBE_API_KEY
        })
        return jsonify(response.json()['items'][0])
    except Exception as error:
        print('YouTube API 오류:', error)
        return jsonify({'error': 'YouTube API 요청 중 오류가 발생했습니다.'}), 500

# 사용자 데이터베이스 초기화
def init_user_db():
    conn = sqlite3.connect(DB_DIR / 'user_info.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_user_db()

# 사용자 등록 함수
def register_user(username, password):
    conn = sqlite3.connect(DB_DIR / 'user_info.db')
    c = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# 사용자 로그인 함수
def login_user(username, password):
    conn = sqlite3.connect(DB_DIR / 'user_info.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False

# 회원가입 API 엔드포인트
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if register_user(username, password):
        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."})
    else:
        return jsonify({"success": False, "message": "이미 존재하는 사용자명입니다."}), 400

# 로그인 API 엔드포인트
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if login_user(username, password):
        return jsonify({"success": True, "message": "로그인 성공", "username": username})
    else:
        return jsonify({"success": False, "message": "잘못된 사용자명 또는 비밀번호입니다."}), 401

# 로그아웃 API 엔드포인트
@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        session.pop('username', None)
        return jsonify({"success": True, "message": "로그아웃 되었습니다."})
    except Exception as e:
        print(f"로그아웃 중 오류 발생: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "로그아웃 중 오류가 발생했습니다."}), 500

# Socket.IO 이벤트 처리
@socketio.on('connect')
def handle_connect():
    print('새로운 클라이언트가 연결되었습니다.')
    emit('chat history', get_messages())

@socketio.on('chat message')
def handle_message(msg):
    save_message(msg)
    socketio.emit('chat message', msg)

@socketio.on('video selected')
def handle_video_selected(video_data):
    global current_video
    current_video = video_data
    socketio.emit('video selected', video_data, broadcast=True)

@socketio.on('video time update')
def handle_video_time_update(time):
    global current_time
    current_time = time
    socketio.emit('video time update', time, broadcast=True, include_sender=False)

@socketio.on('disconnect')
def handle_disconnect():
    print('클라이언트 연결이 끊어졌습니다.')

@socketio.on('join room')
def handle_join_room(room):
    join_room(room)
    if current_video:
        emit('current state', {'video': current_video, 'time': current_time})

@socketio.on('play')
def handle_play():
    socketio.emit('play', broadcast=True, include_sender=False)

@socketio.on('pause')
def handle_pause():
    socketio.emit('pause', broadcast=True, include_sender=False)

@socketio.on('request current state')
def handle_request_current_state():
    if current_video:
        emit('current state', {'video': current_video, 'time': current_time})

current_video = None
current_time = 0

if __name__ == '__main__':
    print(f'서버가 http://localhost:{PORT} 에서 실행 중입니다.')
    socketio.run(app, host='0.0.0.0', port=PORT, allow_unsafe_werkzeug=True)