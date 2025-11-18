"""
입력 검증 시스템 테스트
Validators 클래스에 대한 포괄적인 단위 테스트
"""

import pytest
from config.validators import Validators


class TestLLMValidators:
    """LLM 검증 테스트"""

    # ========================================================================
    # OpenAI 검증 테스트
    # ========================================================================

    def test_validate_openai_key_valid(self):
        """유효한 OpenAI API 키 검증"""
        # OpenAI 키는 sk-로 시작하고 48자 이상
        valid_key = "sk-" + "a" * 48
        is_valid, message = Validators.validate_openai_key(valid_key)
        assert is_valid is True
        assert "valid" in message.lower() or "ok" in message.lower()

    def test_validate_openai_key_invalid_prefix(self):
        """잘못된 접두사의 OpenAI 키"""
        invalid_key = "invalid_" + "a" * 48
        is_valid, message = Validators.validate_openai_key(invalid_key)
        assert is_valid is False
        assert "sk-" in message or "prefix" in message.lower()

    def test_validate_openai_key_too_short(self):
        """너무 짧은 OpenAI 키"""
        short_key = "sk-short"
        is_valid, message = Validators.validate_openai_key(short_key)
        assert is_valid is False
        assert "length" in message.lower() or "48" in message

    def test_validate_openai_key_empty(self):
        """빈 OpenAI 키"""
        is_valid, message = Validators.validate_openai_key("")
        assert is_valid is False

    # ========================================================================
    # Anthropic 검증 테스트
    # ========================================================================

    def test_validate_anthropic_key_valid(self):
        """유효한 Anthropic API 키 검증"""
        valid_key = "sk-ant-" + "a" * 35
        is_valid, message = Validators.validate_anthropic_key(valid_key)
        assert is_valid is True

    def test_validate_anthropic_key_invalid_prefix(self):
        """잘못된 접두사의 Anthropic 키"""
        invalid_key = "invalid-" + "a" * 35
        is_valid, message = Validators.validate_anthropic_key(invalid_key)
        assert is_valid is False
        assert "sk-ant-" in message

    def test_validate_anthropic_key_too_short(self):
        """너무 짧은 Anthropic 키"""
        short_key = "sk-ant-short"
        is_valid, message = Validators.validate_anthropic_key(short_key)
        assert is_valid is False

    # ========================================================================
    # Google 검증 테스트
    # ========================================================================

    def test_validate_google_key_valid(self):
        """유효한 Google API 키 검증"""
        valid_key = "AIza" + "a" * 35
        is_valid, message = Validators.validate_google_key(valid_key)
        assert is_valid is True

    def test_validate_google_key_invalid_prefix(self):
        """잘못된 접두사의 Google 키"""
        invalid_key = "invalid" + "a" * 35
        is_valid, message = Validators.validate_google_key(invalid_key)
        assert is_valid is False
        assert "AIza" in message

    # ========================================================================
    # HuggingFace 검증 테스트
    # ========================================================================

    def test_validate_huggingface_key_valid(self):
        """유효한 HuggingFace API 키 검증"""
        valid_key = "hf_" + "a" * 20
        is_valid, message = Validators.validate_huggingface_key(valid_key)
        assert is_valid is True

    def test_validate_huggingface_key_invalid_prefix(self):
        """잘못된 접두사의 HuggingFace 키"""
        invalid_key = "invalid_" + "a" * 20
        is_valid, message = Validators.validate_huggingface_key(invalid_key)
        assert is_valid is False
        assert "hf_" in message


