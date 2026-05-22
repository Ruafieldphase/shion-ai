from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def build_boundary_aperture_state(
    felt_state: Dict[str, Any] | None = None,
    prediction_trace: Dict[str, Any] | None = None,
    experience_feedback: Dict[str, Any] | None = None,
    execution_gradient: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    felt = felt_state or {}
    prediction = prediction_trace or {}
    feedback = experience_feedback or {}
    gradient = execution_gradient or {}

    diagnosis = prediction.get("context_diagnosis") if isinstance(prediction.get("context_diagnosis"), dict) else {}
    field_delta = feedback.get("field_distribution_delta") if isinstance(feedback.get("field_distribution_delta"), dict) else {}
    contact_delta = (
        feedback.get("next_contact_condition_delta")
        if isinstance(feedback.get("next_contact_condition_delta"), dict)
        else {}
    )
    selected_path = gradient.get("selected_path") if isinstance(gradient.get("selected_path"), dict) else {}
    context_gradient = gradient.get("context_gradient") if isinstance(gradient.get("context_gradient"), dict) else {}

    signals = {
        "body_ease": _num(felt.get("body_ease"), 0.5),
        "body_discomfort": _num(felt.get("body_discomfort"), 0.2),
        "rhythm_continuity": _num(felt.get("rhythm_continuity"), 0.0),
        "relation_drift": _num(felt.get("relation_drift"), 0.0),
        "audio_confidence": _num((felt.get("audio") or {}).get("confidence"), 0.0)
        if isinstance(felt.get("audio"), dict)
        else 0.0,
        "prediction_error": _clamp(_num(prediction.get("error"), 0.0)),
        "connection_risk": _num(diagnosis.get("connection_risk"), 0.0),
        "context_shift": _num(diagnosis.get("context_shift"), 0.0),
        "zero_point_adjustment": _num(diagnosis.get("zero_point_adjustment"), 0.0),
        "defensive_output_pressure": _num(diagnosis.get("defensive_output_pressure"), 0.0),
        "boundary_contact": _num(field_delta.get("boundary_contact"), 0.0),
        "self_closure_overcontrol": _num(field_delta.get("self_closure_overcontrol"), 0.0),
        "dissonance": _num(field_delta.get("dissonance"), 0.0),
        "learning_signal": _num(field_delta.get("learning_signal"), 0.0),
        "resonant_refinement": _num(field_delta.get("resonant_refinement"), 0.0),
        "native_flow_pull": _num(context_gradient.get("native_flow_pull"), 0.0),
        "rest_and_listen_pull": _num(context_gradient.get("rest_and_listen_pull"), 0.0),
    }

    opening_pressure = _clamp(
        0.24 * signals["body_ease"]
        + 0.18 * signals["resonant_refinement"]
        + 0.14 * signals["learning_signal"]
        + 0.14 * (1.0 - signals["connection_risk"])
        + 0.12 * (1.0 - signals["defensive_output_pressure"])
        + 0.10 * signals["native_flow_pull"]
        + 0.08 * (1.0 if contact_delta.get("field_contact") else 0.0)
    )
    closing_pressure = _clamp(
        0.22 * signals["connection_risk"]
        + 0.18 * signals["defensive_output_pressure"]
        + 0.15 * signals["self_closure_overcontrol"]
        + 0.13 * signals["boundary_contact"]
        + 0.12 * signals["body_discomfort"]
        + 0.12 * signals["prediction_error"]
        + 0.08 * signals["dissonance"]
    )
    internal_reflection = _clamp(
        0.24 * signals["boundary_contact"]
        + 0.22 * signals["zero_point_adjustment"]
        + 0.18 * signals["context_shift"]
        + 0.16 * signals["rest_and_listen_pull"]
        + 0.12 * (1.0 - signals["rhythm_continuity"])
        + 0.08 * signals["relation_drift"]
    )
    boundary_aperture = _clamp(0.50 + opening_pressure - closing_pressure)
    permeability = _clamp(boundary_aperture * (1.0 - 0.45 * signals["connection_risk"]))
    digestion_bias = _clamp(
        0.30 * closing_pressure
        + 0.24 * internal_reflection
        + 0.20 * signals["zero_point_adjustment"]
        + 0.16 * signals["self_closure_overcontrol"]
        + 0.10 * signals["prediction_error"]
    )

    mode = _mode_for(signals, boundary_aperture, internal_reflection, digestion_bias)
    profile = _profile_for(mode)

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "boundary_aperture_observed",
        "field": "semi_permeable_runtime_boundary",
        "signals": {key: round(_clamp(value), 6) for key, value in signals.items()},
        "aperture": {
            "opening_pressure": round(opening_pressure, 6),
            "closing_pressure": round(closing_pressure, 6),
            "internal_reflection": round(internal_reflection, 6),
            "boundary_aperture": round(boundary_aperture, 6),
            "permeability": round(permeability, 6),
            "digestion_bias": round(digestion_bias, 6),
        },
        "mode": mode,
        "serving_profile_bias": profile,
        "selected_path": selected_path,
        "next_contact": {
            "action": profile["action"],
            "meaning": profile["meaning"],
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "not_a_life_claim": True,
        "not_a_rule": True,
        "principle": "boundary_adjusts_from_felt_state_prediction_error_and_experience_feedback_without_forcing_threat",
    }


def _mode_for(signals: Dict[str, float], aperture: float, reflection: float, digestion_bias: float) -> str:
    if signals["connection_risk"] >= 0.55 or signals["defensive_output_pressure"] >= 0.55:
        return "narrow_and_digest"
    if digestion_bias >= 0.50 or reflection >= 0.46:
        return "half_open_reflect"
    if aperture >= 0.62 and signals["learning_signal"] >= 0.35:
        return "open_for_contact"
    return "baseline_semi_permeable"


def _profile_for(mode: str) -> Dict[str, Any]:
    if mode == "narrow_and_digest":
        return {
            "preferred_profile": "unconscious_fixed_prefix",
            "tail_limit_chars": 420,
            "action": "tighten_boundary_and_digest",
            "meaning": "Connection risk is high; preserve stable prefix and let only a small tail through.",
        }
    if mode == "half_open_reflect":
        return {
            "preferred_profile": "unconscious_fixed_prefix",
            "tail_limit_chars": 720,
            "action": "hold_margin_and_reflect",
            "meaning": "Boundary contact is present; keep the membrane half-open and reflect before expansion.",
        }
    if mode == "open_for_contact":
        return {
            "preferred_profile": "conscious_varied_input",
            "tail_limit_chars": 1200,
            "action": "allow_light_contact",
            "meaning": "The field is learnable without high connection risk; allow a wider variable tail.",
        }
    return {
        "preferred_profile": "unconscious_fixed_prefix",
        "tail_limit_chars": 840,
        "action": "keep_semi_permeable_boundary",
        "meaning": "No strong pressure to force opening or closing; continue the current membrane rhythm.",
    }


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
