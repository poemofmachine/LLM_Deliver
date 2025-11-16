from fastapi import FastAPI

from .config import settings
from .routes import sessions, tokens, workspaces
from .routes import auth  # 1. 방금 만든 auth 라우터 임포트

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Reference FastAPI implementation for Memory Hub v2",
)

app.include_router(workspaces.router)
app.include_router(sessions.router)
app.include_router(tokens.router)
app.include_router(auth.router)  # 2. auth 라우터 포함


@app.get("/health")
def health_check():
    return {"status": "ok"}
