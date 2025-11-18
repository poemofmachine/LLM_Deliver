"""
Superthread API 저장소 어댑터
Superthread를 사용한 클라우드 메모리 저장소 구현
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from .base import StorageAdapter


class SuperthreadAdapter(StorageAdapter):
    """Superthread API를 통한 메모리 저장소 구현"""

    def __init__(self, api_key: str = None, workspace_id: str = None):
        """
        Superthread 어댑터 초기화

        Args:
            api_key: Superthread API 키
            workspace_id: Superthread Workspace ID
        """
        self.api_key = api_key or os.getenv("SUPERTHREAD_API_KEY")
        self.workspace_id = workspace_id or os.getenv("SUPERTHREAD_WORKSPACE_ID")

        if not self.api_key:
            raise ValueError("SUPERTHREAD_API_KEY 환경 변수가 필요합니다")
        if not self.workspace_id:
            raise ValueError("SUPERTHREAD_WORKSPACE_ID 환경 변수가 필요합니다")

        self.base_url = "https://api.superthread.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def save_memory(self, workspace_id: str, content: str, scope: str,
                   team_key: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """
        메모리를 Superthread에 저장

        Args:
            workspace_id: 작업공간 ID
            content: 저장할 내용
            scope: 범위 (personal, team, public)
            team_key: 팀 키 (선택사항)
            category: 카테고리 (선택사항)

        Returns:
            저장 결과 (success, message, doc_id, revision_id)
        """
        try:
            # 문서 데이터 구성
            doc_data = {
                "workspace_id": workspace_id,
                "content": content,
                "scope": scope,
                "team_key": team_key,
                "category": category or "default",
                "created_at": self.format_timestamp(),
                "updated_at": self.format_timestamp()
            }

            # Superthread API에 저장
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=doc_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json()
                doc_id = result.get("id") or result.get("document_id")
                revision_id = self.generate_revision_id()

                return {
                    "success": True,
                    "message": f"메모리가 Superthread에 저장되었습니다 (ID: {doc_id})",
                    "doc_id": doc_id,
                    "revision_id": revision_id,
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"Superthread 저장 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Superthread API 요청 시간 초과",
                "error": "timeout"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Superthread 연결 오류: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"메모리 저장 중 오류: {str(e)}",
                "error": str(e)
            }

    def get_memory(self, workspace_id: str, scope: str,
                  team_key: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Superthread에서 메모리 조회

        Args:
            workspace_id: 작업공간 ID
            scope: 범위 (personal, team, public)
            team_key: 팀 키 (선택사항)
            category: 카테고리 (선택사항)

        Returns:
            조회 결과 (success, message, memory, timestamp)
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents"

            params = {
                "scope": scope,
                "team_key": team_key,
                "category": category or "default"
            }

            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                documents = response.json()

                if documents:
                    # 최신 문서 반환
                    latest_doc = documents[0] if isinstance(documents, list) else documents

                    return {
                        "success": True,
                        "message": "메모리를 Superthread에서 조회했습니다",
                        "memory": latest_doc.get("content", ""),
                        "doc_id": latest_doc.get("id"),
                        "timestamp": self.format_timestamp()
                    }
                else:
                    return {
                        "success": True,
                        "message": "저장된 메모리가 없습니다",
                        "memory": "",
                        "timestamp": self.format_timestamp()
                    }
            else:
                return {
                    "success": False,
                    "message": f"Superthread 조회 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"메모리 조회 중 오류: {str(e)}",
                "error": str(e)
            }

    def list_memories(self, scope: str, team_key: Optional[str] = None,
                     limit: int = 10) -> Dict[str, Any]:
        """
        Superthread에서 메모리 목록 조회

        Args:
            scope: 범위 (personal, team, public)
            team_key: 팀 키 (선택사항)
            limit: 반환할 최대 문서 수

        Returns:
            메모리 목록 (success, message, memories)
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents"

            params = {
                "scope": scope,
                "team_key": team_key,
                "limit": limit
            }

            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                documents = response.json()

                memories = []
                if isinstance(documents, list):
                    for doc in documents:
                        memories.append({
                            "id": doc.get("id"),
                            "content": doc.get("content", ""),
                            "created_at": doc.get("created_at"),
                            "updated_at": doc.get("updated_at")
                        })

                return {
                    "success": True,
                    "message": f"{len(memories)}개의 메모리를 조회했습니다",
                    "memories": memories,
                    "count": len(memories)
                }
            else:
                return {
                    "success": False,
                    "message": f"목록 조회 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"목록 조회 중 오류: {str(e)}",
                "error": str(e)
            }

    def delete_memory(self, workspace_id: str, scope: str,
                     team_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Superthread에서 메모리 삭제

        Args:
            workspace_id: 작업공간 ID
            scope: 범위 (personal, team, public)
            team_key: 팀 키 (선택사항)

        Returns:
            삭제 결과 (success, message)
        """
        try:
            # 먼저 문서 조회
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents"
            params = {"scope": scope, "team_key": team_key}

            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "삭제할 메모리를 찾을 수 없습니다"
                }

            documents = response.json()
            if not documents:
                return {
                    "success": False,
                    "message": "삭제할 메모리가 없습니다"
                }

            # 첫 번째 문서 삭제
            doc_id = documents[0].get("id") if isinstance(documents, list) else documents.get("id")
            delete_endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}"

            delete_response = requests.delete(
                delete_endpoint,
                headers=self.headers,
                timeout=10
            )

            if delete_response.status_code in [200, 204]:
                return {
                    "success": True,
                    "message": f"메모리가 삭제되었습니다 (ID: {doc_id})",
                    "doc_id": doc_id
                }
            else:
                return {
                    "success": False,
                    "message": f"삭제 실패 (상태코드: {delete_response.status_code})",
                    "error": delete_response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"메모리 삭제 중 오류: {str(e)}",
                "error": str(e)
            }

    # ============================================================================
    # 권한 관리 (Permission Management)
    # ============================================================================

    def set_permissions(self, doc_id: str, permissions: Dict[str, str]) -> Dict[str, Any]:
        """
        문서 권한 설정

        Args:
            doc_id: 문서 ID
            permissions: 권한 설정 (사용자/팀별)
                {
                    "user@example.com": "viewer",  # viewer, editor, admin
                    "team-key": "editor"
                }

        Returns:
            권한 설정 결과
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}/permissions"

            for user_or_team, permission_level in permissions.items():
                if permission_level not in ["viewer", "editor", "admin"]:
                    return {
                        "success": False,
                        "message": f"유효하지 않은 권한: {permission_level}",
                        "error": "invalid_permission"
                    }

            data = {
                "permissions": [
                    {
                        "id": user_or_team,
                        "role": permission_level,
                        "type": "user" if "@" in user_or_team else "team"
                    }
                    for user_or_team, permission_level in permissions.items()
                ]
            }

            response = requests.post(
                endpoint,
                headers=self.headers,
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "message": f"{len(permissions)}개의 권한이 설정되었습니다",
                    "permissions": permissions,
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"권한 설정 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"권한 설정 중 오류: {str(e)}",
                "error": str(e)
            }

    def get_permissions(self, doc_id: str) -> Dict[str, Any]:
        """
        문서 권한 조회

        Args:
            doc_id: 문서 ID

        Returns:
            권한 목록
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}/permissions"

            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                permissions = response.json().get("permissions", [])
                return {
                    "success": True,
                    "message": f"{len(permissions)}개의 권한이 조회되었습니다",
                    "permissions": permissions,
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"권한 조회 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"권한 조회 중 오류: {str(e)}",
                "error": str(e)
            }

    # ============================================================================
    # 버전 관리 (Version Management)
    # ============================================================================

    def get_versions(self, doc_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        문서 버전 목록 조회

        Args:
            doc_id: 문서 ID
            limit: 반환할 최대 버전 수

        Returns:
            버전 목록
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}/versions"

            params = {"limit": limit}

            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                versions = response.json().get("versions", [])
                return {
                    "success": True,
                    "message": f"{len(versions)}개의 버전이 조회되었습니다",
                    "versions": versions,
                    "count": len(versions),
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"버전 조회 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 조회 중 오류: {str(e)}",
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
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}/versions/{version_id}/restore"

            response = requests.post(
                endpoint,
                headers=self.headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "message": f"버전이 복원되었습니다 (ID: {version_id})",
                    "version_id": version_id,
                    "doc_id": doc_id,
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"버전 복원 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 복원 중 오류: {str(e)}",
                "error": str(e)
            }

    def create_version(self, doc_id: str, description: str = None) -> Dict[str, Any]:
        """
        현재 상태를 새 버전으로 저장

        Args:
            doc_id: 문서 ID
            description: 버전 설명 (선택사항)

        Returns:
            새 버전 생성 결과
        """
        try:
            endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/documents/{doc_id}/versions"

            data = {
                "description": description or f"자동 저장 버전 ({self.format_timestamp()})"
            }

            response = requests.post(
                endpoint,
                headers=self.headers,
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json()
                version_id = result.get("id") or result.get("version_id")
                return {
                    "success": True,
                    "message": f"새 버전이 생성되었습니다 (ID: {version_id})",
                    "version_id": version_id,
                    "doc_id": doc_id,
                    "timestamp": self.format_timestamp()
                }
            else:
                return {
                    "success": False,
                    "message": f"버전 생성 실패 (상태코드: {response.status_code})",
                    "error": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"버전 생성 중 오류: {str(e)}",
                "error": str(e)
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보 반환"""
        return {
            "type": "superthread",
            "name": "Superthread",
            "status": "connected",
            "workspace_id": self.workspace_id,
            "api_endpoint": self.base_url,
            "features": [
                "클라우드 저장소",
                "팀 협업",
                "문서 버전 관리",
                "권한 관리",
                "실시간 동기화",
                "자동 백업"
            ],
            "advanced_features": [
                "set_permissions - 권한 설정",
                "get_permissions - 권한 조회",
                "get_versions - 버전 조회",
                "revert_to_version - 버전 복원",
                "create_version - 버전 생성"
            ],
            "limits": {
                "max_document_size": "Unlimited",
                "storage_capacity": "Unlimited",
                "api_rate_limit": "1000/hour"
            }
        }
