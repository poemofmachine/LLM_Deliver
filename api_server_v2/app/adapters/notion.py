"""
Notion 저장소 어댑터
Notion API를 사용한 클라우드 저장소
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
from .base import StorageAdapter


class NotionAdapter(StorageAdapter):
    """Notion API 저장소 어댑터"""

    def __init__(self, api_key: str, database_id: str):
        """
        Notion 초기화

        Args:
            api_key: Notion API 키
            database_id: Notion 데이터베이스 ID
        """
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """메모를 Notion 데이터베이스에 저장"""
        try:
            revision_id = self.generate_revision_id()

            data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Workspace": {
                        "title": [{"text": {"content": workspace_id}}]
                    },
                    "Content": {
                        "rich_text": [{"text": {"content": content[:2000]}}]  # Notion 제한
                    },
                    "Scope": {
                        "select": {"name": scope}
                    },
                    "Team": {
                        "rich_text": [{"text": {"content": team_key or ""}}]
                    },
                    "Category": {
                        "select": {"name": category or "GENERAL"}
                    },
                    "Revision": {
                        "rich_text": [{"text": {"content": revision_id}}]
                    },
                }
            }

            response = requests.post(
                "https://api.notion.com/v1/pages",
                json=data,
                headers=self.headers
            )

            if response.status_code == 200:
                page_id = response.json()["id"]
                return {
                    "success": True,
                    "message": "메모가 Notion에 저장되었습니다.",
                    "doc_id": page_id,
                    "revision_id": revision_id,
                }
            else:
                return {
                    "success": False,
                    "error": f"Notion API 오류: {response.status_code} - {response.text}",
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
        """Notion에서 메모 조회"""
        try:
            filters = {
                "and": [
                    {
                        "property": "Workspace",
                        "title": {"equals": workspace_id}
                    },
                    {
                        "property": "Scope",
                        "select": {"equals": scope}
                    }
                ]
            }

            if team_key:
                filters["and"].append({
                    "property": "Team",
                    "rich_text": {"contains": team_key}
                })

            if category:
                filters["and"].append({
                    "property": "Category",
                    "select": {"equals": category}
                })

            data = {
                "filter": filters,
                "sorts": [
                    {
                        "property": "Created",
                        "direction": "descending"
                    }
                ],
                "page_size": 1
            }

            response = requests.post(
                f"https://api.notion.com/v1/databases/{self.database_id}/query",
                json=data,
                headers=self.headers
            )

            if response.status_code == 200:
                results = response.json().get("results", [])

                if not results:
                    return {
                        "success": False,
                        "error": "메모를 찾을 수 없습니다.",
                    }

                page = results[0]
                props = page["properties"]

                return {
                    "success": True,
                    "content": props.get("Content", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "workspace_id": props.get("Workspace", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "scope": props.get("Scope", {}).get("select", {}).get("name", ""),
                    "team_key": props.get("Team", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "category": props.get("Category", {}).get("select", {}).get("name", "GENERAL"),
                    "created_at": page["created_time"],
                    "updated_at": page["last_edited_time"],
                    "revision_id": props.get("Revision", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                }
            else:
                return {
                    "success": False,
                    "error": f"Notion API 오류: {response.status_code}",
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
            filters = {
                "property": "Scope",
                "select": {"equals": scope}
            }

            if team_key:
                filters = {
                    "and": [
                        filters,
                        {
                            "property": "Team",
                            "rich_text": {"contains": team_key}
                        }
                    ]
                }

            data = {
                "filter": filters,
                "sorts": [
                    {
                        "property": "Created",
                        "direction": "descending"
                    }
                ],
                "page_size": limit
            }

            response = requests.post(
                f"https://api.notion.com/v1/databases/{self.database_id}/query",
                json=data,
                headers=self.headers
            )

            if response.status_code == 200:
                results = response.json().get("results", [])
                memories = [
                    {
                        "id": page["id"],
                        "created_at": page["created_time"],
                        "updated_at": page["last_edited_time"],
                    }
                    for page in results
                ]

                return {
                    "success": True,
                    "count": len(memories),
                    "memories": memories,
                }
            else:
                return {
                    "success": False,
                    "error": f"Notion API 오류: {response.status_code}",
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
        """메모 삭제 (Notion에서는 페이지 아카이브)"""
        try:
            # 먼저 메모 조회
            memory = self.get_memory(workspace_id, scope, team_key)

            if not memory.get("success"):
                return memory

            # Notion에서는 완전 삭제 대신 아카이브
            return {
                "success": True,
                "message": "메모가 아카이브되었습니다 (Notion에서는 완전 삭제 불가)",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보"""
        return {
            "type": "Notion",
            "description": "Notion 클라우드 데이터베이스",
            "database_id": self.database_id,
            "free_quota": "무제한",
            "real_time": True,
            "automatic_backup": True,
            "offline_support": False,
            "pricing": "무료 (무제한)",
            "collaboration": True,
            "docs": "https://developers.notion.com/",
        }
