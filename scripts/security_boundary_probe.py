#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from security_boundary_probe import build_security_boundary_state


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "security_boundary_latest.json"
OUT_JSONL = OUT_DIR / "security_boundary.jsonl"
OUT_MD = OUT_DIR / "security_boundary_latest.md"

HASH_LIMIT_BYTES = 2_000_000


def _run(command: List[str], timeout: float = 20.0) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": command,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": command}


def _run_powershell(script: str, timeout: float = 20.0) -> Dict[str, Any]:
    return _run(["powershell", "-NoProfile", "-Command", script], timeout=timeout)


def _parse_json_output(result: Dict[str, Any]) -> Any:
    if not result.get("ok") or not result.get("stdout"):
        return []
    try:
        value = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return []
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _git_changes() -> List[Dict[str, Any]]:
    result = _run(["git", "status", "--porcelain=v1"], timeout=20)
    rows: List[Dict[str, Any]] = []
    for line in str(result.get("stdout", "")).splitlines():
        if not line:
            continue
        status = line[:2].strip() or line[:2]
        path_text = line[3:] if len(line) > 3 else ""
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        path = ROOT / path_text
        rows.append(
            {
                "status": status,
                "path": path_text,
                "sha256": _hash_file(path),
                "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
            }
        )
    return rows


def _hash_file(path: Path) -> str:
    try:
        if not path.exists() or not path.is_file() or path.stat().st_size > HASH_LIMIT_BYTES:
            return ""
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return ""


def _processes() -> List[Dict[str, Any]]:
    script = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.Name -in @('python.exe','pythonw.exe','ollama.exe') } | "
        "Select-Object @{n='pid';e={$_.ProcessId}},@{n='name';e={$_.Name}},"
        "@{n='path';e={$_.ExecutablePath}},@{n='command_line';e={$_.CommandLine}} | "
        "ConvertTo-Json -Compress"
    )
    return _parse_json_output(_run_powershell(script, timeout=20))


def _listeners() -> List[Dict[str, Any]]:
    script = (
        "$procs = @{}; "
        "Get-CimInstance Win32_Process | ForEach-Object { $procs[[int]$_.ProcessId] = $_.Name }; "
        "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | "
        "Select-Object @{n='local_address';e={$_.LocalAddress}},@{n='local_port';e={$_.LocalPort}},"
        "@{n='owning_process';e={$_.OwningProcess}},@{n='process_name';e={$procs[[int]$_.OwningProcess]}} | "
        "ConvertTo-Json -Compress"
    )
    return _parse_json_output(_run_powershell(script, timeout=25))


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _latest_jsonl(path: Path) -> Dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        return value if isinstance(value, dict) else {}
    return {}


def _trace_observations() -> Dict[str, Any]:
    return {
        "boundary_aperture": _read_json(OUT_DIR / "boundary_aperture_latest.json"),
        "contextual_gradient": _read_json(OUT_DIR / "contextual_execution_gradient_latest.json"),
        "field_prediction": _latest_jsonl(ROOT / "outputs" / "field_prediction_errors.jsonl"),
        "experience_feedback": _latest_jsonl(ROOT / "outputs" / "experience_feedback.jsonl"),
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    signals = payload["signals"]
    readings = payload["readings"]
    lines = [
        "# Security Boundary Probe",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Next action: `{payload['next_contact']['action']}`",
        f"- Not an intrusion claim: `{payload['not_an_intrusion_claim']}`",
        "",
        "## Signals",
        "",
        "| Signal | Value |",
        "|---|---:|",
    ]
    for key in ("ambiguity", "intrusion_pressure", "verification_need"):
        lines.append(f"| `{key}` | `{signals[key]}` |")
    lines.extend(
        [
            "",
            "## Surfaces",
            "",
            f"- File changes: `{readings['files']['total_changes']}`",
            f"- Sensitive paths: `{len(readings['files']['sensitive_paths'])}`",
            f"- Runtime processes: `{readings['processes']['expected_runtime_processes']}` expected / `{readings['processes']['unknown_processes']}` unknown",
            f"- Listeners: `{readings['listeners']['total_listeners']}` total / `{readings['listeners']['unexpected_external_listeners']}` unexpected external",
            f"- Boundary mode: `{readings['traces']['boundary_mode']}`",
            "",
            "## Meaning",
            "",
            payload["next_contact"]["meaning"],
            "",
            "This probe does not block, delete, quarantine, or claim an intrusion. It separates sources so internal metabolism is not confused with external contact.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload() -> Dict[str, Any]:
    state = build_security_boundary_state(
        file_changes=_git_changes(),
        process_observations=_processes(),
        listener_observations=_listeners(),
        trace_observations=_trace_observations(),
    )
    state["collector"] = {
        "timestamp": datetime.now().isoformat(),
        "hash_limit_bytes": HASH_LIMIT_BYTES,
        "workspace": str(ROOT),
        "writes_outputs_only": True,
    }
    return state


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    _write_markdown(payload)
    print(json.dumps({"status": payload["status"], "mode": payload["mode"], "next_contact": payload["next_contact"]}, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
