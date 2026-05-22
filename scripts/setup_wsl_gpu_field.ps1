[CmdletBinding()]
param(
    [string]$Distro = "Ubuntu-24.04",
    [switch]$NoInstall,
    [switch]$EnableHypervisorBoot
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$outDir = Join-Path $root "outputs\hermes"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outPath = Join-Path $outDir "wsl_gpu_field_setup_latest.json"

function Write-SetupState {
    param(
        [string]$Status,
        [hashtable]$Extra = @{}
    )
    $payload = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        status = $Status
        distro = $Distro
        route = [ordered]@{
            vmware_ubuntu = "freedom_field_and_orchestration"
            windows_ollama = "current_gpu_heart"
            wsl2 = "small_gpu_linux_experiment"
        }
        permission = [ordered]@{
            external_api_cost = $false
            irreversible_effect = $false
        }
    }
    foreach ($key in $Extra.Keys) {
        $payload[$key] = $Extra[$key]
    }
    $json = $payload | ConvertTo-Json -Depth 8
    $jsonLine = $payload | ConvertTo-Json -Depth 8 -Compress
    Set-Content -Path $outPath -Value $json -Encoding UTF8
    Add-Content -Path (Join-Path $outDir "wsl_gpu_field_setup.jsonl") -Value $jsonLine -Encoding UTF8
    Write-Output $json
}

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

$wslConfig = @"
[wsl2]
memory=4GB
processors=3
swap=2GB
localhostForwarding=true
dnsTunneling=true
"@
Set-Content -Path (Join-Path $HOME ".wslconfig") -Value $wslConfig -Encoding ASCII

if (-not $isAdmin) {
    Write-SetupState -Status "wsl_gpu_field_setup_needs_elevated_powershell" -Extra @{
        next_step = "Run this script from PowerShell as Administrator, then reboot if Windows asks."
        command = "powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    }
    exit 3
}

if ($EnableHypervisorBoot) {
    bcdedit /set hypervisorlaunchtype auto | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-SetupState -Status "wsl_gpu_field_setup_hypervisor_boot_failed" -Extra @{
            next_step = "Run this script from elevated PowerShell. If it still fails, inspect bcdedit manually."
            last_exit_code = $LASTEXITCODE
        }
        exit 6
    }
    Write-SetupState -Status "wsl_gpu_field_setup_hypervisor_boot_enabled" -Extra @{
        next_step = "Reboot Windows, then run setup_wsl_gpu_field.ps1 again without -EnableHypervisorBoot."
        boot_change = "bcdedit /set hypervisorlaunchtype auto"
    }
    exit 0
}

Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -All -NoRestart | Out-Null
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -All -NoRestart | Out-Null

wsl --shutdown | Out-Null
wsl --update | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-SetupState -Status "wsl_gpu_field_setup_pending_reboot_or_wsl_update" -Extra @{
        next_step = "Reboot Windows, then run wsl --install --no-distribution from elevated PowerShell if WSL still reports HCS_E_HYPERV_NOT_INSTALLED."
        last_exit_code = $LASTEXITCODE
    }
    exit 4
}

if (-not $NoInstall) {
    wsl --install -d $Distro --no-launch
    if ($LASTEXITCODE -ne 0) {
        Write-SetupState -Status "wsl_gpu_field_setup_pending_reboot_or_virtual_machine_platform" -Extra @{
            next_step = "Run setup_wsl_gpu_field.ps1 -EnableHypervisorBoot from elevated PowerShell, reboot Windows, then run setup again."
            last_exit_code = $LASTEXITCODE
        }
        exit 5
    }
}

Write-SetupState -Status "wsl_gpu_field_setup_requested" -Extra @{
    next_step = "Reboot Windows if requested, then launch the distro once to create the Linux user."
}
