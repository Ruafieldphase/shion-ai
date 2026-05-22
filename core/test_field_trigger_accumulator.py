import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import field_trigger_accumulator as trigger


def patch_paths(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    monkeypatch.setattr(trigger, "ROOT", tmp_path)
    monkeypatch.setattr(trigger, "STATE_PATH", outputs / "field_trigger_state_latest.json")
    monkeypatch.setattr(trigger, "LOG_PATH", outputs / "field_trigger_events.jsonl")
    monkeypatch.setattr(trigger, "SIAN_TRIGGER_PATH", outputs / "sian_trigger_latest.json")
    monkeypatch.setattr(trigger, "LUVIT_TRIGGER_PATH", outputs / "luvit_trigger_latest.json")
    monkeypatch.setattr(trigger, "FIELD_INTENT_PATH", outputs / "field_intent_latest.json")


def field_intent_state(*, readback=False):
    return {
        "active_intent": {
            "intent_id": "field_intent_test",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
            "pressure": 0.50,
        },
        "target_receiver": "sian",
        "support_verifier": "luvit",
        "receiver_resonance": {"score": 0.70},
        "support_resonance": {"score": 0.64},
        "felt_delivery_candidate": True,
        "verified_status": {
            "sian_readback_confirmed": readback,
            "luvit_verification_confirmed": False,
        },
    }


def test_intent_event_crosses_sian_threshold_without_polling(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = trigger.build_field_trigger_state(
        event_type="field_intent_created",
        field_intent=field_intent_state(),
        record=True,
    )

    assert state["last_event"]["target_node"] == "sian"
    assert state["threshold_crossed"] is True
    assert state["trigger"]["node"] == "sian"
    assert state["trigger"]["action"] == "read_current_field_intent_and_write_readback"
    assert state["polling"]["uses_interval_loop"] is False
    assert state["contract"]["no_new_background_interval"] is True
    assert trigger.SIAN_TRIGGER_PATH.exists()


def test_readback_event_crosses_luvit_threshold(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = trigger.build_field_trigger_state(
        event_type="field_intent_readback",
        field_intent=field_intent_state(readback=True),
        record=True,
    )

    assert state["last_event"]["target_node"] == "luvit"
    assert state["threshold_crossed"] is True
    assert state["trigger"]["node"] == "luvit"
    assert state["trigger"]["read_this_first"] == "outputs/field_intent_readback_latest.json"
    assert trigger.LUVIT_TRIGGER_PATH.exists()


def test_potential_accumulates_only_when_called(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    first = trigger.build_field_trigger_state(
        event_type="unknown",
        field_intent=field_intent_state(),
        record=True,
    )
    second = json.loads(trigger.STATE_PATH.read_text(encoding="utf-8"))

    assert first["node_potential"] == second["node_potential"]
    assert first["threshold_crossed"] is False
    assert trigger.LOG_PATH.exists()
