from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import os
import re
import secrets
import html
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import bcrypt
import logging
from datetime import timedelta

# 로깅 설정 (민감 정보 노출 방지)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path('./config/.env'))

app = Flask(__name__)

# 보안: secret_key를 환경변수에서 로드 (없으면 랜덤 생성)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# 세션 보안 설정
app.config.update(
    SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',  # HTTPS에서만 쿠키 전송
    SESSION_COOKIE_HTTPONLY=True,  # JavaScript에서 쿠키 접근 차단
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF 방어
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)  # 세션 유효 시간
)

# CORS 설정 (환경별 분리)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

# Rate Limiting 설정 (무차별 대입 공격 방어)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

PORT = int(os.getenv('PORT', 3000))
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 보안: 비밀번호 정책
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')

# 데이터베이스 디렉토리 설정
DB_DIR = Path('./db')
DB_DIR.mkdir(exist_ok=True)


def get_db_connection(db_name):
    """데이터베이스 연결 (컨텍스트 매니저용)"""
    conn = sqlite3.connect(DB_DIR / db_name)
    conn.row_factory = sqlite3.Row
    return conn


# 데이터베이스 초기화
def init_db():
    with get_db_connection('message_log.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      content TEXT NOT NULL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()


init_db()


def sanitize_message(message):
    """XSS 방어를 위한 메시지 정제"""
    if not message or not isinstance(message, str):
        return ""
    # HTML 특수문자 이스케이프
    return html.escape(message.strip())[:1000]  # 최대 1000자 제한


def save_message(message):
    """메시지 저장 (정제 후)"""
    sanitized = sanitize_message(message)
    if not sanitized:
        return False
    with get_db_connection('message_log.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (content) VALUES (?)", (sanitized,))
        conn.commit()
    logger.info("메시지 저장 완료")
    return True


def get_messages(limit=100):
    """메시지 불러오기 (최근 N개)"""
    with get_db_connection('message_log.db') as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,))
        messages = [row[0] for row in c.fetchall()]
    return list(reversed(messages))


def validate_username(username):
    """사용자명 유효성 검사"""
    if not username or not isinstance(username, str):
        return False, "사용자명을 입력해주세요."
    username = username.strip()
    if len(username) < USERNAME_MIN_LENGTH:
        return False, f"사용자명은 최소 {USERNAME_MIN_LENGTH}자 이상이어야 합니다."
    if len(username) > USERNAME_MAX_LENGTH:
        return False, f"사용자명은 최대 {USERNAME_MAX_LENGTH}자까지 가능합니다."
    if not USERNAME_PATTERN.match(username):
        return False, "사용자명은 영문, 숫자, 밑줄(_)만 사용할 수 있습니다."
    return True, username


def validate_password(password):
    """비밀번호 정책 검사"""
    if not password or not isinstance(password, str):
        return False, "비밀번호를 입력해주세요."
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"비밀번호는 최소 {PASSWORD_MIN_LENGTH}자 이상이어야 합니다."
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"비밀번호는 최대 {PASSWORD_MAX_LENGTH}자까지 가능합니다."
    if not re.search(r'[A-Za-z]', password):
        return False, "비밀번호에 영문자를 포함해야 합니다."
    if not re.search(r'\d', password):
        return False, "비밀번호에 숫자를 포함해야 합니다."
    return True, None


# YouTube 검색 API 엔드포인트
@app.route('/api/search', methods=['GET'])
@limiter.limit("30 per minute")
def search():
    try:
        q = request.args.get('q', '').strip()
        if not q:
            return jsonify({'error': '검색어를 입력해주세요.'}), 400
        if len(q) > 100:
            return jsonify({'error': '검색어가 너무 깁니다.'}), 400
        
        response = requests.get('https://www.googleapis.com/youtube/v3/search', params={
            'part': 'snippet',
            'q': q,
            'type': 'video',
            'key': YOUTUBE_API_KEY,
            'maxResults': 10
        }, timeout=10)
        response.raise_for_status()
        return jsonify(response.json().get('items', []))
    except requests.Timeout:
        logger.error('YouTube API 타임아웃')
        return jsonify({'error': '요청 시간이 초과되었습니다.'}), 504
    except Exception as error:
        logger.error(f'YouTube API 오류: {type(error).__name__}')
        return jsonify({'error': 'YouTube API 요청 중 오류가 발생했습니다.'}), 500


