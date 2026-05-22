param(
    [ValidateSet("probe", "plan", "install-vllm", "install-sglang", "start-vllm", "start-sglang", "benchmark-vllm", "benchmark-sglang")]
    [string]$Action = "probe",
    [string]$Distro = "Ubuntu-24.04",
    [string]$Model = "Qwen/Qwen2.5-0.5B-Instruct",
    [int]$VllmPort = 8000,
    [int]$SglangPort = 30000,
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$OutDir = Join-Path $Root "outputs\hermes"
$LatestJson = Join-Path $OutDir "llm_serving_wsl_launcher_latest.json"
$LatestMd = Join-Path $OutDir "llm_serving_wsl_launcher_latest.md"
$StreamJsonl = Join-Path $OutDir "llm_serving_wsl_launcher.jsonl"

function Read-TrimmedFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return ""
    }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -eq 0) {
        return ""
    }
    $zeroCount = 0
    foreach ($byte in $bytes) {
        if ($byte -eq 0) {
            $zeroCount += 1
        }
    }
    if ($zeroCount -gt [Math]::Floor($bytes.Length / 8)) {
        return ([System.Text.Encoding]::Unicode.GetString($bytes)).Trim()
    }
    return ([System.Text.Encoding]::UTF8.GetString($bytes)).Trim()
}

function Invoke-Captured {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [int]$Timeout = 30
    )
    $stdout = [System.IO.Path]::GetTempFileName()
    $stderr = [System.IO.Path]::GetTempFileName()
    $started = Get-Date
    try {
        $proc = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -PassThru -Wait -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $elapsed = ((Get-Date) - $started).TotalSeconds
        return [ordered]@{
            ok = ($proc.ExitCode -eq 0)
            exit_code = $proc.ExitCode
            elapsed_seconds = [Math]::Round($elapsed, 4)
            stdout = Read-TrimmedFile -Path $stdout
            stderr = Read-TrimmedFile -Path $stderr
            command = @($FilePath) + $ArgumentList
        }
    }
    catch {
        $elapsed = ((Get-Date) - $started).TotalSeconds
        return [ordered]@{
            ok = $false
            elapsed_seconds = [Math]::Round($elapsed, 4)
            error = $_.Exception.Message
            command = @($FilePath) + $ArgumentList
        }
    }
    finally {
        Remove-Item -LiteralPath $stdout, $stderr -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-WslBash {
    param(
        [string]$Script,
        [int]$Timeout = 30
    )
    Invoke-Captured -FilePath "wsl.exe" -ArgumentList @("-d", $Distro, "--", "bash", "-lc", $Script) -Timeout $Timeout
}

function Test-Http {
    param([string]$Url)
    try {
        $response = Invoke-RestMethod -Uri $Url -TimeoutSec 5
        return [ordered]@{ ok = $true; url = $Url; data = $response }
    }
    catch {
        return [ordered]@{ ok = $false; url = $Url; error = $_.Exception.Message }
    }
}

function Get-Probe {
    $wslList = Invoke-Captured -FilePath "wsl.exe" -ArgumentList @("-l", "-v") -Timeout $TimeoutSeconds
    $wslLaunch = Invoke-WslBash -Script "uname -a; python3 --version; command -v uv && uv --version || true; command -v nvidia-smi && nvidia-smi --query-gpu=name,compute_cap,memory.total --format=csv,noheader || true" -Timeout $TimeoutSeconds
    $vllm = Test-Http -Url "http://127.0.0.1:$VllmPort/v1/models"
    $sglang = Test-Http -Url "http://127.0.0.1:$SglangPort/v1/models"
    return [ordered]@{
        wsl_list = $wslList
        wsl_launch = $wslLaunch
        vllm_endpoint = $vllm
        sglang_endpoint = $sglang
        ready = [ordered]@{
            wsl = [bool]$wslLaunch.ok
            vllm = [bool]$vllm.ok
            sglang = [bool]$sglang.ok
        }
    }
}

function Get-InstallScript {
    param([ValidateSet("vllm", "sglang")][string]$Engine)
    if ($Engine -eq "vllm") {
        return @"
set -euo pipefail
python3 -m venv ~/.venvs/shion-vllm
source ~/.venvs/shion-vllm/bin/activate
python -m pip install -U pip uv
uv pip install vllm --torch-backend=auto
"@
    }
    return @"
set -euo pipefail
python3 -m venv ~/.venvs/shion-sglang
source ~/.venvs/shion-sglang/bin/activate
python -m pip install -U pip uv
uv pip install sglang sglang-kernel --extra-index-url https://sgl-project.github.io/whl/cu129/ --extra-index-url https://download.pytorch.org/whl/cu129 --index-strategy unsafe-best-match
"@
}

function Get-StartScript {
    param([ValidateSet("vllm", "sglang")][string]$Engine)
    if ($Engine -eq "vllm") {
        return "source ~/.venvs/shion-vllm/bin/activate && vllm serve '$Model' --host 0.0.0.0 --port $VllmPort --gpu-memory-utilization 0.82 --max-model-len 2048"
    }
    return "source ~/.venvs/shion-sglang/bin/activate && python -m sglang.launch_server --model-path '$Model' --host 0.0.0.0 --port $SglangPort"
}

function Start-WslServer {
    param([ValidateSet("vllm", "sglang")][string]$Engine)
    $script = Get-StartScript -Engine $Engine
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($script))
    Start-Process -FilePath "wsl.exe" -ArgumentList @("-d", $Distro, "--", "bash", "-lc", "echo $encoded | base64 -d | bash") -WindowStyle Hidden
    return [ordered]@{ ok = $true; engine = $Engine; started_hidden = $true; script = $script }
}

