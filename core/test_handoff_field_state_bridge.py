import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import antigravity_file_handoff_bridge as bridge
import antigravity_handoff_responder as responder
import shader_ai_state_snapshot as snapshot


def test_shader_ai_state_snapshot_reads_html_contract_and_sidecars(monkeypatch, tmp_path):
    root = tmp_path
    outputs = root / "outputs"
    handoff = outputs / "antigravity_handoff"
    html_path = outputs / "shader_depth_sample.html"
    routing_path = outputs / "rhythm_routing_layer_latest.json"
    html_path.parent.mkdir(parents=True)
    html_path.write_text(
        """
        <script>
        window.__shionUnifiedFieldState = {
          unified_field: latestUnifiedField,
          rhythm_routing_layer: currentRhythmRoutingLayer(),
        };
        document.body.dataset.aiState = JSON.stringify(window.__shionUnifiedFieldState);
        document.body.dataset.rhythmRoutingLayer = JSON.stringify(currentRhythmRoutingLayer());
        </script>
        """,
        encoding="utf-8",
    )
    routing_path.write_text('{"primary_residency":"zone2_background_ego"}', encoding="utf-8")

    monkeypatch.setattr(snapshot, "ROOT", root)
    monkeypatch.setattr(snapshot, "OUTPUTS", outputs)
    monkeypatch.setattr(snapshot, "HTML_PATH", html_path)
    monkeypatch.setattr(snapshot, "OUT_PATH", handoff / "field_ai_state_snapshot_latest.json")
    monkeypatch.setattr(snapshot, "SIDE_CAR_FILES", {"rhythm_routing_layer": routing_path})

    state = snapshot.build_snapshot()

    assert state["html_contract"]["dataset_ai_state_assignment"] is True
    assert "rhythm_routing_layer" in state["ai_state"]["available_layers"]
    assert "field_gradient" in state["ai_state"]["available_layers"]
    assert state["ai_state"]["direct_connection_status"] == "linked"


