#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"

DEFAULT_BASE_URL = "http://192.168.119.1:11434"
DEFAULT_MODEL = "gemma3:latest"
HEAVY_TEST_MODEL = "gemma4:e2b"
OLLAMA_EXE = Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"


def _request_json(base_url: str, path: str, payload: Dict[str, Any] | None = None, timeout: float = 60.0) -> Dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {"ok": True, "data": json.loads(response.read().decode("utf-8", errors="replace"))}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        return {"ok": False, "http_status": exc.code, "error": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _generate(base_url: str, model: str, prompt: str, keep_alive: str, timeout: float) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {
            "temperature": 0,
            "num_predict": 24,
            "num_ctx": 1024,
        },
    }
    started = time.perf_counter()
    result = _request_json(base_url, "/api/generate", payload, timeout=timeout)
    result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    if result.get("ok") and isinstance(result.get("data"), dict):
        data = result["data"]
        result["reading"] = {
            "response": str(data.get("response", "")).strip()[:200],
            "done": data.get("done"),
            "done_reason": data.get("done_reason"),
            "eval_count": data.get("eval_count"),
        }
        result.pop("data", None)
    return result


def _unload(base_url: str, model: str) -> Dict[str, Any]:
    return _request_json(
        base_url,
        "/api/generate",
        {"model": model, "prompt": "", "stream": False, "keep_alive": 0},
        timeout=30,
    )


def _nvidia_smi() -> Dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"ok": False, "skipped": "nvidia_smi_checked_on_windows_host_only"}
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="replace",
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _ollama_ps(base_url: str) -> Dict[str, Any]:
    return _request_json(base_url, "/api/ps", timeout=20)


def build_payload(base_url: str, model: str, unload: bool) -> Dict[str, Any]:
    tags = _request_json(base_url, "/api/tags", timeout=20)
    models = []
    if tags.get("ok"):
        models = [item.get("name") for item in tags.get("data", {}).get("models", []) if item.get("name")]
    if model not in models:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "windows_ollama_gpu_route_pending",
            "base_url": base_url,
            "model": model,
            "tags": {"ok": tags.get("ok"), "models": models, "error": tags.get("error")},
            "principle": "windows_ollama_is_gpu_heart_not_linux_free_roam_body",
        }

    expected = f"OK_WINDOWS_GPU_{model.replace(':', '_').replace('-', '_').upper()}_ROUTE"
    before = _nvidia_smi()
    result = _generate(base_url, model, f"Reply with exactly {expected}.", "2m", timeout=360)
    ps = _ollama_ps(base_url)
    after = _nvidia_smi()
    unload_result = _unload(base_url, model) if unload else {"ok": True, "skipped": "model_left_warm"}
    response = result.get("reading", {}).get("response", "")
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "windows_ollama_gpu_route_ready" if result.get("ok") and expected in response else "windows_ollama_gpu_route_observed",
        "platform": platform.system(),
        "base_url": base_url,
        "model": model,
        "expected": expected,
        "result": result,
        "ollama_ps": ps,
        "nvidia_smi": {"before": before, "after": after},
        "unload": unload_result,
        "route": {
            "free_roam_body": "vmware_ubuntu",
            "gpu_heart": "windows_ollama_on_rtx_2070s",
            "next_experiment": "wsl2_cuda_ollama_small_field",
        },
        "permission": {
            "external_api_cost": False,
            "windows_workspace_write": False,
            "irreversible_effect": False,
        },
        "principle": "vmware_is_free_roam_body_windows_ollama_is_gpu_heart",
    }


def _model_slug(model: str) -> str:
    return model.replace(":", "_").replace("/", "_").replace("\\", "_").replace("-", "_")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Windows Ollama as the GPU endpoint for the Linux free-roam field.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--heavy", action="store_true", help=f"Probe {HEAVY_TEST_MODEL} instead of the default model.")
    parser.add_argument("--keep-warm", action="store_true", help="Leave the model loaded after probing.")
    args = parser.parse_args()
    model = HEAVY_TEST_MODEL if args.heavy else args.model
    payload = build_payload(args.base_url, model, unload=not args.keep_warm)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_slug = _model_slug(model)
    names = [
        OUT_DIR / "windows_ollama_gpu_route_latest.json",
        OUT_DIR / "windows_ollama_gpu_route.json",
        OUT_DIR / f"windows_ollama_gpu_route_{platform.system().lower()}.json",
        OUT_DIR / f"windows_ollama_gpu_route_{model_slug}.json",
    ]
    for path in names:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_DIR / "windows_ollama_gpu_route.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "windows_ollama_gpu_route_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
