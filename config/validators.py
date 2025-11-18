"""
입력 검증 모듈
API 키, URL, 이메일 등의 형식 검증
"""

import re
import os
from typing import Tuple


class Validators:
    """입력 검증 클래스"""

    # ============================================================================
    # API 키 검증
    # ============================================================================

    @staticmethod
    def validate_openai_key(api_key: str) -> Tuple[bool, str]:
        """
        OpenAI API 키 검증
        형식: sk-로 시작하는 48자 이상
        """
        if not api_key:
            return False, "API 키를 입력하세요"

        if not api_key.startswith("sk-"):
            return False, "OpenAI API 키는 'sk-'로 시작해야 합니다"

        if len(api_key) < 48:
            return False, f"API 키가 너무 짧습니다 (최소 48자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 OpenAI API 키"

    @staticmethod
    def validate_anthropic_key(api_key: str) -> Tuple[bool, str]:
        """
        Anthropic (Claude) API 키 검증
        형식: sk-ant-로 시작
        """
        if not api_key:
            return False, "API 키를 입력하세요"

        if not api_key.startswith("sk-ant-"):
            return False, "Claude API 키는 'sk-ant-'로 시작해야 합니다"

        if len(api_key) < 40:
            return False, f"API 키가 너무 짧습니다 (최소 40자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 Claude API 키"

    @staticmethod
    def validate_google_key(api_key: str) -> Tuple[bool, str]:
        """
        Google (Gemini) API 키 검증
        형식: AIza로 시작
        """
        if not api_key:
            return False, "API 키를 입력하세요"

        if not api_key.startswith("AIza"):
            return False, "Google API 키는 'AIza'로 시작해야 합니다"

        if len(api_key) < 30:
            return False, f"API 키가 너무 짧습니다 (최소 30자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 Google API 키"

    @staticmethod
    def validate_huggingface_key(api_key: str) -> Tuple[bool, str]:
        """
        Hugging Face API 키 검증
        형식: hf_로 시작
        """
        if not api_key:
            return False, "API 키를 입력하세요"

        if not api_key.startswith("hf_"):
            return False, "Hugging Face API 키는 'hf_'로 시작해야 합니다"

        if len(api_key) < 20:
            return False, f"API 키가 너무 짧습니다 (최소 20자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 Hugging Face API 키"

    # ============================================================================
    # Firebase 검증
    # ============================================================================

    @staticmethod
    def validate_firebase_credentials(credentials_path: str) -> Tuple[bool, str]:
        """
        Firebase 자격증명 파일 검증
        """
        if not credentials_path:
            return False, "Firebase 자격증명 파일 경로를 입력하세요"

        if not os.path.exists(credentials_path):
            return False, f"파일을 찾을 수 없습니다: {credentials_path}"

        if not credentials_path.endswith(".json"):
            return False, "Firebase 자격증명은 .json 파일이어야 합니다"

        try:
            import json
            with open(credentials_path, 'r') as f:
                data = json.load(f)

            required_fields = ["type", "project_id", "private_key_id", "private_key"]
            missing = [field for field in required_fields if field not in data]

            if missing:
                return False, f"필수 필드 누락: {', '.join(missing)}"

            return True, "✅ 유효한 Firebase 자격증명"
        except json.JSONDecodeError:
            return False, "JSON 파일 형식이 잘못되었습니다"
        except Exception as e:
            return False, f"파일 읽기 오류: {str(e)}"

    # ============================================================================
    # Notion 검증
    # ============================================================================

    @staticmethod
    def validate_notion_api_key(api_key: str) -> Tuple[bool, str]:
        """
        Notion API 키 검증
        형식: secret_로 시작
        """
        if not api_key:
            return False, "Notion API 키를 입력하세요"

        if not api_key.startswith("secret_"):
            return False, "Notion API 키는 'secret_'로 시작해야 합니다"

        if len(api_key) < 40:
            return False, f"API 키가 너무 짧습니다 (최소 40자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 Notion API 키"

    @staticmethod
    def validate_notion_database_id(database_id: str) -> Tuple[bool, str]:
        """
        Notion 데이터베이스 ID 검증
        형식: 32개의 16진수 (하이픈 포함)
        """
        if not database_id:
            return False, "Notion 데이터베이스 ID를 입력하세요"

        # 하이픈 제거
        clean_id = database_id.replace("-", "")

        if len(clean_id) != 32:
            return False, f"데이터베이스 ID가 잘못되었습니다 (32자, 현재 {len(clean_id)}자)"

        if not re.match(r"^[0-9a-f]{32}$", clean_id):
            return False, "데이터베이스 ID는 16진수여야 합니다"

        return True, "✅ 유효한 Notion 데이터베이스 ID"

    # ============================================================================
    # MongoDB 검증
    # ============================================================================

    @staticmethod
    def validate_mongodb_connection_string(connection_string: str) -> Tuple[bool, str]:
        """
        MongoDB 연결 문자열 검증
        형식: mongodb+srv:// 또는 mongodb://
        """
        if not connection_string:
            return False, "MongoDB 연결 문자열을 입력하세요"

        if not (connection_string.startswith("mongodb+srv://") or connection_string.startswith("mongodb://")):
            return False, "MongoDB 연결 문자열은 'mongodb+srv://' 또는 'mongodb://'로 시작해야 합니다"

        if "@" not in connection_string:
            return False, "MongoDB 연결 문자열에 사용자명과 비밀번호가 필요합니다"

        if len(connection_string) < 30:
            return False, "MongoDB 연결 문자열이 너무 짧습니다"

        return True, "✅ 유효한 MongoDB 연결 문자열"

    # ============================================================================
    # Superthread 검증
    # ============================================================================

    @staticmethod
    def validate_superthread_api_key(api_key: str) -> Tuple[bool, str]:
        """
        Superthread API 키 검증
        """
        if not api_key:
            return False, "Superthread API 키를 입력하세요"

        if len(api_key) < 20:
            return False, f"API 키가 너무 짧습니다 (최소 20자, 현재 {len(api_key)}자)"

        return True, "✅ 유효한 Superthread API 키"

    @staticmethod
    def validate_superthread_workspace_id(workspace_id: str) -> Tuple[bool, str]:
        """
        Superthread 워크스페이스 ID 검증
        """
        if not workspace_id:
            return False, "Superthread 워크스페이스 ID를 입력하세요"

        if len(workspace_id) < 5:
            return False, f"워크스페이스 ID가 너무 짧습니다"

        return True, "✅ 유효한 Superthread 워크스페이스 ID"

    # ============================================================================
    # 공통 검증
    # ============================================================================

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        URL 형식 검증
        """
        if not url:
            return False, "URL을 입력하세요"

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$", re.IGNORECASE)

        if not url_pattern.match(url):
            return False, "유효하지 않은 URL 형식입니다"

        return True, "✅ 유효한 URL"

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        이메일 형식 검증
        """
        if not email:
            return False, "이메일을 입력하세요"

        email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        if not email_pattern.match(email):
            return False, "유효하지 않은 이메일 형식입니다"

        return True, "✅ 유효한 이메일"

    @staticmethod
    def validate_field_required(value: str, field_name: str) -> Tuple[bool, str]:
        """
        필수 필드 검증
        """
        if not value or not value.strip():
            return False, f"{field_name}은(는) 필수 입력 사항입니다"

        return True, f"✅ {field_name} 입력됨"

    @staticmethod
    def validate_field_length(value: str, min_length: int = 0, max_length: int = None) -> Tuple[bool, str]:
        """
        필드 길이 검증
        """
        if len(value) < min_length:
            return False, f"최소 {min_length}자 이상이어야 합니다 (현재 {len(value)}자)"

        if max_length and len(value) > max_length:
            return False, f"최대 {max_length}자 이하여야 합니다 (현재 {len(value)}자)"

        return True, "✅ 길이 유효"

    # ============================================================================
    # 저장소별 전체 검증
    # ============================================================================

    @staticmethod
    def validate_llm_settings(llm_type: str, settings: dict) -> Tuple[bool, str]:
        """
        LLM 설정 전체 검증
        """
        if llm_type == "openai":
            api_key = settings.get("api_key", "")
            return Validators.validate_openai_key(api_key)

        elif llm_type == "anthropic":
            api_key = settings.get("api_key", "")
            return Validators.validate_anthropic_key(api_key)

        elif llm_type == "google":
            api_key = settings.get("api_key", "")
            return Validators.validate_google_key(api_key)

        elif llm_type == "huggingface":
            api_key = settings.get("api_key", "")
            return Validators.validate_huggingface_key(api_key)

        elif llm_type == "local":
            endpoint = settings.get("endpoint", "")
            valid, msg = Validators.validate_url(endpoint)
            if not valid:
                return False, "Local Ollama 엔드포인트 URL이 유효하지 않습니다"
            return True, "✅ 유효한 Local Ollama 설정"

        return False, f"알 수 없는 LLM 타입: {llm_type}"

    @staticmethod
    def validate_storage_settings(storage_type: str, settings: dict) -> Tuple[bool, str]:
        """
        저장소 설정 전체 검증
        """
        if storage_type == "sqlite":
            db_path = settings.get("db_path", "memory_hub.db")
            return True, f"✅ SQLite 설정 유효 ({db_path})"

        elif storage_type == "firebase":
            credentials_path = settings.get("credentials_path", "")
            return Validators.validate_firebase_credentials(credentials_path)

        elif storage_type == "notion":
            api_key_valid, msg1 = Validators.validate_notion_api_key(settings.get("api_key", ""))
            if not api_key_valid:
                return False, msg1

            db_id_valid, msg2 = Validators.validate_notion_database_id(settings.get("database_id", ""))
            if not db_id_valid:
                return False, msg2

            return True, "✅ Notion 설정 유효"

        elif storage_type == "mongodb":
            conn_str = settings.get("connection_string", "")
            return Validators.validate_mongodb_connection_string(conn_str)

        elif storage_type == "superthread":
            api_key_valid, msg1 = Validators.validate_superthread_api_key(settings.get("api_key", ""))
            if not api_key_valid:
                return False, msg1

            ws_id_valid, msg2 = Validators.validate_superthread_workspace_id(settings.get("workspace_id", ""))
            if not ws_id_valid:
                return False, msg2

            return True, "✅ Superthread 설정 유효"

        return False, f"알 수 없는 저장소 타입: {storage_type}"


# 편의 함수
def validate_api_key(api_key: str, llm_type: str = None) -> bool:
    """API 키 검증 편의 함수"""
    if llm_type == "openai":
        valid, _ = Validators.validate_openai_key(api_key)
        return valid
    elif llm_type == "anthropic":
        valid, _ = Validators.validate_anthropic_key(api_key)
        return valid
    elif llm_type == "google":
        valid, _ = Validators.validate_google_key(api_key)
        return valid
    return bool(api_key and len(api_key) >= 20)


if __name__ == "__main__":
    # 테스트
    print("Validators 모듈 로드 완료")
