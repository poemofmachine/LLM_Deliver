@echo off
setlocal
cd /d "%~dp0\..\.."
echo 클립보드 워처를 시작합니다. 종료하려면 창을 닫거나 Ctrl+C를 누르세요.
python clients/python/watch_clipboard.py %*
pause
