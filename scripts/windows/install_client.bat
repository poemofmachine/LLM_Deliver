@echo off
setlocal
cd /d "%~dp0\..\.."
echo Installing Python dependencies from clients/python/requirements.txt ...
python -m pip install -r clients/python/requirements.txt
if errorlevel 1 (
    echo 설치 중 오류가 발생했습니다.
    exit /b 1
)
echo 설치가 완료되었습니다.
