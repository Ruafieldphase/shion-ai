#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"

DEFAULT_MODEL = "gemma3:1b"
FALLBACK_MODELS = ("gemma3:1b", "llama3.2:latest", "gemma3:latest")
WINDOWS_OLLAMA = "http://127.0.0.1:11434"
LINUX_TO_WINDOWS_OLLAMA = "http://192.168.119.1:11434"
LINUX_OLLAMA = "http://127.0.0.1:11434"
WINDOWS_TO_LINUX_OLLAMA = "http://192.168.119.128:11434"


def _candidate_base_url() -> str:
    if platform.system().lower() == "linux":
        return LINUX_OLLAMA
    return WINDOWS_OLLAMA


def _candidate_base_urls() -> list[Dict[str, str]]:
    if platform.system().lower() == "linux":
        return [
            {"name": "linux_ollama_local", "base_url": LINUX_OLLAMA},
            {"name": "linux_to_windows_ollama", "base_url": LINUX_TO_WINDOWS_OLLAMA},
        ]
    return [
        {"name": "windows_to_linux_ollama", "base_url": WINDOWS_TO_LINUX_OLLAMA},
        {"name": "windows_ollama_local", "base_url": WINDOWS_OLLAMA},
    ]


def _ollama_tags(base_url: str) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        models = [item.get("name") for item in data.get("models", []) if item.get("name")]
        return {"ok": True, "models": models}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "models": []}


def _select_model(models: list[str]) -> str | None:
    for model in FALLBACK_MODELS:
        if model in models:
            return model
    return None


def _ollama_generate(base_url: str, model: str, expected: str) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": f"Reply with exactly {expected}.",
        "stream": False,
        "options": {"temperature": 0, "num_predict": 24},
    }
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        text = str(data.get("response", "")).strip()
        return {
            "ok": text == expected or expected in text,
            "response_text": text[:200],
            "done": data.get("done"),
            "done_reason": data.get("done_reason"),
            "eval_count": data.get("eval_count"),
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1200]
        return {"ok": False, "http_status": exc.code, "error": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    route_results = []
    selected_route = None
    selected_model = None
    selected_result: Dict[str, Any] = {"ok": False, "error": "no candidate route tested"}
    for candidate in _candidate_base_urls():
        base_url = candidate["base_url"]
        tags = _ollama_tags(base_url)
        model = _select_model(tags.get("models", [])) if tags.get("ok") else None
        expected = f"OK_{candidate['name'].upper()}_ROUTE"
        result = _ollama_generate(base_url, model, expected) if model else {"ok": False, "error": "no supported local model found"}
        route_payload = {
            "name": candidate["name"],
            "base_url": base_url,
            "model": model,
            "tags": tags,
            "result": result,
        }
        route_results.append(route_payload)
        if result.get("ok") and selected_route is None:
            selected_route = candidate
            selected_model = model
            selected_result = result

    if selected_route is None:
        selected_route = {"name": "none", "base_url": _candidate_base_url()}
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "local_gemma_route_ready" if selected_result.get("ok") else "local_gemma_route_pending",
        "platform": platform.system(),
        "base_url": selected_route["base_url"],
        "route_name": selected_route["name"],
        "model": selected_model or DEFAULT_MODEL,
        "result": selected_result,
        "routes": route_results,
        "route": {
            "execution_conductor": "luvit",
            "local_interpreter": "ollama_local_model",
            "hermes_access": "ready_when_hermes_points_to_linux_ollama_openai_compat_endpoint",
        },
        "principle": "local_gemma_is_low_cost_background_rhythm_not_autonomous_conductor",
    }
    system = platform.system().lower()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (
        OUT_DIR / "local_gemma_route_probe.json",
        OUT_DIR / "local_gemma_route_probe_latest.json",
        OUT_DIR / f"local_gemma_route_probe_{system}.json",
    ):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "local_gemma_route_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
