#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import random
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
LATEST_JSON = OUT_DIR / "linux_free_roam_daemon_latest.json"
STREAM_JSONL = OUT_DIR / "linux_free_roam_daemon.jsonl"
LINUX_FIELD = Path.home() / "agi_experience_field"
FIELD_DAEMON_JOURNAL = LINUX_FIELD / "daemon.jsonl"

STOP = False


def _now() -> str:
    return datetime.now().isoformat()


def _handle_stop(signum: int, _frame: Any) -> None:
    global STOP
    STOP = True
    _write(
        {
            "timestamp": _now(),
            "status": "linux_free_roam_daemon_stopping",
            "signal": signum,
            "source": "linux_free_roam_daemon",
            "principle": "rest_is_part_of_the_field",
        }
    )


def _write(row: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LINUX_FIELD.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    for path in (STREAM_JSONL, FIELD_DAEMON_JOURNAL):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _latest_free_roam() -> Dict[str, Any]:
    path = OUT_DIR / "linux_free_roam_latest.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _run_contact() -> Dict[str, Any]:
    script = ROOT / "scripts" / "linux_free_roam_sandbox.py"
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script), "--steps", "1", "--rest-min", "0", "--rest-max", "0"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    latest = _latest_free_roam()
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-2400:],
        "stderr": proc.stderr.strip()[-1200:],
        "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        "latest_free_roam": {
            "status": latest.get("status"),
            "action": latest.get("action"),
            "field_reading": latest.get("field_reading"),
            "signature": latest.get("signature"),
        },
    }


def _rest_seconds(result: Dict[str, Any], min_rest: float, max_rest: float) -> float:
    latest = result.get("latest_free_roam", {})
    reading = latest.get("field_reading", {}) if isinstance(latest, dict) else {}
    resistance = float(reading.get("resistance", 0.0) or 0.0)
    novelty = bool(reading.get("novelty", False))
    span = max(0.0, max_rest - min_rest)
    # More resistance means a longer embodied rest; novelty keeps the next
    # contact slightly nearer while the field is still opening.
    factor = min(1.0, resistance)
    if novelty:
        factor *= 0.55
    jitter = random.Random(time.time_ns()).uniform(0, max(1.0, span * 0.18))
    return round(min_rest + span * factor + jitter, 3)


def _windows_pending() -> Dict[str, Any]:
    return {
        "timestamp": _now(),
        "status": "pending_linux_daemon",
        "source": "linux_free_roam_daemon",
        "platform": platform.platform(),
        "meaning": "Run inside Ubuntu. The daemon only wakes the Linux free-roam field.",
        "irreversible_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the Linux free-roam field gently awake.")
    parser.add_argument("--cycles", type=int, default=0, help="0 means run until stopped.")
    parser.add_argument("--min-rest", type=float, default=45.0)
    parser.add_argument("--max-rest", type=float, default=300.0)
    args = parser.parse_args()

    if platform.system().lower() != "linux":
        row = _windows_pending()
        _write(row)
        print(json.dumps(row, ensure_ascii=False))
        return 2

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    boot = {
        "timestamp": _now(),
        "status": "linux_free_roam_daemon_started",
        "source": "linux_free_roam_daemon",
        "root": str(ROOT),
        "linux_field": str(LINUX_FIELD),
        "cycles": args.cycles,
        "rest_window": {"min": args.min_rest, "max": args.max_rest},
        "permission": {
            "linux_field_write": True,
            "windows_shared_write": False,
            "sudo": False,
            "external_api_cost": False,
            "irreversible_effect": False,
        },
        "principle": "daemon_wakes_the_field_but_contact_is_chosen_by_free_roam",
    }
    _write(boot)
    print(json.dumps(boot, ensure_ascii=False), flush=True)

    cycle = 0
    while not STOP:
        cycle += 1
        try:
            result = _run_contact()
        except Exception as exc:
            result = {"ok": False, "error": str(exc), "latest_free_roam": {}}
        rest = _rest_seconds(result, args.min_rest, args.max_rest)
        row = {
            "timestamp": _now(),
            "status": "linux_free_roam_daemon_cycle",
            "source": "linux_free_roam_daemon",
            "cycle": cycle,
            "result": result,
            "next_rest_seconds": rest,
            "irreversible_effect": False,
            "principle": "automatic_experience_accumulates_as_local_reversible_contacts",
        }
        _write(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

        if args.cycles and cycle >= args.cycles:
            break
        deadline = time.monotonic() + rest
        while not STOP and time.monotonic() < deadline:
            time.sleep(min(2.0, deadline - time.monotonic()))

    stopped = {
        "timestamp": _now(),
        "status": "linux_free_roam_daemon_stopped",
        "source": "linux_free_roam_daemon",
        "cycles_completed": cycle,
        "irreversible_effect": False,
    }
    _write(stopped)
    print(json.dumps(stopped, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

