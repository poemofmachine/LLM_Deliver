"""Clipboard watcher that auto-runs push_memory when a marker appears."""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from typing import Optional, Sequence

try:
    import pyperclip
except Exception:  # pragma: no cover - clipboard optional
    pyperclip = None

try:
    import push_memory
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("push_memory.py를 찾을 수 없습니다.") from exc


DEFAULT_MARKER = "[HANDOFF]"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="클립보드를 감시하다가 특정 패턴이 보이면 push_memory CLI를 실행합니다.",
    )
    parser.add_argument(
        "--marker",
        default=DEFAULT_MARKER,
        help=f"이 문자열로 시작하면 업로드합니다 (기본: {DEFAULT_MARKER})",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="클립보드 확인 주기(초)")
    parser.add_argument("--scope", type=str, help="push_memory에 전달할 scope (personal/team)")
    parser.add_argument("--team", type=str, help="팀 스코프에서 사용할 팀 키")
    parser.add_argument("--no-revision", action="store_true", help="push_memory에 --no-revision 전달")
    parser.add_argument(
        "--once",
        action="store_true",
        help="첫 업로드 이후 종료합니다 (기본은 계속 실행)",
    )
    return parser.parse_args(argv)


def read_clipboard_text() -> str:
    if not pyperclip:
        raise RuntimeError("pyperclip 모듈이 없습니다. pip install pyperclip 로 설치하세요.")
    text = pyperclip.paste()
    return text or ""


def matches_marker(text: str, marker: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and stripped.startswith(marker.strip())


def build_push_args(scope: Optional[str], team: Optional[str], no_revision: bool) -> list[str]:
    push_args = ["--clipboard"]
    if scope:
        push_args += ["--scope", scope]
    if team:
        push_args += ["--team", team]
    if no_revision:
        push_args.append("--no-revision")
    return push_args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        text = read_clipboard_text()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    last_hash = hashlib.sha1(text.encode("utf-8")).hexdigest() if text else ""
    push_args = build_push_args(args.scope, args.team, args.no_revision)
    print(
        f"[watcher] marker='{args.marker}' interval={args.interval}s "
        f"scope={args.scope or 'env default'} team={args.team or '-'}"
    )
    if args.once:
        print("[watcher] once 모드: 업로드 1회 후 종료합니다.")

    uploads = 0
    try:
        while True:
            try:
                current = read_clipboard_text()
            except RuntimeError as exc:
                print(f"[watcher] 클립보드 오류: {exc}", file=sys.stderr)
                time.sleep(args.interval)
                continue

            digest = hashlib.sha1(current.encode("utf-8")).hexdigest() if current else ""
            if digest and digest != last_hash and matches_marker(current, args.marker):
                print("[watcher] 트리거 감지. push_memory 실행 중...")
                code = push_memory.main(push_args)
                if code == 0:
                    uploads += 1
                    last_hash = digest
                    print(f"[watcher] 업로드 완료({uploads}회).")
                    if args.once:
                        break
                else:
                    print("[watcher] push_memory 실패. 재시도하려면 텍스트를 다시 복사하세요.", file=sys.stderr)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[watcher] 종료합니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
