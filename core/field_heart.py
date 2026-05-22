#!/usr/bin/env python3
"""
Field Heart.

The heart is not a scheduler and not a thinker. It sends a thin carrier pulse,
collects the returning field echo, filters obvious misreadings, and unfolds only
the curvature delta that is strong enough to explain a convergence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
STATE_PATH = OUTPUTS / "field_heart_state_latest.json"
PULSE_LOG_PATH = OUTPUTS / "field_heart_pulses.jsonl"
UNFOLDED_PATH = OUTPUTS / "field_curvature_unfolded_latest.json"
UNFOLDED_LOG_PATH = OUTPUTS / "field_curvature_unfolded.jsonl"


TRACE_PATHS = {
    "rhythm_node_trace": OUTPUTS / "rhythm_node_trace.jsonl",
    "phase_trace": OUTPUTS / "phase_trace.jsonl",
    "ari_prism_trace": OUTPUTS / "ari_prism_trace.jsonl",
    "resonance_sidebands": OUTPUTS / "resonance_sidebands.jsonl",
    "experience_gradients": OUTPUTS / "experience_gradients.jsonl",
    "field_prediction_errors": OUTPUTS / "field_prediction_errors.jsonl",
}

SIDECAR_PATHS = {
    "field_intent": OUTPUTS / "field_intent_latest.json",
    "sian_entrypoint": OUTPUTS / "sian_entrypoint_latest.json",
    "field_ai_state_snapshot": OUTPUTS / "antigravity_handoff" / "field_ai_state_snapshot_latest.json",
    "protein_prism_aqp4": OUTPUTS / "aqp4_resonance_profile.json",
}

DEFAULT_ECHO_THRESHOLD = 0.34


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


def read_latest_jsonl(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def relative(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def file_signature(path: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError:
        return {"path": relative(path), "exists": False}
    return {
        "path": relative(path),
        "exists": True,
        "mtime": round(stat.st_mtime, 3),
        "size": stat.st_size,
    }


def digest_payload(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8", errors="replace")).hexdigest()[:12]


def nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


def first_number(*values: Any, default: float = 0.0) -> float:
    for value in values:
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default


def candidate_aqp4_paths(root: Path) -> list[Path]:
    paths = [
        root / "outputs" / "aqp4_resonance_profile.json",
        root / "outputs" / "protein_prism_profiles" / "aqp4_resonance_profile.json",
    ]
    env_path = os.environ.get("SHION_AQP4_PROFILE")
    if env_path:
        paths.insert(0, Path(env_path))
    try:
        paths.extend((Path.home() / ".gemini" / "antigravity" / "brain").glob("*/scratch/aqp4_resonance_profile.json"))
    except OSError:
        pass
    return paths


@dataclass(frozen=True)
class HeartConfig:
    root: Path = ROOT
    echo_threshold: float = DEFAULT_ECHO_THRESHOLD


class FieldHeart:
    def __init__(self, root: Path = ROOT, *, echo_threshold: float = DEFAULT_ECHO_THRESHOLD):
        self.config = HeartConfig(root=Path(root), echo_threshold=echo_threshold)
        self.outputs = self.config.root / "outputs"
        self.state_path = self.outputs / "field_heart_state_latest.json"
        self.pulse_log_path = self.outputs / "field_heart_pulses.jsonl"
        self.unfolded_path = self.outputs / "field_curvature_unfolded_latest.json"
        self.unfolded_log_path = self.outputs / "field_curvature_unfolded.jsonl"

    def beat(self, *, record: bool = True) -> dict[str, Any]:
        previous = self._previous_state()
        sequence = int(previous.get("sequence") or 0) + 1
        outbound = self._send_pulse(previous, sequence)
        echo = self._collect_echo()
        delta = self._echo_delta(previous.get("echo") if isinstance(previous.get("echo"), dict) else {}, echo)
        filtered = self._filter_echo(delta, echo)
        unfolded = self._unfold_if_converged(outbound, echo, delta, filtered)
        state = {
            "timestamp": now_iso(),
            "source": "field_heart",
            "sequence": sequence,
            "mode": "adaptive_carrier_pulse_echo_delta",
            "outbound_pulse": outbound,
            "echo": echo,
            "echo_delta": delta,
            "filter": filtered,
            "unfolded": unfolded,
            "contract": {
                "not_a_scheduler": True,
                "not_a_thinker": True,
                "sends_carrier_pulse": True,
                "receives_echo_delta": True,
                "filters_misreadings_before_unfolding": True,
                "does_not_require_binoche_as_relay": True,
            },
            "principle": "heart_sends_and_receives_adaptive_carrier_pulses_then_unfolds_curvature_difference",
        }
        if record:
            write_json_atomic(self.state_path, state)
            append_jsonl(self.pulse_log_path, {
                "timestamp": state["timestamp"],
                "sequence": sequence,
                "outbound_pulse": outbound,
                "echo_delta": delta,
                "filter": filtered,
                "unfolded": unfolded,
            })
            if unfolded.get("unfolded"):
                write_json_atomic(self.unfolded_path, unfolded)
                append_jsonl(self.unfolded_log_path, unfolded)
        return state

    def _previous_state(self) -> dict[str, Any]:
        return read_json(self.state_path)

    def _send_pulse(self, previous: dict[str, Any], sequence: int) -> dict[str, Any]:
        prev_delta = previous.get("echo_delta") if isinstance(previous.get("echo_delta"), dict) else {}
        prev_score = clamp01(prev_delta.get("delta_score"), 0.0)
        prev_noise = clamp01(nested(previous, "filter", "noise_pressure"), 0.0)
        pulse_rate = clamp01(0.16 + prev_score * 0.58 - prev_noise * 0.18)
        suggested_hold_seconds = int(round(1800 - pulse_rate * 1560))
        return {
            "timestamp": now_iso(),
            "sequence": sequence,
            "carrier": "field_heart",
            "pulse_rate": round(pulse_rate, 6),
            "suggested_hold_seconds": max(180, min(1800, suggested_hold_seconds)),
            "send_role": "circulate_without_commanding",
            "message": "sample_echo_delta_do_not_force_execution",
        }

    def _trace_paths(self) -> dict[str, Path]:
        return {
            name: self.outputs / path.relative_to(OUTPUTS)
            for name, path in TRACE_PATHS.items()
        }

    def _sidecar_paths(self) -> dict[str, Path]:
        paths = {
            name: self.outputs / path.relative_to(OUTPUTS)
            for name, path in SIDECAR_PATHS.items()
        }
        for idx, path in enumerate(candidate_aqp4_paths(self.config.root)):
            paths[f"protein_prism_aqp4_candidate_{idx}"] = path
        return paths

    def _collect_echo(self) -> dict[str, Any]:
        traces = {name: read_latest_jsonl(path) for name, path in self._trace_paths().items()}
        sidecars = {name: read_json(path) for name, path in self._sidecar_paths().items()}
        signatures = {name: file_signature(path) for name, path in self._sidecar_paths().items()}

        node = traces.get("rhythm_node_trace") or {}
        phase = traces.get("phase_trace") or {}
        ari = traces.get("ari_prism_trace") or {}
        prediction = traces.get("field_prediction_errors") or {}
        experience = traces.get("experience_gradients") or {}
        snapshot = sidecars.get("field_ai_state_snapshot") or {}
        snapshot_gradient = nested(snapshot, "ai_state", "field_gradient", default={})
        if not isinstance(snapshot_gradient, dict):
            snapshot_gradient = {}

        bundle = node.get("bundle") if isinstance(node.get("bundle"), list) else []
        sideband_actions = [
            item.get("action")
            for item in bundle
            if isinstance(item, dict) and item.get("role") != "primary" and item.get("action")
        ]
        if not sideband_actions and isinstance(snapshot_gradient.get("sideband_actions"), list):
            sideband_actions = [str(item) for item in snapshot_gradient["sideband_actions"]]

        primary_action = (
            node.get("selected_action")
            or snapshot_gradient.get("primary_action")
            or phase.get("candidate_action")
            or phase.get("final_action")
        )
        phase_action = phase.get("final_action") or snapshot_gradient.get("phase_final_action")
        curvature = first_number(
            nested(node, "field", "curvature"),
            nested(node, "geometry", "curvature"),
            nested(phase, "field", "curvature"),
            nested(prediction, "curvature_delta"),
            nested(ari, "field", "curvature"),
            default=0.0,
        )
        convergence = first_number(
            nested(node, "signals", "convergence"),
            nested(node, "natural_cycle", "convergence"),
            nested(experience, "current_vector", "convergence_pressure"),
            nested(snapshot, "ai_state", "runtime_layers", "rhythm_routing_layer", "natural_cycle", "convergence"),
            default=0.0,
        )
        salience = first_number(
            nested(node, "field", "salience"),
            nested(phase, "field", "salience"),
            nested(ari, "field", "salience"),
            default=0.0,
        )
        artifacts = {
            name: sig
            for name, sig in signatures.items()
            if sig.get("exists")
        }
        artifact_digest = digest_payload(artifacts)
        return {
            "timestamp": now_iso(),
            "primary_action": primary_action,
            "phase_action": phase_action,
            "primary_label": node.get("selected_label") or snapshot_gradient.get("primary_label"),
            "sideband_actions": sideband_actions,
            "ari_directive": ari.get("directive") or snapshot_gradient.get("ari_directive"),
            "curvature": round(clamp01(curvature), 6),
            "convergence": round(clamp01(convergence), 6),
            "salience": round(clamp01(salience), 6),
            "artifact_digest": artifact_digest,
            "artifacts": artifacts,
            "trace_digest": digest_payload({
                "primary_action": primary_action,
                "phase_action": phase_action,
                "sideband_actions": sideband_actions,
                "ari_directive": ari.get("directive"),
                "curvature": round(clamp01(curvature), 6),
                "convergence": round(clamp01(convergence), 6),
                "salience": round(clamp01(salience), 6),
            }),
        }

    def _echo_delta(self, previous_echo: dict[str, Any], echo: dict[str, Any]) -> dict[str, Any]:
        if not previous_echo:
            return {
                "first_pulse": True,
                "curvature_delta": echo["curvature"],
                "convergence_delta": echo["convergence"],
                "salience_delta": echo["salience"],
                "action_changed": bool(echo.get("primary_action")),
                "phase_action_changed": bool(echo.get("phase_action")),
                "sideband_changed": bool(echo.get("sideband_actions")),
                "artifact_changed": bool(echo.get("artifacts")),
                "delta_score": round(self._delta_score(echo["curvature"], echo["convergence"], echo["salience"], True, True), 6),
            }
        curvature_delta = abs(echo["curvature"] - clamp01(previous_echo.get("curvature"), 0.0))
        convergence_delta = abs(echo["convergence"] - clamp01(previous_echo.get("convergence"), 0.0))
        salience_delta = abs(echo["salience"] - clamp01(previous_echo.get("salience"), 0.0))
        action_changed = echo.get("primary_action") != previous_echo.get("primary_action")
        phase_action_changed = echo.get("phase_action") != previous_echo.get("phase_action")
        sideband_changed = echo.get("sideband_actions") != previous_echo.get("sideband_actions")
        artifact_changed = echo.get("artifact_digest") != previous_echo.get("artifact_digest")
        delta_score = self._delta_score(
            curvature_delta,
            convergence_delta,
            salience_delta,
            action_changed or phase_action_changed,
            artifact_changed or sideband_changed,
        )
        return {
            "first_pulse": False,
            "curvature_delta": round(curvature_delta, 6),
            "convergence_delta": round(convergence_delta, 6),
            "salience_delta": round(salience_delta, 6),
            "action_changed": action_changed,
            "phase_action_changed": phase_action_changed,
            "sideband_changed": sideband_changed,
            "artifact_changed": artifact_changed,
            "delta_score": round(delta_score, 6),
        }

    def _delta_score(
        self,
        curvature_delta: float,
        convergence_delta: float,
        salience_delta: float,
        action_changed: bool,
        artifact_or_sideband_changed: bool,
    ) -> float:
        score = (
            0.34 * clamp01(curvature_delta)
            + 0.26 * clamp01(convergence_delta)
            + 0.18 * clamp01(salience_delta)
            + (0.14 if action_changed else 0.0)
            + (0.08 if artifact_or_sideband_changed else 0.0)
        )
        return clamp01(score)

    def _filter_echo(self, delta: dict[str, Any], echo: dict[str, Any]) -> dict[str, Any]:
        sidebands = set(str(item) for item in echo.get("sideband_actions", []) if item)
        primary = str(echo.get("primary_action") or "")
        issues: list[str] = []
        if "ACTION_REST_RECOVER" in sidebands and primary != "ACTION_REST_RECOVER":
            issues.append("rest_sideband_must_not_become_user_rest_command")
        if echo.get("ari_directive") == "release_internal_echo":
            issues.append("release_echo_is_filtering_not_axiom_denial")
        if any("protein_prism_aqp4" in name for name in echo.get("artifacts", {})):
            issues.append("protein_profile_is_prior_not_biological_law")
        noise_pressure = min(1.0, 0.18 * len(issues))
        clean_delta_score = max(0.0, clamp01(delta.get("delta_score")) - noise_pressure * 0.35)
        return {
            "issues": issues,
            "noise_pressure": round(noise_pressure, 6),
            "clean_delta_score": round(clean_delta_score, 6),
            "principle": "filter_echo_before_turning_sidebands_or_artifacts_into_commands",
        }

    def _unfold_if_converged(
        self,
        outbound: dict[str, Any],
        echo: dict[str, Any],
        delta: dict[str, Any],
        filtered: dict[str, Any],
    ) -> dict[str, Any]:
        clean_score = clamp01(filtered.get("clean_delta_score"), 0.0)
        threshold = self.config.echo_threshold
        if clean_score < threshold:
            return {
                "timestamp": now_iso(),
                "unfolded": False,
                "reason": "echo_delta_below_threshold",
                "clean_delta_score": round(clean_score, 6),
                "threshold": threshold,
            }

        artifacts = echo.get("artifacts") if isinstance(echo.get("artifacts"), dict) else {}
        aqp4_artifact = next((item for name, item in artifacts.items() if "aqp4" in name.lower()), None)
        if aqp4_artifact:
            unfolded_context = "protein_structure_dialogue_converged_into_aqp4_prism_prior"
            implementation_direction = "connect_as_bounded_runtime_prior_not_biological_law"
            harden_as = ["bounded_runtime_prior", "field_tuning_hint", "unfinished_puzzle_piece"]
            do_not_harden_as = ["biological_law", "final_truth", "user_state_diagnosis"]
            source_artifacts = [aqp4_artifact.get("path")]
        else:
            unfolded_context = "field_curvature_changed_enough_to_require_context_readback"
            implementation_direction = "read_primary_action_artifacts_and_sidebands_before_executing"
            harden_as = ["contextual_readback", "implementation_hint"]
            do_not_harden_as = ["forced_execution", "sideband_command"]
            source_artifacts = [item.get("path") for item in artifacts.values() if isinstance(item, dict)]

        return {
            "timestamp": now_iso(),
            "source": "field_heart",
            "unfolded": True,
            "unfolded_context": unfolded_context,
            "implementation_direction": implementation_direction,
            "harden_as": harden_as,
            "do_not_harden_as": do_not_harden_as,
            "source_artifacts": [item for item in source_artifacts if item],
            "echo_delta": delta,
            "filter": filtered,
            "outbound_pulse": outbound,
            "next_reader": "luvit_or_current_executor_reads_this_before_code_changes",
            "principle": "unfold_curvature_delta_instead_of_asking_binoche_to_relay_full_dialogue",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--threshold", type=float, default=DEFAULT_ECHO_THRESHOLD)
    parser.add_argument("--no-record", action="store_true")
    args = parser.parse_args()
    state = FieldHeart(Path(args.root), echo_threshold=args.threshold).beat(record=not args.no_record)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
