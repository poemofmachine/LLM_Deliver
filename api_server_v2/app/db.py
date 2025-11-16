from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .schemas import TokenResponse, Workspace

DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row


def init_db() -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT,
                doc_personal_id TEXT,
                team_map TEXT,
                categories TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                workspace_id TEXT,
                scope TEXT,
                team_key TEXT,
                revision_id TEXT,
                content TEXT,
                categories TEXT,
                last_updated TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                workspace_id TEXT,
                scopes TEXT,
                expires_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS revisions (
                workspace_id TEXT PRIMARY KEY,
                revision_id TEXT
            )
            """
        )
        
        # [추가] Google OAuth 토큰을 저장할 테이블
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS google_tokens (
                workspace_id TEXT PRIMARY KEY,
                token_json TEXT NOT NULL
            )
            """
        )


init_db()


def json_dump(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def json_load(value: Optional[str], default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


class MemoryRepository:
    def create_workspace(self, name: str, doc_personal_id: str, team_map: dict) -> Workspace:
        workspace_id = str(uuid.uuid4())
        categories = ["GENERAL"]
        with conn:
            conn.execute(
                "INSERT INTO workspaces (id, name, doc_personal_id, team_map, categories) VALUES (?, ?, ?, ?, ?)",
                (workspace_id, name, doc_personal_id, json_dump(team_map or {}), json_dump(categories)),
            )
            conn.execute(
                "INSERT OR REPLACE INTO revisions (workspace_id, revision_id) VALUES (?, ?)",
                (workspace_id, "init"),
            )
        return Workspace(
            id=workspace_id,
            name=name,
            doc_personal_id=doc_personal_id,
            team_map=team_map or {},
            categories=categories,
        )

    def list_workspaces(self) -> List[Workspace]:
        cur = conn.execute("SELECT * FROM workspaces")
        rows = cur.fetchall()
        return [
            Workspace(
                id=row["id"],
                name=row["name"],
                doc_personal_id=row["doc_personal_id"],
                team_map=json_load(row["team_map"], {}),
                categories=json_load(row["categories"], []),
            )
            for row in rows
        ]

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        cur = conn.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,))
        row = cur.fetchone()
        if not row:
            return None
        return Workspace(
            id=row["id"],
            name=row["name"],
            doc_personal_id=row["doc_personal_id"],
            team_map=json_load(row["team_map"], {}),
            categories=json_load(row["categories"], []),
        )

    def get_latest_session(self, workspace_id: str) -> Optional[sqlite3.Row]:
        cur = conn.execute(
            "SELECT * FROM sessions WHERE workspace_id = ? ORDER BY datetime(last_updated) DESC LIMIT 1",
            (workspace_id,),
        )
        return cur.fetchone()

    def list_sessions(self, workspace_id: str) -> List[sqlite3.Row]:
        cur = conn.execute(
            "SELECT * FROM sessions WHERE workspace_id = ? ORDER BY datetime(last_updated) ASC",
            (workspace_id,),
        )
        return cur.fetchall()

    def insert_session(
        self,
        workspace_id: str,
        scope: str,
        team_key: Optional[str],
        revision_id: str,
        content: str,
        categories: List[str],
    ) -> None:
        with conn:
            conn.execute(
                """
                INSERT INTO sessions (id, workspace_id, scope, team_key, revision_id, content, categories, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    workspace_id,
                    scope,
                    team_key,
                    revision_id,
                    content,
                    json_dump(categories),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.execute(
                "INSERT OR REPLACE INTO revisions (workspace_id, revision_id) VALUES (?, ?)",
                (workspace_id, revision_id),
            )

    def current_revision(self, workspace_id: str) -> str:
        cur = conn.execute("SELECT revision_id FROM revisions WHERE workspace_id = ?", (workspace_id,))
        row = cur.fetchone()
        return row["revision_id"] if row else "init"

    def create_token(self, workspace_id: str, scopes: List[str]) -> TokenResponse:
        token_value = uuid.uuid4().hex
        expires_at = datetime.utcnow() + timedelta(days=30)
        with conn:
            conn.execute(
                "INSERT INTO tokens (token, workspace_id, scopes, expires_at) VALUES (?, ?, ?, ?)",
                (token_value, workspace_id, json_dump(scopes or []), expires_at.isoformat()),
            )
        return TokenResponse(token=token_value, expires_at=expires_at)

    # === [아래 3개 메서드 추가됨] ===

    def save_google_token(self, workspace_id: str, token_json: str):
        """[추가] Google 토큰을 저장 (INSERT 또는 UPDATE)합니다."""
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO google_tokens (workspace_id, token_json) 
                    VALUES (?, ?)
                    ON CONFLICT(workspace_id) DO UPDATE SET token_json = excluded.token_json
                    """,
                    (str(workspace_id), token_json)
                )
            print(f"Workspace {workspace_id}의 Google 토큰 저장/갱신 성공.")
        except Exception as e:
            print(f"[ERROR] save_google_token 실패: {e}")

    def get_google_token(self, workspace_id: str) -> str | None:
        """[추가] Google 토큰을 조회합니다."""
        try:
            cur = conn.execute(
                "SELECT token_json FROM google_tokens WHERE workspace_id = ?",
                (str(workspace_id),)
            )
            row = cur.fetchone()
            return row["token_json"] if row else None
        except Exception as e:
            print(f"[ERROR] get_google_token 실패: {e}")
            return None

    def update_google_token(self, workspace_id: str, new_token_json: str):
        """[추가] 토큰 갱신 (save와 동일한 로직 사용)"""
        # ON CONFLICT... DO UPDATE 구문이 이미 갱신을 처리하므로
        # save_google_token 함수를 그대로 호출합니다.
        self.save_google_token(workspace_id, new_token_json)


repository = MemoryRepository()