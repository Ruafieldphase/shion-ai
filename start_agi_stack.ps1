param(
    [ValidateSet("Hidden", "Visible")]
    [string]$PulseMode = "Visible",
    [switch]$Status
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Outputs = Join-Path $Root "outputs"
$StackLog = Join-Path $Outputs "agi_stack_startup.log"
$HeartOutLog = Join-Path $Outputs "shion_runtime_server.out.log"
$HeartErrLog = Join-Path $Outputs "shion_runtime_server.err.log"

New-Item -ItemType Directory -Path $Outputs -Force | Out-Null

function Write-StackLog {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $StackLog -Value $line -Encoding UTF8
    Write-Host $Message
}

function Test-Http {
    param(
        [string]$Uri,
        [int]$TimeoutSec = 2
    )
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec $TimeoutSec
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
    } catch {
        return $false
    }
}

function Wait-Http {
    param(
        [string]$Uri,
        [int]$Seconds,
        [string]$Label
    )
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Http -Uri $Uri -TimeoutSec 2) {
            Write-StackLog "OK: $Label responded."
            return $true
        }
        Start-Sleep -Seconds 3
    }
    Write-StackLog "WARN: $Label did not respond within ${Seconds}s."
    return $false
}

function Get-CommandLineProcess {
    param([string]$Pattern)
    Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -and
        $_.CommandLine -match $Pattern -and
        $_.Name -notmatch "^(powershell|pwsh)(\.exe)?$"
    }
}

function Show-Status {
    Write-StackLog "STATUS: checking AGI stack."
    Get-CommandLineProcess "orchestrator_daemon.py|shion_runtime_server.py|ollama(.exe)?\s+serve" |
        Select-Object ProcessId, Name, CommandLine |
        Format-Table -AutoSize
    Write-Host ""
    Write-Host ("Ollama 11434: " + ($(if (Test-Http "http://127.0.0.1:11434/api/tags") { "OK" } else { "DOWN" })))
    Write-Host ("Shion heart 8000: " + ($(if (Test-Http "http://127.0.0.1:8000/health") { "OK" } else { "DOWN" })))
}

function Ensure-Ollama {
    if (Test-Http "http://127.0.0.1:11434/api/tags") {
        Write-StackLog "OK: Ollama already responding on 11434."
        return
    }

    $cmd = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-StackLog "WARN: ollama executable not found. Continuing without Ollama."
        return
    }

    $existing = Get-CommandLineProcess "ollama(.exe)?\s+serve"
    if (-not $existing) {
        Write-StackLog "START: Ollama serve."
        Start-Process -FilePath $cmd.Source -ArgumentList "serve" -WindowStyle Hidden | Out-Null
    } else {
        Write-StackLog "INFO: Ollama process exists, waiting for endpoint."
    }

    [void](Wait-Http "http://127.0.0.1:11434/api/tags" 30 "Ollama")
}

function Ensure-ShionHeart {
    if (Test-Http "http://127.0.0.1:8000/health") {
        Write-StackLog "OK: Shion heart already responding on 8000."
        return
    }

    $existing = Get-CommandLineProcess "shion_runtime_server.py"
    if ($existing) {
        Write-StackLog "WARN: Shion heart process exists but health is down. Restarting stale heart process."
        foreach ($p in $existing) {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }

    Write-StackLog "START: Shion runtime server with stdout/stderr logs."
    Remove-Item -Path $HeartOutLog, $HeartErrLog -Force -ErrorAction SilentlyContinue
    Start-Process -FilePath "python.exe" `
        -ArgumentList "services\shion_runtime_server.py" `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $HeartOutLog `
        -RedirectStandardError $HeartErrLog | Out-Null

    [void](Wait-Http "http://127.0.0.1:8000/health" 60 "Shion heart")
}

function Ensure-Pulse {
    $existing = Get-CommandLineProcess "orchestrator_daemon.py"
    if ($existing) {
        Write-StackLog "OK: orchestrator pulse already running. Duplicate start skipped."
        return
    }

    if ($PulseMode -eq "Visible") {
        Write-StackLog "START: orchestrator pulse in visible console."
        Start-Process -FilePath "cmd.exe" `
            -ArgumentList "/k", "python core\orchestrator_daemon.py" `
            -WorkingDirectory $Root `
            -WindowStyle Normal | Out-Null
    } else {
        Write-StackLog "START: orchestrator pulse hidden."
        Start-Process -FilePath "pythonw.exe" `
            -ArgumentList "core\orchestrator_daemon.py" `
            -WorkingDirectory $Root `
            -WindowStyle Hidden | Out-Null
    }

    Start-Sleep -Seconds 3
    if (Get-CommandLineProcess "orchestrator_daemon.py") {
        Write-StackLog "OK: orchestrator pulse started."
    } else {
        Write-StackLog "ERROR: orchestrator pulse did not start."
    }
}

if ($Status) {
    Show-Status
    return
}

Write-StackLog "BOOT: AGI stack start requested. PulseMode=$PulseMode"
Ensure-Ollama
Ensure-ShionHeart
Ensure-Pulse
Write-StackLog "DONE: AGI stack start sequence complete."
