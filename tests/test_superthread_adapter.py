"""
Superthread 저장소 어댑터 테스트
Superthread API 통합 테스트
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from api_server_v2.app.adapters.superthread import SuperthreadAdapter


class TestSuperthreadAdapter:
    """Superthread 어댑터 테스트"""

    @pytest.fixture
    def adapter(self):
        """Superthread 어댑터 인스턴스 생성"""
        with patch.dict(os.environ, {
            'SUPERTHREAD_API_KEY': 'test_key_123',
            'SUPERTHREAD_WORKSPACE_ID': 'workspace_123'
        }):
            return SuperthreadAdapter()

    # ========================================================================
    # 초기화 테스트
    # ========================================================================

    def test_adapter_initialization(self, adapter):
        """어댑터 초기화 테스트"""
        assert adapter.api_key == 'test_key_123'
        assert adapter.workspace_id == 'workspace_123'
        assert adapter.base_url == "https://api.superthread.com/v1"
        assert "Bearer test_key_123" in adapter.headers["Authorization"]

    def test_missing_api_key(self):
        """API 키 누락 시 에러 발생"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SUPERTHREAD_API_KEY"):
                SuperthreadAdapter()

    def test_missing_workspace_id(self):
        """Workspace ID 누락 시 에러 발생"""
        with patch.dict(os.environ, {'SUPERTHREAD_API_KEY': 'test_key'}, clear=True):
            with pytest.raises(ValueError, match="SUPERTHREAD_WORKSPACE_ID"):
                SuperthreadAdapter()

    # ========================================================================
    # 메모리 관리 테스트
    # ========================================================================

    @patch('requests.post')
    def test_save_memory_success(self, mock_post, adapter):
        """메모리 저장 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'doc_123',
            'content': '테스트 메모리',
            'created_at': '2024-11-18T00:00:00Z'
        }
        mock_post.return_value = mock_response

        result = adapter.save_memory(
            workspace_id='workspace_123',
            content='테스트 메모리',
            scope='personal'
        )

        assert result['success'] is True
        assert 'doc_123' in result['doc_id']
        assert 'saved' in result['message'].lower() or 'superthread' in result['message'].lower()

    @patch('requests.post')
    def test_save_memory_failure(self, mock_post, adapter):
        """메모리 저장 실패 테스트"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        result = adapter.save_memory(
            workspace_id='workspace_123',
            content='테스트 메모리',
            scope='personal'
        )

        assert result['success'] is False
        assert 'error' in result or 'failed' in result['message'].lower()

    @patch('requests.get')
    def test_list_memories_success(self, mock_get, adapter):
        """메모리 목록 조회 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 'doc_1', 'content': '메모리 1', 'created_at': '2024-11-18T00:00:00Z'},
            {'id': 'doc_2', 'content': '메모리 2', 'created_at': '2024-11-18T01:00:00Z'},
        ]
        mock_get.return_value = mock_response

        result = adapter.list_memories(scope='personal', limit=10)

        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['memories']) == 2

    @patch('requests.delete')
    def test_delete_memory_success(self, mock_delete, adapter):
        """메모리 삭제 성공 테스트"""
        # 먼저 get을 위한 mock 설정
        with patch('requests.get') as mock_get:
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = [
                {'id': 'doc_123', 'content': '메모리'}
            ]
            mock_get.return_value = mock_get_response

            mock_response = Mock()
            mock_response.status_code = 200
            mock_delete.return_value = mock_response

            result = adapter.delete_memory(
                workspace_id='workspace_123',
                scope='personal'
            )

            assert result['success'] is True
            assert 'deleted' in result['message'].lower()

    # ========================================================================
    # 권한 관리 테스트
    # ========================================================================

    @patch('requests.post')
    def test_set_permissions_success(self, mock_post, adapter):
        """권한 설정 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'permissions': 'set'}
        mock_post.return_value = mock_response

        permissions = {
            'user@example.com': 'viewer',
            'admin@example.com': 'admin'
        }

        result = adapter.set_permissions('doc_123', permissions)

        assert result['success'] is True
        assert 'permissions' in result['message'].lower()

    @patch('requests.get')
    def test_get_permissions_success(self, mock_get, adapter):
        """권한 조회 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'permissions': [
                {'id': 'user@example.com', 'role': 'viewer'},
                {'id': 'admin@example.com', 'role': 'admin'}
            ]
        }
        mock_get.return_value = mock_response

        result = adapter.get_permissions('doc_123')

        assert result['success'] is True
        assert len(result['permissions']) >= 0

    # ========================================================================
    # 버전 관리 테스트
    # ========================================================================

    @patch('requests.get')
    def test_get_versions_success(self, mock_get, adapter):
        """버전 조회 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'versions': [
                {'id': 'v_1', 'timestamp': '2024-11-18T00:00:00Z'},
                {'id': 'v_2', 'timestamp': '2024-11-18T01:00:00Z'},
            ]
        }
        mock_get.return_value = mock_response

        result = adapter.get_versions('doc_123', limit=10)

        assert result['success'] is True
        assert result['count'] == 2

    @patch('requests.post')
    def test_create_version_success(self, mock_post, adapter):
        """버전 생성 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'v_3'}
        mock_post.return_value = mock_response

        result = adapter.create_version('doc_123', 'Test version')

        assert result['success'] is True
        assert 'created' in result['message'].lower()

    @patch('requests.post')
    def test_revert_to_version_success(self, mock_post, adapter):
        """버전 복원 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'doc_123'}
        mock_post.return_value = mock_response

        result = adapter.revert_to_version('doc_123', 'v_1')

        assert result['success'] is True
        assert 'restored' in result['message'].lower()

    # ========================================================================
    # 검색 테스트
    # ========================================================================

    @patch('requests.post')
    def test_search_memories_success(self, mock_post, adapter):
        """메모리 검색 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {'id': 'doc_1', 'content': 'Python 검색결과'},
                {'id': 'doc_2', 'content': 'Python 프로그래밍'},
            ]
        }
        mock_post.return_value = mock_response

        result = adapter.search_memories('Python', scope='personal', limit=20)

        assert result['success'] is True
        assert result['count'] == 2

    # ========================================================================
    # 배치 작업 테스트
    # ========================================================================

    @patch('requests.post')
    def test_batch_save_memories_success(self, mock_post, adapter):
        """배치 저장 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'doc_new'}
        mock_post.return_value = mock_response

        memories = [
            {'content': '메모리 1', 'scope': 'personal'},
            {'content': '메모리 2', 'scope': 'personal'},
        ]

        result = adapter.batch_save_memories(memories)

        assert result['success'] is True
        assert result['saved_count'] == 2
        assert result['failed_count'] == 0

    @patch('requests.delete')
    def test_batch_delete_memories_success(self, mock_delete, adapter):
        """배치 삭제 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        doc_ids = ['doc_1', 'doc_2', 'doc_3']
        result = adapter.batch_delete_memories(doc_ids)

        assert result['success'] is True
        assert result['deleted_count'] == 3

    # ========================================================================
    # 통계 테스트
    # ========================================================================

    @patch('requests.get')
    def test_get_workspace_stats_success(self, mock_get, adapter):
        """워크스페이스 통계 조회 성공 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'total_documents': 42,
            'total_size': 1024000,
            'members': 5,
            'teams': 2,
            'storage_used': 512000,
            'storage_limit': 'Unlimited'
        }
        mock_get.return_value = mock_response

        result = adapter.get_workspace_stats()

        assert result['success'] is True
        assert result['stats']['total_documents'] == 42
        assert result['stats']['members'] == 5

    # ========================================================================
    # 저장소 정보 테스트
    # ========================================================================

    def test_get_storage_info(self, adapter):
        """저장소 정보 조회 테스트"""
        info = adapter.get_storage_info()

        assert info['type'] == 'superthread'
        assert info['name'] == 'Superthread'
        assert 'features' in info
        assert 'core_methods' in info
        assert 'permission_methods' in info
        assert 'version_methods' in info
        assert 'search_methods' in info
        assert 'batch_methods' in info
        assert 'monitoring_methods' in info

    # ========================================================================
    # 타임스탬프 테스트
    # ========================================================================

    def test_format_timestamp(self, adapter):
        """타임스탬프 포맷 테스트"""
        timestamp = adapter.format_timestamp()

        assert isinstance(timestamp, str)
        assert 'T' in timestamp  # ISO format
        assert len(timestamp) > 0

    # ========================================================================
    # 에러 처리 테스트
    # ========================================================================

    @patch('requests.post')
    def test_request_timeout(self, mock_post, adapter):
        """요청 타임아웃 테스트"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = adapter.save_memory(
            workspace_id='workspace_123',
            content='테스트',
            scope='personal'
        )

        assert result['success'] is False
        assert 'timeout' in result['message'].lower()

    @patch('requests.post')
    def test_connection_error(self, mock_post, adapter):
        """연결 에러 테스트"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = adapter.save_memory(
            workspace_id='workspace_123',
            content='테스트',
            scope='personal'
        )

        assert result['success'] is False
        assert 'error' in result

    # ========================================================================
    # 유효성 검사 테스트
    # ========================================================================

    def test_invalid_permission_level(self, adapter):
        """유효하지 않은 권한 레벨 테스트"""
        with patch('requests.post') as mock_post:
            permissions = {'user@example.com': 'invalid_role'}

            result = adapter.set_permissions('doc_123', permissions)

            assert result['success'] is False
            assert 'invalid' in result['message'].lower()


