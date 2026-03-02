@echo off
chcp 65001 >nul
title 🫀 Shion Unconscious System

echo ============================================
echo   Shion Unconscious System - Auto Recovery
echo ============================================
echo.

:: ─── 1단계: 심장 시작 (LLM 서버) ───
echo [1/3] 심장(LLM 서버) 확인 중...

tasklist /FI "WINDOWTITLE eq Shion*Heart*" 2>nul | find "python" >nul
if %errorlevel%==0 (
    echo    심장이 이미 뛰고 있습니다.
) else (
    echo    심장 시작 중...
    start "Shion Heart" /MIN pythonw services\shion_runtime_server.py
    echo    심장 시작됨.
)

:: ─── 2단계: 심장 대기 ───
echo.
echo [2/3] 심장이 뛰는지 확인 중...

set WAIT=0
:wait_loop
if %WAIT% GEQ 30 (
    echo    경고: 심장 응답 없음. 맥박만 시작합니다.
    goto start_pulse
)

powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2 -UseBasicParsing; if($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo    심장 확인 완료!
    goto start_pulse
)

set /A WAIT+=3
echo    대기 중... %WAIT%/30초
timeout /t 3 /nobreak >nul
goto wait_loop

:: ─── 3단계: 맥박 루프 (크래시 자동 복구) ───
:start_pulse
echo.
echo [3/3] 맥박(Pulse Loop) 시작 - 크래시 시 자동 재시작
echo.

:pulse_loop
echo [%date% %time%] 맥박 시작...
python core\shion_minimal.py

echo.
echo [%date% %time%] 맥박 중단 감지! 30초 후 재시작...
echo    (Ctrl+C로 완전 종료)
timeout /t 30 /nobreak >nul
echo 맥박 재시작 중...
goto pulse_loop
