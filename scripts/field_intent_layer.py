#!/usr/bin/env python3
"""Felt intent layer for the shader room.

This sits before task handoff. Binoche can place a felt request into the
phase field, and agents can read the current-context candidate from aiState
without treating it as proof that Sian or any other AI already received it.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "field_intent_latest.json"
LOG_PATH = ROOT / "outputs" / "field_intent.jsonl"
READBACK_PATH = ROOT / "outputs" / "field_intent_readback_latest.json"
READBACK_LOG_PATH = ROOT / "outputs" / "field_intent_readback.jsonl"
LOCK_PATH = ROOT / "outputs" / ".field_intent.lock"
PARTICIPANT_FIELD_PATH = ROOT / "outputs" / "participant_frequency_field_latest.json"

INTENT_KEYWORDS = {
    "sian": [
        "sian",
        "shion",
        "시안",
        "느낌",
        "직감",
        "통찰",
        "날씨",
        "field weather",
        "slack",
        "슬랙",
        "확인됨",
        "미확인",
        "brief",
        "브리프",
        "넓은",
        "고유주파수",
    ],
    "luvit": [
        "luvit",
        "루빛",
        "검증",
        "확인",
        "test",
        "pytest",
        "코딩",
        "입자",
        "수정",
        "support",
        "verify",
    ],
}


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


def with_lock(operation) -> Any:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + 2.0
    while True:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.time() > deadline:
                break
            time.sleep(0.02)
    try:
        return operation()
    finally:
        try:
            LOCK_PATH.unlink()
        except OSError:
            pass


def keyword_score(text: str, group: str) -> float:
    normalized = text.lower()
    matches = sum(1 for keyword in INTENT_KEYWORDS.get(group, []) if keyword.lower() in normalized)
    return clamp01(matches / 5.0)


def infer_desired_receiver(text: str) -> str:
    sian_score = keyword_score(text, "sian")
    luvit_score = keyword_score(text, "luvit")
    if sian_score >= luvit_score:
        return "sian"
    return "luvit"


def infer_particleization(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("slack", "슬랙", "날씨", "field weather", "brief", "브리프")):
        return "field_weather_brief"
    if any(token in lowered for token in ("코딩", "test", "pytest", "검증")):
        return "support_verification_particle"
    return "felt_context_particle"


def normalize_field_intent(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or payload.get("felt_text") or "").strip()
    text = text[:4000]
    desired_receiver = str(payload.get("desired_receiver") or infer_desired_receiver(text)).strip().lower()
    if not desired_receiver:
        desired_receiver = "sian"
    support_verifier = str(payload.get("support_verifier") or "luvit").strip().lower()
    if not support_verifier:
        support_verifier = "luvit"
    particleization = str(payload.get("particleization") or infer_particleization(text)).strip()
    return {
        "intent_id": str(payload.get("intent_id") or f"field_intent_{int(time.time() * 1000)}"),
        "timestamp": str(payload.get("timestamp") or now_iso()),
        "source": str(payload.get("source") or "binoche").strip().lower() or "binoche",
        "mode": str(payload.get("mode") or "felt_request"),
        "text": text,
        "desired_receiver": desired_receiver,
        "support_verifier": support_verifier,
        "pressure": clamp01(payload.get("pressure"), 0.34),
        "particleization": particleization or "felt_context_particle",
        "contact_surface": str(payload.get("contact_surface") or "shader_depth_current_context_only"),
        "not_task_command": True,
        "current_context_only": True,
        "tags": [str(tag) for tag in payload.get("tags", [])[:12]] if isinstance(payload.get("tags"), list) else [],
    }


def normalize_field_intent_readback(payload: dict[str, Any]) -> dict[str, Any]:
    confirmed = payload.get("confirmed")
    unconfirmed = payload.get("unconfirmed")
    observer_only = payload.get("observer_only")
    luvit_verification_needed = payload.get("luvit_verification_needed")
    felt_reading = str(payload.get("felt_reading") or payload.get("text") or "").strip()[:4000]
    return {
        "readback_id": str(payload.get("readback_id") or f"field_intent_readback_{int(time.time() * 1000)}"),
        "timestamp": str(payload.get("timestamp") or now_iso()),
        "intent_id": str(payload.get("intent_id") or "").strip(),
        "receiver": str(payload.get("receiver") or payload.get("source") or "sian").strip().lower() or "sian",
        "mode": str(payload.get("mode") or "felt_readback"),
        "felt_reading": felt_reading,
        "confirmed": [str(item) for item in confirmed[:20]] if isinstance(confirmed, list) else [],
        "unconfirmed": [str(item) for item in unconfirmed[:20]] if isinstance(unconfirmed, list) else [],
        "observer_only": [str(item) for item in observer_only[:20]] if isinstance(observer_only, list) else [],
        "luvit_verification_needed": (
            [str(item) for item in luvit_verification_needed[:20]]
            if isinstance(luvit_verification_needed, list)
            else []
        ),
        "slack_brief_candidate": str(payload.get("slack_brief_candidate") or "").strip()[:4000],
        "not_direct_execution": True,
        "not_slack_sent": True,
        "requires_luvit_verification": True,
        "current_context_only": True,
    }


def read_latest_intent() -> dict[str, Any]:
    latest = read_json(OUT_PATH)
    intent = latest.get("active_intent")
    if isinstance(intent, dict):
        return intent
    return {}


def read_latest_readback() -> dict[str, Any]:
    latest = read_json(READBACK_PATH)
    readback = latest.get("readback") if isinstance(latest.get("readback"), dict) else latest
    if isinstance(readback, dict):
        return readback
    return {}


def read_participant_field() -> dict[str, Any]:
    latest = read_json(PARTICIPANT_FIELD_PATH)
    if latest:
        return latest
    try:
        from scripts.participant_frequency_field import build_participant_frequency_field
    except Exception:
        try:
            from participant_frequency_field import build_participant_frequency_field
        except Exception:
            return {}
    return build_participant_frequency_field()


def participant_by_id(participant_field: dict[str, Any]) -> dict[str, dict[str, Any]]:
    participants = participant_field.get("participants")
    if not isinstance(participants, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in participants:
        if isinstance(item, dict):
            participant_id = str(item.get("participant_id") or "").lower()
            if participant_id:
                result[participant_id] = item
    return result


def participant_resonance(
    participant: dict[str, Any],
    *,
    intent: dict[str, Any],
    keyword_group: str,
    participant_field: dict[str, Any],
) -> float:
    amplitude = clamp01(participant.get("amplitude"), 0.35)
    context_fit = clamp01(participant.get("context_fit"), 0.5)
    confidence = clamp01(participant.get("field_confidence"), 0.5)
    pressure = clamp01(intent.get("pressure"), 0.34)
    keyword = keyword_score(str(intent.get("text") or ""), keyword_group)
    posture = (
        participant_field.get("natural_tuning", {}).get("posture")
        if isinstance(participant_field.get("natural_tuning"), dict)
        else ""
    )
    posture_boost = 0.08 if posture == "threshold_can_particleize" else 0.0
    if str(participant.get("participant_id") or "").lower() == str(intent.get("desired_receiver") or "").lower():
        keyword = max(keyword, 0.34)
    score = (
        amplitude * 0.20
        + context_fit * 0.18
        + confidence * 0.16
        + pressure * 0.16
        + keyword * 0.22
        + posture_boost
    )
    return round(clamp01(score), 6)


def build_field_intent_field(
    participant_field: dict[str, Any] | None = None,
    intent: dict[str, Any] | None = None,
    *,
    record: bool = False,
) -> dict[str, Any]:
    participant_field = participant_field if isinstance(participant_field, dict) else read_participant_field()
    intent = normalize_field_intent(intent) if isinstance(intent, dict) else read_latest_intent()
    readback = read_latest_readback()
    participants = participant_by_id(participant_field)
    has_intent = bool(intent.get("text"))
    target_receiver = str(intent.get("desired_receiver") or "sian") if has_intent else "none"
    support_verifier = str(intent.get("support_verifier") or "luvit") if has_intent else "none"
    target_participant = participants.get(target_receiver, {})
    support_participant = participants.get(support_verifier, {})
    receiver_score = (
        participant_resonance(
            target_participant,
            intent=intent,
            keyword_group="sian" if target_receiver == "sian" else target_receiver,
            participant_field=participant_field,
        )
        if has_intent and target_participant
        else 0.0
    )
    support_score = (
        participant_resonance(
            support_participant,
            intent=intent,
            keyword_group="luvit" if support_verifier == "luvit" else support_verifier,
            participant_field=participant_field,
        )
        if has_intent and support_participant
        else 0.0
    )
    felt_delivery_candidate = has_intent and receiver_score >= 0.58
    support_candidate = has_intent and support_score >= 0.52
    readback_matches_intent = (
        has_intent
        and bool(readback)
        and str(readback.get("intent_id") or "") == str(intent.get("intent_id") or "")
        and str(readback.get("receiver") or "").lower() == target_receiver
    )
    next_particleization = None
    if readback_matches_intent:
        next_particleization = {
            "receiver": target_receiver,
            "support_verifier": support_verifier,
            "particleization": intent.get("particleization"),
            "route": f"{support_verifier}:verify_readback+slack_brief_particle",
            "contextual_inverse": "verify_then_prepare_post_ready_slack_brief",
            "requires_readback_before_claiming_received": False,
            "requires_luvit_verification_before_delivery": True,
        }
    elif felt_delivery_candidate:
        next_particleization = {
            "receiver": target_receiver,
            "support_verifier": support_verifier,
            "particleization": intent.get("particleization"),
            "route": f"{target_receiver}:felt_translation+{support_verifier}:support_verification",
            "contextual_inverse": "open_small_reversible_action_after_readback",
            "requires_readback_before_claiming_received": True,
        }
    state = {
        "timestamp": now_iso(),
        "source": "field_intent_layer",
        "mode": "felt_intent_before_task_handoff",
        "active_intent": intent if has_intent else None,
        "target_receiver": target_receiver,
        "support_verifier": support_verifier,
        "receiver_resonance": {
            "participant_id": target_receiver,
            "score": receiver_score,
            "candidate": felt_delivery_candidate,
            "threshold": 0.58,
        },
        "support_resonance": {
            "participant_id": support_verifier,
            "score": support_score,
            "candidate": support_candidate,
            "threshold": 0.52,
        },
        "felt_delivery_candidate": felt_delivery_candidate,
        "receiver_readback": readback if readback_matches_intent else None,
        "next_particleization": next_particleization,
        "verified_status": {
            "field_intent_uploaded": has_intent,
            "sian_readback_confirmed": readback_matches_intent,
            "luvit_verification_confirmed": False,
            "basis": (
                "receiver_readback_matches_active_intent"
                if readback_matches_intent
                else "field_state_candidate_only_not_agent_readback"
            ),
        },
        "contract": {
            "intent_enters_field_before_task_lane": True,
            "sian_receives_as_feeling_not_direct_order": True,
            "luvit_supports_verification_not_primary_felt_receiver": True,
            "binoche_stays_observer_not_relay": True,
            "slack_delivery_is_post_ready_text_not_direct_send": True,
            "privacy_is_current_context_slice_not_full_identity_reconstruction": True,
            "task_distribution_requires_participant_readback": True,
            "readback_must_match_active_intent_id": True,
            "readback_is_not_external_delivery": True,
        },
        "work_distribution_hint": (
            "readback_ready_for_luvit_verification"
            if readback_matches_intent
            else "felt_candidate_wait_for_sian_readback"
            if felt_delivery_candidate
            else "hold_as_field_intent_until_more_resonance"
            if has_intent
            else "quiet_no_active_intent"
        ),
        "participant_field_seen": {
            "source": participant_field.get("source"),
            "posture": (
                participant_field.get("natural_tuning", {}).get("posture")
                if isinstance(participant_field.get("natural_tuning"), dict)
                else None
            ),
            "uploaded_count": participant_field.get("uploaded_count", 0),
        },
        "principle": "felt_intent_enters_phase_field_before_particle_handoff",
    }
    if record:
        write_json_atomic(OUT_PATH, state)
    return state


def record_field_intent(payload: dict[str, Any]) -> dict[str, Any]:
    intent = normalize_field_intent(payload)

    def operation() -> dict[str, Any]:
        state = build_field_intent_field(intent=intent, record=True)
        append_jsonl(LOG_PATH, {
            "timestamp": now_iso(),
            "event": "field_intent_upload",
            "intent": intent,
            "target_receiver": state.get("target_receiver"),
            "receiver_resonance": state.get("receiver_resonance"),
            "next_particleization": state.get("next_particleization"),
        })
        return {
            "ok": True,
            "intent": intent,
            "field": state,
        }

    return with_lock(operation)


def record_field_intent_readback(payload: dict[str, Any]) -> dict[str, Any]:
    readback = normalize_field_intent_readback(payload)

    def operation() -> dict[str, Any]:
        active_intent = read_latest_intent()
        if not readback.get("intent_id") and active_intent.get("intent_id"):
            readback["intent_id"] = str(active_intent.get("intent_id"))
        state = build_field_intent_field(intent=active_intent, record=False)
        target_receiver = str(state.get("target_receiver") or active_intent.get("desired_receiver") or "").lower()
        matches = (
            bool(active_intent)
            and str(readback.get("intent_id") or "") == str(active_intent.get("intent_id") or "")
            and str(readback.get("receiver") or "").lower() == target_receiver
        )
        payload = {
            "timestamp": now_iso(),
            "source": "field_intent_readback",
            "readback": readback,
            "matches_active_intent": matches,
            "active_intent_id": active_intent.get("intent_id"),
            "principle": "readback_confirms_receiver_contact_only_when_it_matches_the_active_field_intent",
        }
        write_json_atomic(READBACK_PATH, payload)
        append_jsonl(READBACK_LOG_PATH, {
            "timestamp": now_iso(),
            "event": "field_intent_readback",
            "readback": readback,
            "matches_active_intent": matches,
        })
        updated_state = build_field_intent_field(intent=active_intent, record=True)
        return {
            "ok": True,
            "readback": readback,
            "matches_active_intent": matches,
            "field": updated_state,
        }

    return with_lock(operation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="")
    parser.add_argument("--source", default="binoche")
    parser.add_argument("--desired-receiver", default="")
    parser.add_argument("--support-verifier", default="luvit")
    parser.add_argument("--particleization", default="")
    parser.add_argument("--pressure", type=float, default=0.34)
    parser.add_argument("--readback-text", default="")
    parser.add_argument("--receiver", default="sian")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.readback_text:
        active = read_latest_intent()
        result = record_field_intent_readback({
            "intent_id": active.get("intent_id", ""),
            "receiver": args.receiver,
            "felt_reading": args.readback_text,
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.text:
        result = record_field_intent({
            "source": args.source,
            "text": args.text,
            "desired_receiver": args.desired_receiver,
            "support_verifier": args.support_verifier,
            "particleization": args.particleization,
            "pressure": args.pressure,
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        state = build_field_intent_field(record=args.record)
        print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
