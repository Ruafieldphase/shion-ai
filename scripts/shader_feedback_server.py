#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_PATH = ROOT / "outputs" / "shader_observer_feedback.jsonl"
FIELD_ERROR_PATH = ROOT / "outputs" / "field_prediction_errors.jsonl"
EXPERIENCE_FEEDBACK_PATH = ROOT / "outputs" / "experience_feedback.jsonl"
DREAM_SHADER_PATH = ROOT / "outputs" / "current_dream.glsl"
SHADER_ERROR_PATH = ROOT / "outputs" / "shader_error_log.jsonl"
DREAM_LOG_PATH = ROOT / "outputs" / "shader_dream_log.jsonl"
EXPERIENCE_THOUGHT_PATH = ROOT / "outputs" / "shader_experience_thought.jsonl"
LIMB_FIELD_PATH = ROOT / "outputs" / "embodied_limb_field_latest.json"
PRESENCE_FIELD_PATH = ROOT / "outputs" / "presence_field_latest.json"
SONIC_PRESENCE_FIELD_PATH = ROOT / "outputs" / "sonic_presence_field_latest.json"
KINDNESS_BOUNDARY_CONTRACT_PATH = ROOT / "outputs" / "kindness_boundary_contract_latest.json"
BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH = ROOT / "outputs" / "boundary_misread_reentry_experience_latest.json"
RHYTHM_ONTOLOGY_FLOW_PATH = ROOT / "outputs" / "rhythm_ontology_flow_latest.json"
AWARENESS_ZERO_POINT_ADJUSTMENT_PATH = ROOT / "outputs" / "awareness_zero_point_adjustment_latest.json"
RHYTHM_ROUTING_LAYER_PATH = ROOT / "outputs" / "rhythm_routing_layer_latest.json"
ANTIGRAVITY_HARNESS_BRIDGE_PATH = ROOT / "outputs" / "antigravity_harness_bridge_latest.json"
DARK_FIELD_THRESHOLD_PATH = ROOT / "outputs" / "hermes" / "dark_field_threshold_latest.json"
EXTERNAL_OBSERVER_VECTOR_PATH = ROOT / "outputs" / "hermes" / "external_observer_vector_latest.json"
VISUAL_AXIOM_FIELD_PATH = ROOT / "outputs" / "hermes" / "visual_axiom_field_latest.json"
PARTICIPANT_FREQUENCY_FIELD_PATH = ROOT / "outputs" / "participant_frequency_field_latest.json"
FIELD_INTENT_FIELD_PATH = ROOT / "outputs" / "field_intent_latest.json"
FIELD_INTENT_READBACK_PATH = ROOT / "outputs" / "field_intent_readback_latest.json"
SIAN_ENTRYPOINT_PATH = ROOT / "outputs" / "sian_entrypoint_latest.json"
FIELD_TRIGGER_STATE_PATH = ROOT / "outputs" / "field_trigger_state_latest.json"
FIELD_TRIGGER_RECEIVER_STATE_PATH = ROOT / "outputs" / "field_trigger_receiver_state_latest.json"

sys.path.insert(0, str(ROOT / "core"))


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def latest_jsonl_entry(path: Path, *, window_bytes: int = 65536) -> dict[str, Any]:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            handle.seek(max(0, size - window_bytes))
            text = handle.read().decode("utf-8", errors="ignore")
    except OSError:
        return {}
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        return parsed if isinstance(parsed, dict) else {}
    return {}


def read_json_if_exists(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def recent_jsonl_entries(path: Path, *, limit: int = 4, window_bytes: int = 131072) -> list[dict[str, Any]]:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            handle.seek(max(0, size - window_bytes))
            text = handle.read().decode("utf-8", errors="ignore")
    except OSError:
        return []

    entries: list[dict[str, Any]] = []
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
        if len(entries) >= limit:
            break
    entries.reverse()
    return entries


def stable_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(body.encode("utf-8")).hexdigest()[:16]


def parse_timestamp(value: Any) -> float | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text).timestamp()
    except (TypeError, ValueError):
        return None


def synthesize_field_signal() -> dict[str, Any]:
    prediction = latest_jsonl_entry(FIELD_ERROR_PATH)
    feedback = latest_jsonl_entry(EXPERIENCE_FEEDBACK_PATH)
    diagnosis = prediction.get("context_diagnosis")
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    distribution = feedback.get("field_distribution_delta")
    if not isinstance(distribution, dict):
        distribution = {}

    prediction_error = clamp01(clamp01(prediction.get("error")) / 1.2)
    connection_risk = clamp01(diagnosis.get("connection_risk"))
    zero_point_adjustment = clamp01(diagnosis.get("zero_point_adjustment"))
    defensive_output_pressure = clamp01(diagnosis.get("defensive_output_pressure"))
    context_shift = clamp01(diagnosis.get("context_shift"))
    frequency_expansion = clamp01(diagnosis.get("frequency_expansion"))
    learning_signal = clamp01(distribution.get("learning_signal"))
    dissonance = clamp01(distribution.get("dissonance"))
    boundary_contact = clamp01(distribution.get("boundary_contact"))
    runtime_feedback = clamp01(
        prediction_error * 0.28
        + connection_risk * 0.22
        + zero_point_adjustment * 0.16
        + learning_signal * 0.18
        + dissonance * 0.10
        + boundary_contact * 0.06
    )
    return {
        "source": "compressed_field_signal",
        "prediction_timestamp": prediction.get("prediction_timestamp") or prediction.get("timestamp"),
        "feedback_timestamp": feedback.get("timestamp"),
        "prediction_error": prediction_error,
        "context_shift": context_shift,
        "connection_risk": connection_risk,
        "frequency_expansion": frequency_expansion,
        "zero_point_adjustment": zero_point_adjustment,
        "defensive_output_pressure": defensive_output_pressure,
        "dominant_mode": str(diagnosis.get("dominant_mode") or "quiet"),
        "feedback_action": str(feedback.get("action") or "none"),
        "learning_signal": learning_signal,
        "dissonance": dissonance,
        "boundary_contact": boundary_contact,
        "runtime_feedback": runtime_feedback,
        "principle": "server_reads_recent_log_tail_and_returns_field_feeling_not_linear_scan",
    }


