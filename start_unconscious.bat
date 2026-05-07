@echo off
cd /d %~dp0
chcp 65001 >nul
title Shion AGI Stack

set "PULSE_MODE=Visible"
if /I "%~1"=="hidden" set "PULSE_MODE=Hidden"
if /I "%~1"=="auto-hidden" set "PULSE_MODE=Hidden"
if /I "%~1"=="auto" set "PULSE_MODE=Hidden"
if /I "%~1"=="auto-visible" set "PULSE_MODE=Visible"

echo ============================================
echo   Shion AGI Stack - Auto Recovery
echo ============================================
echo   mode: %PULSE_MODE%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_agi_stack.ps1" -PulseMode %PULSE_MODE%

if /I "%~1" NEQ "auto" if /I "%~1" NEQ "auto-hidden" if /I "%~1" NEQ "auto-visible" (
    echo.
    echo 완료. 이 창은 닫아도 됩니다.
    pause
)
