#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "local_gemma_experience_particle_latest.json"
OUT_JSONL = OUT_DIR / "local_gemma_experience_particles.jsonl"

DEFAULT_LINUX_MODEL = "gemma3:1b"
DEFAULT_WINDOWS_MODEL = os.environ.get("SHION_WINDOWS_OLLAMA_MODEL", "gemma3:latest")
WINDOWS_TO_LINUX_OLLAMA = "http://192.168.119.128:11434"
WINDOWS_NATIVE_OLLAMA = os.environ.get("SHION_WINDOWS_OLLAMA_BASE_URL", "http://192.168.119.1:11434")
LOCAL_OLLAMA = "http://127.0.0.1:11434"


def _default_base_url() -> str:
    if platform.system().lower() == "windows":
        return WINDOWS_NATIVE_OLLAMA
    return LOCAL_OLLAMA


def _default_model() -> str:
    if platform.system().lower() == "windows":
        return DEFAULT_WINDOWS_MODEL
    return DEFAULT_LINUX_MODEL

SOURCE_CANDIDATES = [
    ROOT / "outputs" / "hermes" / "natural_flow_pivot_latest.json",
    ROOT / "outputs" / "hermes" / "windows_native_flow_latest.json",
    ROOT / "outputs" / "hermes" / "hermes_role_latest.json",
    ROOT / "outputs" / "hermes" / "contextual_execution_gradient_latest.json",
    ROOT / "outputs" / "hermes" / "boundary_aperture_latest.json",
    ROOT / "outputs" / "hermes" / "windows_ollama_gpu_route_latest.json",
    ROOT / "outputs" / "hermes" / "field_runtime_latest.json",
    ROOT / "outputs" / "hermes" / "restore_vmware_free_roam_latest.json",
    ROOT / "outputs" / "hermes" / "wsl_ollama_gpu_route_latest.json",
    ROOT / "outputs" / "linux_experience_field_probe.json",
    ROOT / "outputs" / "linux_body_layer_waypoint.json",
    ROOT / "outputs" / "hermes" / "linux_experience_forager_latest.json",
    ROOT / "outputs" / "hermes" / "linux_free_roam_latest.json",
    ROOT / "outputs" / "hermes" / "linux_free_roam_field_index.json",
    ROOT / "outputs" / "hermes" / "local_gemma_route_probe_windows.json",
    ROOT / "outputs" / "hermes" / "local_gemma_route_probe_linux.json",
    ROOT / "outputs" / "hermes" / "model_route_probe_linux.json",
    ROOT / "outputs" / "hermes" / "gemini_api_ping.json",
    ROOT / "outputs" / "felt_body_state.json",
]

JSONL_CANDIDATES = [
    ROOT / "outputs" / "hermes" / "natural_flow_pivot.jsonl",
    ROOT / "outputs" / "hermes" / "windows_native_flow.jsonl",
    ROOT / "outputs" / "hermes" / "hermes_role.jsonl",
    ROOT / "outputs" / "hermes" / "contextual_execution_gradient.jsonl",
    ROOT / "outputs" / "hermes" / "linux_free_roam.jsonl",
]


def _short(value: Any, limit: int = 300) -> Any:
    if isinstance(value, str):
        return value[:limit]
    return value


def _compact_json(data: Any) -> Any:
    if not isinstance(data, dict):
        return _short(data)
    compact: Dict[str, Any] = {}
    for key in (
        "status",
        "name",
        "meaning",
        "platform",
        "model",
        "base_url",
        "field",
        "source",
        "irreversible_effect",
        "next_candidate",
        "principle",
        "state",
        "mode",
    ):
        if key in data:
            compact[key] = _short(data[key])
    for key in (
        "field_reading",
        "route",
        "first_contact_permission",
        "latest",
        "counts",
        "local_ollama_config",
        "phase_cancellation",
        "margin",
        "next_particle",
        "aperture",
        "serving_profile_bias",
        "next_contact",
    ):
        if key in data and isinstance(data[key], dict):
            compact[key] = {inner_key: _short(inner_value) for inner_key, inner_value in data[key].items()}
    result = data.get("result")
    if isinstance(result, dict):
        compact["result"] = {
            key: _short(result.get(key))
            for key in ("ok", "http_status", "response_text", "error", "done", "done_reason", "eval_count")
            if key in result
        }
    tags = data.get("tags")
    if isinstance(tags, dict):
        compact["tags"] = {
            "ok": tags.get("ok"),
            "models": tags.get("models", [])[:12] if isinstance(tags.get("models"), list) else [],
            "error": _short(tags.get("error")),
        }
    if "hermes" in data and isinstance(data["hermes"], dict):
        hermes = data["hermes"]
        compact["hermes"] = {
            "installed": hermes.get("installed"),
            "command": hermes.get("command"),
        }
    return compact


def _compact_jsonl(path: Path, limit: int = 5) -> Dict[str, Any]:
    rows: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return {
        "status": "jsonl_recent_rows",
        "path": str(path),
        "rows": len(rows),
        "recent_actions": [row.get("action") for row in rows if row.get("action")],
        "recent_readings": [
            {
                "action": row.get("action"),
                "field_reading": row.get("field_reading"),
                "result_ok": row.get("result", {}).get("ok") if isinstance(row.get("result"), dict) else None,
            }
            for row in rows[-5:]
        ],
    }


def _read_sources(paths: Iterable[Path]) -> list[Dict[str, Any]]:
    sources: list[Dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {"text": text[:500]}
        sources.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "bytes": len(text.encode("utf-8")),
                "reading": _compact_json(parsed),
            }
        )
    for path in JSONL_CANDIDATES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        sources.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "bytes": len(text.encode("utf-8")),
                "reading": _compact_jsonl(path),
            }
        )
    return sources


