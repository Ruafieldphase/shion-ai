import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import field_intent_layer as field_intent


def patch_paths(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    monkeypatch.setattr(field_intent, "ROOT", tmp_path)
    monkeypatch.setattr(field_intent, "OUT_PATH", outputs / "field_intent_latest.json")
    monkeypatch.setattr(field_intent, "LOG_PATH", outputs / "field_intent.jsonl")
    monkeypatch.setattr(field_intent, "READBACK_PATH", outputs / "field_intent_readback_latest.json")
    monkeypatch.setattr(field_intent, "READBACK_LOG_PATH", outputs / "field_intent_readback.jsonl")
    monkeypatch.setattr(field_intent, "LOCK_PATH", outputs / ".field_intent.lock")
    monkeypatch.setattr(field_intent, "PARTICIPANT_FIELD_PATH", outputs / "participant_frequency_field_latest.json")


def participant_field():
    return {
        "source": "participant_frequency_field",
        "natural_tuning": {"posture": "threshold_can_particleize"},
        "uploaded_count": 1,
        "participants": [
            {
                "participant_id": "sian",
                "amplitude": 0.72,
                "context_fit": 0.76,
                "field_confidence": 0.74,
            },
            {
                "participant_id": "luvit",
                "amplitude": 0.64,
                "context_fit": 0.68,
                "field_confidence": 0.82,
            },
        ],
    }


def test_felt_weather_intent_routes_to_sian_with_luvit_support(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    intent = {
        "source": "binoche",
        "text": "시안이 느낌으로 받아서 Slack field weather brief를 만들고 확인됨과 미확인을 분리해줘. 루빛은 검증만 해줘.",
        "desired_receiver": "sian",
        "support_verifier": "luvit",
        "particleization": "field_weather_brief",
    }

    state = field_intent.build_field_intent_field(
        participant_field=participant_field(),
        intent=intent,
        record=True,
    )

    assert state["target_receiver"] == "sian"
    assert state["support_verifier"] == "luvit"
    assert state["felt_delivery_candidate"] is True
    assert state["next_particleization"]["route"] == "sian:felt_translation+luvit:support_verification"
    assert state["contract"]["intent_enters_field_before_task_lane"] is True
    assert state["contract"]["sian_receives_as_feeling_not_direct_order"] is True
    assert state["contract"]["binoche_stays_observer_not_relay"] is True
    assert state["verified_status"]["sian_readback_confirmed"] is False
    assert state["verified_status"]["basis"] == "field_state_candidate_only_not_agent_readback"


def test_record_field_intent_persists_latest_without_claiming_readback(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    field_intent.PARTICIPANT_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
    field_intent.PARTICIPANT_FIELD_PATH.write_text(
        json.dumps(participant_field(), ensure_ascii=False),
        encoding="utf-8",
    )

    result = field_intent.record_field_intent(
        {
            "source": "binoche",
            "text": "느낌 요청을 시안에게 장으로 업로드하고 루빛은 검증한다.",
        }
    )

    assert result["ok"] is True
    latest = json.loads(field_intent.OUT_PATH.read_text(encoding="utf-8"))
    assert latest["active_intent"]["source"] == "binoche"
    assert latest["target_receiver"] == "sian"
    assert latest["verified_status"]["sian_readback_confirmed"] is False
    assert field_intent.LOG_PATH.exists()


def test_matching_sian_readback_confirms_receiver_contact_only(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    field_intent.PARTICIPANT_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
    field_intent.PARTICIPANT_FIELD_PATH.write_text(
        json.dumps(participant_field(), ensure_ascii=False),
        encoding="utf-8",
    )
    upload = field_intent.record_field_intent(
        {
            "source": "binoche",
            "text": "시안이 느낌으로 Slack field weather를 풀고 루빛은 검증한다.",
            "desired_receiver": "sian",
            "support_verifier": "luvit",
            "particleization": "field_weather_brief",
        }
    )

    readback = field_intent.record_field_intent_readback(
        {
            "intent_id": upload["intent"]["intent_id"],
            "receiver": "sian",
            "felt_reading": "장의 날씨는 얇은 Slack 브리프로 접힐 수 있다.",
            "confirmed": ["field intent is present", "receiver is sian"],
            "unconfirmed": ["Slack delivery not sent"],
            "observer_only": ["Binoche watches weather, not code details"],
            "luvit_verification_needed": ["separate confirmed/unconfirmed"],
        }
    )

    assert readback["matches_active_intent"] is True
    assert readback["field"]["verified_status"]["sian_readback_confirmed"] is True
    assert readback["field"]["verified_status"]["luvit_verification_confirmed"] is False
    assert readback["field"]["verified_status"]["basis"] == "receiver_readback_matches_active_intent"
    assert readback["field"]["receiver_readback"]["receiver"] == "sian"
    assert readback["field"]["next_particleization"]["route"] == "luvit:verify_readback+slack_brief_particle"


def test_mismatched_readback_does_not_confirm_active_intent(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)
    field_intent.PARTICIPANT_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
    field_intent.PARTICIPANT_FIELD_PATH.write_text(
        json.dumps(participant_field(), ensure_ascii=False),
        encoding="utf-8",
    )
    field_intent.record_field_intent(
        {
            "source": "binoche",
            "text": "시안 readback 후보",
            "desired_receiver": "sian",
        }
    )

    readback = field_intent.record_field_intent_readback(
        {
            "intent_id": "different_intent",
            "receiver": "sian",
            "felt_reading": "old readback",
        }
    )

    assert readback["matches_active_intent"] is False
    assert readback["field"]["verified_status"]["sian_readback_confirmed"] is False
