"""
MongoDB Atlas 저장소 어댑터
MongoDB 클라우드 데이터베이스
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import Optional, Dict, Any
from datetime import datetime
from bson.objectid import ObjectId
from .base import StorageAdapter


class MongoDBAdapter(StorageAdapter):
    """MongoDB Atlas 저장소 어댑터"""

    def __init__(self, connection_string: str, database_name: str = "memory_hub"):
        """
        MongoDB 초기화

        Args:
            connection_string: MongoDB 연결 문자열
            database_name: 데이터베이스 이름
        """
        self.connection_string = connection_string
        self.database_name = database_name

        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # 연결 테스트
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            self.collection = self.db["memories"]

            # 인덱스 생성
            self.collection.create_index([
                ("workspace_id", 1),
                ("scope", 1),
                ("team_key", 1)
            ])
        except ServerSelectionTimeoutError as e:
            raise ConnectionError(f"MongoDB 연결 실패: {str(e)}")

    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """메모를 MongoDB에 저장"""
        try:
            revision_id = self.generate_revision_id()
            now = datetime.utcnow()

            document = {
                "workspace_id": workspace_id,
                "content": content,
                "scope": scope,
                "team_key": team_key,
                "category": category or "GENERAL",
                "revision_id": revision_id,
                "created_at": now,
                "updated_at": now,
            }

            result = self.collection.insert_one(document)

            return {
                "success": True,
                "message": "메모가 MongoDB에 저장되었습니다.",
                "doc_id": str(result.inserted_id),
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
        """MongoDB에서 메모 조회"""
        try:
            query = {
                "workspace_id": workspace_id,
                "scope": scope,
            }

            if team_key:
                query["team_key"] = team_key

            if category:
                query["category"] = category

            doc = self.collection.find_one(query, sort=[("updated_at", -1)])

            if not doc:
                return {
                    "success": False,
                    "error": "메모를 찾을 수 없습니다.",
                }

            return {
                "success": True,
                "content": doc.get("content"),
                "workspace_id": doc.get("workspace_id"),
                "scope": doc.get("scope"),
                "team_key": doc.get("team_key"),
                "category": doc.get("category"),
                "created_at": self.format_timestamp(doc.get("created_at")),
                "updated_at": self.format_timestamp(doc.get("updated_at")),
                "revision_id": doc.get("revision_id"),
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
            query = {"scope": scope}

            if team_key:
                query["team_key"] = team_key

            docs = list(
                self.collection.find(query)
                .sort("updated_at", -1)
                .limit(limit)
            )

            # ObjectId를 문자열로 변환
            for doc in docs:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = self.format_timestamp(doc.get("created_at"))
                doc["updated_at"] = self.format_timestamp(doc.get("updated_at"))

            return {
                "success": True,
                "count": len(docs),
                "memories": docs,
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
            query = {
                "workspace_id": workspace_id,
                "scope": scope,
            }

            if team_key:
                query["team_key"] = team_key

            result = self.collection.delete_many(query)

            return {
                "success": True,
                "message": f"{result.deleted_count}개의 메모가 삭제되었습니다.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보"""
        try:
            info = self.client.server_info()
            memory_count = self.collection.count_documents({})

            return {
                "type": "MongoDB Atlas",
                "description": "MongoDB 클라우드 NoSQL 데이터베이스",
                "database": self.database_name,
                "memory_count": memory_count,
                "free_quota": "512MB 저장소",
                "real_time": True,
                "automatic_backup": True,
                "offline_support": False,
                "pricing": "무료 (512MB까지)",
                "scalability": "높음",
                "docs": "https://docs.mongodb.com/",
            }
        except Exception as e:
            return {
                "type": "MongoDB Atlas",
                "error": str(e),
            }
