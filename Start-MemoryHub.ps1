#requires -version 5.0

Write-Host ">>> Memory Hub 환경 설정을 시작합니다." -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python 명령을 찾을 수 없습니다. Python 3.9 이상을 설치하세요."
    exit 1
}

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RootDir ".venv"

if (-not (Test-Path $VenvDir)) {
    Write-Host ">>> 가상환경 생성: $VenvDir" -ForegroundColor Yellow
    python -m venv $VenvDir
}

Write-Host ">>> 가상환경 활성화" -ForegroundColor Yellow
& "$VenvDir\Scripts\Activate.ps1"

Write-Host ">>> pip 최신화" -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ">>> FastAPI/uvicorn/google-auth 패키지 설치" -ForegroundColor Yellow
pip install fastapi "uvicorn[standard]" google-auth-oauthlib python-dotenv

if (Test-Path "$RootDir\clients\memory_cli\requirements.txt") {
    Write-Host ">>> Memory CLI 부가 의존성 설치" -ForegroundColor Yellow
    pip install -r "$RootDir\clients\memory_cli\requirements.txt"
}

Write-Host @"

설치가 완료되었습니다.

1) Google Cloud Console에서 발급받은 OAuth client_secrets.json을 api_server_v2\ 폴더에 복사하세요. (client_secrets.example.json 참고)
2) FastAPI 서버 실행:
   $env:VIRTUAL_ENV\Scripts\Activate.ps1
   cd api_server_v2
   python -m uvicorn app.main:app --reload
3) 브라우저에서 http://127.0.0.1:8000/auth/google 에 접속해 Google 인증을 완료하세요.
4) Chrome에서 clients\browser_extension 폴더를 개발자 모드로 로드하고,
   팝업에서 API Base/Token/Workspace를 저장하세요.
5) ChatGPT/Gemini/Claude/Grok 입력창에서 ';s' 를 입력하면 퀵 패널이 열립니다.

원클릭 설치 패키지는 추후 제공 예정이며, 현재는 위 단계를 순서대로 따라 주세요.
"@
