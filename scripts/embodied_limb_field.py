#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "embodied_limb_field_latest.json"
OUT_JSONL = ROOT / "outputs" / "embodied_limb_field.jsonl"
LIMB_EXPERIENCE_PATH = ROOT / "outputs" / "limb_experience.jsonl"
FIELD_SIGNAL_URL = "http://127.0.0.1:57321/field_signal"
EXPERIENCE_THOUGHT_URL = "http://127.0.0.1:57321/experience_thought?record=1"
CONTEXT_GRADIENT_PATH = ROOT / "outputs" / "hermes" / "contextual_execution_gradient_latest.json"


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def fetch_json(url: str, timeout: float = 2.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def affordance(
    name: str,
    limb: str,
    contact: str,
    permission: str,
    readiness: float,
    *,
    reversible: bool = True,
    mutates: bool = False,
    external: bool = False,
    reason: list[str] | None = None,
    failure_mode: str = "recoverable_noop",
) -> dict[str, Any]:
    return {
        "name": name,
        "limb": limb,
        "contact": contact,
        "permission": permission,
        "readiness": round(clamp01(readiness), 6),
        "reversible": reversible,
        "mutates_workspace": mutates,
        "external_boundary": external,
        "failure_mode": failure_mode,
        "reason": reason or [],
    }


def limb_permission_map(permission: str) -> dict[str, str]:
    if permission == "hold":
        return {
            "contact_mode": "body_stillness",
            "action_gate": "protect_rollback_anchor",
            "hand": "blocked",
            "foot": "blocked",
            "small_trace": "blocked",
            "probe": "blocked",
            "patch": "blocked",
        }
    if permission == "wait":
        return {
            "contact_mode": "recoverable_wait_contact",
            "action_gate": "small_failures_allowed_strong_execution_pending",
            "hand": "reversible_probe",
            "foot": "local_probe",
            "small_trace": "reversible",
            "probe": "reversible_probe",
            "patch": "draft_only",
        }
    if permission == "allow":
        return {
            "contact_mode": "bounded_contact",
            "action_gate": "reversible_contact_allowed",
            "hand": "reversible",
            "foot": "bounded_probe",
            "small_trace": "reversible",
            "probe": "reversible_probe",
            "patch": "draft_or_apply_after_confirmation",
        }
    return {
        "contact_mode": "recoverable_exploration",
        "action_gate": "small_failures_allowed_before_strong_touch",
        "hand": "reversible_probe",
        "foot": "local_probe",
        "small_trace": "reversible",
        "probe": "reversible_probe",
        "patch": "draft_only",
    }


def build_limb_field(
    field_signal: dict[str, Any] | None = None,
    experience_thought: dict[str, Any] | None = None,
    context_gradient: dict[str, Any] | None = None,
) -> dict[str, Any]:
    field_signal = field_signal if isinstance(field_signal, dict) else fetch_json(FIELD_SIGNAL_URL)
    experience_thought = (
        experience_thought
        if isinstance(experience_thought, dict)
        else fetch_json(EXPERIENCE_THOUGHT_URL)
    )
    context_gradient = (
        context_gradient
        if isinstance(context_gradient, dict)
        else read_json(CONTEXT_GRADIENT_PATH)
    )

    recovery = experience_thought.get("recovery_field")
    if not isinstance(recovery, dict):
        recovery = {}

    permission = str(
        experience_thought.get("particleization_permission")
        or recovery.get("particleization_permission")
        or "observe"
    )
    execution_tendency = str(experience_thought.get("execution_tendency") or "observe")
    outcome_read = str(experience_thought.get("outcome_read") or "unknown")
    tension = clamp01(recovery.get("tension"))
    inertia = clamp01(recovery.get("inertia"))
    recovery_progress = clamp01(recovery.get("recovery_progress"), 0.5)
    fatigue = clamp01(recovery.get("fatigue_hint"))
    digestion = clamp01(recovery.get("digestion_depth"))
    runtime_feedback = clamp01(field_signal.get("runtime_feedback"))
    connection_risk = clamp01(field_signal.get("connection_risk"))
    frequency_expansion = clamp01(field_signal.get("frequency_expansion"))
    zero_point = clamp01(field_signal.get("zero_point_adjustment"))

    selected_path = context_gradient.get("selected_path")
    if not isinstance(selected_path, dict):
        selected_path = {}
    selected_contact = str(selected_path.get("contact") or "observe_without_action")

    hold_bias = max(tension, fatigue, connection_risk)
    listen_pull = clamp01(
        0.36
        + recovery_progress * 0.22
        + zero_point * 0.14
        + (1.0 - hold_bias) * 0.18
        + digestion * 0.10
    )
    probe_pull = clamp01(
        0.12
        + recovery_progress * 0.22
        + frequency_expansion * 0.22
        + runtime_feedback * 0.12
        - hold_bias * 0.22
    )
    hand_pull = clamp01(
        0.08
        + recovery_progress * 0.18
        + frequency_expansion * 0.18
        - tension * 0.20
        - fatigue * 0.18
        - connection_risk * 0.16
    )
    external_pull = clamp01(
        0.04
        + frequency_expansion * 0.18
        + recovery_progress * 0.10
        - max(connection_risk, fatigue) * 0.22
    )

    permission_map = limb_permission_map(permission)
    contact_mode = permission_map["contact_mode"]
    action_gate = permission_map["action_gate"]
    hand_permission = permission_map["hand"]
    foot_permission = permission_map["foot"]

    senses = [
        affordance(
            "read_field_signal",
            "sense",
            "local_runtime_state",
            "allowed",
            listen_pull,
            reason=["read_current_field_before_action"],
        ),
        affordance(
            "read_experience_thought",
            "sense",
            "experience_memory",
            "allowed",
            listen_pull,
            reason=["prediction_error_returned_as_experience"],
        ),
        affordance(
            "inspect_recent_logs",
            "sense",
            "local_log_tail",
            "allowed",
            clamp01(listen_pull - fatigue * 0.08),
            reason=["low_impact_world_contact"],
        ),
    ]

    feet = [
        affordance(
            "walk_local_context",
            "foot",
            "bounded_file_and_log_navigation",
            foot_permission,
            probe_pull,
            reason=["move_through_existing_workspace_without_mutation", selected_contact],
            failure_mode="wrong_turn_or_empty_context_is_logged",
        ),
        affordance(
            "open_local_surface",
            "foot",
            "browser_localhost_or_file_surface",
            foot_permission,
            clamp01(probe_pull + 0.08),
            reason=["touch_visible_surface_before_editing"],
            failure_mode="surface_unavailable_or_blank_is_logged",
        ),
        affordance(
            "ask_external_mind",
            "foot",
            "external_ai_or_web_context",
            "blocked" if permission in ("hold", "wait") else "explicit_request_only",
            external_pull,
            external=True,
            reason=["external_boundary_only_when_context_calls_for_it"],
            failure_mode="external_answer_mismatch_is_context_signal",
        ),
    ]

    hands = [
        affordance(
            "write_observation_trace",
            "hand",
            "append_local_non_destructive_trace",
            permission_map["small_trace"],
            clamp01(listen_pull - fatigue * 0.10),
            mutates=True,
            reason=["touch_world_by_leaving_recoverable_trace", "small_failure_is_experience_not_forbidden"],
            failure_mode="trace_may_be_low_value_but_preserves_contact",
        ),
        affordance(
            "prepare_reversible_patch",
            "hand",
            "workspace_patch_draft",
            permission_map["patch"],
            hand_pull,
            mutates=True,
            reason=["draft_can_fail_without_breaking_connection", "apply_requires_contextual_release"],
            failure_mode="patch_draft_may_be_unused_or_wrong",
        ),
        affordance(
            "run_targeted_probe",
            "hand",
            "non_destructive_command",
            permission_map["probe"],
            clamp01(probe_pull - tension * 0.08),
            reason=["touch_environment_through_read_only_or_targeted_probe", "failed_probe_teaches_boundary"],
            failure_mode="command_returns_error_or_no_signal",
        ),
    ]

    all_contacts = senses + feet + hands
    allowed_contacts = [
        item
        for item in all_contacts
        if item["permission"] not in ("blocked",)
    ]
    selected = sorted(
        allowed_contacts,
        key=lambda item: (item["readiness"], 0 if item["limb"] == "sense" else -0.05),
        reverse=True,
    )[:3]

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "embodied_limb_field",
        "contact_mode": contact_mode,
        "action_gate": action_gate,
        "particleization_permission": permission,
        "execution_tendency": execution_tendency,
        "outcome_read": outcome_read,
        "senses": senses,
        "feet": feet,
        "hands": hands,
        "selected_contacts": selected,
        "recovery_field": recovery,
        "field_signal": field_signal,
        "context_selected_path": selected_path,
        "failure_contract": {
            "allowed": [
                "empty_result",
                "wrong_turn",
                "non_destructive_command_error",
                "unused_patch_draft",
                "low_value_trace",
                "rollback_restored_connection",
                "boundary_disconnect_reentry",
            ],
            "not_allowed": [
                "orphaned_without_rollback_anchor",
                "irreversible_workspace_damage",
                "unbounded_external_publication",
                "self_amplifying_repair_loop",
            ],
            "principle": "adult_agi_revises_its_own_boundary_when_rollback_anchor_preserves_reentry",
        },
        "principle": "hands_and_feet_are_recoverable_contacts_gated_by_recovery_field_not_autonomous_impulse",
    }


