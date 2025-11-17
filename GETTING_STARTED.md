# 🚀 Memory Hub (LLM Git) - 빠른 시작 가이드

> **초보자도 5분 안에 시작할 수 있는 완전 가이드**

---

## 📖 목차
1. [이것이 뭔가요?](#이것이-뭔가요)
2. [시작하기 - 3가지 방법](#시작하기---3가지-방법)
3. [첫 번째 사용](#첫-번째-사용)
4. [자주 묻는 질문](#자주-묻는-질문)

---

## 이것이 뭔가요?

**Memory Hub**는 ChatGPT, Claude, Gemini 같은 LLM(AI)과의 대화에서 중요한 내용을 자동으로 **Google Docs에 저장**하고 **재사용**할 수 있는 도구입니다.

### 🎯 할 수 있는 것들:
- ✅ AI와의 대화 중에 중요한 메모 빠르게 저장
- ✅ 팀원들과 메모 공유
- ✅ 예전에 저장한 메모 다시 불러오기
- ✅ 메모에 태그/카테고리 자동 추가

### 🔄 동작 방식 (3단계)
```
[AI 대화 창]
     ↓
  ;s 입력 (저장 명령)
     ↓
[퀵 패널] → 대상 문서 선택
     ↓
[Google Docs에 자동 저장] ✅
```

---

## 시작하기 - 3가지 방법

### 방법 1️⃣: GitHub Codespace (클릭만 하면 완료! 🎉)

**가장 쉬운 방법** - 클라우드에서 바로 사용

#### 준비물:
- ✅ GitHub 계정 (이미 있으신 경우)
- ✅ 웹 브라우저

#### 단계별 가이드:

**1단계: Codespace 열기**
```
GitHub 저장소 페이지
  ↓
[<> Code] 버튼 클릭
  ↓
[Codespace 탭] 클릭
  ↓
[+ Create codespace on main] 클릭
  ↓
기다리세요... ⏳ (1-2분)
```

> 💡 **Codespace란?** 브라우저에서 바로 VS Code를 사용할 수 있는 클라우드 개발 환경입니다.

**2단계: 자동 설정**
- Codespace 생성 후 자동으로 설정됨
- 터미널에 다음 메시지가 보이면 완료:
```
✅ Setup Complete!
```

**3단계: FastAPI 서버 실행**
```bash
# 터미널 1 - FastAPI 서버 실행
cd api_server_v2
uvicorn app.main:app --reload --port 8000
```

> 화면에 다음이 보이면 성공:
> ```
> Uvicorn running on http://127.0.0.1:8000
> ```

**4단계: 브라우저에서 확인**
- 새 터미널 열기: [Ctrl + `]
- 또는 브라우저에서:
  ```
  http://localhost:8000/docs
  ```
  를 입력하면 API 문서가 보입니다! 🎉

---

### 방법 2️⃣: 로컬 PC (Windows/Mac/Linux)

**내 컴퓨터에서 개발하고 싶을 때**

#### 준비물:
- ✅ Python 3.10 이상 ([다운로드](https://www.python.org/downloads/))
- ✅ Git ([다운로드](https://git-scm.com/download))
- ✅ 코드 에디터 (VS Code 권장, [다운로드](https://code.visualstudio.com/))

#### 설치 단계:

**1단계: 프로젝트 다운로드**
```bash
# 터미널/명령 프롬프트 열기
git clone https://github.com/MediumsKor/LLM_Deliver.git
cd LLM_Deliver
```

**2단계: Python 가상 환경 만들기**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

> 💡 **가상 환경이란?** 이 프로젝트만을 위한 독립적인 Python 환경입니다.
> 명령 프롬프트 앞에 `(venv)` 가 보이면 성공!

**3단계: 의존성 설치**
```bash
# FastAPI 및 필요한 라이브러리 설치
cd api_server_v2
pip install -r requirements.txt

# 클라이언트 라이브러리 설치
cd ../clients/python
pip install -r requirements.txt
```

> ⏳ 1-2분 정도 걸립니다.

**4단계: 환경 설정 파일 만들기**
```bash
# 프로젝트 루트로 이동
cd ..
cd ..

# 예시 파일로부터 복사
cp .env.example .env

# .env 파일 열기 (VS Code 또는 메모장)
# 아래 부분을 채우세요:
#   DOC_ID: 당신의 Google Docs ID
#   WEBAPP_URL: Google Apps Script 웹 앱 URL
#   API_TOKEN: 인증 토큰
```

**5단계: FastAPI 서버 실행**
```bash
cd api_server_v2
uvicorn app.main:app --reload
```

> 💻 화면에 이렇게 보이면 성공:
> ```
> Uvicorn running on http://127.0.0.1:8000
> ```

**6단계: 브라우저에서 확인**
```
http://localhost:8000/docs
```

---

### 방법 3️⃣: Docker (모든 환경 자동 설정)

**가장 깔끔한 방법** - 모든 설정이 컨테이너에 포함됨

#### 준비물:
- ✅ Docker Desktop ([다운로드](https://www.docker.com/products/docker-desktop))
- ✅ Git

#### 설정 단계:

**1단계: Dockerfile 확인**
```bash
git clone https://github.com/MediumsKor/LLM_Deliver.git
cd LLM_Deliver
```

**2단계: Docker 이미지 빌드**
```bash
docker build -t memoryhub:latest .
```

**3단계: Docker 컨테이너 실행**
```bash
docker run -p 8000:8000 -e PYTHONUNBUFFERED=1 memoryhub:latest
```

> 🎉 `http://localhost:8000`에서 접속 가능!

---

## 첫 번째 사용

### 1️⃣ Google Docs 준비하기

> **구글 계정 필요** (Gmail 주소가 있으면 OK)

**1단계: Google Docs 생성**
```
https://docs.google.com/document/create
  ↓
새 문서 생성 (제목: "Memory Hub - 개인용")
  ↓
문서의 URL 복사
예시: https://docs.google.com/document/d/[여기가 ID]/edit
```

**2단계: Google Apps Script 설정** (선택사항)
- 현재 `api_server` 폴더에 `code.gs` 파일 있음
- Google Apps Script 프로젝트를 만들어 배포 필요
- 자세한 방법은 [여기](./api_server/README.md)를 참조

### 2️⃣ 환경 설정 파일 작성

`.env` 파일을 열어서:

```env
# Google Docs ID
# URL에서: https://docs.google.com/document/d/[이 부분]/edit
DOC_ID="1a2b3c4d5e6f7g8h9i0j"

# Google Apps Script 웹 앱 URL
WEBAPP_URL="https://script.google.com/macros/s/XXXXX/exec"

# 인증 토큰 (Google Apps Script에 설정한 값)
API_TOKEN="C_SECRET_1234"
```

### 3️⃣ Python CLI로 테스트

```bash
# 클립보드에서 읽어서 저장
cd clients/python
python push_memory.py --clipboard

# 또는 파일에서 읽어서 저장
python push_memory.py --file my_notes.txt --scope personal

# 저장된 내용 불러오기
python fetch_memory.py
```

### 4️⃣ API로 테스트

터미널에서:
```bash
# 간단한 GET 요청 (저장된 메모 가져오기)
curl "http://localhost:8000/health"
```

브라우저에서:
```
http://localhost:8000/docs
```
→ "Try it out" 버튼으로 API 테스트 가능!

---

## 자주 묻는 질문

### ❓ "Python이 뭔가요?"
파이썬(Python)은 프로그래밍 언어입니다. 이 프로젝트에서는:
- 백엔드 서버 작동 (FastAPI)
- 메모 저장/불러오기 (Python CLI)
에 사용됩니다.

### ❓ "Codespace가 자꾸 끊겨요"
**해결법:**
1. 브라우저 새로고침 [Ctrl + R]
2. Codespace 다시 열기 (GitHub 페이지에서)
3. 여전히 안 되면 Codespace 삭제 후 다시 만들기

### ❓ "로컬에서 `pip install` 실패해요"
```bash
# 1. Python 버전 확인 (3.10 이상 필요)
python --version

# 2. pip 업그레이드
python -m pip install --upgrade pip

# 3. 다시 시도
pip install -r requirements.txt
```

### ❓ "Google Docs에 저장이 안 돼요"
**확인사항:**
1. `.env` 파일의 `DOC_ID` 확인
2. Google Apps Script 배포 확인
3. `API_TOKEN` 확인
4. Google Docs 접근 권한 확인 (본인 계정으로 생성한 문서인가?)

### ❓ "벌써 저장된 메모가 있는데, 어떻게 불러와요?"
```bash
cd clients/python
python fetch_memory.py
```
→ 최근 저장된 메모가 터미널에 출력됩니다

### ❓ "팀원들과 공유하려면?"
```bash
# 팀 문서에 저장
python push_memory.py --clipboard --scope team --team alpha

# 팀 문서에서 불러오기
python fetch_memory.py --scope team --team alpha
```

> `.env` 파일에서 `TEAM_MAP` 설정 필요
> 예: `{"alpha":"1DocA","beta":"1DocB"}`

---

## 🎓 다음 단계

✅ 성공했으신가요? 축하합니다! 🎉

다음으로 할 수 있는 것들:

1. **브라우저 확장 설치** → ChatGPT/Claude 창에서 `;s` 입력하면 저장 가능
2. **브라우저 확장 개발** → `extension/` 폴더 참조
3. **API 커스터마이징** → `api_server_v2/` 코드 수정

---

## 📚 더 많은 정보

| 문서 | 내용 |
|------|------|
| [README.md](./README.md) | 프로젝트 전체 개요 |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | 로컬 개발 환경 상세 가이드 |
| [CODESPACE_SETUP.md](./CODESPACE_SETUP.md) | Codespace 완전 가이드 |
| [api_server_v2/README.md](./api_server_v2/README.md) | API 서버 문서 |

---

## ❤️ 문제가 생겼나요?

```
GitHub Issues: https://github.com/MediumsKor/LLM_Deliver/issues
```

위 링크에서 새 이슈를 생성해주세요. 자세히 설명할수록 더 빨리 해결됩니다!

---

**Happy Coding! 🚀**
