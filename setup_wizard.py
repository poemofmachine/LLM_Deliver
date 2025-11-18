"""
Memory Hub 초기 설정 마법사
Streamlit 기반의 대화형 설정 UI
"""

import streamlit as st
import sys
from pathlib import Path

# 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from config.llm_config import get_llm_list, get_llm_config, get_llm_info
from config.storage_config import get_storage_list, get_storage_config, get_storage_info
from config.config_manager import get_config_manager
from config.validators import Validators


# ============================================================================
# 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="Memory Hub 초기 설정",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
    }
    .step-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "current_step" not in st.session_state:
    # 설정이 이미 저장되어 있으면 완료 화면으로
    config_manager = get_config_manager()
    if config_manager.is_configured():
        st.session_state.current_step = 5
    else:
        st.session_state.current_step = 1

if "llm_selected" not in st.session_state:
    st.session_state.llm_selected = None

if "storage_selected" not in st.session_state:
    st.session_state.storage_selected = None

if "llm_settings" not in st.session_state:
    st.session_state.llm_settings = {}

if "storage_settings" not in st.session_state:
    st.session_state.storage_settings = {}


# ============================================================================
# 함수
# ============================================================================

def render_breadcrumb():
    """Breadcrumb 네비게이션"""
    steps = ["🏠 홈", "🤖 LLM 선택", "💾 저장소 선택", "⚙️ 설정 입력", "✅ 완료"]
    current = st.session_state.current_step

    breadcrumb = " > ".join(steps[:current])
    st.markdown(f"**{breadcrumb}**", unsafe_allow_html=True)
    st.markdown("---")


