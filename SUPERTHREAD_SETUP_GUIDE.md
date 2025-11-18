# 🧵 Superthread 저장소 완벽 설정 가이드

Superthread를 Memory Hub의 저장소로 사용하기 위한 완전한 설정 및 사용 가이드입니다.

---

## 📋 목차

1. [계정 생성 및 설정](#계정-생성-및-설정)
2. [API 키 발급](#api-키-발급)
3. [환경 변수 설정](#환경-변수-설정)
4. [저장소 기능](#저장소-기능)
5. [API 엔드포인트](#api-엔드포인트)
6. [사용 예제](#사용-예제)
7. [문제 해결](#문제-해결)

---

## 계정 생성 및 설정

### 1단계: Superthread 가입

1. [Superthread](https://superthread.com/)에 접속합니다
2. 이메일로 새 계정을 만듭니다
3. 이메일 인증을 완료합니다

### 2단계: 워크스페이스 생성

1. 대시보드에 로그인합니다
2. "새 워크스페이스 만들기" 버튼을 클릭합니다
3. 워크스페이스 이름을 입력합니다 (예: "Memory Hub")
4. 워크스페이스가 생성됩니다

### 3단계: 팀 멤버 초대 (선택사항)

1. 워크스페이스 설정으로 이동합니다
2. "멤버" 탭을 선택합니다
3. 팀원의 이메일을 입력하여 초대합니다
4. 권한 레벨을 설정합니다:
   - **Admin**: 완전한 관리 권한
   - **Editor**: 문서 편집 권한
   - **Viewer**: 읽기 전용 권한

---

## API 키 발급

### API 키 생성 방법

1. 워크스페이스 설정 → "API & Integrations" 탭
2. "새 API 키 생성" 클릭
3. 키 이름을 입력합니다 (예: "Memory Hub Integration")
4. 권한 범위를 선택합니다:
   - `documents.read` - 문서 읽기
   - `documents.write` - 문서 쓰기
   - `documents.delete` - 문서 삭제
   - `permissions.manage` - 권한 관리
   - `versions.manage` - 버전 관리
5. "생성" 버튼을 클릭합니다
6. **API 키를 안전하게 보관합니다** (다시 표시되지 않습니다)

### Workspace ID 확인

1. 워크스페이스 설정 → "일반" 탭
2. "Workspace ID" 필드에서 ID를 복사합니다
3. 형식: `workspace_12345...`

---

## 환경 변수 설정

### .env 파일 구성

```bash
# Superthread 저장소 설정
STORAGE_TYPE=superthread
SUPERTHREAD_API_KEY=sk_test_xxxxxxxxxxxxx
SUPERTHREAD_WORKSPACE_ID=workspace_xxxxxxxxxxxxx
```

### 설정 파일 (setup_wizard.py)

Streamlit 설정 마법사를 사용하면 자동으로 설정됩니다:

```bash
cd /path/to/LLM_Deliver
streamlit run setup_wizard.py
```

**설정 단계:**
1. "AI 모델 선택" - 사용할 LLM 선택 (예: Claude, ChatGPT)
2. "저장소 선택" - "🧵 Superthread" 선택
3. "API 키 및 설정 입력"
   - API 키 입력 (검증 버튼으로 확인)
   - Workspace ID 입력 (검증 버튼으로 확인)
4. "설정 완료" - 자동으로 암호화되어 저장

---

## 저장소 기능

### ✨ 주요 기능

#### 1. **핵심 메모리 관리**
- 📝 메모리 저장 - 내용을 Superthread에 저장
- 🔍 메모리 조회 - 저장된 메모리 검색
- 📋 목록 조회 - 전체 메모리 목록 표시
- 🗑️ 메모리 삭제 - 메모리 완전 삭제

#### 2. **권한 관리** (Team Collaboration)
```python
# 사용자별 권한 설정
permissions = {
    "user@example.com": "viewer",      # 읽기만 가능
    "team-lead@example.com": "editor", # 수정 가능
    "admin@example.com": "admin"       # 완전 관리
}
storage.set_permissions(doc_id, permissions)
```

#### 3. **버전 관리** (Version Control)
```python
# 버전 목록 조회
storage.get_versions(doc_id, limit=10)

# 새 버전 생성
storage.create_version(doc_id, "설명 추가")

# 이전 버전으로 복원
storage.revert_to_version(doc_id, version_id)
```

#### 4. **고급 검색** (Full-Text Search)
```python
# 키워드로 메모리 검색
storage.search_memories(
    query="python 데이터 분석",
    scope="personal",
    limit=20
)
```

#### 5. **배치 작업** (Batch Operations)
```python
# 여러 메모리 일괄 저장
memories = [
    {"content": "메모리 1", "scope": "personal"},
    {"content": "메모리 2", "scope": "team"},
]
storage.batch_save_memories(memories)

# 여러 메모리 일괄 삭제
storage.batch_delete_memories(["doc_id_1", "doc_id_2"])
```

#### 6. **워크스페이스 통계** (Monitoring)
```python
# 워크스페이스 통계 조회
stats = storage.get_workspace_stats()
# 반환값: total_documents, storage_used, members, teams 등
```

---

## API 엔드포인트

### Base URL
```
http://localhost:8000/superthread
```

### 📝 메모리 관리

#### 메모리 저장
```http
POST /superthread/memories
Content-Type: application/json

{
  "content": "저장할 메모리 내용",
  "scope": "personal",
  "category": "default"
}
```

#### 메모리 목록
```http
GET /superthread/memories?scope=personal&limit=10
```

#### 메모리 삭제
```http
DELETE /superthread/memories/{doc_id}
```

### 🔍 검색

```http
POST /superthread/search
Content-Type: application/json

{
  "query": "검색 키워드",
  "scope": "personal",
  "limit": 20
}
```

### 👥 권한 관리

#### 권한 설정
```http
POST /superthread/permissions/{doc_id}
Content-Type: application/json

{
  "permissions": {
    "user@example.com": "viewer",
    "team-lead@example.com": "editor"
  }
}
```

#### 권한 조회
```http
GET /superthread/permissions/{doc_id}
```

### 📦 배치 작업

#### 일괄 저장
```http
POST /superthread/batch/save
Content-Type: application/json

{
  "memories": [
    {"content": "메모리 1", "scope": "personal"},
    {"content": "메모리 2", "scope": "team"}
  ]
}
```

#### 일괄 삭제
```http
POST /superthread/batch/delete
Content-Type: application/json

{
  "doc_ids": ["doc_id_1", "doc_id_2", "doc_id_3"]
}
```

### 📊 버전 관리

#### 버전 조회
```http
GET /superthread/versions/{doc_id}?limit=10
```

#### 버전 생성
```http
POST /superthread/versions/{doc_id}?description="새로운 버전"
```

#### 버전 복원
```http
POST /superthread/versions/{doc_id}/restore/{version_id}
```

### 📈 통계

#### 워크스페이스 통계
```http
GET /superthread/stats
```

#### 저장소 정보
```http
GET /superthread/info
```

#### 헬스 체크
```http
GET /superthread/health
```

---

## 사용 예제

### Python 예제 1: 기본 메모리 저장

```python
from api_server_v2.app.adapters.factory import get_storage

# 저장소 초기화
storage = get_storage()

# 메모리 저장
result = storage.save_memory(
    workspace_id="workspace_xxxxx",
    content="AI 학습 노트: Python 기초",
    scope="personal",
    category="education"
)

print(result["message"])  # "메모리가 Superthread에 저장되었습니다"
print(result["doc_id"])   # 문서 ID
```

### Python 예제 2: 팀 협업

```python
# 1. 문서 저장
doc_result = storage.save_memory(
    workspace_id="workspace_xxxxx",
    content="프로젝트 계획",
    scope="team",
    team_key="project-alpha"
)
doc_id = doc_result["doc_id"]

# 2. 팀원에게 권한 부여
permissions = {
    "alice@company.com": "editor",
    "bob@company.com": "viewer",
    "manager@company.com": "admin"
}
storage.set_permissions(doc_id, permissions)

# 3. 버전 생성
storage.create_version(doc_id, "초기 계획 작성")

# 4. 현재 권한 확인
perms = storage.get_permissions(doc_id)
print(f"현재 권한: {perms['permissions']}")
```

### Python 예제 3: 검색 및 배치 작업

```python
# 1. 메모리 검색
search_result = storage.search_memories(
    query="Python",
    scope="personal",
    limit=20
)
print(f"검색 결과: {search_result['count']}개")

# 2. 배치 저장
memories = [
    {"content": "노트 1", "scope": "personal", "category": "python"},
    {"content": "노트 2", "scope": "personal", "category": "python"},
    {"content": "노트 3", "scope": "team", "team_key": "study"},
]
batch_result = storage.batch_save_memories(memories)
print(f"저장 완료: {batch_result['saved_count']}/{len(memories)}")

# 3. 워크스페이스 통계
stats = storage.get_workspace_stats()
print(f"전체 문서: {stats['stats']['total_documents']}")
print(f"사용 용량: {stats['stats']['storage_used']}")
```

### cURL 예제: API 호출

```bash
# 1. 메모리 저장
curl -X POST "http://localhost:8000/superthread/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "학습 내용",
    "scope": "personal",
    "category": "study"
  }'

# 2. 메모리 목록 조회
curl -X GET "http://localhost:8000/superthread/memories?scope=personal&limit=10"

# 3. 검색
curl -X POST "http://localhost:8000/superthread/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python",
    "scope": "personal",
    "limit": 20
  }'

# 4. 통계 조회
curl -X GET "http://localhost:8000/superthread/stats"
```

---

## 문제 해결

### ❌ "API 키가 유효하지 않습니다"

**원인:**
- API 키가 잘못 입력됨
- API 키가 만료됨
- 복사 시 공백 포함

**해결:**
1. Superthread 대시보드에서 새 API 키 생성
2. 공백 없이 정확히 입력
3. 환경 변수 다시 설정

### ❌ "Workspace ID를 찾을 수 없습니다"

**원인:**
- Workspace ID 형식이 잘못됨
- 워크스페이스가 삭제됨

**해결:**
1. 대시보드에서 현재 Workspace ID 확인
2. "workspace_"로 시작하는지 확인
3. 필요하면 새 워크스페이스 생성

### ❌ "권한이 없습니다"

**원인:**
- API 키의 권한 범위가 제한됨
- 사용자가 해당 문서에 접근 권한 없음

**해결:**
1. API 키의 권한 범위 확인
2. 필요한 권한 추가
3. 새 API 키 생성

### ✅ 연결 테스트

```bash
# API 서버 시작
cd api_server_v2
uvicorn app.main:app --reload

# 다른 터미널에서 테스트
curl http://localhost:8000/superthread/health

# 예상 응답
# {
#   "status": "healthy",
#   "type": "superthread",
#   "workspace_id": "workspace_xxxxx",
#   "timestamp": "2024-11-18T..."
# }
```

---

## 🎯 Best Practices

### 1. **API 키 보안**
- ✅ 환경 변수로 관리
- ✅ `.env` 파일을 `.gitignore`에 추가
- ✅ API 키 정기적으로 로테이션
- ❌ 코드에 직접 입력하지 않기
- ❌ 공개 저장소에 커밋하지 않기

### 2. **성능 최적화**
- 배치 작업 사용: 대량 데이터는 `batch_save_memories` 사용
- 검색 제한: `limit` 파라미터로 결과 수 제한
- 캐싱: 자주 조회하는 데이터는 로컬 캐시 활용

### 3. **권한 관리**
- 최소 권한 원칙: 필요한 최소 권한만 부여
- 정기 검토: 팀 구성 변화에 따라 권한 업데이트
- 감사 로그: 주요 작업의 로그 기록

### 4. **데이터 백업**
- 정기 백업: 중요 데이터는 주기적으로 백업
- 버전 관리: `create_version`으로 중요 시점 기록
- 아카이빙: 오래된 데이터는 별도 저장소로 이동

---

## 📚 추가 리소스

- [Superthread 공식 문서](https://docs.superthread.com/)
- [Superthread API 레퍼런스](https://api.superthread.com/docs)
- [Memory Hub 문서](./README.md)
- [저장소 어댑터 구현](./api_server_v2/app/adapters/superthread.py)

---

## 🤝 지원

문제가 발생하면:

1. [GitHub Issues](https://github.com/MediumsKor/LLM_Deliver/issues)에서 확인
2. [Superthread 지원팀](https://superthread.com/support)에 문의
3. 우리 커뮤니티 포럼에서 질문

**행운을 빕니다! 🚀**
