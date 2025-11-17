"""
설정 관리자 (Configuration Manager)
사용자의 LLM, 저장소, API 키 등을 관리합니다.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigManager:
    """설정 관리자"""

    def __init__(self, config_dir: str = "config"):
        """
        초기화

        Args:
            config_dir: 설정 파일 저장 디렉토리
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "user_config.json"
        self.env_file = Path(".env")
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"설정 로드 실패: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """기본 설정 생성"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "llm": {
                "selected": None,
                "settings": {}
            },
            "storage": {
                "selected": None,
                "settings": {}
            },
            "general": {
                "language": "ko",
                "theme": "light"
            }
        }

    def save_config(self) -> bool:
        """설정 파일 저장"""
        try:
            self.config_data["updated_at"] = datetime.now().isoformat()

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            return False

    # ========================================================================
    # LLM 설정
    # ========================================================================

    def set_llm(self, llm_id: str, settings: Dict[str, str]) -> bool:
        """LLM 설정"""
        try:
            self.config_data["llm"]["selected"] = llm_id
            self.config_data["llm"]["settings"] = settings

            # 환경 변수에도 저장
            self._save_env_var("LLM_TYPE", llm_id)
            for key, value in settings.items():
                env_key = f"LLM_{key.upper()}"
                self._save_env_var(env_key, value)

            return self.save_config()
        except Exception as e:
            print(f"LLM 설정 저장 실패: {e}")
            return False

    def get_llm(self) -> Optional[str]:
        """현재 선택된 LLM"""
        return self.config_data.get("llm", {}).get("selected")

    def get_llm_settings(self) -> Dict[str, str]:
        """LLM 설정값 조회"""
        return self.config_data.get("llm", {}).get("settings", {})

    def get_llm_setting(self, key: str) -> Optional[str]:
        """특정 LLM 설정값 조회"""
        return self.config_data.get("llm", {}).get("settings", {}).get(key)

    # ========================================================================
    # 저장소 설정
    # ========================================================================

    def set_storage(self, storage_id: str, settings: Dict[str, str]) -> bool:
        """저장소 설정"""
        try:
            self.config_data["storage"]["selected"] = storage_id
            self.config_data["storage"]["settings"] = settings

            # 환경 변수에도 저장
            self._save_env_var("STORAGE_TYPE", storage_id)
            for key, value in settings.items():
                env_key = f"STORAGE_{key.upper()}"
                self._save_env_var(env_key, value)

            return self.save_config()
        except Exception as e:
            print(f"저장소 설정 저장 실패: {e}")
            return False

    def get_storage(self) -> Optional[str]:
        """현재 선택된 저장소"""
        return self.config_data.get("storage", {}).get("selected")

    def get_storage_settings(self) -> Dict[str, str]:
        """저장소 설정값 조회"""
        return self.config_data.get("storage", {}).get("settings", {})

    def get_storage_setting(self, key: str) -> Optional[str]:
        """특정 저장소 설정값 조회"""
        return self.config_data.get("storage", {}).get("settings", {}).get(key)

    # ========================================================================
    # 환경 변수 관리
    # ========================================================================

    def _save_env_var(self, key: str, value: str) -> bool:
        """환경 변수를 .env 파일에 저장"""
        try:
            # 기존 .env 파일 읽기
            env_vars = {}
            if self.env_file.exists():
                with open(self.env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip()

            # 새 값 추가/업데이트
            env_vars[key] = value

            # .env 파일 저장
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.write("# Memory Hub 설정 파일\n")
                f.write("# 이 파일은 자동으로 생성되었습니다\n\n")
                for k, v in env_vars.items():
                    # 값에 공백이 있으면 따옴표로 감싸기
                    if " " in v:
                        f.write(f'{k}="{v}"\n')
                    else:
                        f.write(f'{k}={v}\n')

            return True
        except Exception as e:
            print(f"환경 변수 저장 실패: {e}")
            return False

    def get_env_var(self, key: str) -> Optional[str]:
        """환경 변수 조회"""
        return os.getenv(key)

    # ========================================================================
    # 전체 설정
    # ========================================================================

    def get_full_config(self) -> Dict[str, Any]:
        """전체 설정 조회"""
        return self.config_data

    def reset_config(self) -> bool:
        """설정 초기화"""
        try:
            self.config_data = self._create_default_config()
            return self.save_config()
        except Exception as e:
            print(f"설정 초기화 실패: {e}")
            return False

    def export_config(self, filepath: str) -> bool:
        """설정을 파일로 내보내기 (백업용)"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 내보내기 실패: {e}")
            return False

    def import_config(self, filepath: str) -> bool:
        """설정을 파일에서 불러오기"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
            return self.save_config()
        except Exception as e:
            print(f"설정 가져오기 실패: {e}")
            return False

    # ========================================================================
    # 설정 유효성 검사
    # ========================================================================

    def is_configured(self) -> bool:
        """설정이 완료되었는지 확인"""
        llm_selected = self.get_llm() is not None
        storage_selected = self.get_storage() is not None
        return llm_selected and storage_selected

    def get_configuration_status(self) -> Dict[str, bool]:
        """설정 상태 조회"""
        return {
            "llm_configured": self.get_llm() is not None,
            "storage_configured": self.get_storage() is not None,
            "fully_configured": self.is_configured(),
        }


# 싱글톤 인스턴스
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """설정 관리자 싱글톤 인스턴스"""
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager()

    return _config_manager