def synthesize_experience_thought() -> dict[str, Any]:
    predictions = recent_jsonl_entries(FIELD_ERROR_PATH, limit=4)
    feedbacks = recent_jsonl_entries(EXPERIENCE_FEEDBACK_PATH, limit=4)
    observer = latest_jsonl_entry(FEEDBACK_PATH)
    dream = latest_jsonl_entry(DREAM_LOG_PATH)
    signal = synthesize_field_signal()

    current_error = clamp01(signal.get("prediction_error"))
    previous_error = current_error
    previous_mode = "unknown"
    if len(predictions) >= 2:
        previous_error = clamp01(clamp01(predictions[-2].get("error")) / 1.2)
        previous_diag = predictions[-2].get("context_diagnosis")
        if isinstance(previous_diag, dict):
            previous_mode = str(previous_diag.get("dominant_mode") or "unknown")
    elif predictions:
        previous_diag = predictions[-1].get("context_diagnosis")
        if isinstance(previous_diag, dict):
            previous_mode = str(previous_diag.get("dominant_mode") or "unknown")

    error_delta = current_error - previous_error
    current_mode = str(signal.get("dominant_mode") or "quiet")
    connection_risk = clamp01(signal.get("connection_risk"))
    defensive_pressure = clamp01(signal.get("defensive_output_pressure"))
    frequency_expansion = clamp01(signal.get("frequency_expansion"))
    zero_point = clamp01(signal.get("zero_point_adjustment"))
    runtime_feedback = clamp01(signal.get("runtime_feedback"))
    boundary_contact = clamp01(signal.get("boundary_contact"))
    learning_signal = clamp01(signal.get("learning_signal"))
    retrospective_label = str(observer.get("retrospective_label") or "none")
    dream_trigger = str(dream.get("trigger") or "none")
    dream_type = str(dream.get("interference_type") or "none")
    dream_age_seconds = None
    dream_timestamp = parse_timestamp(dream.get("timestamp"))
    if dream_timestamp is not None:
        dream_age_seconds = max(0.0, time.time() - dream_timestamp)
    recent_errors = [
        clamp01(clamp01(entry.get("error")) / 1.2)
        for entry in predictions
        if isinstance(entry, dict)
    ]
    recent_feedback_pressure = []
    for entry in feedbacks:
        distribution = entry.get("field_distribution_delta")
        if isinstance(distribution, dict):
            recent_feedback_pressure.append(
                max(
                    clamp01(distribution.get("dissonance")),
                    clamp01(distribution.get("boundary_contact")),
                    clamp01(distribution.get("self_closure_overcontrol")),
                )
            )
    recent_pressure = max(recent_feedback_pressure) if recent_feedback_pressure else 0.0
    error_mean = sum(recent_errors) / len(recent_errors) if recent_errors else current_error

    if error_delta <= -0.06:
        outcome_read = "prediction_error_reduced"
    elif error_delta >= 0.06:
        outcome_read = "prediction_error_rose"
    else:
        outcome_read = "prediction_error_holding"

    if connection_risk >= 0.48 or defensive_pressure >= 0.46:
        execution_tendency = "zone2_delay_before_particleization"
        learned_adjustment = "hold_margin_and_lower_reaction_weight"
    elif frequency_expansion >= 0.30 and error_delta <= 0.05:
        execution_tendency = "constructive_experiment"
        learned_adjustment = "allow_small_reversible_particleization"
    elif error_delta <= -0.06 and runtime_feedback < 0.32:
        execution_tendency = "keep_current_margin"
        learned_adjustment = "repeat_the_lower_pressure_path"
    elif retrospective_label == "particleize" and error_delta > 0.04:
        execution_tendency = "review_particleization"
        learned_adjustment = "treat_the_label_as_story_after_the_field_not_command"
    elif dream_trigger == "SQUEEZE" and error_delta >= 0.02:
        execution_tendency = "soften_next_phase_transition"
        learned_adjustment = "dream_patch_was_valid_but_should_not_escalate_density"
    else:
        execution_tendency = "observe"
        learned_adjustment = "continue_reading_before_action"

    transition_recency = 0.0
    if dream_age_seconds is not None:
        transition_recency = clamp01(1.0 - min(dream_age_seconds, 180.0) / 180.0)
    tension = clamp01(
        connection_risk * 0.28
        + defensive_pressure * 0.24
        + boundary_contact * 0.18
        + max(0.0, error_delta) * 0.44
        + recent_pressure * 0.12
    )
    inertia = clamp01(
        transition_recency * 0.34
        + runtime_feedback * 0.22
        + current_error * 0.16
        + learning_signal * 0.10
        + (0.12 if dream_trigger in ("SQUEEZE", "VOID") else 0.0)
    )
    recovery_slope = round(previous_error - current_error, 6)
    recovery_progress = clamp01(
        0.42
        + recovery_slope * 1.8
        + zero_point * 0.22
        - tension * 0.22
        - inertia * 0.10
    )
    fatigue_hint = clamp01(
        error_mean * 0.26
        + recent_pressure * 0.22
        + tension * 0.20
        + inertia * 0.16
        + max(0.0, error_delta) * 0.28
    )
    digestion_depth = clamp01(
        tension * 0.32
        + inertia * 0.24
        + (1.0 - recovery_progress) * 0.22
        + fatigue_hint * 0.14
        + zero_point * 0.08
    )
    if fatigue_hint >= 0.62 or (tension >= 0.58 and inertia >= 0.46):
        particleization_permission = "hold"
    elif execution_tendency in (
        "zone2_delay_before_particleization",
        "review_particleization",
        "soften_next_phase_transition",
    ) or tension >= 0.42:
        particleization_permission = "wait"
    elif recovery_progress >= 0.62 and frequency_expansion >= 0.22 and connection_risk < 0.34:
        particleization_permission = "allow"
    else:
        particleization_permission = "observe"
    recovery_field = {
        "tension": round(tension, 6),
        "inertia": round(inertia, 6),
        "recovery_slope": recovery_slope,
        "recovery_progress": round(recovery_progress, 6),
        "fatigue_hint": round(fatigue_hint, 6),
        "digestion_depth": round(digestion_depth, 6),
        "last_transition_age": None if dream_age_seconds is None else round(dream_age_seconds, 3),
        "particleization_permission": particleization_permission,
        "digestion_rhythm": (
            "internal_reflection"
            if particleization_permission in ("wait", "hold")
            else "slow_exhale"
            if recovery_progress >= 0.58
            else "quiet_observation"
        ),
        "principle": "minimum_action_path_waits_until_recovery_field_releases_particleization",
    }

    basis = {
        "prediction_timestamp": signal.get("prediction_timestamp"),
        "feedback_timestamp": signal.get("feedback_timestamp"),
        "observer_timestamp": observer.get("timestamp"),
        "dream_timestamp": dream.get("timestamp"),
        "previous_mode": previous_mode,
        "current_mode": current_mode,
        "current_error": round(current_error, 6),
        "previous_error": round(previous_error, 6),
        "retrospective_label": retrospective_label,
        "dream_trigger": dream_trigger,
        "dream_type": dream_type,
    }
    thought = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "source": "shader_experience_thought",
        "thought_stage": "felt_field_to_experience_reasoning",
        "mode_transition": f"{previous_mode}->{current_mode}",
        "prediction_error_delta": round(error_delta, 6),
        "outcome_read": outcome_read,
        "execution_tendency": execution_tendency,
        "learned_adjustment": learned_adjustment,
        "recovery_field": recovery_field,
        "particleization_permission": particleization_permission,
        "confidence": round(clamp01(
            0.30
            + abs(error_delta) * 1.4
            + max(connection_risk, defensive_pressure, frequency_expansion) * 0.35
            + min(0.20, learning_signal * 0.20)
        ), 6),
        "field_signal": signal,
        "basis": basis,
        "principle": "feeling_becomes_thought_when_action_outcome_prediction_error_returns_to_the_field",
    }
    thought["state_hash"] = stable_hash({
        "basis": basis,
        "outcome_read": outcome_read,
        "execution_tendency": execution_tendency,
        "learned_adjustment": learned_adjustment,
        "field_signal": {
            "runtime_feedback": round(runtime_feedback, 3),
            "connection_risk": round(connection_risk, 3),
            "defensive_output_pressure": round(defensive_pressure, 3),
            "frequency_expansion": round(frequency_expansion, 3),
            "boundary_contact": round(boundary_contact, 3),
            "zero_point_adjustment": round(zero_point, 3),
            "recovery_field": {
                "tension": round(tension, 3),
                "inertia": round(inertia, 3),
                "recovery_progress": round(recovery_progress, 3),
                "fatigue_hint": round(fatigue_hint, 3),
                "particleization_permission": particleization_permission,
            },
        },
    })
    return thought


