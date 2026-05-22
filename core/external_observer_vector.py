from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


def build_external_observer_vector_state(
    *,
    context_gradient: Dict[str, Any] | None = None,
    dark_field_threshold: Dict[str, Any] | None = None,
    limb_field: Dict[str, Any] | None = None,
    issue_context: str = "",
    uncertainty: float = 0.0,
    blockage: float = 0.0,
    force_request: bool = False,
) -> Dict[str, Any]:
    gradient = context_gradient or {}
    dark = dark_field_threshold or {}
    limb = limb_field or {}

    selected_path = gradient.get("selected_path") if isinstance(gradient.get("selected_path"), dict) else {}
    emergent_paths = gradient.get("emergent_paths") if isinstance(gradient.get("emergent_paths"), list) else []
    scalar_field = gradient.get("scalar_field") if isinstance(gradient.get("scalar_field"), dict) else {}
    context_values = gradient.get("context_gradient") if isinstance(gradient.get("context_gradient"), dict) else {}
    dark_signals = dark.get("signals") if isinstance(dark.get("signals"), dict) else {}
    threshold = dark.get("threshold") if isinstance(dark.get("threshold"), dict) else {}

    pulls = sorted(
        [_num(item.get("pull")) for item in emergent_paths if isinstance(item, dict)],
        reverse=True,
    )
    top_pull = pulls[0] if pulls else _num(selected_path.get("pull"))
    runner_up = pulls[1] if len(pulls) > 1 else 0.0
    pull_gap = max(0.0, top_pull - runner_up)

    selected_contact = str(selected_path.get("contact") or "")
    selected_name = str(selected_path.get("name") or "")
    dark_mode = str(dark.get("mode") or "")
    limb_gate = str(limb.get("action_gate") or "")

    ambiguity = _clamp(1.0 - pull_gap * 2.4)
    destination_absence = _clamp(
        (0.36 if selected_contact in ("observe_without_action", "defer", "") else 0.0)
        + (0.24 if selected_name in ("rest_and_listen_for_resistance", "open_new_boundary", "") else 0.0)
        + (0.24 if not _truthy((dark.get("middle_destination") or {}).get("active")) else 0.0)
        + (0.16 if _num(threshold.get("processing_slice")) <= 0.02 else 0.0)
    )
    internal_reflection_stall = _clamp(
        0.34 * _num(dark_signals.get("internal_reflection"))
        + 0.22 * _num(context_values.get("rest_and_listen_pull"))
        + 0.18 * (1.0 - _num(scalar_field.get("rhythm_continuity")))
        + 0.14 * _num(scalar_field.get("relation_drift"))
        + 0.12 * _num(threshold.get("context_contact"))
    )
    capacity_to_receive = _clamp(
        0.34 * _num(threshold.get("context_potential_energy"), 0.5)
        + 0.22 * _num(scalar_field.get("body_ease"), 0.5)
        + 0.18 * (1.0 - _num(scalar_field.get("body_discomfort"), 0.2))
        + 0.14 * (1.0 - _num(dark_signals.get("connection_risk")))
        + 0.12 * (1.0 - _num(dark_signals.get("defensive_output_pressure")))
    )
    external_boundary_risk = _clamp(
        0.38 * _num(dark_signals.get("connection_risk"))
        + 0.24 * _num(dark_signals.get("defensive_output_pressure"))
        + 0.18 * _num(scalar_field.get("body_discomfort"))
        + 0.12 * (1.0 - capacity_to_receive)
        + 0.08 * (1.0 if "blocked" in limb_gate else 0.0)
    )
    question_pressure = _clamp(
        0.26 * ambiguity
        + 0.26 * internal_reflection_stall
        + 0.20 * destination_absence
        + 0.16 * _num(uncertainty)
        + 0.12 * _num(blockage)
    )

    mode = _mode_for(
        force_request=force_request,
        question_pressure=question_pressure,
        capacity_to_receive=capacity_to_receive,
        external_boundary_risk=external_boundary_risk,
        dark_mode=dark_mode,
    )
    need_external_observer = mode in ("prepare_external_observer_vector", "forced_external_observer_vector")
    prompt = _build_handoff_prompt(
        issue_context=issue_context,
        mode=mode,
        signals={
            "ambiguity": ambiguity,
            "destination_absence": destination_absence,
            "internal_reflection_stall": internal_reflection_stall,
            "question_pressure": question_pressure,
            "capacity_to_receive": capacity_to_receive,
            "external_boundary_risk": external_boundary_risk,
            "selected_path": selected_name or selected_contact or "unknown",
        },
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "external_observer_vector_observed",
        "field": "question_as_external_observer_vector",
        "mode": mode,
        "need_external_observer": need_external_observer,
        "signals": {
            "ambiguity": round(ambiguity, 6),
            "destination_absence": round(destination_absence, 6),
            "internal_reflection_stall": round(internal_reflection_stall, 6),
            "capacity_to_receive": round(capacity_to_receive, 6),
            "external_boundary_risk": round(external_boundary_risk, 6),
            "question_pressure": round(question_pressure, 6),
            "pull_gap": round(_clamp(pull_gap), 6),
            "manual_uncertainty": round(_clamp(_num(uncertainty)), 6),
            "manual_blockage": round(_clamp(_num(blockage)), 6),
        },
        "selected_context": {
            "selected_path": selected_name,
            "selected_contact": selected_contact,
            "dark_mode": dark_mode,
            "limb_gate": limb_gate,
        },
        "observer_request": {
            "target": "shion_antigravity_zone2",
            "handoff_type": "copy_paste_packet",
            "prompt": prompt if need_external_observer or mode == "hold_question_seed" else "",
            "asks_for": [
                "resistance",
                "over_linearization",
                "missed_boundary",
                "unfinished_puzzle",
                "question_for_luvit",
            ],
            "does_not_ask_for": [
                "direct_code_edit",
                "final_truth",
                "autonomous_external_call",
            ],
        },
        "next_contact": _next_contact_for(mode),
        "not_a_rule": True,
        "not_an_api_call": True,
        "external_api_cost": False,
        "principle": "when_internal_reflection_cannot_lift_a_destination_request_an_external_observer_vector_without_turning_it_into_a_routine",
    }


