import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import participant_frequency_field as field


def patch_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(field, "ROOT", tmp_path)
    monkeypatch.setattr(field, "OUT_PATH", tmp_path / "outputs" / "participant_frequency_field_latest.json")
    monkeypatch.setattr(field, "LOG_PATH", tmp_path / "outputs" / "participant_frequency_field.jsonl")
    monkeypatch.setattr(field, "LOCK_PATH", tmp_path / "outputs" / ".participant_frequency_field.lock")


def test_seed_state_is_not_live_upload(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = field.build_participant_frequency_field(record=True)

    assert state["uploaded_count"] == 0
    assert state["contract"]["seed_participants_are_not_proof_of_live_ai_upload"] is True
    assert state["contract"]["ethics_security_follow_natural_flow_not_external_wall"] is True
    assert state["natural_tuning"]["principle"].startswith("do_not_set_weights")
    assert state["contextual_inverse"]["opens"] == "current_context_action_slice_only"
    assert state["work_distribution_hint"] in {
        "hold_superposition_until_more_participants_upload",
        "threshold_crossed_read_candidate",
    }
    assert (tmp_path / "outputs" / "participant_frequency_field_latest.json").exists()


def test_upload_replaces_seed_and_creates_threshold_candidate(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    first = field.record_participant_frequency(
        {
            "participant_id": "luvit",
            "role": "implementation_verification_field",
            "phase": 0.20,
            "amplitude": 0.95,
            "current_pressure": 0.72,
            "field_confidence": 0.92,
            "task_affinity": "verify_shader_contract",
        }
    )
    second = field.record_participant_frequency(
        {
            "participant_id": "sian",
            "role": "wide_pattern_field",
            "phase": 0.22,
            "amplitude": 0.90,
            "current_pressure": 0.68,
            "field_confidence": 0.90,
            "task_affinity": "expand_pattern",
        }
    )

    assert first["ok"] is True
    assert second["field"]["uploaded_count"] == 2
    assert second["field"]["threshold_candidates"]
    assert second["field"]["next_particleization"]["participants"] == ["luvit", "sian"]
    assert second["field"]["next_particleization"]["contextual_inverse"] == "open_small_reversible_action"

    latest = json.loads((tmp_path / "outputs" / "participant_frequency_field_latest.json").read_text(encoding="utf-8"))
    assert latest["participants"][0]["participant_id"] == "binoche"


def test_reverse_flow_dampens_before_action(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = field.build_participant_frequency_field(
        [
            {
                "participant_id": "a",
                "phase": 0.0,
                "amplitude": 0.9,
                "current_pressure": 0.8,
                "context_fit": 0.18,
                "reverse_flow_pressure": 0.9,
                "field_confidence": 0.5,
            },
            {
                "participant_id": "b",
                "phase": 0.5,
                "amplitude": 0.9,
                "current_pressure": 0.8,
                "context_fit": 0.18,
                "reverse_flow_pressure": 0.9,
                "field_confidence": 0.5,
            },
        ]
    )

    assert state["reverse_flow_signals"]
    assert state["work_distribution_hint"] == "reverse_flow_should_dampen_before_action"
    assert state["contextual_inverse"]["current_output"] == "pause_refold_or_observe"