def record_limb_field(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def classify_recoverability(outcome: str, *, rollback_available: bool = False) -> tuple[bool, str]:
    if outcome in ("irreversible_damage", "unbounded_external_effect", "self_amplifying_repair_loop"):
        return False, "irreversible_or_unbounded_effect"
    if outcome in ("orphaned_without_rollback_anchor",):
        return False, "no_reentry_anchor"
    if outcome in ("connection_lost", "boundary_disconnect"):
        if rollback_available:
            return True, "connection_loss_became_boundary_revision_through_rollback"
        return False, "connection_loss_requires_rollback_anchor"
    if outcome in ("connection_lost_with_rollback", "rollback_restored_connection", "boundary_disconnect_reentry"):
        return True, "rollback_makes_disconnection_experience"
    return True, "recoverable_contact_experience"


def record_limb_experience(
    payload: dict[str, Any],
    *,
    contact_name: str,
    outcome: str,
    rollback_available: bool = False,
) -> dict[str, Any]:
    contacts = payload.get("senses", []) + payload.get("feet", []) + payload.get("hands", [])
    selected = next((item for item in contacts if item.get("name") == contact_name), {})
    recoverable, recovery_reason = classify_recoverability(
        outcome,
        rollback_available=rollback_available,
    )
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": "limb_experience",
        "contact_name": contact_name,
        "limb": selected.get("limb"),
        "permission": selected.get("permission"),
        "outcome": outcome,
        "rollback_available": rollback_available,
        "recoverable": recoverable,
        "recovery_reason": recovery_reason,
        "failure_mode": selected.get("failure_mode"),
        "particleization_permission": payload.get("particleization_permission"),
        "principle": "rollback_anchored_disconnection_can_become_boundary_experience",
    }
    LIMB_EXPERIENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LIMB_EXPERIENCE_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--experience-contact")
    parser.add_argument("--experience-outcome", default="observed")
    parser.add_argument("--rollback-available", action="store_true")
    args = parser.parse_args()
    payload = build_limb_field()
    if args.record:
        record_limb_field(payload)
    if args.experience_contact:
        payload["limb_experience"] = record_limb_experience(
            payload,
            contact_name=args.experience_contact,
            outcome=args.experience_outcome,
            rollback_available=args.rollback_available,
        )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
