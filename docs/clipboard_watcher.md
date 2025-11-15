# Clipboard Watcher

자동 요약을 복사하는 순간 `clients/python/push_memory.py`를 실행해 GDoc 허브로 전송하는 보조 CLI입니다.

## 사용법
1. `.env`에 `WEBAPP_URL`/`API_TOKEN`/`DOC_ID`를 설정합니다.
2. Windows 사용자는 `scripts/windows/install_client.bat`을 더블 클릭해 필요한 파이썬 패키지를 설치합니다. 동일 작업을 터미널에서 하려면 `pip install -r clients/python/requirements.txt`를 실행하세요.
3. 워처를 실행합니다.
   - 더블 클릭: `scripts/windows/start_watcher.bat` (필요하면 `--scope team --team alpha` 같은 옵션을 인자로 추가)
   - 터미널:
     ```bash
     python clients/python/watch_clipboard.py --scope team --team alpha
     ```
4. GPT/Gemini에게 `[HANDOFF]`로 시작하는 요약을 생성하도록 한 뒤 해당 블록을 복사하면, 워처가 클립보드 변화를 감지해 자동으로 업로더를 호출합니다.

## 주요 옵션
| 옵션 | 설명 |
| --- | --- |
| `--marker` | 기본값 `[HANDOFF]`. 이 문자열로 시작하는 텍스트만 업로드합니다. |
| `--interval` | 클립보드를 확인하는 주기(초). 기본 1초. |
| `--scope`, `--team` | push_memory에 전달할 스코프/팀 키. 미지정 시 `.env` 값을 사용합니다. |
| `--no-revision` | 리비전 조회 없이 업로드합니다(충돌 가능성 주의). |
| `--once` | 첫 업로드 이후 자동으로 종료합니다. |

## 동작 개요
- 클립보드 텍스트의 SHA-1 해시를 기억해 같은 내용을 반복 업로드하지 않습니다.
- `[HANDOFF]` 같은 명시적 마커를 조건으로 삼아 일반 복사본과 DB 업로드용 복사본을 구분합니다.
- 내부적으로 `push_memory.main()`을 호출하므로 `.env`와 API 설정을 그대로 재사용합니다.