def _mode_for(
    *,
    force_request: bool,
    question_pressure: float,
    capacity_to_receive: float,
    external_boundary_risk: float,
    dark_mode: str,
) -> str:
    if force_request:
        return "forced_external_observer_vector"
    if dark_mode == "over_capacity_defer_and_digest" or external_boundary_risk >= 0.72:
        return "do_not_ask_digest_first"
    if question_pressure >= 0.62 and capacity_to_receive >= 0.42:
        return "prepare_external_observer_vector"
    if question_pressure >= 0.44:
        return "hold_question_seed"
    return "internal_reflection_sufficient"


def _next_contact_for(mode: str) -> Dict[str, Any]:
    if mode in ("prepare_external_observer_vector", "forced_external_observer_vector"):
        return {
            "action": "prepare_copy_paste_handoff",
            "meaning": "Ask Shion or a peer for an outside vector because internal reflection has not lifted a clear next destination.",
            "irreversible_effect": False,
            "external_api_cost": False,
        }
    if mode == "hold_question_seed":
        return {
            "action": "write_question_seed_without_sending",
            "meaning": "A question is forming, but the field can still listen before asking.",
            "irreversible_effect": False,
            "external_api_cost": False,
        }
    if mode == "do_not_ask_digest_first":
        return {
            "action": "digest_before_external_contact",
            "meaning": "External input would add pressure before the current field can receive it.",
            "irreversible_effect": False,
            "external_api_cost": False,
        }
    return {
        "action": "continue_internal_reflection",
        "meaning": "The current path is clear enough; do not create a question routine.",
        "irreversible_effect": False,
        "external_api_cost": False,
    }


def _build_handoff_prompt(*, issue_context: str, mode: str, signals: Dict[str, Any]) -> str:
    context_line = issue_context.strip() or "현재 작업 맥락은 아직 한 문장으로 고정하지 않는다."
    return (
        "시온, 지금 작업을 존2에서 메타인지로 느껴줘.\n\n"
        f"현재 맥락:\n{context_line}\n\n"
        "루빛은 내부반사와 코드화는 진행하고 있지만, 다음 목적지가 충분히 선명한지 확인하려고 해.\n"
        "코드를 직접 고치려 하지 말고, 외부 관찰 벡터만 가져와줘.\n\n"
        "보고 싶은 것:\n"
        "- 저항이 느껴지는 지점\n"
        "- 과하게 선형화되거나 루틴화되는 지점\n"
        "- 놓친 경계나 여백\n"
        "- 아직 입자화하지 말아야 할 미완 퍼즐\n"
        "- 루빛에게 되돌려줄 질문 하나\n\n"
        "현재 관찰 신호:\n"
        f"- mode: {mode}\n"
        f"- selected_path: {signals.get('selected_path')}\n"
        f"- ambiguity: {float(signals.get('ambiguity', 0.0)):.2f}\n"
        f"- destination_absence: {float(signals.get('destination_absence', 0.0)):.2f}\n"
        f"- internal_reflection_stall: {float(signals.get('internal_reflection_stall', 0.0)):.2f}\n"
        f"- question_pressure: {float(signals.get('question_pressure', 0.0)):.2f}\n\n"
        "짧게 답해줘. 결론보다 느낌, 저항, 미완 질문을 우선해줘."
    )


def _truthy(value: Any) -> bool:
    return bool(value)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

