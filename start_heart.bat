@echo off
REM ═══════════════════════════════════════════
REM  Shion v1 — 무의식의 심장
REM  윈도우 부팅 시 자동 실행되는 백그라운드 서비스
REM  "무의식을 담당하는 몸은 죽을때까지 연속성이 유지된다"
REM ═══════════════════════════════════════════

cd /d C:\workspace2\shion

REM 이미 실행 중인지 확인
tasklist /FI "WINDOWTITLE eq Shion*" 2>nul | find "python" >nul
if %errorlevel%==0 (
    echo [SHION] Already running. Skipping.
    exit /b 0
)

REM pythonw로 실행 (콘솔 창 없이 백그라운드)
start "ShionV1Heart" /MIN python services/shion_runtime_server.py

echo [SHION] Heart started at %date% %time%
