"""
저장소 (Storage) 설정 정의
SQLite, Firebase, Notion, MongoDB 등의 저장소별 설정
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class StorageConfig:
    """저장소 설정 정보"""
    name: str  # 저장소 이름
    display_name: str  # 표시 이름
    type: str  # 저장소 타입
    description: str  # 설명
    free_tier: bool  # 무료 티어 제공 여부
    setup_url: str  # 설정 방법 URL
    required_fields: List[str]  # 필수 설정 항목
    optional_fields: List[str] = field(default_factory=list)  # 선택 설정 항목
    features: List[str] = field(default_factory=list)  # 주요 기능
    storage_limit: str = ""  # 저장소 용량 제한
    setup_steps: List[str] = field(default_factory=list)  # 설정 단계
    auto_setup: bool = False  # 자동 설정 가능 여부
    env_vars: Dict[str, str] = field(default_factory=dict)  # 환경 변수


# ============================================================================
# 저장소 설정 정의
# ============================================================================

STORAGE_CONFIGS: Dict[str, StorageConfig] = {
    "sqlite": StorageConfig(
        name="sqlite",
        display_name="💾 SQLite (로컬 저장소)",
        type="sqlite",
        description="로컬 파일 기반 데이터베이스. 가장 빠르고 간단함",
        free_tier=True,
        setup_url="https://www.sqlite.org/",
        required_fields=[],
        optional_fields=["db_path"],
        features=[
            "⚡ 매우 빠른 속도",
            "🆓 완전히 무료",
            "📂 로컬 파일 기반",
            "🔒 완전한 데이터 소유",
            "❌ 인터넷 불필요",
            "🔄 다기기 동기화 불가",
        ],
        storage_limit="무제한",
        setup_steps=[
            "1. Python 가상 환경 준비",
            "2. 프로젝트 폴더 설정",
            "3. 데이터베이스 자동 생성",
        ],
        auto_setup=True,
        env_vars={
            "STORAGE_TYPE": "sqlite",
            "SQLITE_DB_PATH": "memory_hub.db"
        }
    ),

    "firebase": StorageConfig(
        name="firebase",
        display_name="🔥 Firebase (Google 클라우드)",
        type="firebase",
        description="Google의 클라우드 데이터베이스. 실시간 동기화 지원",
        free_tier=True,
        setup_url="https://firebase.google.com/",
        required_fields=["credentials_path"],
        optional_fields=[],
        features=[
            "☁️ 클라우드 저장",
            "🔄 실시간 동기화",
            "🆓 무료 1GB",
            "🔐 Google 보안",
            "📱 모바일 지원",
            "⚙️ 자동 백업",
        ],
        storage_limit="1GB (무료), 초과시 유료",
        setup_steps=[
            "1. Google 계정 준비",
            "2. Firebase 프로젝트 생성",
            "3. Firestore 데이터베이스 생성",
            "4. 서비스 계정 키 다운로드",
            "5. credentials.json 파일 저장",
        ],
        auto_setup=False,
        env_vars={
            "STORAGE_TYPE": "firebase",
            "FIREBASE_CREDENTIALS": "api_server_v2/credentials.json"
        }
    ),

    "notion": StorageConfig(
        name="notion",
        display_name="📝 Notion (팀 협업)",
        type="notion",
        description="Notion 데이터베이스. 팀 협업과 UI가 우수함",
        free_tier=True,
        setup_url="https://www.notion.so/",
        required_fields=["api_key", "database_id"],
        optional_fields=[],
        features=[
            "👥 팀 협업",
            "🎨 아름다운 UI",
            "🆓 무료 플랜",
            "📊 강력한 데이터베이스",
            "🔗 다양한 연동",
            "✏️ 리치 텍스트",
        ],
        storage_limit="무제한",
        setup_steps=[
            "1. Notion 계정 준비",
            "2. Notion 데이터베이스 생성",
            "3. Notion 통합 생성",
            "4. API 키 발급",
            "5. 데이터베이스 ID 복사",
        ],
        auto_setup=False,
        env_vars={
            "STORAGE_TYPE": "notion",
            "NOTION_API_KEY": "your_api_key",
            "NOTION_DATABASE_ID": "your_database_id"
        }
    ),

    "mongodb": StorageConfig(
        name="mongodb",
        display_name="🍃 MongoDB (NoSQL 클라우드)",
        type="mongodb",
        description="MongoDB Atlas. 클라우드 NoSQL 데이터베이스",
        free_tier=True,
        setup_url="https://www.mongodb.com/cloud/atlas",
        required_fields=["connection_string"],
        optional_fields=["database_name"],
        features=[
            "☁️ 클라우드 호스팅",
            "📈 우수한 확장성",
            "🆓 512MB 무료",
            "🔄 실시간 동기화",
            "🔐 보안",
            "📊 유연한 스키마",
        ],
        storage_limit="512MB (무료), 초과시 유료",
        setup_steps=[
            "1. MongoDB 계정 생성",
            "2. Atlas 클러스터 생성",
            "3. 데이터베이스 사용자 생성",
            "4. IP 화이트리스트 추가",
            "5. 연결 문자열 복사",
        ],
        auto_setup=False,
        env_vars={
            "STORAGE_TYPE": "mongodb",
            "MONGODB_CONNECTION_STRING": "mongodb+srv://...",
            "MONGODB_DATABASE_NAME": "memory_hub"
        }
    ),
}


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_storage_list() -> List[Dict[str, str]]:
    """저장소 목록 반환 (UI 표시용)"""
    return [
        {
            "id": storage_id,
            "name": config.display_name,
            "type": config.type,
            "free": "✅ 무료" if config.free_tier else "❌ 유료",
            "limit": config.storage_limit,
            "description": config.description,
        }
        for storage_id, config in STORAGE_CONFIGS.items()
    ]


def get_storage_config(storage_id: str) -> StorageConfig:
    """저장소 설정 조회"""
    if storage_id not in STORAGE_CONFIGS:
        raise ValueError(f"알 수 없는 저장소: {storage_id}")
    return STORAGE_CONFIGS[storage_id]


def get_required_fields(storage_id: str) -> List[str]:
    """저장소의 필수 설정 항목 반환"""
    config = get_storage_config(storage_id)
    return config.required_fields


def validate_storage_config(storage_id: str, config: Dict[str, str]) -> tuple[bool, str]:
    """저장소 설정 유효성 검사"""
    try:
        storage_config = get_storage_config(storage_id)

        # 필수 항목 확인
        missing_fields = [
            field for field in storage_config.required_fields
            if field not in config or not config[field]
        ]

        if missing_fields:
            return False, f"필수 항목 누락: {', '.join(missing_fields)}"

        return True, "✅ 유효한 설정입니다"

    except ValueError as e:
        return False, str(e)


def get_storage_info(storage_id: str) -> Dict[str, Any]:
    """저장소 상세 정보 반환"""
    config = get_storage_config(storage_id)
    return {
        "name": config.display_name,
        "type": config.type,
        "description": config.description,
        "required_fields": config.required_fields,
        "optional_fields": config.optional_fields,
        "features": config.features,
        "storage_limit": config.storage_limit,
        "setup_url": config.setup_url,
        "setup_steps": config.setup_steps,
        "free_tier": config.free_tier,
        "auto_setup": config.auto_setup,
    }


def get_setup_instructions(storage_id: str) -> str:
    """저장소 설정 지침 반환"""
    config = get_storage_config(storage_id)
    instructions = f"""
📋 {config.display_name} 설정 가이드

{config.description}

📊 사양:
  - 저장소 용량: {config.storage_limit}
  - 자동 설정: {'✅ 가능' if config.auto_setup else '❌ 수동 설정 필요'}

🔧 설정 단계:
"""
    for i, step in enumerate(config.setup_steps, 1):
        instructions += f"  {step}\n"

    instructions += f"\n🔗 설정 방법: {config.setup_url}"

    return instructions
