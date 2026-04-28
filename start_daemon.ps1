# 자율 오케스트레이터 데몬 시작/중단 스크립트
# ============================================
# 
# 시작:  .\start_daemon.ps1
# 중단:  .\start_daemon.ps1 -Stop
# 상태:  .\start_daemon.ps1 -Status

param(
    [switch]$Stop,
    [switch]$Status
)

$DaemonScript = "c:\workspace2\shion\core\orchestrator_daemon.py"
$StopFile = "c:\workspace2\shion\outputs\orchestrator_daemon.stop"
$LogFile = "c:\workspace2\shion\outputs\daemon.log"
$PidFile = "c:\workspace2\shion\outputs\daemon.pid"

if ($Stop) {
    Write-Host "🛑 데몬 중단 요청..." -ForegroundColor Yellow
    "" | Out-File -FilePath $StopFile -Encoding utf8
    Write-Host "   stop 파일 생성: $StopFile"
    Write-Host "   다음 체크 시 (최대 10초 내) 자동 종료됩니다."
    return
}

if ($Status) {
    Write-Host "📊 데몬 상태:" -ForegroundColor Cyan
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "   ✅ 실행 중 (PID: $pid)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ PID $pid 프로세스 없음" -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ PID 파일 없음" -ForegroundColor Red
    }
    
    if (Test-Path $LogFile) {
        Write-Host "`n   최근 로그:"
        Get-Content $LogFile -Tail 10
    }
    return
}

# 시작
Write-Host "🎯 자율 오케스트레이터 데몬 시작" -ForegroundColor Green
Write-Host "   30분마다 3사이클 실행 (비용: 0원)"
Write-Host "   중단: .\start_daemon.ps1 -Stop"
Write-Host "   상태: .\start_daemon.ps1 -Status"
Write-Host "   로그: $LogFile"
Write-Host ""

# 백그라운드 실행
$proc = Start-Process -FilePath "pythonw" `
    -ArgumentList $DaemonScript `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Out-File -FilePath $PidFile -Encoding utf8

Write-Host "   ✅ 시작됨 (PID: $($proc.Id))" -ForegroundColor Green
Write-Host "   pythonw으로 백그라운드 실행 중"
