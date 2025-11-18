# 🎨 프로세스 시각화 방법 가이드

> **상황별 최적의 시각화 방법 선택하기**

---

## 📑 목차
1. [방법 비교](#방법-비교)
2. [각 방법의 상세 설명](#각-방법의-상세-설명)
3. [구현 예제](#구현-예제)
4. [추천 방법](#추천-방법)

---

## 방법 비교

### 📊 종합 비교표

```
┌─────────────────────────────────────────────────────────────────────────┐
│         방법        │ 난이도 │ 시간 │ 기능 │ 커스터마이징 │    추천    │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Streamlit        │  ⭐   │ 빠름 │ ⭐⭐⭐ │    제한적    │ ✅ 최고   │
│ 2. FastAPI + React  │ ⭐⭐⭐ │ 느림 │ ⭐⭐⭐⭐⭐ │   완전    │ 👍 최종  │
│ 3. Gradio          │  ⭐   │ 빠름 │ ⭐⭐  │    제한적    │ 👌 ML   │
│ 4. Flask           │ ⭐⭐  │ 중간 │ ⭐⭐⭐ │    가능     │ 👌 미니  │
│ 5. 웹소켓 (WebSocket)│ ⭐⭐ │ 중간 │ ⭐⭐⭐⭐ │    가능     │ 👌 실시간│
└─────────────────────────────────────────────────────────────────────────┘
```

### 🎯 상황별 추천

| 상황 | 추천 방법 | 이유 |
|------|---------|------|
| **빠르게 프로토타입 만들기** | Streamlit | 5분 만에 UI 완성 |
| **완벽한 UI 원함** | FastAPI + React | 무한한 커스터마이징 |
| **ML 모델 데모** | Gradio | 모델 테스트에 최적화 |
| **가벼운 서비스** | Flask | 간단한 기능만 필요할 때 |
| **실시간 업데이트** | WebSocket | 진행 상황을 실시간으로 표시 |

---

## 각 방법의 상세 설명

### 1️⃣ Streamlit (현재 구현)

**특징**: 순수 Python으로 UI 구축

#### 장점:
```
✅ 매우 빠른 개발 (5분)
✅ Python만 필요
✅ 자동 새로고침
✅ 통계 차트 내장
✅ 처음 사용자에게 최고
```

#### 단점:
```
❌ 커스터마이징 제한
❌ 디자인 자유도 낮음
❌ 복잡한 상호작용 어려움
```

#### 구현 시간:
```
프로토타입: 1-2시간
간단한 대시보드: 2-4시간
```

#### 설치:
```bash
pip install streamlit requests
streamlit run streamlit_dashboard.py
```

---

### 2️⃣ FastAPI + React

**특징**: 최신 웹 기술의 조합

#### 장점:
```
✅ 완전한 UI 커스터마이징
✅ 최신 프론트엔드 기술
✅ 우수한 성능
✅ 큰 프로젝트에 적합
✅ 전문가 수준의 UI 가능
```

#### 단점:
```
❌ 학습 곡선이 가파름
❌ 개발 시간 오래 걸림
❌ 복잡한 구성
```

#### 구현 시간:
```
기본 대시보드: 4-8시간
완전한 앱: 2-4주
```

#### 기술 스택:
```
Backend: FastAPI (이미 있음!)
Frontend: React / Vue / Svelte
통신: REST API / WebSocket
```

---

### 3️⃣ Gradio

**특징**: ML 모델 데모에 특화

#### 장점:
```
✅ 매우 빠른 구현 (2-3분)
✅ ML 모델 테스트에 최적화
✅ 코드 간단함
```

#### 단점:
```
❌ 복잡한 UI 어려움
❌ 커스터마이징 제한
```

#### 예시:
```python
import gradio as gr
import requests

def push_memory(content):
    response = requests.post(
        "http://localhost:8000/sessions",
        json={"content": content}
    )
    return response.json()

interface = gr.Interface(
    fn=push_memory,
    inputs=gr.Textbox(label="메모"),
    outputs=gr.JSON()
)

interface.launch()
```

---

### 4️⃣ Flask

**특징**: 가벼운 웹 프레임워크

#### 장점:
```
✅ 간단한 구조
✅ 완전한 제어
✅ 가벼움
```

#### 단점:
```
❌ 수작업이 많음
❌ 빌트인 UI 컴포넌트 없음
```

#### 예시:
```python
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/push", methods=["POST"])
def push():
    content = request.json.get("content")
    # FastAPI 호출...
    return {"status": "success"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

### 5️⃣ WebSocket (실시간 업데이트)

**특징**: 양방향 실시간 통신

#### 특징:
```
✅ 실시간 진행 상황 업데이트
✅ 채팅 같은 상호작용 가능
✅ 서버에서 클라이언트로 능동적 전송
```

#### 사용 사례:
```
- 프로세스 진행 상황 실시간 표시
- 여러 사용자 협업
- 실시간 알림
```

#### FastAPI + WebSocket 예시:
```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/push")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 진행 상황 업데이트
    await websocket.send_json({
        "status": "진행 중",
        "step": 1,
        "message": "유효성 검사..."
    })

    # ... 작업 수행 ...

    await websocket.send_json({
        "status": "완료",
        "step": 5,
        "message": "저장 완료!"
    })
```

---

## 구현 예제

### 예제 1: Streamlit (이미 구현됨)

현재 `/home/user/LLM_Deliver/clients/streamlit_dashboard.py` 참조

### 예제 2: Gradio로 간단한 UI 만들기

**파일**: `clients/gradio_dashboard.py`

```python
import gradio as gr
import requests
import json
from typing import Tuple

WEBAPP_URL = "http://localhost:8000"

def push_memory(memory_text: str, workspace_id: str) -> Tuple[str, str]:
    """메모 저장"""
    try:
        response = requests.post(
            f"{WEBAPP_URL}/sessions",
            json={
                "workspace_id": workspace_id,
                "content": memory_text,
                "scope": "personal"
            }
        )

        if response.status_code == 200:
            return "✅ 저장 성공!", json.dumps(response.json(), indent=2)
        else:
            return "❌ 저장 실패", response.text
    except Exception as e:
        return "❌ 오류", str(e)

def fetch_memory(workspace_id: str) -> Tuple[str, str]:
    """메모 불러오기"""
    try:
        response = requests.get(
            f"{WEBAPP_URL}/sessions/latest",
            params={
                "workspace_id": workspace_id,
                "scope": "personal"
            }
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "내용 없음")
            metadata = json.dumps(data, indent=2, ensure_ascii=False)
            return content, metadata
        else:
            return "오류", response.text
    except Exception as e:
        return "오류", str(e)

# Gradio 인터페이스
with gr.Blocks(title="Memory Hub") as demo:
    gr.Markdown("# 🧠 Memory Hub Gradio Dashboard")

    with gr.Tabs():
        # PUSH 탭
        with gr.Tab("📤 메모 저장"):
            workspace_push = gr.Textbox(
                label="워크스페이스 ID",
                placeholder="workspace-id-here"
            )
            memory_input = gr.Textbox(
                label="메모",
                lines=5,
                placeholder="저장할 메모를 입력하세요"
            )
            push_btn = gr.Button("💾 저장", variant="primary")

            push_status = gr.Textbox(label="상태", interactive=False)
            push_result = gr.JSON(label="결과")

            push_btn.click(
                push_memory,
                inputs=[memory_input, workspace_push],
                outputs=[push_status, push_result]
            )

        # PULL 탭
        with gr.Tab("📥 메모 불러오기"):
            workspace_pull = gr.Textbox(
                label="워크스페이스 ID",
                placeholder="workspace-id-here"
            )
            pull_btn = gr.Button("📥 불러오기", variant="primary")

            content_output = gr.Textbox(label="메모 내용", lines=5, interactive=False)
            metadata_output = gr.JSON(label="메타데이터")

            pull_btn.click(
                fetch_memory,
                inputs=[workspace_pull],
                outputs=[content_output, metadata_output]
            )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
```

**실행:**
```bash
pip install gradio
python clients/gradio_dashboard.py
```

**접속:**
```
http://localhost:7860
```

---

### 예제 3: FastAPI + HTML로 간단한 UI

**파일**: `api_server_v2/app/static/dashboard.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Hub Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }

        .process-container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .process-step {
            display: flex;
            align-items: center;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }

        .process-step.active {
            background: #e8f5e9;
            border-left-color: #4CAF50;
        }

        .process-step.pending {
            background: #f5f5f5;
            border-left-color: #ddd;
        }

        .process-step.error {
            background: #ffebee;
            border-left-color: #d32f2f;
        }

        .step-icon {
            font-size: 24px;
            margin-right: 15px;
            width: 40px;
        }

        .step-content {
            flex: 1;
        }

        .step-title {
            font-weight: bold;
            color: #333;
        }

        .step-message {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }

        .input-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }

        textarea, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
        }

        textarea:focus, input:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
        }

        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }

        button:hover {
            background: #45a049;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }

        .tab-button {
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 10px 20px;
            cursor: pointer;
            color: #666;
            font-size: 16px;
        }

        .tab-button.active {
            border-bottom-color: #4CAF50;
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Memory Hub Dashboard</h1>

        <div class="tabs">
            <button class="tab-button active" onclick="switchTab(0)">📤 메모 저장</button>
            <button class="tab-button" onclick="switchTab(1)">📥 메모 불러오기</button>
        </div>

        <!-- 메모 저장 -->
        <div id="tab-0" class="process-container">
            <h2>📤 메모 저장하기</h2>

            <div class="input-group">
                <label>📁 워크스페이스</label>
                <input type="text" id="workspace-push" placeholder="workspace-id">
            </div>

            <div class="input-group">
                <label>📝 메모</label>
                <textarea id="memory-content" rows="8" placeholder="저장할 메모를 입력하세요"></textarea>
            </div>

            <button onclick="pushMemory()">💾 저장</button>

            <div id="process-steps" style="margin-top: 20px;"></div>
        </div>

        <!-- 메모 불러오기 -->
        <div id="tab-1" class="process-container" style="display: none;">
            <h2>📥 메모 불러오기</h2>

            <div class="input-group">
                <label>📁 워크스페이스</label>
                <input type="text" id="workspace-pull" placeholder="workspace-id">
            </div>

            <button onclick="pullMemory()">📥 불러오기</button>

            <div id="pull-result" style="margin-top: 20px;"></div>
        </div>
    </div>

    <script>
        async function pushMemory() {
            const workspace = document.getElementById('workspace-push').value;
            const content = document.getElementById('memory-content').value;
            const container = document.getElementById('process-steps');

            if (!content) {
                alert('메모를 입력하세요!');
                return;
            }

            container.innerHTML = '';

            const steps = [
                { icon: '📝', title: '유효성 검사' },
                { icon: '🔐', title: '인증 확인' },
                { icon: '💾', title: 'DB 저장' },
                { icon: '☁️', title: 'Google Docs 동기화' },
                { icon: '✅', title: '저장 완료' }
            ];

            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const div = document.createElement('div');
                div.className = i === 0 ? 'process-step active' : 'process-step pending';
                div.innerHTML = `
                    <div class="step-icon">${step.icon}</div>
                    <div class="step-content">
                        <div class="step-title">${step.title}</div>
                    </div>
                `;
                container.appendChild(div);

                await new Promise(resolve => setTimeout(resolve, 500));
            }

            alert('메모가 저장되었습니다!');
        }

        async function pullMemory() {
            const workspace = document.getElementById('workspace-pull').value;
            const container = document.getElementById('pull-result');

            const div = document.createElement('div');
            div.className = 'process-step active';
            div.innerHTML = '<div class="step-title">📥 불러오기 완료!</div>';
            container.appendChild(div);
        }

        function switchTab(index) {
            // 모든 탭 숨기기
            document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));

            // 선택된 탭 표시
            document.getElementById(`tab-${index}`).style.display = 'block';
            document.querySelectorAll('.tab-button')[index].classList.add('active');
        }
    </script>
