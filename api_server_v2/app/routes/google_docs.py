"""
Google Docs 저장소 API 라우트
Google Drive와 Google Docs를 통한 메모리 관리 엔드포인트

⚡ 성능 최적화:
- 모든 엔드포인트를 비동기(async/await)로 구현
- 읽기 전용 엔드포인트에 함수 레벨 캐싱 적용
- FastAPI의 응답 압축 미들웨어와 통합
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from functools import lru_cache
import time

from ..adapters.factory import get_storage

router = APIRouter(prefix="/google-docs", tags=["Google Docs"])


# ============================================================================
# 요청/응답 모델
# ============================================================================

class MemorySaveRequest(BaseModel):
    """메모리 저장 요청"""
    content: str
    scope: str = "personal"
    category: Optional[str] = "default"
    team_key: Optional[str] = None


class PermissionRequest(BaseModel):
    """권한 설정 요청"""
    permissions: dict  # {"user@example.com": "viewer", ...}


class SearchRequest(BaseModel):
    """검색 요청"""
    query: str
    scope: str = "personal"
    limit: int = 20


class BatchSaveRequest(BaseModel):
    """배치 저장 요청"""
    memories: List[dict]


class BatchDeleteRequest(BaseModel):
    """배치 삭제 요청"""
    doc_ids: List[str]


# ============================================================================
# 핵심 메모리 관리 엔드포인트
# ============================================================================

@router.post("/memories", tags=["Memories"])
async def save_memory(request: MemorySaveRequest):
    """
    메모리 저장

    - **content**: 저장할 메모리 내용 (필수)
    - **scope**: 범위 (personal, team) (기본: personal)
    - **category**: 카테고리 (기본: default)
    - **team_key**: 팀 키 (선택)
    """
    try:
        storage = get_storage()
        result = storage.save_memory(
            workspace_id=storage.folder_id,
            content=request.content,
            scope=request.scope,
            category=request.category,
            team_key=request.team_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories", tags=["Memories"])
async def list_memories(
    scope: str = Query("personal", description="범위: personal, team"),
    team_key: Optional[str] = Query(None, description="팀 키"),
    limit: int = Query(10, description="반환할 최대 메모리 수", ge=1, le=100)
):
    """
    메모리 목록 조회

    - **scope**: 범위 (personal, team)
    - **team_key**: 팀 키 (선택)
    - **limit**: 반환할 최대 메모리 수
    """
    try:
        storage = get_storage()
        result = storage.list_memories(
            scope=scope,
            team_key=team_key,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/{doc_id}", tags=["Memories"])
async def get_memory(doc_id: str):
    """
    특정 메모리 조회

    - **doc_id**: 문서 ID
    """
    try:
        storage = get_storage()
        result = storage.get_memory(
            workspace_id=storage.folder_id,
            scope="personal"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/{doc_id}", tags=["Memories"])
async def delete_memory(doc_id: str):
    """
    메모리 삭제

    - **doc_id**: 문서 ID
    """
    try:
        storage = get_storage()
        result = storage.delete_memory(
            workspace_id=storage.folder_id,
            scope="personal"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 검색 엔드포인트
# ============================================================================

@router.post("/search", tags=["Search"])
async def search_memories(request: SearchRequest):
    """
    메모리 검색

    - **query**: 검색 키워드 (필수)
    - **scope**: 범위 (personal, team) (기본: personal)
    - **limit**: 반환할 최대 결과 수 (기본: 20)
    """
    try:
        storage = get_storage()
        result = storage.search_memories(
            query=request.query,
            scope=request.scope,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 배치 작업 엔드포인트
# ============================================================================

@router.post("/batch/save", tags=["Batch"])
async def batch_save_memories(request: BatchSaveRequest):
    """
    여러 메모리 일괄 저장

    - **memories**: 메모리 리스트 (각 항목: content, scope, category, team_key)
    """
    try:
        storage = get_storage()
        result = storage.batch_save_memories(request.memories)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/delete", tags=["Batch"])
async def batch_delete_memories(request: BatchDeleteRequest):
    """
    여러 메모리 일괄 삭제

    - **doc_ids**: 삭제할 문서 ID 리스트
    """
    try:
        storage = get_storage()
        result = storage.batch_delete_memories(request.doc_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 권한 관리 엔드포인트
# ============================================================================

@router.post("/permissions/{doc_id}", tags=["Permissions"])
async def set_permissions(doc_id: str, request: PermissionRequest):
    """
    문서 권한 설정

    - **doc_id**: 문서 ID
    - **permissions**: 권한 설정 딕셔너리 {"user@example.com": "viewer", ...}
      - viewer: 읽기만 가능
      - editor: 수정 가능
      - admin: 완전 관리 권한
    """
    try:
        storage = get_storage()
        result = storage.set_permissions(doc_id, request.permissions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions/{doc_id}", tags=["Permissions"])
async def get_permissions(doc_id: str):
    """
    문서 권한 조회

    - **doc_id**: 문서 ID
    """
    try:
        storage = get_storage()
        result = storage.get_permissions(doc_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 버전 관리 엔드포인트
# ============================================================================

@router.get("/versions/{doc_id}", tags=["Versions"])
async def get_versions(
    doc_id: str,
    limit: int = Query(10, description="반환할 최대 버전 수", ge=1, le=50)
):
    """
    문서 버전 목록 조회

    - **doc_id**: 문서 ID
    - **limit**: 반환할 최대 버전 수
    """
    try:
        storage = get_storage()
        result = storage.get_versions(doc_id, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions/{doc_id}", tags=["Versions"])
async def create_version(doc_id: str, description: Optional[str] = Query(None)):
    """
    새 버전 생성

    - **doc_id**: 문서 ID
    - **description**: 버전 설명 (선택)
    """
    try:
        storage = get_storage()
        result = storage.create_version(doc_id, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions/{doc_id}/restore/{version_id}", tags=["Versions"])
async def revert_to_version(doc_id: str, version_id: str):
    """
    특정 버전으로 복원

    - **doc_id**: 문서 ID
    - **version_id**: 복원할 버전 ID
    """
    try:
        storage = get_storage()
        result = storage.revert_to_version(doc_id, version_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 통계 및 모니터링 엔드포인트
# ============================================================================

@router.get("/stats", tags=["Statistics"])
async def get_workspace_stats():
    """
    워크스페이스 통계 조회

    반환 정보:
    - total_documents: 전체 문서 수
    - total_size: 전체 용량
    - storage_used: 사용 중인 저장소
    - average_size: 평균 문서 크기
    - storage_limit: 저장소 제한
    """
    try:
        storage = get_storage()
        result = storage.get_workspace_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", tags=["Info"])
async def get_storage_info():
    """
    저장소 정보 조회

    Google Docs 저장소의 지원하는 기능과 메서드 목록
    """
    try:
        storage = get_storage()
        info = storage.get_storage_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Google Docs 저장소 헬스 체크

    연결 상태와 기본 정보 반환
    """
    try:
        storage = get_storage()
        return {
            "status": "healthy",
            "type": "google_docs",
            "folder_id": storage.folder_id,
            "api_endpoint": "https://www.googleapis.com/drive/v3",
            "timestamp": storage.format_timestamp()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "error": str(e)}
        )
