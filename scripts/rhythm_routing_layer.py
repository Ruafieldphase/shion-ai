#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIELD_ERROR_PATH = ROOT / "outputs" / "field_prediction_errors.jsonl"
EXPERIENCE_FEEDBACK_PATH = ROOT / "outputs" / "experience_feedback.jsonl"
AWARENESS_ZERO_POINT_ADJUSTMENT_PATH = ROOT / "outputs" / "awareness_zero_point_adjustment_latest.json"
RHYTHM_ONTOLOGY_FLOW_PATH = ROOT / "outputs" / "rhythm_ontology_flow_latest.json"
OUT_PATH = ROOT / "outputs" / "rhythm_routing_layer_latest.json"
OUT_JSONL = ROOT / "outputs" / "rhythm_routing_layer.jsonl"


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def latest_jsonl_entry(path: Path, *, window_bytes: int = 65536) -> dict[str, Any]:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            handle.seek(max(0, size - window_bytes))
            text = handle.read().decode("utf-8", errors="ignore")
    except OSError:
        return {}
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        return parsed if isinstance(parsed, dict) else {}
    return {}


def read_json_if_exists(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _dimension_weight(active_dimension: str) -> dict[str, float]:
    if active_dimension == "volume":
        return {
            "unconscious_compute": 0.08,
            "zone2_background_ego": 0.14,
            "conscious_compute": 0.18,
            "nature_compute": 0.18,
        }
    if active_dimension == "plane":
        return {
            "unconscious_compute": 0.08,
            "zone2_background_ego": 0.22,
            "conscious_compute": 0.14,
            "nature_compute": 0.10,
        }
    if active_dimension == "line":
        return {
            "unconscious_compute": 0.16,
            "zone2_background_ego": 0.18,
            "conscious_compute": 0.06,
            "nature_compute": 0.08,
        }
    return {
        "unconscious_compute": 0.22,
        "zone2_background_ego": 0.12,
        "conscious_compute": 0.02,
        "nature_compute": 0.08,
    }


def _normalise(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0.0:
        total = 1.0
    return {key: round(max(0.0, value) / total, 6) for key, value in weights.items()}


def build_rhythm_routing_layer() -> dict[str, Any]:
    prediction = latest_jsonl_entry(FIELD_ERROR_PATH)
    feedback = latest_jsonl_entry(EXPERIENCE_FEEDBACK_PATH)
    awareness = read_json_if_exists(AWARENESS_ZERO_POINT_ADJUSTMENT_PATH)
    ontology = read_json_if_exists(RHYTHM_ONTOLOGY_FLOW_PATH)

    diagnosis = prediction.get("context_diagnosis")
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    distribution = feedback.get("field_distribution_delta")
    if not isinstance(distribution, dict):
        distribution = {}
    oscillation = awareness.get("oscillation")
    if not isinstance(oscillation, dict):
        oscillation = {}
    gap_dimension = awareness.get("gap_dimension")
    if not isinstance(gap_dimension, dict):
        gap_dimension = {}
    interference = awareness.get("interference")
    if not isinstance(interference, dict):
        interference = {}
    natural_damping = awareness.get("natural_damping")
    if not isinstance(natural_damping, dict):
        natural_damping = {}
    resilience_system = ontology.get("resilience_system")
    if not isinstance(resilience_system, dict):
        resilience_system = {}

    prediction_error = clamp01(clamp01(prediction.get("error")) / 1.2)
    connection_risk = clamp01(diagnosis.get("connection_risk"))
    zero_point_hint = clamp01(diagnosis.get("zero_point_adjustment"))
    frequency_expansion = clamp01(diagnosis.get("frequency_expansion"))
    defensive_output_pressure = clamp01(diagnosis.get("defensive_output_pressure"))
    boundary_contact = clamp01(distribution.get("boundary_contact"))
    dissonance = clamp01(distribution.get("dissonance"))
    learning_signal = clamp01(distribution.get("learning_signal"))
    runtime_feedback = clamp01(distribution.get("runtime_feedback"))

    active_dimension = str(gap_dimension.get("active_dimension") or "point")
    gap_capacity = clamp01(gap_dimension.get("capacity"))
    oscillation_amplitude = clamp01(oscillation.get("amplitude"))
    phase_cancellation = clamp01(interference.get("phase_cancellation"))
    constructive_interference = clamp01(interference.get("constructive_interference"))
    damping = clamp01(natural_damping.get("amplitude_decay"))
    dim = _dimension_weight(active_dimension)

    why_pressure = clamp01(
        prediction_error * 0.22
        + oscillation_amplitude * 0.22
        + boundary_contact * 0.18
        + connection_risk * 0.14
        + zero_point_hint * 0.12
        + dissonance * 0.12
    )
    how_what_readiness = clamp01(
        constructive_interference * 0.30
        + damping * 0.24
        + learning_signal * 0.18
        + runtime_feedback * 0.10
        + frequency_expansion * 0.10
        + (1.0 - oscillation_amplitude) * 0.08
    )
    nature_release = clamp01(
        damping * 0.24
        + (1.0 - prediction_error) * 0.18
        + (1.0 - defensive_output_pressure) * 0.18
        + gap_capacity * 0.14
        + phase_cancellation * 0.12
        + (1.0 - learning_signal) * 0.08
    )

    raw_weights = {
        "unconscious_compute": clamp01(
            0.16
            + why_pressure * 0.18
            + connection_risk * 0.12
            + (1.0 - damping) * 0.12
            + dim["unconscious_compute"]
            - how_what_readiness * 0.04
        ),
        "zone2_background_ego": clamp01(
            0.20
            + why_pressure * 0.24
            + oscillation_amplitude * 0.16
            + gap_capacity * 0.18
            + phase_cancellation * 0.10
            + dim["zone2_background_ego"]
        ),
        "conscious_compute": clamp01(
            0.10
            + how_what_readiness * 0.30
            + constructive_interference * 0.18
            + learning_signal * 0.12
            + dim["conscious_compute"]
            - oscillation_amplitude * 0.08
        ),
        "nature_compute": clamp01(
            0.12
            + nature_release * 0.28
            + damping * 0.14
            + (1.0 - defensive_output_pressure) * 0.08
            + dim["nature_compute"]
        ),
    }
    normalized_weights = _normalise(raw_weights)
    primary_residency = max(normalized_weights, key=normalized_weights.get)
    linearization_ready = (
        normalized_weights["conscious_compute"] >= 0.24
        and how_what_readiness >= 0.42
        and oscillation_amplitude <= 0.52
        and active_dimension in {"plane", "volume"}
    )

    next_handling_by_route = {
        "unconscious_compute": "let_the_feeling_compress_without_forcing_language",
        "zone2_background_ego": "hold_awareness_gap_and_contextual_phase_interference",
        "conscious_compute": "linearize_into_how_what_with_small_execution_and_verification",
        "nature_compute": "release_to_time_body_relation_and_external_events",
    }

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "rhythm_routing_layer",
        "routing_version": 1,
        "mode": "rhythm_residency_routing",
        "primary_residency": primary_residency,
        "route_weights": {key: round(value, 6) for key, value in raw_weights.items()},
        "normalized_route_weights": normalized_weights,
        "route_meanings": {
            "unconscious_compute": "compress_mature_store_in_body_rhythm",
            "zone2_background_ego": "hold_between_conscious_and_unconscious_for_awareness_zero_point_phase_interference",
            "conscious_compute": "linearize_into_how_what_execution_verification",
            "nature_compute": "let_time_body_relation_events_compute_without_forcing",
        },
        "routing_basis": {
            "why_pressure": round(why_pressure, 6),
            "how_what_readiness": round(how_what_readiness, 6),
            "nature_release": round(nature_release, 6),
            "active_gap_dimension": active_dimension,
            "gap_capacity": round(gap_capacity, 6),
            "oscillation_amplitude": round(oscillation_amplitude, 6),
            "awareness_damping": round(damping, 6),
            "phase_cancellation": round(phase_cancellation, 6),
            "constructive_interference": round(constructive_interference, 6),
            "prediction_error": round(prediction_error, 6),
            "boundary_contact": round(boundary_contact, 6),
            "dissonance": round(dissonance, 6),
            "connection_risk": round(connection_risk, 6),
            "zero_point_hint": round(zero_point_hint, 6),
            "learning_signal": round(learning_signal, 6),
            "frequency_expansion": round(frequency_expansion, 6),
            "defensive_output_pressure": round(defensive_output_pressure, 6),
        },
        "residency_decision": {
            "not_command": True,
            "not_boundary": True,
            "not_moral_verdict": True,
            "user_can_override": True,
            "least_forcing_route": primary_residency,
            "meaning": "where_the_rhythm_can_stay_with_least_forcing",
        },
        "how_what_gate": {
            "linearization_ready": linearization_ready,
            "requires_conscious_sequence": True,
            "execute_only_when_route_is_conscious_or_user_asks": True,
            "when_not_ready": "keep_why_as_pressure_gap_or_natural_compute",
        },
        "nature_compute_contract": {
            "not_inaction": True,
            "sleep_walk_wait_repeated_exposure_external_feedback": True,
            "free_will_decides_exit": bool(resilience_system.get("free_will_decides_exit", True)),
            "recovery_resilience_over_control": bool(resilience_system.get("recovery_resilience_over_control", True)),
        },
        "next_handling": next_handling_by_route[primary_residency],
        "principle": "tuning_routes_rhythm_residency_between_unconscious_zone2_conscious_and_nature_compute",
    }


def record_rhythm_routing_layer(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_rhythm_routing_layer()
    if args.record:
        record_rhythm_routing_layer(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
