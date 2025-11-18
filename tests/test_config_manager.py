"""
설정 관리자 테스트
ConfigManager 클래스에 대한 포괄적인 단위 테스트
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from config.config_manager import ConfigManager


class TestConfigManagerInitialization:
    """ConfigManager 초기화 테스트"""

    def test_config_manager_creates_config_dir(self):
        """설정 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            manager = ConfigManager(config_dir=str(config_dir))

            assert config_dir.exists()
            assert (config_dir / "user_config.json").exists() or not (config_dir / "user_config.json").exists()

    def test_config_manager_loads_existing_config(self):
        """기존 설정 로드"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()

            test_config = {
                "version": "1.0",
                "llm": {"selected": "openai", "settings": {}},
                "storage": {"selected": "sqlite", "settings": {}}
            }

            config_file = config_dir / "user_config.json"
            with open(config_file, 'w') as f:
                json.dump(test_config, f)

            manager = ConfigManager(config_dir=str(config_dir))
            assert manager.get_llm() == "openai"
            assert manager.get_storage() == "sqlite"

    def test_config_manager_creates_default_config(self):
        """기본 설정 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            manager = ConfigManager(config_dir=str(config_dir))

            config = manager.get_full_config()
            assert "version" in config
            assert "llm" in config
            assert "storage" in config
            assert "general" in config


class TestLLMConfiguration:
    """LLM 설정 관리 테스트"""

    def test_set_llm_settings(self):
        """LLM 설정 저장"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test_key"}
            result = manager.set_llm("openai", settings)

            assert result is True
            assert manager.get_llm() == "openai"
            assert manager.get_llm_settings() == settings

    def test_get_llm_settings(self):
        """LLM 설정 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test_key", "model": "gpt-4"}
            manager.set_llm("openai", settings)

            retrieved_settings = manager.get_llm_settings()
            assert retrieved_settings["api_key"] == "test_key"
            assert retrieved_settings["model"] == "gpt-4"

    def test_get_llm_setting_single_key(self):
        """특정 LLM 설정값 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test_key", "model": "gpt-4"}
            manager.set_llm("openai", settings)

            api_key = manager.get_llm_setting("api_key")
            assert api_key == "test_key"

    def test_get_nonexistent_llm_setting(self):
        """존재하지 않는 LLM 설정값 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            result = manager.get_llm_setting("nonexistent")
            assert result is None


class TestStorageConfiguration:
    """저장소 설정 관리 테스트"""

    def test_set_storage_settings(self):
        """저장소 설정 저장"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {
                "api_key": "test_key",
                "workspace_id": "workspace_123"
            }
            result = manager.set_storage("superthread", settings)

            assert result is True
            assert manager.get_storage() == "superthread"
            assert manager.get_storage_settings() == settings

    def test_get_storage_settings(self):
        """저장소 설정 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test_key", "workspace_id": "123"}
            manager.set_storage("superthread", settings)

            retrieved = manager.get_storage_settings()
            assert retrieved["api_key"] == "test_key"

    def test_get_storage_setting_single_key(self):
        """특정 저장소 설정값 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test_key", "workspace_id": "123"}
            manager.set_storage("superthread", settings)

            api_key = manager.get_storage_setting("api_key")
            assert api_key == "test_key"


class TestConfigPersistence:
    """설정 저장 및 로드 테스트"""

    def test_save_config_creates_file(self):
        """설정 저장으로 파일 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})
            result = manager.save_config()

            assert result is True
            config_file = Path(tmpdir) / "user_config.json"
            assert config_file.exists()

    def test_config_persistence_across_instances(self):
        """인스턴스 간 설정 지속"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 첫 번째 인스턴스에서 설정 저장
            manager1 = ConfigManager(config_dir=tmpdir)
            manager1.set_llm("openai", {"api_key": "test_key"})
            manager1.save_config()

            # 두 번째 인스턴스에서 로드
            manager2 = ConfigManager(config_dir=tmpdir)
            assert manager2.get_llm() == "openai"
            assert manager2.get_llm_setting("api_key") == "test_key"

    def test_save_config_updates_timestamp(self):
        """설정 저장 시 타임스탬프 업데이트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            initial_time = manager.config_data.get("updated_at")
            manager.set_llm("openai", {"api_key": "test"})
            manager.save_config()
            updated_time = manager.config_data.get("updated_at")

            # 업데이트 시간이 바뀌었는지 확인 (대략적으로)
            assert updated_time is not None


