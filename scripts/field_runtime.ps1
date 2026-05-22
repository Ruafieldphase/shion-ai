[CmdletBinding()]
param(
    [ValidateSet("FreeRoam", "GpuExperiment", "Status", "StopWsl")]
    [string]$Mode = "Status",
    [switch]$KeepWsl,
    [switch]$AllowGuiFallback,
    [ValidateSet("gui", "nogui")]
    [string]$VmUi = "gui"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$OutDir = Join-Path $Root "outputs\hermes"
$LatestPath = Join-Path $OutDir "field_runtime_latest.json"
$StreamPath = Join-Path $OutDir "field_runtime.jsonl"
$Vmrun = "D:\Program Files\VMware\vmrun.exe"
$VmwareExe = "D:\Program Files\VMware\vmware.exe"
$Vmx = "D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmx"

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

function Invoke-Text {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList = @(),
        [int]$TimeoutSeconds = 30
    )
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = ($ArgumentList | ForEach-Object {
        if ($_ -match '[\s"]') {
            '"' + ($_ -replace '"', '\"') + '"'
        } else {
            $_
        }
    }) -join " "
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $process = [System.Diagnostics.Process]::Start($psi)
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        try { $process.Kill() } catch {}
        return [ordered]@{
            ok = $false
            exit_code = $null
            stdout = ""
            stderr = "timeout"
            command = @($FilePath) + $ArgumentList
        }
    }
    $stdout = $process.StandardOutput.ReadToEnd().Replace([string][char]0, "").Trim()
    $stderr = $process.StandardError.ReadToEnd().Replace([string][char]0, "").Trim()
    return [ordered]@{
        ok = ($process.ExitCode -eq 0)
        exit_code = $process.ExitCode
        stdout = $stdout
        stderr = $stderr
        command = @($FilePath) + $ArgumentList
    }
}

function Test-Http {
    param([string]$Uri)
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 2
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
    } catch {
        return $false
    }
}

function Get-VmwareState {
    $processes = Get-Process -Name vmware,vmware-vmx -ErrorAction SilentlyContinue |
        Select-Object Name, Id, CPU, WorkingSet64
    $vmrunList = if (Test-Path $Vmrun) {
        Invoke-Text -FilePath $Vmrun -ArgumentList @("-T", "ws", "list") -TimeoutSeconds 20
    } else {
        [ordered]@{ ok = $false; stderr = "vmrun_not_found"; stdout = ""; command = @($Vmrun) }
    }
    $locks = Get-ChildItem -Path (Split-Path -Parent $Vmx) -Filter "*.lck" -Directory -ErrorAction SilentlyContinue |
        Select-Object FullName, LastWriteTime
    return [ordered]@{
        processes = @($processes)
        vmrun_list = $vmrunList
        vmx = $Vmx
        locks = @($locks)
        running = (($vmrunList.stdout -like "*$Vmx*") -or ($processes | Where-Object { $_.Name -eq "vmware-vmx" }))
    }
}

function Get-WslState {
    $list = Invoke-Text -FilePath "wsl.exe" -ArgumentList @("-l", "-v") -TimeoutSeconds 20
    $status = Invoke-Text -FilePath "wsl.exe" -ArgumentList @("--status") -TimeoutSeconds 20
    return [ordered]@{
        list = $list
        status = $status
        running = ($list.stdout -match "Ubuntu-24\.04\s+Running")
    }
}