def render_welcome():
    """환영 화면"""
    render_breadcrumb()

    st.markdown("""
        <div class="welcome-box">
            <h1>🚀 Memory Hub 초기 설정</h1>
            <p style="font-size: 18px; margin-top: 10px;">
                AI 메모리를 클라우드에 저장하세요!
            </p>
            <p style="margin-top: 15px; opacity: 0.9;">
                몇 가지 간단한 선택으로 설정을 완료할 수 있습니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📋 설정 단계")
    st.info("""
    **Step 1️⃣**: 사용할 AI 모델 선택 (ChatGPT, Claude, Gemini 등)

    **Step 2️⃣**: 메모 저장소 선택 (SQLite, Firebase, Notion, MongoDB)

    **Step 3️⃣**: API 키 및 필수 정보 입력

    **Step 4️⃣**: 설정 완료 및 저장
    """)

    st.markdown("---")

    if st.button("🎯 시작하기", key="start_setup"):
        st.session_state.current_step = 2
        st.rerun()


def render_llm_selection():
    """LLM 선택 화면"""
    render_breadcrumb()
    st.markdown("## Step 1️⃣: AI 모델 선택")
    st.markdown("""
    사용할 AI 모델을 선택하세요. 각 모델은 다양한 특징을 가지고 있습니다.
    """)

    st.markdown("---")

    # LLM 목록 표시
    llm_list = get_llm_list()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🤖 사용 가능한 AI 모델")

        selected_llm = None
        for llm in llm_list:
            with st.container():
                col_name, col_free = st.columns([3, 1])

                with col_name:
                    st.markdown(f"**{llm['name']}**")
                    st.caption(f"제공자: {llm['provider']}")
                    st.write(llm['description'])

                with col_free:
                    st.markdown(llm['free'])

                if st.button("선택", key=f"select_{llm['id']}"):
                    selected_llm = llm['id']
                    st.session_state.llm_selected = selected_llm
                    st.session_state.current_step = 3
                    st.rerun()

                st.markdown("---")

    with col2:
        st.markdown("### 💡 팁")
        st.info("""
        **추천:**
        - **처음**: ChatGPT (가장 강력)
        - **개인용**: Claude (긴 문맥)
        - **저비용**: Gemini (저렴)
        - **로컬**: 로컬 모델 (프라이빗)
        """)


def render_storage_selection():
    """저장소 선택 화면"""
    render_breadcrumb()
    st.markdown("## Step 2️⃣: 저장소 선택")
    st.markdown("""
    메모를 저장할 저장소를 선택하세요. 각 저장소는 다양한 특징을 가지고 있습니다.
    """)

    st.markdown("---")

    # 저장소 목록 표시
    storage_list = get_storage_list()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 💾 사용 가능한 저장소")

        for storage in storage_list:
            with st.container():
                col_name, col_limit = st.columns([3, 1])

                with col_name:
                    st.markdown(f"**{storage['name']}**")
                    st.caption(f"유형: {storage['type']}")
                    st.write(storage['description'])
                    st.caption(f"용량: {storage['limit']}")

                with col_limit:
                    st.markdown(storage['free'])

                if st.button("선택", key=f"select_{storage['id']}"):
                    st.session_state.storage_selected = storage['id']
                    st.session_state.current_step = 4
                    st.rerun()

                st.markdown("---")

    with col2:
        st.markdown("### 💡 추천")
        st.info("""
        **상황별 추천:**
        - **개발용**: SQLite (빠르고 무료)
        - **팀협업**: Notion (UI 우수)
        - **클라우드**: Firebase (Google 안전)
        - **확장성**: MongoDB (NoSQL)
        """)


def render_settings_input():
    """설정 입력 화면"""
    render_breadcrumb()
    st.markdown("## Step 3️⃣: API 키 및 설정 입력")

    # LLM 설정
    st.markdown("### 🤖 AI 모델 설정")

    llm_id = st.session_state.llm_selected
    llm_config = get_llm_config(llm_id)
    llm_info = get_llm_info(llm_id)

    st.markdown(f"**선택된 모델**: {llm_info['name']}")
    st.caption(llm_info['description'])

    st.markdown("**필수 정보:**")
    for field in llm_config.required_fields:
        if field == "api_key":
            col1, col2 = st.columns([3, 1])

            with col1:
                st.session_state.llm_settings[field] = st.text_input(
                    f"🔑 API 키",
                    type="password",
                    key=f"llm_{field}"
                )

            with col2:
                if st.button("✓", key=f"validate_llm_{field}", help="검증"):
                    api_key = st.session_state.llm_settings.get(field, "")
                    if api_key:
                        # LLM 타입별 검증
                        if llm_id == "openai":
                            is_valid, message = Validators.validate_openai_key(api_key)
                        elif llm_id == "anthropic":
                            is_valid, message = Validators.validate_anthropic_key(api_key)
                        elif llm_id == "google":
                            is_valid, message = Validators.validate_google_key(api_key)
                        elif llm_id == "huggingface":
                            is_valid, message = Validators.validate_huggingface_key(api_key)
                        else:
                            is_valid, message = True, "✅ 유효한 입력"

                        if is_valid:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("⚠️ API 키를 입력하세요")

            # 검증 결과 표시
            api_key = st.session_state.llm_settings.get(field, "")
            if api_key:
                if llm_id == "openai":
                    is_valid, _ = Validators.validate_openai_key(api_key)
                elif llm_id == "anthropic":
                    is_valid, _ = Validators.validate_anthropic_key(api_key)
                elif llm_id == "google":
                    is_valid, _ = Validators.validate_google_key(api_key)
                elif llm_id == "huggingface":
                    is_valid, _ = Validators.validate_huggingface_key(api_key)
                else:
                    is_valid = True

                if is_valid:
                    st.caption("✅ 유효한 API 키")
                else:
                    st.caption("❌ 유효하지 않은 API 키")
        else:
            st.session_state.llm_settings[field] = st.text_input(
                f"📝 {field}",
                key=f"llm_{field}"
            )

    if llm_config.optional_fields:
        st.markdown("**선택 정보:**")
        for field in llm_config.optional_fields:
            st.session_state.llm_settings[field] = st.text_input(
                f"📝 {field}",
                key=f"llm_opt_{field}"
            )

    st.markdown("---")

    # 저장소 설정
    st.markdown("### 💾 저장소 설정")

    storage_id = st.session_state.storage_selected
    storage_config = get_storage_config(storage_id)
    storage_info = get_storage_info(storage_id)

    st.markdown(f"**선택된 저장소**: {storage_info['name']}")
    st.caption(storage_info['description'])

    st.markdown("**필수 정보:**")
    for field in storage_config.required_fields:
        if "key" in field.lower() or "password" in field.lower():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.session_state.storage_settings[field] = st.text_input(
                    f"🔑 {field}",
                    type="password",
                    key=f"storage_{field}"
                )

            with col2:
                if st.button("✓", key=f"validate_storage_{field}", help="검증"):
                    value = st.session_state.storage_settings.get(field, "")
                    if value:
                        # 저장소 타입별 검증
                        if storage_id == "firebase" and field == "credentials_path":
                            is_valid, message = Validators.validate_firebase_credentials(value)
                        elif storage_id == "notion" and field == "api_key":
                            is_valid, message = Validators.validate_notion_api_key(value)
                        elif storage_id == "mongodb" and field == "connection_string":
                            is_valid, message = Validators.validate_mongodb_connection_string(value)
                        elif storage_id == "superthread" and field == "api_key":
                            is_valid, message = Validators.validate_superthread_api_key(value)
                        else:
                            is_valid, message = True, "✅ 유효한 입력"

                        if is_valid:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("⚠️ 값을 입력하세요")

            # 검증 결과 표시
            value = st.session_state.storage_settings.get(field, "")
            if value:
                if storage_id == "firebase" and field == "credentials_path":
                    is_valid, _ = Validators.validate_firebase_credentials(value)
                elif storage_id == "notion" and field == "api_key":
                    is_valid, _ = Validators.validate_notion_api_key(value)
                elif storage_id == "mongodb" and field == "connection_string":
                    is_valid, _ = Validators.validate_mongodb_connection_string(value)
                elif storage_id == "superthread" and field == "api_key":
                    is_valid, _ = Validators.validate_superthread_api_key(value)
                else:
                    is_valid = True

                if is_valid:
                    st.caption("✅ 유효한 값")
                else:
                    st.caption("❌ 유효하지 않은 값")
        else:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.session_state.storage_settings[field] = st.text_input(
                    f"📝 {field}",
                    key=f"storage_{field}"
                )

            with col2:
                if st.button("✓", key=f"validate_storage_{field}_text", help="검증"):
                    value = st.session_state.storage_settings.get(field, "")
                    if value:
                        # 저장소 타입별 검증
                        if storage_id == "notion" and field == "database_id":
                            is_valid, message = Validators.validate_notion_database_id(value)
                        elif storage_id == "superthread" and field == "workspace_id":
                            is_valid, message = Validators.validate_superthread_workspace_id(value)
                        else:
                            is_valid, message = True, "✅ 유효한 입력"

                        if is_valid:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("⚠️ 값을 입력하세요")

            # 검증 결과 표시
            value = st.session_state.storage_settings.get(field, "")
            if value:
                if storage_id == "notion" and field == "database_id":
                    is_valid, _ = Validators.validate_notion_database_id(value)
                elif storage_id == "superthread" and field == "workspace_id":
                    is_valid, _ = Validators.validate_superthread_workspace_id(value)
                else:
                    is_valid = True

                if is_valid:
                    st.caption("✅ 유효한 값")
                else:
                    st.caption("❌ 유효하지 않은 값")

    if storage_config.optional_fields:
        st.markdown("**선택 정보:**")
        for field in storage_config.optional_fields:
            st.session_state.storage_settings[field] = st.text_input(
                f"📝 {field}",
                key=f"storage_opt_{field}"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ 이전", key="back_to_storage"):
            st.session_state.current_step = 2
            st.rerun()

    with col2:
        if st.button("➡️ 다음 (완료)", key="finish_setup"):
            st.session_state.current_step = 5
            st.rerun()


def render_completion():
    """설정 완료 화면"""
    render_breadcrumb()
    st.markdown("## Step 5️⃣: 설정 완료")

    # 설정 저장
    config_manager = get_config_manager()

    try:
        # 새로운 설정이 있으면 저장 (Step 4에서 온 경우)
        if st.session_state.llm_selected and st.session_state.storage_selected:
            config_manager.set_llm(st.session_state.llm_selected, st.session_state.llm_settings)
            config_manager.set_storage(st.session_state.storage_selected, st.session_state.storage_settings)
            st.markdown("""
                <div class="success-box">
                    <h2>✅ 설정이 완료되었습니다!</h2>
                    <p>모든 설정이 저장되었습니다.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 기존 설정을 표시
            st.markdown("""
                <div class="success-box">
                    <h2>✅ 설정이 이미 완료되어 있습니다!</h2>
                    <p>저장된 설정을 확인하세요.</p>
                </div>
            """, unsafe_allow_html=True)

        # 저장된 설정 조회
        saved_llm = config_manager.get_llm()
        saved_storage = config_manager.get_storage()

        st.markdown("### 📋 현재 설정")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**AI 모델**")
            if saved_llm:
                st.info(f"""
                ✅ 모델: **{saved_llm}**
                """)
            else:
                st.warning("⚠️ AI 모델이 설정되지 않았습니다")

        with col2:
            st.markdown("**저장소**")
            if saved_storage:
                st.info(f"""
                ✅ 저장소: **{saved_storage}**
                """)
            else:
                st.warning("⚠️ 저장소가 설정되지 않았습니다")

        st.markdown("---")

        st.markdown("### 🚀 다음 단계")
        st.success("""
        ✅ 설정 마법사 완료!

        **이제 대시보드를 실행하세요:**

        ```bash
        cd clients
        streamlit run streamlit_dashboard_simple.py
        ```

        또는 **FastAPI 서버와 함께 사용** (선택):
        ```bash
        cd api_server_v2
        uvicorn app.main:app --reload
        ```

        대시보드에서 메모를 저장하고 불러올 수 있습니다!
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⚙️ 설정 변경", key="reconfigure"):
                st.session_state.current_step = 2
                st.rerun()

        with col2:
            if st.button("📋 설정 조회", key="view_config"):
                # .env 파일 표시
                import os
                env_file = os.path.expanduser("~/.memory_hub/.env")
                if os.path.exists(env_file):
                    with open(env_file, "r") as f:
                        st.code(f.read(), language="bash")
                else:
                    st.info("설정 파일이 아직 생성되지 않았습니다")

        with col3:
            if st.button("✅ 완료", key="finish_wizard"):
                st.markdown("""
                    <div class="success-box">
                        <h3>🎉 설정이 완료되었습니다!</h3>
                        <p>이제 대시보드를 실행하세요:</p>
                        <p><code>cd clients && streamlit run streamlit_dashboard_simple.py</code></p>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        st.markdown("---")

        if st.button("🔄 다시 시도", key="retry_setup"):
            st.session_state.current_step = 2
            st.rerun()


# ============================================================================
# 메인
# ============================================================================

def main():
    """메인 함수"""
    # 진행도 표시
    progress = st.progress(0)
    step_num = (st.session_state.current_step - 1) / 4
    progress.progress(min(step_num, 1.0))

    if st.session_state.current_step == 1:
        render_welcome()
    elif st.session_state.current_step == 2:
        render_llm_selection()
    elif st.session_state.current_step == 3:
        render_storage_selection()
    elif st.session_state.current_step == 4:
        render_settings_input()
    elif st.session_state.current_step == 5:
        render_completion()


if __name__ == "__main__":
    main()
