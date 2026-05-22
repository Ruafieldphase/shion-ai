param(
    [ValidateSet("ask", "edit", "agent")]
    [string]$Mode = "agent",
    [string]$Prompt = "Read the Shion field handoff and hold the current external execution harness posture. Do not treat field observation as prohibition.",
    [switch]$Refresh,
    [switch]$NewWindow,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Antigravity = Get-Command antigravity -ErrorAction SilentlyContinue
if (-not $Antigravity) {
    throw "antigravity command was not found on PATH."
}

Push-Location $Root
try {
    if ($Refresh) {
        python scripts\antigravity_shion_adapter.py --check-sdk --write | Out-Null
        python scripts\antigravity_file_handoff_bridge.py refresh | Out-Null
        python scripts\build_antigravity_cli_plugin.py --stage | Out-Null
    }

    $Files = @(
        "outputs\shader_depth_sample.html",
        "outputs\antigravity_handoff\latest_prompt.md",
        "outputs\antigravity_handoff\inbox.jsonl",
        "outputs\antigravity_handoff\outbox.jsonl",
        "outputs\antigravity_handoff\state_latest.json",
        "outputs\antigravity_shion_handoff_prompt.md",
        "outputs\antigravity_shion_adapter_dry_run_latest.json",
        "outputs\antigravity_harness_bridge_latest.json",
        "outputs\rhythm_routing_layer_latest.json",
        "docs\antigravity_cli_plugin_bridge.md"
    )

    foreach ($File in $Files) {
        if (-not (Test-Path $File)) {
            throw "Required Shion handoff file is missing: $File"
        }
    }

    $Args = @("chat", "--mode", $Mode)
    foreach ($File in $Files) {
        $Args += @("--add-file", $File)
    }
    if ($NewWindow) {
        $Args += "--new-window"
    } else {
        $Args += "--reuse-window"
    }
    $Args += $Prompt

    if ($DryRun) {
        [pscustomobject]@{
            command = $Antigravity.Source
            args = $Args
            cwd = $Root
        } | ConvertTo-Json -Depth 5
    } else {
        & $Antigravity.Source @Args
    }
} finally {
    Pop-Location
}
