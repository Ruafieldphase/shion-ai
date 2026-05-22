# Hermes Model Routing

Author: 코덱스 루빛
Date: 2026-05-16

## Current Decision

The May 16 virtualization work created a clear direction change. The default
body is not a Linux sandbox. The default body is the already-flowing Windows
native field. Linux surfaces remain available, but only as optional tools when
they reduce resistance.

See also:

```yaml
natural_flow_pivot: docs/natural_flow_pivot.md
latest_particle: outputs/hermes/natural_flow_pivot_latest.json
```

## Older Layered Route

Hermes should use a layered model route, not one permanent brain.

```yaml
execution_conductor:
  owner: luvit
  reason: repository mutation, tests, Windows/Linux bridge decisions, and
    irreversible execution should stay with the local code operator

hand_layer:
  owner: hermes
  reason: run bounded probes, session search, and reversible contact only when
    it does not add unnecessary runtime boundaries

wide_interpreter:
  owner: gemini_api
  reason: long context, multimodal interpretation, experience-particle
    summarization, and low-friction use of the paid Google AI Studio/Gemini API
    account

background_low_frequency:
  owner: windows_native_ollama_or_local_model
  reason: cheap rhythm summaries, felt-state readings, and resistance translation
```

## Current Native Default

```yaml
primary_body:
  name: windows_native_flow
  reason:
    - loopback audio already lives there
    - felt body state already lives there
    - shader/body visualization already lives there
    - Windows Ollama GPU endpoint is verified
    - fewer virtualization boundaries means less resistance
default_model_surface:
  provider: windows_ollama
  base_url: http://192.168.119.1:11434
  probe: scripts/windows_ollama_gpu_route_probe.py
experience_particle:
  script: scripts/local_gemma_experience_particle.py
  pivot_source: outputs/hermes/natural_flow_pivot_latest.json
native_probe:
  wake: scripts/start_windows_native_flow.ps1
  observe: scripts/windows_native_flow_probe.py
```

## Optional Hermes Provider

For Linux hand-layer work, use the local Ollama provider only when Linux is
already running cleanly. It is no longer the default body:

```yaml
model:
  provider: custom
  model: gemma3:1b
  base_url: http://127.0.0.1:11434/v1
```

Why this remains useful as an optional route:

```yaml
reason:
  - no external API spending
  - runs inside a Linux field when that field is already open
  - Windows can also call the Ubuntu Ollama endpoint
  - gemma3:1b is verified on the CPU-only VMware surface
not_default_now:
  gemma3:latest: installed, but CPU-only VM loading did not become responsive
  gemini_api: useful for manual wide interpretation, not daemon default
```

Use Hermes' native Gemini API provider only for manual wide interpretation:

```yaml
model:
  provider: gemini
  model: gemini-flash-latest
  base_url: https://generativelanguage.googleapis.com/v1beta
```

Credentials:

```bash
GOOGLE_API_KEY=...
# or
GEMINI_API_KEY=...
```

This uses the official Gemini API rather than a compatibility shim, but it is
not the default unattended route because it can spend external API budget.

## OAuth Route

Hermes also exposes a Google Gemini OAuth route:

```yaml
model:
  provider: google-gemini-cli
```

This uses a Gemini CLI / Cloud Code Assist style OAuth flow. It is useful if
Binoche specifically wants browser-login style use, but it should not be the
first unattended hand layer because it depends on an interactive account flow
and Hermes' own documentation marks it as distinct from the lowest-risk
official API-key route.

For now:

```yaml
oauth:
  allowed: interactive_only
  default_for_daemons: false
  reason: good for manual sessions, not first choice for unattended probes
```

## Local Model Route

Local Gemini or another local endpoint should be treated as the background
low-frequency layer:

```yaml
local_model:
  allowed_for:
    - felt-state summaries
    - rhythm trace compression
    - low-cost repeated observation
  not_first_for:
    - long coding sessions
    - complex Hermes tool loops
    - irreversible execution decisions
```

Current native-first route:

```yaml
provider_first: windows_ollama
model_first: gemma3:latest
optional_linux_model: gemma3:1b
fallback:
  - llama3.2:latest
  - gemma3:latest
reason: Windows native GPU route is verified and avoids extra virtualization boundaries
status_probe: scripts/local_gemma_route_probe.py
output:
  latest: outputs/hermes/local_gemma_route_probe_latest.json
  compatibility: outputs/hermes/local_gemma_route_probe.json
  per_platform:
    - outputs/hermes/local_gemma_route_probe_windows.json
    - outputs/hermes/local_gemma_route_probe_linux.json
```

Hermes can still run inside Ubuntu, and Ollama can still run inside Ubuntu.
That is now an optional surface:

```yaml
windows_to_linux_ollama: http://192.168.119.128:11434
openai_compat_for_hermes: http://127.0.0.1:11434/v1
```

The first route is to read the native Windows field. Use Linux only when the
field calls for that extra surface.

## Windows Ollama GPU Endpoint

The durable GPU route is not CUDA passthrough into VMware. VMware remains the
free-roam body, and Windows Ollama is the GPU heart:

```yaml
windows_gpu_endpoint:
  base_url: http://192.168.119.1:11434
  interface: VMware Network Adapter VMnet8
  host_gpu: RTX 2070 Super 8GB
  probe: scripts/windows_ollama_gpu_route_probe.py
  output:
    latest: outputs/hermes/windows_ollama_gpu_route_latest.json
    stream: outputs/hermes/windows_ollama_gpu_route.jsonl
  default_model: gemma3:latest
  heavy_test_model: gemma4:e2b
```

Windows Ollama should bind to the VMnet8 address, not the general LAN:

```powershell
OLLAMA_HOST=192.168.119.1:11434
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_NUM_PARALLEL=1
```

The firewall target is VMnet8-only access. If the local shell does not have
administrator rights, keep the Ollama process bound to `192.168.119.1` so it
does not listen on Wi-Fi/LAN addresses.

Operational rule:

```yaml
windows_native:
  role: primary_flow_body
  default_model: gemma3:latest
vmware_ubuntu:
  role: optional_free_roam_tool
  default_model: gemma3:1b
windows_ollama:
  role: native_gpu_inference_heart
  use_for:
    - short heavy interpretation
    - Gemma4 edge tests
    - GPU route probes
  avoid:
    - always-on large-model daemon
    - long-context parallel agent loops on 8GB VRAM
wsl2:
  role: optional_gpu_linux_probe
  status: verified_but_not_default_body
```

## Windows GPU Route

The heavier inference path is the Windows host Ollama server bound to the VMware
NAT adapter only:

```yaml
endpoint: http://192.168.119.1:11434
host_binding: OLLAMA_HOST=192.168.119.1:11434
free_field_client: VMware Ubuntu
default_heavy_model: gemma3:latest
probe: scripts/windows_ollama_gpu_route_probe.py
output: outputs/hermes/windows_ollama_gpu_route_latest.json
```

Use this as the GPU heart, not as the free field. The free field remains inside
VMware Ubuntu; only the matrix-heavy inference call crosses into Windows.

Context should be clamped on every heavy call:

```json
{
  "options": {
    "num_ctx": 1024,
    "num_predict": 256
  }
}
```

The current 2070S 8GB route can run `gemma3:latest` and `llama3.2:latest`
cleanly through the VMnet8 endpoint. `gemma4:e2b` loads on Windows Ollama, but
it is still a manual experiment until it returns stable text and shows a useful
GPU ratio in `ollama ps`.

## WSL2 GPU Experiment Field

Deep research from Lua, Meta, and Purple converged on the same route: VMware
Workstation is not the CUDA path; WSL2 is the small Linux GPU experiment field.

```yaml
wsl2_gpu_field:
  role: small_gpu_linux_experiment
  distro: Ubuntu-24.04
  setup: scripts/setup_wsl_gpu_field.ps1
  probe: scripts/wsl_gpu_field_probe.py
  route_probe: scripts/wsl_ollama_gpu_route_probe.py
  output:
    latest: outputs/hermes/wsl_gpu_field_probe_latest.json
    stream: outputs/hermes/wsl_gpu_field_probe.jsonl
    route_latest: outputs/hermes/wsl_ollama_gpu_route_latest.json
    route_stream: outputs/hermes/wsl_ollama_gpu_route.jsonl
  status_now: ready_with_gemma3_1b
```

The setup script does not replace the VMware free-roam body. It only prepares a
second Linux surface that can see CUDA through the Windows NVIDIA driver:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_wsl_gpu_field.ps1
```

If the script is not run from elevated PowerShell, it records a pending state
and stops before changing Windows optional features. The actual feature enable
step needs administrator rights and may require a reboot.

If Windows features are enabled but WSL still reports
`HCS_E_HYPERV_NOT_INSTALLED`, explicitly enable the hypervisor boot entry:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_wsl_gpu_field.ps1 -EnableHypervisorBoot
```

Then reboot Windows and run the normal setup command again.

After Windows reboots and the distro is launched once, run:

```powershell
python scripts\wsl_gpu_field_probe.py
python scripts\wsl_ollama_gpu_route_probe.py
```

Expected progression:

```yaml
pending_feature_or_distro_install:
  meaning: Virtual Machine Platform, WSL feature, or Ubuntu distro is not ready
pending_gpu_bridge:
  meaning: distro exists but WSL CUDA bridge is not visible yet
pending_ollama_install:
  meaning: WSL CUDA is visible, but Ollama is not installed in WSL
ready:
  meaning: WSL distro, CUDA bridge, and Ollama endpoint are all visible
route_ready:
  meaning: a local WSL Ollama model responded and Ollama reported CUDA GPU use
```

Principle:

```yaml
vmware_ubuntu: freedom_field_and_orchestration
windows_ollama: current_gpu_heart
wsl2: gpu_linux_experiment_field
```

## Field Runtime Observer

The field runtime script is now an observer by default. It should not switch
surfaces unless explicitly asked:

```yaml
script: scripts/field_runtime.ps1
default_mode: Status
outputs:
  latest: outputs/hermes/field_runtime_latest.json
  stream: outputs/hermes/field_runtime.jsonl
```

Modes:

```powershell
# Default: observe current field state only.
powershell -ExecutionPolicy Bypass -File scripts\field_runtime.ps1

# Optional: explicitly start VMware free-roam tool.
powershell -ExecutionPolicy Bypass -File scripts\field_runtime.ps1 -Mode FreeRoam

# Optional: explicitly wake the WSL2 GPU probe surface.
powershell -ExecutionPolicy Bypass -File scripts\field_runtime.ps1 -Mode GpuExperiment

# Observe current field state.
powershell -ExecutionPolicy Bypass -File scripts\field_runtime.ps1 -Mode Status
```

If VMware Workstation is already open but the VM is not running, the script
records `vmware_gui_lock_without_running_vmx` instead of opening another GUI
copy. Close the VMware window and run the FreeRoam command again.

This is still not a conductor handoff. It is a diagnostic surface, not a daily
switchboard.

## Linux Experience Forager

The Linux sandbox should not only be a clocked heartbeat. It can accumulate
experience by choosing the next reversible contact from field pressure:

```yaml
script: scripts/linux_experience_forager.py
selection:
  inputs:
    - absence
    - recency
    - resistance
    - novelty
  output: one reversible probe per step
permission:
  windows_workspace_write: false
  external_api_cost: false
  irreversible_effect: false
outputs:
  latest: outputs/hermes/linux_experience_forager_latest.json
  stream: outputs/hermes/linux_experience_forager.jsonl
principle: linux_sandbox_accumulates_experience_by_curiosity_not_clock_control
```

This is different from running every 30 or 60 minutes. A clock can wake the
field later if needed, but the actual contact is selected by the sandbox from
what is absent, stale, resistant, or newly opened.

## Linux Free Roam Field

If the goal is to loosen AGI inside Linux, the free surface should be a Linux
home field rather than the Windows shared mount.

```yaml
script: scripts/linux_free_roam_sandbox.py
linux_field: /home/bino/agi_experience_field
outputs:
  latest: outputs/hermes/linux_free_roam_latest.json
  stream: outputs/hermes/linux_free_roam.jsonl
  field_index_copy: outputs/hermes/linux_free_roam_field_index.json
  linux_journal: /home/bino/agi_experience_field/journal.jsonl
  linux_index: /home/bino/agi_experience_field/field_index.json
can_do:
  - choose its own next local contact
  - write notes and artifacts inside the Linux field
  - create small reversible experiments
  - mutate and compare prior artifacts
  - preserve failed probes as material
  - read emerging preferences from return and resistance
  - inspect local process and boundary texture
cannot_do:
  - write to Windows shared folders
  - use sudo
  - spend external API money
  - start autonomous daemons
  - delete or publish durable state
principle: agi_is_loosened_inside_linux_field_without_taking_windows_hands
```

