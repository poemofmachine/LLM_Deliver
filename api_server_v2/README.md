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
