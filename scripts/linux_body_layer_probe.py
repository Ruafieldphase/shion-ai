#!/usr/bin/env python3
"""
Pending waypoint stub for the future Linux body layer.

This script does not connect to Linux yet. It records the VM evidence and the
next activation checklist so the task can be resumed without relying on human
memory.
"""

from __future__ import annotations

import json
import platform
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
    running_platform = platform.system().lower()
    is_linux_guest = running_platform == "linux"
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "linux_guest_observed_pending_body_connection" if is_linux_guest else "pending_middle_destination",
        "name": "linux_body_layer_pending",
        "meaning": "candidate independent body layer for future Shion action experiments; currently preferred as parallel experience field first",
        "plan": str(PLAN),
        "platform": platform.platform(),
        "evidence": {
            "vmx": {
                "path": str(VMX),
                "exists": VMX.exists() if not is_linux_guest else None,
                "note": None if not is_linux_guest else "windows_host_path_not_visible_from_linux_guest",
            },
            "vmdk": {
                "path": str(VMDK),
                "exists": VMDK.exists() if not is_linux_guest else None,
                "bytes": VMDK.stat().st_size if VMDK.exists() and not is_linux_guest else None,
                "note": None if not is_linux_guest else "windows_host_path_not_visible_from_linux_guest",
            },
            "ubuntu_iso": {"path": str(UBUNTU_ISO), "exists": UBUNTU_ISO.exists() if not is_linux_guest else None},
            "autoinst_iso": {"path": str(AUTOINST_ISO), "exists": AUTOINST_ISO.exists() if not is_linux_guest else None},
            "memory_mb_expected": 16000,
            "network_expected": "nat",
            "guest_observed": is_linux_guest,
            "workspace_path": str(ROOT),
            "workspace_exists": ROOT.exists(),
        },
        "next_condition": "use_linux_as_parallel_experience_field_before_connecting_as_body_layer",
        "activation_checklist": [
            "confirm_blender_playground_still_reflects_shion_state",
            "power_on_AGI_Meta_OS_visibly_in_VMware",
            "verify_linux_boot",
            "verify_shared_folder_mounts",
            "verify_network_nat",
            "run_small_linux_command_probe",
            "run_parallel_linux_experience_field_probe",
            "connect_as_body_layer_only_after_experience_field_evidence",
        ],
        "guardrail": "do_not_attach_to_autonomous_action_loops_before_parallel_experience_field_resistance_is_observed",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
