# 🎬 PlayChat

> 실시간 영상 동기화 시청 및 채팅 플랫폼

[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Vuetify](https://img.shields.io/badge/Vuetify-3.x-1867C0?logo=vuetify)](https://vuetifyjs.com/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask)](https://flask.palletsprojects.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-4.x-010101?logo=socket.io)](https://socket.io/)

---

## 📖 소개

PlayChat은 여러 사용자가 **동시에 같은 YouTube 영상을 시청**하면서 **실시간으로 채팅**할 수 있는 웹 애플리케이션입니다. 영상의 재생/일시정지/탐색이 모든 참여자에게 동기화되어, 마치 같은 공간에서 함께 시청하는 경험을 제공합니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🔐 **사용자 인증** | 회원가입 및 로그인 (bcrypt 암호화) |
| 🎥 **영상 동기화** | YouTube 영상 검색 및 실시간 동기화 재생 |
| 💬 **실시간 채팅** | Socket.IO 기반 실시간 메시지 송수신 |
| 📜 **채팅 기록** | SQLite DB를 통한 메시지 기록 저장 |
| 🛡️ **보안 기능** | Rate Limiting, XSS 방어, 세션 보안 |

---

## 🛠️ 기술 스택

### Frontend
- **Vue.js 3** - 프로그레시브 JavaScript 프레임워크
- **Vuetify 3** - Material Design 컴포넌트 라이브러리
- **Vue Router 4** - SPA 라우팅
- **Socket.IO Client** - 실시간 양방향 통신
- **Axios** - HTTP 클라이언트
- **Vite** - 차세대 빌드 도구

### Backend
- **Flask** - Python 웹 프레임워크
- **Flask-SocketIO** - WebSocket 지원
- **Flask-Limiter** - Rate Limiting (무차별 대입 공격 방어)
- **SQLite** - 경량 데이터베이스
- **bcrypt** - 비밀번호 해싱

### External API
- **YouTube Data API v3** - 영상 검색 및 정보 조회

---

## 📋 요구사항

- **Node.js** 18.x 이상
- **Python** 3.9 이상
- **Google YouTube Data API v3 Key** ([발급 방법](https://developers.google.com/youtube/v3/getting-started))

---

## 🚀 시작하기

### 1. 저장소 클론

```bash
git clone <repository-url>
cd PLAYCHAT_PROJECT
```

### 2. 환경 변수 설정

`config/.env.example`을 참고하여 `config/.env` 파일을 생성합니다:

```bash
cp config/.env.example config/.env
```

`.env` 파일을 열어 필수 환경 변수를 설정합니다:

```env
# 서버 설정
PORT=3000
FLASK_ENV=development

# 보안 (프로덕션에서는 반드시 변경)
SECRET_KEY=your_secret_key_here

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# CORS 허용 도메인 (프로덕션)
ALLOWED_ORIGINS=http://localhost:5173
```

> ⚠️ **보안 주의**: `SECRET_KEY`는 프로덕션 환경에서 반드시 강력한 랜덤 문자열로 변경하세요!

### 3. 의존성 설치

```bash
# Frontend 의존성
npm install --legacy-peer-deps

# Backend 의존성
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

**개발 모드:**

```bash
# 터미널 1: Frontend (Vite 개발 서버)
npm run dev

# 터미널 2: Backend (Flask 서버)
python app.py
```

**프로덕션 빌드:**

```bash
npm run build
npm run serve
```

---

## 📁 프로젝트 구조

```
PLAYCHAT_PROJECT/
├── config/                 # 환경 설정
│   └── .env               # 환경 변수 (gitignore)
├── db/                    # SQLite 데이터베이스
│   ├── message_log.db     # 채팅 메시지 저장
│   └── user_info.db       # 사용자 정보 저장
├── public/                # 정적 파일
│   └── favicon.ico
├── src/                   # Vue.js 소스 코드
│   ├── assets/            # 이미지, 폰트 등 자원
│   ├── components/        # 재사용 가능한 컴포넌트
│   │   ├── ChatView.vue   # 채팅 UI
│   │   ├── Login.vue      # 로그인 폼
│   │   ├── Register.vue   # 회원가입 폼
│   │   └── VideoPlayer.vue# 영상 플레이어
│   ├── plugins/           # Vue 플러그인 설정
│   │   ├── vuetify.js     # Vuetify 설정
│   │   └── webfontloader.js
│   ├── router/            # Vue Router 설정
│   │   └── index.js
│   ├── views/             # 페이지 컴포넌트
│   │   ├── AboutView.vue
│   │   ├── HomeView.vue
│   │   └── MainView.vue   # 메인 화면 (영상+채팅)
│   ├── App.vue            # 루트 컴포넌트
│   └── main.js            # 앱 진입점
├── app.py                 # Flask 백엔드 서버
├── index.html             # HTML 템플릿
├── package.json           # npm 설정
├── requirements.txt       # Python 패키지 목록
├── vite.config.js         # Vite 설정
└── README.md
```

---

## 🔌 API 엔드포인트

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register` | 회원가입 |
| `POST` | `/api/login` | 로그인 |
| `POST` | `/api/logout` | 로그아웃 |
| `GET` | `/api/search?q={query}` | YouTube 영상 검색 |
| `GET` | `/api/videos/{id}` | 영상 상세 정보 조회 |

### Socket.IO Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `chat message` | ↔️ | 채팅 메시지 송수신 |
| `chat history` | ← | 이전 채팅 기록 수신 |
| `video selected` | ↔️ | 영상 선택 동기화 |
| `video time update` | ↔️ | 영상 재생 시간 동기화 |
| `play` / `pause` | ↔️ | 재생/일시정지 동기화 |

---

## 🔧 개발 스크립트

```bash
npm run dev      # 개발 서버 실행 (HMR)
npm run build    # 프로덕션 빌드
npm run serve    # 빌드된 파일 미리보기
npm run lint     # ESLint 검사
```

---

## 🔒 보안 기능

이 프로젝트에는 다음과 같은 보안 기능이 구현되어 있습니다:

| 보안 기능 | 설명 |
|-----------|------|
| **비밀번호 해싱** | bcrypt (rounds=12)를 사용한 안전한 비밀번호 저장 |
| **비밀번호 정책** | 최소 8자, 영문+숫자 필수 |
| **Rate Limiting** | 로그인 10회/분, 회원가입 5회/분 제한 |
| **세션 보안** | HTTPOnly, SameSite 쿠키 설정 |
| **XSS 방어** | 채팅 메시지 HTML 이스케이프 처리 |
| **입력값 검증** | 서버 측 유효성 검사 |
| **CORS 설정** | 허용된 도메인만 API 접근 가능 |

### 프로덕션 배포 시 체크리스트

- [ ] `SECRET_KEY`를 강력한 랜덤 문자열로 변경
- [ ] `FLASK_ENV=production` 설정
- [ ] HTTPS 적용 후 `SESSION_COOKIE_SECURE=True` 활성화
- [ ] `ALLOWED_ORIGINS`를 실제 도메인으로 변경
- [ ] 데이터베이스 백업 설정

---

## 🤝 기여하기

1. 이 저장소를 Fork 합니다
2. 새 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m '[Add] 새로운 기능 추가'`)
4. 브랜치에 Push 합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 Issue를 생성해 주세요.
