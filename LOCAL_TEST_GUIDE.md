# 🖥️ 로컬 PC에서 Streamlit 대시보드 테스트 가이드

> **Windows / Mac / Linux에서 Memory Hub 대시보드 실행하기**

---

## 📑 목차
1. [준비물](#준비물)
2. [단계별 설정](#단계별-설정)
3. [실행 방법](#실행-방법)
4. [문제 해결](#문제-해결)

---

## 준비물

### ✅ 필요한 것들:

#### 1️⃣ **Git** (프로젝트 다운로드)
- **Windows**: https://git-scm.com/download/win
- **Mac**: https://git-scm.com/download/mac
- **Linux**: `sudo apt-get install git`

**확인:**
```bash
git --version
# 예상 출력: git version 2.40.0
```

---

#### 2️⃣ **Python 3.10 이상**
- **다운로드**: https://www.python.org/downloads/

**확인:**
```bash
python --version
# 또는
python3 --version
# 예상 출력: Python 3.11.0
```

> ⚠️ **Windows 사용자**: 설치 시 "Add Python to PATH" 반드시 ✅ 체크!

---

#### 3️⃣ **코드 에디터** (선택사항이지만 권장)
- **VS Code**: https://code.visualstudio.com/
- 또는 메모장/텍스트 에디터

---

## 단계별 설정

### 1️⃣ 프로젝트 다운로드

#### **Windows (명령 프롬프트 또는 PowerShell):**

```bash
# 1. 작업할 폴더로 이동 (예: 문서)
cd Documents

# 2. 프로젝트 복제
git clone https://github.com/MediumsKor/LLM_Deliver.git

# 3. 프로젝트 폴더로 이동
cd LLM_Deliver
```

#### **Mac / Linux (터미널):**

```bash
# 1. 작업할 폴더로 이동
cd ~/Documents

# 2. 프로젝트 복제
git clone https://github.com/MediumsKor/LLM_Deliver.git

# 3. 프로젝트 폴더로 이동
cd LLM_Deliver
```

---

### 2️⃣ Python 가상 환경 생성

#### **Windows:**

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
venv\Scripts\activate
```

#### **Mac / Linux:**

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate
```

**성공 확인:**
```
(venv) C:\Users\YourName\LLM_Deliver>  # Windows
(venv) username@mac:LLM_Deliver %      # Mac
```

프롬프트 앞에 `(venv)` 가 보이면 성공! ✅

---

### 3️⃣ 의존성 설치

```bash
# Streamlit과 필요한 패키지 설치
pip install streamlit requests python-dotenv pyperclip
```

또는 requirements.txt 사용:

```bash
# clients/python 디렉토리의 requirements.txt 사용
pip install -r clients/python/requirements.txt
```

**설치 확인:**
```bash
streamlit --version
# 예상 출력: Streamlit, version 1.28.0
```

---

## 실행 방법

### 🎯 **가장 간단한 방법 (추천)**

#### **1단계: Streamlit 대시보드 실행**

```bash
# 프로젝트 루트 디렉토리에서
streamlit run clients/streamlit_dashboard_simple.py
```

#### **2단계: 자동으로 브라우저 열기**

명령을 실행하면 자동으로 브라우저가 열립니다:

```
Local URL: http://localhost:8501
```

만약 자동으로 열리지 않으면, 브라우저 주소창에:
```
http://localhost:8501
```

를 입력하세요.

---

### ✅ 성공 화면

대시보드가 열리면 다음이 보입니다:

```
🧠 Memory Hub Dashboard

[📤 메모 저장] [📥 메모 불러오기] [🏢 워크스페이스] [📊 프로세스 흐름도]
```

---

## 🧪 각 기능 테스트

### 📤 **메모 저장 테스트**

1. **"📤 메모 저장"** 탭 클릭
2. 워크스페이스 이름 입력 (예: "개인 작업")
3. 저장 위치 선택 (personal 또는 team)
4. 메모 텍스트 입력:
   ```
   [HANDOFF]
   이것은 테스트 메모입니다.
   Streamlit 대시보드를 테스트 중입니다.
   ```
5. **"💾 Google Docs에 저장"** 버튼 클릭
6. 프로세스 흐름 확인:
   ```
   ✅ 📝 메모 유효성 검사
   ✅ 🔐 인증 확인
   ✅ 💾 로컬 DB 저장
   ✅ ☁️ Google Docs 동기화
   ✅ ✅ 저장 완료!

   🎉 메모가 성공적으로 저장되었습니다!
   ```

---

### 📥 **메모 불러오기 테스트**

1. **"📥 메모 불러오기"** 탭 클릭
2. 워크스페이스 이름 입력 (위에서 사용한 이름과 동일)
3. 불러올 위치 선택
4. **"📥 메모 불러오기"** 버튼 클릭
5. 진행 과정 확인:
   ```
   🔐 인증 확인 | ☁️ Google Docs 조회 | 📊 메타데이터 파싱 | ✅ 완료
   ```

---

### 🏢 **워크스페이스 관리 테스트**

1. **"🏢 워크스페이스"** 탭 클릭
2. 예시 워크스페이스 목록 확인
3. 새 워크스페이스 입력:
   - 이름: "팀 마케팅"
   - 스코프: team
4. **"생성"** 버튼 클릭
5. 성공 메시지 확인:
   ```
   ✅ '팀 마케팅' 워크스페이스 생성됨!
   ```

---

### 📊 **프로세스 흐름도 확인**

1. **"📊 프로세스 흐름도"** 탭 클릭
2. PUSH/PULL 흐름도 시각화 확인:
   ```
   📤 PUSH:
   입력 → 유효성 검사 → 인증 확인 → DB 저장 → Google Docs 동기화 → 완료

   📥 PULL:
   요청 → 인증 확인 → Google Docs 조회 → 메타데이터 파싱 → 완료
   ```

---

## 🚀 다음 단계: FastAPI 서버 연결 (선택사항)

현재 Streamlit 대시보드는 **시뮬레이션 모드**로 작동합니다.

실제 Google Docs 연동을 위해 **FastAPI 서버**를 연결할 수 있습니다:

### **Step 1: 다른 터미널에서 FastAPI 서버 실행**

```bash
# 프로젝트의 api_server_v2 디렉토리로 이동
cd api_server_v2

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload
```

**성공 메시지:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### **Step 2: 환경 설정**

프로젝트 루트에서 `.env` 파일 생성:

```env
# Google Docs ID
DOC_ID="당신의Google Docs ID"

# Google Apps Script 웹 앱 URL
WEBAPP_URL="https://script.google.com/macros/s/XXXXX/exec"

# API 토큰
API_TOKEN="C_SECRET_1234"
```

### **Step 3: Streamlit 대시보드에서 확인**

대시보드 화면 상단에:
```
✅ 서버 연결됨 | 🔗 http://localhost:8000 | ✅ API 토큰 설정됨
```

이 표시되면 완전한 연동입니다! 🎉

---

## 🔧 Streamlit 커맨드 팁

### **포트 변경** (8501이 이미 사용 중인 경우)

```bash
streamlit run clients/streamlit_dashboard_simple.py --server.port=8502
```

그 후 `http://localhost:8502` 접속

### **로깅 활성화** (디버깅용)

```bash
streamlit run clients/streamlit_dashboard_simple.py --logger.level=debug
```

### **전체 IP에서 접속 허용** (네트워크 공유)

```bash
streamlit run clients/streamlit_dashboard_simple.py \
  --server.address=0.0.0.0 \
  --server.port=8501
```

다른 컴퓨터에서:
```
http://당신의PC_IP:8501
```

---

## 🐛 문제 해결

### ❓ "streamlit: 명령을 찾을 수 없습니다"

**원인**: Streamlit이 설치되지 않거나 가상 환경이 활성화되지 않음

**해결:**
```bash
# 1. 가상 환경 활성화 확인
# (venv) 가 보여야 함

# 2. 다시 설치
pip install streamlit

# 3. 버전 확인
streamlit --version
```

---

### ❓ "포트 8501이 이미 사용 중입니다"

**해결:**
```bash
# 다른 포트 사용
streamlit run clients/streamlit_dashboard_simple.py --server.port=8502
```

---

### ❓ "ModuleNotFoundError: No module named 'streamlit'"

**원인**: 의존성이 설치되지 않음

**해결:**
```bash
# 1. 가상 환경 활성화 확인
# (venv) 가 보여야 함

# 2. 의존성 설치
pip install -r clients/python/requirements.txt

# 또는
pip install streamlit requests python-dotenv pyperclip
```

---

### ❓ "git: 명령을 찾을 수 없습니다"

**원인**: Git이 설치되지 않음

**해결**: https://git-scm.com/downloads 에서 설치

---

### ❓ "Python을 찾을 수 없습니다"

**Windows 사용자:**
1. Python 다시 설치
2. "Add Python to PATH" ✅ 반드시 체크
3. PC 재부팅

**Mac/Linux 사용자:**
```bash
# python 대신 python3 사용
python3 --version
python3 -m venv venv
source venv/bin/activate
```

---

## 📚 추가 리소스

| 문서 | 내용 |
|------|------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | 빠른 시작 (모든 방법) |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | 로컬 PC 상세 가이드 |
| [STREAMLIT_DASHBOARD.md](./STREAMLIT_DASHBOARD.md) | Streamlit 완전 가이드 |
| [PROCESS_VISUALIZATION_METHODS.md](./PROCESS_VISUALIZATION_METHODS.md) | 시각화 방법 비교 |

---

## ✅ 체크리스트

로컬 PC에서 준비한 것들:

- [ ] Git 설치 (`git --version` 확인)
- [ ] Python 3.10+ 설치 (`python --version` 확인)
- [ ] 프로젝트 복제 (`git clone`)
- [ ] 가상 환경 생성 (`python -m venv venv`)
- [ ] 가상 환경 활성화 (`(venv)` 확인)
- [ ] 의존성 설치 (`pip install streamlit`)
- [ ] Streamlit 실행 (`streamlit run`)
- [ ] 브라우저에서 확인 (`http://localhost:8501`)

---

## 🎉 완료!

**축하합니다!** 로컬 PC에서 Memory Hub Streamlit 대시보드를 실행했습니다!

이제 다음을 할 수 있습니다:

1. ✅ 메모 저장/불러오기 프로세스 시각화 확인
2. ✅ 워크스페이스 관리
3. ✅ 프로세스 흐름도 확인
4. ✅ (선택사항) FastAPI 서버 연동

---

## 💬 피드백

문제가 발생하거나 질문이 있으시면:

GitHub Issues: https://github.com/MediumsKor/LLM_Deliver/issues

---

**Happy Testing! 🚀✨**