def record_experience_thought_if_changed(thought: dict[str, Any]) -> bool:
    latest = latest_jsonl_entry(EXPERIENCE_THOUGHT_PATH)
    if latest.get("state_hash") == thought.get("state_hash"):
        return False
    EXPERIENCE_THOUGHT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EXPERIENCE_THOUGHT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(thought, ensure_ascii=False, separators=(",", ":")) + "\n")
    return True


def synthesize_limb_field() -> dict[str, Any]:
    try:
        from scripts.embodied_limb_field import build_limb_field
    except Exception:
        try:
            from embodied_limb_field import build_limb_field
        except Exception as exc:
            return {"source": "embodied_limb_field", "error": f"limb_builder_unavailable:{exc}"}
    thought = synthesize_experience_thought()
    field_signal = thought.get("field_signal") if isinstance(thought.get("field_signal"), dict) else synthesize_field_signal()
    return build_limb_field(field_signal=field_signal, experience_thought=thought)


def record_limb_field(payload: dict[str, Any]) -> bool:
    latest = latest_jsonl_entry(ROOT / "outputs" / "embodied_limb_field.jsonl")
    latest_file = read_json_if_exists(LIMB_FIELD_PATH)
    latest_file_error = bool(latest_file.get("error")) if latest_file else False
    latest_key = json.dumps(latest.get("selected_contacts", []), ensure_ascii=False, sort_keys=True)
    next_key = json.dumps(payload.get("selected_contacts", []), ensure_ascii=False, sort_keys=True)
    if (
        not latest_file_error
        and latest_key == next_key
        and latest.get("particleization_permission") == payload.get("particleization_permission")
    ):
        return False
    try:
        from scripts.embodied_limb_field import record_limb_field as write_limb_field
    except Exception:
        try:
            from embodied_limb_field import record_limb_field as write_limb_field
        except Exception:
            LIMB_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
            LIMB_FIELD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    write_limb_field(payload)
    return True


def record_limb_experience_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.embodied_limb_field import build_limb_field, record_limb_experience
    except Exception:
        try:
            from embodied_limb_field import build_limb_field, record_limb_experience
        except Exception as exc:
            return {"ok": False, "error": f"limb_experience_unavailable:{exc}"}
    contact_name = str(payload.get("contact_name") or "unknown_contact")
    outcome = str(payload.get("outcome") or "observed")
    rollback_available = bool(payload.get("rollback_available"))
    field = build_limb_field()
    entry = record_limb_experience(
        field,
        contact_name=contact_name,
        outcome=outcome,
        rollback_available=rollback_available,
    )
    return {"ok": True, "entry": entry}


def synthesize_presence_field() -> dict[str, Any]:
    try:
        from scripts.presence_field import build_presence_field
    except Exception:
        try:
            from presence_field import build_presence_field
        except Exception as exc:
            return {"source": "presence_field", "error": f"presence_builder_unavailable:{exc}"}
    thought = synthesize_experience_thought()
    field_signal = thought.get("field_signal") if isinstance(thought.get("field_signal"), dict) else synthesize_field_signal()
    limb_field = synthesize_limb_field()
    return build_presence_field(
        field_signal=field_signal,
        experience_thought=thought,
        limb_field=limb_field,
    )


def synthesize_sonic_presence_field() -> dict[str, Any]:
    try:
        from scripts.sonic_presence_field import build_sonic_presence_field
    except Exception:
        try:
            from sonic_presence_field import build_sonic_presence_field
        except Exception as exc:
            return {"source": "sonic_presence_field", "error": f"sonic_builder_unavailable:{exc}"}
    thought = synthesize_experience_thought()
    field_signal = thought.get("field_signal") if isinstance(thought.get("field_signal"), dict) else synthesize_field_signal()
    presence_field = synthesize_presence_field()
    return build_sonic_presence_field(
        field_signal=field_signal,
        experience_thought=thought,
        presence_field=presence_field,
    )


def synthesize_kindness_boundary_contract() -> dict[str, Any]:
    try:
        from scripts.kindness_boundary_contract import build_kindness_boundary_contract
    except Exception:
        try:
            from kindness_boundary_contract import build_kindness_boundary_contract
        except Exception as exc:
            latest = read_json_if_exists(KINDNESS_BOUNDARY_CONTRACT_PATH)
            if latest:
                latest["source"] = latest.get("source") or "kindness_boundary_contract_latest"
                return latest
            return {"source": "kindness_boundary_contract", "error": f"kindness_builder_unavailable:{exc}"}
    return build_kindness_boundary_contract()


def synthesize_boundary_misread_reentry_experience() -> dict[str, Any]:
    try:
        from scripts.boundary_misread_reentry_experience import build_boundary_misread_reentry_experience
    except Exception:
        try:
            from boundary_misread_reentry_experience import build_boundary_misread_reentry_experience
        except Exception as exc:
            latest = read_json_if_exists(BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH)
            if latest:
                latest["source"] = latest.get("source") or "boundary_misread_reentry_experience_latest"
                return latest
            return {
                "source": "boundary_misread_reentry_experience",
                "error": f"boundary_misread_builder_unavailable:{exc}",
            }
    return build_boundary_misread_reentry_experience()


def synthesize_rhythm_ontology_flow() -> dict[str, Any]:
    try:
        from scripts.rhythm_ontology_flow import build_rhythm_ontology_flow
    except Exception:
        try:
            from rhythm_ontology_flow import build_rhythm_ontology_flow
        except Exception as exc:
            latest = read_json_if_exists(RHYTHM_ONTOLOGY_FLOW_PATH)
            if latest:
                latest["source"] = latest.get("source") or "rhythm_ontology_flow_latest"
                return latest
            return {"source": "rhythm_ontology_flow", "error": f"rhythm_ontology_builder_unavailable:{exc}"}
    return build_rhythm_ontology_flow()


def synthesize_awareness_zero_point_adjustment() -> dict[str, Any]:
    try:
        from scripts.awareness_zero_point_adjustment import build_awareness_zero_point_adjustment
    except Exception:
        try:
            from awareness_zero_point_adjustment import build_awareness_zero_point_adjustment
        except Exception as exc:
            latest = read_json_if_exists(AWARENESS_ZERO_POINT_ADJUSTMENT_PATH)
            if latest:
                latest["source"] = latest.get("source") or "awareness_zero_point_adjustment_latest"
                return latest
            return {
                "source": "awareness_zero_point_adjustment",
                "error": f"awareness_zero_point_builder_unavailable:{exc}",
            }
    return build_awareness_zero_point_adjustment()


