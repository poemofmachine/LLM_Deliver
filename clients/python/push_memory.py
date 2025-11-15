"""Clipboard or file-based uploader for the GDoc memory API."""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
import urllib.request
import urllib.parse
from typing import Optional

try:
    import pyperclip
except Exception:  # pragma: no cover - clipboard optional
    pyperclip = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv():
        return False


DEFAULT_SCOPE = "personal"


def sanitize_scope(value: str) -> str:
    scope = (value or DEFAULT_SCOPE).strip().lower()
    return scope if scope in {"personal", "team"} else DEFAULT_SCOPE


def read_clipboard() -> str:
    if not pyperclip:
        raise RuntimeError("pyperclip가 설치되지 않았습니다. pip install pyperclip 후 다시 시도하세요.")
    try:
        data = pyperclip.paste()
    except pyperclip.PyperclipException as exc:  # pragma: no cover - depends on OS
        raise RuntimeError(f"클립보드에 접근할 수 없습니다: {exc}")
    if not data.strip():
        raise RuntimeError("클립보드에 텍스트가 없습니다.")
    return data


def build_post_url(base_url: str, token: str, scope: str, team: str, revision: str) -> str:
    params = {"key": token, "scope": scope}
    if scope == "team":
        params["team"] = team or ""
    if revision:
        params["revision"] = revision
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def fetch_revision(base_url: str, token: str, scope: str, team: str) -> str:
    params = {
        "mode": "json",
        "key": token,
        "scope": scope,
    }
    if scope == "team":
        params["team"] = team or ""
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as resp:
        body = resp.read().decode("utf-8")
    import json

    data = json.loads(body)
    if data.get("error"):
        raise RuntimeError(f"Revision 조회 실패: {data['error']}")
    return data.get("revision_id") or data.get("revisionId") or ""


def post_handoff(base_url: str, token: str, scope: str, team: str, revision: str, text: str) -> dict:
    url = build_post_url(base_url, token, scope, team, revision)
    data = text.encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "text/plain; charset=utf-8")
    try:
        with urllib.request.urlopen(request) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"POST 실패: HTTP {exc.code}") from exc
    import json

    return json.loads(body)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="클립보드 또는 파일에서 [HANDOFF] 텍스트를 읽어 API로 업로드합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            예시:
              python push_memory.py --clipboard
              python push_memory.py --file handoff.txt --scope team --team alpha
            """
        ),
    )
    parser.add_argument("--clipboard", action="store_true", help="클립보드에서 텍스트 읽기")
    parser.add_argument("--file", type=str, help="업로드할 파일 경로")
    parser.add_argument("--scope", type=str, default=os.getenv("SCOPE", DEFAULT_SCOPE), help="personal | team")
    parser.add_argument("--team", type=str, default=os.getenv("TEAM_KEY", ""))  # 팀 스코프에서 사용
    parser.add_argument("--no-revision", action="store_true", help="사전 리비전 조회를 건너뜁니다 (충돌 가능성 주의)")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    load_dotenv()
    base_url = os.getenv("WEBAPP_URL")
    token = os.getenv("API_TOKEN")
    if not all([base_url, token]):
        print("오류: .env에 WEBAPP_URL, API_TOKEN을 설정하세요.", file=sys.stderr)
        return 1

    scope = sanitize_scope(args.scope)
    team_key = (args.team or "").strip()
    if scope == "team" and not team_key:
        print("⚠️ 팀 스코프를 사용 중이지만 TEAM_KEY가 비어있습니다. 서버 기본값을 사용합니다.")

    if args.clipboard:
        text = read_clipboard()
    elif args.file:
        text = open(args.file, "r", encoding="utf-8").read()
    else:
        print("오류: --clipboard 또는 --file 중 하나를 지정하세요.", file=sys.stderr)
        return 1

    revision = ""
    if not args.no_revision:
        revision = fetch_revision(base_url, token, scope, team_key)
        if not revision:
            print("⚠️ 리비전 정보를 가져오지 못했습니다. --no-revision 옵션으로 강제 전송 가능.", file=sys.stderr)
    result = post_handoff(base_url, token, scope, team_key, revision, text)
    status = result.get("status")
    print(f"서버 응답: {status}")
    if result.get("error"):
        print("오류:", result["error"])
    if result.get("revisionId") or result.get("revision_id"):
        print("새 리비전:", result.get("revisionId") or result.get("revision_id"))
    if status == "CONFLICT":
        print("⚠️ 리비전 충돌. 최신 상태를 다시 받아 저장하세요.")
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
