from fastapi import APIRouter, HTTPException

from ..schemas import SessionCreateRequest, SessionResponse
from ..services.memory import memory_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/latest", response_model=SessionResponse | None)
def latest_session(workspace_id: str, scope: str, team_key: str | None = None, category: str | None = None):
    session = memory_service.latest_session(workspace_id, scope, team_key, category)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return session


@router.post("", response_model=SessionResponse, responses={409: {"description": "Conflict"}})
def create_session(payload: SessionCreateRequest):
    result = memory_service.create_session(payload)
    if hasattr(result, "status") and getattr(result, "status") == "CONFLICT":
        raise HTTPException(
            status_code=409,
            detail={
                "status": result.status,
                "expected_revision": result.expected_revision,
                "provided_revision": result.provided_revision,
            },
        )
    return result
