#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"


def _run(command: list[str], timeout: float = 5.0) -> Dict[str, Any]:
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
            "stdout": _sanitize(proc.stdout.strip()[:2000]),
            "stderr": _sanitize(proc.stderr.strip()[:2000]),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _sanitize(text: str) -> str:
    text = re.sub(r"AIza[0-9A-Za-z_\-\.]*", "[redacted-google-api-key]", text)
    text = re.sub(r"(GOOGLE_API_KEY|GEMINI_API_KEY)=\S+", r"\1=[redacted]", text)
    return text


def _file_meta(path: Path) -> Dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "bytes": path.stat().st_size if exists and path.is_file() else None,
    }


def _env_present(name: str) -> bool:
    return bool(os.environ.get(name))


def _env_file_has_key(path: Path, name: str) -> bool:
    if not path.exists():
        return False
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(f"{name}=") and line.split("=", 1)[1].strip():
                return True
    except OSError:
        return False
    return False


def _config_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _local_ollama_configured(config_text: str) -> bool:
    return (
        'provider: "custom"' in config_text
        and "127.0.0.1:11434" in config_text
        and ("gemma3:1b" in config_text or "llama3.2:latest" in config_text)
    )


def _home_paths() -> Dict[str, Path]:
    home = Path.home()
    return {
        "hermes_config": home / ".hermes" / "config.yaml",
        "hermes_env": home / ".hermes" / ".env",
        "gcloud_adc": home / ".config" / "gcloud" / "application_default_credentials.json",
    }


def _credential_reading(paths: Dict[str, Path]) -> Dict[str, Any]:
    has_google_api_key = _env_present("GOOGLE_API_KEY") or _env_file_has_key(paths["hermes_env"], "GOOGLE_API_KEY")
    has_gemini_api_key = _env_present("GEMINI_API_KEY") or _env_file_has_key(paths["hermes_env"], "GEMINI_API_KEY")
    has_adc = paths["gcloud_adc"].exists() or _env_present("GOOGLE_APPLICATION_CREDENTIALS")
    return {
        "api_key_env_present": {
            "GOOGLE_API_KEY": has_google_api_key,
            "GEMINI_API_KEY": has_gemini_api_key,
        },
        "official_oauth_adc_present": has_adc,
        "hermes_oauth_provider": {
            "provider": "google-gemini-cli",
            "requires_interactive_browser_flow": True,
            "recommended_for_unattended_hand_layer": False,
        },
        "recommended_provider": "custom_ollama",
        "recommended_model": "gemma3:1b",
        "recommended_base_url": "http://127.0.0.1:11434/v1",
    }


def _hermes_reading() -> Dict[str, Any]:
    hermes = shutil.which("hermes")
    if not hermes:
        local_hermes = Path.home() / ".local" / "bin" / "hermes"
        if local_hermes.exists():
            hermes = str(local_hermes)
    reading: Dict[str, Any] = {"command": hermes, "installed": bool(hermes)}
    if hermes:
        reading["version"] = _run([hermes, "--version"], timeout=5.0)
        reading["status"] = _run([hermes, "status"], timeout=8.0)
    return reading


def build_payload() -> Dict[str, Any]:
    paths = _home_paths()
    credentials = _credential_reading(paths)
    hermes = _hermes_reading()
    has_api_key = any(credentials["api_key_env_present"].values())
    config_text = _config_text(paths["hermes_config"])
    has_local_ollama = _local_ollama_configured(config_text)
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "hermes_model_route_configured" if hermes["installed"] and (has_local_ollama or has_api_key) else "hermes_model_route_pending",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version.split()[0],
            "cwd": str(Path.cwd()),
        },
        "hermes": hermes,
        "paths": {name: _file_meta(path) for name, path in paths.items()},
        "credentials": credentials,
        "local_ollama_config": {
            "configured": has_local_ollama,
            "model": "gemma3:1b" if "gemma3:1b" in config_text else None,
            "base_url": "http://127.0.0.1:11434/v1" if "127.0.0.1:11434" in config_text else None,
        },
        "route": {
            "execution_conductor": "luvit",
            "hand_layer": "hermes",
            "wide_interpreter": "manual_gemini_api_when_needed",
            "background_low_frequency": "ubuntu_ollama_gemma3_1b",
        },
        "first_contact_permission": {
            "read_shion_outputs": True,
            "linux_bounded_probe": True,
            "windows_workspace_write": False,
            "daemon_or_schedule": False,
            "irreversible_effect": False,
        },
        "experience_particle_output": str(ROOT / "outputs" / "hermes" / "experience_particles.jsonl"),
        "requires_api_ping": False,
        "principle": "luvit_conducts_hermes_touches_local_model_translates_without_external_spend",
    }
    return payload


def main() -> int:
    payload = build_payload()
    system = str(payload["platform"]["system"]).lower()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (
        OUT_DIR / "model_route_probe.json",
        OUT_DIR / "model_route_probe_latest.json",
        OUT_DIR / f"model_route_probe_{system}.json",
    ):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "hermes_model_route_configured" else 2


if __name__ == "__main__":
    raise SystemExit(main())
