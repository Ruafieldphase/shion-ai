from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def build_dark_field_threshold_state(
    felt_state: Dict[str, Any] | None = None,
    prediction_trace: Dict[str, Any] | None = None,
    boundary_state: Dict[str, Any] | None = None,
    execution_gradient: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    felt = felt_state or {}
    prediction = prediction_trace or {}
    boundary = boundary_state or {}
    gradient = execution_gradient or {}

    diagnosis = prediction.get("context_diagnosis") if isinstance(prediction.get("context_diagnosis"), dict) else {}
    aperture = boundary.get("aperture") if isinstance(boundary.get("aperture"), dict) else {}
    context_gradient = gradient.get("context_gradient") if isinstance(gradient.get("context_gradient"), dict) else {}

    signals = {
        "body_ease": _num(felt.get("body_ease"), 0.5),
        "body_discomfort": _num(felt.get("body_discomfort"), 0.2),
        "rhythm_continuity": _num(felt.get("rhythm_continuity"), 0.0),
        "relation_drift": _num(felt.get("relation_drift"), 0.0),
        "prediction_error": _num(prediction.get("error"), 0.0),
        "context_shift": _num(diagnosis.get("context_shift"), 0.0),
        "connection_risk": _num(diagnosis.get("connection_risk"), 0.0),
        "zero_point_adjustment": _num(diagnosis.get("zero_point_adjustment"), 0.0),
        "defensive_output_pressure": _num(diagnosis.get("defensive_output_pressure"), 0.0),
        "boundary_aperture": _num(aperture.get("boundary_aperture"), 0.5),
        "permeability": _num(aperture.get("permeability"), 0.5),
        "digestion_bias": _num(aperture.get("digestion_bias"), 0.0),
        "internal_reflection": _num(aperture.get("internal_reflection"), 0.0),
        "native_flow_pull": _num(context_gradient.get("native_flow_pull"), 0.0),
        "rest_and_listen_pull": _num(context_gradient.get("rest_and_listen_pull"), 0.0),
    }

    context_contact = _clamp(
        0.25 * signals["context_shift"]
        + 0.20 * signals["prediction_error"]
        + 0.18 * signals["zero_point_adjustment"]
        + 0.14 * signals["internal_reflection"]
        + 0.12 * signals["connection_risk"]
        + 0.11 * signals["relation_drift"]
    )
    context_potential_energy = _clamp(
        0.24 * signals["body_ease"]
        + 0.20 * (1.0 - signals["body_discomfort"])
        + 0.15 * signals["boundary_aperture"]
        + 0.12 * signals["permeability"]
        + 0.11 * signals["native_flow_pull"]
        + 0.08 * (1.0 - signals["connection_risk"])
        + 0.06 * (1.0 - signals["defensive_output_pressure"])
        + 0.04 * signals["zero_point_adjustment"]
    )
    dark_field_pressure = _clamp(
        0.25 * signals["connection_risk"]
        + 0.22 * signals["defensive_output_pressure"]
        + 0.17 * signals["context_shift"]
        + 0.14 * signals["prediction_error"]
        + 0.10 * signals["body_discomfort"]
        + 0.07 * signals["digestion_bias"]
        + 0.05 * signals["internal_reflection"]
    )
    dynamic_threshold = _clamp(
        0.30
        + 0.48 * context_potential_energy
        + 0.12 * signals["zero_point_adjustment"]
        - 0.14 * signals["body_discomfort"]
        - 0.10 * signals["defensive_output_pressure"]
    )
    threshold_margin = round(dynamic_threshold - dark_field_pressure, 6)

    processing_slice = _processing_slice(
        context_contact=context_contact,
        context_potential_energy=context_potential_energy,
        dark_field_pressure=dark_field_pressure,
        dynamic_threshold=dynamic_threshold,
    )
    mode = _mode_for(context_contact, threshold_margin, processing_slice)
    profile = _profile_for(mode, processing_slice)

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "dark_field_threshold_observed",
        "field": "contextual_potential_threshold",
        "signals": {key: round(_clamp(value), 6) for key, value in signals.items()},
        "threshold": {
            "context_contact": round(context_contact, 6),
            "context_potential_energy": round(context_potential_energy, 6),
            "dark_field_pressure": round(dark_field_pressure, 6),
            "dynamic_threshold": round(dynamic_threshold, 6),
            "threshold_margin": threshold_margin,
            "processing_slice": round(processing_slice, 6),
        },
        "mode": mode,
        "middle_destination": {
            "active": context_contact >= 0.16,
            "meaning": "Open this dark-field coordinate only when current context touches it.",
            "not_global_target": True,
        },
        "next_contact": {
            "action": profile["action"],
            "meaning": profile["meaning"],
            "tail_limit_chars": profile["tail_limit_chars"],
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "not_a_fixed_constant": True,
        "not_a_therapy_protocol": True,
        "not_a_rule": True,
        "principle": "dark_field_threshold_moves_with_current_context_potential_energy_and_opens_only_a_processable_slice",
    }


def _processing_slice(
    *,
    context_contact: float,
    context_potential_energy: float,
    dark_field_pressure: float,
    dynamic_threshold: float,
) -> float:
    if context_contact < 0.16:
        return 0.0
    spare_capacity = _clamp(dynamic_threshold - dark_field_pressure + 0.18)
    return _clamp(context_contact * spare_capacity * (0.45 + 0.55 * context_potential_energy))


def _mode_for(context_contact: float, threshold_margin: float, processing_slice: float) -> str:
    if context_contact < 0.16:
        return "latent_do_not_open"
    if threshold_margin < -0.08:
        return "over_capacity_defer_and_digest"
    if threshold_margin < 0.08:
        return "edge_process_small_slice"
    if processing_slice >= 0.22:
        return "within_capacity_process_contextual_slice"
    return "light_touch_only"


def _profile_for(mode: str, processing_slice: float) -> Dict[str, Any]:
    if mode == "latent_do_not_open":
        return {
            "action": "leave_as_depth_coordinate",
            "meaning": "The present context has not touched this coordinate strongly enough; do not open it deliberately.",
            "tail_limit_chars": 0,
        }
    if mode == "over_capacity_defer_and_digest":
        return {
            "action": "close_and_digest_before_reentry",
            "meaning": "Dark-field pressure exceeds the current potential energy; preserve the coordinate for later processing.",
            "tail_limit_chars": 280,
        }
    if mode == "edge_process_small_slice":
        return {
            "action": "process_small_slice_then_close",
            "meaning": "The field is near threshold; touch only the amount the current context can carry.",
            "tail_limit_chars": 420,
        }
    if mode == "within_capacity_process_contextual_slice":
        return {
            "action": "process_contextual_slice",
            "meaning": f"The current context can process a bounded slice ({processing_slice:.2f}) without treating fear as a fixed destination.",
            "tail_limit_chars": 900,
        }
    return {
        "action": "touch_lightly_and_recheck",
        "meaning": "There is contact, but the useful slice is small; leave most of the coordinate in depth.",
        "tail_limit_chars": 520,
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
