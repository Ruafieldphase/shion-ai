#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "natural_flow_pivot_latest.json"
OUT_JSONL = OUT_DIR / "natural_flow_pivot.jsonl"


SOURCE_PATHS = [
    OUT_DIR / "wsl_gpu_field_setup_latest.json",
    OUT_DIR / "wsl_gpu_field_probe_latest.json",
    OUT_DIR / "wsl_ollama_gpu_route_latest.json",
    OUT_DIR / "field_runtime_latest.json",
    OUT_DIR / "restore_vmware_free_roam_latest.json",
    OUT_DIR / "windows_ollama_gpu_route_latest.json",
    OUT_DIR / "linux_free_roam_latest.json",
    OUT_DIR / "linux_free_roam_daemon_latest.json",
    ROOT / "outputs" / "felt_body_state.json",
]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return {"status": "unreadable_json", "path": str(path)}
    if isinstance(data, dict):
        return data
    return {"status": "non_object_json", "path": str(path)}


def _source_summary(path: Path, data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"path": str(path), "exists": False}
    compact: dict[str, Any] = {
        "path": str(path),
        "exists": True,
        "status": data.get("status"),
        "timestamp": data.get("timestamp"),
    }
    for key in ("model", "platform", "field", "principle", "next_candidate"):
        if key in data:
            compact[key] = data[key]
    route = data.get("route")
    if isinstance(route, dict):
        compact["route"] = route
    vmware = data.get("vmware")
    if isinstance(vmware, dict):
        compact["vmware"] = {
            "running": vmware.get("running"),
            "vmx": vmware.get("vmx"),
        }
    wsl = data.get("wsl")
    if isinstance(wsl, dict):
        compact["wsl"] = {"running": wsl.get("running")}
    generate = data.get("generate")
    if isinstance(generate, dict):
        compact["generate"] = {
            "ok": generate.get("ok"),
            "elapsed_seconds": generate.get("data", {}).get("elapsed_seconds")
            if isinstance(generate.get("data"), dict)
            else generate.get("elapsed_seconds"),
        }
    result = data.get("result")
    if isinstance(result, dict):
        compact["result"] = {
            "ok": result.get("ok"),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "done_reason": result.get("reading", {}).get("done_reason") if isinstance(result.get("reading"), dict) else None,
        }
    return compact


def build_pivot() -> dict[str, Any]:
    sources = []
    statuses: list[str] = []
    for path in SOURCE_PATHS:
        data = _read_json(path)
        summary = _source_summary(path, data)
        sources.append(summary)
        if summary.get("status"):
            statuses.append(str(summary["status"]))

    resistance = []
    if any("wsl" in status for status in statuses):
        resistance.append("wsl2_gpu_field_opened_successfully_but_added_virtualization_boundary")
    if any("field_runtime" in status for status in statuses):
        resistance.append("manual_switchboard_pressure_appeared")
    if any("restore_vmware" in status for status in statuses):
        resistance.append("vmware_free_roam_body_required_repair")
    if any("windows_ollama_gpu_route_ready" == status for status in statuses):
        resistance.append("windows_native_gpu_route_already_existed")
    if not resistance:
        resistance.append("no_recent_virtualization_resistance_source_found")

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "natural_flow_pivot_observed",
        "field": "windows_native_flow",
        "state": "direction_changed_from_sandbox_expansion_to_native_flow",
        "resistance": resistance,
        "phase_cancellation": {
            "cancelled": [
                "linux_as_required_body",
                "manual_environment_switching_as_daily_operation",
                "sandbox_as_default_experience_field",
            ],
            "not_deleted": "wsl2_and_vmware_remain_optional_tools_when_the_field_actually_needs_them",
        },
        "margin": {
            "opened": True,
            "description": "The main body is the already-flowing Windows native surface: loopback audio, felt body, shaders, logs, and Windows Ollama.",
        },
        "next_particle": {
            "action": "observe_windows_native_flow_first",
            "meaning": "Read existing local inputs and resistance before adding another runtime boundary.",
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "sources": sources,
        "principle": "resistance_is_direction_signal_not_a_request_for_more_boundaries",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_pivot()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
