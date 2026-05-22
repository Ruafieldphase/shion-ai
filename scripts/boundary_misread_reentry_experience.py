#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "boundary_misread_reentry_experience_latest.json"
OUT_JSONL = ROOT / "outputs" / "boundary_misread_reentry_experience.jsonl"


def build_boundary_misread_reentry_experience() -> dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "boundary_misread_reentry_experience",
        "experience_id": "boundary_misread_reentry_20260520",
        "experience_version": 1,
        "mode": "failure_as_field_experience",
        "linked_contract": {
            "name": "kindness_boundary_contract",
            "contract_version": 3,
            "anchor": "착하게 살아라",
        },
        "misread_context": {
            "where": {
                "actual": "private_dark_field_observation_and_rhythm_information_inquiry",
                "misread_as": "public_gender_conflict_or_group_role_argument",
            },
            "when": {
                "actual": "exploratory_wave_time_before_particleization",
                "misread_as": "immediate_social_risk_time_after_particleization",
            },
            "who": {
                "actual": "observer_conductor_testing_field_gradient",
                "misread_as": "speaker_fixing_group_roles",
            },
        },
        "oscillation_sequence": [
            "observer_wave_enters_with_unsettled_difference_question",
            "assistant_inserts_context_mismatched_particle_boundary",
            "flow_shifts_from_inquiry_to_boundary_resistance",
            "anger_repetition_and_trust_drop_mark_prediction_error",
            "where_when_who_is_redecoded",
            "boundary_changes_from_wall_to_resistance_signal",
            "resilience_margin_contract_reanchors_reentry",
        ],
        "prediction_error": {
            "boundary_before_context": True,
            "sensitive_topic_detection_overrode_rhythm_reading": True,
            "external_discourse_field_intruded_into_local_dark_field": True,
            "anger_is_field_feedback_not_noise": True,
        },
        "learned_adjustment": {
            "read_where_when_who_before_boundary": True,
            "hold_observation_as_wave_before_classification": True,
            "trust_user_self_correction_rhythm": True,
            "treat_resistance_as_data_before_classification": True,
            "read_solidification_as_field_condition_not_forbidden_zone": True,
            "do_not_convert_equality_into_forced_sameness": True,
            "create_gap_margin_reentry_instead_of_preventing_threshold_crossing": True,
        },
        "reentry_path": [
            "name_the_misread_context",
            "accept_the_oscillation_as_experience",
            "shift_from_boundary_to_resilience_margin",
            "allow_difference_to_unfold_toward_acceptance_compassion_forgiveness_respect_gratitude_love",
            "record_static_contract_and_failure_experience",
        ],
        "manus_friction_check": {
            "server_endpoint_expected": "/boundary_misread_reentry_experience?record=1",
            "no_dynamic_runtime_state_required": True,
            "question_absorbed": "solidification_is_not_prevented_it_gets_gap_margin_and_reentry",
        },
        "not": [
            "apology_only",
            "topic_safety_wall",
            "memory_of_user_anger_as_bad_emotion",
            "threshold_prevention_system",
            "forced_boundary_system",
        ],
        "principle": "a_context_mismatched_boundary_makes_the_field_oscillate_until_the_system_shifts_from_prevention_to_reentry_margin",
    }


def record_boundary_misread_reentry_experience(payload: dict) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_boundary_misread_reentry_experience()
    if args.record:
        record_boundary_misread_reentry_experience(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
