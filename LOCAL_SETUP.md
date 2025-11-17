# 💻 로컬 PC 개발 환경 설정 가이드

> **Windows / Mac / Linux에서 로컬 개발 환경 구성하기**

---

## 📑 목차
1. [준비물](#준비물)
2. [설치 단계](#설치-단계)
3. [프로젝트 실행](#프로젝트-실행)
4. [문제 해결](#문제-해결)

---

## 준비물

### ✅ 필수 설치 프로그램

#### 1️⃣ Python 3.10 이상
**다운로드**: https://www.python.org/downloads/

**설치 후 확인**:
```bash
python --version
# 또는
python3 --version
```

예상 출력:
```
Python 3.11.0
```

> ⚠️ **Windows 사용자 주의:**
> 설치 마지막 화면에서 "**Add Python to PATH**" 체크박스를 반드시 ✅ 확인하세요!

---

#### 2️⃣ Git
**다운로드**: https://git-scm.com/download

**설치 후 확인**:
```bash
git --version
```

예상 출력:
```
git version 2.40.0
```

---

#### 3️⃣ 코드 에디터 (선택사항이지만 권장)
**추천: VS Code**
https://code.visualstudio.com/

**VS Code 확장 설치 (권장)**:
1. VS Code 열기
2. 왼쪽 사이드바 [확장] 클릭
3. 다음 검색 후 설치:
   - `Python` (Microsoft)
   - `Pylance` (Microsoft)
   - `Black Formatter` (Microsoft)

---

## 설치 단계

### 1️⃣ 프로젝트 다운로드

#### **방법 A: Git 명령어 (권장)**

**1. 터미널/명령 프롬프트 열기**

**Windows**:
```
Windows 메뉴 → "cmd" 검색 → [Command Prompt] 열기
또는: [Windows 키 + R] → "cmd" 입력 → [Enter]
```

**Mac**:
```
[Cmd + Space] → "terminal" 검색 → [Enter]
```

**Linux**:
```
[Ctrl + Alt + T] (또는 응용프로그램 → 터미널)
```

**2. 프로젝트 디렉토리로 이동**
```bash
# 작업할 폴더로 이동 (예: 문서 폴더)
# Windows
cd Documents

# Mac/Linux
cd ~/Documents
```

**3. 프로젝트 복제**
```bash
git clone https://github.com/MediumsKor/LLM_Deliver.git
cd LLM_Deliver
```

#### **방법 B: 수동 다운로드**

1. GitHub 페이지 방문: https://github.com/MediumsKor/LLM_Deliver
2. [<> Code] 버튼 → [Download ZIP]
3. 파일 압축 해제
4. 터미널에서 해당 폴더로 이동

---

### 2️⃣ Python 가상 환경 생성

**가상 환경이란?**
> 이 프로젝트만을 위한 독립적인 Python 환경입니다.
> 다른 프로젝트의 라이브러리와 겹치지 않습니다.

#### **Windows에서:**
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
venv\Scripts\activate
```

#### **Mac/Linux에서:**
```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate
```

**성공 확인**:
```
(venv) C:\Users\YourName\LLM_Deliver>  # Windows
(venv) username@mac:LLM_Deliver %      # Mac
```

> 프롬프트 앞에 `(venv)`가 보이면 성공! ✅

---

### 3️⃣ Python 패키지 업그레이드 (선택사항)

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# setuptools 업그레이드
python -m pip install --upgrade setuptools
```

---

### 4️⃣ FastAPI 서버 의존성 설치

```bash
# api_server_v2 디렉토리로 이동
cd api_server_v2

# 필수 패키지 설치
pip install -r requirements.txt
```

**설치 중 화면 예시**:
```
Collecting fastapi==0.104.1
  Downloading fastapi-0.104.1-py3-none-any.whl (92 kB)
Installing collected packages: pydantic, uvicorn, fastapi, ...
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**설치 완료 확인**:
```bash
python -c "import fastapi; print(fastapi.__version__)"
# 예상 출력: 0.104.1
```

> ⏳ 첫 설치는 1-2분 정도 걸립니다.

---

### 5️⃣ Python 클라이언트 의존성 설치

```bash
# 프로젝트 루트로 이동
cd ..

# 클라이언트 패키지 설치
cd clients/python
pip install -r requirements.txt
```

**필수 패키지**:
- `python-dotenv`: 환경 변수 관리
- `pyperclip`: 클립보드 접근

---

### 6️⃣ 환경 설정 파일 생성

```bash
# 프로젝트 루트로 돌아가기
cd ../..

# 예시 파일 복사
cp .env.example .env
# Windows의 경우:
# copy .env.example .env
```

**`.env` 파일 편집**:

**Windows**:
```
탐색기 → LLM_Deliver 폴더 → .env 파일 → 마우스 오른쪽 클릭 → [열기] → 메모장
```

**Mac**:
```bash
open -e .env
# 또는 VS Code 사용: code .env
```

**Linux**:
```bash
nano .env
# 또는 VS Code 사용: code .env
```

**파일 내용 작성**:
```env
# Google Docs ID
# URL 예: https://docs.google.com/document/d/1a2b3c4d5e6f/edit
#         여기가 ID ↑
DOC_ID="1a2b3c4d5e6f7g8h9i0j"

# Google Apps Script 웹 앱 URL
# Google Apps Script 배포 후 받은 URL
WEBAPP_URL="https://script.google.com/macros/s/XXXXX/exec"

# 인증 토큰
# Google Apps Script 프로젝트 속성에서 설정한 토큰
API_TOKEN="C_SECRET_1234"
```

> 💾 **저장하기:**
> - Windows: [Ctrl + S]
> - Mac: [Cmd + S]
> - Linux: [Ctrl + S] (nano) 또는 에디터 메뉴

---

## 프로젝트 실행

### 🚀 FastAPI 서버 시작

**Step 1: api_server_v2 디렉토리로 이동**
```bash
cd api_server_v2
```

**Step 2: 서버 실행**
```bash
uvicorn app.main:app --reload
```

**성공 메시지**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

> 🎉 서버가 실행 중입니다!

---

### 📖 브라우저에서 확인

**Step 1: 브라우저 열기** (Chrome, Firefox, Safari 등)

**Step 2: 주소창에 입력**
```
http://localhost:8000/docs
```

**Step 3: 아름다운 API 문서 확인** 📚

```
Swagger UI 페이지가 표시됩니다:
- API 엔드포인트 목록
- 각 API의 상세 설명
- [Try it out] 버튼으로 직접 테스트 가능
```

---

### 🔄 서버 중지

```bash
# 터미널에서:
# [Ctrl + C] 키 조합
```

> 깨끗하게 종료됩니다. ✅

---

### 📤 메모 저장하기

**Step 1: 새 터미널 열기**
```
기존 서버 터미널은 그대로 두고
새로운 터미널 창 열기
```

**Step 2: 클라이언트 디렉토리로 이동**
```bash
cd clients/python
```

**Step 3: 메모 저장**

#### **방법 1: 클립보드에서 저장** (추천)
```bash
python push_memory.py --clipboard
```

> 먼저 텍스트를 복사([Ctrl + C])한 후 실행하세요

#### **방법 2: 파일에서 저장**
```bash
# 먼저 notes.txt 파일을 생성하고 내용 작성
# 그 후:
python push_memory.py --file notes.txt --scope personal
```

#### **방법 3: 팀 문서에 저장**
```bash
python push_memory.py --clipboard --scope team --team alpha
```

**성공 메시지**:
```
✅ 메모가 Google Docs에 저장되었습니다!
```

---

### 📥 저장된 메모 불러오기

```bash
cd clients/python
python fetch_memory.py
```

**출력**:
```
[최근 저장된 메모]
[HANDOFF]
...메모 내용...
```

---

### 🧪 테스트 실행

```bash
# 프로젝트 루트에서
pytest clients/python/tests/ -v

# 예상 결과:
# tests/test_conflict_flow.py::test_example PASSED
# ============== 1 passed in 0.05s ==============
```

---

## 문제 해결

### ❓ "Python을 찾을 수 없습니다"

**확인사항**:
1. Python 설치 확인
   ```bash
   python --version
   ```

2. Windows 사용자: PATH 설정 확인
   ```
   설정 → 시스템 → 정보 → 고급 시스템 설정
   → 환경 변수 → Path에 Python 경로 확인
   ```

3. 재부팅 후 재시도

---

### ❓ "pip install이 실패해요"

**해결 방법**:

```bash
# 1. pip 업그레이드
python -m pip install --upgrade pip

# 2. requirements.txt 경로 확인
ls requirements.txt  # 파일이 있어야 함

# 3. 다시 시도
pip install -r requirements.txt
```

**특정 패키지만 설치**:
```bash
pip install fastapi uvicorn pydantic
```

---

### ❓ "uvicorn: 명령을 찾을 수 없습니다"

**확인사항**:
1. 가상 환경 활성화 확인
   ```bash
   # (venv)가 보여야 함
   ```

2. 의존성 설치 확인
   ```bash
   pip list | grep uvicorn
   ```

3. 다시 설치
   ```bash
   pip install uvicorn
   ```

---

### ❓ "포트 8000이 이미 사용 중입니다"

**원인**: 다른 프로그램이 포트 8000을 사용 중

**해결법**:

#### **Windows**:
```bash
# 포트 8000을 사용하는 프로세스 찾기
netstat -ano | findstr :8000

# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

#### **Mac/Linux**:
```bash
# 포트 8000을 사용하는 프로세스 찾기
lsof -i :8000

# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

---

### ❓ "ModuleNotFoundError: No module named 'fastapi'"

**확인**:
1. 가상 환경 활성화됨?
   ```bash
   # (venv) 표시 확인
   ```

2. 올바른 폴더?
   ```bash
   # api_server_v2 폴더에 있어야 함
   pwd  # 또는 cd를 통해 경로 확인
   ```

3. 의존성 설치?
   ```bash
   pip install -r requirements.txt
   ```

---

### ❓ "Google Docs에 저장이 안 돼요"

**확인사항**:

1. `.env` 파일 확인
   ```bash
   # 파일이 프로젝트 루트에 있어야 함
   ls -la .env  # Mac/Linux
   dir .env     # Windows
   ```

2. `.env` 파일 내용 확인
   ```env
   DOC_ID="실제 ID 입력?" # ✅ 빈 칸이면 안 됨
   WEBAPP_URL="URL 입력?"
   API_TOKEN="토큰 입력?"
   ```

3. Google Docs ID 확인
   ```
   URL: https://docs.google.com/document/d/1a2b3c4d5/edit
                                         ↑ 이 부분만 DOC_ID에
   ```

4. Google Apps Script 배포 확인
   - Google Apps Script 프로젝트 확인
   - "배포" > "웹 앱"으로 배포됨?

---

### ❓ "git clone이 실패해요"

```bash
# Git 설치 확인
git --version

# 인터넷 연결 확인
ping github.com

# HTTPS 대신 SSH 사용 (GitHub SSH 키 설정 필요)
git clone git@github.com:MediumsKor/LLM_Deliver.git
```

---

### ❓ "가상 환경을 해제하려면?"

```bash
# Windows
deactivate

# Mac/Linux
deactivate
```

> 프롬프트에서 `(venv)` 표시가 사라집니다.

---

### ❓ "가상 환경을 다시 활성화하려면?"

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

## 📚 유용한 명령어

| 명령어 | 설명 |
|--------|------|
| `pip list` | 설치된 패키지 목록 |
| `pip install -U package` | 패키지 업그레이드 |
| `pip uninstall package` | 패키지 제거 |
| `python -m pip check` | 의존성 문제 확인 |
| `deactivate` | 가상 환경 종료 |

---

## 🎓 다음 단계

✅ 로컬 개발 환경 설정 완료!

다음으로:
1. 코드 수정 및 테스트
2. Git으로 변경사항 커밋
3. GitHub에 푸시

---

## 📚 관련 문서

| 문서 | 내용 |
|------|------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | 빠른 시작 (모든 방법) |
| [CODESPACE_SETUP.md](./CODESPACE_SETUP.md) | Codespace 설정 |
| [README.md](./README.md) | 프로젝트 개요 |
| [api_server_v2/README.md](./api_server_v2/README.md) | API 서버 상세 문서 |

---

## 🆘 더 많은 도움

**문제가 해결되지 않으셨나요?**

GitHub Issues에 질문하기:
https://github.com/MediumsKor/LLM_Deliver/issues

다음 정보를 포함해주세요:
- 운영체제 (Windows/Mac/Linux)
- 에러 메시지 (스크린샷)
- 실행한 명령어

---

**Happy Local Development! 🚀💻**