class TestSuperthreadIntegration:
    """통합 테스트"""

    @pytest.fixture
    def adapter(self):
        """실제 환경에서의 어댑터 (테스트용)"""
        with patch.dict(os.environ, {
            'SUPERTHREAD_API_KEY': 'test_integration_key',
            'SUPERTHREAD_WORKSPACE_ID': 'workspace_integration'
        }):
            return SuperthreadAdapter()

    def test_end_to_end_workflow(self, adapter):
        """엔드 투 엔드 워크플로우 테스트"""
        # 이 테스트는 실제 API가 필요하므로 mock으로 진행
        with patch('requests.post') as mock_post, \
             patch('requests.get') as mock_get, \
             patch('requests.delete') as mock_delete:

            # 1. 메모리 저장
            mock_post.return_value = Mock(
                status_code=201,
                json=lambda: {'id': 'doc_workflow_test'}
            )
            save_result = adapter.save_memory(
                workspace_id='workspace_integration',
                content='워크플로우 테스트',
                scope='personal'
            )
            assert save_result['success'] is True

            # 2. 메모리 조회
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: [{'id': 'doc_workflow_test', 'content': '워크플로우 테스트'}]
            )
            list_result = adapter.list_memories(scope='personal')
            assert list_result['success'] is True

            # 3. 메모리 삭제
            mock_delete.return_value = Mock(status_code=200)
            # delete_memory는 먼저 get을 호출하므로
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: [{'id': 'doc_workflow_test'}]
            )
            delete_result = adapter.delete_memory(
                workspace_id='workspace_integration',
                scope='personal'
            )
            assert delete_result['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
