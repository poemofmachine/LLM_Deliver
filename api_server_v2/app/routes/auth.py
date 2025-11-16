# api_server_v2/app/routes/auth.py (완전 수정본)

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from ..db import repository # (필수) db.py의 repository 임포트

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# 1. client_secrets.json 파일 경로 확인!
CLIENT_SECRETS_FILE = "client_secrets.json" # (api_server_v2/ 폴더에 위치)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]
REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"


@router.get("/google")
async def auth_google(request: Request, workspace_id: str):
    """
    사용자를 Google 로그인 페이지로 리디렉션시킵니다.
    """
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    except FileNotFoundError:
        return {"detail": f"'{CLIENT_SECRETS_FILE}' 파일을 찾을 수 없습니다."}

    # [핵심 수정 1]
    # state 값을 CSRF용 랜덤 문자열 대신,
    # workspace_id 자체로 사용합니다. (테스트용)
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=workspace_id, # <--- state에 workspace_id를 담아서 보냅니다.
        prompt='consent'   # [추가!] '권한 허용' 화면을 매번 강제로 띄웁니다.
    )
    
    print(f"인증 시도 워크스페이스: {workspace_id} (state로 전달)")
    return RedirectResponse(authorization_url)


@router.get("/google/callback")
async def auth_google_callback(request: Request, code: str, state: str):
    """
    Google이 사용자를 이 주소로 리디렉션 (토큰 교환)
    """
    
    # [핵심 수정 2]
    # Google이 'state' 값을 그대로 돌려주므로,
    # 이 state 값이 바로 우리가 인증하려던 workspace_id 입니다.
    workspace_id = state 
    
    print(f"콜백 수신. state(workspace_id): {workspace_id}")

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        token_json = credentials.to_json()

        # (핵심!) 이제 올바른 ID로 저장됩니다.
        print(f"DB에 토큰 저장 시도 (Workspace: {workspace_id})")
        repository.save_google_token(workspace_id, token_json) 
        
        return {"message": "인증 성공! 토큰이 성공적으로 발급/저장되었습니다."}

    except Exception as e:
        print(f"토큰 교환 오류: {e}")
        return {"error": "인증에 실패했습니다.", "details": str(e)}