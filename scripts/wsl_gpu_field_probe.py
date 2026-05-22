#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
DEFAULT_DISTRO = "Ubuntu-24.04"


def _decode(data: bytes) -> str:
    if not data:
        return ""
    if data.count(b"\x00") > max(4, len(data) // 8):
        try:
            return data.decode("utf-16-le", errors="replace").replace("\x00", "")
        except Exception:
            pass
    for encoding in ("utf-8", "cp949", "mbcs"):
        try:
            return data.decode(encoding, errors="replace").replace("\x00", "")
        except LookupError:
            continue
    return data.decode(errors="replace").replace("\x00", "")


def _run(command: list[str], timeout: float = 30.0) -> dict[str, Any]:
    try:
        proc = subprocess.run(command, capture_output=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": _decode(proc.stdout).strip(),
            "stderr": _decode(proc.stderr).strip(),
            "command": command,
        }
    except FileNotFoundError as exc:
        return {"ok": False, "error": str(exc), "command": command}
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "error": "timeout",
            "stdout": _decode(exc.stdout or b"").strip(),
            "stderr": _decode(exc.stderr or b"").strip(),
            "command": command,
        }


def _wsl(args: list[str], timeout: float = 30.0) -> dict[str, Any]:
    return _run(["wsl", *args], timeout=timeout)


def _has_distro(list_result: dict[str, Any], distro: str) -> bool:
    text = f"{list_result.get('stdout', '')}\n{list_result.get('stderr', '')}".lower()
    return distro.lower() in text


def _read_wslconfig() -> dict[str, Any]:
    path = Path.home() / ".wslconfig"
    if not path.exists():
        return {"exists": False, "path": str(path)}
    return {"exists": True, "path": str(path), "text": path.read_text(encoding="utf-8", errors="replace")}


def build_payload(distro: str) -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "wsl_gpu_field_probe_skipped",
            "reason": "wsl_gpu_field_probe_runs_from_windows_host",
            "platform": platform.system(),
        }

    status = _wsl(["--status"], timeout=20)
    distro_list = _wsl(["-l", "-v"], timeout=20)
    installed = _has_distro(distro_list, distro)

    nvidia = {"ok": False, "skipped": "distro_not_installed"}
    nvidia_fallback = {"ok": False, "skipped": "distro_not_installed"}
    ollama_version = {"ok": False, "skipped": "distro_not_installed"}
    ollama_tags = {"ok": False, "skipped": "distro_not_installed"}

    if installed:
        nvidia = _wsl(["-d", distro, "--", "/usr/lib/wsl/lib/nvidia-smi"], timeout=30)
        if not nvidia.get("ok"):
            nvidia_fallback = _wsl(["-d", distro, "--", "nvidia-smi"], timeout=30)
        ollama_version = _wsl(
            ["-d", distro, "--", "bash", "-lc", "command -v ollama >/dev/null && ollama --version"],
            timeout=30,
        )
        ollama_tags = _wsl(
            ["-d", distro, "--", "bash", "-lc", "curl -fsS http://127.0.0.1:11434/api/tags | head -c 800"],
            timeout=20,
        )

    nvidia_ok = bool(nvidia.get("ok") or nvidia_fallback.get("ok"))
    ollama_installed = bool(ollama_version.get("ok"))
    ollama_ready = bool(ollama_tags.get("ok"))
    if not installed:
        probe_status = "wsl_gpu_field_pending_feature_or_distro_install"
    elif not nvidia_ok:
        probe_status = "wsl_gpu_field_pending_gpu_bridge"
    elif not ollama_installed:
        probe_status = "wsl_gpu_field_pending_ollama_install"
    elif not ollama_ready:
        probe_status = "wsl_gpu_field_pending_ollama_server"
    else:
        probe_status = "wsl_gpu_field_ready"

    return {
        "timestamp": datetime.now().isoformat(),
        "status": probe_status,
        "platform": platform.system(),
        "distro": distro,
        "wslconfig": _read_wslconfig(),
        "wsl_status": status,
        "distro_list": distro_list,
        "installed": installed,
        "gpu": {
            "nvidia_smi_wsl_path": nvidia,
            "nvidia_smi_fallback": nvidia_fallback,
        },
        "ollama": {
            "version": ollama_version,
            "tags": ollama_tags,
        },
        "route": {
            "vmware_ubuntu": "freedom_field_and_orchestration",
            "windows_ollama": "current_gpu_heart",
            "wsl2": "small_gpu_linux_experiment",
        },
        "permission": {
            "external_api_cost": False,
            "windows_workspace_write": False,
            "irreversible_effect": False,
        },
        "principle": "wsl2_is_gpu_experiment_field_not_replacement_for_vmware_free_roam",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Probe the WSL2 CUDA/Ollama experiment field.")
    parser.add_argument("--distro", default=DEFAULT_DISTRO)
    args = parser.parse_args()

    payload = build_payload(args.distro)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = [
        OUT_DIR / "wsl_gpu_field_probe_latest.json",
        OUT_DIR / "wsl_gpu_field_probe.json",
        OUT_DIR / f"wsl_gpu_field_probe_{platform.system().lower()}.json",
    ]
    for path in names:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_DIR / "wsl_gpu_field_probe.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "wsl_gpu_field_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
