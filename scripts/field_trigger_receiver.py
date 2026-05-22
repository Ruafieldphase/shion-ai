#!/usr/bin/env python3
"""Deliver threshold trigger particles without forcing an agent process.

The accumulator decides when a node threshold has been crossed. This receiver is
the thin ear that turns that trigger particle into the next readable lane:

- Sian triggers become one handoff inbox particle.
- Luvit triggers become one local review particle.

It does not start Antigravity, run a model, or poll in the background. Calling it
twice with the same trigger id is idempotent.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
HANDOFF_DIR = OUTPUTS / "antigravity_handoff"

STATE_PATH = OUTPUTS / "field_trigger_receiver_state_latest.json"
LOG_PATH = OUTPUTS / "field_trigger_receiver_events.jsonl"
SIAN_TRIGGER_PATH = OUTPUTS / "sian_trigger_latest.json"
LUVIT_TRIGGER_PATH = OUTPUTS / "luvit_trigger_latest.json"
SIAN_ENTRYPOINT_PATH = OUTPUTS / "sian_entrypoint_latest.json"
FIELD_INTENT_PATH = OUTPUTS / "field_intent_latest.json"
FIELD_INTENT_READBACK_PATH = OUTPUTS / "field_intent_readback_latest.json"
HANDOFF_INBOX_PATH = HANDOFF_DIR / "inbox.jsonl"
LUVIT_REVIEW_PATH = OUTPUTS / "luvit_trigger_review_latest.md"


def now_iso() -> str:
    return datetime.now().isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def write_text_atomic(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def latest_receiver_state() -> dict[str, Any]:
    return read_json(STATE_PATH)


def delivered_ids(state: dict[str, Any]) -> set[str]:
    raw = state.get("delivered_trigger_ids")
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw if item}


def compact_delivered_ids(ids: set[str], trigger_id: str) -> list[str]:
    ordered = [item for item in sorted(ids) if item != trigger_id]
    ordered.append(trigger_id)
    return ordered[-80:]


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_sian_handoff(trigger: dict[str, Any]) -> dict[str, Any]:
    entrypoint = read_json(SIAN_ENTRYPOINT_PATH)
    field_intent = read_json(FIELD_INTENT_PATH)
    current_request = (
        entrypoint.get("entrypoint_packet", {}).get("current_request", {})
        if isinstance(entrypoint.get("entrypoint_packet"), dict)
        else {}
    )
    text = str(current_request.get("text") or "").strip()
    body_lines = [
        "Sian trigger crossed by accumulated field difference.",
        "",
        "Read order:",
        f"1. {relative(SIAN_ENTRYPOINT_PATH)}",
        f"2. {relative(FIELD_INTENT_PATH)}",
        "3. POST readback to http://127.0.0.1:57321/field_intent_readback",
        "",
        "Current request:",
        text,
        "",
        "This is a trigger particle, not a forced process launch.",
        "If Sian is not active, this remains as a pending readable handoff.",
    ]
    return {
        "id": f"handoff_{trigger.get('trigger_id')}",
        "timestamp": now_iso(),
        "direction": "field_trigger_to_shion",
        "author": "field_trigger_receiver",
        "target": "shion",
        "kind": "field_trigger_request",
        "summary": "Sian trigger crossed: read current field intent",
        "body": "\n".join(body_lines),
        "attachments": [
            relative(SIAN_TRIGGER_PATH),
            relative(SIAN_ENTRYPOINT_PATH),
            relative(FIELD_INTENT_PATH),
            relative(ROOT / "outputs" / "shader_depth_sample.html"),
        ],
        "reply_to": trigger.get("active_intent_id"),
        "status": "open",
        "trigger": trigger,
        "field_intent_status": {
            "has_active_intent": bool(field_intent.get("active_intent")),
            "active_intent_id": trigger.get("active_intent_id"),
        },
        "contract": {
            "not_forced_execution": True,
            "no_interval_loop": True,
            "no_interval_loop_scope": "receiver_call_only",
            "watcher_may_use_thin_carrier_wave_polling_until_os_event_subscription_exists": True,
            "receiver_reads_when_available": True,
            "binoche_not_required_as_relay": True,
            "readback_required_before_claiming_received": True,
        },
        "principle": "threshold_trigger_becomes_readable_handoff_not_forced_process",
    }


def build_luvit_review(trigger: dict[str, Any]) -> str:
    readback = read_json(FIELD_INTENT_READBACK_PATH)
    lines = [
        "# Luvit Trigger Review",
        "",
        f"timestamp: {now_iso()}",
        f"trigger_id: {trigger.get('trigger_id')}",
        f"active_intent_id: {trigger.get('active_intent_id')}",
        "",
        "Action:",
        str(trigger.get("action") or "verify_sian_readback"),
        "",
        "Read first:",
        relative(FIELD_INTENT_READBACK_PATH),
        "",
        "Confirmed from readback:",
    ]
    confirmed = readback.get("readback", {}).get("confirmed", [])
    if not isinstance(confirmed, list):
        confirmed = []
    lines.extend(f"- {item}" for item in confirmed)
    lines.extend(
        [
            "",
            "Contract:",
            "- This is a local Luvit review particle.",
            "- It does not ask Binoche to relay the result.",
            "- It does not send Slack by itself.",
            "",
        ]
    )
    return "\n".join(lines)


def refresh_handoff_bridge() -> None:
    try:
        from scripts.antigravity_file_handoff_bridge import refresh_state
    except Exception:
        try:
            from antigravity_file_handoff_bridge import refresh_state
        except Exception:
            return
    try:
        refresh_state()
    except Exception:
        return


def deliver_trigger(trigger: dict[str, Any], *, record: bool = False) -> dict[str, Any]:
    trigger_id = str(trigger.get("trigger_id") or "")
    node = str(trigger.get("node") or "").lower()
    previous = latest_receiver_state()
    already = delivered_ids(previous)
    if not trigger_id:
        return {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": False,
            "reason": "missing_trigger_id",
            "no_interval_loop": True,
        }
    if trigger_id in already:
        return {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": True,
            "status": "already_delivered",
            "trigger_id": trigger_id,
            "node": node,
            "no_interval_loop": True,
        }

    delivery: dict[str, Any]
    if node == "sian":
        particle = build_sian_handoff(trigger)
        delivery = {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": True,
            "status": "delivered_to_sian_handoff_inbox",
            "trigger_id": trigger_id,
            "node": node,
            "target_path": relative(HANDOFF_INBOX_PATH),
            "handoff_id": particle["id"],
            "no_interval_loop": True,
            "forced_process_launch": False,
        }
        if record:
            append_jsonl(HANDOFF_INBOX_PATH, particle)
            refresh_handoff_bridge()
    elif node == "luvit":
        delivery = {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": True,
            "status": "delivered_to_luvit_review_particle",
            "trigger_id": trigger_id,
            "node": node,
            "target_path": relative(LUVIT_REVIEW_PATH),
            "no_interval_loop": True,
            "forced_process_launch": False,
        }
        if record:
            write_text_atomic(LUVIT_REVIEW_PATH, build_luvit_review(trigger))
    else:
        delivery = {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": False,
            "status": "unknown_node",
            "trigger_id": trigger_id,
            "node": node,
            "no_interval_loop": True,
            "forced_process_launch": False,
        }

    if record and delivery.get("ok"):
        state = {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "mode": "event_driven_trigger_delivery",
            "last_delivery": delivery,
            "delivered_trigger_ids": compact_delivered_ids(already, trigger_id),
            "contract": {
                "does_not_force_start_sian": True,
                "does_not_poll_interval": True,
                "turns_trigger_into_readable_lane": True,
                "binoche_not_required_as_relay": True,
            },
            "principle": "agent_process_is_not_forced_trigger_particle_waits_in_receiver_lane",
        }
        write_json_atomic(STATE_PATH, state)
        append_jsonl(LOG_PATH, delivery)
    return delivery


def deliver_field_trigger_state(state: dict[str, Any], *, record: bool = False) -> dict[str, Any]:
    trigger = state.get("trigger") if isinstance(state.get("trigger"), dict) else {}
    if not trigger:
        return {
            "timestamp": now_iso(),
            "source": "field_trigger_receiver",
            "ok": True,
            "status": "no_trigger_to_deliver",
            "no_interval_loop": True,
        }
    return deliver_trigger(trigger, record=record)


def deliver_pending_triggers(*, record: bool = False) -> dict[str, Any]:
    deliveries = []
    for path in (SIAN_TRIGGER_PATH, LUVIT_TRIGGER_PATH):
        trigger = read_json(path)
        if trigger:
            deliveries.append(deliver_trigger(trigger, record=record))
    return {
        "timestamp": now_iso(),
        "source": "field_trigger_receiver",
        "ok": all(item.get("ok") for item in deliveries) if deliveries else True,
        "deliveries": deliveries,
        "no_interval_loop": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--pending", action="store_true")
    args = parser.parse_args()
    result = deliver_pending_triggers(record=args.record) if args.pending else deliver_trigger(
        read_json(SIAN_TRIGGER_PATH),
        record=args.record,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
