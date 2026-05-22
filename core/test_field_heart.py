import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_heart import FieldHeart


def append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def test_field_heart_sends_receives_filters_and_unfolds_aqp4_prior(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    append_jsonl(
        outputs / "rhythm_node_trace.jsonl",
        {
            "selected_action": "ACTION_OBSERVE",
            "selected_label": "observe field",
            "geometry": {"curvature": 0.18},
            "bundle": [],
        },
    )

    heart = FieldHeart(tmp_path, echo_threshold=0.20)
    first = heart.beat(record=True)
    assert first["outbound_pulse"]["send_role"] == "circulate_without_commanding"

    (outputs / "aqp4_resonance_profile.json").write_text(
        json.dumps({"protein": "Human Aquaporin-4 (AQP4)", "uniprot_accession": "P55087"}),
        encoding="utf-8",
    )
    append_jsonl(
        outputs / "rhythm_node_trace.jsonl",
        {
            "selected_action": "ACTION_AXIOM_RELEASE",
            "selected_label": "axiom release",
            "geometry": {"curvature": 0.86},
            "natural_cycle": {"convergence": 0.74},
            "bundle": [
                {"role": "primary", "action": "ACTION_AXIOM_RELEASE"},
                {"role": "sideband", "action": "ACTION_REST_RECOVER"},
            ],
        },
    )
    append_jsonl(
        outputs / "ari_prism_trace.jsonl",
        {"directive": "release_internal_echo", "field": {"salience": 0.72}},
    )

    second = heart.beat(record=True)

    assert second["echo_delta"]["curvature_delta"] > 0.5
    assert "rest_sideband_must_not_become_user_rest_command" in second["filter"]["issues"]
    assert "protein_profile_is_prior_not_biological_law" in second["filter"]["issues"]
    assert second["unfolded"]["unfolded"] is True
    assert second["unfolded"]["unfolded_context"] == "protein_structure_dialogue_converged_into_aqp4_prism_prior"
    assert "biological_law" in second["unfolded"]["do_not_harden_as"]
    assert (outputs / "field_curvature_unfolded_latest.json").exists()


def test_field_heart_keeps_small_echo_as_unfolded_false(tmp_path):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    append_jsonl(
        outputs / "rhythm_node_trace.jsonl",
        {
            "selected_action": "ACTION_OBSERVE",
            "geometry": {"curvature": 0.05},
            "natural_cycle": {"convergence": 0.04},
        },
    )

    state = FieldHeart(tmp_path, echo_threshold=0.90).beat(record=False)

    assert state["unfolded"]["unfolded"] is False
    assert state["unfolded"]["reason"] == "echo_delta_below_threshold"
    assert state["contract"]["sends_carrier_pulse"] is True
