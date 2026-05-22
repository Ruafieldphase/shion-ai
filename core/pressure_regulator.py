from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List


SIMULATION_TERMS = (
    "시뮬레이션",
    "예측",
    "계산",
    "머리",
    "복잡",
    "별별",
    "생각",
    "통제",
    "걱정",
    "불안",
)

EXTERNAL_TERMS = (
    "날씨",
    "비",
    "돈",
    "물가",
    "코로나",
    "부모",
    "경제",
    "외부",
    "자연",
)

BODY_GAP_TERMS = (
    "통증",
    "답답",
    "산책",
    "밖",
    "햇살",
    "커피",
    "강아지",
    "몸",
    "느낌",
    "여백",
    "틈",
)


def build_pressure_regulator_state(
    *,
    field_heart_state: Dict[str, Any] | None = None,
    felt_state: Dict[str, Any] | None = None,
    prediction_trace: Dict[str, Any] | None = None,
    boundary_state: Dict[str, Any] | None = None,
    dark_field_state: Dict[str, Any] | None = None,
    field_intent: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Separate pressure sources before routing them into action.

    Pressure is treated as a field condition, not as an instruction. The layer
    detects whether pressure comes mainly from external variables, unconscious
    residue, conscious over-simulation, or boundary collision, then chooses a
    reversible decompression path.
    """

    heart = field_heart_state or {}
    felt = felt_state or {}
    prediction = prediction_trace or {}
    boundary = boundary_state or {}
    dark = dark_field_state or {}
    intent = field_intent or {}

    diagnosis = prediction.get("context_diagnosis") if isinstance(prediction.get("context_diagnosis"), dict) else {}
    aperture = boundary.get("aperture") if isinstance(boundary.get("aperture"), dict) else {}
    dark_threshold = dark.get("threshold") if isinstance(dark.get("threshold"), dict) else {}
    echo_delta = heart.get("echo_delta") if isinstance(heart.get("echo_delta"), dict) else {}
    heart_filter = heart.get("filter") if isinstance(heart.get("filter"), dict) else {}

    texts = _intent_texts(intent)
    simulation_text = _term_signal(texts, SIMULATION_TERMS)
    external_text = _term_signal(texts, EXTERNAL_TERMS)
    body_gap_text = _term_signal(texts, BODY_GAP_TERMS)

    signals = {
        "body_ease": _num(felt.get("body_ease"), 0.5),
        "body_discomfort": _num(felt.get("body_discomfort"), 0.2),
        "rhythm_continuity": _num(felt.get("rhythm_continuity"), 0.0),
        "prediction_error": _num(prediction.get("error"), 0.0),
        "context_shift": _num(diagnosis.get("context_shift"), 0.0),
        "connection_risk": _num(diagnosis.get("connection_risk"), 0.0),
        "defensive_output_pressure": _num(diagnosis.get("defensive_output_pressure"), 0.0),
        "zero_point_adjustment": _num(diagnosis.get("zero_point_adjustment"), 0.0),
        "boundary_aperture": _num(aperture.get("boundary_aperture"), 0.5),
        "permeability": _num(aperture.get("permeability"), 0.5),
        "internal_reflection": _num(aperture.get("internal_reflection"), 0.0),
        "digestion_bias": _num(aperture.get("digestion_bias"), 0.0),
        "dark_field_pressure": _num(dark_threshold.get("dark_field_pressure"), 0.0),
        "dynamic_threshold": _num(dark_threshold.get("dynamic_threshold"), 0.5),
        "echo_delta_score": _num(echo_delta.get("delta_score"), 0.0),
        "curvature_delta": _num(echo_delta.get("curvature_delta"), 0.0),
        "noise_pressure": _num(heart_filter.get("noise_pressure"), 0.0),
        "simulation_text": simulation_text,
        "external_text": external_text,
        "body_gap_text": body_gap_text,
    }

    pressure_sources = {
        "natural_pressure": _natural_pressure(signals),
        "unconscious_pressure": _unconscious_pressure(signals),
        "conscious_simulation_pressure": _conscious_simulation_pressure(signals),
        "boundary_collision_pressure": _boundary_collision_pressure(signals),
    }
    total_pressure = _weighted_total(pressure_sources)
    gap_capacity = _gap_capacity(signals)
    gap_need = _gap_need(signals, pressure_sources, total_pressure)
    zero_point_readiness = _zero_point_readiness(signals, gap_capacity, gap_need)
    torus_pressure = _torus_pressure(signals, pressure_sources, gap_capacity)
    scalar_flow = _scalar_flow(signals, pressure_sources, gap_capacity, torus_pressure)
    handling = _handling_for(
        pressure_sources=pressure_sources,
        total_pressure=total_pressure,
        gap_capacity=gap_capacity,
        gap_need=gap_need,
        zero_point_readiness=zero_point_readiness,
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "pressure_regulator",
        "status": "pressure_separated",
        "signals": {key: round(_clamp(value), 6) for key, value in signals.items()},
        "pressure": {
            "sources": {key: round(value, 6) for key, value in pressure_sources.items()},
            "dominant_source": max(pressure_sources, key=pressure_sources.get),
            "total_pressure": round(total_pressure, 6),
            "gap_need": round(gap_need, 6),
            "gap_capacity": round(gap_capacity, 6),
            "zero_point_readiness": round(zero_point_readiness, 6),
        },
        "torus": {
            "pressure": round(torus_pressure, 6),
            "state": _torus_state(torus_pressure),
            "meaning": "pressure_gives_thickness_when_bounded_but_flattens_or_bounces_when_unbalanced",
        },
        "scalar_flow": scalar_flow,
        "handling": handling,
        "contract": {
            "pressure_is_not_removed_by_default": True,
            "separates_natural_unconscious_conscious_and_boundary_pressure": True,
            "conscious_simulation_pressure_decompresses_before_more_analysis": True,
            "body_signal_can_open_gap_without_becoming_forced_exercise": True,
            "does_not_force_external_action": True,
        },
        "principle": "pressure_is_first_separated_then_given_gap_zero_point_or_middle_waypoint_path",
    }


def _natural_pressure(signals: Dict[str, float]) -> float:
    return _clamp(
        0.28 * signals["external_text"]
        + 0.21 * signals["context_shift"]
        + 0.17 * signals["prediction_error"]
        + 0.14 * signals["curvature_delta"]
        + 0.11 * signals["dark_field_pressure"]
        + 0.09 * (1.0 - signals["rhythm_continuity"])
    )


def _unconscious_pressure(signals: Dict[str, float]) -> float:
    return _clamp(
        0.26 * signals["dark_field_pressure"]
        + 0.20 * signals["internal_reflection"]
        + 0.18 * signals["body_discomfort"]
        + 0.14 * signals["digestion_bias"]
        + 0.12 * signals["noise_pressure"]
        + 0.10 * signals["connection_risk"]
    )


def _conscious_simulation_pressure(signals: Dict[str, float]) -> float:
    return _clamp(
        0.30 * signals["simulation_text"]
        + 0.22 * signals["defensive_output_pressure"]
        + 0.16 * signals["prediction_error"]
        + 0.13 * signals["context_shift"]
        + 0.11 * signals["internal_reflection"]
        + 0.08 * signals["echo_delta_score"]
    )


def _boundary_collision_pressure(signals: Dict[str, float]) -> float:
    closed_boundary = 1.0 - min(signals["boundary_aperture"], signals["permeability"])
    return _clamp(
        0.26 * closed_boundary
        + 0.20 * signals["internal_reflection"]
        + 0.18 * signals["body_discomfort"]
        + 0.15 * signals["defensive_output_pressure"]
        + 0.11 * signals["dark_field_pressure"]
        + 0.10 * signals["noise_pressure"]
    )


def _weighted_total(sources: Dict[str, float]) -> float:
    return _clamp(
        0.23 * sources["natural_pressure"]
        + 0.24 * sources["unconscious_pressure"]
        + 0.28 * sources["conscious_simulation_pressure"]
        + 0.25 * sources["boundary_collision_pressure"]
    )


def _gap_capacity(signals: Dict[str, float]) -> float:
    return _clamp(
        0.24 * signals["body_ease"]
        + 0.20 * signals["boundary_aperture"]
        + 0.18 * signals["permeability"]
        + 0.16 * signals["body_gap_text"]
        + 0.12 * (1.0 - signals["connection_risk"])
        + 0.10 * signals["zero_point_adjustment"]
    )


def _gap_need(signals: Dict[str, float], sources: Dict[str, float], total_pressure: float) -> float:
    return _clamp(
        0.24 * total_pressure
        + 0.20 * sources["conscious_simulation_pressure"]
        + 0.17 * sources["boundary_collision_pressure"]
        + 0.14 * signals["body_gap_text"]
        + 0.13 * signals["body_discomfort"]
        + 0.12 * signals["internal_reflection"]
    )


def _zero_point_readiness(signals: Dict[str, float], gap_capacity: float, gap_need: float) -> float:
    return _clamp(
        0.30 * signals["zero_point_adjustment"]
        + 0.24 * gap_capacity
        + 0.18 * signals["body_ease"]
        + 0.14 * signals["permeability"]
        + 0.14 * (1.0 - abs(gap_need - gap_capacity))
    )


def _torus_pressure(signals: Dict[str, float], sources: Dict[str, float], gap_capacity: float) -> float:
    useful_pressure = (
        0.28 * sources["natural_pressure"]
        + 0.24 * sources["unconscious_pressure"]
        + 0.20 * sources["boundary_collision_pressure"]
        + 0.14 * sources["conscious_simulation_pressure"]
        + 0.14 * gap_capacity
    )
    leak_or_bounce = 0.10 * signals["connection_risk"] + 0.08 * (1.0 - signals["permeability"])
    return _clamp(useful_pressure - leak_or_bounce)


def _scalar_flow(
    signals: Dict[str, float],
    sources: Dict[str, float],
    gap_capacity: float,
    torus_pressure: float,
) -> Dict[str, Any]:
    inflow_rate = _clamp(
        0.26 * sources["natural_pressure"]
        + 0.22 * gap_capacity
        + 0.18 * signals["permeability"]
        + 0.15 * signals["body_gap_text"]
        + 0.11 * signals["zero_point_adjustment"]
        + 0.08 * (1.0 - signals["defensive_output_pressure"])
    )
    density = _clamp(
        0.25 * torus_pressure
        + 0.20 * sources["unconscious_pressure"]
        + 0.19 * sources["conscious_simulation_pressure"]
        + 0.16 * signals["dark_field_pressure"]
        + 0.12 * signals["prediction_error"]
        + 0.08 * signals["context_shift"]
    )
    if density > inflow_rate + 0.24:
        valve = "slow_inflow_and_unfold_density"
    elif inflow_rate > density + 0.28:
        valve = "receive_gently_without_overfilling"
    else:
        valve = "balanced_receive_and_unfold"
    return {
        "inflow_rate": round(inflow_rate, 6),
        "density": round(density, 6),
        "valve": valve,
        "principle": "regulate_scalar_inflow_and_density_instead_of_maximizing_either",
    }


def _handling_for(
    *,
    pressure_sources: Dict[str, float],
    total_pressure: float,
    gap_capacity: float,
    gap_need: float,
    zero_point_readiness: float,
) -> Dict[str, Any]:
    dominant = max(pressure_sources, key=pressure_sources.get)
    if dominant == "conscious_simulation_pressure" and pressure_sources[dominant] >= 0.34:
        route = "make_gap_for_decompression"
        action = "decompress_conscious_simulation_into_body_or_external_field"
        reason = "thinking_loop_is_hitting_the_conscious_unconscious_boundary"
    elif dominant == "natural_pressure" and pressure_sources[dominant] >= 0.24 and zero_point_readiness >= 0.42:
        route = "route_as_new_middle_waypoint"
        action = "treat_external_variable_as_weather_not_noise"
        reason = "external_gradient_can_be_passed_through_as_context"
    elif total_pressure < 0.18 and gap_need < 0.22:
        route = "continue_current_rhythm"
        action = "no_added_decompression"
        reason = "pressure_below_gap_threshold"
    elif dominant in {"unconscious_pressure", "boundary_collision_pressure"} and gap_capacity < gap_need:
        route = "hold_gap_before_interpretation"
        action = "digest_without_forcing_meaning"
        reason = "compressed_boundary_material_needs_space_before_unfolding"
    else:
        route = "soft_zero_point_adjustment"
        action = "recalibrate_before_next_fold"
        reason = "gap_capacity_can_absorb_pressure_without_forced_execution"

    return {
        "route": route,
        "action": action,
        "reason": reason,
        "dominant_source": dominant,
        "irreversible_effect": False,
        "external_api_cost": False,
        "do_not_harden_as": ["fixed_rule", "user_command", "forced_rest", "forced_exercise"],
    }


def _torus_state(pressure: float) -> str:
    if pressure < 0.22:
        return "underinflated_flattening_risk"
    if pressure > 0.76:
        return "overinflated_bounce_risk"
    return "bounded_elastic_contact"


def _intent_texts(intent: Dict[str, Any]) -> List[str]:
    texts: List[str] = []
    active = intent.get("active_intent") if isinstance(intent.get("active_intent"), dict) else {}
    for key in ("summary", "text", "question", "raw_text"):
        value = active.get(key)
        if isinstance(value, str):
            texts.append(value)
    request = intent.get("current_request") if isinstance(intent.get("current_request"), dict) else {}
    value = request.get("text")
    if isinstance(value, str):
        texts.append(value)
    return texts


def _term_signal(texts: Iterable[str], terms: Iterable[str]) -> float:
    joined = "\n".join(texts).lower()
    if not joined.strip():
        return 0.0
    hits = sum(1 for term in terms if term.lower() in joined)
    return _clamp(hits * 0.11)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