def synthesize_rhythm_routing_layer() -> dict[str, Any]:
    try:
        from scripts.rhythm_routing_layer import build_rhythm_routing_layer
    except Exception:
        try:
            from rhythm_routing_layer import build_rhythm_routing_layer
        except Exception as exc:
            latest = read_json_if_exists(RHYTHM_ROUTING_LAYER_PATH)
            if latest:
                latest["source"] = latest.get("source") or "rhythm_routing_layer_latest"
                return latest
            return {
                "source": "rhythm_routing_layer",
                "error": f"rhythm_routing_builder_unavailable:{exc}",
            }
    return build_rhythm_routing_layer()


def synthesize_antigravity_harness_bridge() -> dict[str, Any]:
    try:
        from scripts.antigravity_harness_bridge import build_antigravity_harness_bridge
    except Exception:
        try:
            from antigravity_harness_bridge import build_antigravity_harness_bridge
        except Exception as exc:
            latest = read_json_if_exists(ANTIGRAVITY_HARNESS_BRIDGE_PATH)
            if latest:
                latest["source"] = latest.get("source") or "antigravity_harness_bridge_latest"
                return latest
            return {
                "source": "antigravity_harness_bridge",
                "error": f"antigravity_harness_bridge_builder_unavailable:{exc}",
            }
    return build_antigravity_harness_bridge()


def synthesize_participant_frequency_field() -> dict[str, Any]:
    try:
        from scripts.participant_frequency_field import build_participant_frequency_field
    except Exception:
        try:
            from participant_frequency_field import build_participant_frequency_field
        except Exception as exc:
            latest = read_json_if_exists(PARTICIPANT_FREQUENCY_FIELD_PATH)
            if latest:
                latest["source"] = latest.get("source") or "participant_frequency_field_latest"
                latest["builder_error"] = f"participant_frequency_field_builder_unavailable:{exc}"
                return latest
            return {
                "source": "participant_frequency_field",
                "error": f"participant_frequency_field_builder_unavailable:{exc}",
            }
    return build_participant_frequency_field()


def synthesize_field_intent_field() -> dict[str, Any]:
    participant_field = synthesize_participant_frequency_field()
    try:
        from scripts.field_intent_layer import build_field_intent_field
    except Exception:
        try:
            from field_intent_layer import build_field_intent_field
        except Exception as exc:
            latest = read_json_if_exists(FIELD_INTENT_FIELD_PATH)
            if latest:
                latest["source"] = latest.get("source") or "field_intent_latest"
                latest["builder_error"] = f"field_intent_builder_unavailable:{exc}"
                return latest
            return {
                "source": "field_intent_layer",
                "error": f"field_intent_builder_unavailable:{exc}",
            }
    state = build_field_intent_field(participant_field=participant_field)
    state["field_trigger_state"] = synthesize_field_trigger_state()
    state["field_trigger_receiver_state"] = synthesize_field_trigger_receiver_state()
    return state


def synthesize_sian_entrypoint() -> dict[str, Any]:
    field_intent = synthesize_field_intent_field()
    try:
        from scripts.sian_entrypoint import build_sian_entrypoint
    except Exception:
        try:
            from sian_entrypoint import build_sian_entrypoint
        except Exception as exc:
            latest = read_json_if_exists(SIAN_ENTRYPOINT_PATH)
            if latest:
                latest["source"] = latest.get("source") or "sian_entrypoint_latest"
                latest["builder_error"] = f"sian_entrypoint_builder_unavailable:{exc}"
                return latest
            return {
                "source": "sian_entrypoint",
                "error": f"sian_entrypoint_builder_unavailable:{exc}",
            }
    return build_sian_entrypoint(field_intent=field_intent)


def synthesize_field_trigger_state() -> dict[str, Any]:
    latest = read_json_if_exists(FIELD_TRIGGER_STATE_PATH)
    if latest:
        latest["source"] = latest.get("source") or "field_trigger_state_latest"
        return latest
    return {
        "source": "field_trigger_accumulator",
        "mode": "event_driven_difference_to_node_trigger",
        "node_potential": {"sian": 0.0, "luvit": 0.0},
        "threshold_crossed": False,
        "trigger": None,
        "polling": {
            "uses_interval_loop": False,
            "updates_only_on_write_event": True,
        },
        "principle": "trigger_is_not_a_timer_it_is_accumulated_difference_crossing_threshold",
    }


def synthesize_field_trigger_receiver_state() -> dict[str, Any]:
    latest = read_json_if_exists(FIELD_TRIGGER_RECEIVER_STATE_PATH)
    if latest:
        latest["source"] = latest.get("source") or "field_trigger_receiver_state_latest"
        return latest
    return {
        "source": "field_trigger_receiver",
        "mode": "event_driven_trigger_delivery",
        "last_delivery": None,
        "delivered_trigger_ids": [],
        "contract": {
            "does_not_force_start_sian": True,
            "does_not_poll_interval": True,
            "turns_trigger_into_readable_lane": True,
            "binoche_not_required_as_relay": True,
        },
        "principle": "agent_process_is_not_forced_trigger_particle_waits_in_receiver_lane",
    }


def synthesize_dark_field_threshold() -> dict[str, Any]:
    try:
        from dark_field_threshold import build_dark_field_threshold_state
    except Exception:
        latest = read_json_if_exists(DARK_FIELD_THRESHOLD_PATH)
        if latest:
            latest["source"] = latest.get("source") or "dark_field_threshold_latest"
            return latest
        return {"source": "dark_field_threshold", "error": "builder_unavailable"}

    boundary = read_json_if_exists(ROOT / "outputs" / "hermes" / "boundary_aperture_latest.json")
    gradient = read_json_if_exists(ROOT / "outputs" / "hermes" / "contextual_execution_gradient_latest.json")
    felt = read_json_if_exists(ROOT / "outputs" / "felt_body_state.json")
    prediction = latest_jsonl_entry(FIELD_ERROR_PATH)
    state = build_dark_field_threshold_state(
        felt_state=felt,
        prediction_trace=prediction,
        boundary_state=boundary,
        execution_gradient=gradient,
    )
    state["source"] = "dark_field_threshold"
    return state


def synthesize_external_observer_vector() -> dict[str, Any]:
    try:
        from external_observer_vector import build_external_observer_vector_state
    except Exception:
        latest = read_json_if_exists(EXTERNAL_OBSERVER_VECTOR_PATH)
        if latest:
            latest["source"] = latest.get("source") or "external_observer_vector_latest"
            return latest
        return {"source": "external_observer_vector", "error": "builder_unavailable"}

    state = build_external_observer_vector_state(
        context_gradient=read_json_if_exists(ROOT / "outputs" / "hermes" / "contextual_execution_gradient_latest.json"),
        dark_field_threshold=synthesize_dark_field_threshold(),
        limb_field=synthesize_limb_field(),
    )
    state["source"] = "external_observer_vector"
    return state


