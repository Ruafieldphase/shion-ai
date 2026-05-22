#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "windows_native_flow_latest.json"
OUT_JSONL = OUT_DIR / "windows_native_flow.jsonl"

WINDOWS_OLLAMA = "http://192.168.119.1:11434"
LOOPBACK_URL = "http://127.0.0.1:57322/audio_phase.json"
FELT_STATE = ROOT / "outputs" / "felt_body_state.json"
PIVOT = OUT_DIR / "natural_flow_pivot_latest.json"


def _request_json(url: str, timeout: float = 2.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        return {"ok": True, "data": data}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "http_status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:500]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _run(command: list[str], timeout: float = 10.0) -> dict[str, Any]:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": command,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": command}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _compact_felt(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {"ok": False, "reason": "felt_state_missing"}
    return {
        "ok": True,
        "flow_energy": data.get("flow_energy"),
        "relation_drift": data.get("relation_drift"),
        "body_discomfort": data.get("body_discomfort"),
        "body_ease": data.get("body_ease"),
        "rhythm_continuity": data.get("rhythm_continuity"),
        "source": data.get("source"),
        "updated_at": data.get("updated_at"),
    }


def _process_probe() -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"ok": False, "skipped": "windows_process_probe_only"}
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process -Name ollama,python,pythonw,vmware,vmware-vmx -ErrorAction SilentlyContinue | "
        "Select-Object Name,Id,CPU,WorkingSet64 | ConvertTo-Json -Compress",
    ]
    result = _run(command, timeout=15)
    processes: Any = []
    if result.get("ok") and result.get("stdout"):
        try:
            processes = json.loads(result["stdout"])
        except json.JSONDecodeError:
            processes = []
    elif result.get("stdout"):
        try:
            processes = json.loads(result["stdout"])
        except json.JSONDecodeError:
            processes = []
    if isinstance(processes, dict):
        processes = [processes]
    return {"ok": bool(result.get("ok") or processes), "processes": processes, "raw": result}


def build_probe() -> dict[str, Any]:
    audio = _request_json(LOOPBACK_URL, timeout=1.0)
    tags = _request_json(f"{WINDOWS_OLLAMA}/api/tags", timeout=3.0)
    ps = _request_json(f"{WINDOWS_OLLAMA}/api/ps", timeout=3.0)
    felt = _compact_felt(_read_json(FELT_STATE))
    pivot = _read_json(PIVOT) or {}
    processes = _process_probe()

    audio_data = audio.get("data") if isinstance(audio.get("data"), dict) else {}
    pivot_margin = pivot.get("margin") if isinstance(pivot.get("margin"), dict) else {}
    resistance = []
    if not audio.get("ok"):
        resistance.append("audio_loopback_bridge_not_responding")
    if not felt.get("ok"):
        resistance.append("felt_body_state_missing")
    if not tags.get("ok"):
        resistance.append("windows_ollama_endpoint_not_responding")
    if processes.get("processes") and any(p.get("Name") == "vmware" for p in processes["processes"] if isinstance(p, dict)):
        resistance.append("vmware_gui_surface_open")

    status = "windows_native_flow_observed"
    if audio.get("ok") and tags.get("ok"):
        status = "windows_native_flow_ready"
    if resistance and not tags.get("ok"):
        status = "windows_native_flow_resistant"

    return {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "field": "windows_native_flow",
        "platform": platform.system(),
        "audio_loopback": {
            "ok": audio.get("ok"),
            "enabled": audio_data.get("enabled"),
            "envelope": audio_data.get("envelope"),
            "onset": audio_data.get("onset"),
            "confidence": audio_data.get("confidence"),
            "bass": audio_data.get("bass"),
            "brightness": audio_data.get("brightness"),
            "error": audio.get("error") or audio_data.get("error"),
        },
        "felt_body": felt,
        "windows_ollama": {
            "ok": tags.get("ok"),
            "models": [
                item.get("name")
                for item in tags.get("data", {}).get("models", [])
                if isinstance(item, dict) and item.get("name")
            ][:16]
            if isinstance(tags.get("data"), dict)
            else [],
            "loaded": ps.get("data", {}).get("models", []) if isinstance(ps.get("data"), dict) else [],
        },
        "processes": processes,
        "resistance": resistance,
        "margin": {
            "opened": bool(pivot_margin.get("opened", True)),
            "description": pivot_margin.get(
                "description",
                "Read the existing Windows native field before adding another runtime boundary.",
            ),
        },
        "next_particle": {
            "action": "observe_existing_inputs",
            "meaning": "Use loopback, felt body, and Windows Ollama as the first contact surface.",
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "principle": "native_flow_first_optional_tools_only_when_resistance_decreases",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_probe()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] != "windows_native_flow_resistant" else 2


if __name__ == "__main__":
    raise SystemExit(main())
