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
OUT_PATH = ROOT / "outputs" / "awareness_zero_point_adjustment_latest.json"
OUT_JSONL = ROOT / "outputs" / "awareness_zero_point_adjustment.jsonl"


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


def _active_gap_dimension(gap_capacity: float) -> str:
    if gap_capacity >= 0.72:
        return "volume"
    if gap_capacity >= 0.48:
        return "plane"
    if gap_capacity >= 0.24:
        return "line"
    return "point"


def build_awareness_zero_point_adjustment() -> dict[str, Any]:
    prediction = latest_jsonl_entry(FIELD_ERROR_PATH)
    feedback = latest_jsonl_entry(EXPERIENCE_FEEDBACK_PATH)
    diagnosis = prediction.get("context_diagnosis")
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    distribution = feedback.get("field_distribution_delta")
    if not isinstance(distribution, dict):
        distribution = {}

    prediction_error = clamp01(clamp01(prediction.get("error")) / 1.2)
    boundary_contact = clamp01(distribution.get("boundary_contact"))
    dissonance = clamp01(distribution.get("dissonance"))
    connection_risk = clamp01(diagnosis.get("connection_risk"))
    zero_point_hint = clamp01(diagnosis.get("zero_point_adjustment"))
    frequency_expansion = clamp01(diagnosis.get("frequency_expansion"))
    learning_signal = clamp01(distribution.get("learning_signal"))

    oscillation_amplitude = clamp01(
        prediction_error * 0.32
        + boundary_contact * 0.24
        + dissonance * 0.18
        + connection_risk * 0.16
        + zero_point_hint * 0.10
    )
    self_noticing = clamp01(0.22 + zero_point_hint * 0.34 + learning_signal * 0.20 + frequency_expansion * 0.14)
    gap_capacity = clamp01(self_noticing * 0.48 + zero_point_hint * 0.24 + (1.0 - oscillation_amplitude) * 0.16 + learning_signal * 0.12)
    curvature_deabsolutization = clamp01(self_noticing * 0.42 + gap_capacity * 0.36 + zero_point_hint * 0.22)
    phase_cancellation = clamp01(curvature_deabsolutization * 0.42 + oscillation_amplitude * gap_capacity * 0.36 + zero_point_hint * 0.22)
    constructive_interference = clamp01(learning_signal * 0.34 + frequency_expansion * 0.22 + gap_capacity * 0.26 + self_noticing * 0.18)
    natural_damping = clamp01(phase_cancellation * 0.44 + gap_capacity * 0.30 + curvature_deabsolutization * 0.18 + (1.0 - dissonance) * 0.08)

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "awareness_zero_point_adjustment",
        "awareness_version": 1,
        "mode": "automatic_zero_point_adjustment",
        "trigger": {
            "self_noticing_without_judgment": True,
            "korean_anchor": "내가 흥분하고 있구나",
            "not_command": True,
            "not_reframe": True,
            "meaning": "awareness creates a phase reference without forcing correction",
        },
        "oscillation": {
            "amplitude": round(oscillation_amplitude, 6),
            "read_as": "wave_to_be_noticed_not_problem_to_block",
            "inputs": {
                "prediction_error": round(prediction_error, 6),
                "boundary_contact": round(boundary_contact, 6),
                "dissonance": round(dissonance, 6),
                "connection_risk": round(connection_risk, 6),
            },
        },
        "gap_dimension": {
            "active_dimension": _active_gap_dimension(gap_capacity),
            "capacity": round(gap_capacity, 6),
            "point": "self_noticing_appears",
            "line": "distance_between_emotion_and_awareness",
            "plane": "context_interference_space_where_where_when_who_can_spread",
            "volume": "embodied_field_recalibration",
            "meaning": "the gap moves from point to line to plane to volume as gradient-processing dimension increases",
        },
        "emotional_curvature": {
            "curvature_deabsolutization": round(curvature_deabsolutization, 6),
            "bent_depth_is_not_erased": True,
            "meaning": "awareness does not flatten emotion away; it makes the emotional curvature observable instead of absolute",
        },
        "zero_point_adjustment": {
            "automatic": True,
            "context_dependency": "WHERE_WHEN_WHO",
            "current_context_rebalances_without_command": True,
            "zero_point_hint": round(zero_point_hint, 6),
        },
        "interference": {
            "phase_cancellation": round(phase_cancellation, 6),
            "constructive_interference": round(constructive_interference, 6),
            "phase_cancellation_meaning": "excessive oscillation loses exclusive pull",
            "constructive_interference_meaning": "context-fit direction gains clarity",
        },
        "natural_damping": {
            "amplitude_decay": round(natural_damping, 6),
            "release_happens_without_force": True,
            "no_forced_exit": True,
            "no_forced_reframe": True,
            "letting_go_emerges": natural_damping >= 0.48,
        },
        "principle": "awareness_opens_a_gap_where_contextual_zero_point_adjustment_phase_cancellation_and_constructive_interference_happen_automatically",
    }


def record_awareness_zero_point_adjustment(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_awareness_zero_point_adjustment()
    if args.record:
        record_awareness_zero_point_adjustment(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
