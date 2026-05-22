#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
DEFAULT_DISTRO = "Ubuntu-24.04"
DEFAULT_MODEL = "gemma3:1b"


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
    started = time.perf_counter()
    try:
        proc = subprocess.run(command, capture_output=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "stdout": _decode(proc.stdout).strip(),
            "stderr": _decode(proc.stderr).strip(),
            "command": command,
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "error": str(exc),
            "command": command,
        }


def _wsl(distro: str, args: list[str], timeout: float = 30.0) -> dict[str, Any]:
    return _run(["wsl", "-d", distro, "--", *args], timeout=timeout)


def _generate(distro: str, model: str, expected: str) -> dict[str, Any]:
    code = f"""
import json, time, urllib.request
payload = {{
    'model': {model!r},
    'prompt': 'Reply with exactly {expected}.',
    'stream': False,
    'keep_alive': '2m',
    'options': {{'temperature': 0, 'num_predict': 24, 'num_ctx': 1024}},
}}
req = urllib.request.Request(
    'http://127.0.0.1:11434/api/generate',
    data=json.dumps(payload).encode('utf-8'),
    headers={{'Content-Type': 'application/json'}},
    method='POST',
)
started = time.perf_counter()
with urllib.request.urlopen(req, timeout=180) as response:
    data = json.loads(response.read().decode('utf-8', errors='replace'))
print(json.dumps({{
    'elapsed_seconds': round(time.perf_counter() - started, 3),
    'response': str(data.get('response', '')).strip(),
    'done': data.get('done'),
    'done_reason': data.get('done_reason'),
    'eval_count': data.get('eval_count'),
}}, ensure_ascii=False))
"""
    result = _wsl(distro, ["python3", "-c", textwrap.dedent(code)], timeout=240)
    if result.get("ok") and result.get("stdout"):
        try:
            result["data"] = json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass
    return result


def build_payload(distro: str, model: str) -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "wsl_ollama_gpu_route_skipped",
            "reason": "wsl_ollama_gpu_route_probe_runs_from_windows_host",
            "platform": platform.system(),
        }

    tags = _wsl(distro, ["bash", "-lc", "curl -fsS http://127.0.0.1:11434/api/tags"], timeout=30)
    models: list[str] = []
    if tags.get("ok") and tags.get("stdout"):
        try:
            models = [item.get("name", "") for item in json.loads(tags["stdout"]).get("models", [])]
        except json.JSONDecodeError:
            pass
    if model not in models:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "wsl_ollama_gpu_route_pending_model",
            "distro": distro,
            "model": model,
            "tags": tags,
            "models": models,
            "principle": "wsl2_gpu_route_needs_a_local_model_before_inference_probe",
        }

    expected = f"OK_WSL_GPU_{model.replace(':', '_').replace('-', '_').upper()}_ROUTE"
    before = _wsl(
        distro,
        ["/usr/lib/wsl/lib/nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
        timeout=30,
    )
    generated = _generate(distro, model, expected)
    ps = _wsl(distro, ["ollama", "ps"], timeout=30)
    after = _wsl(
        distro,
        ["/usr/lib/wsl/lib/nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
        timeout=30,
    )
    logs = _wsl(
        distro,
        [
            "bash",
            "-lc",
            "journalctl -u ollama --no-pager -n 80 | grep -Ei 'offloaded|GPULayers|inference compute|CUDA|model weights' | tail -n 30",
        ],
        timeout=30,
    )
    response = str(generated.get("data", {}).get("response", ""))
    ps_text = str(ps.get("stdout", ""))
    logs_text = str(logs.get("stdout", ""))
    gpu_confirmed = "100% GPU" in ps_text or "offloaded 27/27 layers to GPU" in logs_text or "GPULayers" in logs_text

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "wsl_ollama_gpu_route_ready" if generated.get("ok") and expected in response and gpu_confirmed else "wsl_ollama_gpu_route_observed",
        "platform": platform.system(),
        "distro": distro,
        "model": model,
        "expected": expected,
        "generate": generated,
        "ollama_ps": ps,
        "nvidia_smi": {"before": before, "after": after},
        "ollama_logs": logs,
        "route": {
            "vmware_ubuntu": "freedom_field_and_orchestration",
            "windows_ollama": "current_gpu_heart",
            "wsl2_ollama": "gpu_linux_experiment_field",
        },
        "permission": {
            "external_api_cost": False,
            "windows_workspace_write": False,
            "irreversible_effect": False,
        },
        "principle": "wsl2_is_a_small_gpu_linux_experiment_field_not_the_main_free_roam_body",
    }


def _model_slug(model: str) -> str:
    return model.replace(":", "_").replace("/", "_").replace("\\", "_").replace("-", "_")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe WSL2 Ollama as a CUDA-backed Linux inference field.")
    parser.add_argument("--distro", default=DEFAULT_DISTRO)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    payload = build_payload(args.distro, args.model)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_slug = _model_slug(args.model)
    names = [
        OUT_DIR / "wsl_ollama_gpu_route_latest.json",
        OUT_DIR / "wsl_ollama_gpu_route.json",
        OUT_DIR / f"wsl_ollama_gpu_route_{model_slug}.json",
    ]
    for path in names:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_DIR / "wsl_ollama_gpu_route.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "wsl_ollama_gpu_route_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
