# 🖥️ 로컬 PC 테스트 완전 가이드

> **개발 완료! 이제 로컬에서 전체 시스템을 테스트하세요**

---

## 📋 목차

1. [개발 상태 확인](#개발-상태-확인)
2. [로컬 설정 (5분)](#로컬-설정-5분)
3. [테스트 시나리오](#테스트-시나리오)
4. [기능별 테스트](#기능별-테스트)
5. [문제 해결](#문제-해결)

---

## ✅ 개발 상태 확인

### 완성된 기능들

```
✅ Codespace 환경 설정
✅ 완전한 사용 설명서 (3개 문서)
✅ Streamlit 대시보드 (기본 + 간소화 버전)
✅ 프로세스 시각화 UI
✅ 멀티 저장소 지원
   ├─ SQLite (로컬)
   ├─ Firebase (클라우드)
   ├─ Notion (협업)
   └─ MongoDB (NoSQL)
✅ Setup Wizard (초기 설정 마법사)
✅ Config Manager (설정 관리)
✅ 5가지 AI 모델 지원
   ├─ ChatGPT (OpenAI)
   ├─ Claude (Anthropic)
   ├─ Gemini (Google)
   ├─ Hugging Face
   └─ 로컬 모델 (Ollama)
✅ API 어댑터들
   ├─ Firebase 어댑터
   ├─ 기타 저장소 어댑터
   └─ 추상 인터페이스
```

### 생성된 파일 구조

```
LLM_Deliver/
├── config/
│   ├── __init__.py
│   ├── llm_config.py (AI 모델 설정)
│   ├── storage_config.py (저장소 설정)
│   └── config_manager.py (설정 관리)
├── api_server_v2/
│   ├── app/adapters/
│   │   ├── base.py (추상 클래스)
│   │   ├── sqlite.py
│   │   ├── firebase.py
│   │   ├── notion.py
│   │   ├── mongodb.py
│   │   ├── factory.py (동적 선택)
│   │   └── google_docs.py
│   └── requirements.txt (모든 의존성 포함)
├── clients/
│   ├── streamlit_dashboard.py (완전 버전)
│   ├── streamlit_dashboard_simple.py (간소화 버전)
│   └── python/requirements.txt
├── .devcontainer/ (Codespace)
├── setup_wizard.py (설정 마법사)
├── GETTING_STARTED.md
├── LOCAL_SETUP.md
├── CODESPACE_SETUP.md
├── LOCAL_TEST_GUIDE.md
├── STREAMLIT_DASHBOARD.md
├── ALTERNATIVE_STORAGE_OPTIONS.md
├── PROCESS_VISUALIZATION_METHODS.md
└── README.md (개선됨)
```

---

## 🚀 로컬 설정 (5분)

### Step 1: 프로젝트 클론

```bash
git clone https://github.com/MediumsKor/LLM_Deliver.git
cd LLM_Deliver
```

### Step 2: Python 가상 환경

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: 의존성 설치

```bash
# Setup Wizard를 위한 Streamlit
pip install streamlit

# 전체 의존성 (선택)
pip install -r api_server_v2/requirements.txt
pip install -r clients/python/requirements.txt
```

### Step 4: Setup Wizard 실행

```bash
streamlit run setup_wizard.py
```

**화면에 나타나는 것:**
```
🚀 Memory Hub 초기 설정

Step 1️⃣: AI 모델 선택
Step 2️⃣: 저장소 선택
Step 3️⃣: API 키 입력
Step 4️⃣: 설정 완료
```

---

## 🧪 테스트 시나리오

### 시나리오 1️⃣: SQLite만 사용 (가장 간단! ⭐)

**소요 시간:** 5분
**필요한 것:** Python만

```bash
# 1. Setup Wizard에서 선택
   - AI 모델: ChatGPT 또는 Claude 또는 로컬 모델
   - 저장소: SQLite
   - API 키: (로컬 모델 선택 시 불필요)

# 2. 자동으로 생성되는 파일
   ✅ config/user_config.json
   ✅ .env
   ✅ api_server_v2/memory_hub.db

# 3. Streamlit 대시보드 실행
cd clients
streamlit run streamlit_dashboard_simple.py

# 4. 브라우저에서 http://localhost:8501 접속
```

### 시나리오 2️⃣: Firebase 클라우드 저장

**소요 시간:** 10분 (Firebase 설정 포함)
**필요한 것:** Firebase 계정

```bash
# 1. Firebase 프로젝트 설정
   - https://firebase.google.com 접속
   - 새 프로젝트 생성
   - Firestore 데이터베이스 생성
   - 서비스 계정 키 다운로드 (JSON)

# 2. Setup Wizard에서 선택
   - AI 모델: ChatGPT
   - 저장소: Firebase
   - credentials.json 파일 경로 입력

# 3. 자동으로 생성
   ✅ .env (STORAGE_TYPE=firebase)
   ✅ config/user_config.json

# 4. 테스트
cd clients
streamlit run streamlit_dashboard_simple.py
```

### 시나리오 3️⃣: Notion 팀 협업

**소요 시간:** 15분
**필요한 것:** Notion 계정

```bash
# 1. Notion 설정
   - https://www.notion.so 접속
   - 새 데이터베이스 생성
   - https://www.notion.so/my-integrations 에서
     통합 생성 후 API 키 받기

# 2. Setup Wizard에서 선택
   - 저장소: Notion
   - API 키와 데이터베이스 ID 입력

# 3. 테스트
cd clients
streamlit run streamlit_dashboard_simple.py
```

### 시나리오 4️⃣: 모든 기능 완전 테스트

**소요 시간:** 30분
**필요한 것:** API 키들

```bash
# 1. ChatGPT API 키 받기 (선택)
   https://platform.openai.com/api-keys

# 2. FastAPI 서버 실행 (터미널 1)
cd api_server_v2
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Streamlit 대시보드 실행 (터미널 2)
cd clients
streamlit run streamlit_dashboard_simple.py

# 4. 테스트
   - 메모 저장 (PUSH)
   - 메모 불러오기 (PULL)
   - 워크스페이스 관리
   - 프로세스 흐름도 확인
```

---

## ✅ 기능별 테스트

### 📖 Setup Wizard 테스트

```
✅ 테스트 항목:
1. 첫 실행 시 환영 화면 표시
2. Step 1: AI 모델 목록 보이기
3. Step 2: 저장소 목록 보이기
4. Step 3: 필수 정보 입력
5. Step 4: 설정 완료 및 파일 생성

✅ 확인 사항:
- config/user_config.json 생성됨
- .env 파일 생성됨
- 올바른 환경 변수 설정됨
```

### 📊 Streamlit 대시보드 테스트

#### Tab 1: 메모 저장 (PUSH)

```bash
# 테스트 단계:
1. "📤 메모 저장" 탭 열기
2. 메모 입력:
   [HANDOFF]
   테스트 메모입니다.
   2024-11-17 테스트 중

3. "💾 Google Docs에 저장" 클릭
4. 프로세스 진행 상황 확인:
   ✅ 📝 유효성 검사
   ✅ 🔐 인증 확인
   ✅ 💾 DB 저장
   ✅ ☁️ 저장소 동기화
   ✅ ✅ 저장 완료!

5. 성공 메시지 및 메트릭 확인
```

#### Tab 2: 메모 불러오기 (PULL)

```bash
# 테스트 단계:
1. "📥 메모 불러오기" 탭 열기
2. 같은 워크스페이스 선택
3. "📥 메모 불러오기" 클릭
4. 4단계 진행 표시 확인
5. 저장된 메모 표시 확인
6. 메타데이터 확인:
   - 수정 시간
   - 리비전 ID
   - 카테고리
```

#### Tab 3: 워크스페이스 관리

```bash
# 테스트 단계:
1. "🏢 워크스페이스" 탭 열기
2. 기존 워크스페이스 목록 확인
3. 새 워크스페이스 생성:
   - 이름: "테스트 팀"
   - 스코프: team
   - "생성" 클릭
4. 성공 메시지 확인
```

#### Tab 4: 프로세스 흐름도

```bash
# 테스트 단계:
1. "📊 프로세스 흐름도" 탭 열기
2. PUSH 흐름도 확인
3. PULL 흐름도 확인
4. ASCII 다이어그램이 제대로 표시되는지 확인
```

### 🔌 저장소 기능 테스트

#### SQLite 테스트

```bash
# 1. 데이터베이스 파일 확인
ls -la api_server_v2/memory_hub.db

# 2. 데이터베이스 내용 확인 (선택)
sqlite3 api_server_v2/memory_hub.db
sqlite> SELECT * FROM memories;
sqlite> .quit

# 3. 새 메모 저장 후 파일 크기 증가 확인
ls -lh api_server_v2/memory_hub.db
```

#### Firebase 테스트 (설정한 경우)

```bash
# 1. Firebase Console에서 데이터 확인
   https://console.firebase.google.com

# 2. Firestore → memories 컬렉션 확인
   - 저장된 메모 문서 보이기
   - 타임스탬프 확인

# 3. 실시간 동기화 확인
   - 다른 기기에서도 메모 보이기
```

---

## 🐛 문제 해결

### ❓ "Setup Wizard를 실행할 수 없음"

```bash
# 해결:
1. Streamlit 설치 확인
   pip install streamlit

2. 경로 확인
   pwd  # LLM_Deliver 폴더에 있는지 확인

3. 다시 실행
   streamlit run setup_wizard.py
```

### ❓ "메모 저장에 실패함"

```bash
# 확인 사항:
1. .env 파일 존재 확인
   cat .env

2. 저장소 설정 확인
   STORAGE_TYPE=sqlite 확인

3. 경로 권한 확인
   ls -la config/user_config.json
```

### ❓ "Firebase 연결 실패"

```bash
# 확인 사항:
1. credentials.json 파일 경로 확인
2. Firebase 프로젝트가 Firestore 활성화되었는지 확인
3. 서비스 계정 권한 확인
   - Editor 권한 필요
```

### ❓ "포트 8501이 이미 사용 중"

```bash
# 다른 포트로 실행
streamlit run setup_wizard.py --server.port=8502
streamlit run clients/streamlit_dashboard_simple.py --server.port=8503
```

---

## 📊 테스트 체크리스트

### 초기 설정
- [ ] 프로젝트 클론 완료
- [ ] Python 가상 환경 활성화
- [ ] Streamlit 설치 완료
- [ ] Setup Wizard 실행 성공

### Setup Wizard
- [ ] Step 1: AI 모델 선택 완료
- [ ] Step 2: 저장소 선택 완료
- [ ] Step 3: API 키 입력 완료
- [ ] Step 4: 설정 저장 완료
- [ ] .env 파일 생성됨
- [ ] config/user_config.json 생성됨

### Streamlit 대시보드
- [ ] 메모 저장 (PUSH) 성공
- [ ] 메모 불러오기 (PULL) 성공
- [ ] 워크스페이스 생성 성공
- [ ] 프로세스 흐름도 표시 정상
- [ ] 모든 탭 작동 정상

### 저장소 기능
- [ ] 선택한 저장소에 데이터 저장됨
- [ ] 저장된 데이터 조회 성공
- [ ] 메타데이터 정상 저장
- [ ] 타임스탬프 정상 기록

### 추가 기능 (선택)
- [ ] FastAPI 서버 실행 성공 (선택)
- [ ] 다양한 저장소 테스트 (선택)
- [ ] 여러 AI 모델 테스트 (선택)

---

## 🎯 권장 테스트 순서

### 1️⃣ 기본 테스트 (10분)
```bash
# 1. Setup Wizard로 SQLite 설정
streamlit run setup_wizard.py
# AI 모델: ChatGPT API 키 또는 로컬 모델
# 저장소: SQLite

# 2. Streamlit 대시보드 실행
streamlit run clients/streamlit_dashboard_simple.py

# 3. 메모 저장/불러오기 테스트
```

### 2️⃣ 저장소 테스트 (15분)
```bash
# 각 저장소별 테스트:
- SQLite: 기본값 (설정 불필요)
- Firebase: 크레덴셜 파일 필요
- Notion: API 키 필요
- MongoDB: 연결 문자열 필요
```

### 3️⃣ 전체 시스템 테스트 (30분)
```bash
# FastAPI 서버 + Streamlit 동시 실행
# 모든 기능 종합 테스트
```

---

## ✨ 테스트 완료 후

테스트가 완료되면 다음을 할 수 있습니다:

```
✅ 로컬에서 모든 기능 확인됨
✅ 다양한 저장소 옵션 테스트 완료
✅ UI/UX 사용성 확인 완료

→ 프로덕션 배포 준비
→ 팀원들과 공유
→ 실제 사용 시작
```

---

## 📚 참고 문서

| 문서 | 내용 |
|------|------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | 빠른 시작 (모든 방법) |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | 로컬 상세 설정 |
| [LOCAL_TEST_GUIDE.md](./LOCAL_TEST_GUIDE.md) | 로컬 테스트 (기본) |
| [STREAMLIT_DASHBOARD.md](./STREAMLIT_DASHBOARD.md) | Streamlit 가이드 |
| [ALTERNATIVE_STORAGE_OPTIONS.md](./ALTERNATIVE_STORAGE_OPTIONS.md) | 저장소 옵션 |

---

## 🎉 시작하기

**지금 바로 시작하세요:**

```bash
# 1. Setup Wizard 실행
streamlit run setup_wizard.py

# 2. 설정 완료 후 대시보드 실행
streamlit run clients/streamlit_dashboard_simple.py

# 3. 브라우저에서 테스트
# http://localhost:8501
```

---

**행운을 빕니다! 🚀**
