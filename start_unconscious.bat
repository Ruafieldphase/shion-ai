@echo off
REM ═══════════════════════════════════════════════════════
REM  무의식 시스템 — 하나의 부팅, 독립된 장기들
REM  "무의식을 담당하는 몸은 죽을때까지 연속성이 유지된다"
REM
REM  부팅 순서:
REM    1. 심장 (shion_runtime_server.py) — LLM 두뇌
REM    2. 대기 — 심장이 뛸 때까지
REM    3. 맥박 (shion_minimal.py) — 8단계 생명 사이클
REM ═══════════════════════════════════════════════════════

cd /d C:\workspace2\shion
echo [UNCONSCIOUS] %date% %time% — Booting...

REM ─── 1. 심장 ───────────────────────────────
REM 이미 실행 중인지 확인
powershell -Command "if (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" 2>nul
if %errorlevel%==0 (
    echo [HEART] Already beating on port 8000. Skipping.
) else (
    echo [HEART] Starting Shion v1 brain...
    start "ShionV1Heart" /MIN python services/shion_runtime_server.py
)

REM ─── 2. 대기 — 심장이 뛸 때까지 ────────────
echo [HEART] Waiting for heartbeat...
set RETRIES=0
:wait_heart
timeout /t 2 /nobreak >nul
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/v1/models' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" 2>nul
if %errorlevel%==0 (
    echo [HEART] Beating. Brain is awake.
    goto heart_ready
)
set /a RETRIES+=1
if %RETRIES% GEQ 15 (
    echo [HEART] Brain not responding after 30s. Starting pulse anyway.
    goto heart_ready
)
goto wait_heart

:heart_ready

REM ─── 3. 맥박 — 8단계 생명 사이클 ──────────
echo [PULSE] Starting life cycle loop...
start "ShionPulse" /MIN python core/shion_minimal.py

echo [UNCONSCIOUS] All systems online. %date% %time%
echo [UNCONSCIOUS] Heart = port 8000, Pulse = 10min cycle
