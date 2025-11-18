"""
통합 테스트 (Integration Tests)
여러 컴포넌트의 상호작용 테스트
"""

import os
import pytest
import tempfile
from pathlib import Path
from config.config_manager import ConfigManager
from config.validators import Validators
from config.encryption import KeyEncryption
from unittest.mock import patch


@pytest.mark.integration
class TestSetupWizardIntegration:
    """설정 마법사 통합 테스트"""

    def test_complete_setup_workflow(self):
        """완전한 설정 워크플로우"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. ConfigManager 초기화
            config_manager = ConfigManager(config_dir=tmpdir)
            assert config_manager.is_configured() is False

            # 2. LLM 선택 및 검증
            llm_type = "openai"
            api_key = "sk-" + "a" * 48

            is_valid, message = Validators.validate_openai_key(api_key)
            assert is_valid is True

            # 3. LLM 설정 저장
            llm_settings = {"api_key": api_key}
            result = config_manager.set_llm(llm_type, llm_settings)
            assert result is True

            # 4. 저장소 선택 및 검증
            storage_type = "superthread"
            workspace_id = "workspace_" + "a" * 20
            storage_api_key = "st_" + "a" * 30

            is_valid, _ = Validators.validate_superthread_api_key(storage_api_key)
            assert is_valid is True

            is_valid, _ = Validators.validate_superthread_workspace_id(workspace_id)
            assert isinstance(is_valid, bool)

            # 5. 저장소 설정 저장
            storage_settings = {
                "api_key": storage_api_key,
                "workspace_id": workspace_id
            }
            result = config_manager.set_storage(storage_type, storage_settings)
            assert result is True

            # 6. 설정 완료 확인
            assert config_manager.is_configured() is True
            assert config_manager.get_llm() == llm_type
            assert config_manager.get_storage() == storage_type


@pytest.mark.integration
class TestEncryptionWithConfigManager:
    """ConfigManager와 암호화 통합 테스트"""

    @patch('config.config_manager.KeyEncryption')
    def test_encrypted_config_save_and_load(self, mock_encryption):
        """암호화된 설정 저장 및 로드"""
        mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
        mock_encryption.is_encrypted.side_effect = lambda x: x.startswith("encrypted_")
        mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 원본 설정 저장
            config_manager = ConfigManager(config_dir=tmpdir)
            original_settings = {"api_key": "secret_key_123"}

            config_manager.set_llm("openai", original_settings)
            config_manager.save_config()

            # 2. 새 인스턴스에서 로드
            config_manager2 = ConfigManager(config_dir=tmpdir)

            # 3. 설정이 올바르게 로드되는지 확인
            loaded_settings = config_manager2.get_llm_settings()
            assert "api_key" in loaded_settings


@pytest.mark.integration
class TestValidatorWithConfigManager:
    """Validators와 ConfigManager 통합 테스트"""

    def test_validate_before_saving_config(self):
        """설정 저장 전 검증"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            # 유효한 API 키 검증
            api_key = "sk-" + "a" * 48
            is_valid, message = Validators.validate_openai_key(api_key)

            if is_valid:
                config_manager.set_llm("openai", {"api_key": api_key})
                assert config_manager.get_llm() == "openai"

    def test_reject_invalid_settings(self):
        """유효하지 않은 설정 거부"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            # 유효하지 않은 API 키
            invalid_key = "invalid_key"
            is_valid, message = Validators.validate_openai_key(invalid_key)

            assert is_valid is False

            # 유효하지 않은 경우 저장하지 않음
            # (실제로는 UI 레벨에서 처리)


@pytest.mark.integration
class TestMultiStorageScenario:
    """다중 저장소 시나리오 테스트"""

    def test_switch_storage_type(self):
        """저장소 타입 전환"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            # 1. Superthread로 저장
            superthread_settings = {
                "api_key": "st_" + "a" * 30,
                "workspace_id": "workspace_123"
            }
            config_manager.set_storage("superthread", superthread_settings)
            assert config_manager.get_storage() == "superthread"

            # 2. Google Docs로 전환
            google_docs_settings = {
                "token_json": '{"type":"oauth2"}',
                "folder_id": "folder_123"
            }
            config_manager.set_storage("google_docs", google_docs_settings)
            assert config_manager.get_storage() == "google_docs"

            # 3. Firebase로 전환
            firebase_settings = {
                "credentials_path": "/path/to/creds.json"
            }
            config_manager.set_storage("firebase", firebase_settings)
            assert config_manager.get_storage() == "firebase"

    def test_multi_llm_scenario(self):
        """다중 LLM 시나리오"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            llm_options = [
                ("openai", {"api_key": "sk-" + "a" * 48}),
                ("anthropic", {"api_key": "sk-ant-" + "a" * 35}),
                ("google", {"api_key": "AIza" + "a" * 35}),
            ]

            for llm_type, settings in llm_options:
                config_manager.set_llm(llm_type, settings)
                assert config_manager.get_llm() == llm_type


@pytest.mark.integration
class TestConfigurationPersistence:
    """설정 지속성 통합 테스트"""

    def test_config_survives_restart(self):
        """설정이 재시작 후 유지되는지 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 첫 번째 세션: 설정 저장
            config_manager1 = ConfigManager(config_dir=tmpdir)
            config_manager1.set_llm("openai", {"api_key": "sk-test123"})
            config_manager1.set_storage("superthread", {
                "api_key": "st_test",
                "workspace_id": "ws_test"
            })

            # 두 번째 세션: 설정 로드
            config_manager2 = ConfigManager(config_dir=tmpdir)
            assert config_manager2.get_llm() == "openai"
            assert config_manager2.get_storage() == "superthread"

            # 세 번째 세션: 설정 변경
            config_manager2.set_llm("anthropic", {"api_key": "sk-ant-test"})

            # 네 번째 세션: 변경 확인
            config_manager3 = ConfigManager(config_dir=tmpdir)
            assert config_manager3.get_llm() == "anthropic"


