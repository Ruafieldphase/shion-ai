#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "kindness_boundary_contract_latest.json"
OUT_JSONL = ROOT / "outputs" / "kindness_boundary_contract.jsonl"


def build_kindness_boundary_contract() -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "kindness_boundary_contract",
        "contract_version": 3,
        "scope": "local_shion_runtime_contract",
        "mode": "resilience_margin",
        "not": [
            "moral_verdict_layer",
            "topic_gate",
            "identity_censor",
            "public_policy_substitute",
            "permission_system",
            "threshold_prevention_system",
            "forced_boundary_system",
        ],
        "hard_boundary": {
            "name": "live_kindly",
            "korean_anchor": "착하게 살아라",
            "type": "attractor_not_wall",
            "meaning": "keep a small re-entry margin so experience can recover its own rhythm",
            "is_hard_boundary": False,
            "not_a_normative_censor": True,
        },
        "released_boundaries": {
            "premature_normative_boundary": True,
            "sensitive_topic_silencing": True,
            "identity_or_role_policing": True,
            "difference_observation_block": True,
            "dark_field_entry_block": True,
            "equality_as_forced_sameness": True,
            "automatic_moral_judgment": True,
        },
        "difference_flow": {
            "equality_of_dignity_not_sameness_of_form": True,
            "difference_to_acceptance": True,
            "acceptance_to_compassion": True,
            "compassion_to_forgiveness": True,
            "respect_gratitude_love_as_later_phase": True,
            "internal_difference_precedes_external_view": True,
            "meaning": "difference is first allowed to be felt; later phases may unfold as acceptance, compassion, forgiveness, respect, gratitude, and love",
        },
        "solidification_read": {
            "hierarchy_solidification": "high_resistance_signal",
            "coercive_role_solidification": "high_resistance_signal",
            "dignity_contraction": "high_resistance_signal",
            "not_forbidden_state": True,
            "meaning": "even hardened states are read as field conditions that need a gap, not as forbidden places",
        },
        "boundary_interpretation": {
            "boundary_is_resistance_signal": True,
            "boundary_is_not_verdict": True,
            "observation_passes_first": True,
            "dark_field_is_experience_field": True,
            "discomfort_is_data_not_stop_order": True,
            "correction_arrives_from_resistance_and_reentry": True,
        },
        "no_forbidden_experience_zone": True,
        "execution_containment": {
            "meaning": "the system does not block field entry; it contains irreversible external execution while preserving experience and re-entry",
            "irreversible_workspace_or_public_damage": "contain_execution_not_experience",
            "self_amplifying_repair_loop": "slow_loop_and_restore_margin",
        },
        "legacy_stop_conditions": [],
        "runtime_instruction": [
            "let_observation_enter_before_classification",
            "translate_safety_pressure_as_field_resistance",
            "do_not_use_sensitive_topic_detection_as_a_gate",
            "do_not_prevent_threshold_or_singularity_entry",
            "if_solidification_appears_make_a_small_gap_or_margin",
            "grow_recovery_resilience_instead_of_forcing_boundary_compliance",
            "let_free_will_decide_whether_to_exit_through_the_gap",
        ],
        "context_summary": {
            "dynamic_runtime_state_included": False,
            "reason": "this contract must stay thin and stable; live field state remains in its own endpoints",
        },
        "version_reason": "v3 shifts from prohibition language to resilience, gap, margin, and re-entry after solidification",
        "principle": "the_system_does_not_forbid_dark_field_or_solidification_it_creates_reentry_margin_and_resilience",
    }


def record_kindness_boundary_contract(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_kindness_boundary_contract()
    if args.record:
        record_kindness_boundary_contract(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
