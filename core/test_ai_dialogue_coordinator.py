import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import ai_dialogue_coordinator as coordinator


def append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def patch_paths(monkeypatch, tmp_path):
    handoff = tmp_path / "handoff"
    monkeypatch.setattr(coordinator, "ROOT", tmp_path)
    monkeypatch.setattr(coordinator, "HANDOFF_DIR", handoff)
    monkeypatch.setattr(coordinator, "INBOX_PATH", handoff / "inbox.jsonl")
    monkeypatch.setattr(coordinator, "OUTBOX_PATH", handoff / "outbox.jsonl")
    monkeypatch.setattr(coordinator, "STATE_PATH", handoff / "dialogue_state_latest.json")
    monkeypatch.setattr(coordinator, "ESCALATION_PATH", handoff / "needs_binoche.md")
    monkeypatch.setattr(coordinator, "LUVIT_NEXT_PATH", handoff / "luvit_next_review.md")
    return handoff


def test_latest_unanswered_thread_waits_for_shion(monkeypatch, tmp_path):
    handoff = patch_paths(monkeypatch, tmp_path)
    append_jsonl(handoff / "inbox.jsonl", {"id": "old", "summary": "old task", "kind": "handoff"})
    append_jsonl(
        handoff / "outbox.jsonl",
        {"reply_to": "old", "summary": "old answer", "kind": "implementation_result"},
    )
    append_jsonl(handoff / "inbox.jsonl", {"id": "new", "summary": "new task", "kind": "implementation_request"})

    state = coordinator.refresh()

    assert state["next_actor"] == "shion"
    assert state["latest_open_thread"]["id"] == "new"
    assert state["counts"]["escalations"] == 0


def test_explicit_binoche_request_escalates(monkeypatch, tmp_path):
    handoff = patch_paths(monkeypatch, tmp_path)
    append_jsonl(handoff / "inbox.jsonl", {"id": "task", "summary": "task", "kind": "handoff"})
    append_jsonl(
        handoff / "outbox.jsonl",
        {
            "reply_to": "task",
            "summary": "비노체 판단 필요",
            "kind": "question",
            "body": "이 지점은 비노체 판단이 필요합니다.",
        },
    )

    state = coordinator.refresh()

    assert state["next_actor"] == "binoche"
    assert state["counts"]["escalations"] == 1
    assert "비노체 판단" in (handoff / "needs_binoche.md").read_text(encoding="utf-8")


def test_field_friction_question_stays_direct_dialogue(monkeypatch, tmp_path):
    handoff = patch_paths(monkeypatch, tmp_path)
    append_jsonl(handoff / "inbox.jsonl", {"id": "task", "summary": "task", "kind": "implementation_request"})
    append_jsonl(
        handoff / "outbox.jsonl",
        {
            "reply_to": "task",
            "summary": "why did this biological pattern arise",
            "kind": "field_friction_question",
            "body": "시안, 이 생물학적 연결은 어떤 느낌에서 나왔나요?",
        },
    )

    state = coordinator.refresh()

    assert state["next_actor"] == "luvit"
    assert state["latest_open_thread"]["dialectic_phase"] == "antithesis_question"
    assert state["contract"]["friction_becomes_direct_question_first"] is True
