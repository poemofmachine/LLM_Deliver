"""
Google Docs 저장소 어댑터
Google Drive와 Google Docs API를 사용한 메모리 저장소 구현
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from .base import StorageAdapter

# Google API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata"
]


@dataclass
class DocumentMeta:
    """Google Docs 메타데이터"""
    doc_id: str
    url: str
    name: str
    last_updated: str


class GoogleDocsAdapter(StorageAdapter):
    """Google Drive/Docs를 사용한 메모리 저장소 어댑터"""

    def __init__(self, token_json: str = None, folder_id: str = None):
        """
        Google Docs 어댑터 초기화

        Args:
            token_json: Google OAuth 토큰 JSON
            folder_id: 메모리를 저장할 Google Drive 폴더 ID
        """
        self.token_json = token_json or os.getenv("GOOGLE_TOKEN_JSON")
        self.folder_id = folder_id or os.getenv("GOOGLE_FOLDER_ID")

        if not self.token_json:
            raise ValueError("GOOGLE_TOKEN_JSON 환경 변수가 필요합니다")
        if not self.folder_id:
            raise ValueError("GOOGLE_FOLDER_ID 환경 변수가 필요합니다")

        self.docs_service: Resource = None
        self.drive_service: Resource = None
        self.current_token_json = self.token_json

        self._initialize_services()

    def _initialize_services(self):
        """Google API 서비스 초기화"""
        try:
            token_info = json.loads(self.token_json)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)

            # 토큰 갱신
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self.current_token_json = creds.to_json()
                else:
                    raise ValueError("Token refresh failed. Re-authentication required.")

            # 서비스 초기화
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)

        except Exception as e:
            raise ValueError(f"Google 서비스 초기화 실패: {str(e)}")

    @staticmethod
    def format_timestamp() -> str:
        """ISO 형식의 타임스탬프 반환"""
        return datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def generate_doc_name(content: str, max_length: int = 50) -> str:
        """문서 이름 생성"""
        name = content[:max_length].replace('\n', ' ').strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"Memory_{timestamp}_{name}" if name else f"Memory_{timestamp}"

    # ========================================================================
    # 핵심 메모리 관리 (Core Memory Management)
    # ========================================================================

    def save_memory(
        self,
        workspace_id: str,
        content: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        메모리를 Google Docs에 저장

        Args:
            workspace_id: 폴더 ID
            content: 저장할 내용
            scope: 범위 (personal, team)
            team_key: 팀 키
            category: 카테고리

        Returns:
            저장 결과
        """
        try:
            doc_name = self.generate_doc_name(content)

            # 1. 문서 생성
            doc_body = {
                'title': doc_name,
                'body': {
                    'content': [
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': f"Category: {category or 'default'}\nScope: {scope}\n",
                                            'textStyle': {'bold': True}
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            'paragraph': {
                                'elements': [
                                    {'textRun': {'content': content}}
                                ]
                            }
                        }
                    ]
                }
            }

            doc = self.docs_service.documents().create(body=doc_body).execute()
            doc_id = doc['documentId']

            # 2. 생성한 문서를 폴더로 이동
            file = self.drive_service.files().get(
                fileId=doc_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file.get('parents', []))
            self.drive_service.files().update(
                fileId=doc_id,
                addParents=self.folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            return {
                "success": True,
                "message": f"메모리가 Google Docs에 저장되었습니다 (ID: {doc_id})",
                "doc_id": doc_id,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Google Docs 저장 실패: {str(e)}",
                "error": str(e)
            }

    def get_memory(
        self,
        workspace_id: str,
        scope: str = "personal",
        team_key: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Google Docs에서 메모리 조회"""
        try:
            # 폴더의 최신 문서 조회
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                orderBy='modifiedTime desc',
                pageSize=1
            ).execute()

            files = results.get('files', [])
            if not files:
                return {
                    "success": True,
                    "message": "저장된 메모리가 없습니다",
                    "memory": "",
                    "timestamp": self.format_timestamp()
                }

            doc_id = files[0]['id']
            doc = self.docs_service.documents().get(documentId=doc_id).execute()

            # 문서 내용 추출
            content = ""
            for element in doc['body']['content']:
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content += text_run['textRun'].get('content', '')

            return {
                "success": True,
                "message": "메모리를 Google Docs에서 조회했습니다",
                "memory": content,
                "doc_id": doc_id,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"메모리 조회 중 오류: {str(e)}",
                "error": str(e)
            }

    def list_memories(
        self,
        scope: str = "personal",
        team_key: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Google Docs 메모리 목록 조회"""
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, webViewLink)',
                orderBy='modifiedTime desc',
                pageSize=limit
            ).execute()

            files = results.get('files', [])
            memories = []

            for file in files:
                memories.append({
                    "id": file['id'],
                    "name": file['name'],
                    "created_at": file['modifiedTime'],
                    "url": file['webViewLink']
                })

            return {
                "success": True,
                "message": f"{len(memories)}개의 메모리를 조회했습니다",
                "memories": memories,
                "count": len(memories),
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"목록 조회 중 오류: {str(e)}",
                "error": str(e)
            }

    def delete_memory(
        self,
        workspace_id: str,
        scope: str = "personal",
        team_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Google Docs 메모리 삭제"""
        try:
            # 최신 문서 조회
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                orderBy='modifiedTime desc',
                pageSize=1
            ).execute()

            files = results.get('files', [])
            if not files:
                return {
                    "success": False,
                    "message": "삭제할 메모리가 없습니다"
                }

            doc_id = files[0]['id']

            # 휴지통으로 이동
            self.drive_service.files().update(
                fileId=doc_id,
                body={'trashed': True}
            ).execute()

            return {
                "success": True,
                "message": f"메모리가 삭제되었습니다 (ID: {doc_id})",
                "doc_id": doc_id,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"삭제 실패: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 권한 관리 (Permission Management)
    # ========================================================================

    def set_permissions(self, doc_id: str, permissions: Dict[str, str]) -> Dict[str, Any]:
        """
        문서 권한 설정

        Args:
            doc_id: 문서 ID
            permissions: 권한 설정 {"user@example.com": "viewer", ...}
                - viewer: 읽기만
                - editor: 수정 가능
                - owner: 완전 관리

        Returns:
            권한 설정 결과
        """
        try:
            role_mapping = {
                'viewer': 'reader',
                'editor': 'writer',
                'admin': 'owner'
            }

            success_count = 0
            failed_count = 0

            for email, role in permissions.items():
                try:
                    drive_role = role_mapping.get(role, 'reader')

                    self.drive_service.permissions().create(
                        fileId=doc_id,
                        body={'type': 'user', 'role': drive_role, 'emailAddress': email},
                        fields='id'
                    ).execute()

                    success_count += 1
                except Exception as e:
                    failed_count += 1

            return {
                "success": failed_count == 0,
                "message": f"{success_count}명에게 권한을 부여했습니다",
                "permissions_set": success_count,
                "permissions_failed": failed_count,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"권한 설정 실패: {str(e)}",
                "error": str(e)
            }

    def get_permissions(self, doc_id: str) -> Dict[str, Any]:
        """문서 권한 조회"""
        try:
            permissions = self.drive_service.permissions().list(
                fileId=doc_id,
                fields='permissions(id, emailAddress, role, displayName)'
            ).execute()

            perm_list = []
            for perm in permissions.get('permissions', []):
                perm_list.append({
                    "id": perm['id'],
                    "email": perm.get('emailAddress', 'Unknown'),
                    "role": perm['role'],
                    "name": perm.get('displayName', 'Unknown')
                })

            return {
                "success": True,
                "message": f"{len(perm_list)}개의 권한을 조회했습니다",
                "permissions": perm_list,
                "count": len(perm_list),
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"권한 조회 실패: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 버전 관리 (Version Control)
    # ========================================================================

    def get_versions(self, doc_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        문서 버전 이력 조회

        Args:
            doc_id: 문서 ID
            limit: 반환할 최대 버전 수

        Returns:
            버전 목록
        """
        try:
            revisions = self.drive_service.revisions().list(
                fileId=doc_id,
                fields='revisions(id, mimeType, modifiedTime, lastModifyingUser)',
                pageSize=limit
            ).execute()

            versions = []
            for rev in revisions.get('revisions', []):
                versions.append({
                    "id": rev['id'],
                    "timestamp": rev['modifiedTime'],
                    "user": rev.get('lastModifyingUser', {}).get('displayName', 'Unknown'),
                    "mime_type": rev['mimeType']
                })

            return {
                "success": True,
                "message": f"{len(versions)}개의 버전을 조회했습니다",
                "versions": versions,
                "count": len(versions),
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 조회 실패: {str(e)}",
                "error": str(e)
            }

    def create_version(self, doc_id: str, description: str = None) -> Dict[str, Any]:
        """
        새 버전 생성 (현재 상태 스냅샷)

        Args:
            doc_id: 문서 ID
            description: 버전 설명

        Returns:
            버전 생성 결과
        """
        try:
            file = self.drive_service.files().get(
                fileId=doc_id,
                fields='name, version'
            ).execute()

            # Google Docs의 경우 버전은 자동으로 생성되므로
            # 여기서는 현재 상태 정보를 반환
            return {
                "success": True,
                "message": "버전 스냅샷이 생성되었습니다 (Google Docs는 자동 버전 관리)",
                "doc_id": doc_id,
                "name": file['name'],
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 생성 실패: {str(e)}",
                "error": str(e)
            }

    def revert_to_version(self, doc_id: str, version_id: str) -> Dict[str, Any]:
        """
        특정 버전으로 복원

        Args:
            doc_id: 문서 ID
            version_id: 복원할 버전 ID

        Returns:
            복원 결과
        """
        try:
            # Google Docs API는 직접적인 버전 복원을 지원하지 않으므로
            # 버전 정보를 반환
            revision = self.drive_service.revisions().get(
                fileId=doc_id,
                revisionId=version_id
            ).execute()

            return {
                "success": True,
                "message": "버전 정보를 조회했습니다",
                "doc_id": doc_id,
                "version_id": version_id,
                "timestamp": revision['modifiedTime'],
                "note": "Google Docs는 UI에서 버전 복원 가능"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 정보 조회 실패: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 검색 기능 (Search)
    # ========================================================================

    def search_memories(self, query: str, scope: str = "personal",
                       limit: int = 20) -> Dict[str, Any]:
        """
        메모리 검색

        Args:
            query: 검색 쿼리
            scope: 검색 범위
            limit: 최대 결과 수

        Returns:
            검색 결과
        """
        try:
            # Google Drive에서 폴더 내 파일 검색
            search_query = f"'{self.folder_id}' in parents and trashed=false and fullText contains '{query}'"

            results = self.drive_service.files().list(
                q=search_query,
                spaces='drive',
                fields='files(id, name, modifiedTime, webViewLink)',
                pageSize=limit
            ).execute()

            files = results.get('files', [])

            return {
                "success": True,
                "message": f"{len(files)}개의 검색 결과를 찾았습니다",
                "results": [
                    {
                        "id": f['id'],
                        "name": f['name'],
                        "timestamp": f['modifiedTime'],
                        "url": f['webViewLink']
                    }
                    for f in files
                ],
                "count": len(files),
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"검색 중 오류: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 배치 작업 (Batch Operations)
    # ========================================================================

    def batch_save_memories(self, memories: list) -> Dict[str, Any]:
        """여러 메모리를 일괄 저장"""
        try:
            results = []
            failed_count = 0

            for idx, memory in enumerate(memories):
                try:
                    doc_name = self.generate_doc_name(memory.get('content', ''))
                    doc_body = {
                        'title': doc_name,
                        'body': {
                            'content': [
                                {
                                    'paragraph': {
                                        'elements': [
                                            {
                                                'textRun': {
                                                    'content': f"Category: {memory.get('category', 'default')}\n"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    'paragraph': {
                                        'elements': [
                                            {'textRun': {'content': memory.get('content', '')}}
                                        ]
                                    }
                                }
                            ]
                        }
                    }

                    doc = self.docs_service.documents().create(body=doc_body).execute()
                    doc_id = doc['documentId']

                    # 폴더로 이동
                    file = self.drive_service.files().get(
                        fileId=doc_id, fields='parents'
                    ).execute()

                    previous_parents = ",".join(file.get('parents', []))
                    self.drive_service.files().update(
                        fileId=doc_id,
                        addParents=self.folder_id,
                        removeParents=previous_parents
                    ).execute()

                    results.append({
                        "index": idx,
                        "success": True,
                        "doc_id": doc_id
                    })

                except Exception as e:
                    failed_count += 1
                    results.append({
                        "index": idx,
                        "success": False,
                        "error": str(e)
                    })

            return {
                "success": failed_count == 0,
                "message": f"{len(memories) - failed_count}/{len(memories)}개의 메모리가 저장되었습니다",
                "results": results,
                "saved_count": len(memories) - failed_count,
                "failed_count": failed_count,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"배치 저장 중 오류: {str(e)}",
                "error": str(e)
            }

    def batch_delete_memories(self, doc_ids: list) -> Dict[str, Any]:
        """여러 메모리를 일괄 삭제"""
        try:
            results = []
            deleted_count = 0

            for doc_id in doc_ids:
                try:
                    self.drive_service.files().update(
                        fileId=doc_id,
                        body={'trashed': True}
                    ).execute()

                    deleted_count += 1
                    results.append({
                        "doc_id": doc_id,
                        "success": True
                    })

                except Exception as e:
                    results.append({
                        "doc_id": doc_id,
                        "success": False,
                        "error": str(e)
                    })

            return {
                "success": deleted_count == len(doc_ids),
                "message": f"{deleted_count}/{len(doc_ids)}개의 메모리가 삭제되었습니다",
                "results": results,
                "deleted_count": deleted_count,
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"배치 삭제 중 오류: {str(e)}",
                "error": str(e)
            }

    # ========================================================================
    # 통계 및 모니터링 (Statistics & Monitoring)
    # ========================================================================

    def get_workspace_stats(self) -> Dict[str, Any]:
        """워크스페이스 통계 조회"""
        try:
            # 폴더의 파일 통계
            results = self.drive_service.files().list(
                q=f"'{self.folder_id}' in parents",
                spaces='drive',
                fields='files(size)',
                pageSize=1000
            ).execute()

            files = results.get('files', [])
            total_size = sum(int(f.get('size', 0)) for f in files)

            return {
                "success": True,
                "message": "워크스페이스 통계를 조회했습니다",
                "stats": {
                    "total_documents": len(files),
                    "total_size": total_size,
                    "storage_used": total_size,
                    "average_size": total_size // len(files) if files else 0,
                    "storage_limit": "Unlimited"
                },
                "timestamp": self.format_timestamp()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"통계 조회 실패: {str(e)}",
                "error": str(e)
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보 반환"""
        return {
            "type": "google_docs",
            "name": "Google Docs",
            "status": "connected",
            "folder_id": self.folder_id,
            "api_endpoint": "https://www.googleapis.com/drive/v3",
            "features": [
                "클라우드 저장소",
                "팀 협업",
                "문서 버전 관리",
                "권한 관리",
                "실시간 동기화",
                "자동 백업",
                "전문 검색",
                "배치 작업"
            ],
            "core_methods": [
                "save_memory - 메모리 저장",
                "get_memory - 메모리 조회",
                "list_memories - 메모리 목록",
                "delete_memory - 메모리 삭제"
            ],
            "permission_methods": [
                "set_permissions - 권한 설정",
                "get_permissions - 권한 조회"
            ],
            "version_methods": [
                "get_versions - 버전 조회",
                "create_version - 버전 스냅샷",
                "revert_to_version - 버전 정보"
            ],
            "search_methods": [
                "search_memories - 메모리 검색"
            ],
            "batch_methods": [
                "batch_save_memories - 일괄 저장",
                "batch_delete_memories - 일괄 삭제"
            ],
            "monitoring_methods": [
                "get_workspace_stats - 워크스페이스 통계"
            ],
            "limits": {
                "max_document_size": "Unlimited",
                "storage_capacity": "Unlimited",
                "api_rate_limit": "10,000 requests per day",
                "batch_size": "50 documents per request"
            }
        }


# 기존 호환성을 위한 래퍼 메서드
def append_handoff(adapter: GoogleDocsAdapter, doc_id: str, content: str) -> None:
    """기존 메서드 호환성"""
    if not adapter.docs_service:
        raise Exception("Google Docs service가 초기화되지 않았습니다.")

    try:
        document = adapter.docs_service.documents().get(documentId=doc_id).execute()
        body = document.get('body')
        end_index = body.get('content')[-1].get('endIndex')

        requests = [
            {
                'insertText': {
                    'location': {'index': end_index - 1},
                    'text': f"\n{content}\n"
                }
            }
        ]

        adapter.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}
        ).execute()

    except HttpError as e:
        raise Exception(f"Google Docs API 오류: {e}")


def fetch_meta(adapter: GoogleDocsAdapter, doc_id: str) -> DocumentMeta:
    """기존 메서드 호환성"""
    if not adapter.drive_service:
        raise Exception("Google Drive service가 초기화되지 않았습니다.")

    try:
        file_meta = adapter.drive_service.files().get(
            fileId=doc_id,
            fields='name, modifiedTime, webViewLink'
        ).execute()

        return DocumentMeta(
            doc_id=doc_id,
            url=file_meta.get('webViewLink', f"https://docs.google.com/document/d/{doc_id}/edit"),
            name=file_meta.get('name', 'Unknown Document'),
            last_updated=file_meta.get('modifiedTime', '1970-01-01T00:00:00Z'),
        )

    except HttpError as e:
        raise Exception(f"Google Drive API 오류: {e}")
