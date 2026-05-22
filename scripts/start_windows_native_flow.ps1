[CmdletBinding()]
param(
    [switch]$Status
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$OutDir = Join-Path $Root "outputs\hermes"
$LogDir = Join-Path $Root "outputs"
$LatestPath = Join-Path $OutDir "windows_native_flow_start_latest.json"
$StreamPath = Join-Path $OutDir "windows_native_flow_start.jsonl"
$AudioOut = Join-Path $LogDir "audio_loopback_phase_bridge.out.log"
$AudioErr = Join-Path $LogDir "audio_loopback_phase_bridge.err.log"
$FeltOut = Join-Path $LogDir "felt_body_consumer.out.log"
$FeltErr = Join-Path $LogDir "felt_body_consumer.err.log"

New-Item -ItemType Directory -Path $OutDir, $LogDir -Force | Out-Null

function Test-Http {
    param([string]$Uri)
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 2
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
    } catch {
        return $false
    }
}

function Get-CommandLineProcess {
    param([string]$Pattern)
    Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -and $_.CommandLine -match $Pattern
    } | Select-Object ProcessId, Name, CommandLine
}

function Write-State {
    param(
        [string]$StatusValue,
        [hashtable]$Extra = @{}
    )
    $payload = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        status = $StatusValue
        field = "windows_native_flow"
        audio_loopback_endpoint = "http://127.0.0.1:57322/audio_phase.json"
        felt_body_state = (Join-Path $Root "outputs\felt_body_state.json")
        processes = @{
            audio = @(Get-CommandLineProcess "audio_loopback_phase_bridge.py")
            felt = @(Get-CommandLineProcess "felt_body_consumer.py")
        }
        endpoints = @{
            audio_loopback = (Test-Http "http://127.0.0.1:57322/audio_phase.json")
            windows_ollama = (Test-Http "http://192.168.119.1:11434/api/tags")
        }
        permission = @{
            external_api_cost = $false
            irreversible_effect = $false
        }
        principle = "wake_existing_windows_inputs_without_adding_runtime_boundary"
    }
    foreach ($key in $Extra.Keys) {
        $payload[$key] = $Extra[$key]
    }
    $json = $payload | ConvertTo-Json -Depth 8
    $jsonLine = $payload | ConvertTo-Json -Depth 8 -Compress
    Set-Content -Path $LatestPath -Value $json -Encoding UTF8
    Add-Content -Path $StreamPath -Value $jsonLine -Encoding UTF8
    Write-Output $json
}

if ($Status) {
    Write-State -StatusValue "windows_native_flow_start_status"
    exit 0
}

$started = @()

if (-not (Test-Http "http://127.0.0.1:57322/audio_phase.json")) {
    Start-Process -FilePath "python.exe" `
        -ArgumentList "scripts\audio_loopback_phase_bridge.py" `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $AudioOut `
        -RedirectStandardError $AudioErr | Out-Null
    $started += "audio_loopback_phase_bridge"
    Start-Sleep -Seconds 3
}

if (-not (Get-CommandLineProcess "felt_body_consumer.py")) {
    Start-Process -FilePath "python.exe" `
        -ArgumentList "scripts\felt_body_consumer.py" `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $FeltOut `
        -RedirectStandardError $FeltErr | Out-Null
    $started += "felt_body_consumer"
    Start-Sleep -Seconds 2
}

$statusValue = if ((Test-Http "http://127.0.0.1:57322/audio_phase.json") -and (Test-Path (Join-Path $Root "outputs\felt_body_state.json"))) {
    "windows_native_flow_inputs_ready"
} else {
    "windows_native_flow_inputs_observed"
}

Write-State -StatusValue $statusValue -Extra @{ started = $started }
