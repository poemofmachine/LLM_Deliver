"""
LLM (Large Language Model) 설정 정의
ChatGPT, Claude, Gemini 등의 LLM별 설정
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM 설정 정보"""
    name: str  # LLM 이름
    display_name: str  # 표시 이름
    provider: str  # 제공자 (OpenAI, Anthropic, Google 등)
    api_key_required: bool  # API 키 필요 여부
    api_endpoint: str  # API 엔드포인트
    description: str  # 설명
    free_tier: bool  # 무료 티어 제공 여부
    setup_url: str  # 설정 방법 URL
    required_fields: List[str]  # 필요한 설정 항목
    optional_fields: List[str] = field(default_factory=list)  # 선택 설정 항목
    features: List[str] = field(default_factory=list)  # 주요 기능
    pricing_info: str = ""  # 가격 정보


# ============================================================================
# LLM 설정 정의
# ============================================================================

LLM_CONFIGS: Dict[str, LLMConfig] = {
    "openai": LLMConfig(
        name="openai",
        display_name="🟢 ChatGPT (OpenAI)",
        provider="OpenAI",
        api_key_required=True,
        api_endpoint="https://api.openai.com/v1",
        description="OpenAI의 강력한 언어 모델. GPT-4, GPT-3.5 등 지원",
        free_tier=True,
        setup_url="https://platform.openai.com/api-keys",
        required_fields=["api_key"],
        optional_fields=["model", "temperature", "max_tokens"],
        features=[
            "🔥 매우 강력한 성능",
            "💬 자연스러운 대화",
            "📝 코드 생성 우수",
            "🌍 다국어 지원",
        ],
        pricing_info="무료 크레딧 $18 + 사용량 기준 유료"
    ),

    "anthropic": LLMConfig(
        name="anthropic",
        display_name="🔴 Claude (Anthropic)",
        provider="Anthropic",
        api_key_required=True,
        api_endpoint="https://api.anthropic.com",
        description="Anthropic의 Claude. 긴 문맥 처리에 우수",
        free_tier=True,
        setup_url="https://console.anthropic.com/",
        required_fields=["api_key"],
        optional_fields=["model", "temperature", "max_tokens"],
        features=[
            "📚 100K 토큰 컨텍스트",
            "✨ 안전한 AI",
            "🎯 정확한 답변",
            "🔒 프라이버시 중시",
        ],
        pricing_info="무료 베타 + 사용량 기준 유료"
    ),

    "google": LLMConfig(
        name="google",
        display_name="🔵 Gemini (Google)",
        provider="Google",
        api_key_required=True,
        api_endpoint="https://generativelanguage.googleapis.com",
        description="Google의 Gemini. 멀티모달 지원",
        free_tier=True,
        setup_url="https://ai.google.dev/",
        required_fields=["api_key"],
        optional_fields=["model", "temperature", "max_tokens"],
        features=[
            "🖼️ 멀티모달 (텍스트+이미지)",
            "🚀 빠른 응답",
            "🔄 Google 생태계 연동",
            "💰 저렴한 가격",
        ],
        pricing_info="무료 티어 제공 + 사용량 기준 유료"
    ),

    "huggingface": LLMConfig(
        name="huggingface",
        display_name="🤗 Hugging Face",
        provider="Hugging Face",
        api_key_required=True,
        api_endpoint="https://api-inference.huggingface.co",
        description="오픈소스 모델 호스팅 플랫폼",
        free_tier=True,
        setup_url="https://huggingface.co/",
        required_fields=["api_key", "model_id"],
        optional_fields=["temperature", "max_length"],
        features=[
            "🆓 무료 오픈소스 모델",
            "🔧 커스터마이징 가능",
            "🌐 다양한 모델",
            "📊 커뮤니티 지원",
        ],
        pricing_info="완전 무료"
    ),

    "local": LLMConfig(
        name="local",
        display_name="💻 로컬 모델 (Ollama)",
        provider="Local",
        api_key_required=False,
        api_endpoint="http://localhost:11434",
        description="로컬에서 실행하는 오픈소스 모델. Ollama 필요",
        free_tier=True,
        setup_url="https://ollama.ai",
        required_fields=["model_name"],
        optional_fields=["temperature", "num_predict"],
        features=[
            "🔒 완전 프라이빗",
            "🚀 빠른 로컬 실행",
            "🆓 무료",
            "❌ 인터넷 불필요",
        ],
        pricing_info="완전 무료 (로컬 실행)"
    ),
}


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_llm_list() -> List[Dict[str, str]]:
    """LLM 목록 반환 (UI 표시용)"""
    return [
        {
            "id": llm_id,
            "name": config.display_name,
            "provider": config.provider,
            "free": "✅ 무료 지원" if config.free_tier else "❌ 유료만",
            "description": config.description,
        }
        for llm_id, config in LLM_CONFIGS.items()
    ]


def get_llm_config(llm_id: str) -> LLMConfig:
    """LLM 설정 조회"""
    if llm_id not in LLM_CONFIGS:
        raise ValueError(f"알 수 없는 LLM: {llm_id}")
    return LLM_CONFIGS[llm_id]


def get_required_fields(llm_id: str) -> List[str]:
    """LLM의 필수 설정 항목 반환"""
    config = get_llm_config(llm_id)
    return config.required_fields


def validate_llm_config(llm_id: str, config: Dict[str, str]) -> tuple[bool, str]:
    """LLM 설정 유효성 검사"""
    try:
        llm_config = get_llm_config(llm_id)

        # 필수 항목 확인
        missing_fields = [
            field for field in llm_config.required_fields
            if field not in config or not config[field]
        ]

        if missing_fields:
            return False, f"필수 항목 누락: {', '.join(missing_fields)}"

        # API 키 검증 (간단한 검사)
        if "api_key" in config and llm_config.api_key_required:
            api_key = config.get("api_key", "")
            if len(api_key) < 20:
                return False, "API 키가 너무 짧습니다"

        return True, "✅ 유효한 설정입니다"

    except ValueError as e:
        return False, str(e)


def get_llm_info(llm_id: str) -> Dict[str, Any]:
    """LLM 상세 정보 반환"""
    config = get_llm_config(llm_id)
    return {
        "name": config.display_name,
        "provider": config.provider,
        "description": config.description,
        "api_endpoint": config.api_endpoint,
        "required_fields": config.required_fields,
        "optional_fields": config.optional_fields,
        "features": config.features,
        "pricing": config.pricing_info,
        "setup_url": config.setup_url,
        "free_tier": config.free_tier,
    }
