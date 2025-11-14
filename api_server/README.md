# 🚀 API Server (v2.2 Hybrid)

이 스크립트는 GDoc 메모리 시스템을 위한 '웹 UI'와 '자동화 API'를 모두 제공합니다.

- **`code.gs`**: 핵심 서버 로직 (v2.2)
- **`ui.html`**: `doGet(mode=ui)`로 접근 시 보여줄 웹페이지

## 🏁 빠른 배포 가이드
1.  Google Apps Script (script.google.com)에서 새 프로젝트를 생성합니다.
2.  `code.gs` 파일의 내용을 복사하여 붙여넣습니다.
3.  **[+ 파일 추가]** 버튼을 눌러 **[HTML]**을 선택하고, 파일 이름을 `ui`로 지정합니다. (`ui.html`)
4.  `ui.html` 파일의 내용을 복사하여 붙여넣습니다.
5.  `code.gs` 파일 상단의 `DOC_ID` 변수를 자신의 GDoc ID로 수정합니다.
6.  **[중요] API 토큰 설정 (보안):**
    * [파일] > [프로젝트 속성] > [스크립트 속성] 탭으로 이동합니다.
    * `API_TOKEN` 이라는 속성을 추가하고, 값에 C님만의 **비밀번호** (예: `C_SECRET_1234`)를 입력하고 저장합니다.
7.  [배포] > [새 배포] > [유형: 웹 앱]을 선택합니다.
8.  [액세스 권한] > **[모든 사용자(Anonymous)]**로 설정합니다.
9.  [배포]를 눌러 생성된 **웹 앱 URL**을 복사합니다.

## 💡 API 사용법

배포된 `[웹 앱 URL]`을 기준으로 작동합니다.

### 1. 웹 UI 사용 (브라우저)
- `[웹 앱 URL]` (파라미터 없음)
- 핸드오프 텍스트를 붙여넣고 [저장] 버튼을 누릅니다.

### 2. 자동화 '쓰기' (Tasker/Python `POST`)
- **URL:** `[웹 앱 URL]?key=[API_TOKEN]`
- **Method:** `POST`
- **Body (Text/Plain):** `[HANDOFF]...` 블록 텍스트
- Tasker의 'HTTP Post' 또는 Python의 `requests.post()`로 사용합니다.

### 3. 자동화 '읽기' (Tasker/Python `GET`)
- **URL:** `[웹 앱 URL]?mode=json&key=[API_TOKEN]`
- **Method:** `GET`
- **결과:** GDoc의 최신 블록을 파싱한 **JSON**을 반환합니다.
- `clients/python/fetch_memory.py` 스크립트가 이 주소를 사용합니다.