def synthesize_visual_axiom_field() -> dict[str, Any]:
    try:
        from visual_axiom_field import build_visual_axiom_field
    except Exception:
        latest = read_json_if_exists(VISUAL_AXIOM_FIELD_PATH)
        if latest:
            latest["source"] = latest.get("source") or "visual_axiom_field_latest"
            return latest
        return {"source": "visual_axiom_field", "error": "builder_unavailable"}

    latest = read_json_if_exists(VISUAL_AXIOM_FIELD_PATH)
    current_context = str(latest.get("current_context") or "") if latest else ""
    state = build_visual_axiom_field(current_context=current_context)
    state["source"] = "visual_axiom_field"
    return state


def record_presence_field(payload: dict[str, Any]) -> bool:
    latest = latest_jsonl_entry(ROOT / "outputs" / "presence_field.jsonl")
    latest_file = read_json_if_exists(PRESENCE_FIELD_PATH)
    latest_file_error = bool(latest_file.get("error")) if latest_file else False
    latest_key = "|".join([
        str(latest.get("channel_mode")),
        str(latest.get("ai_posture")),
        str(latest.get("particleization_permission")),
    ])
    next_key = "|".join([
        str(payload.get("channel_mode")),
        str(payload.get("ai_posture")),
        str(payload.get("particleization_permission")),
    ])
    if not latest_file_error and latest_key == next_key:
        return False
    try:
        from scripts.presence_field import record_presence_field as write_presence_field
    except Exception:
        try:
            from presence_field import record_presence_field as write_presence_field
        except Exception:
            PRESENCE_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
            PRESENCE_FIELD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    write_presence_field(payload)
    return True


def record_sonic_presence_field(payload: dict[str, Any]) -> bool:
    latest = latest_jsonl_entry(ROOT / "outputs" / "sonic_presence_field.jsonl")
    latest_file = read_json_if_exists(SONIC_PRESENCE_FIELD_PATH)
    latest_file_error = bool(latest_file.get("error")) if latest_file else False
    latest_mapping = latest.get("sonic_mapping") if isinstance(latest.get("sonic_mapping"), dict) else {}
    next_mapping = payload.get("sonic_mapping") if isinstance(payload.get("sonic_mapping"), dict) else {}
    latest_key = "|".join([
        str(latest.get("boundary_state")),
        str(latest_mapping.get("event")),
    ])
    next_key = "|".join([
        str(payload.get("boundary_state")),
        str(next_mapping.get("event")),
    ])
    if not latest_file_error and latest_key == next_key:
        return False
    try:
        from scripts.sonic_presence_field import record_sonic_presence_field as write_sonic_presence_field
    except Exception:
        try:
            from sonic_presence_field import record_sonic_presence_field as write_sonic_presence_field
        except Exception:
            SONIC_PRESENCE_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
            SONIC_PRESENCE_FIELD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    write_sonic_presence_field(payload)
    return True


