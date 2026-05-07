#!/usr/bin/env python3
"""
Pending waypoint stub for the future Linux body layer.

This script does not connect to Linux yet. It records the VM evidence and the
next activation checklist so the task can be resumed without relying on human
memory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "outputs" / "linux_body_layer_waypoint.json"
PLAN = ROOT / "docs" / "next_linux_body_layer_plan.md"

VMX = Path(r"D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmx")
VMDK = Path(r"D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmdk")
UBUNTU_ISO = Path(r"D:\VMware_ISOs\ubuntu-24.04.3-desktop-amd64.iso")
AUTOINST_ISO = Path(r"D:\Virtual Machines\AGI_Meta_OS\autoinst.iso")


def main() -> int:
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "pending_middle_destination",
        "name": "linux_body_layer_pending",
        "meaning": "candidate independent body layer for future Shion action experiments",
        "plan": str(PLAN),
        "evidence": {
            "vmx": {"path": str(VMX), "exists": VMX.exists()},
            "vmdk": {"path": str(VMDK), "exists": VMDK.exists(), "bytes": VMDK.stat().st_size if VMDK.exists() else None},
            "ubuntu_iso": {"path": str(UBUNTU_ISO), "exists": UBUNTU_ISO.exists()},
            "autoinst_iso": {"path": str(AUTOINST_ISO), "exists": AUTOINST_ISO.exists()},
            "memory_mb_expected": 16000,
            "network_expected": "nat",
        },
        "next_condition": "after_blender_playground_is_observed_stable_then_boot_vm_visibly_and_probe",
        "activation_checklist": [
            "confirm_blender_playground_still_reflects_shion_state",
            "power_on_AGI_Meta_OS_visibly_in_VMware",
            "verify_linux_boot",
            "verify_shared_folder_mounts",
            "verify_network_nat",
            "run_small_linux_command_probe",
            "connect_as_body_layer_only_after_live_evidence",
        ],
        "guardrail": "do_not_reinstall_or_attach_to_autonomous_loops_before_live_boot_probe",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
