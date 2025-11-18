"""
Storage Factory
환경 변수에 따라 적절한 저장소 어댑터를 선택합니다.
"""

import os
from typing import Optional
from .base import StorageAdapter
from .sqlite import SQLiteAdapter
from .firebase import FirebaseAdapter
from .notion import NotionAdapter
from .mongodb import MongoDBAdapter
from .superthread import SuperthreadAdapter


class StorageFactory:
    """저장소 어댑터 팩토리"""

    # 싱글톤 인스턴스
    _instance: Optional[StorageAdapter] = None

    @classmethod
    def get_storage(cls) -> StorageAdapter:
        """
        환경 설정에 따라 저장소 어댑터 반환

        환경 변수:
            STORAGE_TYPE: 저장소 타입 (sqlite/firebase/notion/mongodb/superthread)
                         기본값: sqlite

            SQLite:
                SQLITE_DB_PATH: 데이터베이스 파일 경로 (기본값: memory_hub.db)

            Firebase:
                FIREBASE_CREDENTIALS: Firebase 서비스 계정 키 파일 경로

            Notion:
                NOTION_API_KEY: Notion API 키
                NOTION_DATABASE_ID: Notion 데이터베이스 ID

            MongoDB:
                MONGODB_CONNECTION_STRING: MongoDB 연결 문자열
                MONGODB_DATABASE_NAME: 데이터베이스 이름 (기본값: memory_hub)

            Superthread:
                SUPERTHREAD_API_KEY: Superthread API 키
                SUPERTHREAD_WORKSPACE_ID: Superthread 워크스페이스 ID

        Returns:
            StorageAdapter 인스턴스

        Raises:
            ValueError: 알 수 없는 저장소 타입 또는 필수 환경 변수 누락
        """
        if cls._instance is not None:
            return cls._instance

        storage_type = os.getenv("STORAGE_TYPE", "sqlite").lower()

        if storage_type == "sqlite":
            cls._instance = cls._create_sqlite()
        elif storage_type == "firebase":
            cls._instance = cls._create_firebase()
        elif storage_type == "notion":
            cls._instance = cls._create_notion()
        elif storage_type == "mongodb":
            cls._instance = cls._create_mongodb()
        elif storage_type == "superthread":
            cls._instance = cls._create_superthread()
        else:
            raise ValueError(
                f"알 수 없는 저장소 타입: {storage_type}\n"
                f"지원하는 타입: sqlite, firebase, notion, mongodb, superthread"
            )

        return cls._instance

    @staticmethod
    def _create_sqlite() -> StorageAdapter:
        """SQLite 어댑터 생성"""
        db_path = os.getenv("SQLITE_DB_PATH")
        return SQLiteAdapter(db_path)

    @staticmethod
    def _create_firebase() -> StorageAdapter:
        """Firebase 어댑터 생성"""
        credentials_path = os.getenv("FIREBASE_CREDENTIALS")
        if not credentials_path:
            credentials_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "credentials.json"
            )
        return FirebaseAdapter(credentials_path)

    @staticmethod
    def _create_notion() -> StorageAdapter:
        """Notion 어댑터 생성"""
        api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")

        if not api_key:
            raise ValueError(
                "NOTION_API_KEY 환경 변수가 필요합니다.\n"
                "설정 방법: MULTI_STORAGE_SETUP.md를 참조하세요."
            )

        if not database_id:
            raise ValueError(
                "NOTION_DATABASE_ID 환경 변수가 필요합니다.\n"
                "설정 방법: MULTI_STORAGE_SETUP.md를 참조하세요."
            )

        return NotionAdapter(api_key, database_id)

    @staticmethod
    def _create_mongodb() -> StorageAdapter:
        """MongoDB 어댑터 생성"""
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")

        if not connection_string:
            raise ValueError(
                "MONGODB_CONNECTION_STRING 환경 변수가 필요합니다.\n"
                "설정 방법: MULTI_STORAGE_SETUP.md를 참조하세요."
            )

        database_name = os.getenv("MONGODB_DATABASE_NAME", "memory_hub")
        return MongoDBAdapter(connection_string, database_name)

    @staticmethod
    def _create_superthread() -> StorageAdapter:
        """Superthread 어댑터 생성"""
        api_key = os.getenv("SUPERTHREAD_API_KEY")
        workspace_id = os.getenv("SUPERTHREAD_WORKSPACE_ID")

        if not api_key:
            raise ValueError(
                "SUPERTHREAD_API_KEY 환경 변수가 필요합니다.\n"
                "Superthread 계정에서 API 키를 발급해주세요."
            )

        if not workspace_id:
            raise ValueError(
                "SUPERTHREAD_WORKSPACE_ID 환경 변수가 필요합니다.\n"
                "Superthread 워크스페이스 ID를 설정해주세요."
            )

        return SuperthreadAdapter(api_key, workspace_id)

    @classmethod
    def reset(cls):
        """싱글톤 인스턴스 리셋 (테스트용)"""
        cls._instance = None

    @classmethod
    def list_available_storages(cls) -> Dict[str, str]:
        """사용 가능한 저장소 목록"""
        return {
            "sqlite": "로컬 파일 기반 데이터베이스",
            "firebase": "Google Firebase Firestore",
            "notion": "Notion API",
            "mongodb": "MongoDB Atlas",
            "superthread": "Superthread 팀 협업 플랫폼",
        }


# 편의 함수
def get_storage() -> StorageAdapter:
    """현재 저장소 어댑터 반환"""
    return StorageFactory.get_storage()


# 타입 힌트
from typing import Dict