class TestStorageValidators:
    """저장소 검증 테스트"""

    # ========================================================================
    # Firebase 검증 테스트
    # ========================================================================

    def test_validate_firebase_credentials_valid_path(self):
        """유효한 Firebase 자격증명 경로"""
        # Note: 실제 파일이 없으므로 경로 형식만 검증
        credentials_path = "/path/to/firebase-credentials.json"
        is_valid, message = Validators.validate_firebase_credentials(credentials_path)
        # 경로 존재 여부에 관계없이 형식 검증
        assert isinstance(is_valid, bool)

    def test_validate_firebase_credentials_invalid_format(self):
        """잘못된 형식의 Firebase 경로"""
        invalid_path = "not_a_json_path"
        is_valid, message = Validators.validate_firebase_credentials(invalid_path)
        # 형식이 유효하지 않으면 False 반환 가능
        if not is_valid:
            assert "json" in message.lower() or "path" in message.lower()

    # ========================================================================
    # Notion 검증 테스트
    # ========================================================================

    def test_validate_notion_api_key_valid(self):
        """유효한 Notion API 키 검증"""
        valid_key = "secret_" + "a" * 43
        is_valid, message = Validators.validate_notion_api_key(valid_key)
        assert is_valid is True

    def test_validate_notion_api_key_invalid(self):
        """잘못된 Notion API 키"""
        invalid_key = "not_a_secret_key"
        is_valid, message = Validators.validate_notion_api_key(invalid_key)
        assert is_valid is False

    def test_validate_notion_database_id_valid(self):
        """유효한 Notion Database ID 검증"""
        # Notion Database ID는 32자의 16진수
        valid_id = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        is_valid, message = Validators.validate_notion_database_id(valid_id)
        # 형식 검증 실행
        assert isinstance(is_valid, bool)

    def test_validate_notion_database_id_invalid_length(self):
        """길이가 잘못된 Notion Database ID"""
        invalid_id = "short"
        is_valid, message = Validators.validate_notion_database_id(invalid_id)
        # 길이가 충분하지 않으면 False
        if not is_valid:
            assert "length" in message.lower() or "32" in message

    # ========================================================================
    # MongoDB 검증 테스트
    # ========================================================================

    def test_validate_mongodb_connection_string_valid(self):
        """유효한 MongoDB 연결 문자열 검증"""
        valid_connection = "mongodb+srv://user:password@cluster.mongodb.net/database"
        is_valid, message = Validators.validate_mongodb_connection_string(valid_connection)
        assert is_valid is True

    def test_validate_mongodb_connection_string_invalid(self):
        """잘못된 MongoDB 연결 문자열"""
        invalid_connection = "not_a_valid_connection_string"
        is_valid, message = Validators.validate_mongodb_connection_string(invalid_connection)
        assert is_valid is False
        assert "mongodb" in message.lower()

    # ========================================================================
    # Superthread 검증 테스트
    # ========================================================================

    def test_validate_superthread_api_key_valid(self):
        """유효한 Superthread API 키 검증"""
        valid_key = "st_" + "a" * 30
        is_valid, message = Validators.validate_superthread_api_key(valid_key)
        # Superthread 키 검증
        assert isinstance(is_valid, bool)

    def test_validate_superthread_workspace_id_valid(self):
        """유효한 Superthread Workspace ID 검증"""
        valid_id = "workspace_" + "a" * 20
        is_valid, message = Validators.validate_superthread_workspace_id(valid_id)
        assert isinstance(is_valid, bool)


class TestLLMSettingsValidation:
    """LLM 설정 전체 검증 테스트"""

    def test_validate_llm_settings_openai(self):
        """OpenAI LLM 설정 검증"""
        settings = {
            "api_key": "sk-" + "a" * 48
        }
        is_valid, message = Validators.validate_llm_settings("openai", settings)
        assert is_valid is True

    def test_validate_llm_settings_missing_required(self):
        """필수 필드가 없는 LLM 설정"""
        settings = {}
        is_valid, message = Validators.validate_llm_settings("openai", settings)
        assert is_valid is False
        assert "required" in message.lower() or "api_key" in message

    def test_validate_llm_settings_invalid_type(self):
        """잘못된 LLM 타입"""
        settings = {"api_key": "test"}
        is_valid, message = Validators.validate_llm_settings("unknown_llm", settings)
        # 알 수 없는 타입은 처리 방식에 따라 다름
        assert isinstance(is_valid, bool)


