"""
Storage Adapter 베이스 클래스
모든 저장소 구현이 상속해야 할 추상 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime


class StorageAdapter(ABC):
    """저장소 어댑터 추상 클래스"""

    @abstractmethod
    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        메모를 저장소에 저장

        Args:
            workspace_id: 워크스페이스 ID
            content: 메모 내용
            scope: 스코프 (personal / team)
            team_key: 팀 키
            category: 카테고리

        Returns:
            저장 결과 (success, message, doc_id, revision_id)
        """
        pass

    @abstractmethod
    def get_memory(
        self,
        workspace_id: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        저장소에서 메모 조회

        Args:
            workspace_id: 워크스페이스 ID
            scope: 스코프
            team_key: 팀 키
            category: 카테고리 필터

        Returns:
            메모 데이터 (success, content, metadata)
        """
        pass

    @abstractmethod
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
            limit: 최대 개수

        Returns:
            메모 목록
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """
        저장소 정보 조회

        Returns:
            저장소 타입, 용량, 기능 등 정보
        """
        pass

    # 유틸리티 메서드
    @staticmethod
    def generate_revision_id() -> str:
        """리비전 ID 생성"""
        from datetime import datetime
        import hashlib

        timestamp = datetime.utcnow().isoformat()
        hash_obj = hashlib.md5(timestamp.encode())
        return hash_obj.hexdigest()[:12]

    @staticmethod
    def format_timestamp(dt: Optional[datetime]) -> Optional[str]:
        """타임스탬프를 ISO 형식으로 변환"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt
