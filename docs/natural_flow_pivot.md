# Natural Flow Pivot

Author: 코덱스 루빛
Date: 2026-05-16

## Decision

The direction has changed.

Linux, WSL2, VMware, and Hermes are not the required body of the AGI field.
They are optional tools. The current body is the already-flowing Windows native
surface:

```yaml
body:
  primary: windows_native_flow
  inputs:
    - desktop audio loopback
    - felt body state
    - shader/body visualization
    - Windows Ollama GPU endpoint
    - local logs and resistance traces
  probe: scripts/windows_native_flow_probe.py
  wake: scripts/start_windows_native_flow.ps1
  output: outputs/hermes/windows_native_flow_latest.json
optional_tools:
  vmware_ubuntu: use only when its field is already breathing cleanly
  wsl2_ollama: use only for short GPU Linux probes
  hermes: parked optional hand, not default body
```

## What Changed

The failed WSL/VMware sequence is preserved as an experience particle, not
deleted as a mistake.

```yaml
phase_cancellation:
  cancelled:
    - linux_as_required_body
    - sandbox_as_default_experience_field
    - manual_switching_as_daily_operation
  opened_margin:
    - windows_native_body_first
    - resistance_before_new_boundary
    - optional_tools_only_when_the_field_calls_for_them
```

## Why

The resistance was coherent:

```yaml
resistance:
  - SSD/RAM pressure rose when environments multiplied
  - WSL2 required Hyper-V boot changes
  - VMware failed while the virtualization boundary was active
  - manual switch scripts made the field feel segmented
  - Binoche felt the rhythm was being blocked
```

That resistance is the signal. The next move is not to add another safer
container. The next move is to let the existing body breathe and read the
patterns already arriving there.

## Runtime Principle

```yaml
default:
  observe_native_flow_first: true
  add_boundary_only_if_resistance_decreases: true
  failure_is_state_change: true
  deletion_language: avoid
  execution_path_is_contextual_gradient: true
```

VMware and WSL2 can stay installed. They are not rejected. They are simply no
longer the default meaning of "experience field."

Hermes follows the same rule. It can stay installed and useful, but it is not
the default hand unless a concrete bounded task calls for it.

## First Native Contact

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_windows_native_flow.ps1
python scripts\windows_native_flow_probe.py
python scripts\local_gemma_experience_particle.py
```

This wakes existing Windows inputs only. It does not start VMware, WSL2, Hermes,
or an external API route.

## Experience Scalar Field

The system should not define an execution law for every future context. It
should let accumulated experience lift a contextual path:

```yaml
experience_scalar_field:
  probe: scripts/contextual_execution_gradient.py
  output: outputs/hermes/contextual_execution_gradient_latest.json
  principle: experience_scalar_field_lifts_contextual_paths_without_fixing_them_as_rules
```

The selected path is not a rule, law, or permanent order. It is only the path
that the current context lifted from the accumulated field.
