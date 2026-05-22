# Next Linux Experience Field Plan

Author: 코덱스 루빛
Date: 2026-05-05

## Purpose

This is a pending waypoint, not an active connection task.

Linux is the candidate experience field: a more independent environment where
Shion can run many reversible probes in parallel before any result is allowed
to touch the Windows operating body. It is not a place to bypass caution. It is
a second field where simulation can be wide while verified experience remains
small and observable.

## Current VM Evidence

```yaml
vm:
  name: AGI_Meta_OS
  vmx: D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmx
  vmdk: D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmdk
  vmdk_status: present
  guest_os: Ubuntu 24.04.3 LTS
  kernel_seen_in_vmx: 6.14.0-37-generic
  memory_mb: 16000
  cpu_count: 4
  network: nat
  shared_folders:
    - host: C:\workspace\agi
      guest: agi
    - host: C:\
      guest: C
    - host: D:\
      guest: D
    - host: E:\
      guest: E
  iso:
    ubuntu: D:\VMware_ISOs\ubuntu-24.04.3-desktop-amd64.iso
    autoinst: D:\Virtual Machines\AGI_Meta_OS\autoinst.iso
```

Earlier failure mode:

```yaml
failure:
  previous_observation: VMware failed to power on when memory was too high
  likely_cause: host_memory_pressure
  current_mitigation: memsize_lowered_to_16000
```

## Why Later

```yaml
reason:
  blender_playground: just_activated_as_visible_neural_field
  risk: connecting_linux_now_mixes_visual_field_validation_with_body_execution_debugging
  decision: hold_linux_as_pending_middle_destination
  reframing: linux_is_parallel_experience_field_not_immediate_action_body
```

## Next Session Activation Checklist

```yaml
activation_steps:
  - confirm_blender_playground_still_reflects_shion_state
  - power_on_AGI_Meta_OS_visibly_in_VMware
  - verify_linux_boot
  - verify_shared_folder_mounts
  - verify_network_nat
  - run_small_linux_command_probe
  - run_parallel_linux_experience_field_probe
  - only_then_connect_as_experience_field
```

## First Probe Commands

Run these only after the VM is visibly booted.

```powershell
cd /d C:\workspace2\shion
python scripts\linux_body_layer_probe.py
python scripts\linux_experience_field_probe.py
```

Expected outputs:

```yaml
outputs:
  json: outputs/linux_body_layer_waypoint.json
  experience_field_json: outputs/linux_experience_field_probe.json
```

## Guardrail

```yaml
do:
  - keep_linux_as_parallel_experience_field_candidate
  - verify_live_boot_before claiming connection
  - run one small probe before long-running services
  - run parallel probes only as reversible observations
  - preserve Blender as observation field
  - keep Hermes as a hand layer candidate before any autonomous authority

do_not:
  - reinstall Linux while VMDK is present
  - attach Linux to autonomous action loops immediately
  - treat Linux probes as permission for irreversible Windows actions
  - debug Linux and Blender instability at the same time
  - treat VM existence as experience-field activation
  - let Hermes write directly into the Windows workspace during first contact
```

## Parallel Experience Field

```yaml
principle:
  simulation: many candidates can run in parallel inside Linux
  experience: world contact must still be verified as observable particles
  bridge: compare Linux probe resistance with Windows runtime resistance
  output: record resistance, margin_opened, and experience_mode before action
```

Linux is the new field, not the new authority. It can create more experience
surface than Binoche can provide serially, but Shion should still read the
result as field contact: resistance, margin, phase rebalance, and possible
spiral turn.

## Hermes As Hand Layer

Hermes may become a useful hand layer for both Shion and Luvit after the Linux
experience field is stable. Its first role should be observer-hand: run bounded
Linux probes, search its own session history, and return experience particles
without directly mutating the Windows workspace.

Detailed contract:

```yaml
contract: docs/hermes_hand_layer_contract.md
first_permission: read_and_probe_inside_linux
first_output: outputs/hermes/experience_particles.jsonl
authority: hands_not_conductor
```
