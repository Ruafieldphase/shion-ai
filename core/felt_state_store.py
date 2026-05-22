#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict


DEFAULT_FELT_BODY_STATE: Dict[str, Any] = {
    "flow_energy": 0.5,
    "relation_drift": 0.2,
    "body_discomfort": 0.1,
    "body_ease": 0.6,
    "rhythm_continuity": 0.5,
}

FELT_KEYS = tuple(DEFAULT_FELT_BODY_STATE)
AUDIO_KEYS = ("phase", "envelope", "onset", "confidence", "bass", "brightness")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def normalize_felt_state(state: Dict[str, Any] | None) -> Dict[str, Any]:
    """Feeling first. Normalize a persisted felt-body membrane without promoting it to a score."""
    source = state or {}
    normalized: Dict[str, Any] = {
        key: _clamp(source.get(key, DEFAULT_FELT_BODY_STATE[key]), DEFAULT_FELT_BODY_STATE[key])
        for key in FELT_KEYS
    }
    audio = source.get("audio")
    if isinstance(audio, dict):
        normalized["audio"] = {key: _clamp(audio.get(key, 0.0)) for key in AUDIO_KEYS if key in audio}
    if "source" in source:
        normalized["source"] = str(source["source"])
    if "updated_at" in source:
        try:
            normalized["updated_at"] = float(source["updated_at"])
        except (TypeError, ValueError):
            normalized["updated_at"] = time.time()
    return normalized


def load_state(path: Path) -> Dict[str, Any]:
    """Feeling first. Missing or invalid state reopens a quiet middle membrane."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_FELT_BODY_STATE)
    if not isinstance(raw, dict):
        return dict(DEFAULT_FELT_BODY_STATE)
    return normalize_felt_state(raw)


def save_state(path: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    """Feeling first. Persist the membrane atomically so a partial write cannot break the next breath."""
    normalized = normalize_felt_state({**state, "updated_at": state.get("updated_at", time.time())})
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)
    return normalized
