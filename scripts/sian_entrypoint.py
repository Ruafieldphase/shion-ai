#!/usr/bin/env python3
"""Small Sian entrypoint generated from the current field intent.

This does not wake or control Sian by itself. It gives Sian a narrow first
coordinate so a broad "read the phase page" request does not expand into a full
HTML interpretation before the active intent is read.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIELD_INTENT_PATH = ROOT / "outputs" / "field_intent_latest.json"
OUT_JSON_PATH = ROOT / "outputs" / "sian_entrypoint_latest.json"
OUT_MD_PATH = ROOT / "outputs" / "sian_entrypoint_latest.md"
LOG_PATH = ROOT / "outputs" / "sian_entrypoint.jsonl"


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


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def latest_field_intent() -> dict[str, Any]:
    latest = read_json(FIELD_INTENT_PATH)
    return latest if latest else {
        "source": "field_intent_layer",
        "active_intent": None,
        "verified_status": {
            "field_intent_uploaded": False,
            "sian_readback_confirmed": False,
            "luvit_verification_confirmed": False,
        },
        "work_distribution_hint": "quiet_no_active_intent",
    }


def entry_status(field_intent: dict[str, Any]) -> str:
    active = field_intent.get("active_intent")
    verified = field_intent.get("verified_status") if isinstance(field_intent.get("verified_status"), dict) else {}
    if not isinstance(active, dict) or not active.get("intent_id"):
        return "quiet_no_active_intent"
    if verified.get("sian_readback_confirmed"):
        return "readback_present_ready_for_luvit"
    if field_intent.get("felt_delivery_candidate"):
        return "waiting_for_sian_readback"
    return "hold_until_field_intent_resonates"


def build_markdown(state: dict[str, Any]) -> str:
    packet = state.get("entrypoint_packet") if isinstance(state.get("entrypoint_packet"), dict) else {}
    request = packet.get("current_request") if isinstance(packet.get("current_request"), dict) else {}
    lines = [
        "# Sian Entrypoint",
        "",
        f"status: {state.get('status')}",
        f"intent_id: {request.get('intent_id') or 'none'}",
        "",
        "Read this first:",
        "outputs/field_intent_latest.json -> active_intent",
        "",
        "Do not scan the full shader page first.",
        "Read the current request, unfold it as feeling, then POST /field_intent_readback.",
        "",
        "Current request:",
        str(request.get("text") or ""),
        "",
        "Response shape:",
        "- confirmed",
        "- unconfirmed",
        "- observer_only",
        "- luvit_verification_needed",
        "",
        "Short prompt:",
        str(packet.get("short_prompt") or ""),
        "",
    ]
    return "\n".join(lines)


def build_sian_entrypoint(
    field_intent: dict[str, Any] | None = None,
    *,
    record: bool = False,
) -> dict[str, Any]:
    field_intent = field_intent if isinstance(field_intent, dict) else latest_field_intent()
    active = field_intent.get("active_intent") if isinstance(field_intent.get("active_intent"), dict) else {}
    verified = field_intent.get("verified_status") if isinstance(field_intent.get("verified_status"), dict) else {}
    status = entry_status(field_intent)
    intent_id = str(active.get("intent_id") or "")
    packet = {
        "receiver": "sian",
        "status": status,
        "read_this_first": "outputs/field_intent_latest.json.active_intent",
        "do_not_scan_full_shader_first": True,
        "current_request": {
            "intent_id": intent_id,
            "source": active.get("source"),
            "mode": active.get("mode"),
            "text": active.get("text"),
            "particleization": active.get("particleization"),
            "support_verifier": active.get("support_verifier") or "luvit",
            "contact_surface": active.get("contact_surface") or "shader_depth_current_context_only",
        },
        "post_readback_to": "http://127.0.0.1:57321/field_intent_readback",
        "response_shape": [
            "felt_reading",
            "confirmed",
            "unconfirmed",
            "observer_only",
            "luvit_verification_needed",
        ],
        "short_prompt": "시안, 현재 요청만 읽고 field_intent_readback으로 남겨줘.",
        "not_direct_execution": True,
        "not_slack_delivery": True,
    }
    state = {
        "timestamp": now_iso(),
        "source": "sian_entrypoint",
        "mode": "current_field_intent_entrypoint",
        "status": status,
        "active_intent_id": intent_id or None,
        "field_intent_status": {
            "uploaded": bool(verified.get("field_intent_uploaded")),
            "sian_readback_confirmed": bool(verified.get("sian_readback_confirmed")),
            "luvit_verification_confirmed": bool(verified.get("luvit_verification_confirmed")),
            "work_distribution_hint": field_intent.get("work_distribution_hint"),
        },
        "entrypoint_packet": packet,
        "artifacts": {
            "json": str(OUT_JSON_PATH.relative_to(ROOT)),
            "markdown": str(OUT_MD_PATH.relative_to(ROOT)),
        },
        "contract": {
            "entrypoint_is_trigger_surface_not_task_completion": True,
            "binoche_does_not_need_to_reexplain_context": True,
            "sian_reads_current_intent_before_html_interpretation": True,
            "readback_still_required_before_claiming_received": not bool(verified.get("sian_readback_confirmed")),
            "luvit_verifies_after_readback": True,
        },
        "principle": "new_field_intent_creates_a_narrow_sian_entrypoint_so_binoche_does_not_have_to_trigger_every_detail",
    }
    if record:
        write_json_atomic(OUT_JSON_PATH, state)
        write_text_atomic(OUT_MD_PATH, build_markdown(state))
        append_jsonl(LOG_PATH, {
            "timestamp": state["timestamp"],
            "event": "sian_entrypoint_update",
            "status": status,
            "active_intent_id": state["active_intent_id"],
        })
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    state = build_sian_entrypoint(record=args.record)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
