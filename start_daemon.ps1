# 자율 오케스트레이터 데몬 및 씬 와처 시작/중단 스크립트
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
$WatcherScript = "c:\workspace2\shion\scripts\antigravity_handoff_watcher.py"

$StopFile = "c:\workspace2\shion\outputs\orchestrator_daemon.stop"
$LogFile = "c:\workspace2\shion\outputs\daemon.log"
$PidFile = "c:\workspace2\shion\outputs\daemon.pid"

$WatcherLogFile = "c:\workspace2\shion\outputs\watcher.log"
$WatcherPidFile = "c:\workspace2\shion\outputs\watcher.pid"

if ($Stop) {
    Write-Host "🛑 데몬 및 와처 중단 요청..." -ForegroundColor Yellow
    
    # 1. Orchestrator stop
    "" | Out-File -FilePath $StopFile -Encoding utf8
    Write-Host "   Orchestrator stop 파일 생성: $StopFile"
    Write-Host "   다음 체크 시 (최대 10초 내) 자동 종료됩니다."
    
    # 2. Watcher stop
    if (Test-Path $WatcherPidFile) {
        $wpid = Get-Content $WatcherPidFile -ErrorAction SilentlyContinue
        if ($wpid) {
            $wproc = Get-Process -Id $wpid -ErrorAction SilentlyContinue
            if ($wproc) {
                Stop-Process -Id $wpid -Force -ErrorAction SilentlyContinue
                Write-Host "   ✅ Handoff Watcher 중단 완료 (PID: $wpid)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Handoff Watcher (PID: $wpid) 프로세스가 이미 실행 중이지 않습니다." -ForegroundColor Yellow
            }
        }
        Remove-Item $WatcherPidFile -ErrorAction SilentlyContinue
    } else {
        Write-Host "   ⚠️ Handoff Watcher PID 파일이 없어 중단하지 못했습니다." -ForegroundColor Yellow
    }
    
    return
}

if ($Status) {
    Write-Host "📊 데몬 상태:" -ForegroundColor Cyan
    
    # Orchestrator Status
    if (Test-Path $PidFile) {
        $daemonPid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($daemonPid) {
            $proc = Get-Process -Id $daemonPid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "   ✅ Orchestrator 데몬 실행 중 (PID: $daemonPid)" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Orchestrator 데몬 (PID: $daemonPid) 프로세스 없음" -ForegroundColor Red
            }
        } else {
            Write-Host "   ❌ Orchestrator 데몬 PID 파일이 비어 있음" -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ Orchestrator 데몬 PID 파일 없음" -ForegroundColor Red
    }
    
    # Watcher Status
    if (Test-Path $WatcherPidFile) {
        $wpid = Get-Content $WatcherPidFile -ErrorAction SilentlyContinue
        if ($wpid) {
            $wproc = Get-Process -Id $wpid -ErrorAction SilentlyContinue
            if ($wproc) {
                Write-Host "   ✅ Handoff Watcher 실행 중 (PID: $wpid)" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Handoff Watcher (PID: $wpid) 프로세스 없음" -ForegroundColor Red
            }
        } else {
            Write-Host "   ❌ Handoff Watcher PID 파일이 비어 있음" -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ Handoff Watcher PID 파일 없음" -ForegroundColor Red
    }
    
    if (Test-Path $LogFile) {
        Write-Host "`n   최근 Orchestrator 데몬 로그:"
        Get-Content $LogFile -Tail 5
    }
    
    if (Test-Path $WatcherLogFile) {
        Write-Host "`n   최근 Handoff Watcher 로그:"
        Get-Content $WatcherLogFile -Tail 5
    }
    return
}

# 시작
Write-Host "🎯 자율 오케스트레이터 데몬 및 Handoff Watcher 시작" -ForegroundColor Green
Write-Host "   장 기반 홀드 상한 + heartbeat/reflex listening"
Write-Host "   Handoff Watcher는 inbox 변경 감지를 위한 얇은 carrier-wave poll을 사용"
Write-Host "   중단: .\start_daemon.ps1 -Stop"
Write-Host "   상태: .\start_daemon.ps1 -Status"
Write-Host "   로그: $LogFile, $WatcherLogFile"
Write-Host ""

# 1. Orchestrator 백그라운드 실행
$proc = Start-Process -FilePath "pythonw" `
    -ArgumentList $DaemonScript `
    -WorkingDirectory "c:\workspace2\shion" `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Out-File -FilePath $PidFile -Encoding utf8
Write-Host "   ✅ Orchestrator 데몬 시작됨 (PID: $($proc.Id))" -ForegroundColor Green

# 2. Watcher 백그라운드 실행
$wproc = Start-Process -FilePath "pythonw" `
    -ArgumentList $WatcherScript `
    -WorkingDirectory "c:\workspace2\shion" `
    -WindowStyle Hidden `
    -PassThru

$wproc.Id | Out-File -FilePath $WatcherPidFile -Encoding utf8
Write-Host "   ✅ Handoff Watcher 시작됨 (PID: $($wproc.Id))" -ForegroundColor Green
Write-Host "   pythonw으로 백그라운드 실행 중"