function Get-Recommendation {
    param($Probe)
    if (-not $Probe.ready.wsl) {
        return [ordered]@{
            next_action = "enable_virtual_machine_platform_or_restore_wsl_before_install"
            note = "vLLM upstream serving should use Linux/WSL here; Windows-native Python remains the Ollama baseline."
        }
    }
    if ($Probe.ready.vllm -or $Probe.ready.sglang) {
        return [ordered]@{
            next_action = "run_benchmark_against_ready_endpoint"
            note = "At least one OpenAI-compatible candidate is already responding."
        }
    }
    return [ordered]@{
        next_action = "install_one_engine_in_fresh_wsl_venv"
        note = "Prefer one engine at a time on the 8GB GPU. Start with the role you want to test first."
    }
}

function Write-Outputs {
    param($Payload)
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    $json = $Payload | ConvertTo-Json -Depth 12
    Set-Content -LiteralPath $LatestJson -Value $json -Encoding UTF8
    Add-Content -LiteralPath $StreamJsonl -Value (($Payload | ConvertTo-Json -Depth 12 -Compress)) -Encoding UTF8

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# LLM Serving WSL Launcher")
    $lines.Add("")
    $lines.Add(("- Generated: {0}" -f $Payload.timestamp))
    $lines.Add(("- Action: {0}" -f $Payload.action))
    $lines.Add(("- Recommendation: {0}" -f $Payload.recommendation.next_action))
    $lines.Add("")
    $lines.Add("## Readiness")
    $lines.Add("")
    $lines.Add(("- WSL: {0}" -f $Payload.probe.ready.wsl))
    $lines.Add(("- vLLM endpoint: {0}" -f $Payload.probe.ready.vllm))
    $lines.Add(("- SGLang endpoint: {0}" -f $Payload.probe.ready.sglang))
    $lines.Add("")
    $lines.Add("## Probe Evidence")
    $lines.Add("")
    $lines.Add("### WSL List")
    $lines.Add("")
    $lines.Add('```text')
    $lines.Add($Payload.probe.wsl_list.stdout)
    if ($Payload.probe.wsl_list.stderr) {
        $lines.Add($Payload.probe.wsl_list.stderr)
    }
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("### WSL Launch")
    $lines.Add("")
    $lines.Add('```text')
    if ($Payload.probe.wsl_launch.stdout) {
        $lines.Add($Payload.probe.wsl_launch.stdout)
    }
    if ($Payload.probe.wsl_launch.stderr) {
        $lines.Add($Payload.probe.wsl_launch.stderr)
    }
    if ($Payload.probe.wsl_launch.error) {
        $lines.Add($Payload.probe.wsl_launch.error)
    }
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("## Planned Commands")
    $lines.Add("")
    $lines.Add("### vLLM")
    $lines.Add("")
    $lines.Add('```bash')
    $lines.Add($Payload.plans.vllm)
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("### SGLang")
    $lines.Add("")
    $lines.Add('```bash')
    $lines.Add($Payload.plans.sglang)
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("## Start Commands")
    $lines.Add("")
    $lines.Add("### vLLM")
    $lines.Add("")
    $lines.Add('```bash')
    $lines.Add((Get-StartScript -Engine "vllm"))
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("### SGLang")
    $lines.Add("")
    $lines.Add('```bash')
    $lines.Add((Get-StartScript -Engine "sglang"))
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("## Benchmark Commands")
    $lines.Add("")
    $lines.Add('```powershell')
    $lines.Add("python scripts\llm_serving_benchmark.py --provider windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest --provider vllm,openai,http://127.0.0.1:$VllmPort,$Model")
    $lines.Add("python scripts\llm_serving_benchmark.py --provider windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest --provider sglang,openai,http://127.0.0.1:$SglangPort,$Model")
    $lines.Add('```')
    Set-Content -LiteralPath $LatestMd -Value ($lines -join "`n") -Encoding UTF8
}

