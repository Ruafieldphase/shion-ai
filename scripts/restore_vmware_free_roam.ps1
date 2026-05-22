[CmdletBinding()]
param(
    [switch]$DisableHypervisorBoot
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$OutDir = Join-Path $Root "outputs\hermes"
$LatestPath = Join-Path $OutDir "restore_vmware_free_roam_latest.json"
$StreamPath = Join-Path $OutDir "restore_vmware_free_roam.jsonl"
$Vmx = "D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmx"

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

function Write-State {
    param(
        [string]$Status,
        [hashtable]$Extra = @{}
    )
    $payload = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        status = $Status
        vmx = $Vmx
        principle = "restore_vmware_free_roam_body_before_more_gpu_field_work"
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

$vmProcesses = @(Get-Process -Name vmware,vmware-vmx -ErrorAction SilentlyContinue | Select-Object Name, Id)
$locks = @(Get-ChildItem -Path (Split-Path -Parent $Vmx) -Filter "*.lck" -Directory -ErrorAction SilentlyContinue | Select-Object FullName, LastWriteTime)

if ($vmProcesses.Count -gt 0 -or $locks.Count -gt 0) {
    Write-State -Status "restore_vmware_free_roam_pending_close_vmware" -Extra @{
        next_step = "Close VMware Workstation completely, then run this script again."
        processes = $vmProcesses
        locks = $locks
    }
    exit 3
}

if (-not (Test-Path $Vmx)) {
    Write-State -Status "restore_vmware_free_roam_missing_vmx" -Extra @{ error = "VMX not found" }
    exit 2
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = "$Vmx.before_restore_free_roam_$stamp"
Copy-Item -LiteralPath $Vmx -Destination $backup -Force

$text = Get-Content -LiteralPath $Vmx -Raw
if ($text -match '(?m)^vhv\.enable\s*=') {
    $text = $text -replace '(?m)^vhv\.enable\s*=\s*".*"$', 'vhv.enable = "FALSE"'
} else {
    $text = $text.TrimEnd() + "`r`nvhv.enable = `"FALSE`"`r`n"
}
Set-Content -LiteralPath $Vmx -Value $text -Encoding ASCII

$bootChange = $null
if ($DisableHypervisorBoot) {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    if (-not $isAdmin) {
        Write-State -Status "restore_vmware_free_roam_needs_admin_for_hypervisor_off" -Extra @{
            backup = $backup
            vmx_change = "vhv.enable = FALSE"
            next_step = "Run from elevated PowerShell with -DisableHypervisorBoot, or reboot and test VMware first."
        }
        exit 4
    }
    bcdedit /set hypervisorlaunchtype off | Out-Null
    $bootChange = "bcdedit /set hypervisorlaunchtype off"
}

Write-State -Status "restore_vmware_free_roam_vmx_repaired" -Extra @{
    backup = $backup
    vmx_change = "vhv.enable = FALSE"
    hypervisor_boot_change = $bootChange
    next_step = "Try starting AGI_Meta_OS in VMware. If it still fails, run this script from elevated PowerShell with -DisableHypervisorBoot and reboot."
}