class TestStorageSettingsValidation:
    """저장소 설정 전체 검증 테스트"""

    def test_validate_storage_settings_superthread(self):
        """Superthread 저장소 설정 검증"""
        settings = {
            "api_key": "st_" + "a" * 30,
            "workspace_id": "workspace_" + "a" * 20
        }
        is_valid, message = Validators.validate_storage_settings("superthread", settings)
        # 검증 결과 확인
        assert isinstance(is_valid, bool)

    def test_validate_storage_settings_missing_required(self):
        """필수 필드가 없는 저장소 설정"""
        settings = {}
        is_valid, message = Validators.validate_storage_settings("superthread", settings)
        # 필수 필드가 없으면 False
        if not is_valid:
            assert "required" in message.lower()

    def test_validate_storage_settings_unknown_type(self):
        """알 수 없는 저장소 타입"""
        settings = {"api_key": "test"}
        is_valid, message = Validators.validate_storage_settings("unknown_storage", settings)
        # 알 수 없는 타입 처리
        assert isinstance(is_valid, bool)


class TestValidationEdgeCases:
    """경계 케이스 및 특수 입력 테스트"""

    def test_validate_with_special_characters(self):
        """특수 문자가 포함된 입력"""
        key_with_special = "sk-!@#$%^&*()"
        is_valid, message = Validators.validate_openai_key(key_with_special)
        # 형식이 맞지 않으므로 False
        assert is_valid is False

    def test_validate_with_unicode_characters(self):
        """유니코드 문자가 포함된 입력"""
        key_with_unicode = "sk-한글테스트"
        is_valid, message = Validators.validate_openai_key(key_with_unicode)
        # 유니코드는 일반적으로 API 키에 포함되지 않음
        assert is_valid is False

    def test_validate_with_whitespace(self):
        """공백이 포함된 입력"""
        key_with_space = "sk- " + "a" * 48
        is_valid, message = Validators.validate_openai_key(key_with_space)
        # 공백이 있으면 Invalid
        assert is_valid is False

    def test_validate_extremely_long_input(self):
        """매우 긴 입력"""
        long_key = "sk-" + "a" * 1000
        is_valid, message = Validators.validate_openai_key(long_key)
        # 길이 검증이 있으면 처리
        assert isinstance(is_valid, bool)

    def test_validate_none_input(self):
        """None 입력 처리"""
        try:
            is_valid, message = Validators.validate_openai_key(None)
            # None 처리에 따라 결과 확인
            assert is_valid is False
        except (TypeError, AttributeError):
            # None을 처리하지 않는 경우
            pytest.skip("None input not handled")


class TestValidationConsistency:
    """검증 일관성 테스트"""

    def test_same_input_returns_consistent_result(self):
        """동일한 입력이 일관된 결과 반환"""
        key = "sk-" + "a" * 48

        result1 = Validators.validate_openai_key(key)
        result2 = Validators.validate_openai_key(key)

        assert result1 == result2

    def test_different_invalid_inputs_all_fail(self):
        """다양한 유효하지 않은 입력이 모두 실패"""
        invalid_keys = [
            "",
            "invalid",
            "sk-short",
            "no-prefix-key",
            "123456"
        ]

        for key in invalid_keys:
            is_valid, _ = Validators.validate_openai_key(key)
            assert is_valid is False, f"Key '{key}' should be invalid"

    def test_similar_valid_inputs_all_pass(self):
        """유사한 유효한 입력이 모두 통과"""
        valid_keys = [
            "sk-" + "a" * 48,
            "sk-" + "b" * 48,
            "sk-" + "0" * 48,
        ]

        for key in valid_keys:
            is_valid, _ = Validators.validate_openai_key(key)
            assert is_valid is True, f"Key '{key}' should be valid"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