# YouTube 비디오 상세 정보 API 엔드포인트
@app.route('/api/videos/<video_id>', methods=['GET'])
@limiter.limit("60 per minute")
def video_details(video_id):
    try:
        # 비디오 ID 유효성 검사 (YouTube ID 형식: 11자 영숫자)
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            return jsonify({'error': '유효하지 않은 비디오 ID입니다.'}), 400
        
        response = requests.get('https://www.googleapis.com/youtube/v3/videos', params={
            'part': 'snippet',
            'id': video_id,
            'key': YOUTUBE_API_KEY
        }, timeout=10)
        response.raise_for_status()
        items = response.json().get('items', [])
        if not items:
            return jsonify({'error': '비디오를 찾을 수 없습니다.'}), 404
        return jsonify(items[0])
    except requests.Timeout:
        logger.error('YouTube API 타임아웃')
        return jsonify({'error': '요청 시간이 초과되었습니다.'}), 504
    except Exception as error:
        logger.error(f'YouTube API 오류: {type(error).__name__}')
        return jsonify({'error': 'YouTube API 요청 중 오류가 발생했습니다.'}), 500


# 사용자 데이터베이스 초기화
def init_user_db():
    with get_db_connection('user_info.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      login_attempts INTEGER DEFAULT 0,
                      locked_until DATETIME DEFAULT NULL)''')
        conn.commit()


init_user_db()


def register_user(username, password):
    """사용자 등록 (비밀번호 해싱)"""
    with get_db_connection('user_info.db') as conn:
        c = conn.cursor()
        try:
            # bcrypt 해싱 (자동 솔트 포함)
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            logger.info(f"새 사용자 등록: {username}")
            return True
        except sqlite3.IntegrityError:
            return False


def login_user(username, password):
    """사용자 로그인 검증"""
    with get_db_connection('user_info.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), result[0])
            if is_valid:
                logger.info(f"로그인 성공: {username}")
            return is_valid
        return False


# 회원가입 API 엔드포인트
@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")  # 회원가입 Rate Limit
def register():
    data = request.json or {}
    
    # 사용자명 검증
    is_valid, result = validate_username(data.get('username'))
    if not is_valid:
        return jsonify({"success": False, "message": result}), 400
    username = result
    
    # 비밀번호 검증
    is_valid, error_msg = validate_password(data.get('password'))
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400
    password = data.get('password')
    
    if register_user(username, password):
        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."})
    else:
        return jsonify({"success": False, "message": "이미 존재하는 사용자명입니다."}), 400


# 로그인 API 엔드포인트
@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")  # 로그인 Rate Limit (무차별 대입 방어)
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "message": "사용자명과 비밀번호를 입력해주세요."}), 400
    
    if login_user(username, password):
        session['username'] = username
        session.permanent = True
        return jsonify({"success": True, "message": "로그인 성공", "username": username})
    else:
        # 보안: 사용자 존재 여부를 노출하지 않음
        return jsonify({"success": False, "message": "잘못된 사용자명 또는 비밀번호입니다."}), 401


# 로그아웃 API 엔드포인트
@app.route('/api/logout', methods=['POST'])
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"로그아웃: {username}")
    return jsonify({"success": True, "message": "로그아웃 되었습니다."})


# Socket.IO 이벤트 처리
@socketio.on('connect')
def handle_connect():
    logger.info('새로운 클라이언트 연결')
    emit('chat history', get_messages())


@socketio.on('chat message')
def handle_message(msg):
    if save_message(msg):
        socketio.emit('chat message', sanitize_message(msg))


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
    logger.info('클라이언트 연결 해제')


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
    is_production = os.getenv('FLASK_ENV') == 'production'
    logger.info(f'서버가 http://localhost:{PORT} 에서 실행 중입니다.')
    socketio.run(
        app,
        host='0.0.0.0',
        port=PORT,
        debug=not is_production,
        allow_unsafe_werkzeug=not is_production
    )
