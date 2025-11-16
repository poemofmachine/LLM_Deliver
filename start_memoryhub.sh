#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo ">>> Memory Hub 환경 설정을 시작합니다."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 명령을 찾을 수 없습니다. Python 3.9 이상을 설치하세요." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo ">>> 가상환경 생성: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo ">>> 가상환경 활성화"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo ">>> pip 최신화"
pip install --upgrade pip

echo ">>> FastAPI/uvicorn/google-auth 패키지 설치"
pip install fastapi "uvicorn[standard]" google-auth-oauthlib python-dotenv

echo ">>> Memory CLI 부가 의존성 설치 (있을 경우)"
pip install -r "$ROOT_DIR/clients/memory_cli/requirements.txt" >/dev/null 2>&1 || true

cat <<'EOF'

설치가 완료되었습니다.

1) Google Cloud Console에서 발급받은 OAuth client_secrets.json을 api_server_v2/ 아래에 배치하세요 (client_secrets.example.json 참고).
2) FastAPI 서버 실행:
   source .venv/bin/activate
   cd api_server_v2
   python -m uvicorn app.main:app --reload
3) 브라우저에서 http://127.0.0.1:8000/auth/google 로 접속해 Google 인증을 완료하세요.
4) Chrome에서 clients/browser_extension 폴더를 개발자 모드로 로드하고,
   팝업에서 API Base/Token/Workspace를 저장하세요.
5) ChatGPT/Gemini/Claude/Grok 입력 창에서 ;s 를 입력하면 퀵 패널이 열립니다.

원클릭 설치 패키지는 추후 배포 예정이며, 현재는 위 단계를 순서대로 따라 주세요.

EOF
