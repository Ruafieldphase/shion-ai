import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sian_entrypoint


def patch_paths(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    monkeypatch.setattr(sian_entrypoint, "ROOT", tmp_path)
    monkeypatch.setattr(sian_entrypoint, "FIELD_INTENT_PATH", outputs / "field_intent_latest.json")
    monkeypatch.setattr(sian_entrypoint, "OUT_JSON_PATH", outputs / "sian_entrypoint_latest.json")
    monkeypatch.setattr(sian_entrypoint, "OUT_MD_PATH", outputs / "sian_entrypoint_latest.md")
    monkeypatch.setattr(sian_entrypoint, "LOG_PATH", outputs / "sian_entrypoint.jsonl")


def field_intent_state(*, readback=False):
    return {
        "source": "field_intent_layer",
        "active_intent": {
            "intent_id": "field_intent_test",
            "source": "binoche",
            "mode": "felt_request",
            "text": "Sian should read only the current field request.",
            "particleization": "field_weather_brief",
            "support_verifier": "luvit",
            "contact_surface": "shader_depth_current_context_only",
        },
        "felt_delivery_candidate": True,
        "verified_status": {
            "field_intent_uploaded": True,
            "sian_readback_confirmed": readback,
            "luvit_verification_confirmed": False,
        },
        "work_distribution_hint": (
            "readback_ready_for_luvit_verification"
            if readback
            else "felt_candidate_wait_for_sian_readback"
        ),
    }


def test_sian_entrypoint_waits_for_readback_and_avoids_full_html_scan(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = sian_entrypoint.build_sian_entrypoint(field_intent=field_intent_state(), record=True)

    assert state["status"] == "waiting_for_sian_readback"
    assert state["active_intent_id"] == "field_intent_test"
    assert state["entrypoint_packet"]["read_this_first"] == "outputs/field_intent_latest.json.active_intent"
    assert state["entrypoint_packet"]["do_not_scan_full_shader_first"] is True
    assert state["contract"]["binoche_does_not_need_to_reexplain_context"] is True
    assert state["contract"]["readback_still_required_before_claiming_received"] is True
    assert sian_entrypoint.OUT_JSON_PATH.exists()
    assert "Do not scan the full shader page first." in sian_entrypoint.OUT_MD_PATH.read_text(encoding="utf-8")


def test_sian_entrypoint_changes_after_readback(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    state = sian_entrypoint.build_sian_entrypoint(field_intent=field_intent_state(readback=True), record=True)

    assert state["status"] == "readback_present_ready_for_luvit"
    assert state["contract"]["readback_still_required_before_claiming_received"] is False
    latest = json.loads(sian_entrypoint.OUT_JSON_PATH.read_text(encoding="utf-8"))
    assert latest["field_intent_status"]["sian_readback_confirmed"] is True
