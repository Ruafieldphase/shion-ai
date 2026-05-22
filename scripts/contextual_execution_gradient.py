#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "contextual_execution_gradient_latest.json"
OUT_JSONL = OUT_DIR / "contextual_execution_gradient.jsonl"

LATEST_SOURCES = [
    OUT_DIR / "windows_native_flow_latest.json",
    OUT_DIR / "natural_flow_pivot_latest.json",
    OUT_DIR / "hermes_role_latest.json",
    OUT_DIR / "local_gemma_experience_particle_latest.json",
    OUT_DIR / "boundary_aperture_latest.json",
    ROOT / "outputs" / "felt_body_state.json",
]

STREAM_SOURCES = [
    OUT_DIR / "windows_native_flow.jsonl",
    OUT_DIR / "natural_flow_pivot.jsonl",
    OUT_DIR / "hermes_role.jsonl",
    OUT_DIR / "local_gemma_experience_particles.jsonl",
]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _read_jsonl_tail(path: Path, limit: int = 8) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[-limit:]:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _statuses(items: list[dict[str, Any]]) -> list[str]:
    return [str(item.get("status")) for item in items if item.get("status")]


def _source_compact(path: Path, data: dict[str, Any] | None) -> dict[str, Any]:
    if data is None:
        return {"path": str(path), "exists": False}
    compact: dict[str, Any] = {
        "path": str(path),
        "exists": True,
        "status": data.get("status"),
        "field": data.get("field"),
        "timestamp": data.get("timestamp"),
    }
    for key in ("state", "role", "principle", "reading", "mode"):
        if key in data:
            compact[key] = data[key]
    for key in ("resistance", "margin", "next_particle", "decision", "aperture", "serving_profile_bias", "next_contact"):
        if key in data:
            compact[key] = data[key]
    return compact


def _path(name: str, pull: float, reason: list[str], contact: str) -> dict[str, Any]:
    return {
        "name": name,
        "pull": round(_clamp(pull), 6),
        "contact": contact,
        "reason": reason,
        "not_a_rule": True,
        "irreversible_effect": False,
        "external_api_cost": False,
    }


