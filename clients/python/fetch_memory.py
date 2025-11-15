import os
import json
import datetime
import pathlib
import urllib.request
import urllib.parse

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback when python-dotenv is absent
    def load_dotenv():
        return False

# 1. .env 파일 로드
load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
API_TOKEN = os.getenv("API_TOKEN")
REVISION_CACHE_PATH = pathlib.Path("clients/python/.revision_cache")

SKIP_KEYS = {"parsed_at", "revision_id", "last_updated", "doc_url"}


def request_handoff_json(webapp_url, token):
    params = {'mode': 'json', 'key': token}
    url = f"{webapp_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url) as r:
            response_text = r.read().decode("utf-8")
            if not response_text.startswith('{'):
                raise json.JSONDecodeError("Response was not JSON", response_text, 0)
            data = json.loads(response_text)
            if data.get("error"):
                raise RuntimeError(f"API 오류: {data['error']}")
            return data
    except json.JSONDecodeError as e:
        raise RuntimeError(f"API 호출 실패(JSON 오류): {e}") from e
    except Exception as e:
        raise RuntimeError(f"API 호출 실패: {e}") from e


def build_markdown(data, timestamp):
    content = [f"# HANDOFF Snapshot ({timestamp})"]
    parsed_at = data.get("parsed_at")
    last_updated = data.get("last_updated")
    revision_id = data.get("revision_id")
    doc_url = data.get("doc_url")

    meta_line = []
    if parsed_at:
        meta_line.append(f"Parsed at: {parsed_at}")
    if last_updated:
        meta_line.append(f"GDoc Last Updated: {last_updated}")
    if revision_id:
        meta_line.append(f"Revision: {revision_id}")
    if meta_line:
        content.append(f"*({' | '.join(meta_line)})*\n")
    if doc_url:
        content.append(f"[원문 문서 열기]({doc_url})\n")

    for key, value in data.items():
        if key in SKIP_KEYS or key is None:
            continue
        if key == "parsed_at":
            continue
        if key == "Source Link":
            content.append(f"## {key}\n- {value}\n")
        else:
            content.append(f"## {key}\n{value}\n")
    return "\n".join(content)


def read_cached_revision():
    try:
        return REVISION_CACHE_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def write_cached_revision(revision_id):
    if not revision_id:
        return
    REVISION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVISION_CACHE_PATH.write_text(revision_id, encoding="utf-8")


def describe_revision_change(previous, current):
    if not current:
        return "Revision 정보를 가져오지 못했습니다."
    if not previous:
        return f"최초 동기화 완료 (Revision: {current})."
    if previous == current:
        return "변경 사항 없음 — 문서는 마지막 스냅샷과 동일합니다."
    return f"새 리비전 감지: {current} (이전: {previous})"


def main():
    if not all([WEBAPP_URL, API_TOKEN]):
        print("오류: .env 파일에 WEBAPP_URL, API_TOKEN이 모두 설정되어야 합니다.")
        return

    print("v2.2 API 서버(JSON 모드)에서 최신 데이터를 가져오는 중...")
    data = request_handoff_json(WEBAPP_URL, API_TOKEN)

    revision_message = describe_revision_change(read_cached_revision(), data.get("revision_id"))
    print(revision_message)

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = pathlib.Path(f"examples/handoff_{ts}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_markdown(data, ts), encoding="utf-8")

    write_cached_revision(data.get("revision_id"))
    print(f"성공! '{out_path}' 파일에 최신 핸드오프가 저장되었습니다.")


if __name__ == "__main__":
    main()
