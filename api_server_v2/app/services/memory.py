from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ..db import json_load, repository
from ..schemas import (
    ConflictResponse,
    SessionCreateRequest,
    SessionResponse,
    TokenCreateRequest,
    TokenResponse,
    Workspace,
    WorkspaceCreateRequest,
)

# [추가 1]
# 4단계에서 완성한 어댑터와 메타데이터 클래스를 임포트합니다.
from ..adapters.google_docs import GoogleDocsAdapter, DocumentMeta


class MemoryService:
    """Persistent service backed by sqlite repository."""

    # ... (list_workspaces, get_workspace, create_workspace는 변경 없음) ...
    def list_workspaces(self) -> List[Workspace]:
        return repository.list_workspaces()

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return repository.get_workspace(workspace_id)

    def create_workspace(self, payload: WorkspaceCreateRequest) -> Workspace:
        return repository.create_workspace(payload.name, payload.doc_personal_id, payload.team_map)


    def latest_session(
        self,
        workspace_id: str,
        scope: str,
        team_key: Optional[str],
        category: Optional[str],
    ) -> Optional[SessionResponse]:
        """
        [PULL 로직] 로컬 DB에서 최신 세션을 가져오고,
        Google Docs API를 호출하여 실제 메타데이터를 함께 반환합니다.
        """
        
        # 1. Google Docs 메타데이터 먼저 조회 (PULL)
        # (로컬 DB 조회 '전에' 호출해야 토큰 갱신을 먼저 처리할 수 있음)
        meta: DocumentMeta | None = None
        try:
            # (선행 작업 1) 워크스페이스에서 GDoc ID 가져오기
            workspace = repository.get_workspace(workspace_id)
            if not workspace:
                raise ValueError("WORKSPACE_NOT_FOUND")
            doc_id = workspace.doc_personal_id
            
            # (선행 작업 2) DB에서 Google OAuth 토큰 가져오기
            token_json = repository.get_google_token(workspace_id)
            if not token_json:
                raise Exception("Google 인증 토큰이 없습니다. 먼저 인증하세요.")

            # (어댑터 사용 1) 어댑터 초기화 (이때 토큰 갱신 발생 가능)
            adapter = GoogleDocsAdapter(token_json)

            # (어댑터 사용 2) GDoc 실제 메타데이터 가져오기
            meta = adapter.fetch_meta(doc_id)
            
            # (선행 작업 3) 갱신된 토큰이 있다면 DB에 다시 저장
            refreshed_token_json = adapter.get_current_token_json()
            if refreshed_token_json != token_json:
                repository.update_google_token(workspace_id, refreshed_token_json)
        
        except Exception as e:
            # GDoc API 호출에 실패해도 (예: 토큰 만료) 
            # 로컬 DB 데이터는 반환하도록 오류를 출력만 합니다.
            print(f"[ERROR] Google Docs meta fetch 실패: {e}")
            # TODO: 인증 만료(Re-authentication required) 오류 시 
            #       클라이언트에 "REAUTH_REQUIRED" 상태를 보내는 것이 좋음
            meta = None


        # 2. 로컬 DB에서 세션 조회 (기존 로직)
        sessions = repository.list_sessions(workspace_id)
        if not sessions:
            return None
            
        row_to_return = None
        if category:
            cat_upper = category.strip().upper()
            for row in reversed(sessions):
                categories = [c.upper() for c in json_load(row["categories"], [])]
                if cat_upper in categories:
                    row_to_return = row
                    break
            if not row_to_return:
                return None
        else:
            row_to_return = sessions[-1]

        # 3. 로컬 DB 정보(row)와 GDoc 메타(meta)를 합쳐서 반환
        return self._row_to_session(row_to_return, meta)


    def create_session(self, payload: SessionCreateRequest) -> SessionResponse | ConflictResponse:
        """
        [PUSH 로직] 로컬 DB에 세션을 저장하고,
        Google Docs API를 호출하여 실제 문서에 내용을 추가(append)합니다.
        """
        workspace = repository.get_workspace(payload.workspace_id)
        if not workspace:
            raise ValueError("WORKSPACE_NOT_FOUND")

        # 1. 리비전 충돌 검사 (기존 로직)
        current_revision = repository.current_revision(payload.workspace_id)
        if payload.revision and payload.revision != current_revision:
            return ConflictResponse(
                expected_revision=current_revision,
                provided_revision=payload.revision,
            )

        # 2. 로컬 DB에 저장 (기존 로직)
        revision_id = str(uuid.uuid4())
        categories = self._derive_categories(payload.content)
        repository.insert_session(
            payload.workspace_id,
            payload.scope,
            payload.team_key,
            revision_id,
            payload.content,
            categories,
        )

        # 3. [추가] Google Docs에 PUSH
        meta: DocumentMeta | None = None
        doc_url: str | None = None
        try:
            doc_id = workspace.doc_personal_id
            
            # (선행 작업 2) DB에서 Google OAuth 토큰 가져오기
            token_json = repository.get_google_token(payload.workspace_id)
            if not token_json:
                raise Exception("Google 인증 토큰이 없습니다. 먼저 인증하세요.")

            # (어댑터 사용 1) 어댑터 초기화 (토큰 갱신)
            adapter = GoogleDocsAdapter(token_json)

            # (어댑터 사용 2) GDoc에 내용 추가 (PUSH)
            adapter.append_handoff(doc_id, payload.content)

            # (어댑터 사용 3) PUSH 성공 후, 최신 메타데이터 다시 가져오기
            meta = adapter.fetch_meta(doc_id)
            doc_url = meta.url if meta else None
            
            # (선행 작업 3) 갱신된 토큰 DB에 저장
            refreshed_token_json = adapter.get_current_token_json()
            if refreshed_token_json != token_json:
                repository.update_google_token(payload.workspace_id, refreshed_token_json)

        except Exception as e:
            # GDoc PUSH 실패 시, 로컬 저장은 이미 완료되었음
            print(f"[ERROR] Google Docs append_handoff 실패: {e}")
            # TODO: 클라이언트에 "PUSH_FAILED" 같은 상태를 보내는 것이 좋음
            pass

        # 4. 최종 응답 반환
        return SessionResponse(
            revision_id=revision_id,
            # [수정] GDoc 메타가 있으면 GDoc의 수정 시간을, 없으면 현재 시간을 사용
            last_updated=datetime.fromisoformat(meta.last_updated) if meta else datetime.utcnow(),
            categories=categories,
            scope=payload.scope,
            team_key=payload.team_key,
            content=payload.content,
            doc_url=doc_url, # [수정] GDoc URL 반환
            matched_category=None,
            status="OK_LOCAL_SAVED" # (PUSH 성공 여부와 관계없이 로컬 성공)
        )

    def create_token(self, payload: TokenCreateRequest) -> TokenResponse:
        # (변경 없음 - FastAPI 서버 API 키 발급 로직)
        return repository.create_token(payload.workspace_id, payload.scopes)

    def _derive_categories(self, text: str) -> List[str]:
        # (변경 없음)
        lowered = (text or "").lower()
        if "meeting" in lowered or "회의" in lowered:
            return ["MEETING"]
        if "bug" in lowered or "오류" in lowered:
            return ["BUG"]
        return ["GENERAL"]

    def _row_to_session(
        self, 
        row, 
        meta: DocumentMeta | None = None # [추가] GDoc 메타 객체를 받음
    ) -> SessionResponse:
        """Helper: DB row와 GDoc Meta를 SessionResponse로 변환"""
        
        # [수정] GDoc 메타가 있으면 GDoc 정보를, 없으면 DB 정보를 우선 사용
        doc_url = meta.url if meta else None
        last_updated = (
            datetime.fromisoformat(meta.last_updated) 
            if meta else datetime.fromisoformat(row["last_updated"])
        )

        return SessionResponse(
            revision_id=row["revision_id"],
            last_updated=last_updated, # [수정]
            categories=json_load(row["categories"], []),
            scope=row["scope"],
            team_key=row["team_key"],
            content=row["content"],
            doc_url=doc_url, # [수정]
            matched_category=None,
            status="OK_PULLED",
        )


memory_service = MemoryService()
