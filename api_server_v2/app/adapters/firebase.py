"""
Firebase Firestore 어댑터
메모를 Firebase Firestore에 저장하고 조회합니다.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Optional, Dict, Any
import json
import os


class FirebaseAdapter:
    """Firebase Firestore 어댑터"""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Firebase 초기화

        Args:
            credentials_path: Firebase 서비스 계정 키 파일 경로
                            (기본값: api_server_v2/credentials.json)
        """
        # 기본 경로 설정
        if credentials_path is None:
            credentials_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "credentials.json"
            )

        # 이미 초기화되었는지 확인
        try:
            self.db = firestore.client()
        except ValueError:
            # 처음 초기화하는 경우
            if os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
            else:
                raise FileNotFoundError(
                    f"Firebase 서비스 계정 키를 찾을 수 없습니다.\n"
                    f"경로: {credentials_path}\n\n"
                    f"설정 방법: FIREBASE_SETUP.md를 참조하세요."
                )

        self.collection_name = "memories"

    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        메모를 Firestore에 저장

        Args:
            workspace_id: 워크스페이스 ID
            content: 메모 내용
            scope: 스코프 (personal / team)
            team_key: 팀 키 (team 스코프일 때)
            category: 카테고리

        Returns:
            저장된 메모 정보
        """
        # 문서 ID 생성 (workspace_id 기반)
        doc_id = f"{scope}_{team_key or workspace_id}"

        # 저장할 데이터
        data = {
            "workspace_id": workspace_id,
            "content": content,
            "scope": scope,
            "team_key": team_key,
            "category": category or "GENERAL",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "revision_id": self._generate_revision_id(),
        }

        try:
            # Firestore에 저장
            self.db.collection(self.collection_name).document(doc_id).set(data)

            return {
                "success": True,
                "message": "메모가 Firebase에 저장되었습니다.",
                "doc_id": doc_id,
                "revision_id": data["revision_id"],
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
        """
        Firestore에서 메모 조회

        Args:
            workspace_id: 워크스페이스 ID
            scope: 스코프 (personal / team)
            team_key: 팀 키 (team 스코프일 때)
            category: 카테고리 필터 (선택)

        Returns:
            조회된 메모 정보
        """
        doc_id = f"{scope}_{team_key or workspace_id}"

        try:
            # 문서 조회
            doc = self.db.collection(self.collection_name).document(doc_id).get()

            if not doc.exists:
                return {
                    "success": False,
                    "error": "메모를 찾을 수 없습니다.",
                }

            data = doc.to_dict()

            # 카테고리 필터 (지정된 경우)
            if category and data.get("category") != category:
                return {
                    "success": False,
                    "error": f"카테고리 '{category}'를 찾을 수 없습니다.",
                }

            # 타임스탬프를 ISO 형식으로 변환
            if isinstance(data.get("created_at"), datetime):
                data["created_at"] = data["created_at"].isoformat()
            if isinstance(data.get("updated_at"), datetime):
                data["updated_at"] = data["updated_at"].isoformat()

            return {
                "success": True,
                "content": data.get("content"),
                "workspace_id": data.get("workspace_id"),
                "scope": data.get("scope"),
                "team_key": data.get("team_key"),
                "category": data.get("category"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "revision_id": data.get("revision_id"),
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
        """
        메모 목록 조회

        Args:
            scope: 스코프 필터
            team_key: 팀 키 필터
            limit: 최대 조회 수

        Returns:
            메모 목록
        """
        try:
            query = self.db.collection(self.collection_name)

            # 필터 적용
            if scope:
                query = query.where("scope", "==", scope)
            if team_key:
                query = query.where("team_key", "==", team_key)

            # 최근 수정순 정렬
            query = query.order_by("updated_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)

            docs = query.stream()

            memories = []
            for doc in docs:
                data = doc.to_dict()
                # 타임스탬프 변환
                if isinstance(data.get("updated_at"), datetime):
                    data["updated_at"] = data["updated_at"].isoformat()
                memories.append(data)

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
        """
        메모 삭제

        Args:
            workspace_id: 워크스페이스 ID
            scope: 스코프
            team_key: 팀 키

        Returns:
            삭제 결과
        """
        doc_id = f"{scope}_{team_key or workspace_id}"

        try:
            self.db.collection(self.collection_name).document(doc_id).delete()

            return {
                "success": True,
                "message": "메모가 삭제되었습니다.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """
        저장소 정보 조회

        Returns:
            Firebase Firestore 정보
        """
        return {
            "type": "Firebase Firestore",
            "description": "Google의 클라우드 NoSQL 데이터베이스",
            "free_quota": "1GB 저장소, 50,000 읽기/일",
            "real_time": True,
            "automatic_backup": True,
            "offline_support": True,
            "pricing": "무료 (1GB까지)",
            "docs": "https://firebase.google.com/docs/firestore",
        }

    @staticmethod
    def _generate_revision_id() -> str:
        """리비전 ID 생성"""
        from datetime import datetime
        import hashlib

        timestamp = datetime.utcnow().isoformat()
        hash_obj = hashlib.md5(timestamp.encode())
        return hash_obj.hexdigest()[:12]


# 싱글톤 인스턴스
_firebase_instance = None


def get_firebase_adapter() -> FirebaseAdapter:
    """Firebase 어댑터 싱글톤 인스턴스 반환"""
    global _firebase_instance

    if _firebase_instance is None:
        _firebase_instance = FirebaseAdapter()

    return _firebase_instance
