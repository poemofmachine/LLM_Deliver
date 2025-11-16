# Memory Hub (LLM Git)

## 🇰🇷 소개
Memory Hub는 LLM 대화에서 생성되는 [HANDOFF] 블록을 개인용/팀용 Google Docs에 안정적으로 저장하고 재활용할 수 있게 해 주는 “LLM용 git” 플랫폼입니다. FastAPI 서버가 Google OAuth 토큰을 안전하게 관리하고, CLI·브라우저 확장·LLM 오버레이가 `pull/push/diff` 루틴을 자동화합니다. 사용자는 LLM 창에서 `;s`만 입력하면 퀵 패널이 떠서 대상 문서(scope/team)를 고르고, 최신 메모를 가져오거나 곧바로 저장할 수 있습니다.

## 🇺🇸 Overview
Memory Hub is an “LLM-native git” workflow that captures [HANDOFF] blocks from AI chats into personal/team Google Docs with revision locks and categories. A FastAPI backend handles OAuth tokens and revision tracking, while the official CLI and Chromium extension expose git-like `pull/push/diff` flows. Inside ChatGPT, Gemini, Claude, or Grok, typing `;s` opens a quick panel where users choose personal/team docs, fetch the latest memory, and push updates directly through the API.


# API Server v2 (FastAPI Prototype)

LLM Git 비전을 위한 참조 서버 스켈레톤입니다. 현재는 FastAPI + Pydantic 기반으로 기본 라우트/스키마와 더미 서비스만 포함합니다.

## 구조
```
api_server_v2/
 └─ app/
     ├─ main.py          # FastAPI 앱 엔트리포인트
     ├─ config.py        # 환경 변수/설정
     ├─ schemas.py       # Pydantic 모델 (OpenAPI와 동일)
     ├─ services/        # 비즈니스 로직 (예: MemoryService)
     └─ routes/          # 세션/워크스페이스/토큰 라우트
```

## 로컬 실행
```
cd api_server_v2
uvicorn app.main:app --reload
```

> 실제 Google Docs 연동/DB는 향후 adapters 추가 시 구현됩니다. 현재는 in-memory mock으로 동작합니다.
