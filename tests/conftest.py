"""
Pytest 설정 및 공통 Fixture
테스트 환경 설정 및 재사용 가능한 테스트 객체 정의
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_config_dir():
    """임시 설정 디렉토리"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def config_manager_instance(temp_config_dir):
    """ConfigManager 인스턴스"""
    from config.config_manager import ConfigManager
    return ConfigManager(config_dir=temp_config_dir)


@pytest.fixture
def sample_llm_settings():
    """샘플 LLM 설정"""
    return {
        "openai": {"api_key": "sk-" + "a" * 48},
        "anthropic": {"api_key": "sk-ant-" + "a" * 35},
        "google": {"api_key": "AIza" + "a" * 35},
        "huggingface": {"api_key": "hf_" + "a" * 20},
    }


@pytest.fixture
def sample_storage_settings():
    """샘플 저장소 설정"""
    return {
        "superthread": {
            "api_key": "st_" + "a" * 30,
            "workspace_id": "workspace_" + "a" * 20
        },
        "firebase": {
            "credentials_path": "/path/to/firebase-key.json"
        },
        "notion": {
            "api_key": "secret_" + "a" * 43,
            "database_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        },
        "mongodb": {
            "connection_string": "mongodb+srv://user:password@cluster.mongodb.net/database"
        }
    }


@pytest.fixture
def mock_encryption_key():
    """모의 암호화 키"""
    from cryptography.fernet import Fernet
    return Fernet.generate_key()


@pytest.fixture
def mock_google_docs_adapter():
    """모의 Google Docs 어댑터"""
    with patch('api_server_v2.app.adapters.google_docs.GoogleDocsAdapter') as mock:
        instance = MagicMock()
        instance.save_memory.return_value = {
            "success": True,
            "doc_id": "test_doc_123"
        }
        instance.get_memory.return_value = {
            "success": True,
            "memory": "test content"
        }
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_superthread_adapter():
    """모의 Superthread 어댑터"""
    with patch('api_server_v2.app.adapters.superthread.SuperthreadAdapter') as mock:
        instance = MagicMock()
        instance.save_memory.return_value = {
            "success": True,
            "doc_id": "doc_123"
        }
        instance.list_memories.return_value = {
            "success": True,
            "memories": [],
            "count": 0
        }
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_storage_factory():
    """모의 저장소 팩토리"""
    with patch('api_server_v2.app.adapters.factory.get_storage') as mock:
        adapter = MagicMock()
        adapter.save_memory.return_value = {"success": True}
        adapter.list_memories.return_value = {"success": True, "memories": []}
        mock.return_value = adapter
        yield mock


# ============================================================================
# 테스트 마크 (Markers)
# ============================================================================

def pytest_configure(config):
    """Pytest 설정"""
    config.addinivalue_line(
        "markers", "slow: 실행 시간이 오래 걸리는 테스트"
    )
    config.addinivalue_line(
        "markers", "unit: 단위 테스트"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "e2e: 엔드 투 엔드 테스트"
    )


# ============================================================================
# 테스트 후킹 (Hooks)
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """테스트 수집 후 수정"""
    for item in items:
        # 파일명에 따라 마크 추가
        if "test_validators" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_encryption" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_config_manager" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


# ============================================================================
# 세션 레벨 설정
# ============================================================================

@pytest.fixture(scope="session")
def test_config_data():
    """테스트용 설정 데이터"""
    return {
        "version": "1.0",
        "llm": {
            "selected": "openai",
            "settings": {
                "api_key": "sk-test1234567890"
            }
        },
        "storage": {
            "selected": "superthread",
            "settings": {
                "api_key": "st_test1234567890",
                "workspace_id": "workspace_test123"
            }
        }
    }


@pytest.fixture(scope="session")
def test_validators():
    """테스트용 Validators 설정"""
    return {
        "valid_openai_key": "sk-" + "a" * 48,
        "valid_anthropic_key": "sk-ant-" + "a" * 35,
        "valid_google_key": "AIza" + "a" * 35,
        "invalid_key": "invalid_key_format"
    }


# ============================================================================
# 환경 설정 (Environment Setup)
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """각 테스트 전 환경 설정"""
    # 테스트 환경 변수 설정
    os.environ['PYTEST_RUNNING'] = 'true'
    yield
    # 테스트 후 정리
    if 'PYTEST_RUNNING' in os.environ:
        del os.environ['PYTEST_RUNNING']


# ============================================================================
# 성능 측정 (Performance Tracking)
# ============================================================================

@pytest.fixture
def performance_tracker():
    """성능 측정 추적기"""
    import time

    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        def elapsed_ms(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return None

    return PerformanceTracker()


# ============================================================================
# 보조 함수
# ============================================================================

def create_temp_config_file(temp_dir, config_data):
    """임시 설정 파일 생성"""
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "user_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    return config_dir


def cleanup_temp_files(*paths):
    """임시 파일 정리"""
    for path in paths:
        if isinstance(path, Path) and path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
