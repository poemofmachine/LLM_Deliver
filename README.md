# Memory Hub (LLM Git)

## 🇰🇷 소개
Memory Hub는 LLM 대화에서 생성되는 [HANDOFF] 블록을 개인용/팀용 Google Docs에 안정적으로 저장하고 재활용할 수 있게 해 주는 “LLM용 git” 플랫폼입니다. FastAPI 서버가 Google OAuth 토큰을 안전하게 관리하고, CLI·브라우저 확장·LLM 오버레이가 `pull/push/diff` 루틴을 자동화합니다. 사용자는 LLM 창에서 `;s`만 입력하면 퀵 패널이 떠서 대상 문서(scope/team)를 고르고, 최신 메모를 가져오거나 곧바로 저장할 수 있습니다.

## 🇺🇸 Overview
Memory Hub is an “LLM-native git” workflow that captures [HANDOFF] blocks from AI chats into personal/team Google Docs with revision locks and categories. A FastAPI backend handles OAuth tokens and revision tracking, while the official CLI and Chromium extension expose git-like `pull/push/diff` flows. Inside ChatGPT, Gemini, Claude, or Grok, typing `;s` opens a quick panel where users choose personal/team docs, fetch the latest memory, and push updates directly through the API.


# 🚀 API Server (v2.2 Hybrid+)

개인용 문서 1개 + 팀별 문서를 동시에 제어하면서 자동 카테고리 태깅/필터링을 제공하는 Apps Script 서버입니다.

- **`code.gs`**: 멀티 문서 라우팅, 리비전 락, 카테고리 파싱, JSON API
- **`ui.html`**: 개인/팀 토글 + 팀 선택 + 세션 동기화 UI

## 🏁 빠른 배포 가이드
1. Google Apps Script 프로젝트를 생성한 뒤 `code.gs`/`ui.html`을 각각 붙여넣습니다.
2. `code.gs` 상단 `DOC_ID`를 기본 개인 문서 ID로 설정합니다.
3. [파일] > [프로젝트 속성] > [스크립트 속성]에서 아래 항목을 설정합니다.
   - `API_TOKEN`: 인증 토큰(예: `C_SECRET_1234`)
   - `DOC_ID_PERSONAL`: 개인용 문서 ID (`DOC_ID`와 동일하면 생략 가능)
   - `TEAM_MAP`: 팀 키 → 문서 ID JSON. 예) `{"alpha":"1DocA","beta":"1DocB"}`
4. [배포] > [새 배포] > [유형: 웹 앱] → 액세스: **모든 사용자(Anonymous)** → URL 복사.

## 💡 API 사용법

배포된 `[웹 앱 URL]`을 기준으로 동작합니다.

### 1. 웹 UI
- `[웹 앱 URL]`
- 상단에서 **개인/팀**을 선택하고, 팀 스코프일 경우 드롭다운에서 팀 키를 고른 뒤 사용합니다.
- “최신 상태 불러오기” → 작업 → “GDoc에 저장” 순으로 동기화합니다.

### 2. 자동 쓰기 (`POST`)
- **URL:** `[웹 앱 URL]?key=TOKEN&scope=personal`  
  - 팀 문서에 쓰려면 `&scope=team&team=alpha`처럼 파라미터 추가
- **Method:** `POST`
- **Body:** `[HANDOFF]...` 텍스트. 서버가 자동으로 `[AUTO_CATEGORY] ...` 라인을 삽입합니다.
- **CLI 업로더:** PC에서는 `python clients/python/push_memory.py --clipboard`로 클립보드 내용을 곧바로 업로드할 수 있습니다. 파일 업로드는 `--file handoff.txt --scope team --team alpha`처럼 사용하세요.

### 3. 자동 읽기 (`GET`)
- **URL:** `[웹 앱 URL]?mode=json&key=TOKEN&scope=team&team=alpha&category=MEETING`
  - `scope` 기본값은 `personal`
  - `team`은 팀 스코프에서 필수
  - `category`는 선택. 값이 있으면 해당 카테고리를 가진 최신 블록만 반환합니다.
- **결과:** 최신 (또는 필터 매칭된) [HANDOFF] 블록을 파싱한 JSON.
- `clients/python/fetch_memory.py`가 이 엔드포인트를 사용하며 `.env`에서 `SCOPE`/`TEAM_KEY`/`CATEGORY_FILTER`를 지정할 수 있습니다.
