#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "linux_experience_forager_latest.json"
OUT_JSONL = OUT_DIR / "linux_experience_forager.jsonl"


def _run(command: list[str], timeout: float = 6.0) -> Dict[str, Any]:
    started = time.perf_counter()
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
            "stdout": proc.stdout.strip()[:1600],
            "stderr": proc.stderr.strip()[:800],
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }


def _path_texture(paths: list[Path]) -> Dict[str, Any]:
    items = []
    for path in paths:
        exists = path.exists()
        items.append(
            {
                "path": str(path),
                "exists": exists,
                "is_dir": path.is_dir() if exists else False,
                "children_sample": sorted(item.name for item in path.iterdir())[:10] if exists and path.is_dir() else [],
            }
        )
    return {"ok": any(item["exists"] for item in items), "items": items}


def _workspace_particles() -> Dict[str, Any]:
    files = sorted(OUT_DIR.glob("*.json*"), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)[:12]
    return {
        "ok": OUT_DIR.exists(),
        "dir": str(OUT_DIR),
        "files": [
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }
            for path in files
        ],
    }


def _ollama_bridge() -> Dict[str, Any]:
    url = "http://192.168.119.1:11434/api/tags"
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        return {
            "ok": True,
            "url": url,
            "models": [item.get("name") for item in data.get("models", []) if item.get("name")],
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "error": str(exc),
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }


def _host_pulse() -> Dict[str, Any]:
    load = os.getloadavg() if hasattr(os, "getloadavg") else None
    return {
        "ok": True,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cwd": str(Path.cwd()),
        "loadavg": load,
        "uptime": _run(["uptime"], timeout=3.0),
    }


def _hermes_status() -> Dict[str, Any]:
    hermes = Path.home() / ".local" / "bin" / "hermes"
    if not hermes.exists():
        return {"ok": False, "error": "hermes command not found", "path": str(hermes)}
    result = _run([str(hermes), "status"], timeout=10.0)
    stdout = result.get("stdout", "")
    result["stdout"] = stdout.replace("AIza", "[redacted-google-prefix]")
    return result


def _process_surface() -> Dict[str, Any]:
    return _run(["bash", "-lc", "ps -u \"$USER\" -o pid,comm,etime,%cpu,%mem --sort=-%cpu | head -12"], timeout=5.0)


@dataclass(frozen=True)
class Probe:
    name: str
    weight: float
    run: Callable[[], Dict[str, Any]]


PROBES: list[Probe] = [
    Probe("host_pulse", 0.75, _host_pulse),
    Probe("shared_mount_texture", 1.0, lambda: _path_texture([Path("/home/bino/C"), ROOT, Path("/mnt/hgfs/C")])),
    Probe("workspace_particles", 1.1, _workspace_particles),
    Probe("hermes_hand_status", 0.9, _hermes_status),
    Probe("ollama_bridge_visibility", 1.25, _ollama_bridge),
    Probe("process_surface", 0.65, _process_surface),
]


def _history() -> list[Dict[str, Any]]:
    if not OUT_JSONL.exists():
        return []
    rows: list[Dict[str, Any]] = []
    for line in OUT_JSONL.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _signature(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _choose_probe(history: list[Dict[str, Any]]) -> Probe:
    counts = {probe.name: 0 for probe in PROBES}
    last_seen = {probe.name: -1 for probe in PROBES}
    recent_failures = {probe.name: 0 for probe in PROBES}
    for idx, row in enumerate(history):
        name = row.get("probe")
        if name in counts:
            counts[name] += 1
            last_seen[name] = idx
            if not row.get("result", {}).get("ok"):
                recent_failures[name] += 1

    size = max(1, len(history))
    best: tuple[float, Probe] | None = None
    for probe in PROBES:
        absence = 1.0 / (1.0 + counts[probe.name])
        recency = 1.0 if last_seen[probe.name] < 0 else (size - last_seen[probe.name]) / size
        resistance_pull = min(0.75, recent_failures[probe.name] * 0.12)
        score = probe.weight + absence + recency + resistance_pull
        if best is None or score > best[0]:
            best = (score, probe)
    assert best is not None
    return best[1]


def _particle(probe: Probe, result: Dict[str, Any], history: list[Dict[str, Any]]) -> Dict[str, Any]:
    resistance = 0.0 if result.get("ok") else 1.0
    slow = float(result.get("duration_ms", 0) or 0) > 3000.0
    if slow:
        resistance = max(resistance, 0.35)
    signature = _signature({"probe": probe.name, "ok": result.get("ok"), "result": result})
    novelty = signature not in {str(item.get("signature")) for item in history[-80:]}
    margin_opened = bool(resistance or novelty)
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "linux_experience_foraged",
        "source": "linux_experience_forager",
        "probe": probe.name,
        "signature": signature,
        "result": result,
        "field_reading": {
            "resistance": resistance,
            "novelty": novelty,
            "margin_opened": margin_opened,
            "experience_mode": "self_selected_reversible_contact",
        },
        "irreversible_effect": False,
        "next_selection": "field_weighted_by_absence_recency_resistance",
        "principle": "linux_sandbox_accumulates_experience_by_curiosity_not_clock_control",
    }


def _write(row: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _windows_pending() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "pending_linux_sandbox",
        "source": "linux_experience_forager",
        "platform": platform.platform(),
        "meaning": "Run this inside Ubuntu so the experience field can choose its own reversible contacts.",
        "irreversible_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Let Linux choose one reversible experience probe from field pressure.")
    parser.add_argument("--steps", type=int, default=1, help="Number of self-selected contacts to accumulate.")
    parser.add_argument("--rest-min", type=float, default=2.0, help="Minimum rest between contacts when steps > 1.")
    parser.add_argument("--rest-max", type=float, default=12.0, help="Maximum rest between contacts when steps > 1.")
    args = parser.parse_args()

    if platform.system().lower() != "linux":
        row = _windows_pending()
        _write(row)
        print(json.dumps(row, ensure_ascii=False))
        return 2

    last: Dict[str, Any] | None = None
    for step in range(max(1, args.steps)):
        history = _history()
        probe = _choose_probe(history)
        result = probe.run()
        row = _particle(probe, result, history)
        row["step"] = step + 1
        row["steps_requested"] = max(1, args.steps)
        _write(row)
        print(json.dumps(row, ensure_ascii=False))
        last = row
        if step + 1 < max(1, args.steps):
            resistance = row["field_reading"]["resistance"]
            rest = args.rest_min + (args.rest_max - args.rest_min) * min(1.0, resistance)
            time.sleep(rest)
    return 0 if last and last["status"] == "linux_experience_foraged" else 2


if __name__ == "__main__":
    raise SystemExit(main())

