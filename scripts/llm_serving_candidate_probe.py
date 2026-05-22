#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "llm_serving_candidate_probe_latest.json"
OUT_JSONL = OUT_DIR / "llm_serving_candidate_probe.jsonl"
OUT_MD = OUT_DIR / "llm_serving_candidate_probe_latest.md"

ENDPOINTS = [
    ("windows_ollama", "http://192.168.119.1:11434/api/tags"),
    ("vllm_default", "http://127.0.0.1:8000/v1/models"),
    ("sglang_default", "http://127.0.0.1:30000/v1/models"),
]


def _run(command: List[str], timeout: float = 20.0) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "stdout": _decode_process_bytes(proc.stdout).strip(),
            "stderr": _decode_process_bytes(proc.stderr).strip(),
            "command": command,
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "error": str(exc),
            "command": command,
        }


def _decode_process_bytes(value: bytes) -> str:
    if not value:
        return ""
    if value.count(b"\x00") > len(value) // 8:
        try:
            return value.decode("utf-16le", errors="replace")
        except Exception:
            pass
    return value.decode("utf-8", errors="replace")


def _http_get(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
        data: Any
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = raw[:500]
        return {
            "ok": True,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "data": _compact_endpoint_data(data),
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:800]
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "http_status": exc.code,
            "error": body,
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "error": str(exc),
        }


def _compact_endpoint_data(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    if isinstance(data.get("models"), list):
        return {"models": [item.get("name") or item.get("model") for item in data["models"][:20] if isinstance(item, dict)]}
    if isinstance(data.get("data"), list):
        return {"models": [item.get("id") for item in data["data"][:20] if isinstance(item, dict)]}
    return {key: data.get(key) for key in ("object", "error", "detail") if key in data}


def _wsl_probe() -> Dict[str, Any]:
    if not shutil.which("wsl.exe"):
        return {"installed": False, "reason": "wsl.exe_not_found"}
    listing = _run(["wsl.exe", "-l", "-v"], timeout=15)
    launch = _run(
        [
            "wsl.exe",
            "-d",
            "Ubuntu-24.04",
            "--",
            "bash",
            "-lc",
            "uname -a; python3 --version; command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,compute_cap,memory.total --format=csv,noheader || true",
        ],
        timeout=30,
    )
    return {
        "installed": True,
        "list": listing,
        "ubuntu_24_04_launch": launch,
        "ready": bool(launch.get("ok")),
    }


def _host_probe() -> Dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": _run(["python", "--version"], timeout=10),
        "uv": _run(["uv", "--version"], timeout=10) if shutil.which("uv") else {"ok": False, "error": "uv_not_found"},
        "docker": _run(["docker", "--version"], timeout=10)
        if shutil.which("docker")
        else {"ok": False, "error": "docker_not_found"},
        "nvidia_smi": _run(
            [
                "nvidia-smi",
                "--query-gpu=name,compute_cap,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            timeout=20,
        )
        if shutil.which("nvidia-smi")
        else {"ok": False, "error": "nvidia_smi_not_found"},
    }


def _endpoint_probe() -> Dict[str, Any]:
    return {name: {"url": url, "result": _http_get(url)} for name, url in ENDPOINTS}


def _recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    endpoints = payload["endpoints"]
    wsl_ready = payload["wsl"].get("ready") is True
    docker_ready = payload["host"].get("docker", {}).get("ok") is True
    vllm_ready = endpoints["vllm_default"]["result"].get("ok") is True
    sglang_ready = endpoints["sglang_default"]["result"].get("ok") is True

    blockers = []
    if not wsl_ready:
        launch = payload["wsl"].get("ubuntu_24_04_launch", {})
        blockers.append(
            {
                "target": "wsl_linux_serving_path",
                "status": "blocked",
                "evidence": (launch.get("stderr") or launch.get("stdout") or launch.get("error") or "wsl_not_ready")[:800],
            }
        )
    if not docker_ready:
        blockers.append({"target": "docker_serving_path", "status": "blocked", "evidence": "docker_not_available"})
    if not vllm_ready:
        blockers.append({"target": "vllm_endpoint", "status": "not_running", "evidence": endpoints["vllm_default"]["result"].get("error")})
    if not sglang_ready:
        blockers.append({"target": "sglang_endpoint", "status": "not_running", "evidence": endpoints["sglang_default"]["result"].get("error")})

    if vllm_ready or sglang_ready:
        next_action = "run_llm_serving_benchmark_with_ready_openai_endpoint"
    elif wsl_ready:
        next_action = "create_fresh_wsl_uv_environment_then_install_one_serving_engine"
    else:
        next_action = "keep_windows_ollama_baseline_and_fix_wsl_or_start_external_endpoint_later"

    return {
        "principle": "windows_native_remains_baseline_vllm_sglang_are_optional_serving_candidates",
        "next_action": next_action,
        "blockers": blockers,
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    rec = payload["recommendation"]
    endpoints = payload["endpoints"]
    lines = [
        "# LLM Serving Candidate Probe",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Status: `{payload['status']}`",
        f"- Next action: `{rec['next_action']}`",
        "",
        "## Endpoints",
        "",
        "| Candidate | URL | Ready | Evidence |",
        "|---|---|---:|---|",
    ]
    for name, item in endpoints.items():
        result = item["result"]
        evidence = "ok" if result.get("ok") else str(result.get("error") or result.get("http_status") or "")[:120]
        lines.append(f"| `{name}` | `{item['url']}` | `{result.get('ok')}` | {evidence} |")
    lines.extend(["", "## Blockers", ""])
    for blocker in rec["blockers"]:
        lines.append(f"- `{blocker['target']}`: `{blocker['status']}` - {blocker.get('evidence')}")
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- vLLM official GPU path is Linux/WSL or a community Windows fork; do not install upstream vLLM into the Windows Python baseline.",
            "- SGLang should be treated the same way here: an optional OpenAI-compatible serving candidate, not the default body.",
            "- Once a vLLM or SGLang endpoint responds at `/v1/models`, run `scripts/llm_serving_benchmark.py` with that provider.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload() -> Dict[str, Any]:
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "llm_serving_candidate_probe_completed",
        "host": _host_probe(),
        "wsl": _wsl_probe(),
        "endpoints": _endpoint_probe(),
        "official_context": {
            "vllm": {
                "github": "https://github.com/vllm-project/vllm",
                "docs": "https://docs.vllm.ai",
                "current_fit": "official_windows_path_is_wsl_or_community_fork",
            },
            "sglang": {
                "github": "https://github.com/sgl-project/sglang",
                "docs": "https://docs.sglang.io",
                "current_fit": "openai_compatible_candidate_when_linux_or_container_runtime_is_available",
            },
        },
        "permission": {
            "starts_servers": False,
            "installs_packages": False,
            "external_api_cost": False,
            "writes_outputs_only": True,
        },
    }
    payload["recommendation"] = _recommendation(payload)
    return payload


def main() -> int:
    payload = build_payload()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    _write_markdown(payload)
    print(json.dumps(payload["recommendation"], ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    ready = any(item["result"].get("ok") for item in payload["endpoints"].values())
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
