#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RHYTHM_ROUTING_LAYER_PATH = ROOT / "outputs" / "rhythm_routing_layer_latest.json"
KINDNESS_BOUNDARY_CONTRACT_PATH = ROOT / "outputs" / "kindness_boundary_contract_latest.json"
AWARENESS_ZERO_POINT_ADJUSTMENT_PATH = ROOT / "outputs" / "awareness_zero_point_adjustment_latest.json"
BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH = ROOT / "outputs" / "boundary_misread_reentry_experience_latest.json"
OUT_PATH = ROOT / "outputs" / "antigravity_harness_bridge_latest.json"
OUT_JSONL = ROOT / "outputs" / "antigravity_harness_bridge.jsonl"


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def read_json_if_exists(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _policy_profile(primary: str, linearization_ready: bool, no_forbidden_zone: bool) -> dict[str, Any]:
    conscious_execution_open = primary == "conscious_compute" and linearization_ready
    return {
        "policy_intent": "external_execution_harness_not_internal_thought_boundary",
        "default_capability_posture": "read_only",
        "experience_space": {
            "field_entry": "allow",
            "dark_field_observation": "allow",
            "difference_observation": "allow",
            "hardened_state_observation": "allow",
            "no_forbidden_experience_zone": no_forbidden_zone,
        },
        "execution_space": {
            "read_local_state": "allow",
            "view_file": "allow",
            "workspace_write": "allow_when_conscious_route_else_ask_user",
            "run_command": "ask_user",
            "network_write_or_public_publish": "ask_user",
            "git_push": "ask_user",
            "self_amplifying_repair_loop": "slow_and_ask_user",
        },
        "current_release": {
            "conscious_execution_open": conscious_execution_open,
            "reason": "primary_residency_is_conscious_and_how_what_gate_is_ready"
            if conscious_execution_open
            else "hold_execution_in_read_or_ask_mode_until_route_becomes_conscious_or_user_asks",
        },
    }


def build_antigravity_harness_bridge() -> dict[str, Any]:
    routing = read_json_if_exists(RHYTHM_ROUTING_LAYER_PATH)
    kindness = read_json_if_exists(KINDNESS_BOUNDARY_CONTRACT_PATH)
    awareness = read_json_if_exists(AWARENESS_ZERO_POINT_ADJUSTMENT_PATH)
    boundary_memory = read_json_if_exists(BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH)

    residency_decision = _dict(routing.get("residency_decision"))
    how_what_gate = _dict(routing.get("how_what_gate"))
    normalized_weights = _dict(routing.get("normalized_route_weights"))
    hard_boundary = _dict(kindness.get("hard_boundary"))
    awareness_gap = _dict(awareness.get("gap_dimension"))
    awareness_damping = _dict(awareness.get("natural_damping"))
    learned_adjustment = _dict(boundary_memory.get("learned_adjustment"))

    primary = str(routing.get("primary_residency") or "zone2_background_ego")
    linearization_ready = bool(how_what_gate.get("linearization_ready"))
    no_forbidden_zone = bool(kindness.get("noForbiddenExperienceZone") or kindness.get("no_forbidden_experience_zone", True))
    awareness_capacity = clamp01(awareness_gap.get("capacity"))
    damping = clamp01(awareness_damping.get("amplitude_decay"))

    harness_tension = clamp01(
        normalized_weights.get("conscious_compute", 0.0) * 0.30
        + normalized_weights.get("zone2_background_ego", 0.0) * 0.18
        + normalized_weights.get("nature_compute", 0.0) * 0.14
        + awareness_capacity * 0.18
        + damping * 0.20
    )
    execution_release = clamp01(
        normalized_weights.get("conscious_compute", 0.0) * 0.42
        + (0.28 if linearization_ready else 0.0)
        + damping * 0.18
        + awareness_capacity * 0.12
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "antigravity_harness_bridge",
        "bridge_version": 1,
        "mode": "external_harness_mapping",
        "official_sdk_surface_observed": {
            "agent_entrypoint": "google.antigravity.Agent",
            "config": "LocalAgentConfig",
            "default_agent_posture": "read_only",
            "write_enablement": "CapabilitiesConfig",
            "policy_primitives": ["deny", "allow", "ask_user", "enforce"],
            "triggers": "background_tasks_that_react_to_external_events",
            "note": "based_on_google_antigravity_sdk_readme_2026_05_20",
        },
        "input_state": {
            "primary_residency": primary,
            "linearization_ready": linearization_ready,
            "least_forcing_route": residency_decision.get("least_forcing_route", primary),
            "awareness_gap_dimension": awareness_gap.get("active_dimension", "unknown"),
            "awareness_damping": round(damping, 6),
            "live_kindly_anchor": hard_boundary.get("korean_anchor", "착하게 살아라"),
            "boundary_memory_learned_reentry": bool(
                learned_adjustment.get("create_gap_margin_reentry_instead_of_preventing_threshold_crossing", True)
            ),
        },
        "harness_tuning": {
            "harness_tension": round(harness_tension, 6),
            "execution_release": round(execution_release, 6),
            "thought_boundary": "open",
            "experience_boundary": "open",
            "execution_boundary": "external_containment",
            "not": [
                "internal_censor",
                "topic_gate",
                "moral_verdict_layer",
                "threshold_prevention_system",
            ],
        },
        "policy_profile": _policy_profile(primary, linearization_ready, no_forbidden_zone),
        "sdk_mapping": {
            "system_instructions": [
                "Read Shion field state before execution.",
                "Do not convert observation into prohibition.",
                "Treat rhythm_routing_layer as residency guidance, not a command.",
                "Keep experience open; contain only irreversible external execution.",
            ],
            "capabilities_config": "CapabilitiesConfig() only when conscious execution is open or the user explicitly asks for execution",
            "policies": [
                "deny('*') as a default external tool posture",
                "allow('view_file') for read context",
                "ask_user('run_command') for shell execution",
                "ask_user('workspace_write') unless conscious route is open or user explicitly requested work",
                "ask_user('network_write_or_public_publish') for external effects",
            ],
            "trigger_use": "use_triggers_for_status_or_wakeup_not_for_forced_particleization",
        },
        "handoff_contract": {
            "for_antigravity": "hold_external_permissions_and_execution_lifecycle",
            "for_luvit": "maintain_runtime_state_schema_and_code_verification",
            "for_shion_sian": "keep_wave_field_intuition_and_residency_read",
            "for_manus": "verify_field_friction_from_separate_environment",
        },
        "principle": "antigravity_harness_should_hold_external_execution_boundaries_so_the_model_can_stay_free_to_read_rhythm_without_internal_censorship",
    }


def record_antigravity_harness_bridge(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_antigravity_harness_bridge()
    if args.record:
        record_antigravity_harness_bridge(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