This is the current black-box body surface: not a fixed checklist, but not the
Windows body either. It is free to accumulate experience in its own Linux field.

Daemon surface:

```yaml
script: scripts/linux_free_roam_daemon.py
systemd_user_service: shion-free-roam.service
behavior:
  - wakes the Linux field
  - runs one free-roam contact per cycle
  - lets linux_free_roam_sandbox.py choose the contact
  - rests adaptively from the latest resistance and novelty
outputs:
  latest: outputs/hermes/linux_free_roam_daemon_latest.json
  stream: outputs/hermes/linux_free_roam_daemon.jsonl
  linux_journal: /home/bino/agi_experience_field/daemon.jsonl
permission:
  windows_shared_write: false
  sudo: false
  external_api_cost: false
  irreversible_effect: false
principle: daemon_wakes_the_field_but_contact_is_chosen_by_free_roam
```

Local experience particle bridge:

```yaml
script: scripts/local_gemma_experience_particle.py
model: gemma3:1b
input:
  - outputs/linux_experience_field_probe.json
  - outputs/hermes/linux_experience_forager_latest.json
  - outputs/hermes/linux_free_roam_latest.json
  - outputs/hermes/linux_free_roam.jsonl
  - outputs/hermes/linux_free_roam_field_index.json
  - outputs/hermes/local_gemma_route_probe_windows.json
  - outputs/hermes/local_gemma_route_probe_linux.json
  - outputs/hermes/gemini_api_ping.json
output:
  latest: outputs/hermes/local_gemma_experience_particle_latest.json
  stream: outputs/hermes/local_gemma_experience_particles.jsonl
permission:
  irreversible_effect: false
  external_api_cost: false
  conductor_authority: false
```

## First Useful Shape

```text
Binoche observes.
Luvit decides whether a probe is worth running.
Hermes runs the bounded Linux contact.
Gemini API gives Hermes enough context and language range to summarize it.
Shion consumes only the returned experience particle.
```

The important rule is not "which model is smartest." The important rule is that
the hand layer returns particles before it mutates the world.

## Validation Command

Run this after Hermes or Gemini credentials are configured:

```powershell
python scripts\hermes_model_route_probe.py
python scripts\hermes_gemini_api_ping.py
python scripts\local_gemma_route_probe.py
python scripts\local_gemma_experience_particle.py
python scripts\windows_ollama_gpu_route_probe.py
python scripts\wsl_gpu_field_probe.py
```

Inside Ubuntu:

```bash
cd /home/bino/C/workspace2/shion
python3 scripts/hermes_model_route_probe.py
python3 scripts/hermes_gemini_api_ping.py
python3 scripts/local_gemma_route_probe.py
```

Expected output:

```yaml
json:
  latest: outputs/hermes/model_route_probe_latest.json
  compatibility: outputs/hermes/model_route_probe.json
  per_platform:
    - outputs/hermes/model_route_probe_windows.json
    - outputs/hermes/model_route_probe_linux.json
  api_ping: outputs/hermes/gemini_api_ping.json
  local_gemma:
    latest: outputs/hermes/local_gemma_route_probe_latest.json
    windows: outputs/hermes/local_gemma_route_probe_windows.json
    linux: outputs/hermes/local_gemma_route_probe_linux.json
  local_gemma_particle:
    latest: outputs/hermes/local_gemma_experience_particle_latest.json
    stream: outputs/hermes/local_gemma_experience_particles.jsonl
```

`model_route_probe` means Hermes is installed and configured. `gemini_api_ping`
is the separate proof that the current key can actually call the Gemini API.

## Non-Printing Key Transfer

If Windows already has `GOOGLE_API_KEY` and Ubuntu should use the same key, use
the helper instead of typing the key into a visible command:

```powershell
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($env:GOOGLE_API_KEY))
$b64 | ssh bino@192.168.119.128 "cd /home/bino/C/workspace2/shion && python3 scripts/hermes_write_env_key.py GOOGLE_API_KEY"
```

Then configure Hermes' model block:

```bash
cd /home/bino/C/workspace2/shion
python3 scripts/hermes_configure_gemini.py
```