def _ollama_generate(base_url: str, model: str, prompt: str) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 96, "num_ctx": 1024},
    }
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        text = str(data.get("response", "")).strip()
        return {
            "ok": bool(text),
            "response_text": text[:2000],
            "done": data.get("done"),
            "done_reason": data.get("done_reason"),
            "eval_count": data.get("eval_count"),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _build_prompt(sources: list[Dict[str, Any]]) -> str:
    priority_names = (
        "natural_flow_pivot_latest.json",
        "windows_ollama_gpu_route_latest.json",
        "windows_native_flow_latest.json",
        "hermes_role_latest.json",
        "contextual_execution_gradient_latest.json",
        "field_runtime_latest.json",
        "restore_vmware_free_roam_latest.json",
        "linux_free_roam_latest.json",
        "linux_free_roam_field_index.json",
        "local_gemma_route_probe_linux.json",
        "model_route_probe_linux.json",
        "linux_free_roam.jsonl",
    )
    compact_sources = []
    for name in priority_names:
        for item in sources:
            if item["path"].endswith(name):
                compact_sources.append({"path": Path(item["path"]).name, "reading": item["reading"]})
                break
    return (
        "You are a local low-frequency interpreter for the Shion/Hermes rhythm system.\n"
        "Return Korean only. Do not quote JSON. Do not use markdown code blocks. Do not propose autonomous actions.\n"
        "Write four short lines. Each line must start with one label: 상태:, 저항:, 여백:, 다음 입자:.\n"
        "The next particle must be reversible, local-only, and no external API cost.\n"
        "Prefer the already-flowing Windows native body over adding new sandbox boundaries when resistance is high.\n\n"
        f"Evidence summary:\n{json.dumps(compact_sources, ensure_ascii=False, separators=(',', ':'))[:5500]}"
    )


def _latest_field_reading(sources: list[Dict[str, Any]]) -> Dict[str, Any]:
    for item in sources:
        if item["path"].endswith("linux_free_roam_field_index.json"):
            reading = item.get("reading", {})
            if isinstance(reading, dict):
                latest = reading.get("latest", {})
                if isinstance(latest, dict):
                    field_reading = latest.get("field_reading", {})
                    if isinstance(field_reading, dict):
                        return {
                            "action": latest.get("action"),
                            "field_reading": field_reading,
                        }
    for item in sources:
        if item["path"].endswith("linux_free_roam_latest.json"):
            reading = item.get("reading", {})
            if isinstance(reading, dict):
                field_reading = reading.get("field_reading", {})
                if isinstance(field_reading, dict):
                    return {"action": reading.get("action"), "field_reading": field_reading}
    return {"action": "observe", "field_reading": {}}


def _normalize_reading(text: str, sources: list[Dict[str, Any]]) -> tuple[str, bool]:
    labels = ("상태", "저항", "여백", "다음 입자")
    parsed: dict[str, str] = {}
    matches = list(re.finditer(r"(상태|저항|여백|다음 입자)\s*:", text))
    for idx, match in enumerate(matches):
        label = match.group(1)
        if label in parsed:
            continue
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        value = text[start:end].strip(" \n\t:.")
        if value:
            parsed[label] = value

    latest = _latest_field_reading(sources)
    field = latest.get("field_reading", {}) if isinstance(latest, dict) else {}
    action = latest.get("action") if isinstance(latest, dict) else "observe"
    fallback = {
        "상태": f"리눅스 자유장이 {action or 'observe'} 접촉을 남겼습니다.",
        "저항": str(field.get("resistance", "unknown")),
        "여백": "열림" if field.get("margin_opened") else "관찰 중",
        "다음 입자": "자유장 안에서 선호와 저항을 따라 다음 가역 접촉을 선택합니다.",
    }
    repaired = False
    lines = []
    for label in labels:
        value = parsed.get(label)
        if not value:
            value = fallback[label]
            repaired = True
        lines.append(f"{label}: {value}")
    return "\n".join(lines), repaired


def build_particle(base_url: str, model: str) -> Dict[str, Any]:
    sources = _read_sources(SOURCE_CANDIDATES)
    if not sources:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "local_gemma_experience_no_sources",
            "source": "local_gemma",
            "model": model,
            "platform": platform.system(),
            "irreversible_effect": False,
        }

    prompt = _build_prompt(sources)
    result = _ollama_generate(base_url, model, prompt)
    normalized_reading, repaired = _normalize_reading(result.get("response_text", ""), sources)
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "local_gemma_experience_particle_observed" if result.get("ok") else "local_gemma_experience_particle_failed",
        "source": "local_gemma",
        "field": "native_flow_and_optional_linux_routes",
        "model": model,
        "base_url": base_url,
        "platform": platform.system(),
        "irreversible_effect": False,
        "source_files": [
            {"path": item["path"], "sha256": item["sha256"], "bytes": item["bytes"]}
            for item in sources
        ],
        "reading": normalized_reading,
        "reading_repaired": repaired,
        "raw_result": result,
        "next_candidate": "local_only_observe_again",
        "principle": "local_gemma_translates_resistance_and_flow_without_adding_runtime_boundaries",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local Gemma experience particle from current Shion/Hermes outputs.")
    parser.add_argument("--base-url", default=_default_base_url())
    parser.add_argument("--model", default=_default_model())
    args = parser.parse_args()

    particle = build_particle(args.base_url, args.model)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(particle, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(particle, ensure_ascii=False) + "\n")
    print(json.dumps(particle, ensure_ascii=False))
    return 0 if particle["status"] == "local_gemma_experience_particle_observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