function Write-State {
    param(
        [string]$Status,
        [hashtable]$Extra = @{}
    )
    $payload = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        status = $Status
        mode = $Mode
        route = [ordered]@{
        windows_native = "primary_flow_body"
        vmware_ubuntu = "optional_free_roam_tool"
        windows_ollama = "native_gpu_heart"
        wsl2_ollama = "optional_gpu_linux_probe"
        }
        vmware = Get-VmwareState
        wsl = Get-WslState
        endpoints = [ordered]@{
            windows_ollama_vmnet8 = (Test-Http "http://192.168.119.1:11434/api/tags")
            wsl_ollama_localhost = (Test-Http "http://127.0.0.1:11434/api/tags")
        }
        permission = [ordered]@{
            external_api_cost = $false
            irreversible_effect = $false
        }
    }
    foreach ($key in $Extra.Keys) {
        $payload[$key] = $Extra[$key]
    }
    $json = $payload | ConvertTo-Json -Depth 10
    $jsonLine = $payload | ConvertTo-Json -Depth 10 -Compress
    Set-Content -Path $LatestPath -Value $json -Encoding UTF8
    Add-Content -Path $StreamPath -Value $jsonLine -Encoding UTF8
    Write-Output $json
}

function Stop-WslField {
    $result = Invoke-Text -FilePath "wsl.exe" -ArgumentList @("--shutdown") -TimeoutSeconds 30
    Start-Sleep -Seconds 2
    return $result
}

function Start-VmwareField {
    if (-not (Test-Path $Vmx)) {
        throw "VMX not found: $Vmx"
    }
    $state = Get-VmwareState
    if ($state.running) {
        return [ordered]@{ ok = $true; skipped = "vmware_already_running" }
    }
    if (($state.locks | Measure-Object).Count -gt 0 -and ($state.processes | Where-Object { $_.Name -eq "vmware" })) {
        return [ordered]@{
            ok = $false
            reason = "vmware_gui_lock_without_running_vmx"
            next_step = "Close the VMware Workstation window that has the VMX open, then run field_runtime.ps1 again."
        }
    }
    if (Test-Path $Vmrun) {
        $result = Invoke-Text -FilePath $Vmrun -ArgumentList @("-T", "ws", "start", $Vmx, $VmUi) -TimeoutSeconds 120
        if ($result.ok) {
            Start-Sleep -Seconds 5
            return $result
        }
        if (-not $AllowGuiFallback) {
            return [ordered]@{
                ok = $false
                reason = "vmrun_start_failed"
                vmrun = $result
                next_step = "If VMware GUI is open, close it. If this persists after closing GUI, start VMware once manually to inspect the visible error."
            }
        }
    }
    if (Test-Path $VmwareExe) {
        Start-Process -FilePath $VmwareExe -ArgumentList "`"$Vmx`"" -WindowStyle Normal | Out-Null
        Start-Sleep -Seconds 8
        return [ordered]@{ ok = $true; fallback = "vmware_exe_started"; command = @($VmwareExe, $Vmx) }
    }
    return [ordered]@{ ok = $false; stderr = "vmrun_and_vmware_exe_not_found" }
}

function Start-WslGpuField {
    $start = Invoke-Text -FilePath "wsl.exe" -ArgumentList @("-d", "Ubuntu-24.04", "--", "bash", "-lc", "systemctl is-active ollama >/dev/null || sudo systemctl start ollama; ollama --version; /usr/lib/wsl/lib/nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits") -TimeoutSeconds 60
    return $start
}

if ($Mode -eq "Status") {
    Write-State -Status "field_runtime_status"
    exit 0
}

if ($Mode -eq "StopWsl") {
    $stop = Stop-WslField
    Write-State -Status "field_runtime_wsl_stopped" -Extra @{ action = $stop }
    exit 0
}

if ($Mode -eq "GpuExperiment") {
    $gpu = Start-WslGpuField
    Write-State -Status "field_runtime_gpu_experiment_ready" -Extra @{ action = $gpu }
    exit 0
}

if ($Mode -eq "FreeRoam") {
    $wslStop = if ($KeepWsl) {
        [ordered]@{ ok = $true; skipped = "KeepWsl" }
    } else {
        Stop-WslField
    }
    $vmStart = Start-VmwareField
    $status = if ($vmStart.ok) { "field_runtime_free_roam_ready" } else { "field_runtime_free_roam_observed" }
    Write-State -Status $status -Extra @{
        wsl_action = $wslStop
        vmware_action = $vmStart
    }
    exit $(if ($vmStart.ok) { 0 } else { 2 })
}
