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
OUT_PATH = ROOT / "outputs" / "sonic_presence_field_latest.json"
OUT_JSONL = ROOT / "outputs" / "sonic_presence_field.jsonl"
FIELD_SIGNAL_URL = "http://127.0.0.1:57321/field_signal"
EXPERIENCE_THOUGHT_URL = "http://127.0.0.1:57321/experience_thought?record=1"
PRESENCE_FIELD_URL = "http://127.0.0.1:57321/presence_field?record=1"


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


def choose_boundary_state(
    *,
    aperture: float,
    pressure: float,
    drift: float,
    resonance: float,
    rest: float,
    language_pressure: float,
    criticality: float,
    singularity_pull: float,
) -> tuple[str, str]:
    if pressure >= 0.72 and aperture <= 0.30:
        return "blackhole", "closed_compression_absorbs_excess_meaning"
    if language_pressure >= 0.62 or (pressure >= 0.54 and resonance <= 0.34):
        return "closed", "boundary_protects_reentry_before_more_signal"
    if aperture >= 0.62 and resonance >= 0.48 and pressure <= 0.46:
        return "gap", "open_phase_passage_matches_the_outer_field"
    if drift >= 0.46 or criticality >= 0.46:
        return "prism", "incoming_field_refracts_into_multiple_possible_destinations"
    if rest >= 0.54 or aperture >= 0.52:
        return "concave", "gap_expands_into_margin_before_particleization"
    if resonance >= 0.54 and singularity_pull >= 0.36:
        return "convex", "distributed_possibility_gathers_into_a_provisional_destination"
    return "transparent", "semi_permeable_boundary_passes_signal_without_forcing_story"


