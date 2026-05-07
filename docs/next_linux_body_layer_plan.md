# Next Linux Body Layer Plan

Author: 코덱스 루빛
Date: 2026-05-05

## Purpose

This is a pending waypoint, not an active connection task.

Linux is the candidate body layer: a more independent execution environment
where Shion can later run long-lived tools, network/server experiments, and
failure-to-learning loops without overloading the Windows/Blender observation
layer.

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
  - only_then_connect_as_body_layer
```

## First Probe Commands

Run these only after the VM is visibly booted.

```powershell
cd /d C:\workspace2\shion
python scripts\linux_body_layer_probe.py
```

Expected outputs:

```yaml
outputs:
  json: outputs/linux_body_layer_waypoint.json
```

## Guardrail

```yaml
do:
  - keep_linux_as_action_body_candidate
  - verify_live_boot_before claiming connection
  - run one small probe before long-running services
  - preserve Blender as observation field

do_not:
  - reinstall Linux while VMDK is present
  - attach Linux to autonomous action loops immediately
  - debug Linux and Blender instability at the same time
  - treat VM existence as body-layer activation
```