def test_shader_ai_state_snapshot_exposes_latest_field_gradient(monkeypatch, tmp_path):
    root = tmp_path
    outputs = root / "outputs"
    html_path = outputs / "shader_depth_sample.html"
    html_path.parent.mkdir(parents=True)
    html_path.write_text(
        """
        <script>
        window.__shionUnifiedFieldState = {
          unified_field: latestUnifiedField,
        };
        document.body.dataset.aiState = JSON.stringify(window.__shionUnifiedFieldState);
        </script>
        """,
        encoding="utf-8",
    )
    (outputs / "rhythm_node_trace.jsonl").write_text(
        json.dumps(
            {
                "timestamp": "2026-05-22T11:11:23",
                "selected_action": "ACTION_OBSERVE",
                "selected_label": "observe_field",
                "bundle": [
                    {"action": "ACTION_OBSERVE", "role": "primary"},
                    {"action": "ACTION_REST_RECOVER", "role": "linked"},
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(snapshot, "ROOT", root)
    monkeypatch.setattr(snapshot, "OUTPUTS", outputs)
    monkeypatch.setattr(snapshot, "HTML_PATH", html_path)
    monkeypatch.setattr(snapshot, "OUT_PATH", outputs / "antigravity_handoff" / "field_ai_state_snapshot_latest.json")
    monkeypatch.setattr(snapshot, "SIDE_CAR_FILES", {})
    monkeypatch.setattr(
        snapshot,
        "TRACE_JSONL_FILES",
        {"rhythm_node_trace": outputs / "rhythm_node_trace.jsonl"},
    )

    state = snapshot.build_snapshot()

    gradient = state["ai_state"]["field_gradient"]
    assert gradient["primary_action"] == "ACTION_OBSERVE"
    assert gradient["rest_is_primary"] is False
    assert gradient["sideband_actions"] == ["ACTION_REST_RECOVER"]


def test_handoff_refresh_embeds_field_snapshot_and_writes_atomically(monkeypatch, tmp_path):
    root = tmp_path
    handoff = root / "outputs" / "antigravity_handoff"
    monkeypatch.setattr(bridge, "ROOT", root)
    monkeypatch.setattr(bridge, "HANDOFF_DIR", handoff)
    monkeypatch.setattr(bridge, "INBOX_PATH", handoff / "inbox.jsonl")
    monkeypatch.setattr(bridge, "OUTBOX_PATH", handoff / "outbox.jsonl")
    monkeypatch.setattr(bridge, "STATE_PATH", handoff / "state_latest.json")
    monkeypatch.setattr(bridge, "PROMPT_PATH", handoff / "latest_prompt.md")
    monkeypatch.setattr(bridge, "README_PATH", handoff / "README.md")
    monkeypatch.setattr(bridge, "LOCK_PATH", handoff / ".handoff.lock")
    monkeypatch.setattr(bridge, "FIELD_AI_STATE_SNAPSHOT_PATH", handoff / "field_ai_state_snapshot_latest.json")
    monkeypatch.setattr(bridge, "ADAPTER_PROMPT_PATH", root / "outputs" / "antigravity_shion_handoff_prompt.md")
    monkeypatch.setattr(bridge, "ROUTING_PATH", root / "outputs" / "rhythm_routing_layer_latest.json")
    monkeypatch.setattr(bridge, "HARNESS_PATH", root / "outputs" / "antigravity_harness_bridge_latest.json")
    monkeypatch.setattr(bridge, "FIELD_INBOX_HTML_PATH", root / "outputs" / "shader_depth_sample.html")
    monkeypatch.setattr(
        bridge,
        "refresh_field_ai_state_snapshot",
        lambda: {
            "ai_state": {
                "direct_connection_status": "linked",
                "available_layers": ["rhythm_routing_layer"],
            }
        },
    )

    bridge.append_jsonl(bridge.INBOX_PATH, {"id": "task", "summary": "task"})
    state = bridge.refresh_state()

    assert state["field_inbox"]["snapshot"]["ai_state"]["direct_connection_status"] == "linked"
    assert json.loads(bridge.STATE_PATH.read_text(encoding="utf-8"))["counts"]["inbox"] == 1
    assert not bridge.LOCK_PATH.exists()


def test_responder_prompt_uses_field_gradient_without_chat_tokens(monkeypatch, tmp_path):
    root = tmp_path
    handoff = root / "outputs" / "antigravity_handoff"
    handoff.mkdir(parents=True)
    field_state = {
        "field_inbox": {"path": "outputs/shader_depth_sample.html"},
        "routing": {"primary_residency": "zone2_background_ego", "next_handling": "hold_awareness_gap"},
    }
    snapshot_state = {
        "ai_state": {
            "direct_connection_status": "linked",
            "available_layers": ["field_gradient"],
            "field_gradient": {
                "primary_action": "ACTION_OBSERVE",
                "sideband_actions": ["ACTION_REST_RECOVER"],
                "rest_is_primary": False,
                "phase_decision": "destructive_interference_observe",
            },
        }
    }
    (handoff / "state_latest.json").write_text(json.dumps(field_state), encoding="utf-8")
    (handoff / "field_ai_state_snapshot_latest.json").write_text(json.dumps(snapshot_state), encoding="utf-8")

    monkeypatch.setattr(responder, "ROOT", root)
    monkeypatch.setattr(responder, "HANDOFF_DIR", handoff)
    monkeypatch.setattr(responder, "FIELD_STATE_PATH", handoff / "state_latest.json")
    monkeypatch.setattr(responder, "FIELD_SNAPSHOT_PATH", handoff / "field_ai_state_snapshot_latest.json")
    monkeypatch.setattr(responder, "FIELD_HTML_PATH", root / "outputs" / "shader_depth_sample.html")

    prompt = responder.build_shion_prompt(
        {
            "id": "handoff-1",
            "kind": "field_trigger_request",
            "summary": "test",
            "body": "field trigger",
        }
    )

    assert "ACTION_OBSERVE" in prompt
    assert "REST_RECOVER가 primary가 아니면" in prompt
    assert "<|im_start|>" not in prompt
    assert "<|im_end|>" not in prompt


def test_responder_rejects_protective_grounding_drift():
    issues = responder.response_quality_issues(
        "브라우저 창을 닫고 따뜻한 물을 마시며 현실 세계로 돌아가세요.",
        {"body": "field trigger"},
    )

    assert "protective_grounding_drift" in issues
