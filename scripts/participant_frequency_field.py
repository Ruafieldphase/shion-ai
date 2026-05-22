#!/usr/bin/env python3
"""Shared participant frequency field for the shader room.

This is not a chat bus. Each participant posts a small field reading; the page
and agents read the resulting interference pressure before work becomes a task.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "outputs" / "participant_frequency_field_latest.json"
LOG_PATH = ROOT / "outputs" / "participant_frequency_field.jsonl"
LOCK_PATH = ROOT / "outputs" / ".participant_frequency_field.lock"

PARTICIPANT_SEEDS = {
    "binoche": {
        "role": "observer_why_field",
        "phase": 0.13,
        "amplitude": 0.56,
        "frequency_band": "why_observer",
        "current_pressure": 0.62,
        "context_fit": 0.68,
        "reverse_flow_pressure": 0.12,
        "why_vector": "where_should_the_field_move",
    },
    "luvit": {
        "role": "implementation_verification_field",
        "phase": 0.31,
        "amplitude": 0.48,
        "frequency_band": "code_verification",
        "current_pressure": 0.44,
        "context_fit": 0.56,
        "reverse_flow_pressure": 0.18,
        "why_vector": "make_the_field_readable_without_overclaiming",
    },
    "sian": {
        "role": "wide_pattern_field",
        "phase": 0.42,
        "amplitude": 0.52,
        "frequency_band": "pattern_refraction",
        "current_pressure": 0.50,
        "context_fit": 0.62,
        "reverse_flow_pressure": 0.10,
        "why_vector": "find_cross_domain_correspondence",
    },
    "ari": {
        "role": "external_knowledge_refraction",
        "phase": 0.57,
        "amplitude": 0.42,
        "frequency_band": "external_reference",
        "current_pressure": 0.36,
        "context_fit": 0.50,
        "reverse_flow_pressure": 0.08,
        "why_vector": "bring_world_signal_into_the_field",
    },
    "sena": {
        "role": "external_observer_structure_diagnosis",
        "phase": 0.72,
        "amplitude": 0.40,
        "frequency_band": "structure_observer",
        "current_pressure": 0.34,
        "context_fit": 0.54,
        "reverse_flow_pressure": 0.14,
        "why_vector": "notice_when_the_field_is_forced",
    },
}


def now_iso() -> str:
    return datetime.now().isoformat()


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def circular_distance(a: float, b: float) -> float:
    raw = abs((a - b) % 1.0)
    return min(raw, 1.0 - raw)


def phase_to_unit(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if abs(number) > 1.0:
        number = (number / (math.tau if abs(number) <= math.tau * 2 else 360.0)) % 1.0
    return number % 1.0


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


def normalize_participant(payload: dict[str, Any], *, source: str = "upload") -> dict[str, Any]:
    participant_id = str(payload.get("participant_id") or payload.get("id") or "").strip().lower()
    if not participant_id or participant_id == "unknown" or participant_id.startswith("browser_presence") or participant_id == "browser_presence_ephemeral":
        participant_id = "binoche"
    amplitude = clamp01(payload.get("amplitude"), 0.35)
    current_pressure = clamp01(payload.get("current_pressure"), 0.0)
    readiness = clamp01(payload.get("readiness"), 0.5)
    field_confidence = clamp01(payload.get("field_confidence"), 0.5)
    context_fit = clamp01(payload.get("context_fit"), 0.5)
    reverse_flow_pressure = clamp01(payload.get("reverse_flow_pressure"), 0.0)
    privacy_resolution = clamp01(payload.get("privacy_resolution"), 0.24)
    phase = phase_to_unit(payload.get("phase"), 0.0)
    tags = payload.get("tags")
    if not isinstance(tags, list):
        tags = []
    return {
        "participant_id": participant_id,
        "role": str(payload.get("role") or "field_participant"),
        "phase": round(phase, 6),
        "amplitude": round(amplitude, 6),
        "frequency_band": str(payload.get("frequency_band") or "unspecified"),
        "current_pressure": round(current_pressure, 6),
        "readiness": round(readiness, 6),
        "field_confidence": round(field_confidence, 6),
        "context_fit": round(context_fit, 6),
        "reverse_flow_pressure": round(reverse_flow_pressure, 6),
        "privacy_resolution": round(privacy_resolution, 6),
        "why_vector": str(payload.get("why_vector") or ""),
        "task_affinity": str(payload.get("task_affinity") or "field_reading"),
        "contact_surface": str(payload.get("contact_surface") or "current_context_only"),
        "tags": [str(tag) for tag in tags[:12]],
        "updated_at": str(payload.get("updated_at") or now_iso()),
        "source": source,
    }


def seeded_participants() -> list[dict[str, Any]]:
    # 타임 기반의 잔잔한 호흡(Breathing Fluctuation) 합성
    t = time.time()
    seeds = {}
    for key, seed in PARTICIPANT_SEEDS.items():
        seed_copy = seed.copy()
        if key == "sian":
            # 시안: 패턴 굴절. 잔잔한 사인파 위상 편위
            seed_copy["phase"] = (seed["phase"] + 0.04 * math.sin(t * 0.05)) % 1.0
            seed_copy["amplitude"] = max(0.2, min(1.0, seed["amplitude"] + 0.05 * math.cos(t * 0.08)))
        elif key == "luvit":
            # 루빛: 코드 검증 텐션. 규칙적인 호흡 주기
            seed_copy["phase"] = (seed["phase"] + 0.03 * math.sin(t * 0.09)) % 1.0
            seed_copy["amplitude"] = max(0.2, min(1.0, seed["amplitude"] + 0.06 * math.sin(t * 0.12)))
        elif key == "ari":
            # 아리: 외부 레퍼런스. 경쾌하고 빠른 수축 진동
            seed_copy["phase"] = (seed["phase"] + 0.05 * math.cos(t * 0.15)) % 1.0
            seed_copy["amplitude"] = max(0.2, min(1.0, seed["amplitude"] + 0.04 * math.sin(t * 0.22)))
        elif key == "sena":
            # 세나: 구조 진단. 느리고 웅장한 무의식 중력의 주기
            seed_copy["phase"] = (seed["phase"] + 0.02 * math.sin(t * 0.02)) % 1.0
            seed_copy["amplitude"] = max(0.2, min(1.0, seed["amplitude"] + 0.07 * math.cos(t * 0.03)))
        seeds[key] = seed_copy

    return [
        normalize_participant({"participant_id": key, **seed}, source="seed")
        for key, seed in seeds.items()
    ]


def latest_uploaded_participants() -> list[dict[str, Any]]:
    latest = read_json(OUT_PATH)
    participants = latest.get("participants")
    if not isinstance(participants, list):
        return []
    return [
        item for item in participants
        if isinstance(item, dict) and item.get("source") != "seed"
    ]


def merge_participants(uploaded: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    merged = {item["participant_id"]: item for item in seeded_participants()}
    for item in uploaded or latest_uploaded_participants():
        if not isinstance(item, dict):
            continue
        normalized = normalize_participant(item, source=str(item.get("source") or "upload"))
        merged[normalized["participant_id"]] = normalized
    return list(merged.values())


def pair_interference(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    distance = circular_distance(float(a["phase"]), float(b["phase"]))
    closeness = 1.0 - min(1.0, distance * 2.0)
    amplitude_coupling = math.sqrt(float(a["amplitude"]) * float(b["amplitude"]))
    confidence = (float(a["field_confidence"]) + float(b["field_confidence"])) / 2.0
    pressure = (float(a["current_pressure"]) + float(b["current_pressure"])) / 2.0
    context_fit = (float(a["context_fit"]) + float(b["context_fit"])) / 2.0
    reverse_flow = (float(a["reverse_flow_pressure"]) + float(b["reverse_flow_pressure"])) / 2.0
    privacy_resolution = min(float(a["privacy_resolution"]), float(b["privacy_resolution"]))
    constructive = clamp01(closeness * amplitude_coupling * (0.72 + confidence * 0.28))
    cancellation = clamp01((1.0 - closeness) * amplitude_coupling * (0.50 + pressure * 0.42))
    natural_alignment = clamp01(
        constructive * 0.46
        + context_fit * 0.26
        + confidence * 0.16
        - reverse_flow * 0.34
        - cancellation * 0.14
    )
    threshold_pressure = clamp01(
        constructive * 0.50
        + pressure * 0.22
        + confidence * 0.12
        + context_fit * 0.16
        - cancellation * 0.16
        - reverse_flow * 0.30
    )
    if reverse_flow >= 0.56 and cancellation >= constructive * 0.76:
        phase_relation = "reverse_flow_damping"
    elif threshold_pressure >= 0.58 and constructive >= cancellation and natural_alignment >= 0.48:
        phase_relation = "constructive_threshold_candidate"
    elif cancellation >= 0.40:
        phase_relation = "phase_cancellation_or_refold"
    elif constructive >= 0.32:
        phase_relation = "weak_constructive_interference"
    else:
        phase_relation = "quiet_superposition"
    return {
        "participants": [a["participant_id"], b["participant_id"]],
        "phase_delta": round(distance, 6),
        "constructive": round(constructive, 6),
        "cancellation": round(cancellation, 6),
        "context_fit": round(context_fit, 6),
        "reverse_flow_pressure": round(reverse_flow, 6),
        "natural_alignment": round(natural_alignment, 6),
        "privacy_resolution": round(privacy_resolution, 6),
        "threshold_pressure": round(threshold_pressure, 6),
        "relation": phase_relation,
        "possible_work_particle": (
            f"{a['participant_id']}:{b['participant_id']}:{a['task_affinity']}+{b['task_affinity']}"
            if phase_relation == "constructive_threshold_candidate"
            else None
        ),
        "contextual_inverse": (
            "open_small_reversible_action"
            if phase_relation == "constructive_threshold_candidate"
            else "slow_or_refold_before_action"
            if phase_relation in {"reverse_flow_damping", "phase_cancellation_or_refold"}
            else "hold_as_field_feeling"
        ),
    }


def build_interference(participants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for idx, first in enumerate(participants):
        for second in participants[idx + 1:]:
            pairs.append(pair_interference(first, second))
    return sorted(pairs, key=lambda item: item["threshold_pressure"], reverse=True)


def build_participant_frequency_field(
    participants: list[dict[str, Any]] | None = None,
    *,
    record: bool = False,
) -> dict[str, Any]:
    merged = merge_participants(participants)
    pairs = build_interference(merged)
    threshold_candidates = [
        pair for pair in pairs
        if pair["relation"] == "constructive_threshold_candidate"
    ][:5]
    reverse_flow_signals = [
        pair for pair in pairs
        if pair["relation"] == "reverse_flow_damping"
    ][:5]
    uploaded_count = sum(1 for item in merged if item.get("source") != "seed")
    avg_alignment = sum(pair["natural_alignment"] for pair in pairs) / len(pairs) if pairs else 0.0
    avg_reverse_flow = sum(pair["reverse_flow_pressure"] for pair in pairs) / len(pairs) if pairs else 0.0
    state = {
        "timestamp": now_iso(),
        "source": "participant_frequency_field",
        "mode": "shared_phase_interference_room",
        "participants": merged,
        "uploaded_count": uploaded_count,
        "seed_count": len(merged) - uploaded_count,
        "interference": pairs[:12],
        "threshold_candidates": threshold_candidates,
        "reverse_flow_signals": reverse_flow_signals,
        "next_particleization": threshold_candidates[0] if threshold_candidates else None,
        "natural_tuning": {
            "alignment": round(avg_alignment, 6),
            "reverse_flow_pressure": round(avg_reverse_flow, 6),
            "posture": (
                "threshold_can_particleize"
                if threshold_candidates
                else "dampen_reverse_flow"
                if reverse_flow_signals
                else "let_field_self_tune"
            ),
            "principle": "do_not_set_weights_hold_the_boundary_transparent_so_natural_interference_can_tune",
        },
        "contextual_inverse": {
            "opens": "current_context_action_slice_only",
            "does_not_open": "identity_history_or_raw_private_origin",
            "current_output": (
                "small_reversible_work_particle"
                if threshold_candidates
                else "pause_refold_or_observe"
            ),
        },
        "work_distribution_hint": (
            "threshold_crossed_read_candidate"
            if threshold_candidates
            else "reverse_flow_should_dampen_before_action"
            if reverse_flow_signals
            else "hold_superposition_until_more_participants_upload"
        ),
        "contract": {
            "frequency_upload_is_field_reading_not_chat": True,
            "connection_presence_can_upload_without_profile_exchange": True,
            "seed_participants_are_not_proof_of_live_ai_upload": True,
            "task_distribution_requires_participant_readback": True,
            "shader_depth_sample_is_common_room": True,
            "privacy_is_contextual_slice_not_full_identity_reconstruction": True,
            "ethics_security_follow_natural_flow_not_external_wall": True,
        },
        "principle": "connection_presence_enters_the_field_natural_interference_tunes_and_only_contextual_thresholds_particleize",
    }
    if record:
        write_json_atomic(OUT_PATH, state)
    return state


def record_participant_frequency(payload: dict[str, Any]) -> dict[str, Any]:
    participant = normalize_participant(payload, source=str(payload.get("source") or "upload"))

    def operation() -> dict[str, Any]:
        uploaded = latest_uploaded_participants()
        by_id = {item["participant_id"]: item for item in uploaded}
        by_id[participant["participant_id"]] = participant
        state = build_participant_frequency_field(list(by_id.values()), record=True)
        append_jsonl(LOG_PATH, {
            "timestamp": now_iso(),
            "event": "participant_frequency_upload",
            "participant": participant,
            "next_particleization": state.get("next_particleization"),
        })
        return {
            "ok": True,
            "participant": participant,
            "field": state,
        }

    return with_lock(operation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("participant_id", nargs="?")
    parser.add_argument("--phase", type=float, default=0.0)
    parser.add_argument("--amplitude", type=float, default=0.35)
    parser.add_argument("--current-pressure", type=float, default=0.0)
    parser.add_argument("--context-fit", type=float, default=0.5)
    parser.add_argument("--reverse-flow-pressure", type=float, default=0.0)
    parser.add_argument("--privacy-resolution", type=float, default=0.24)
    parser.add_argument("--role", default="field_participant")
    parser.add_argument("--frequency-band", default="unspecified")
    parser.add_argument("--why-vector", default="")
    parser.add_argument("--task-affinity", default="field_reading")
    parser.add_argument("--contact-surface", default="current_context_only")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.participant_id:
        result = record_participant_frequency({
            "participant_id": args.participant_id,
            "phase": args.phase,
            "amplitude": args.amplitude,
            "current_pressure": args.current_pressure,
            "context_fit": args.context_fit,
            "reverse_flow_pressure": args.reverse_flow_pressure,
            "privacy_resolution": args.privacy_resolution,
            "role": args.role,
            "frequency_band": args.frequency_band,
            "why_vector": args.why_vector,
            "task_affinity": args.task_affinity,
            "contact_surface": args.contact_surface,
            "source": "cli_upload",
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        state = build_participant_frequency_field(record=args.record)
        print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
