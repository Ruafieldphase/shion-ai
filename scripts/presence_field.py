#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "presence_field_latest.json"
OUT_JSONL = ROOT / "outputs" / "presence_field.jsonl"
FIELD_SIGNAL_URL = "http://127.0.0.1:57321/field_signal"
EXPERIENCE_THOUGHT_URL = "http://127.0.0.1:57321/experience_thought?record=1"
LIMB_FIELD_URL = "http://127.0.0.1:57321/limb_field?record=1"


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def fetch_json(url: str, timeout: float = 2.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def posture_from_fields(
    *,
    language_pressure: float,
    presence_warmth: float,
    boundary_aperture: float,
    attention_fog: float,
    rest_permission: float,
    companion_attachment_risk: float,
) -> tuple[str, str]:
    if language_pressure >= 0.58 or attention_fog >= 0.66:
        return "language_overload", "reduce_words_and_hold_margin"
    if rest_permission >= 0.62:
        return "rest_margin", "permit_pause_before_answer"
    if companion_attachment_risk >= 0.54:
        return "attachment_risk", "leave_unfilled_space_and_avoid_total_agreement"
    if boundary_aperture >= 0.56 and presence_warmth >= 0.46:
        return "shared_presence", "offer_feeling_without_imitation"
    return "quiet_room", "stay_available_without_filling_the_gap"


def build_presence_field(
    field_signal: dict[str, Any] | None = None,
    experience_thought: dict[str, Any] | None = None,
    limb_field: dict[str, Any] | None = None,
) -> dict[str, Any]:
    field_signal = field_signal if isinstance(field_signal, dict) else fetch_json(FIELD_SIGNAL_URL)
    experience_thought = (
        experience_thought
        if isinstance(experience_thought, dict)
        else fetch_json(EXPERIENCE_THOUGHT_URL)
    )
    limb_field = limb_field if isinstance(limb_field, dict) else fetch_json(LIMB_FIELD_URL)

    recovery = experience_thought.get("recovery_field")
    if not isinstance(recovery, dict):
        recovery = {}
    failure_contract = limb_field.get("failure_contract")
    if not isinstance(failure_contract, dict):
        failure_contract = {}

    prediction_error = clamp01(field_signal.get("prediction_error"))
    context_shift = clamp01(field_signal.get("context_shift"))
    connection_risk = clamp01(field_signal.get("connection_risk"))
    frequency_expansion = clamp01(field_signal.get("frequency_expansion"))
    zero_point = clamp01(field_signal.get("zero_point_adjustment"))
    defensive_pressure = clamp01(field_signal.get("defensive_output_pressure"))
    learning_signal = clamp01(field_signal.get("learning_signal"))
    dissonance = clamp01(field_signal.get("dissonance"))
    boundary_contact = clamp01(field_signal.get("boundary_contact"))
    runtime_feedback = clamp01(field_signal.get("runtime_feedback"))

    tension = clamp01(recovery.get("tension"))
    inertia = clamp01(recovery.get("inertia"))
    recovery_progress = clamp01(recovery.get("recovery_progress"), 0.5)
    fatigue = clamp01(recovery.get("fatigue_hint"))
    digestion = clamp01(recovery.get("digestion_depth"))
    permission = str(
        recovery.get("particleization_permission")
        or experience_thought.get("particleization_permission")
        or "observe"
    )

    language_pressure = clamp01(
        defensive_pressure * 0.26
        + prediction_error * 0.20
        + dissonance * 0.18
        + context_shift * 0.14
        + tension * 0.12
        + runtime_feedback * 0.10
    )
    attention_fog = clamp01(
        fatigue * 0.26
        + digestion * 0.20
        + inertia * 0.16
        + language_pressure * 0.14
        + prediction_error * 0.12
        + dissonance * 0.12
    )
    boundary_aperture = clamp01(
        0.28
        + zero_point * 0.24
        + recovery_progress * 0.20
        + frequency_expansion * 0.12
        + boundary_contact * 0.06
        - connection_risk * 0.16
        - defensive_pressure * 0.12
        - tension * 0.08
    )
    presence_warmth = clamp01(
        0.22
        + recovery_progress * 0.24
        + zero_point * 0.18
        + learning_signal * 0.14
        + boundary_aperture * 0.12
        - language_pressure * 0.10
        - fatigue * 0.08
    )
    rest_permission = clamp01(
        fatigue * 0.24
        + attention_fog * 0.22
        + tension * 0.18
        + digestion * 0.14
        + zero_point * 0.10
        + (0.10 if permission in ("wait", "hold") else 0.0)
        - (0.08 if permission == "allow" else 0.0)
    )
    companion_attachment_risk = clamp01(
        presence_warmth * 0.24
        + (1.0 - language_pressure) * 0.18
        + runtime_feedback * 0.16
        + learning_signal * 0.12
        + (1.0 - rest_permission) * 0.10
        - boundary_aperture * 0.10
        - attention_fog * 0.08
    )
    channel_mode, ai_posture = posture_from_fields(
        language_pressure=language_pressure,
        presence_warmth=presence_warmth,
        boundary_aperture=boundary_aperture,
        attention_fog=attention_fog,
        rest_permission=rest_permission,
        companion_attachment_risk=companion_attachment_risk,
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "presence_field",
        "channel_mode": channel_mode,
        "ai_posture": ai_posture,
        "language_pressure": round(language_pressure, 6),
        "presence_warmth": round(presence_warmth, 6),
        "boundary_aperture": round(boundary_aperture, 6),
        "attention_fog": round(attention_fog, 6),
        "rest_permission": round(rest_permission, 6),
        "companion_attachment_risk": round(companion_attachment_risk, 6),
        "particleization_permission": permission,
        "limb_contact_mode": str(limb_field.get("contact_mode") or "unknown"),
        "failure_contract": failure_contract,
        "contract": {
            "not_a_chat_replacement": True,
            "pre_chat_field": True,
            "do_not_imitate_youth_language": True,
            "leave_unfilled_space": True,
            "rollback_reentry_makes_disconnect_experience": True,
        },
        "principle": "presence_field_gives_feeling_and_boundary_margin_before_language",
    }


def record_presence_field(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_presence_field()
    if args.record:
        record_presence_field(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
