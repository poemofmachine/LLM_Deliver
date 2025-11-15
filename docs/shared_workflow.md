# Shared Workflow (GDoc Memory Hub)

## 목적
- 개인용 문서 1개 + 팀별 문서 다수를 하나의 Apps Script로 관리합니다.
- 실시간 동기화 없이 “세션 시작 → 작업 → 종료 동기화” 루틴만으로 협업합니다.
- 자동 카테고리 태깅과 카테고리 기반 조회로 중구난방한 정보를 빠르게 재사용합니다.

## 문서 구성 / 스크립트 속성
| 속성 | 예시 값 | 설명 |
| --- | --- | --- |
| `DOC_ID_PERSONAL` | `1Abc...` | 개인 전용 GDoc ID (없으면 `code.gs`의 `DOC_ID` 사용) |
| `TEAM_MAP` | `{"alpha":"1DocA","beta":"1DocB"}` | 팀 키 → 팀 문서 ID JSON. 팀 키는 UI/클라이언트에서 표시됩니다. |
| `API_TOKEN` | `C_SECRET_1234` | API 인증 토큰 |

> 팀 스코프를 사용할 때 `team_key`를 지정하면 매핑된 문서를 사용합니다. 키를 지정하지 않았고 맵에 하나만 등록되어 있다면 그 값이 자동 선택됩니다.

## 세션 절차
1. **세션 시작**  
   - UI 또는 API로 `scope`(personal/team) 및 `team`(팀 키)을 지정해 `GET /?mode=json&...`을 호출합니다.  
   - 응답에는 `revision_id`, `last_updated`, `doc_url`, `categories`가 포함됩니다.
2. **로컬 작업**  
   - [HANDOFF] 블록을 작성하면 서버가 자동으로 `[AUTO_CATEGORY]` 라인을 삽입합니다(회의/버그/리서치 등 키워드 기반).  
   - 별도 카테고리를 쓰고 싶으면 직접 `[AUTO_CATEGORY] CUSTOM`을 적어두어도 됩니다.
3. **세션 종료**  
   - `POST /?key=TOKEN&revision=<id>&scope=...&team=...`으로 업로드합니다.  
   - 리비전이 다르면 `status=CONFLICT`, 누락되면 `status=MISSING_REVISION`.
4. **카테고리 조회**  
   - `GET ...&category=MEETING`처럼 `category` 파라미터를 넘기면 해당 카테고리를 가진 최신 블록만 반환합니다(`matched_category` 필드 제공).

## UI 사용법 (`api_server/ui.html`)
- 상단 “개인용/팀용” 토글과 팀 선택 드롭다운으로 대상 문서를 선택합니다.  
- **[최신 상태 불러오기]**를 누르면 선택된 문서의 리비전/업데이트 시간/링크가 표시됩니다.  
- 저장 시 `syncHandoff(text, revision, scope, teamKey)`를 호출하여 API와 동일한 검증을 거치며, 응답의 자동 카테고리 목록이 화면에 표시됩니다.

## Python 클라이언트 (`clients/python/fetch_memory.py`)
- `.env` 예시:
  ```
  WEBAPP_URL=https://script.google.com/macros/s/XXX/exec
  API_TOKEN=C_SECRET_1234
  SCOPE=team            # personal | team
  TEAM_KEY=alpha        # team 스코프일 때 필수
  CATEGORY_FILTER=MEETING
  ```
- 실행하면 `/examples/handoff_*.md`에 스냅샷을 저장하고, 이전 리비전과 비교해 변경 여부를 알려줍니다.  
- `CATEGORY_FILTER`가 설정되면 해당 카테고리를 가진 최신 블록만 가져옵니다.
- 테스트: `python -m unittest clients/python/tests/test_conflict_flow.py`

## API 파라미터 요약
| 파라미터 | 설명 |
| --- | --- |
| `scope` | `personal` (기본) 또는 `team` |
| `team` 또는 `team_key` | 팀 스코프일 때 사용할 문서 키 |
| `category` | 특정 카테고리를 가진 최신 블록만 조회 |
| `revision` | `POST` 시 필수. 충돌 방지용 리비전 값 |

## 엣지 케이스 & 팁
- **UNKNOWN_TEAM**: `TEAM_MAP`에 없는 키를 요청한 경우. 스크립트 속성을 확인하세요.
- **자동 태깅 보정**: 카테고리가 잘못 지정되면 입력 텍스트에 원하는 키워드를 추가하거나 `[AUTO_CATEGORY]` 라인을 직접 작성하세요.
- **충돌 반복**: 팀 단위 협업 시 저장 전에 항상 “최신 상태 불러오기”를 눌러 리비전과 팀 선택을 다시 확인하세요.
- 추가 CLI 업로더: `python clients/python/push_memory.py --clipboard`로 클립보드 내용을 바로 업로드하거나 `--file handoff.txt`로 파일을 업로드할 수 있습니다. 팀 스코프가 필요하면 `--scope team --team alpha`를 함께 전달하세요.