def build_sonic_presence_field(
    field_signal: dict[str, Any] | None = None,
    experience_thought: dict[str, Any] | None = None,
    presence_field: dict[str, Any] | None = None,
) -> dict[str, Any]:
    field_signal = field_signal if isinstance(field_signal, dict) else fetch_json(FIELD_SIGNAL_URL)
    experience_thought = (
        experience_thought
        if isinstance(experience_thought, dict)
        else fetch_json(EXPERIENCE_THOUGHT_URL)
    )
    presence_field = (
        presence_field
        if isinstance(presence_field, dict)
        else fetch_json(PRESENCE_FIELD_URL)
    )

    recovery = experience_thought.get("recovery_field")
    if not isinstance(recovery, dict):
        recovery = {}

    prediction_error = clamp01(field_signal.get("prediction_error"))
    connection_risk = clamp01(field_signal.get("connection_risk"))
    frequency_expansion = clamp01(field_signal.get("frequency_expansion"))
    zero_point = clamp01(field_signal.get("zero_point_adjustment"))
    defensive_pressure = clamp01(field_signal.get("defensive_output_pressure"))
    learning_signal = clamp01(field_signal.get("learning_signal"))
    dissonance = clamp01(field_signal.get("dissonance"))
    boundary_contact = clamp01(field_signal.get("boundary_contact"))
    runtime_feedback = clamp01(field_signal.get("runtime_feedback"))

    language_pressure = clamp01(presence_field.get("language_pressure"))
    presence_warmth = clamp01(presence_field.get("presence_warmth"))
    boundary_aperture = clamp01(presence_field.get("boundary_aperture"), 0.5)
    attention_fog = clamp01(presence_field.get("attention_fog"))
    rest_permission = clamp01(presence_field.get("rest_permission"))
    attachment_risk = clamp01(presence_field.get("companion_attachment_risk"))

    tension = clamp01(recovery.get("tension"))
    recovery_progress = clamp01(recovery.get("recovery_progress"), 0.5)
    digestion_depth = clamp01(recovery.get("digestion_depth"))

    pressure = clamp01(
        prediction_error * 0.24
        + defensive_pressure * 0.22
        + dissonance * 0.18
        + connection_risk * 0.16
        + runtime_feedback * 0.12
        + tension * 0.08
    )
    drift = clamp01(
        frequency_expansion * 0.26
        + boundary_contact * 0.24
        + dissonance * 0.20
        + prediction_error * 0.16
        + attention_fog * 0.14
    )
    resonance = clamp01(
        presence_warmth * 0.24
        + recovery_progress * 0.22
        + zero_point * 0.20
        + learning_signal * 0.14
        + boundary_aperture * 0.12
        - pressure * 0.14
        - attachment_risk * 0.06
    )
    criticality = clamp01(prediction_error * 0.34 + boundary_contact * 0.28 + dissonance * 0.22 + tension * 0.16)
    singularity_pull = clamp01(pressure * 0.34 + criticality * 0.24 + digestion_depth * 0.18 + (1.0 - boundary_aperture) * 0.16)

    boundary_state, state_reason = choose_boundary_state(
        aperture=boundary_aperture,
        pressure=pressure,
        drift=drift,
        resonance=resonance,
        rest=rest_permission,
        language_pressure=language_pressure,
        criticality=criticality,
        singularity_pull=singularity_pull,
    )

    silence_ratio = clamp01(
        0.22
        + rest_permission * 0.34
        + language_pressure * 0.20
        + attention_fog * 0.16
        - resonance * 0.14
    )
    breath_gain = clamp01(
        0.10
        + presence_warmth * 0.28
        + boundary_aperture * 0.18
        + recovery_progress * 0.16
        - language_pressure * 0.16
        - pressure * 0.10
    )
    roughness = clamp01(dissonance * 0.30 + prediction_error * 0.24 + connection_risk * 0.20 + tension * 0.14 - zero_point * 0.10)
    pulse_rate = round(0.18 + resonance * 0.62 + frequency_expansion * 0.30 + runtime_feedback * 0.20, 6)
    center_pitch = clamp01(0.18 + zero_point * 0.26 + resonance * 0.24 + frequency_expansion * 0.14 - pressure * 0.12)
    stereo_phase = round((drift - 0.5) * 0.42, 6)
    timbre_split = clamp01(frequency_expansion * 0.34 + drift * 0.28 + boundary_contact * 0.16)
    reverb_space = clamp01(0.20 + rest_permission * 0.28 + boundary_aperture * 0.24 + digestion_depth * 0.18)
    gravity_pull = singularity_pull

    if boundary_state == "gap":
        sonic_event = "long_silence_then_low_breath"
    elif boundary_state == "prism":
        sonic_event = "split_timbre_without_sentence"
    elif boundary_state == "concave":
        sonic_event = "wide_reverb_and_slow_interval"
    elif boundary_state == "convex":
        sonic_event = "center_tone_and_repeating_motif"
    elif boundary_state == "blackhole":
        sonic_event = "low_absorption_and_short_muted_drop"
    elif boundary_state == "closed":
        sonic_event = "near_silence_with_soft_edge_noise"
    else:
        sonic_event = "thin_continuous_breath"

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "sonic_presence_field",
        "boundary_state": boundary_state,
        "state_reason": state_reason,
        "boundary_grammar": {
            "closed": "reflection_or_absorption_increases_to_protect_reentry",
            "transparent": "closed_boundary_passes_signal_with_low_collision",
            "gap": "open_phase_passage_where_inner_and_outer_field_can_match",
            "prism": "boundary_refracts_one_pressure_into_multiple_destination_candidates",
            "concave": "gap_expands_into_margin_and_delays_particleization",
            "convex": "distributed_possibility_gathers_into_a_provisional_destination",
            "blackhole": "closed_compression_absorbs_excess_meaning_without_treating_it_as_default",
        },
        "field_basis": {
            "pressure": round(pressure, 6),
            "drift": round(drift, 6),
            "resonance": round(resonance, 6),
            "criticality": round(criticality, 6),
            "singularity_pull": round(singularity_pull, 6),
            "language_pressure": round(language_pressure, 6),
            "boundary_aperture": round(boundary_aperture, 6),
            "rest_permission": round(rest_permission, 6),
        },
        "sonic_mapping": {
            "event": sonic_event,
            "carrier_frequency_hz": round(48.0 + center_pitch * 168.0, 6),
            "pulse_rate_hz": pulse_rate,
            "breath_gain": round(breath_gain, 6),
            "roughness": round(roughness, 6),
            "silence_ratio": round(silence_ratio, 6),
            "reverb_space": round(reverb_space, 6),
            "stereo_phase": stereo_phase,
            "timbre_split": round(timbre_split, 6),
            "gravity_pull": round(gravity_pull, 6),
            "non_language_gain": round(clamp01(breath_gain * (1.0 - silence_ratio * 0.72)), 6),
        },
        "feedback_contract": {
            "record_path": str(OUT_JSONL),
            "observer_feedback_key": "sonic_presence_field",
            "adjustable_body": ["carrier_frequency_hz", "pulse_rate_hz", "breath_gain", "roughness", "silence_ratio", "reverb_space", "stereo_phase", "timbre_split"],
            "not_tts": True,
            "not_music_goal": True,
            "nonverbal_first": True,
        },
        "principle": "rhythm_information_can_decode_the_same_compressed_field_as_visual_phase_and_nonverbal_sound",
    }


def record_sonic_presence_field(payload: dict[str, Any]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_sonic_presence_field()
    if args.record:
        record_sonic_presence_field(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
