# 💾 Memory Hub - Google Docs 대신 사용 가능한 무료 저장소

> **Google Docs 없이 메모를 저장하는 방법들**

---

## 📊 무료 저장소 비교표

```
┌─────────────────┬──────────┬────────────┬──────────┬──────────┬─────────┐
│     서비스      │ 무료플랜 │ 저장용량   │ 설정난이 │  추천   │  특징   │
├─────────────────┼──────────┼────────────┼──────────┼──────────┼─────────┤
│ SQLite          │    ✅    │   무제한   │   ⭐    │ ✅✅✅  │ 로컬   │
│ Notion          │    ✅    │   무제한   │  ⭐⭐   │  ✅✅  │ 클라우드│
│ Firebase        │    ✅    │  1GB 무료  │  ⭐⭐   │  ✅✅  │ 클라우드│
│ MongoDB Atlas   │    ✅    │  512MB     │  ⭐⭐   │  ✅✅  │ 클라우드│
│ Supabase        │    ✅    │   무제한   │  ⭐⭐⭐ │  ✅   │ PostgreSQL│
│ GitHub Gists    │    ✅    │   무제한   │   ⭐    │  ✅✅  │ Git기반│
│ OneNote         │    ✅    │   5GB      │  ⭐⭐   │  ✅✅  │ Microsoft│
│ Dropbox Paper   │    ✅    │  제한적    │  ⭐⭐   │  ✅   │ 협업  │
└─────────────────┴──────────┴────────────┴──────────┴──────────┴─────────┘
```

---

## 🥇 **추천 순위**

### **1위: SQLite (로컬 저장소)** ⭐⭐⭐⭐⭐

**장점:**
```
✅ 완전히 무료
✅ 설치 불필요 (Python에 포함됨)
✅ 속도 빠름
✅ 오프라인 작동
✅ 데이터 완전 소유
✅ 파일로 백업 가능
```

**단점:**
```
❌ 클라우드 공유 불가 (로컬에만 저장)
❌ 여러 기기에서 접속 어려움
```

**적합한 경우:**
- 개인용 메모
- 로컬에만 저장하면 됨
- 속도가 중요할 때
- 비용 절감

---

### **2위: Notion** ⭐⭐⭐⭐

**장점:**
```
✅ 무료 플랜 있음
✅ 아름다운 UI
✅ 테이블, 데이터베이스 지원
✅ 협업 가능
✅ 모바일 앱
✅ API 있음 (공식)
```

**단점:**
```
❌ 무료 플랜에 사용자 5명 제한
❌ API 설정이 조금 복잡
```

**적합한 경우:**
- 팀 협업
- 예쁜 UI 원함
- 데이터베이스 기능 필요

---

### **3위: Firebase Firestore** ⭐⭐⭐⭐

**장점:**
```
✅ Google 제공 (안정성)
✅ 실시간 데이터 동기화
✅ 무료 티어 충분
✅ 자동 백업
✅ 모바일/웹 지원
```

**단점:**
```
❌ 1GB 용량 제한
❌ Google 계정 필요
❌ 데이터베이스 개념 필요
```

**적합한 경우:**
- 클라우드 저장 원함
- 실시간 동기화 필요
- Google 생태계 선호

---

### **4위: MongoDB Atlas** ⭐⭐⭐

**장점:**
```
✅ 무료 클라우드 호스팅
✅ NoSQL 강력함
✅ 확장성 좋음
✅ Python 라이브러리 풍부
```

**단점:**
```
❌ 512MB 용량 제한
❌ 설정이 조금 복잡
```

**적합한 경우:**
- 클라우드 DB 원함
- 스케일업 예상
- NoSQL 선호

---

### **5위: GitHub Gists** ⭐⭐⭐

**장점:**
```
✅ 완전히 무료
✅ Git 기반 (버전 관리)
✅ 공개/비공개 가능
✅ 코드 강조 지원
✅ API 있음
```

**단점:**
```
❌ UI가 단순함
❌ 구조화된 DB 아님
```

**적합한 경우:**
- 코드 스니펫 저장
- 버전 관리 필요
- 간단한 텍스트

---

## 🔧 **각 방법별 구현 예제**

### **1. SQLite (가장 간단!)**

```python
import sqlite3
from datetime import datetime

# 데이터베이스 연결 (자동 생성)
conn = sqlite3.connect('memory_hub.db')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY,
        workspace_id TEXT,
        content TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
''')

# 메모 저장
def save_memory(workspace_id, content):
    cursor.execute('''
        INSERT INTO memories (workspace_id, content, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (workspace_id, content, datetime.now(), datetime.now()))
    conn.commit()
    print("✅ 메모 저장됨 (로컬 DB)")

# 메모 조회
def get_memory(workspace_id):
    cursor.execute('''
        SELECT content, updated_at FROM memories
        WHERE workspace_id = ?
        ORDER BY updated_at DESC LIMIT 1
    ''', (workspace_id,))
    return cursor.fetchone()

# 사용
save_memory("personal", "[HANDOFF]\n테스트 메모")
result = get_memory("personal")
print(f"메모: {result[0]}")
print(f"수정: {result[1]}")
```