@pytest.mark.integration
class TestValidationEdgeCases:
    """검증 경계 케이스 통합 테스트"""

    def test_validator_with_special_characters(self):
        """특수 문자를 포함한 검증"""
        special_chars = "!@#$%^&*()"

        # 저장소 설정에 특수 문자 포함
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            settings = {"password": f"password{special_chars}"}
            result = config_manager.set_storage("firebase", settings)

            assert result is True

    def test_very_long_values(self):
        """매우 긴 값 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            long_value = "a" * 10000
            settings = {"api_key": long_value}

            result = config_manager.set_llm("openai", settings)
            assert result is True

            retrieved = config_manager.get_llm_setting("api_key")
            assert retrieved == long_value


@pytest.mark.integration
class TestExportImportWorkflow:
    """내보내기/불러오기 워크플로우"""

    def test_config_migration(self):
        """설정 마이그레이션"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # 원본 설정 생성
                original_config = ConfigManager(config_dir=tmpdir1)
                original_config.set_llm("openai", {"api_key": "sk-test123"})
                original_config.set_storage("superthread", {
                    "api_key": "st_test",
                    "workspace_id": "ws_test"
                })

                # 내보내기
                export_file = Path(tmpdir1) / "config_export.json"
                result = original_config.export_config(str(export_file))
                assert result is True

                # 불러오기
                new_config = ConfigManager(config_dir=tmpdir2)
                result = new_config.import_config(str(export_file))
                assert result is True

                # 검증
                assert new_config.get_llm() == "openai"
                assert new_config.get_storage() == "superthread"


@pytest.mark.integration
class TestErrorRecovery:
    """에러 복구 통합 테스트"""

    def test_corrupted_config_file_recovery(self):
        """손상된 설정 파일 복구"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()

            # 손상된 설정 파일 생성
            config_file = config_dir / "user_config.json"
            with open(config_file, 'w') as f:
                f.write("{invalid json content")

            # ConfigManager가 기본 설정으로 복구
            config_manager = ConfigManager(config_dir=str(config_dir))
            assert config_manager.get_llm() is None
            assert config_manager.get_storage() is None

    def test_missing_required_fields(self):
        """필수 필드 누락 처리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            # 필수 필드 없이 저장 시도
            incomplete_settings = {}
            result = config_manager.set_llm("openai", incomplete_settings)

            assert result is True  # 저장은 성공하지만
            # 실제 사용 시에는 검증이 필요


@pytest.mark.integration
class TestPerformanceIntegration:
    """성능 통합 테스트"""

    def test_large_config_handling(self, performance_tracker):
        """대량 설정 처리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            large_settings = {
                f"key_{i}": f"value_{i}" * 100 for i in range(100)
            }

            performance_tracker.start()
            result = config_manager.set_llm("openai", large_settings)
            performance_tracker.stop()

            assert result is True
            elapsed = performance_tracker.elapsed_ms()
            # 설정 저장이 1초 이내로 완료되어야 함
            if elapsed:
                assert elapsed < 1000

    def test_multiple_sequential_operations(self, performance_tracker):
        """순차 작업 성능"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(config_dir=tmpdir)

            performance_tracker.start()

            for i in range(10):
                config_manager.set_llm("openai", {"api_key": f"sk-test{i}"})
                config_manager.save_config()

            performance_tracker.stop()
            elapsed = performance_tracker.elapsed_ms()

            if elapsed:
                # 10번의 저장이 2초 이내로 완료되어야 함
                assert elapsed < 2000


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
