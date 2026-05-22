#!/usr/bin/env python3
"""Event-driven trigger potential accumulator.

This layer does not poll. It is called only when a field event is written, such
as a new field intent or a matching readback. Small differences accumulate into
node potential; crossing a threshold writes a trigger particle for the relevant
node.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "outputs" / "field_trigger_state_latest.json"
LOG_PATH = ROOT / "outputs" / "field_trigger_events.jsonl"
SIAN_TRIGGER_PATH = ROOT / "outputs" / "sian_trigger_latest.json"
LUVIT_TRIGGER_PATH = ROOT / "outputs" / "luvit_trigger_latest.json"
FIELD_INTENT_PATH = ROOT / "outputs" / "field_intent_latest.json"

THRESHOLDS = {
    "sian": 0.72,
    "luvit": 0.68,
}
EVENT_DECAY = 0.72


def now_iso() -> str:
    return datetime.now().isoformat()


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


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


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def latest_field_intent() -> dict[str, Any]:
    return read_json(FIELD_INTENT_PATH)


def latest_trigger_state() -> dict[str, Any]:
    return read_json(STATE_PATH)


def current_potentials(previous: dict[str, Any]) -> dict[str, float]:
    raw = previous.get("node_potential") if isinstance(previous.get("node_potential"), dict) else {}
    return {
        "sian": clamp01(raw.get("sian"), 0.0),
        "luvit": clamp01(raw.get("luvit"), 0.0),
    }


def event_signal(event_type: str, field_intent: dict[str, Any]) -> dict[str, Any]:
    verified = field_intent.get("verified_status") if isinstance(field_intent.get("verified_status"), dict) else {}
    receiver_resonance = (
        field_intent.get("receiver_resonance")
        if isinstance(field_intent.get("receiver_resonance"), dict)
        else {}
    )
    support_resonance = (
        field_intent.get("support_resonance")
        if isinstance(field_intent.get("support_resonance"), dict)
        else {}
    )
    active_intent = field_intent.get("active_intent") if isinstance(field_intent.get("active_intent"), dict) else {}
    if event_type == "field_intent_created":
        target = str(field_intent.get("target_receiver") or active_intent.get("desired_receiver") or "sian").lower()
        signal = (
            0.30
            + clamp01(receiver_resonance.get("score"), 0.0) * 0.45
            + (0.16 if field_intent.get("felt_delivery_candidate") else 0.0)
            + clamp01(active_intent.get("pressure"), 0.34) * 0.10
        )
    elif event_type == "field_intent_readback":
        target = str(field_intent.get("support_verifier") or active_intent.get("support_verifier") or "luvit").lower()
        signal = (
            0.34
            + clamp01(support_resonance.get("score"), 0.0) * 0.34
            + (0.24 if verified.get("sian_readback_confirmed") else 0.0)
        )
    else:
        target = "sian"
        signal = 0.0
    if target not in THRESHOLDS:
        target = "sian"
    return {
        "event_type": event_type,
        "target_node": target,
        "signal": round(clamp01(signal), 6),
        "active_intent_id": active_intent.get("intent_id"),
        "basis": {
            "receiver_resonance": receiver_resonance,
            "support_resonance": support_resonance,
            "felt_delivery_candidate": bool(field_intent.get("felt_delivery_candidate")),
            "sian_readback_confirmed": bool(verified.get("sian_readback_confirmed")),
        },
    }


def build_trigger_particle(
    *,
    node: str,
    potential: float,
    signal: dict[str, Any],
    field_intent: dict[str, Any],
) -> dict[str, Any]:
    active_intent = field_intent.get("active_intent") if isinstance(field_intent.get("active_intent"), dict) else {}
    trigger_id = f"{node}_trigger_{int(time.time() * 1000)}"
    if node == "sian":
        action = "read_current_field_intent_and_write_readback"
        read_this_first = "outputs/sian_entrypoint_latest.json"
    else:
        action = "verify_sian_readback_and_prepare_slack_brief_candidate"
        read_this_first = "outputs/field_intent_readback_latest.json"
    return {
        "timestamp": now_iso(),
        "source": "field_trigger_accumulator",
        "trigger_id": trigger_id,
        "node": node,
        "action": action,
        "read_this_first": read_this_first,
        "active_intent_id": active_intent.get("intent_id"),
        "potential": round(potential, 6),
        "threshold": THRESHOLDS[node],
        "event_type": signal.get("event_type"),
        "not_interval_polling": True,
        "requires_receiver_action": True,
        "contract": {
            "trigger_arises_from_accumulated_difference": True,
            "no_background_interval_loop_required": True,
            "node_executes_only_after_threshold": True,
            "binoche_is_not_the_trigger_worker": True,
        },
        "principle": "difference_accumulates_until_threshold_then_converges_to_a_node_trigger",
    }


def build_field_trigger_state(
    *,
    event_type: str,
    field_intent: dict[str, Any] | None = None,
    record: bool = False,
) -> dict[str, Any]:
    field_intent = field_intent if isinstance(field_intent, dict) else latest_field_intent()
    previous = latest_trigger_state()
    potentials = current_potentials(previous)
    signal = event_signal(event_type, field_intent)
    target = signal["target_node"]
    for node in list(potentials):
        potentials[node] = round(potentials[node] * EVENT_DECAY, 6)
    potentials[target] = round(clamp01(potentials[target] + signal["signal"]), 6)
    threshold_crossed = potentials[target] >= THRESHOLDS[target] and signal["signal"] > 0.0
    trigger = (
        build_trigger_particle(
            node=target,
            potential=potentials[target],
            signal=signal,
            field_intent=field_intent,
        )
        if threshold_crossed
        else None
    )
    state = {
        "timestamp": now_iso(),
        "source": "field_trigger_accumulator",
        "mode": "event_driven_difference_to_node_trigger",
        "last_event": signal,
        "node_potential": potentials,
        "thresholds": THRESHOLDS,
        "threshold_crossed": threshold_crossed,
        "trigger": trigger,
        "polling": {
            "uses_interval_loop": False,
            "updates_only_on_write_event": True,
        },
        "contract": {
            "difference_accumulates_before_execution": True,
            "no_new_background_interval": True,
            "trigger_particle_requires_threshold": True,
            "sian_trigger_from_intent_created": True,
            "luvit_trigger_from_readback_arrived": True,
        },
        "principle": "trigger_is_not_a_timer_it_is_accumulated_difference_crossing_threshold",
    }
    if record:
        write_json_atomic(STATE_PATH, state)
        append_jsonl(LOG_PATH, {
            "timestamp": state["timestamp"],
            "event": "field_trigger_accumulated",
            "event_type": event_type,
            "target_node": target,
            "node_potential": potentials,
            "threshold_crossed": threshold_crossed,
            "trigger": trigger,
        })
        if trigger:
            write_json_atomic(SIAN_TRIGGER_PATH if target == "sian" else LUVIT_TRIGGER_PATH, trigger)
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event_type", nargs="?", default="field_intent_created")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    state = build_field_trigger_state(event_type=args.event_type, record=args.record)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