**장점:** 코드 10줄로 완성! 🎉

---

### **2. Notion (API 사용)**

```python
import requests
from datetime import datetime

# Notion API 설정
NOTION_API_KEY = "your-api-key"
DATABASE_ID = "your-database-id"

def save_to_notion(workspace_id, content):
    """Notion 데이터베이스에 메모 저장"""

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": workspace_id}}]
            },
            "Content": {
                "rich_text": [{"text": {"content": content}}]
            },
            "Created": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("✅ Notion에 저장됨")
    else:
        print(f"❌ 저장 실패: {response.status_code}")

# 사용
save_to_notion("personal", "[HANDOFF]\n테스트 메모")
```

**설정:** https://www.notion.so/my-integrations 에서 API 키 받기

---

### **3. Firebase Firestore**

```python
from firebase_admin import initialize_app, firestore
from datetime import datetime

# Firebase 초기화 (credentials.json 필요)
app = initialize_app()
db = firestore.client()

def save_to_firebase(workspace_id, content):
    """Firebase에 메모 저장"""

    db.collection("memories").document(workspace_id).set({
        "workspace_id": workspace_id,
        "content": content,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    print("✅ Firebase에 저장됨")

def get_from_firebase(workspace_id):
    """Firebase에서 메모 조회"""

    doc = db.collection("memories").document(workspace_id).get()

    if doc.exists:
        return doc.to_dict()
    else:
        return None

# 사용
save_to_firebase("personal", "[HANDOFF]\n테스트 메모")
result = get_from_firebase("personal")
print(f"메모: {result['content']}")
```

**설정:**
1. Firebase 콘솔에서 프로젝트 생성
2. Firestore 데이터베이스 활성화
3. 서비스 계정 키 다운로드

---

### **4. GitHub Gists**

```python
import requests
from datetime import datetime

GITHUB_TOKEN = "your-github-token"

def save_to_gist(workspace_id, content):
    """GitHub Gist에 메모 저장"""

    url = "https://api.github.com/gists"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "description": f"Memory Hub - {workspace_id}",
        "public": False,  # 비공개
        "files": {
            f"{workspace_id}.md": {
                "content": content
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        gist_id = response.json()["id"]
        print(f"✅ Gist에 저장됨 (ID: {gist_id})")
        return gist_id
    else:
        print(f"❌ 저장 실패: {response.status_code}")

# 사용
save_to_gist("personal", "[HANDOFF]\n테스트 메모")
```

**설정:** GitHub Personal Access Token 생성

---

## 📋 **각 방법의 용도별 추천**

| 상황 | 추천 | 이유 |
|------|------|------|
| 📱 **개인용, 로컬만** | SQLite | 완전 무료, 설치 쉬움 |
| 👥 **팀 협업 필요** | Notion | 협업, UI 예쁨 |
| ☁️ **클라우드 동기화** | Firebase | Google 안정성, 실시간 |
| 📊 **대규모 프로젝트** | MongoDB | 확장성, 강력함 |
| 🔧 **버전 관리** | GitHub Gists | Git 기반, 코드 친화적 |
| 🎯 **가장 쉬운 방법** | SQLite | 코드 간단, 빠름 |

---

## 🚀 **Memory Hub에 적용하기**

### **현재 구조:**
```
Memory Hub
├── FastAPI 서버
├── Google Docs 저장
└── Streamlit UI
```

### **변경 가능한 구조:**
```
Memory Hub
├── FastAPI 서버
├── 저장소 선택 (SQLite/Firebase/Notion/etc)
└── Streamlit UI
```

---

## 💡 **추천 조합**

### **시나리오 1: 로컬 개발**
```
Streamlit + SQLite
- 가장 간단
- 설치 불필요
- 오프라인 작동
```

### **시나리오 2: 팀 협업**
```
Streamlit + Notion
- 협업 가능
- 예쁜 UI
- 모바일 지원
```

### **시나리오 3: 클라우드**
```
Streamlit + Firebase
- 자동 백업
- 실시간 동기화
- Google 안정성
```

---

## ✅ **다음 단계**

**다음 중 하나를 원하시나요?**

1. **SQLite로 변경** - 가장 간단 (추천)
2. **Notion 연동** - 협업 원할 때
3. **Firebase 연동** - 클라우드 원할 때
4. **MongoDB 연동** - 대규모 프로젝트
5. **여러 옵션 지원** - 유연한 구조

---

**어떤 방법으로 진행하시겠어요?** 🎯