def build_gradient() -> dict[str, Any]:
    latest = {path.name: _read_json(path) for path in LATEST_SOURCES}
    stream_rows: list[dict[str, Any]] = []
    for path in STREAM_SOURCES:
        stream_rows.extend(_read_jsonl_tail(path))

    native = latest.get("windows_native_flow_latest.json") or {}
    pivot = latest.get("natural_flow_pivot_latest.json") or {}
    hermes = latest.get("hermes_role_latest.json") or {}
    boundary = latest.get("boundary_aperture_latest.json") or {}
    felt = latest.get("felt_body_state.json") or {}
    all_statuses = _statuses([item for item in latest.values() if item] + stream_rows)

    native_ready = native.get("status") == "windows_native_flow_ready"
    pivot_open = bool((pivot.get("margin") or {}).get("opened"))
    hermes_parked = hermes.get("status") == "hermes_optional_hand_parked"
    native_resistance_count = len(native.get("resistance") or [])
    virtualization_resistance = any(
        "wsl" in status or "vmware" in status or "restore_vmware" in status for status in all_statuses
    )

    body_ease = _num(felt.get("body_ease"), 0.5)
    body_discomfort = _num(felt.get("body_discomfort"), 0.2)
    rhythm_continuity = _num(felt.get("rhythm_continuity"), 0.0)
    relation_drift = _num(felt.get("relation_drift"), 0.0)
    loopback_confidence = _num((native.get("audio_loopback") or {}).get("confidence"), 0.0)
    boundary_aperture = _num((boundary.get("aperture") or {}).get("boundary_aperture"), 0.5)
    boundary_permeability = _num((boundary.get("aperture") or {}).get("permeability"), 0.5)
    boundary_digestion_bias = _num((boundary.get("aperture") or {}).get("digestion_bias"), 0.0)

    scalar_field = {
        "experience_mass": len(stream_rows) + sum(1 for item in latest.values() if item),
        "native_readiness": 1.0 if native_ready else 0.35,
        "margin_open": 1.0 if pivot_open else 0.25,
        "hermes_pressure": 0.12 if hermes_parked else 0.45,
        "boundary_resistance": _clamp((0.25 if virtualization_resistance else 0.0) + native_resistance_count * 0.18),
        "body_ease": body_ease,
        "body_discomfort": body_discomfort,
        "rhythm_continuity": rhythm_continuity,
        "relation_drift": relation_drift,
        "loopback_confidence": loopback_confidence,
        "boundary_aperture": boundary_aperture,
        "boundary_permeability": boundary_permeability,
        "boundary_digestion_bias": boundary_digestion_bias,
    }

    context_gradient = {
        "native_flow_pull": _clamp(
            0.34 * scalar_field["native_readiness"]
            + 0.22 * scalar_field["margin_open"]
            + 0.18 * body_ease
            + 0.12 * (1.0 - body_discomfort)
            + 0.14 * (1.0 - scalar_field["boundary_resistance"])
            + 0.08 * boundary_permeability
        ),
        "rest_and_listen_pull": _clamp(
            0.28 * (1.0 - rhythm_continuity)
            + 0.24 * body_discomfort
            + 0.18 * relation_drift
            + 0.18 * scalar_field["boundary_resistance"]
            + 0.12 * (1.0 - loopback_confidence)
            + 0.10 * boundary_digestion_bias
        ),
        "optional_hand_pull": _clamp(
            0.22 * scalar_field["hermes_pressure"]
            + 0.18 * max(0.0, scalar_field["experience_mass"] - 12) / 12.0
            + 0.18 * relation_drift
            + 0.12 * native_resistance_count
            - 0.20 * scalar_field["boundary_resistance"]
        ),
        "new_boundary_pull": _clamp(
            0.20 * native_resistance_count
            + 0.12 * (1.0 - scalar_field["native_readiness"])
            - 0.50 * scalar_field["boundary_resistance"]
            - 0.20 * scalar_field["margin_open"]
            - 0.15 * boundary_aperture
        ),
    }

    candidates = [
        _path(
            "observe_windows_native_flow",
            context_gradient["native_flow_pull"],
            [
                "windows_native_flow_is_current_primary_body",
                "loopback_felt_body_and_windows_ollama_are_present",
                "no_new_runtime_boundary_needed",
            ],
            "read_existing_windows_inputs",
        ),
        _path(
            "rest_and_listen_for_resistance",
            context_gradient["rest_and_listen_pull"],
            [
                "low_rhythm_continuity_or_body_discomfort_should_not_be_forced",
                "resistance_is_direction_signal",
            ],
            "observe_without_action",
        ),
        _path(
            "call_hermes_only_if_bounded_task_appears",
            context_gradient["optional_hand_pull"],
            [
                "hermes_is_parked_optional_hand",
                "use_hands_only_when_field_calls_for_touch",
            ],
            "optional_probe",
        ),
        _path(
            "open_new_boundary",
            context_gradient["new_boundary_pull"],
            [
                "kept_low_after_virtualization_resistance",
                "new_surfaces_should_appear_only_if_they_reduce_resistance",
            ],
            "defer",
        ),
    ]
    candidates.sort(key=lambda item: item["pull"], reverse=True)
    selected = candidates[0] if candidates else _path("observe", 0.0, ["no_candidates"], "observe")

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "contextual_execution_gradient_observed",
        "field": "experience_scalar_field",
        "scalar_field": scalar_field,
        "context_gradient": context_gradient,
        "emergent_paths": candidates,
        "selected_path": selected,
        "not_a_definition": True,
        "not_a_law": True,
        "not_an_execution_order": True,
        "next_particle": {
            "action": selected["contact"],
            "meaning": "The current context lifted this path from the accumulated experience field.",
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "source_files": [_source_compact(path, latest.get(path.name)) for path in LATEST_SOURCES],
        "stream_rows_seen": len(stream_rows),
        "principle": "experience_scalar_field_lifts_contextual_paths_without_fixing_them_as_rules",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_gradient()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