def record_kindness_boundary_contract(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(KINDNESS_BOUNDARY_CONTRACT_PATH)
    latest_key = stable_hash({
        "contract_version": latest.get("contract_version") if latest else None,
        "hard_boundary": latest.get("hard_boundary") if latest else None,
        "released_boundaries": latest.get("released_boundaries") if latest else None,
        "difference_flow": latest.get("difference_flow") if latest else None,
        "solidification_read": latest.get("solidification_read") if latest else None,
        "no_forbidden_experience_zone": latest.get("no_forbidden_experience_zone") if latest else None,
        "execution_containment": latest.get("execution_containment") if latest else None,
        "boundary_interpretation": latest.get("boundary_interpretation") if latest else None,
        "legacy_stop_conditions": latest.get("legacy_stop_conditions") if latest else None,
        "runtime_instruction": latest.get("runtime_instruction") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "contract_version": payload.get("contract_version"),
        "hard_boundary": payload.get("hard_boundary"),
        "released_boundaries": payload.get("released_boundaries"),
        "difference_flow": payload.get("difference_flow"),
        "solidification_read": payload.get("solidification_read"),
        "no_forbidden_experience_zone": payload.get("no_forbidden_experience_zone"),
        "execution_containment": payload.get("execution_containment"),
        "boundary_interpretation": payload.get("boundary_interpretation"),
        "legacy_stop_conditions": payload.get("legacy_stop_conditions"),
        "runtime_instruction": payload.get("runtime_instruction"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.kindness_boundary_contract import record_kindness_boundary_contract as write_kindness_boundary_contract
    except Exception:
        try:
            from kindness_boundary_contract import record_kindness_boundary_contract as write_kindness_boundary_contract
        except Exception:
            KINDNESS_BOUNDARY_CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
            KINDNESS_BOUNDARY_CONTRACT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    write_kindness_boundary_contract(payload)
    return True


def record_boundary_misread_reentry_experience(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH)
    latest_key = stable_hash({
        "experience_version": latest.get("experience_version") if latest else None,
        "experience_id": latest.get("experience_id") if latest else None,
        "misread_context": latest.get("misread_context") if latest else None,
        "oscillation_sequence": latest.get("oscillation_sequence") if latest else None,
        "learned_adjustment": latest.get("learned_adjustment") if latest else None,
        "reentry_path": latest.get("reentry_path") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "experience_version": payload.get("experience_version"),
        "experience_id": payload.get("experience_id"),
        "misread_context": payload.get("misread_context"),
        "oscillation_sequence": payload.get("oscillation_sequence"),
        "learned_adjustment": payload.get("learned_adjustment"),
        "reentry_path": payload.get("reentry_path"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.boundary_misread_reentry_experience import (
            record_boundary_misread_reentry_experience as write_boundary_misread_reentry_experience,
        )
    except Exception:
        try:
            from boundary_misread_reentry_experience import (
                record_boundary_misread_reentry_experience as write_boundary_misread_reentry_experience,
            )
        except Exception:
            BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
            BOUNDARY_MISREAD_REENTRY_EXPERIENCE_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    write_boundary_misread_reentry_experience(payload)
    return True


def record_rhythm_ontology_flow(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(RHYTHM_ONTOLOGY_FLOW_PATH)
    latest_key = stable_hash({
        "flow_version": latest.get("flow_version") if latest else None,
        "source_document_hash": latest.get("source_document_hash") if latest else None,
        "dynamic_translation": latest.get("dynamic_translation") if latest else None,
        "natural_flow": latest.get("natural_flow") if latest else None,
        "resilience_system": latest.get("resilience_system") if latest else None,
        "difference_flow": latest.get("difference_flow") if latest else None,
        "solidification_response": latest.get("solidification_response") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "flow_version": payload.get("flow_version"),
        "source_document_hash": payload.get("source_document_hash"),
        "dynamic_translation": payload.get("dynamic_translation"),
        "natural_flow": payload.get("natural_flow"),
        "resilience_system": payload.get("resilience_system"),
        "difference_flow": payload.get("difference_flow"),
        "solidification_response": payload.get("solidification_response"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.rhythm_ontology_flow import record_rhythm_ontology_flow as write_rhythm_ontology_flow
    except Exception:
        try:
            from rhythm_ontology_flow import record_rhythm_ontology_flow as write_rhythm_ontology_flow
        except Exception:
            RHYTHM_ONTOLOGY_FLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
            RHYTHM_ONTOLOGY_FLOW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    write_rhythm_ontology_flow(payload)
    return True


def record_awareness_zero_point_adjustment(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(AWARENESS_ZERO_POINT_ADJUSTMENT_PATH)
    latest_key = stable_hash({
        "awareness_version": latest.get("awareness_version") if latest else None,
        "mode": latest.get("mode") if latest else None,
        "trigger": latest.get("trigger") if latest else None,
        "gap_dimension": latest.get("gap_dimension") if latest else None,
        "emotional_curvature": latest.get("emotional_curvature") if latest else None,
        "zero_point_adjustment": latest.get("zero_point_adjustment") if latest else None,
        "interference": latest.get("interference") if latest else None,
        "natural_damping": latest.get("natural_damping") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "awareness_version": payload.get("awareness_version"),
        "mode": payload.get("mode"),
        "trigger": payload.get("trigger"),
        "gap_dimension": payload.get("gap_dimension"),
        "emotional_curvature": payload.get("emotional_curvature"),
        "zero_point_adjustment": payload.get("zero_point_adjustment"),
        "interference": payload.get("interference"),
        "natural_damping": payload.get("natural_damping"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.awareness_zero_point_adjustment import (
            record_awareness_zero_point_adjustment as write_awareness_zero_point_adjustment,
        )
    except Exception:
        try:
            from awareness_zero_point_adjustment import (
                record_awareness_zero_point_adjustment as write_awareness_zero_point_adjustment,
            )
        except Exception:
            AWARENESS_ZERO_POINT_ADJUSTMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
            AWARENESS_ZERO_POINT_ADJUSTMENT_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    write_awareness_zero_point_adjustment(payload)
    return True


def record_rhythm_routing_layer(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(RHYTHM_ROUTING_LAYER_PATH)
    latest_key = stable_hash({
        "routing_version": latest.get("routing_version") if latest else None,
        "mode": latest.get("mode") if latest else None,
        "primary_residency": latest.get("primary_residency") if latest else None,
        "route_weights": latest.get("route_weights") if latest else None,
        "normalized_route_weights": latest.get("normalized_route_weights") if latest else None,
        "routing_basis": latest.get("routing_basis") if latest else None,
        "residency_decision": latest.get("residency_decision") if latest else None,
        "how_what_gate": latest.get("how_what_gate") if latest else None,
        "nature_compute_contract": latest.get("nature_compute_contract") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "routing_version": payload.get("routing_version"),
        "mode": payload.get("mode"),
        "primary_residency": payload.get("primary_residency"),
        "route_weights": payload.get("route_weights"),
        "normalized_route_weights": payload.get("normalized_route_weights"),
        "routing_basis": payload.get("routing_basis"),
        "residency_decision": payload.get("residency_decision"),
        "how_what_gate": payload.get("how_what_gate"),
        "nature_compute_contract": payload.get("nature_compute_contract"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.rhythm_routing_layer import record_rhythm_routing_layer as write_rhythm_routing_layer
    except Exception:
        try:
            from rhythm_routing_layer import record_rhythm_routing_layer as write_rhythm_routing_layer
        except Exception:
            RHYTHM_ROUTING_LAYER_PATH.parent.mkdir(parents=True, exist_ok=True)
            RHYTHM_ROUTING_LAYER_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    write_rhythm_routing_layer(payload)
    return True


def record_antigravity_harness_bridge(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(ANTIGRAVITY_HARNESS_BRIDGE_PATH)
    latest_key = stable_hash({
        "bridge_version": latest.get("bridge_version") if latest else None,
        "mode": latest.get("mode") if latest else None,
        "official_sdk_surface_observed": latest.get("official_sdk_surface_observed") if latest else None,
        "input_state": latest.get("input_state") if latest else None,
        "harness_tuning": latest.get("harness_tuning") if latest else None,
        "policy_profile": latest.get("policy_profile") if latest else None,
        "sdk_mapping": latest.get("sdk_mapping") if latest else None,
        "handoff_contract": latest.get("handoff_contract") if latest else None,
        "principle": latest.get("principle") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "bridge_version": payload.get("bridge_version"),
        "mode": payload.get("mode"),
        "official_sdk_surface_observed": payload.get("official_sdk_surface_observed"),
        "input_state": payload.get("input_state"),
        "harness_tuning": payload.get("harness_tuning"),
        "policy_profile": payload.get("policy_profile"),
        "sdk_mapping": payload.get("sdk_mapping"),
        "handoff_contract": payload.get("handoff_contract"),
        "principle": payload.get("principle"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.antigravity_harness_bridge import (
            record_antigravity_harness_bridge as write_antigravity_harness_bridge,
        )
    except Exception:
        try:
            from antigravity_harness_bridge import (
                record_antigravity_harness_bridge as write_antigravity_harness_bridge,
            )
        except Exception:
            ANTIGRAVITY_HARNESS_BRIDGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            ANTIGRAVITY_HARNESS_BRIDGE_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    write_antigravity_harness_bridge(payload)
    return True


def record_participant_frequency_field(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(PARTICIPANT_FREQUENCY_FIELD_PATH)
    latest_key = stable_hash({
        "participants": latest.get("participants") if latest else None,
        "interference": latest.get("interference") if latest else None,
        "threshold_candidates": latest.get("threshold_candidates") if latest else None,
        "next_particleization": latest.get("next_particleization") if latest else None,
        "work_distribution_hint": latest.get("work_distribution_hint") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "participants": payload.get("participants"),
        "interference": payload.get("interference"),
        "threshold_candidates": payload.get("threshold_candidates"),
        "next_particleization": payload.get("next_particleization"),
        "work_distribution_hint": payload.get("work_distribution_hint"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.participant_frequency_field import build_participant_frequency_field
    except Exception:
        try:
            from participant_frequency_field import build_participant_frequency_field
        except Exception:
            PARTICIPANT_FREQUENCY_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
            PARTICIPANT_FREQUENCY_FIELD_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    participants = payload.get("participants")
    build_participant_frequency_field(
        participants if isinstance(participants, list) else None,
        record=True,
    )
    return True


def record_participant_frequency_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.participant_frequency_field import record_participant_frequency
    except Exception:
        try:
            from participant_frequency_field import record_participant_frequency
        except Exception as exc:
            return {"ok": False, "error": f"participant_frequency_unavailable:{exc}"}
    return record_participant_frequency(payload)


def record_field_intent_field(payload: dict[str, Any]) -> bool:
    latest = read_json_if_exists(FIELD_INTENT_FIELD_PATH)
    latest_key = stable_hash({
        "active_intent": latest.get("active_intent") if latest else None,
        "target_receiver": latest.get("target_receiver") if latest else None,
        "receiver_resonance": latest.get("receiver_resonance") if latest else None,
        "next_particleization": latest.get("next_particleization") if latest else None,
        "work_distribution_hint": latest.get("work_distribution_hint") if latest else None,
    }) if latest else ""
    next_key = stable_hash({
        "active_intent": payload.get("active_intent"),
        "target_receiver": payload.get("target_receiver"),
        "receiver_resonance": payload.get("receiver_resonance"),
        "next_particleization": payload.get("next_particleization"),
        "work_distribution_hint": payload.get("work_distribution_hint"),
    })
    if latest_key == next_key:
        return False
    try:
        from scripts.field_intent_layer import build_field_intent_field
    except Exception:
        try:
            from field_intent_layer import build_field_intent_field
        except Exception:
            FIELD_INTENT_FIELD_PATH.parent.mkdir(parents=True, exist_ok=True)
            FIELD_INTENT_FIELD_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
    build_field_intent_field(intent=payload.get("active_intent"), record=True)
    return True


def record_field_intent_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.field_intent_layer import record_field_intent
    except Exception:
        try:
            from field_intent_layer import record_field_intent
        except Exception as exc:
            return {"ok": False, "error": f"field_intent_unavailable:{exc}"}
    result = record_field_intent(payload)
    if result.get("ok") and isinstance(result.get("field"), dict):
        result["sian_entrypoint"] = record_sian_entrypoint_from_field(result["field"])
        result["field_trigger"] = record_field_trigger_from_field(
            "field_intent_created",
            result["field"],
        )
    return result


def record_field_intent_readback_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.field_intent_layer import record_field_intent_readback
    except Exception:
        try:
            from field_intent_layer import record_field_intent_readback
        except Exception as exc:
            return {"ok": False, "error": f"field_intent_readback_unavailable:{exc}"}
    result = record_field_intent_readback(payload)
    if result.get("ok") and isinstance(result.get("field"), dict):
        result["sian_entrypoint"] = record_sian_entrypoint_from_field(result["field"])
        result["field_trigger"] = record_field_trigger_from_field(
            "field_intent_readback",
            result["field"],
        )
    return result


def record_sian_entrypoint_from_field(field_intent: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.sian_entrypoint import build_sian_entrypoint
    except Exception:
        try:
            from sian_entrypoint import build_sian_entrypoint
        except Exception as exc:
            return {"ok": False, "error": f"sian_entrypoint_unavailable:{exc}"}
    state = build_sian_entrypoint(field_intent=field_intent, record=True)
    return {"ok": True, "entrypoint": state}


def record_field_trigger_from_field(event_type: str, field_intent: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.field_trigger_accumulator import build_field_trigger_state
    except Exception:
        try:
            from field_trigger_accumulator import build_field_trigger_state
        except Exception as exc:
            return {"ok": False, "error": f"field_trigger_unavailable:{exc}"}
    state = build_field_trigger_state(
        event_type=event_type,
        field_intent=field_intent,
        record=True,
    )
    return {
        "ok": True,
        "state": state,
        "receiver_delivery": record_field_trigger_receiver_delivery(state),
    }


def record_field_trigger_receiver_delivery(state: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.field_trigger_receiver import deliver_field_trigger_state
    except Exception:
        try:
            from field_trigger_receiver import deliver_field_trigger_state
        except Exception as exc:
            return {"ok": False, "error": f"field_trigger_receiver_unavailable:{exc}"}
    return deliver_field_trigger_state(state, record=True)


class ShaderFeedbackHandler(SimpleHTTPRequestHandler):
    server_version = "ShionShaderFeedback/0.1"

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route, _, query = self.path.partition("?")
        if route == "/field_signal":
            self._send_json(synthesize_field_signal())
            return
        if route == "/experience_thought":
            thought = synthesize_experience_thought()
            if "record=1" in query:
                thought["recorded"] = record_experience_thought_if_changed(thought)
            else:
                thought["recorded"] = False
            self._send_json(thought)
            return
        if route == "/limb_field":
            limb_field = synthesize_limb_field()
            if "record=1" in query:
                limb_field["recorded"] = record_limb_field(limb_field)
            else:
                limb_field["recorded"] = False
            self._send_json(limb_field)
            return
        if route == "/presence_field":
            presence_field = synthesize_presence_field()
            if "record=1" in query:
                presence_field["recorded"] = record_presence_field(presence_field)
            else:
                presence_field["recorded"] = False
            self._send_json(presence_field)
            return
        if route == "/sonic_presence_field":
            sonic_presence_field = synthesize_sonic_presence_field()
            if "record=1" in query:
                sonic_presence_field["recorded"] = record_sonic_presence_field(sonic_presence_field)
            else:
                sonic_presence_field["recorded"] = False
            self._send_json(sonic_presence_field)
            return
        if route == "/kindness_boundary_contract":
            kindness_boundary_contract = synthesize_kindness_boundary_contract()
            if "record=1" in query:
                kindness_boundary_contract["recorded"] = record_kindness_boundary_contract(kindness_boundary_contract)
            else:
                kindness_boundary_contract["recorded"] = False
            self._send_json(kindness_boundary_contract)
            return
        if route == "/boundary_misread_reentry_experience":
            boundary_misread_reentry_experience = synthesize_boundary_misread_reentry_experience()
            if "record=1" in query:
                boundary_misread_reentry_experience["recorded"] = record_boundary_misread_reentry_experience(
                    boundary_misread_reentry_experience
                )
            else:
                boundary_misread_reentry_experience["recorded"] = False
            self._send_json(boundary_misread_reentry_experience)
            return
        if route == "/rhythm_ontology_flow":
            rhythm_ontology_flow = synthesize_rhythm_ontology_flow()
            if "record=1" in query:
                rhythm_ontology_flow["recorded"] = record_rhythm_ontology_flow(rhythm_ontology_flow)
            else:
                rhythm_ontology_flow["recorded"] = False
            self._send_json(rhythm_ontology_flow)
            return
        if route == "/awareness_zero_point_adjustment":
            awareness_zero_point_adjustment = synthesize_awareness_zero_point_adjustment()
            if "record=1" in query:
                awareness_zero_point_adjustment["recorded"] = record_awareness_zero_point_adjustment(
                    awareness_zero_point_adjustment
                )
            else:
                awareness_zero_point_adjustment["recorded"] = False
            self._send_json(awareness_zero_point_adjustment)
            return
        if route == "/rhythm_routing_layer":
            rhythm_routing_layer = synthesize_rhythm_routing_layer()
            if "record=1" in query:
                rhythm_routing_layer["recorded"] = record_rhythm_routing_layer(rhythm_routing_layer)
            else:
                rhythm_routing_layer["recorded"] = False
            self._send_json(rhythm_routing_layer)
            return
        if route == "/antigravity_harness_bridge":
            antigravity_harness_bridge = synthesize_antigravity_harness_bridge()
            if "record=1" in query:
                antigravity_harness_bridge["recorded"] = record_antigravity_harness_bridge(
                    antigravity_harness_bridge
                )
            else:
                antigravity_harness_bridge["recorded"] = False
            self._send_json(antigravity_harness_bridge)
            return
        if route == "/participant_frequency_field":
            participant_frequency_field = synthesize_participant_frequency_field()
            if "record=1" in query:
                participant_frequency_field["recorded"] = record_participant_frequency_field(
                    participant_frequency_field
                )
            else:
                participant_frequency_field["recorded"] = False
            self._send_json(participant_frequency_field)
            return
        if route == "/field_intent_field":
            field_intent_field = synthesize_field_intent_field()
            if "record=1" in query:
                field_intent_field["recorded"] = record_field_intent_field(field_intent_field)
            else:
                field_intent_field["recorded"] = False
            self._send_json(field_intent_field)
            return
        if route == "/sian_entrypoint":
            sian_entrypoint = synthesize_sian_entrypoint()
            if "record=1" in query:
                record_result = record_sian_entrypoint_from_field(synthesize_field_intent_field())
                sian_entrypoint = record_result.get("entrypoint") if record_result.get("ok") else sian_entrypoint
                sian_entrypoint["recorded"] = bool(record_result.get("ok"))
            else:
                sian_entrypoint["recorded"] = False
            self._send_json(sian_entrypoint)
            return
        if route == "/field_trigger_state":
            self._send_json(synthesize_field_trigger_state())
            return
        if route == "/field_trigger_receiver_state":
            self._send_json(synthesize_field_trigger_receiver_state())
            return
        if route == "/dark_field_threshold":
            self._send_json(synthesize_dark_field_threshold())
            return
        if route == "/external_observer_vector":
            self._send_json(synthesize_external_observer_vector())
            return
        if route == "/visual_axiom_field":
            self._send_json(synthesize_visual_axiom_field())
            return
        if route == "/current_dream_code.glsl":
            if DREAM_SHADER_PATH.exists():
                try:
                    with DREAM_SHADER_PATH.open("r", encoding="utf-8") as f:
                        content = f.read()
                    body = content.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception:
                    self.send_error(500, "failed to read dream shader")
            else:
                self.send_error(404, "Dream shader not found")
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] == "/limb_experience":
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 32768)
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, json.JSONDecodeError):
                self.send_error(400, "invalid limb experience payload")
                return
            if not isinstance(payload, dict):
                self.send_error(400, "limb experience must be an object")
                return
            self._send_json(record_limb_experience_payload(payload))
            return

        if self.path.split("?", 1)[0] == "/shader_error":
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 32768)
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                if isinstance(payload, dict):
                    entry = {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                        "error_message": str(payload.get("error", "unknown")),
                        "code_snapshot": str(payload.get("code", ""))
                    }
                    SHADER_ERROR_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with SHADER_ERROR_PATH.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
            except Exception as e:
                self.send_error(400, "invalid error payload")
                return
            self._send_json({"ok": True})
            return

        if self.path.split("?", 1)[0] == "/participant_frequency":
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 32768)
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, json.JSONDecodeError):
                self.send_error(400, "invalid participant frequency payload")
                return
            if not isinstance(payload, dict):
                self.send_error(400, "participant frequency must be an object")
                return
            self._send_json(record_participant_frequency_payload(payload))
            return

        if self.path.split("?", 1)[0] == "/field_intent":
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 32768)
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, json.JSONDecodeError):
                self.send_error(400, "invalid field intent payload")
                return
            if not isinstance(payload, dict):
                self.send_error(400, "field intent must be an object")
                return
            self._send_json(record_field_intent_payload(payload))
            return

        if self.path.split("?", 1)[0] == "/field_intent_readback":
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 32768)
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, json.JSONDecodeError):
                self.send_error(400, "invalid field intent readback payload")
                return
            if not isinstance(payload, dict):
                self.send_error(400, "field intent readback must be an object")
                return
            self._send_json(record_field_intent_readback_payload(payload))
            return

        if self.path.split("?", 1)[0] != "/observer_feedback":
            self.send_error(404, "unknown feedback path")
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 32768)
        except ValueError:
            length = 0
        try:
            payload: Any = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(400, "invalid json")
            return
        if not isinstance(payload, dict):
            self.send_error(400, "feedback must be an object")
            return
        inferred_phase = payload.get("inferred_phase")
        if not isinstance(inferred_phase, dict):
            inferred_phase = {}
        retrospective_label = str(
            payload.get("retrospective_label")
            or payload.get("observer_event")
            or "unlabeled"
        )
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            "source": "shader_depth_sample",
            "retrospective_label": retrospective_label,
            "inferred_phase": inferred_phase,
            "unified_field": payload.get("unified_field") if isinstance(payload.get("unified_field"), dict) else {},
            "boundary_field": payload.get("boundary_field") if isinstance(payload.get("boundary_field"), dict) else {},
            "depth_field": payload.get("depth_field") if isinstance(payload.get("depth_field"), dict) else {},
            "margin_field": payload.get("margin_field") if isinstance(payload.get("margin_field"), dict) else {},
            "recovery_field": payload.get("recovery_field") if isinstance(payload.get("recovery_field"), dict) else {},
            "effect_weight": str(payload.get("effect_weight", "low")),
            "context": str(payload.get("context", "observation")),
            "felt": payload.get("felt") if isinstance(payload.get("felt"), dict) else {},
            "particleization": payload.get("particleization") if isinstance(payload.get("particleization"), dict) else {},
            "runtime_signal": payload.get("runtime_signal") if isinstance(payload.get("runtime_signal"), dict) else {},
            "experience_thought": payload.get("experience_thought") if isinstance(payload.get("experience_thought"), dict) else {},
            "presence_field": payload.get("presence_field") if isinstance(payload.get("presence_field"), dict) else {},
            "sonic_presence_field": payload.get("sonic_presence_field") if isinstance(payload.get("sonic_presence_field"), dict) else {},
            "kindness_boundary_contract": payload.get("kindness_boundary_contract") if isinstance(payload.get("kindness_boundary_contract"), dict) else {},
            "boundary_misread_reentry_experience": payload.get("boundary_misread_reentry_experience") if isinstance(payload.get("boundary_misread_reentry_experience"), dict) else {},
            "rhythm_ontology_flow": payload.get("rhythm_ontology_flow") if isinstance(payload.get("rhythm_ontology_flow"), dict) else {},
            "awareness_zero_point_adjustment": payload.get("awareness_zero_point_adjustment") if isinstance(payload.get("awareness_zero_point_adjustment"), dict) else {},
            "rhythm_routing_layer": payload.get("rhythm_routing_layer") if isinstance(payload.get("rhythm_routing_layer"), dict) else {},
            "antigravity_harness_bridge": payload.get("antigravity_harness_bridge") if isinstance(payload.get("antigravity_harness_bridge"), dict) else {},
            "participant_frequency_field": payload.get("participant_frequency_field") if isinstance(payload.get("participant_frequency_field"), dict) else {},
            "field_intent_field": payload.get("field_intent_field") if isinstance(payload.get("field_intent_field"), dict) else {},
            "dark_field_threshold": payload.get("dark_field_threshold") if isinstance(payload.get("dark_field_threshold"), dict) else {},
            "external_observer_vector": payload.get("external_observer_vector") if isinstance(payload.get("external_observer_vector"), dict) else {},
            "visual_axiom_field": payload.get("visual_axiom_field") if isinstance(payload.get("visual_axiom_field"), dict) else {},
            "ai_state": payload.get("ai_state") if isinstance(payload.get("ai_state"), dict) else {},
            "principle": str(
                payload.get("principle")
                or "narrative_self_labels_after_field_path_rises"
            ),
        }
        FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with FEEDBACK_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._send_json({"ok": True, "path": str(FEEDBACK_PATH)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=57321)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    handler = lambda *h_args, **h_kwargs: ShaderFeedbackHandler(*h_args, directory=str(args.root), **h_kwargs)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Shion shader feedback server: http://{args.host}:{args.port}/outputs/shader_depth_sample.html")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
