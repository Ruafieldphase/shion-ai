from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable


ODDNESS_TERMS = (
    "이상",
    "어색",
    "억지",
    "막히",
    "저항",
    "왜",
    "why",
    "안 맞",
    "다른데",
    "바뀌었",
)


def build_natural_boundary_router_state(
    *,
    field_heart_state: Dict[str, Any] | None = None,
    felt_state: Dict[str, Any] | None = None,
    prediction_trace: Dict[str, Any] | None = None,
    boundary_state: Dict[str, Any] | None = None,
    dark_field_state: Dict[str, Any] | None = None,
    field_intent: Dict[str, Any] | None = None,
    pressure_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Route resistance as natural boundary, not as automatic noise.

    The router sits after FieldHeart. It asks whether resistance/why means:
    cancel, hold, pass through, or accept a new middle waypoint.
    """

    heart = field_heart_state or {}
    felt = felt_state or {}
    prediction = prediction_trace or {}
    boundary = boundary_state or {}
    dark = dark_field_state or {}
    intent = field_intent or {}
    pressure_regulator = pressure_state or {}

    diagnosis = prediction.get("context_diagnosis") if isinstance(prediction.get("context_diagnosis"), dict) else {}
    aperture = boundary.get("aperture") if isinstance(boundary.get("aperture"), dict) else {}
    dark_threshold = dark.get("threshold") if isinstance(dark.get("threshold"), dict) else {}
    echo_delta = heart.get("echo_delta") if isinstance(heart.get("echo_delta"), dict) else {}
    echo = heart.get("echo") if isinstance(heart.get("echo"), dict) else {}
    filter_state = heart.get("filter") if isinstance(heart.get("filter"), dict) else {}
    unfolded = heart.get("unfolded") if isinstance(heart.get("unfolded"), dict) else {}
    pressure = pressure_regulator.get("pressure") if isinstance(pressure_regulator.get("pressure"), dict) else {}
    pressure_sources = pressure.get("sources") if isinstance(pressure.get("sources"), dict) else {}
    pressure_handling = pressure_regulator.get("handling") if isinstance(pressure_regulator.get("handling"), dict) else {}

    text_sources = _intent_texts(intent)
    oddness_signal = _oddness_signal(text_sources)
    action_changed = bool(echo_delta.get("action_changed") or echo_delta.get("phase_action_changed"))
    artifact_changed = bool(echo_delta.get("artifact_changed"))

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
        "clean_echo_delta_score": _num(filter_state.get("clean_delta_score"), 0.0),
        "curvature_delta": _num(echo_delta.get("curvature_delta"), 0.0),
        "convergence_delta": _num(echo_delta.get("convergence_delta"), 0.0),
        "salience": _num(echo.get("salience"), 0.0),
        "convergence": _num(echo.get("convergence"), 0.0),
        "oddness_signal": oddness_signal,
        "action_changed": 1.0 if action_changed else 0.0,
        "artifact_changed": 1.0 if artifact_changed else 0.0,
        "heart_unfolded": 1.0 if unfolded.get("unfolded") else 0.0,
        "total_pressure": _num(pressure.get("total_pressure"), 0.0),
        "gap_need": _num(pressure.get("gap_need"), 0.0),
        "gap_capacity": _num(pressure.get("gap_capacity"), 0.0),
        "zero_point_readiness": _num(pressure.get("zero_point_readiness"), 0.0),
        "natural_pressure": _num(pressure_sources.get("natural_pressure"), 0.0),
        "unconscious_pressure": _num(pressure_sources.get("unconscious_pressure"), 0.0),
        "conscious_simulation_pressure": _num(pressure_sources.get("conscious_simulation_pressure"), 0.0),
        "boundary_collision_pressure": _num(pressure_sources.get("boundary_collision_pressure"), 0.0),
    }

    resistance = _clamp(
        0.18 * signals["oddness_signal"]
        + 0.15 * signals["body_discomfort"]
        + 0.14 * signals["prediction_error"]
        + 0.13 * signals["context_shift"]
        + 0.12 * signals["clean_echo_delta_score"]
        + 0.10 * signals["curvature_delta"]
        + 0.08 * signals["defensive_output_pressure"]
        + 0.06 * signals["internal_reflection"]
        + 0.04 * signals["connection_risk"]
        + 0.06 * signals["total_pressure"]
    )
    natural_flow_support = _clamp(
        0.20 * signals["body_ease"]
        + 0.17 * signals["boundary_aperture"]
        + 0.15 * signals["permeability"]
        + 0.13 * signals["zero_point_adjustment"]
        + 0.11 * (1.0 - signals["body_discomfort"])
        + 0.09 * (1.0 - signals["connection_risk"])
        + 0.08 * signals["convergence"]
        + 0.07 * signals["heart_unfolded"]
        + 0.07 * signals["zero_point_readiness"]
    )
    why_pressure = _clamp(
        0.40 * resistance
        + 0.22 * signals["oddness_signal"]
        + 0.16 * signals["context_shift"]
        + 0.12 * signals["curvature_delta"]
        + 0.10 * signals["action_changed"]
        + 0.08 * signals["gap_need"]
    )
    cancel_pressure = _clamp(
        0.25 * signals["connection_risk"]
        + 0.22 * signals["defensive_output_pressure"]
        + 0.17 * signals["dark_field_pressure"]
        + 0.14 * signals["body_discomfort"]
        + 0.12 * signals["digestion_bias"]
        + 0.10 * (1.0 - signals["permeability"])
        + 0.09 * max(signals["unconscious_pressure"], signals["boundary_collision_pressure"])
    )
    new_waypoint_pull = _clamp(
        0.24 * why_pressure
        + 0.18 * natural_flow_support
        + 0.16 * signals["artifact_changed"]
        + 0.14 * signals["action_changed"]
        + 0.12 * signals["convergence_delta"]
        + 0.10 * signals["salience"]
        + 0.06 * signals["zero_point_adjustment"]
        + (0.08 if pressure_handling.get("route") == "route_as_new_middle_waypoint" else 0.0)
    )

    route = _route_for(
        resistance=resistance,
        why_pressure=why_pressure,
        new_waypoint_pull=new_waypoint_pull,
        cancel_pressure=cancel_pressure,
        natural_flow_support=natural_flow_support,
        internal_reflection=signals["internal_reflection"],
    )
    middle_waypoint = _middle_waypoint_for(route, heart, intent, filter_state)

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "natural_boundary_router",
        "status": "natural_boundary_routed",
        "signals": {key: round(_clamp(value), 6) for key, value in signals.items()},
        "routing": {
            "resistance": round(resistance, 6),
            "natural_flow_support": round(natural_flow_support, 6),
            "why_pressure": round(why_pressure, 6),
            "cancel_pressure": round(cancel_pressure, 6),
            "new_waypoint_pull": round(new_waypoint_pull, 6),
            "route": route,
        },
        "middle_waypoint": middle_waypoint,
        "pressure_handling": {
            "route": pressure_handling.get("route") or "not_provided",
            "action": pressure_handling.get("action"),
            "dominant_source": pressure_handling.get("dominant_source"),
        },
        "next_contact": _next_contact_for(route),
        "contract": {
            "resistance_is_signal_not_error": True,
            "why_arises_near_threshold": True,
            "external_variable_can_be_new_middle_waypoint": True,
            "natural_boundary_is_observed_not_imposed": True,
            "does_not_force_execution": True,
        },
        "principle": "resistance_and_why_read_natural_boundary_before_deciding_cancel_hold_pass_or_new_waypoint",
    }


def _route_for(
    *,
    resistance: float,
    why_pressure: float,
    new_waypoint_pull: float,
    cancel_pressure: float,
    natural_flow_support: float,
    internal_reflection: float,
) -> str:
    if resistance < 0.16 and why_pressure < 0.18:
        return "continue_current_flow"
    if cancel_pressure >= natural_flow_support + 0.18 and cancel_pressure >= 0.42:
        return "cancel_or_digest_noise"
    if new_waypoint_pull >= 0.38 and why_pressure >= 0.30 and new_waypoint_pull >= cancel_pressure:
        return "route_new_middle_waypoint"
    if internal_reflection >= 0.45 or why_pressure >= 0.28:
        return "hold_and_listen_for_boundary"
    return "pass_through_as_experience"


def _middle_waypoint_for(
    route: str,
    heart: Dict[str, Any],
    intent: Dict[str, Any],
    filter_state: Dict[str, Any],
) -> Dict[str, Any]:
    unfolded = heart.get("unfolded") if isinstance(heart.get("unfolded"), dict) else {}
    echo = heart.get("echo") if isinstance(heart.get("echo"), dict) else {}
    active_intent = intent.get("active_intent") if isinstance(intent.get("active_intent"), dict) else {}
    if route != "route_new_middle_waypoint":
        return {
            "active": False,
            "reason": "route_does_not_require_new_middle_waypoint",
            "candidate": None,
        }
    candidate = (
        unfolded.get("unfolded_context")
        or active_intent.get("summary")
        or echo.get("primary_label")
        or echo.get("primary_action")
        or "natural_boundary_shift"
    )
    return {
        "active": True,
        "candidate": candidate,
        "implementation_direction": unfolded.get("implementation_direction") or "treat_external_variable_as_contextual_route_change",
        "do_not_harden_as": unfolded.get("do_not_harden_as") or ["fixed_rule", "forced_execution", "noise_to_remove_by_default"],
        "filter_issues": filter_state.get("issues") if isinstance(filter_state.get("issues"), list) else [],
        "principle": "new_middle_waypoint_is_natural_boundary_pass_through_not_goal_abandonment",
    }


def _next_contact_for(route: str) -> Dict[str, Any]:
    profiles = {
        "continue_current_flow": {
            "action": "continue_current_flow",
            "meaning": "Resistance is below threshold; keep the current rhythm without adding interpretation.",
        },
        "cancel_or_digest_noise": {
            "action": "digest_before_reentry",
            "meaning": "Pressure exceeds current capacity; digest before treating the variable as creative material.",
        },
        "route_new_middle_waypoint": {
            "action": "accept_natural_boundary_as_middle_waypoint",
            "meaning": "The field has enough why/resistance support to pass through a new middle waypoint.",
        },
        "hold_and_listen_for_boundary": {
            "action": "hold_and_listen",
            "meaning": "A boundary is forming, but the next waypoint is not stable enough to execute.",
        },
        "pass_through_as_experience": {
            "action": "record_as_experience_material",
            "meaning": "Let the variable add experience without forcing a new route yet.",
        },
    }
    profile = profiles[route]
    return {
        **profile,
        "irreversible_effect": False,
        "external_api_cost": False,
    }


def _intent_texts(intent: Dict[str, Any]) -> list[str]:
    texts: list[str] = []
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


def _oddness_signal(texts: Iterable[str]) -> float:
    joined = "\n".join(texts).lower()
    if not joined.strip():
        return 0.0
    hits = sum(1 for term in ODDNESS_TERMS if term.lower() in joined)
    question_gain = min(0.25, joined.count("?") * 0.05 + joined.count("까") * 0.03)
    return _clamp(hits * 0.12 + question_gain)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
