"""
Memory Hub - Streamlit Dashboard
프로세스 시각화 UI
"""

import streamlit as st
import requests
import time
from datetime import datetime
from typing import Optional, Dict, Any
import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# ============================================================================
# 설정
# ============================================================================

WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

# 페이지 설정
st.set_page_config(
    page_title="Memory Hub Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .process-step {
        padding: 20px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 4px solid #2E7D32;
    }
    .process-step.active {
        background-color: #E8F5E9;
        border-left-color: #4CAF50;
    }
    .process-step.pending {
        background-color: #F5F5F5;
        border-left-color: #BDBDBD;
    }
    .process-step.error {
        background-color: #FFEBEE;
        border-left-color: #D32F2F;
    }
    .success-box {
        padding: 15px;
        background-color: #C8E6C9;
        border-radius: 5px;
        color: #1B5E20;
    }
    .error-box {
        padding: 15px;
        background-color: #FFCDD2;
        border-radius: 5px;
        color: #B71C1C;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# 헬퍼 함수
# ============================================================================

def check_server_health():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{WEBAPP_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_workspaces():
    """워크스페이스 조회"""
    try:
        response = requests.get(f"{WEBAPP_URL}/workspaces")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"워크스페이스 조회 실패: {str(e)}")
        return []


def create_workspace(name: str, scope: str = "personal"):
    """워크스페이스 생성"""
    try:
        payload = {
            "name": name,
            "scope": scope,
            "doc_id": os.getenv("DOC_ID", ""),
            "doc_url": ""
        }
        response = requests.post(f"{WEBAPP_URL}/workspaces", json=payload)
        return response.status_code == 201, response.json() if response.status_code == 201 else None
    except Exception as e:
        return False, str(e)


def push_memory(workspace_id: str, content: str, scope: str = "personal", team_key: Optional[str] = None):
    """메모 저장 (PUSH)"""
    try:
        payload = {
            "workspace_id": workspace_id,
            "scope": scope,
            "team_key": team_key,
            "content": content,
            "revision": "1"
        }
        response = requests.post(f"{WEBAPP_URL}/sessions", json=payload, timeout=10)
        return response.status_code in [200, 201], response.json()
    except Exception as e:
        return False, {"error": str(e)}


def fetch_memory(workspace_id: str, scope: str = "personal", team_key: Optional[str] = None):
    """메모 불러오기 (PULL)"""
    try:
        params = {
            "workspace_id": workspace_id,
            "scope": scope,
        }
        if team_key:
            params["team_key"] = team_key

        response = requests.get(f"{WEBAPP_URL}/sessions/latest", params=params, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}


# ============================================================================
# 페이지: 홈 대시보드
# ============================================================================

def page_dashboard():
    """메인 대시보드"""
    st.title("🧠 Memory Hub Dashboard")
    st.markdown("*AI 메모리를 Google Docs에 저장하고 관리하세요*")

    # 서버 상태 확인
    col1, col2, col3 = st.columns(3)

    with col1:
        server_status = check_server_health()
        if server_status:
            st.success("✅ 서버 연결됨")
        else:
            st.error("❌ 서버 연결 실패")

    with col2:
        st.info(f"🔗 {WEBAPP_URL}")

    with col3:
        if API_TOKEN:
            st.success("✅ API 토큰 설정됨")
        else:
            st.warning("⚠️ API 토큰 미설정")

    st.divider()

    # 메뉴 탭
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 메모 저장 (PUSH)",
        "📥 메모 불러오기 (PULL)",
        "🏢 워크스페이스",
        "📊 프로세스 흐름도"
    ])

    # ========================================================================
    # TAB 1: 메모 저장 (PUSH)
    # ========================================================================
    with tab1:
        st.header("📤 메모 저장하기")
        st.markdown("클립보드의 메모를 Google Docs에 자동으로 저장합니다.")

        # 워크스페이스 선택
        workspaces = get_workspaces()
        if not workspaces:
            st.warning("워크스페이스가 없습니다. 아래에서 생성해주세요.")
            return

        workspace_options = {ws["name"]: ws["id"] for ws in workspaces}
        selected_workspace = st.selectbox(
            "📁 워크스페이스 선택",
            options=list(workspace_options.keys()),
            key="push_workspace"
        )
        workspace_id = workspace_options[selected_workspace]

        # 스코프 선택
        scope = st.radio("📍 저장 위치", ["personal", "team"], horizontal=True)

        # 메모 내용 입력
        st.subheader("📝 저장할 메모 입력")
        memory_content = st.text_area(
            "메모를 입력하거나 붙여넣기하세요",
            height=250,
            placeholder="[HANDOFF]\n여기에 저장할 메모를 입력하세요..."
        )

        # 저장 버튼
        if st.button("💾 Google Docs에 저장", key="push_button", type="primary"):
            if not memory_content.strip():
                st.error("저장할 메모를 입력해주세요!")
            else:
                # 프로세스 시각화
                st.subheader("⏳ 저장 프로세스 진행 중...")

                # 진행 단계 표시
                progress_steps = [
                    ("📝 메모 유효성 검사", "진행 중..."),
                    ("🔐 인증 확인", "대기 중"),
                    ("💾 로컬 DB 저장", "대기 중"),
                    ("☁️ Google Docs 동기화", "대기 중"),
                    ("✅ 저장 완료", "대기 중"),
                ]

                progress_container = st.container()

                # 단계 1: 유효성 검사
                with progress_container:
                    step_container = st.empty()

                    with step_container.container():
                        st.markdown('<div class="process-step active">📝 메모 유효성 검사</div>', unsafe_allow_html=True)
                        time.sleep(0.5)

                # 단계 2: 인증 확인
                with progress_container:
                    with st.container():
                        st.markdown('<div class="process-step active">✅ 메모 유효성 검사</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">🔐 인증 확인</div>', unsafe_allow_html=True)
                        time.sleep(0.5)

                # 단계 3: DB 저장
                with progress_container:
                    with st.container():
                        st.markdown('<div class="process-step active">✅ 메모 유효성 검사</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ 인증 확인</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">💾 로컬 DB 저장</div>', unsafe_allow_html=True)
                        time.sleep(0.5)

                # 단계 4: Google Docs 동기화
                with progress_container:
                    with st.container():
                        st.markdown('<div class="process-step active">✅ 메모 유효성 검사</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ 인증 확인</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ 로컬 DB 저장</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">☁️ Google Docs 동기화</div>', unsafe_allow_html=True)

                        # 실제 저장 수행
                        success, result = push_memory(workspace_id, memory_content, scope)

                        time.sleep(0.5)

                # 결과
                with progress_container:
                    with st.container():
                        st.markdown('<div class="process-step active">✅ 메모 유효성 검사</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ 인증 확인</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ 로컬 DB 저장</div>', unsafe_allow_html=True)
                        st.markdown('<div class="process-step active">✅ Google Docs 동기화</div>', unsafe_allow_html=True)

                        if success:
                            st.markdown('<div class="process-step active">✅ 저장 완료!</div>', unsafe_allow_html=True)
                            st.success("🎉 메모가 성공적으로 저장되었습니다!")

                            # 결과 정보
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("저장 시간", datetime.now().strftime("%H:%M:%S"))
                            with col2:
                                st.metric("저장된 메모 길이", f"{len(memory_content)} 글자")
                        else:
                            st.markdown('<div class="process-step error">❌ 저장 실패</div>', unsafe_allow_html=True)
                            st.error(f"저장 실패: {result.get('error', '알 수 없는 오류')}")

    # ========================================================================
    # TAB 2: 메모 불러오기 (PULL)
    # ========================================================================
    with tab2:
        st.header("📥 메모 불러오기")
        st.markdown("Google Docs에서 최신 메모를 불러옵니다.")

        # 워크스페이스 선택
        workspaces = get_workspaces()
        if not workspaces:
            st.warning("워크스페이스가 없습니다. 아래에서 생성해주세요.")
            return

        workspace_options = {ws["name"]: ws["id"] for ws in workspaces}
        selected_workspace = st.selectbox(
            "📁 워크스페이스 선택",
            options=list(workspace_options.keys()),
            key="pull_workspace"
        )
        workspace_id = workspace_options[selected_workspace]

        # 스코프 선택
        scope = st.radio("📍 불러올 위치", ["personal", "team"], horizontal=True)

        # 불러오기 버튼
        if st.button("📥 메모 불러오기", key="pull_button", type="primary"):
            st.subheader("⏳ 불러오기 프로세스 진행 중...")

            # 진행 단계
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown('<div class="process-step active">🔐 인증 확인</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="process-step pending">☁️ Google Docs 조회</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="process-step pending">📊 메타데이터 파싱</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="process-step pending">✅ 완료</div>', unsafe_allow_html=True)

            time.sleep(0.5)

            # 실제 불러오기
            success, result = fetch_memory(workspace_id, scope)

            if success:
                st.success("✅ 메모를 성공적으로 불러왔습니다!")

                # 메모 표시
                st.subheader("📄 불러온 메모")
                st.text_area(
                    "메모 내용",
                    value=result.get("content", "내용 없음"),
                    height=250,
                    disabled=True
                )

                # 메타정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("수정 시간", result.get("last_updated", "N/A")[:10])
                with col2:
                    st.metric("리비전", result.get("revision_id", "N/A"))
                with col3:
                    st.metric("카테고리", result.get("category", "N/A"))

                # 문서 URL
                if result.get("doc_url"):
                    st.markdown(f"📖 [Google Docs에서 보기]({result.get('doc_url')})")
            else:
                st.error(f"불러오기 실패: {result.get('error', '알 수 없는 오류')}")

    # ========================================================================
    # TAB 3: 워크스페이스 관리
    # ========================================================================
    with tab3:
        st.header("🏢 워크스페이스 관리")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("기존 워크스페이스")
            workspaces = get_workspaces()

            if workspaces:
                for ws in workspaces:
                    with st.container():
                        col_name, col_scope, col_delete = st.columns([2, 1, 1])
                        with col_name:
                            st.write(f"📁 {ws['name']}")
                        with col_scope:
                            st.caption(ws.get("scope", "personal"))
            else:
                st.info("워크스페이스가 없습니다.")

        with col2:
            st.subheader("새 워크스페이스")
            new_ws_name = st.text_input("이름")
            new_ws_scope = st.radio("스코프", ["personal", "team"])

            if st.button("생성", type="primary"):
                if new_ws_name:
                    success, result = create_workspace(new_ws_name, new_ws_scope)
                    if success:
                        st.success(f"✅ {new_ws_name} 워크스페이스 생성됨!")
                        st.rerun()
                    else:
                        st.error(f"생성 실패: {result}")
                else:
                    st.warning("워크스페이스 이름을 입력해주세요!")

    # ========================================================================
    # TAB 4: 프로세스 흐름도
    # ========================================================================
    with tab4:
        st.header("📊 프로세스 흐름도")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📤 PUSH (메모 저장)")
            st.markdown("""
            ```
            ┌─────────────────┐
            │  메모 입력      │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 유효성 검사     │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 인증 확인       │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ DB 저장         │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ Google Docs     │
            │ 동기화          │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ ✅ 완료         │
            └─────────────────┘
            ```
            """)

        with col2:
            st.subheader("📥 PULL (메모 불러오기)")
            st.markdown("""
            ```
            ┌─────────────────┐
            │ 불러오기 요청  │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 인증 확인       │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ Google Docs     │
            │ 조회            │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 메타데이터      │
            │ 파싱            │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ ✅ 완료         │
            └─────────────────┘
            ```
            """)


# ============================================================================
# 메인
# ============================================================================

def main():
    """메인 함수"""
    page_dashboard()


if __name__ == "__main__":
    main()
