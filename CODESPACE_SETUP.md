# ☁️ GitHub Codespace 완전 가이드

> **클라우드 개발 환경에서 5분 안에 시작하기**

---

## 📑 목차
1. [Codespace란?](#codespace란)
2. [단계별 설정](#단계별-설정)
3. [서버 실행](#서버-실행)
4. [자주 묻는 질문](#자주-묻는-질문)

---

## Codespace란?

**Codespace = 클라우드 VS Code** ☁️

```
당신의 PC (Windows/Mac)
         ↓ (인터넷)
   GitHub의 클라우드 서버
         ↓
   VS Code (브라우저)
         ↓
프로젝트 코드 작업 🖥️
```

### 🎯 장점:
- ✅ 설치 없음 (GitHub만 있으면 OK!)
- ✅ 온라인 어디서나 접속 가능
- ✅ 자동으로 모든 도구 설치됨
- ✅ 여러 사람이 동시에 협업 가능

### ⚙️ 사양:
- **CPU**: 2-core 프로세서
- **RAM**: 4GB
- **스토리지**: 32GB
- **월 무료 사용량**: 60시간 (충분합니다!)

---

## 단계별 설정

### 1️⃣ GitHub에서 Codespace 만들기

**Step 1: GitHub 저장소 페이지 열기**
```
https://github.com/MediumsKor/LLM_Deliver
```

**Step 2: Code 버튼 클릭**
```
화면 우측 상단 [<> Code] 버튼 클릭
↓
드롭다운 메뉴 표시
```

**Step 3: Codespace 탭**
```
[Codespace] 탭 클릭
↓
[+ Create codespace on main] 버튼 클릭
```

**Step 4: 기다리기**
```
화면에 메시지 표시:
"Setting up your codespace..." ⏳
↓
1-2분 후...
↓
VS Code가 브라우저에 표시됨! 🎉
```

> 💡 **처음이면 조금 오래 걸립니다** (2-3분)
> 두 번째부터는 빠릅니다 (30초)

---

### 2️⃣ 자동 설정 대기

Codespace가 열리면 자동으로 실행됩니다:

```bash
#!/bin/bash
📝 Setting up environment variables...
✓ Created .env from .env.example

📦 Installing FastAPI server dependencies...
✓ FastAPI dependencies installed

📦 Installing Python client dependencies...
✓ Client dependencies installed

🛠️  Installing development tools...
✓ Development tools installed

====================================
✅ Setup Complete!
====================================
```

> 화면 하단 **터미널(Terminal)** 에 이 메시지가 보이면 설정 완료! 🎉

---

### 3️⃣ 환경 파일 설정

**Step 1: 파일 탐색기에서 .env 파일 열기**
```
좌측 [탐색기] → [.env] 클릭
```

**Step 2: 정보 입력**
```env
# Google Docs ID 입력
# URL: https://docs.google.com/document/d/[이 부분]/edit
DOC_ID="1a2b3c4d5e6f7g8h9i0j"

# Google Apps Script 웹 앱 URL
WEBAPP_URL="https://script.google.com/macros/s/XXXXX/exec"

# 인증 토큰
API_TOKEN="C_SECRET_1234"
```

> ⚠️ **주의:** `.env` 파일에는 비밀 정보가 들어갑니다!
> 절대 GitHub에 올리면 안 됩니다 (자동으로 `.gitignore`에 등록됨)

**Step 3: 파일 저장**
```
[Ctrl + S] (또는 [Cmd + S] Mac)
```

---

## 서버 실행

### 🚀 FastAPI 서버 시작

**Step 1: 터미널 열기**
```
화면 상단 [터미널] → [새 터미널 열기]
또는: [Ctrl + `]
```

**Step 2: 서버 디렉토리로 이동**
```bash
cd api_server_v2
```

**Step 3: 서버 실행**
```bash
uvicorn app.main:app --reload
```

**Step 4: 성공 메시지 확인**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete
```

> 💚 **이 메시지가 보이면 성공!**

---

### 📖 API 문서 확인

**Step 1: 터미널 창의 URL 클릭**
```
터미널에 표시된 URL:
http://127.0.0.1:8000
↓
[Ctrl] 키 누른 상태에서 클릭
```

또는

**Step 2: 브라우저에서 직접 입력**
```
주소창 입력:
http://localhost:8000/docs
```

**Step 3: Swagger UI 확인**
```
아름다운 API 문서가 보입니다! 📚

API 목록:
- GET /health (서버 상태 확인)
- POST /sessions (세션 생성)
- POST /memories (메모 저장)
- GET /memories (메모 조회)
...등등
```

---

### 🧪 API 테스트 (선택사항)

**Swagger UI에서 직접 테스트:**

```
API 문서 페이지에서:
1. API 엔드포인트 선택 (예: /health)
2. [Try it out] 버튼 클릭
3. [Execute] 버튼 클릭
4. 응답 확인
```

**터미널에서 테스트:**

```bash
# 새 터미널 열기 [Ctrl + `]
# 또는 기존 터미널에서 [Ctrl + C] 후 실행

# 1. 서버 상태 확인
curl http://localhost:8000/health

# 응답: {"status":"ok"}

# 2. 메모 조회 (예시)
curl "http://localhost:8000/memories?scope=personal"

# 응답: 저장된 메모 목록이 JSON 형식으로 반환
```

---

## Python 클라이언트 사용

### 📥 저장된 메모 불러오기

**Step 1: 새 터미널 열기**
```
기존 서버 터미널은 그대로 두고
[Ctrl + `] 또는 [터미널] → [새 터미널 열기]
```

**Step 2: 클라이언트 디렉토리로 이동**
```bash
cd clients/python
```

**Step 3: 메모 불러오기**
```bash
python fetch_memory.py
```

**Step 4: 결과 확인**
```
터미널에 저장된 최신 메모가 출력됩니다! 📄
```

---

### 📤 메모 저장하기

**방법 1: 클립보드에서 저장** (추천)
```bash
# 복사할 텍스트를 클립보드에 복사
# (Ctrl + C 또는 Cmd + C)

cd clients/python
python push_memory.py --clipboard
```

**방법 2: 파일에서 저장**
```bash
# 저장할 텍스트를 파일에 저장 (예: notes.txt)

python push_memory.py --file notes.txt --scope personal
```

**방법 3: 팀 문서에 저장**
```bash
# 팀 스코프에 저장
python push_memory.py --clipboard --scope team --team alpha
```

> 💡 `alpha`, `beta` 등은 `.env` 파일의 `TEAM_MAP`에 정의된 팀 이름

---

## 테스트 실행

### ✅ 단위 테스트

```bash
# 프로젝트 루트에서
pytest clients/python/tests/ -v

# 결과 예시:
# tests/test_conflict_flow.py::test_example PASSED [100%]
# ================ 1 passed in 0.05s ================
```

---

## 🔌 Codespace 멈추기/다시 시작

### 임시 중지 (권장)
```
GitHub 페이지 → [Codespace 관리] → [···] → [Suspend]
↓
다시 시작할 때 빠르게 로드됨
↓
비용 절약 (시간 카운트 안 됨)
```

### 완전 삭제
```
GitHub 페이지 → [Codespace 관리] → [···] → [Delete]
↓
처음부터 다시 생성 가능
```

---

## 자주 묻는 질문

### ❓ "Codespace가 자꾸 끊겨요"

**이유**: 브라우저 탭이 오래 비활성 상태
**해결법**:
1. Codespace 탭을 활성 창으로 클릭
2. 아무 키나 누르기
3. 터미널에서 명령 실행하기

### ❓ "서버가 실행되지 않아요"

**확인사항**:
1. `api_server_v2` 디렉토리에 있는지 확인
   ```bash
   pwd  # 경로 확인
   # /workspaces/LLM_Deliver/api_server_v2 이어야 함
   ```

2. 의존성 설치 확인
   ```bash
   pip list | grep fastapi
   # fastapi와 uvicorn이 목록에 있어야 함
   ```

3. 다시 설치
   ```bash
   pip install -r requirements.txt
   ```

### ❓ "포트 8000이 이미 사용 중이에요"

```bash
# 다른 포트 사용
uvicorn app.main:app --reload --port 8001

# 또는 기존 프로세스 종료
# [Ctrl + C] 입력 후 다시 시작
```

### ❓ "변경사항이 저장되지 않았어요"

Codespace는 자동 저장됩니다. 만약 안 됐다면:

```bash
# 수동으로 Git에 커밋
git add .
git commit -m "작업 내용"
git push origin main
```

### ❓ "마이크/카메라 권한 묻는데?"

Codespace는 브라우저 기반이므로, 필요 없으면 **[Deny]** 클릭해도 됩니다.

### ❓ "사용 시간을 어떻게 확인하나요?"

GitHub 계정 → [Settings] → [Billing] → [Codespaces]

### ❓ "다른 사람과 공유할 수 있나요?"

네! Codespace 공유 기능:

```
Codespace 창 → [설정] 아이콘 → [Share]
↓
링크 생성 및 복사
↓
링크를 팀원에게 공유
↓
팀원도 같은 Codespace에 접속 가능!
```

---

## 💾 데이터 백업

Codespace의 모든 파일:
- ✅ GitHub에 커밋하면 **자동 백업됨**
- ❌ 커밋하지 않은 파일은 Codespace 삭제 시 사라집니다

**중요한 작업한 후:**
```bash
# 항상 커밋!
git add .
git commit -m "변경 사항"
git push
```

---

## 🎓 팁 & 트릭

### 🎨 테마 변경
```
Codespace 상단 [설정] → [색상 테마] 선택
```

### ⌨️ 단축키
| 단축키 | 기능 |
|--------|------|
| Ctrl + ` | 터미널 열기/닫기 |
| Ctrl + B | 사이드바 토글 |
| Ctrl + K, Ctrl + C | 터미널 정리 |
| Ctrl + Shift + P | 명령 팔레트 |

### 🔍 파일 검색
```
[Ctrl + P] 누르기
↓
파일명 입력
↓
파일이 바로 열림
```

### 🐛 디버깅
VS Code 확장이 자동 설치되므로:
```bash
# F5 키를 누르면 디버거 실행
# (설정 필요할 수 있음)
```

---

## 📚 관련 문서

| 문서 | 내용 |
|------|------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | 빠른 시작 (모든 방법) |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | 로컬 PC 설정 |
| [README.md](./README.md) | 프로젝트 개요 |

---

## 🆘 더 많은 도움이 필요한가요?

- **GitHub Issues**: https://github.com/MediumsKor/LLM_Deliver/issues
- **Codespace 공식 가이드**: https://docs.github.com/en/codespaces
- **VS Code 단축키**: https://code.visualstudio.com/docs/getstarted/keybindings

---

**Happy Coding in the Cloud! ☁️🚀**
