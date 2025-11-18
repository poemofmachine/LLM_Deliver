"""
SQLite 저장소 어댑터
로컬 파일 기반 데이터베이스
"""

import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime
from .base import StorageAdapter


class SQLiteAdapter(StorageAdapter):
    """SQLite 로컬 저장소 어댑터"""

    def __init__(self, db_path: Optional[str] = None):
        """
        SQLite 초기화

        Args:
            db_path: 데이터베이스 파일 경로 (기본값: memory_hub.db)
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "memory_hub.db"
            )

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # memories 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                content TEXT NOT NULL,
                scope TEXT DEFAULT 'personal',
                team_key TEXT,
                category TEXT DEFAULT 'GENERAL',
                revision_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 인덱스 생성
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_workspace
            ON memories(workspace_id, scope, team_key)
        ''')

        conn.commit()
        conn.close()

    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """메모를 SQLite에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            revision_id = self.generate_revision_id()
            now = datetime.utcnow().isoformat()

            cursor.execute('''
                INSERT INTO memories
                (workspace_id, content, scope, team_key, category, revision_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (workspace_id, content, scope, team_key, category or "GENERAL", revision_id, now, now))

            conn.commit()
            memory_id = cursor.lastrowid
            conn.close()

            return {
                "success": True,
                "message": "메모가 SQLite에 저장되었습니다.",
                "doc_id": str(memory_id),
                "revision_id": revision_id,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_memory(
        self,
        workspace_id: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """SQLite에서 메모 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT * FROM memories
                WHERE workspace_id = ? AND scope = ?
            '''
            params = [workspace_id, scope]

            if team_key:
                query += " AND team_key = ?"
                params.append(team_key)

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY updated_at DESC LIMIT 1"

            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.close()

            if not row:
                return {
                    "success": False,
                    "error": "메모를 찾을 수 없습니다.",
                }

            return {
                "success": True,
                "content": row["content"],
                "workspace_id": row["workspace_id"],
                "scope": row["scope"],
                "team_key": row["team_key"],
                "category": row["category"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "revision_id": row["revision_id"],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_memories(
        self,
        scope: str = "personal",
        team_key: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """메모 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM memories WHERE scope = ?"
            params = [scope]

            if team_key:
                query += " AND team_key = ?"
                params.append(team_key)

            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            memories = [dict(row) for row in rows]

            return {
                "success": True,
                "count": len(memories),
                "memories": memories,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete_memory(
        self,
        workspace_id: str,
        scope: str = "personal",
        team_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """메모 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "DELETE FROM memories WHERE workspace_id = ? AND scope = ?"
            params = [workspace_id, scope]

            if team_key:
                query += " AND team_key = ?"
                params.append(team_key)

            cursor.execute(query, params)
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            return {
                "success": True,
                "message": f"{affected_rows}개의 메모가 삭제되었습니다.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM memories")
            memory_count = cursor.fetchone()[0]

            file_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            conn.close()

            return {
                "type": "SQLite (Local)",
                "description": "로컬 파일 기반 데이터베이스",
                "storage_path": self.db_path,
                "memory_count": memory_count,
                "file_size_mb": round(file_size, 2),
                "free_quota": "무제한",
                "real_time": False,
                "automatic_backup": False,
                "offline_support": True,
                "pricing": "무료",
                "docs": "https://www.sqlite.org/docs.html",
            }
        except Exception as e:
            return {
                "type": "SQLite (Local)",
                "error": str(e),
            }