</body>
</html>
```

**FastAPI에 연결:**

```python
# api_server_v2/app/main.py에 추가

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 정적 파일 서빙
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("app/static/dashboard.html")
```

**접속:**
```
http://localhost:8000/dashboard
```

---

## 추천 방법

### 🥇 지금 당장: **Streamlit** ✅

```bash
# 이미 구현되어 있습니다!
cd clients
streamlit run streamlit_dashboard.py
```

**이유:**
- ✅ 이미 완성된 상태
- ✅ 5분이면 실행 가능
- ✅ 초보자 친화적
- ✅ 프로토타입으로 충분

---

### 🥈 다음 단계: **FastAPI + React**

**언제 추천:**
- 완벽한 디자인 원함
- 대규모 팀 프로젝트
- 전문가 수준의 UI 필요

**대략적인 일정:**
```
주 1: React 프로젝트 설정 및 기본 레이아웃
주 2: API 연결 및 상태 관리
주 3: 스타일링 및 기능 완성
```

---

### 🥉 기타 방법

| 방법 | 언제 사용 | 시간 |
|------|---------|------|
| **Gradio** | ML 모델 데모 | 1-2시간 |
| **Flask** | 간단한 웹앱 | 3-5시간 |
| **WebSocket** | 실시간 업데이트 | 4-6시간 |

---

## 🚀 실행 방법 정리

### 현재 (Streamlit):
```bash
# 터미널 1: FastAPI 서버
cd api_server_v2
uvicorn app.main:app --reload

# 터미널 2: Streamlit 대시보드
cd clients
streamlit run streamlit_dashboard.py
```

### 미래 (선택사항):

**Gradio 추가:**
```bash
pip install gradio
python clients/gradio_dashboard.py  # http://localhost:7860
```

**Flask 추가:**
```bash
pip install flask
python clients/flask_dashboard.py  # http://localhost:5000
```

---

## 📚 다음 학습

1. **Streamlit 심화**: 차트, 맵, 데이터프레임
2. **React 기초**: 컴포넌트, 상태 관리, API 호출
3. **UI/UX 디자인**: 컬러, 타이포그래피, 반응형

---

**Happy Building! 🎨✨**
