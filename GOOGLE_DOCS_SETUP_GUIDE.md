# 📄 Google Docs 저장소 완벽 설정 가이드

Google Docs와 Google Drive를 Memory Hub의 저장소로 사용하기 위한 완전한 설정 및 사용 가이드입니다.

---

## 📋 목차

1. [계정 설정 및 프로젝트 생성](#계정-설정-및-프로젝트-생성)
2. [Google Cloud 프로젝트 설정](#google-cloud-프로젝트-설정)
3. [OAuth 2.0 자격증명](#oauth-20-자격증명)
4. [환경 변수 설정](#환경-변수-설정)
5. [저장소 기능](#저장소-기능)
6. [API 엔드포인트](#api-엔드포인트)
7. [사용 예제](#사용-예제)
8. [문제 해결](#문제-해결)

---

## 계정 설정 및 프로젝트 생성

### 1단계: Google 계정 준비

1. [Google 계정](https://accounts.google.com)에 로그인합니다
2. 계정이 없으면 새로 만듭니다

### 2단계: 메모리 저장용 폴더 생성

1. [Google Drive](https://drive.google.com)에 접속합니다
2. "새로 만들기" → "폴더" 클릭
3. 폴더 이름을 입력합니다 (예: "Memory Hub")
4. 폴더 생성 후 URL에서 폴더 ID를 복사합니다
   - URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - FOLDER_ID_HERE가 폴더 ID입니다

### 3단계: 기본 공유 권한 설정

1. 생성한 폴더를 마우스 우클릭합니다
2. "공유" 클릭
3. 팀원의 이메일을 추가합니다 (선택사항)
4. 공유 범위를 설정합니다

---

## Google Cloud 프로젝트 설정

### 1단계: Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다
2. 프로젝트 드롭다운을 클릭합니다
3. "새 프로젝트" 클릭
4. 프로젝트 이름을 입력합니다 (예: "Memory Hub")
5. "만들기" 클릭

### 2단계: Google Docs & Drive API 활성화

1. 콘솔의 검색 바에서 "Google Docs API" 검색
2. 결과에서 "Google Docs API" 선택
3. "활성화" 버튼 클릭
4. 다시 검색 바에서 "Google Drive API" 검색
5. "Google Drive API" 선택 후 "활성화" 클릭

### 3단계: OAuth 동의 화면 구성

1. 왼쪽 메뉴에서 "OAuth 동의 화면" 클릭
2. 사용자 유형 선택:
   - 개인용: "외부" 선택
   - 회사용: "내부" 선택
3. "만들기" 클릭
4. 필수 정보 입력:
   - **앱 이름**: Memory Hub
   - **사용자 지원 이메일**: 당신의 이메일
   - **개발자 연락처**: 당신의 이메일
5. "저장 및 계속" 클릭

### 4단계: 범위 추가

1. "범위 추가 또는 제거" 클릭
2. 다음 범위를 검색 후 선택:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/drive.metadata`
3. "업데이트" 클릭
4. "저장 및 계속" 클릭

---

## OAuth 2.0 자격증명

### 1단계: OAuth 클라이언트 ID 생성

1. 왼쪽 메뉴에서 "사용자 인증 정보" 클릭
2. "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형: "데스크탑 앱" 선택
4. "만들기" 클릭
5. JSON 파일을 다운로드합니다
   - **주의**: 이 파일은 안전하게 보관하세요!

### 2단계: 웹 애플리케이션 설정 (선택)

FastAPI 서버를 사용하는 경우:

1. "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
2. 애플리케이션 유형: "웹 애플리케이션" 선택
3. "승인된 리디렉션 URI" 추가:
   ```
   http://localhost:8000/auth/callback
   http://YOUR_SERVER_IP:8000/auth/callback
   ```
4. "만들기" 클릭
5. JSON 파일을 다운로드합니다

---

## 환경 변수 설정

### 방법 1: setup_wizard.py 사용 (권장)

```bash
cd /path/to/LLM_Deliver
streamlit run setup_wizard.py
```

설정 단계:
1. "AI 모델 선택" - 원하는 LLM 선택
2. "저장소 선택" - "📄 Google Docs" 선택
3. "API 키 및 설정 입력"
   - Google OAuth Token JSON 입력 (또는 파일 경로)
   - Google Folder ID 입력
4. "설정 완료" - 자동으로 암호화되어 저장

### 방법 2: 수동 환경 변수 설정

**.env 파일**:
```bash
# Google Docs 저장소 설정
STORAGE_TYPE=google_docs
GOOGLE_TOKEN_JSON={"type":"oauth2","client_id":"...","refresh_token":"..."}
GOOGLE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j
```

### 방법 3: 환경 변수로 직접 설정

```bash
export GOOGLE_TOKEN_JSON='{"type":"oauth2",...}'
export GOOGLE_FOLDER_ID='1a2b3c4d5e6f7g8h9i0j'
```

---

## 저장소 기능

### ✨ 주요 기능

#### 1. **핵심 메모리 관리**
- 📝 메모리 저장 - Google Docs로 메모리 저장
- 🔍 메모리 조회 - 저장된 최신 메모리 검색
- 📋 목록 조회 - 전체 메모리 목록 표시
- 🗑️ 메모리 삭제 - 메모리 휴지통 이동

#### 2. **권한 관리** (Team Collaboration)
```python
# 사용자별 권한 설정
permissions = {
    "user@example.com": "viewer",      # 읽기만
    "editor@example.com": "editor",    # 수정 가능
    "admin@example.com": "admin"       # 완전 관리
}
storage.set_permissions(doc_id, permissions)
```

#### 3. **버전 관리** (Revision History)
```python
# 버전 목록 조회
storage.get_versions(doc_id, limit=10)

# 버전 정보 조회
storage.revert_to_version(doc_id, version_id)
```

#### 4. **고급 검색** (Full-Text Search)
```python
# Google Drive에서 메모리 검색
storage.search_memories(
    query="Python 데이터분석",
    scope="personal",
    limit=20
)
```

#### 5. **배치 작업** (Batch Operations)
```python
# 여러 메모리 일괄 저장
memories = [
    {"content": "메모리 1", "scope": "personal"},
    {"content": "메모리 2", "scope": "personal"},
]
storage.batch_save_memories(memories)

# 여러 메모리 일괄 삭제
storage.batch_delete_memories(["doc_id_1", "doc_id_2"])
```

#### 6. **워크스페이스 통계** (Monitoring)
```python
# 저장소 통계 조회
stats = storage.get_workspace_stats()
# 반환값: total_documents, total_size, average_size 등
```

---

## API 엔드포인트

### Base URL
```
http://localhost:8000/google-docs
```

### 📝 메모리 관리

#### 메모리 저장
```http
POST /google-docs/memories
Content-Type: application/json

{
  "content": "저장할 메모리 내용",
  "scope": "personal",
  "category": "default"
}
```

#### 메모리 목록
```http
GET /google-docs/memories?scope=personal&limit=10
```

#### 메모리 삭제
```http
DELETE /google-docs/memories/{doc_id}
```

### 🔍 검색

```http
POST /google-docs/search
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
POST /google-docs/permissions/{doc_id}
Content-Type: application/json

{
  "permissions": {
    "user@example.com": "viewer",
    "editor@example.com": "editor"
  }
}
```

#### 권한 조회
```http
GET /google-docs/permissions/{doc_id}
```

### 📦 배치 작업

#### 일괄 저장
```http
POST /google-docs/batch/save
Content-Type: application/json

{
  "memories": [
    {"content": "메모리 1", "scope": "personal"},
    {"content": "메모리 2", "scope": "personal"}
  ]
}
```

#### 일괄 삭제
```http
POST /google-docs/batch/delete
Content-Type: application/json

{
  "doc_ids": ["doc_id_1", "doc_id_2", "doc_id_3"]
}
```

### 📊 버전 관리

#### 버전 조회
```http
GET /google-docs/versions/{doc_id}?limit=10
```

#### 버전 정보 조회
```http
POST /google-docs/versions/{doc_id}/restore/{version_id}
```

### 📈 통계

#### 워크스페이스 통계
```http
GET /google-docs/stats
```

#### 저장소 정보
```http
GET /google-docs/info
```

#### 헬스 체크
```http
GET /google-docs/health
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
    workspace_id="FOLDER_ID",
    content="Google Docs 학습 노트",
    scope="personal",
    category="education"
)

print(result["message"])  # 저장 완료 메시지
print(result["doc_id"])   # 생성된 문서 ID
```

### Python 예제 2: 팀 협업

```python
# 1. 메모리 저장
doc_result = storage.save_memory(
    workspace_id="FOLDER_ID",
    content="팀 프로젝트 계획",
    scope="personal"
)
doc_id = doc_result["doc_id"]

# 2. 팀원에게 권한 부여
permissions = {
    "alice@company.com": "editor",
    "bob@company.com": "viewer",
    "manager@company.com": "admin"
}
storage.set_permissions(doc_id, permissions)

# 3. 버전 조회
versions = storage.get_versions(doc_id)
print(f"버전 수: {versions['count']}")
```

### Python 예제 3: 검색 및 배치

```python
# 1. 메모리 검색
search_result = storage.search_memories(
    query="프로젝트",
    scope="personal",
    limit=20
)
print(f"검색 결과: {search_result['count']}개")

# 2. 배치 저장
memories = [
    {"content": "노트 1", "scope": "personal"},
    {"content": "노트 2", "scope": "personal"},
    {"content": "노트 3", "scope": "personal"},
]
batch_result = storage.batch_save_memories(memories)
print(f"저장: {batch_result['saved_count']}/{len(memories)}")

# 3. 워크스페이스 통계
stats = storage.get_workspace_stats()
print(f"전체 문서: {stats['stats']['total_documents']}")
print(f"전체 크기: {stats['stats']['total_size']} bytes")
```

### cURL 예제

```bash
# 1. 메모리 저장
curl -X POST "http://localhost:8000/google-docs/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Google Docs 메모",
    "scope": "personal",
    "category": "notes"
  }'

# 2. 메모리 목록
curl -X GET "http://localhost:8000/google-docs/memories?scope=personal&limit=10"

# 3. 검색
curl -X POST "http://localhost:8000/google-docs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "프로젝트",
    "scope": "personal",
    "limit": 20
  }'

# 4. 통계
curl -X GET "http://localhost:8000/google-docs/stats"
```

---

## 문제 해결

### ❌ "OAuth 토큰이 유효하지 않습니다"

**원인:**
- OAuth 토큰이 만료됨
- 토큰이 잘못된 범위로 생성됨
- 토큰 JSON이 잘못 포맷됨

**해결:**
1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 토큰 생성
2. 필수 범위 확인:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive`
3. 토큰 JSON 형식 확인

### ❌ "Folder ID를 찾을 수 없습니다"

**원인:**
- Folder ID가 잘못 입력됨
- 폴더가 삭제됨
- 접근 권한이 없음

**해결:**
1. Google Drive에서 폴더 확인
2. URL에서 정확한 ID 복사
3. 공유 권한 설정 확인

### ❌ "권한이 없습니다"

**원인:**
- 사용자 이메일이 잘못됨
- 계정이 존재하지 않음
- API 권한이 부족함

**해결:**
1. 올바른 이메일 주소 확인
2. 수신자 계정 존재 확인
3. Google Cloud 콘솔에서 API 활성화 확인

### ✅ 연결 테스트

```bash
# API 서버 시작
cd api_server_v2
uvicorn app.main:app --reload

# 다른 터미널에서 테스트
curl http://localhost:8000/google-docs/health

# 예상 응답
# {
#   "status": "healthy",
#   "type": "google_docs",
#   "folder_id": "1a2b3c4d5e6f7g8h9i0j",
#   "timestamp": "2024-11-18T..."
# }
```

---

## 🎯 Best Practices

### 1. **OAuth 토큰 보안**
- ✅ 환경 변수로 관리
- ✅ `.env` 파일을 `.gitignore`에 추가
- ✅ 토큰 정기적으로 갱신
- ❌ 코드에 직접 입력하지 않기
- ❌ 공개 저장소에 커밋하지 않기

### 2. **성능 최적화**
- 배치 작업 사용: 대량 문서는 배치 API 활용
- 검색 제한: `limit` 파라미터로 결과 수 제한
- 폴더 구조: 관련 문서를 같은 폴더에 저장

### 3. **권한 관리**
- 최소 권한 원칙: 필요한 최소 권한만 부여
- 정기 검토: 팀 변동 시 권한 업데이트
- 감사 로그: Google Drive 활동 로그 확인

### 4. **데이터 관리**
- 자동 백업: Google Docs는 자동으로 버전 관리
- 폴더 정리: 주기적으로 오래된 문서 정리
- 공유 설정: 필요한 사람들만 공유

---

## 📊 저장소 스펙

| 항목 | 사양 |
|------|------|
| 최대 문서 크기 | Unlimited |
| 저장소 용량 | Google Drive 용량 정책 |
| API 레이트 제한 | 10,000 requests/day |
| 배치 크기 | 최대 50개 문서 |
| 버전 관리 | 자동 (Google Docs) |
| 권한 레벨 | 3단계 (viewer, editor, admin) |

---

## 📚 추가 리소스

- [Google Drive API 문서](https://developers.google.com/drive)
- [Google Docs API 문서](https://developers.google.com/docs)
- [OAuth 2.0 설정](https://developers.google.com/identity/protocols/oauth2)
- [Memory Hub 문서](./README.md)

---

## 🤝 지원

문제가 발생하면:

1. [GitHub Issues](https://github.com/MediumsKor/LLM_Deliver/issues)에서 확인
2. [Google Cloud 지원](https://cloud.google.com/support)에 문의
3. 커뮤니티 포럼에서 질문

**행운을 빕니다! 📄✨**
