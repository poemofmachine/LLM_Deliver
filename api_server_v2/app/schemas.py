from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    workspace_id: str
    scope: Literal["personal", "team"]
    team_key: Optional[str] = None
    revision: Optional[str] = None
    content: str


class SessionResponse(BaseModel):
    status: str = "OK"
    revision_id: str
    last_updated: datetime
    categories: List[str]
    scope: str
    team_key: Optional[str] = None
    content: Optional[str] = None
    doc_url: Optional[str] = None
    matched_category: Optional[str] = None


class ConflictResponse(BaseModel):
    status: str = "CONFLICT"
    expected_revision: str
    provided_revision: str


class Workspace(BaseModel):
    id: str
    name: str
    doc_personal_id: Optional[str] = None
    team_map: Dict[str, str] = {}
    categories: List[str] = []


class WorkspaceCreateRequest(BaseModel):
    name: str
    doc_personal_id: str
    team_map: Dict[str, str] = {}


class TokenCreateRequest(BaseModel):
    workspace_id: str
    scopes: List[str]


class TokenResponse(BaseModel):
    token: str
    expires_at: datetime


class ErrorResponse(BaseModel):
    error: str