$probe = Get-Probe
$plans = [ordered]@{
    vllm = Get-InstallScript -Engine "vllm"
    sglang = Get-InstallScript -Engine "sglang"
}
$actionResult = [ordered]@{ ok = $true; skipped = "probe_or_plan_only" }

if ($Action -eq "install-vllm") {
    $actionResult = Invoke-WslBash -Script $plans.vllm -Timeout 3600
}
elseif ($Action -eq "install-sglang") {
    $actionResult = Invoke-WslBash -Script $plans.sglang -Timeout 3600
}
elseif ($Action -eq "start-vllm") {
    $actionResult = Start-WslServer -Engine "vllm"
}
elseif ($Action -eq "start-sglang") {
    $actionResult = Start-WslServer -Engine "sglang"
}
elseif ($Action -eq "benchmark-vllm") {
    $actionResult = Invoke-Captured -FilePath "python" -ArgumentList @("scripts\llm_serving_benchmark.py", "--provider", "windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest", "--provider", "vllm,openai,http://127.0.0.1:$VllmPort,$Model") -Timeout 900
}
elseif ($Action -eq "benchmark-sglang") {
    $actionResult = Invoke-Captured -FilePath "python" -ArgumentList @("scripts\llm_serving_benchmark.py", "--provider", "windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest", "--provider", "sglang,openai,http://127.0.0.1:$SglangPort,$Model") -Timeout 900
}

$payload = [ordered]@{
    timestamp = (Get-Date).ToString("o")
    status = "llm_serving_wsl_launcher_observed"
    action = $Action
    distro = $Distro
    model = $Model
    ports = [ordered]@{ vllm = $VllmPort; sglang = $SglangPort }
    probe = $probe
    plans = $plans
    action_result = $actionResult
    recommendation = Get-Recommendation -Probe $probe
    permission = [ordered]@{
        installs_packages = ($Action -like "install-*")
        starts_servers = ($Action -like "start-*")
        external_api_cost = $false
        writes_outputs_only = ($Action -eq "probe" -or $Action -eq "plan")
    }
}

Write-Outputs -Payload $payload
$payload.recommendation | ConvertTo-Json -Depth 6
Write-Host "Wrote $LatestJson"
Write-Host "Wrote $LatestMd"
