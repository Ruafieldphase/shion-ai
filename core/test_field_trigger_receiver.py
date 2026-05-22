import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import field_trigger_receiver as receiver


def patch_paths(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    handoff = outputs / "antigravity_handoff"
    monkeypatch.setattr(receiver, "ROOT", tmp_path)
    monkeypatch.setattr(receiver, "OUTPUTS", outputs)
    monkeypatch.setattr(receiver, "HANDOFF_DIR", handoff)
    monkeypatch.setattr(receiver, "STATE_PATH", outputs / "field_trigger_receiver_state_latest.json")
    monkeypatch.setattr(receiver, "LOG_PATH", outputs / "field_trigger_receiver_events.jsonl")
    monkeypatch.setattr(receiver, "SIAN_TRIGGER_PATH", outputs / "sian_trigger_latest.json")
    monkeypatch.setattr(receiver, "LUVIT_TRIGGER_PATH", outputs / "luvit_trigger_latest.json")
    monkeypatch.setattr(receiver, "SIAN_ENTRYPOINT_PATH", outputs / "sian_entrypoint_latest.json")
    monkeypatch.setattr(receiver, "FIELD_INTENT_PATH", outputs / "field_intent_latest.json")
    monkeypatch.setattr(receiver, "FIELD_INTENT_READBACK_PATH", outputs / "field_intent_readback_latest.json")
    monkeypatch.setattr(receiver, "HANDOFF_INBOX_PATH", handoff / "inbox.jsonl")
    monkeypatch.setattr(receiver, "LUVIT_REVIEW_PATH", outputs / "luvit_trigger_review_latest.md")
    monkeypatch.setattr(receiver, "refresh_handoff_bridge", lambda: None)
    return outputs, handoff


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_sian_trigger_becomes_handoff_without_forced_process(monkeypatch, tmp_path):
    outputs, handoff = patch_paths(monkeypatch, tmp_path)
    write_json(
        outputs / "sian_entrypoint_latest.json",
        {
            "entrypoint_packet": {
                "current_request": {
                    "text": "시안은 현재 field intent를 읽고 readback을 남긴다.",
                }
            }
        },
    )
    write_json(outputs / "field_intent_latest.json", {"active_intent": {"intent_id": "intent-1"}})
    trigger = {
        "trigger_id": "sian_trigger_1",
        "node": "sian",
        "active_intent_id": "intent-1",
        "action": "read_current_field_intent_and_write_readback",
    }

    delivery = receiver.deliver_trigger(trigger, record=True)

    assert delivery["status"] == "delivered_to_sian_handoff_inbox"
    assert delivery["forced_process_launch"] is False
    lines = (handoff / "inbox.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    particle = json.loads(lines[0])
    assert particle["kind"] == "field_trigger_request"
    assert particle["contract"]["not_forced_execution"] is True
    assert "readback" in particle["body"].lower()


def test_same_trigger_is_not_delivered_twice(monkeypatch, tmp_path):
    outputs, handoff = patch_paths(monkeypatch, tmp_path)
    trigger = {"trigger_id": "sian_trigger_once", "node": "sian", "active_intent_id": "intent-1"}

    first = receiver.deliver_trigger(trigger, record=True)
    second = receiver.deliver_trigger(trigger, record=True)

    assert first["status"] == "delivered_to_sian_handoff_inbox"
    assert second["status"] == "already_delivered"
    lines = (handoff / "inbox.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_luvit_trigger_becomes_local_review_particle(monkeypatch, tmp_path):
    outputs, _handoff = patch_paths(monkeypatch, tmp_path)
    write_json(
        outputs / "field_intent_readback_latest.json",
        {"readback": {"confirmed": ["sian readback confirmed"]}},
    )
    trigger = {
        "trigger_id": "luvit_trigger_1",
        "node": "luvit",
        "active_intent_id": "intent-1",
        "action": "verify_sian_readback_and_prepare_slack_brief_candidate",
    }

    delivery = receiver.deliver_trigger(trigger, record=True)

    assert delivery["status"] == "delivered_to_luvit_review_particle"
    body = (outputs / "luvit_trigger_review_latest.md").read_text(encoding="utf-8")
    assert "sian readback confirmed" in body
    assert "does not send Slack by itself" in body
