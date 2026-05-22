import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import scripts.field_intent_layer as field_intent
import scripts.field_trigger_accumulator as field_trigger
import scripts.field_trigger_receiver as field_receiver
import scripts.participant_frequency_field as frequency
import scripts.sian_entrypoint as sian_entrypoint
import shader_feedback_server as server


def patch_paths(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    participant_path = outputs / "participant_frequency_field_latest.json"
    field_intent_path = outputs / "field_intent_latest.json"
    sian_entrypoint_path = outputs / "sian_entrypoint_latest.json"
    field_trigger_path = outputs / "field_trigger_state_latest.json"
    handoff = outputs / "antigravity_handoff"
    monkeypatch.setattr(frequency, "ROOT", tmp_path)
    monkeypatch.setattr(frequency, "OUT_PATH", participant_path)
    monkeypatch.setattr(frequency, "LOG_PATH", outputs / "participant_frequency_field.jsonl")
    monkeypatch.setattr(frequency, "LOCK_PATH", outputs / ".participant_frequency_field.lock")
    monkeypatch.setattr(field_intent, "ROOT", tmp_path)
    monkeypatch.setattr(field_intent, "OUT_PATH", field_intent_path)
    monkeypatch.setattr(field_intent, "LOG_PATH", outputs / "field_intent.jsonl")
    monkeypatch.setattr(field_intent, "READBACK_PATH", outputs / "field_intent_readback_latest.json")
    monkeypatch.setattr(field_intent, "READBACK_LOG_PATH", outputs / "field_intent_readback.jsonl")
    monkeypatch.setattr(field_intent, "LOCK_PATH", outputs / ".field_intent.lock")
    monkeypatch.setattr(field_intent, "PARTICIPANT_FIELD_PATH", participant_path)
    monkeypatch.setattr(field_trigger, "ROOT", tmp_path)
    monkeypatch.setattr(field_trigger, "STATE_PATH", field_trigger_path)
    monkeypatch.setattr(field_trigger, "LOG_PATH", outputs / "field_trigger_events.jsonl")
    monkeypatch.setattr(field_trigger, "SIAN_TRIGGER_PATH", outputs / "sian_trigger_latest.json")
    monkeypatch.setattr(field_trigger, "LUVIT_TRIGGER_PATH", outputs / "luvit_trigger_latest.json")
    monkeypatch.setattr(field_trigger, "FIELD_INTENT_PATH", field_intent_path)
    monkeypatch.setattr(field_receiver, "ROOT", tmp_path)
    monkeypatch.setattr(field_receiver, "OUTPUTS", outputs)
    monkeypatch.setattr(field_receiver, "HANDOFF_DIR", handoff)
    monkeypatch.setattr(field_receiver, "STATE_PATH", outputs / "field_trigger_receiver_state_latest.json")
    monkeypatch.setattr(field_receiver, "LOG_PATH", outputs / "field_trigger_receiver_events.jsonl")
    monkeypatch.setattr(field_receiver, "SIAN_TRIGGER_PATH", outputs / "sian_trigger_latest.json")
    monkeypatch.setattr(field_receiver, "LUVIT_TRIGGER_PATH", outputs / "luvit_trigger_latest.json")
    monkeypatch.setattr(field_receiver, "SIAN_ENTRYPOINT_PATH", sian_entrypoint_path)
    monkeypatch.setattr(field_receiver, "FIELD_INTENT_PATH", field_intent_path)
    monkeypatch.setattr(field_receiver, "FIELD_INTENT_READBACK_PATH", outputs / "field_intent_readback_latest.json")
    monkeypatch.setattr(field_receiver, "HANDOFF_INBOX_PATH", handoff / "inbox.jsonl")
    monkeypatch.setattr(field_receiver, "LUVIT_REVIEW_PATH", outputs / "luvit_trigger_review_latest.md")
    monkeypatch.setattr(field_receiver, "refresh_handoff_bridge", lambda: None)
    monkeypatch.setattr(sian_entrypoint, "ROOT", tmp_path)
    monkeypatch.setattr(sian_entrypoint, "FIELD_INTENT_PATH", field_intent_path)
    monkeypatch.setattr(sian_entrypoint, "OUT_JSON_PATH", sian_entrypoint_path)
    monkeypatch.setattr(sian_entrypoint, "OUT_MD_PATH", outputs / "sian_entrypoint_latest.md")
    monkeypatch.setattr(sian_entrypoint, "LOG_PATH", outputs / "sian_entrypoint.jsonl")
    monkeypatch.setattr(server, "PARTICIPANT_FREQUENCY_FIELD_PATH", participant_path)
    monkeypatch.setattr(server, "FIELD_INTENT_FIELD_PATH", field_intent_path)
    monkeypatch.setattr(server, "SIAN_ENTRYPOINT_PATH", sian_entrypoint_path)
    monkeypatch.setattr(server, "FIELD_TRIGGER_STATE_PATH", field_trigger_path)
    monkeypatch.setattr(server, "FIELD_TRIGGER_RECEIVER_STATE_PATH", outputs / "field_trigger_receiver_state_latest.json")
    participant_path.parent.mkdir(parents=True, exist_ok=True)
    participant_path.write_text(
        json.dumps(
            {
                "source": "participant_frequency_field",
                "natural_tuning": {"posture": "threshold_can_particleize"},
                "participants": [
                    {
                        "participant_id": "sian",
                        "amplitude": 0.75,
                        "context_fit": 0.72,
                        "field_confidence": 0.76,
                    },
                    {
                        "participant_id": "luvit",
                        "amplitude": 0.68,
                        "context_fit": 0.70,
                        "field_confidence": 0.84,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_server_records_field_intent_payload(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    result = server.record_field_intent_payload(
        {
            "source": "binoche",
            "text": "시안이 느낌으로 Slack field weather를 받고 루빛은 검증한다.",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
        }
    )

    assert result["ok"] is True
    assert result["field"]["target_receiver"] == "sian"
    assert result["sian_entrypoint"]["ok"] is True
    assert result["sian_entrypoint"]["entrypoint"]["status"] == "waiting_for_sian_readback"
    assert result["field_trigger"]["ok"] is True
    assert result["field_trigger"]["state"]["last_event"]["target_node"] == "sian"
    assert result["field_trigger"]["receiver_delivery"]["status"] == "delivered_to_sian_handoff_inbox"
    assert result["field"]["verified_status"]["sian_readback_confirmed"] is False
    synthesized = server.synthesize_field_intent_field()
    assert synthesized["active_intent"]["source"] == "binoche"
    assert synthesized["contract"]["intent_enters_field_before_task_lane"] is True


def test_server_records_field_intent_readback_payload(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    upload = server.record_field_intent_payload(
        {
            "source": "binoche",
            "text": "Sian receives the field weather feeling and Luvit verifies.",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
        }
    )

    result = server.record_field_intent_readback_payload(
        {
            "intent_id": upload["intent"]["intent_id"],
            "receiver": "sian",
            "felt_reading": "Field weather brief can be unfolded.",
            "confirmed": ["intent is present"],
            "unconfirmed": ["Slack not sent"],
            "luvit_verification_needed": ["verify brief separation"],
        }
    )

    assert result["ok"] is True
    assert result["matches_active_intent"] is True
    assert result["sian_entrypoint"]["entrypoint"]["status"] == "readback_present_ready_for_luvit"
    assert result["field_trigger"]["state"]["last_event"]["target_node"] == "luvit"
    assert result["field_trigger"]["state"]["threshold_crossed"] is True
    assert result["field_trigger"]["receiver_delivery"]["status"] == "delivered_to_luvit_review_particle"
    assert result["field"]["verified_status"]["sian_readback_confirmed"] is True
    assert result["field"]["verified_status"]["luvit_verification_confirmed"] is False


def test_server_synthesizes_sian_entrypoint(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    server.record_field_intent_payload(
            {
                "source": "binoche",
                "text": "Sian receives the field weather feeling and Slack brief request.",
                "desired_receiver": "sian",
                "support_verifier": "luvit",
            }
    )

    entrypoint = server.synthesize_sian_entrypoint()

    assert entrypoint["status"] == "waiting_for_sian_readback"
    assert entrypoint["entrypoint_packet"]["do_not_scan_full_shader_first"] is True
    assert entrypoint["contract"]["sian_reads_current_intent_before_html_interpretation"] is True


def test_server_exposes_field_trigger_state(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    server.record_field_intent_payload(
        {
            "source": "binoche",
            "text": "Sian receives the field weather feeling and Slack brief request.",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
        }
    )

    state = server.synthesize_field_trigger_state()

    assert state["mode"] == "event_driven_difference_to_node_trigger"
    assert state["polling"]["uses_interval_loop"] is False
    assert state["last_event"]["target_node"] == "sian"


def test_server_exposes_field_trigger_receiver_state(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    server.record_field_intent_payload(
        {
            "source": "binoche",
            "text": "Sian receives the field weather feeling and Slack brief request.",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
        }
    )

    state = server.synthesize_field_trigger_receiver_state()

    assert state["mode"] == "event_driven_trigger_delivery"
    assert state["contract"]["does_not_force_start_sian"] is True
    assert state["last_delivery"]["status"] == "delivered_to_sian_handoff_inbox"
