#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "outputs" / "linux_experience_field_probe.json"
VMX = Path(r"D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmx")
VMDK = Path(r"D:\Virtual Machines\AGI_Meta_OS\AGI_Meta_OS.vmdk")


def _run(command: list[str], *, timeout: float = 5.0) -> Dict[str, Any]:
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
            "stdout": proc.stdout.strip()[:1200],
            "stderr": proc.stderr.strip()[:1200],
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }


def _path_probe(path: Path) -> Dict[str, Any]:
    started = time.perf_counter()
    exists = path.exists()
    return {
        "ok": exists,
        "path": str(path),
        "exists": exists,
        "is_dir": path.is_dir() if exists else False,
        "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def _clock_probe() -> Dict[str, Any]:
    samples = []
    last = time.perf_counter()
    for _ in range(5):
        time.sleep(0.02)
        now = time.perf_counter()
        samples.append(now - last)
        last = now
    return {
        "ok": True,
        "intervals_ms": [round(item * 1000.0, 3) for item in samples],
        "jitter_ms": round((max(samples) - min(samples)) * 1000.0, 3),
    }


def _host_probe() -> Dict[str, Any]:
    return {
        "ok": True,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
    }


def _write_payload(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _windows_pending_payload() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "pending_linux_experience_field",
        "name": "linux_experience_field_pending",
        "meaning": "Linux is reserved as a parallel experience field, not a direct autonomous action body.",
        "host_platform": platform.platform(),
        "wsl_available": False,
        "vm_evidence": {
            "vmx": {"path": str(VMX), "exists": VMX.exists()},
            "vmdk": {"path": str(VMDK), "exists": VMDK.exists(), "bytes": VMDK.stat().st_size if VMDK.exists() else None},
        },
        "activation_condition": "boot AGI_Meta_OS, verify shared folders and network, then run this probe inside Linux",
        "linux_command": "python3 /home/bino/C/workspace2/shion/scripts/linux_experience_field_probe.py",
        "principle": "parallel_simulation_many_candidates_linear_experience_only_after_world_contact",
    }


def _linux_parallel_payload() -> Dict[str, Any]:
    probes: dict[str, Callable[[], Dict[str, Any]]] = {
        "host": _host_probe,
        "kernel": lambda: _run(["uname", "-a"]),
        "python": lambda: _run([sys.executable, "--version"]),
        "workspace_mount": lambda: _path_probe(ROOT),
        "shared_c_home": lambda: _path_probe(Path("/home/bino/C")),
        "shared_c_hgfs": lambda: _path_probe(Path("/mnt/hgfs/C")),
        "network_dns": lambda: _run(["python3", "-c", "import socket; print(socket.gethostbyname('localhost'))"]),
        "clock_jitter": _clock_probe,
    }
    results: Dict[str, Any] = {}
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(8, len(probes))) as pool:
        futures = {pool.submit(func): name for name, func in probes.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = {"ok": False, "error": str(exc)}

    ok_count = sum(1 for item in results.values() if item.get("ok"))
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "linux_experience_field_observed",
        "name": "linux_experience_field",
        "meaning": "parallel probes create a field of experience candidates before any irreversible action is allowed",
        "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        "parallel_probe_count": len(probes),
        "ok_count": ok_count,
        "results": results,
        "field_reading": {
            "resistance": round(1.0 - ok_count / max(1, len(probes)), 6),
            "margin_opened": ok_count < len(probes),
            "experience_mode": "parallel_simulation_field",
        },
        "principle": "ai_can_parallelize_simulation_but_world_experience_particleizes_as_verified_contact",
    }


def main() -> int:
    if platform.system().lower() != "linux":
        payload = _windows_pending_payload()
    else:
        payload = _linux_parallel_payload()
    _write_payload(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] != "pending_linux_experience_field" else 2


if __name__ == "__main__":
    raise SystemExit(main())
