# LLM Serving Benchmark

This benchmark keeps the current Windows-native body as the baseline and measures only already-running local serving endpoints. It does not install servers, start vLLM, start SGLang, or call external APIs.

The numbers are an observation surface, not the decision maker. The runtime should first preserve the natural context shape: stable identity/rhythm prefix, small changing tail, and provider-neutral routing. If a serving engine creates more resistance than flow, the profile remains useful without that engine.

## Purpose

The benchmark separates two runtime shapes:

- `unconscious_fixed_prefix`: stable background prompt plus a small changing tail. This is the SGLang-shaped case because prefix reuse should matter.
- `conscious_varied_input`: irregular front-channel prompts. This is the vLLM-shaped case because serving stability across varied requests should matter.

The benchmark reports median latency, a portable warm-reuse latency signal, and GPU snapshots from `nvidia-smi` when available. The reuse signal is not a native cache-hit counter.

## Serving Profiles

The local profile layer absorbs the useful idea from vLLM/SGLang without installing either engine:

```powershell
python scripts\llm_serving_profile_manifest.py
```

Outputs:

- `outputs/hermes/llm_serving_profiles_latest.json`
- `outputs/hermes/llm_serving_profiles_latest.md`
- `outputs/hermes/llm_serving_profiles.jsonl`

Current profiles:

- `unconscious_fixed_prefix`: stable rhythm prefix plus small tail. This is prefix-cache friendly, but does not require SGLang.
- `conscious_varied_input`: light stable router plus varied tail. This is flexible-serving friendly, but does not require vLLM.

## Official Projects

- vLLM GitHub: <https://github.com/vllm-project/vllm>
- vLLM docs: <https://docs.vllm.ai>
- SGLang GitHub: <https://github.com/sgl-project/sglang>
- SGLang docs: <https://docs.sglang.io>
- SGLang site: <https://www.sglang.io>

## Baseline

Run the current Windows Ollama baseline:

```powershell
python scripts\llm_serving_benchmark.py --iterations 3 --warmups 1 --max-tokens 32
```

Outputs:

- `outputs/hermes/llm_serving_benchmark_latest.json`
- `outputs/hermes/llm_serving_benchmark_latest.md`
- `outputs/hermes/llm_serving_benchmark.jsonl`

## Candidate Readiness

Before installing or starting a new serving engine, check whether the local host, WSL, Docker, and default OpenAI-compatible ports are ready:

```powershell
python scripts\llm_serving_candidate_probe.py
```

Outputs:

- `outputs/hermes/llm_serving_candidate_probe_latest.json`
- `outputs/hermes/llm_serving_candidate_probe_latest.md`
- `outputs/hermes/llm_serving_candidate_probe.jsonl`

For the WSL serving path, use the launcher in probe mode first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action probe
```

Outputs:

- `outputs/hermes/llm_serving_wsl_launcher_latest.json`
- `outputs/hermes/llm_serving_wsl_launcher_latest.md`
- `outputs/hermes/llm_serving_wsl_launcher.jsonl`

## Add vLLM or SGLang

If an OpenAI-compatible vLLM server is already running:

```powershell
python scripts\llm_serving_benchmark.py `
  --provider windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest `
  --provider vllm,openai,http://127.0.0.1:8000,your-model-id
```

If an OpenAI-compatible SGLang server is already running:

```powershell
python scripts\llm_serving_benchmark.py `
  --provider windows_ollama,ollama,http://192.168.119.1:11434,gemma3:latest `
  --provider sglang,openai,http://127.0.0.1:30000,your-model-id
```

The same can be configured with environment variables:

```powershell
$env:SHION_VLLM_BASE_URL="http://127.0.0.1:8000"
$env:SHION_VLLM_MODEL="your-model-id"
$env:SHION_SGLANG_BASE_URL="http://127.0.0.1:30000"
$env:SHION_SGLANG_MODEL="your-model-id"
python scripts\llm_serving_benchmark.py
```

## WSL Launcher

The launcher is intentionally explicit. `probe` and `plan` do not install packages or start servers. Installation and server startup only happen when the action says so.

```powershell
# Observe readiness and write the planned commands.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action probe

# After WSL is healthy, install one engine at a time in a fresh WSL venv.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action install-vllm -Model Qwen/Qwen2.5-0.5B-Instruct
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action install-sglang -Model Qwen/Qwen2.5-0.5B-Instruct

# Start one candidate endpoint.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action start-vllm -Model Qwen/Qwen2.5-0.5B-Instruct
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action start-sglang -Model Qwen/Qwen2.5-0.5B-Instruct

# Run the benchmark against a ready endpoint.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action benchmark-vllm -Model Qwen/Qwen2.5-0.5B-Instruct
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\llm_serving_wsl_launcher.ps1 -Action benchmark-sglang -Model Qwen/Qwen2.5-0.5B-Instruct
```

Current local blocker, if reproduced by the probe: WSL needs Virtual Machine Platform / Hyper-V support restored before the official vLLM path can run.

## Reading The Result

Use the numbers as routing evidence, not as a fixed rule.

- For the unconscious loop, low `unconscious_fixed_prefix` median latency and a positive reuse signal are low-resistance evidence.
- For the conscious loop, stable `conscious_varied_input` latency and few failures are low-resistance evidence.
- If vLLM and SGLang are absent, the script records the skip state rather than forcing infrastructure.
