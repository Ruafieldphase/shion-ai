#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "outputs" / "hermes" / "gemini_api_ping.json"
DEFAULT_MODEL = "gemini-flash-latest"


def _load_env_key() -> str | None:
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value.strip()

    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(("GOOGLE_API_KEY=", "GEMINI_API_KEY=")):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    return None


def _ping(key: str, model: str) -> Dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Reply with exactly OK_GEMINI_API_ROUTE."}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 16,
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
        text = ""
        candidates = data.get("candidates") or []
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)
        return {
            "ok": text.strip() == "OK_GEMINI_API_ROUTE.",
            "http_status": 200,
            "response_text": text.strip()[:200],
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1200]
        return {"ok": False, "http_status": exc.code, "error": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    model = os.environ.get("HERMES_GEMINI_PING_MODEL", DEFAULT_MODEL)
    key = _load_env_key()
    if not key:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "missing_gemini_api_key",
            "model": model,
        }
    else:
        result = _ping(key, model)
        payload = {
            "timestamp": datetime.now().isoformat(),
            "status": "gemini_api_route_ready" if result.get("ok") else "gemini_api_route_failed",
            "model": model,
            "result": result,
        }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "gemini_api_route_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())