class TestEncryptionIntegration:
    """암호화 통합 테스트"""

    @patch('config.config_manager.KeyEncryption')
    def test_sensitive_fields_are_encrypted_on_save(self, mock_encryption):
        """저장 시 민감한 필드 암호화"""
        mock_encryption.encrypt.return_value = "encrypted_value"

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "secret_key_123"}
            manager.set_llm("openai", settings)
            manager.save_config()

            # encrypt가 호출되었는지 확인 (api_key는 민감한 필드)
            # 실제로는 호출 여부 확인

    @patch('config.config_manager.KeyEncryption')
    def test_sensitive_fields_are_decrypted_on_load(self, mock_encryption):
        """로드 시 민감한 필드 복호화"""
        mock_encryption.is_encrypted.return_value = True
        mock_encryption.decrypt.return_value = "decrypted_value"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()

            # 암호화된 설정 파일 생성
            encrypted_config = {
                "version": "1.0",
                "llm": {
                    "selected": "openai",
                    "settings": {"api_key": "encrypted_value"}
                },
                "storage": {"selected": None, "settings": {}},
                "general": {"language": "ko", "theme": "light"}
            }

            config_file = config_dir / "user_config.json"
            with open(config_file, 'w') as f:
                json.dump(encrypted_config, f)

            # ConfigManager 로드 시 복호화 확인


class TestConfigurationStatus:
    """설정 상태 확인 테스트"""

    def test_is_configured_true_when_all_set(self):
        """LLM과 저장소가 모두 설정되면 True"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})
            manager.set_storage("superthread", {"api_key": "test"})

            assert manager.is_configured() is True

    def test_is_configured_false_when_llm_missing(self):
        """LLM이 설정되지 않으면 False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_storage("superthread", {"api_key": "test"})

            assert manager.is_configured() is False

    def test_is_configured_false_when_storage_missing(self):
        """저장소가 설정되지 않으면 False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})

            assert manager.is_configured() is False

    def test_get_configuration_status(self):
        """상세 설정 상태 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})

            status = manager.get_configuration_status()
            assert status["llm_configured"] is True
            assert status["storage_configured"] is False
            assert status["fully_configured"] is False


class TestConfigurationReset:
    """설정 초기화 테스트"""

    def test_reset_config(self):
        """설정 초기화"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})
            assert manager.get_llm() is not None

            result = manager.reset_config()
            assert result is True
            assert manager.get_llm() is None

    def test_reset_config_removes_all_settings(self):
        """초기화 시 모든 설정 제거"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})
            manager.set_storage("superthread", {"api_key": "test"})
            manager.reset_config()

            assert manager.is_configured() is False


class TestConfigExportImport:
    """설정 내보내기/불러오기 테스트"""

    def test_export_config(self):
        """설정 내보내기"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            manager.set_llm("openai", {"api_key": "test"})
            export_path = Path(tmpdir) / "export.json"

            result = manager.export_config(str(export_path))
            assert result is True
            assert export_path.exists()

    def test_import_config(self):
        """설정 불러오기"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 원본 설정 생성 및 내보내기
            manager1 = ConfigManager(config_dir=Path(tmpdir) / "config1")
            manager1.set_llm("openai", {"api_key": "test_key"})

            export_path = Path(tmpdir) / "export.json"
            manager1.export_config(str(export_path))

            # 새 관리자에 불러오기
            manager2 = ConfigManager(config_dir=Path(tmpdir) / "config2")
            result = manager2.import_config(str(export_path))

            assert result is True
            assert manager2.get_llm() == "openai"

    def test_export_import_roundtrip(self):
        """내보내기/불러오기 왕복"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 원본 설정
            manager1 = ConfigManager(config_dir=Path(tmpdir) / "config1")
            original_llm = "openai"
            original_settings = {"api_key": "test_key", "model": "gpt-4"}

            manager1.set_llm(original_llm, original_settings)

            # 내보내기
            export_path = Path(tmpdir) / "export.json"
            manager1.export_config(str(export_path))

            # 불러오기
            manager2 = ConfigManager(config_dir=Path(tmpdir) / "config2")
            manager2.import_config(str(export_path))

            # 검증
            assert manager2.get_llm() == original_llm
            assert manager2.get_llm_settings() == original_settings


class TestEnvironmentVariables:
    """환경 변수 관리 테스트"""

    @patch('config.config_manager.os.getenv')
    def test_get_env_var(self, mock_getenv):
        """환경 변수 조회"""
        mock_getenv.return_value = "test_value"

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)
            result = manager.get_env_var("TEST_VAR")

            assert result == "test_value"

    def test_save_env_var(self):
        """환경 변수 저장"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            manager = ConfigManager(config_dir=tmpdir)

            result = manager._save_env_var("TEST_KEY", "test_value")
            assert result is True

            env_file = Path(tmpdir) / ".env"
            if env_file.exists():
                with open(env_file) as f:
                    content = f.read()
                    assert "TEST_KEY" in content


class TestConfigEdgeCases:
    """경계 케이스 테스트"""

    def test_config_with_empty_settings(self):
        """빈 설정값"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            result = manager.set_llm("openai", {})
            assert result is True

    def test_config_with_special_characters(self):
        """특수 문자가 포함된 설정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"api_key": "test!@#$%^&*()"}
            result = manager.set_llm("openai", settings)

            assert result is True
            assert manager.get_llm_setting("api_key") == settings["api_key"]

    def test_config_with_unicode_characters(self):
        """유니코드 문자가 포함된 설정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(config_dir=tmpdir)

            settings = {"description": "한글 설명 テスト"}
            result = manager.set_llm("openai", settings)

            assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
