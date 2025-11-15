# Shared Workflow (GDoc Memory Hub)

## 목적
여러 사용자가 하나의 Google Doc 메모리를 공유하면서, 세션 시작/종료 시점에만 동기화하여 협업할 수 있도록 하는 절차입니다. 실시간 편집은 지원하지 않지만, 리비전 체크와 충돌 감지를 통해 서로의 변경 사항을 안전하게 병합합니다.

## 세션 절차
1. **세션 시작**: UI 또는 API `GET /?mode=json&key=TOKEN`으로 최신 내용을 불러옵니다. 응답에는 `revision_id`, `last_updated`, `doc_url`이 포함됩니다.
2. **로컬 작업**: 받은 내용을 기반으로 로컬에서 작업하며, 작성하는 [HANDOFF] 블록에는 담당자·세션 요약을 포함합니다.
3. **세션 종료(업로드)**: `POST /?key=TOKEN&revision=<id>`로 블록을 업로드합니다. 서버는 `revision` 값으로 최신 여부를 검증하고, 성공 시 새 리비전을 발급합니다.
4. **충돌 처리**: 서버가 `status=CONFLICT`를 반환하면 다시 `GET`을 호출해 최신 리비전을 가져오고 변경 내용을 병합한 뒤 재전송합니다.

## API 메모
- `GET`: JSON 응답 상단에 `revision_id`, `last_updated`, `doc_url`(문서 링크)이 포함됩니다.
- `POST`: 필수 파라미터 `revision`를 전달해야 하며, 값이 누락되면 `status=MISSING_REVISION`이, 불일치 시 `status=CONFLICT`가 반환됩니다.
- 서버는 저장 시 `LockService`로 동시성을 제어하고 성공 시마다 새로운 리비전 UUID를 발급합니다.

## UI 사용법 (api_server/ui.html)
- 페이지 진입 시 **[최신 상태 불러오기]**로 메타데이터를 먼저 동기화합니다.
- 저장 시 UI가 서버 함수 `syncHandoff(text, revisionId)`를 호출하여 API와 동일한 검증을 거칩니다.
- 충돌·락 타임아웃·리비전 누락 등 상태 메시지가 노출되며, 필요한 경우 자동으로 재동기화를 유도합니다.

## Python 클라이언트 (clients/python/fetch_memory.py)
- `.env`에 `WEBAPP_URL`, `API_TOKEN`을 설정하고 실행하면 `/examples` 아래에 최신 핸드오프 스냅샷을 저장합니다.
- 최근 리비전은 `clients/python/.revision_cache`에 저장되어, 변경 여부를 출력 메시지로 확인할 수 있습니다.
- 테스트: `python -m unittest clients/python/tests/test_conflict_flow.py` 실행 시 JSON 응답 파서와 리비전 비교 로직이 검증됩니다.

## 엣지 케이스 제안
- **잘못된 토큰**: `error: UNAUTHORIZED`를 확인하고 토큰 갱신.
- **충돌 반복**: 업로드 전 항상 [최신 상태 불러오기]를 눌러 리비전 동기화.
- **대량 변경**: [HANDOFF] 블록을 모듈 단위로 나눠 작성해 충돌 시 병합 부담을 줄입니다.
