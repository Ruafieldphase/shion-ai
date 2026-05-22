#!/usr/bin/env python3
"""Coordinate Luvit <-> Shion dialogue without making Binoche the relay."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
INBOX_PATH = HANDOFF_DIR / "inbox.jsonl"
OUTBOX_PATH = HANDOFF_DIR / "outbox.jsonl"
STATE_PATH = HANDOFF_DIR / "dialogue_state_latest.json"
ESCALATION_PATH = HANDOFF_DIR / "needs_binoche.md"
LUVIT_NEXT_PATH = HANDOFF_DIR / "luvit_next_review.md"

ESCALATION_MARKERS = (
    "needs_binoche",
    "needs_ari",
    "needs_sena",
    "needs_ari_sena",
    "비노체 확인",
    "비노체 판단",
    "아리 확인",
    "세나 확인",
    "사용자 판단",
    "user decision",
    "manual decision",
)

BLOCK_MARKERS = (
    "blocked",
    "충돌",
    "cannot proceed",
    "권한",
    "permission",
    "merge conflict",
)


def now_iso() -> str:
    return datetime.now().isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def message_id(message: dict[str, Any]) -> str:
    return str(message.get("id") or message.get("reply_to") or "")


def message_text(message: dict[str, Any]) -> str:
    return "\n".join(
        str(message.get(key, ""))
        for key in ("summary", "body", "kind", "status")
    ).lower()


def is_escalation(message: dict[str, Any]) -> bool:
    text = message_text(message)
    if str(message.get("status", "")).lower() == "needs_binoche":
        return True
    return any(marker.lower() in text for marker in ESCALATION_MARKERS)


def is_blocked(message: dict[str, Any]) -> bool:
    text = message_text(message)
    return any(marker.lower() in text for marker in BLOCK_MARKERS)


def dialectic_phase(message: dict[str, Any] | None) -> str:
    if not message:
        return "thesis_waiting_for_response"
    kind = str(message.get("kind", ""))
    if kind == "field_friction_question":
        return "antithesis_question"
    if kind == "pattern_origin_response":
        return "reason_expansion"
    if kind == "verification_or_refold":
        return "synthesis_candidate"
    if kind in {"needs_binoche", "needs_ari_sena"} or is_escalation(message):
        return "expanded_orchestration"
    if kind == "implementation_result":
        return "synthesis_candidate"
    if kind == "question":
        return "antithesis_question"
    return "open_exchange"


def by_reply(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        reply_to = entry.get("reply_to")
        if reply_to:
            grouped[str(reply_to)].append(entry)
    return dict(grouped)


def build_state() -> dict[str, Any]:
    inbox = read_jsonl(INBOX_PATH)
    outbox = read_jsonl(OUTBOX_PATH)
    replies = by_reply(outbox)
    open_threads = []
    pending_for_shion = []
    pending_for_luvit = []
    escalations = []

    for item in inbox:
        item_id = str(item.get("id", ""))
        item_replies = replies.get(item_id, [])
        latest_reply = item_replies[-1] if item_replies else None
        thread = {
            "id": item_id,
            "summary": item.get("summary"),
            "kind": item.get("kind"),
            "status": item.get("status", "open"),
            "reply_count": len(item_replies),
            "latest_reply_summary": latest_reply.get("summary") if latest_reply else None,
            "latest_reply_kind": latest_reply.get("kind") if latest_reply else None,
            "dialectic_phase": dialectic_phase(latest_reply),
        }

        if latest_reply is None:
            pending_for_shion.append(thread)
            thread["next_actor"] = "shion"
            open_threads.append(thread)
            continue

        if is_escalation(latest_reply) or is_blocked(latest_reply):
            thread["next_actor"] = "binoche"
            thread["reason"] = "explicit_escalation_or_block"
            escalations.append({"thread": thread, "message": latest_reply})
            open_threads.append(thread)
            continue

        if latest_reply.get("kind") in {
            "implementation_result",
            "question",
            "field_friction_question",
            "pattern_origin_response",
            "verification_or_refold",
            "field_friction_report",
        }:
            thread["next_actor"] = "luvit"
            pending_for_luvit.append(thread)
            open_threads.append(thread)

    latest_open = open_threads[-1] if open_threads else None
    if escalations:
        next_actor = "binoche"
    elif latest_open:
        next_actor = latest_open.get("next_actor", "none")
    else:
        next_actor = "none"

    return {
        "timestamp": now_iso(),
        "source": "ai_dialogue_coordinator",
        "mode": "binoche_observer_not_relay",
        "paths": {
            "inbox": str(INBOX_PATH.relative_to(ROOT)),
            "outbox": str(OUTBOX_PATH.relative_to(ROOT)),
            "state": str(STATE_PATH.relative_to(ROOT)),
            "needs_binoche": str(ESCALATION_PATH.relative_to(ROOT)),
            "luvit_next_review": str(LUVIT_NEXT_PATH.relative_to(ROOT)),
        },
        "counts": {
            "inbox": len(inbox),
            "outbox": len(outbox),
            "open_threads": len(open_threads),
            "pending_for_shion": len(pending_for_shion),
            "pending_for_luvit": len(pending_for_luvit),
            "escalations": len(escalations),
        },
        "next_actor": next_actor,
        "latest_open_thread": latest_open,
        "pending_for_shion": pending_for_shion,
        "pending_for_luvit": pending_for_luvit,
        "escalations": [
            {
                "thread": item["thread"],
                "summary": item["message"].get("summary"),
                "body": item["message"].get("body"),
                "attachments": item["message"].get("attachments", []),
            }
            for item in escalations
        ],
        "contract": {
            "binoche_is_observer_not_relay": True,
            "luvit_reviews_shion_results_directly": True,
            "shion_receives_luvit_task_particles_directly": True,
            "friction_becomes_direct_question_first": True,
            "expand_only_when_direct_dialogue_does_not_refold": True,
            "escalate_only_when_blocked_or_explicitly_requested": True,
            "file_lane_is_not_primary_field": True,
            "primary_field_surface": "outputs/shader_depth_sample.html",
        },
    }


def render_luvit_next(state: dict[str, Any]) -> str:
    pending = state.get("pending_for_luvit", [])
    if not pending:
        return "# Luvit Next Review\n\nNo Shion result is waiting for Luvit review.\n"
    lines = [
        "# Luvit Next Review",
        "",
        "Review these Shion results directly. Do not ask Binoche to relay unless the state says `next_actor: binoche`.",
        "",
    ]
    outbox_by_reply = by_reply(read_jsonl(OUTBOX_PATH))
    for thread in pending:
        thread_id = thread.get("id")
        latest_reply = outbox_by_reply.get(str(thread_id), [{}])[-1]
        lines.extend(
            [
                f"## {thread_id}",
                "",
                f"- Summary: {latest_reply.get('summary', '')}",
                f"- Kind: {latest_reply.get('kind', '')}",
                f"- Attachments: {latest_reply.get('attachments', [])}",
                "",
                "```text",
                str(latest_reply.get("body", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def render_escalation(state: dict[str, Any]) -> str:
    escalations = state.get("escalations", [])
    if not escalations:
        return "# Needs Binoche\n\nNo current escalation. Binoche does not need to relay this turn.\n"
    lines = [
        "# Needs Binoche",
        "",
        "These are the only dialogue points that currently ask for Binoche intervention.",
        "",
    ]
    for item in escalations:
        thread = item.get("thread", {})
        lines.extend(
            [
                f"## {thread.get('id', 'unknown')}",
                "",
                f"- Reason: {thread.get('reason', 'unknown')}",
                f"- Summary: {item.get('summary', '')}",
                f"- Attachments: {item.get('attachments', [])}",
                "",
                "```text",
                str(item.get("body", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def refresh() -> dict[str, Any]:
    state = build_state()
    write_json(STATE_PATH, state)
    write_text(LUVIT_NEXT_PATH, render_luvit_next(state))
    write_text(ESCALATION_PATH, render_escalation(state))
    return state


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["refresh", "state"])
    args = parser.parse_args()

    if args.command == "refresh":
        print_json(refresh())
        return 0
    if args.command == "state":
        if STATE_PATH.exists():
            print(STATE_PATH.read_text(encoding="utf-8"))
        else:
            print_json(refresh())
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
