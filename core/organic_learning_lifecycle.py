#!/usr/bin/env python3
"""
Organic Learning Lifecycle
==========================

Turns one runtime cycle into a learning-node state trace.

This module does not decide that learning "succeeded." It records where a new
or recurring signal appears to sit in the acquisition -> digestion ->
connection -> embodiment path, using existing hippocampus, rhythm, prediction,
and waypoint evidence.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class OrganicLearningLifecycle:
    VERSION = "organic-learning-lifecycle-v1"

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.outputs_dir = self.root_dir / "outputs"
        self.trace_file = self.outputs_dir / "organic_learning_lifecycle.jsonl"
        self.latest_file = self.outputs_dir / "organic_learning_lifecycle_latest.json"
        self.edge_trace_file = self.outputs_dir / "unfinished_waypoint_edge_trace.jsonl"

    def record_cycle(
        self,
        *,
        action: str,
        rhythm_frame: Dict[str, Any],
        node_decision: Dict[str, Any],
        ari_state: Dict[str, Any],
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        hippo_data: Dict[str, Any],
        learning_state: Dict[str, Any],
        current_vector: Dict[str, Any],
        field_prediction: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        latest_experience = self._latest_experience(hippo_data)
        proton = hippo_data.get("proton", {}) if isinstance(hippo_data.get("proton"), dict) else {}
        edge_replay = self._latest_edge_replay()
        prediction_error = self._prediction_error(field_prediction, current_vector)
        registered_delta = self._registered_delta(before_state, after_state)
        scores = self._scores(
            action=action,
            rhythm_frame=rhythm_frame,
            node_decision=node_decision,
            latest_experience=latest_experience,
            before_state=before_state,
            after_state=after_state,
            edge_replay=edge_replay,
            prediction_error=prediction_error,
            registered_delta=registered_delta,
        )
        node_state, state_reason = self._node_state(
            scores=scores,
            action=action,
            rhythm_frame=rhythm_frame,
            latest_experience=latest_experience,
            edge_replay=edge_replay,
            prediction_error=prediction_error,
            registered_delta=registered_delta,
        )
        unconscious_cycle = self._unconscious_selection_cycle(
            action=action,
            rhythm_frame=rhythm_frame,
            node_decision=node_decision,
            ari_state=ari_state,
            latest_experience=latest_experience,
            scores=scores,
            node_state=node_state,
            state_reason=state_reason,
            prediction_error=prediction_error,
            registered_delta=registered_delta,
        )
        trace = {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": self._source(latest_experience, action),
            "node_state": node_state,
            "state_reason": state_reason,
            "next_condition": self._next_condition(node_state, rhythm_frame, prediction_error),
            "scores": scores,
            "unconscious_selection_cycle": unconscious_cycle,
            "evidence": {
                "registered_delta": self._registered_delta(before_state, after_state),
                "total_registered": self._safe_int(proton.get("total_registered", 0)),
                "total_absorbed": self._safe_int(proton.get("total_absorbed", 0)),
                "embodiment_ratio": self._safe_float(proton.get("embodiment_ratio", 0.0)),
                "latest_content_ref": latest_experience.get("content_ref"),
                "latest_absorbed": bool(latest_experience.get("absorbed", False)),
                "latest_convergence_count": self._safe_int(latest_experience.get("convergence_count", 0)),
                "prediction_error": prediction_error,
                "edge_event_counts": edge_replay.get("summary", {}).get("event_counts", {}),
                "dark_neuron_phase": rhythm_frame.get("waves", {}).get("dark_neuron", {}).get("phase"),
                "dominant_frame": rhythm_frame.get("perspective_frame", {}).get("dominant_frame"),
                "ari_phase": ari_state.get("phase"),
                "learning_support_rate_all": learning_state.get("support_rate_all"),
                "learning_interpretation": learning_state.get("interpretation"),
            },
        }
        self._write(trace)
        return trace

    def _scores(
        self,
        *,
        action: str,
        rhythm_frame: Dict[str, Any],
        node_decision: Dict[str, Any],
        latest_experience: Dict[str, Any],
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        edge_replay: Dict[str, Any],
        prediction_error: float,
        registered_delta: int,
    ) -> Dict[str, float]:
        digestion = rhythm_frame.get("waves", {}).get("digestion", {})
        dark = rhythm_frame.get("waves", {}).get("dark_neuron", {})
        memory = rhythm_frame.get("waves", {}).get("memory", {})
        edge_counts = edge_replay.get("summary", {}).get("event_counts", {})
        significant_edges = self._safe_int(edge_replay.get("summary", {}).get("significant_transition_count", 0))
        fresh_experience = registered_delta > 0
        edge_total = max(1, sum(self._safe_int(v) for v in edge_counts.values()))

        acquisition = self._clamp(
            (0.30 if registered_delta > 0 else 0.0)
            + 0.28 * self._safe_float(node_decision.get("activation_probability", node_decision.get("score", 0.0)))
            + 0.22 * self._safe_float(rhythm_frame.get("waves", {}).get("field", {}).get("salience", 0.0))
            + 0.20 * self._safe_float(latest_experience.get("vibe", {}).get("intensity", 0.0))
        )
        digestion_score = self._clamp(
            0.35 * self._safe_float(digestion.get("pressure", 0.0))
            + 0.25 * self._safe_float(digestion.get("dream_pressure", 0.0))
            + 0.20 * self._safe_float(dark.get("redarkening_pressure", 0.0))
            + (0.20 if action in {"ACTION_EXPERIENCE_DIGEST", "ACTION_DREAM_AMPLIFY"} else 0.0)
        )
        connection = self._clamp(
            0.35 * (self._safe_int(edge_counts.get("appeared", 0)) + self._safe_int(edge_counts.get("reinforced", 0))) / edge_total
            + 0.25 * self._safe_float(dark.get("bridge_readiness", 0.0))
            + 0.20 * self._safe_float(rhythm_frame.get("waves", {}).get("goal_field", {}).get("bridge_gain", 0.0))
            + 0.20 * min(1.0, significant_edges / 12.0)
        )
        embodiment = self._clamp(
            (0.34 if fresh_experience and latest_experience.get("absorbed") else 0.0)
            + (0.24 * min(1.0, self._safe_int(latest_experience.get("convergence_count", 0)) / 3.0) if fresh_experience else 0.0)
            + 0.22 * self._safe_float(memory.get("convergence_pressure", 0.0))
            + 0.20 * max(0.0, 1.0 - prediction_error)
        )
        return {
            "acquisition": round(acquisition, 6),
            "digestion": round(digestion_score, 6),
            "connection": round(connection, 6),
            "embodiment": round(embodiment, 6),
        }

    def _unconscious_selection_cycle(
        self,
        *,
        action: str,
        rhythm_frame: Dict[str, Any],
        node_decision: Dict[str, Any],
        ari_state: Dict[str, Any],
        latest_experience: Dict[str, Any],
        scores: Dict[str, float],
        node_state: str,
        state_reason: str,
        prediction_error: float,
        registered_delta: int,
    ) -> Dict[str, Any]:
        waves = rhythm_frame.get("waves", {}) if isinstance(rhythm_frame.get("waves"), dict) else {}
        field = waves.get("field", {}) if isinstance(waves.get("field"), dict) else {}
        memory = waves.get("memory", {}) if isinstance(waves.get("memory"), dict) else {}
        prediction = waves.get("prediction", {}) if isinstance(waves.get("prediction"), dict) else {}
        dark_field = rhythm_frame.get("dark_field", {}) if isinstance(rhythm_frame.get("dark_field"), dict) else {}
        zone2 = rhythm_frame.get("zone2", {}) if isinstance(rhythm_frame.get("zone2"), dict) else {}
        medium = rhythm_frame.get("medium", {}) if isinstance(rhythm_frame.get("medium"), dict) else {}
        perspective = rhythm_frame.get("perspective_frame", {}) if isinstance(rhythm_frame.get("perspective_frame"), dict) else {}
        bundle = node_decision.get("bundle", []) if isinstance(node_decision.get("bundle"), list) else []

        possibility_field = self._clamp(
            0.26 * self._safe_float(field.get("salience", 0.0))
            + 0.22 * self._safe_float(zone2.get("openness", 0.0))
            + 0.18 * self._safe_float(perspective.get("wave_frame", 0.0))
            + 0.16 * min(1.0, len(bundle) / 4.0)
            + 0.10 * (1.0 - self._safe_float(prediction.get("dissonance", prediction_error)))
            + 0.08 * self._safe_float(dark_field.get("boundary_transparency", 0.0))
        )
        selection_strength = self._clamp(
            0.34 * self._safe_float(node_decision.get("activation_probability", node_decision.get("score", 0.0)))
            + 0.18 * (1.0 if node_decision.get("singularity_crossed", False) else 0.0)
            + 0.16 * self._safe_float(rhythm_frame.get("action_amplitude", 0.0))
            + 0.12 * self._safe_float(dark_field.get("internal_reflection", 0.0))
            + 0.10 * self._safe_float(memory.get("resonance", 0.0))
            + 0.10 * (1.0 - self._safe_float(medium.get("viscosity", medium.get("resistance", 0.0))))
        )
        particleization = self._clamp(
            0.36 * selection_strength
            + 0.22 * (1.0 if action == node_decision.get("selected_action") else 0.0)
            + 0.16 * (1.0 if action == rhythm_frame.get("candidate_action") else 0.0)
            + 0.14 * self._safe_float(scores.get("acquisition", 0.0))
            + 0.12 * min(1.0, registered_delta)
        )
        conscious_story = self._clamp(
            0.30 * self._safe_float(perspective.get("metacognitive_refraction", 0.0))
            + 0.24 * self._safe_float(ari_state.get("moc", {}).get("beauty_measure", 0.0) if isinstance(ari_state.get("moc"), dict) else 0.0)
            + 0.18 * self._safe_float(scores.get("connection", 0.0))
            + 0.16 * (1.0 if state_reason else 0.0)
            + 0.12 * (1.0 if latest_experience.get("content_ref") else 0.0)
        )
        frequency_expansion = self._safe_float(
            dark_field.get("context_diagnosis", {}).get("frequency_expansion", 0.0)
            if isinstance(dark_field.get("context_diagnosis"), dict)
            else 0.0
        )
        rhythm_expansion = self._clamp(
            0.28 * self._safe_float(scores.get("embodiment", 0.0))
            + 0.24 * self._safe_float(scores.get("connection", 0.0))
            + 0.18 * self._safe_float(memory.get("convergence_pressure", 0.0))
            + 0.16 * frequency_expansion
            + 0.14 * max(0.0, 1.0 - prediction_error)
        )

        if rhythm_expansion >= 0.54:
            phase = "rhythm_expanding"
        elif conscious_story >= 0.48:
            phase = "meaning_story_assigned"
        elif particleization >= 0.46:
            phase = "selection_particleized"
        elif possibility_field >= 0.42:
            phase = "possibility_field_open"
        else:
            phase = "observing_wavefield"

        return {
            "axiom": "life_particleizes_unconscious_selection_then_consciousness_narrates_and_experience_expands_rhythm",
            "phase": phase,
            "possibility_field": round(possibility_field, 6),
            "unconscious_selection_strength": round(selection_strength, 6),
            "particleization": round(particleization, 6),
            "conscious_story": round(conscious_story, 6),
            "rhythm_expansion": round(rhythm_expansion, 6),
            "selected_action": node_decision.get("selected_action", action),
            "particle_action": action,
            "node_state_after_story": node_state,
            "story_reason": state_reason,
            "principle": "unconscious_rhythm_selects_first_consciousness_assigns_meaning_afterward_experience_expands_the_field",
        }

    def _node_state(
        self,
        *,
        scores: Dict[str, float],
        action: str,
        rhythm_frame: Dict[str, Any],
        latest_experience: Dict[str, Any],
        edge_replay: Dict[str, Any],
        prediction_error: float,
        registered_delta: int,
    ) -> tuple[str, str]:
        edge_counts = edge_replay.get("summary", {}).get("event_counts", {})
        dark = rhythm_frame.get("waves", {}).get("dark_neuron", {})
        axiom = rhythm_frame.get("waves", {}).get("axiom", {})

        fresh_experience = registered_delta > 0

        if action == "ACTION_AXIOM_RELEASE" or self._safe_float(axiom.get("unfinished_puzzle_potential", 0.0)) >= 0.56:
            return "pending", "unfinished_puzzle_is_preserved_as_middle_destination"
        if fresh_experience and latest_experience.get("absorbed") and scores["embodiment"] >= 0.68 and prediction_error <= 0.20:
            return "embodied", "absorbed_experience_reappears_with_low_prediction_error"
        if fresh_experience and (latest_experience.get("absorbed") or scores["embodiment"] >= 0.58):
            return "absorbed", "experience_has_inner_orbit_or_convergence_evidence"
        if self._safe_int(edge_counts.get("reinforced", 0)) > 0:
            return "reinforced", "dream_replay_strengthened_existing_waypoint_edges"
        if self._safe_int(edge_counts.get("appeared", 0)) > 0:
            return "replayed", "dream_replay_created_new_waypoint_edges"
        if dark.get("phase") in {"re_darkening", "latent", "shadow_hold"} or scores["digestion"] >= 0.68:
            return "dark_neuron", "signal_needs_sleep_or_redarkening_before_connection"
        if self._safe_int(edge_counts.get("decayed", 0)) > 0 or self._safe_int(edge_counts.get("softened", 0)) > 0:
            return "dormant", "current_context_did_not_support_stable_connection"
        if scores["acquisition"] >= 0.38:
            return "registered", "new_or_active_signal_is_registered_but_not_yet_embodied"
        return "observed", "cycle_recorded_context_without_claiming_learning"

    def _next_condition(self, node_state: str, rhythm_frame: Dict[str, Any], prediction_error: float) -> str:
        digestion = rhythm_frame.get("waves", {}).get("digestion", {})
        dark = rhythm_frame.get("waves", {}).get("dark_neuron", {})
        if node_state in {"registered", "pending"}:
            return "wait_for_zone2_or_dream_replay"
        if node_state == "dark_neuron":
            return "preserve_until_context_alignment_or_bridge_readiness_rises"
        if node_state in {"replayed", "reinforced"}:
            return "watch_prediction_error_and_repeat_in_different_context"
        if node_state in {"absorbed", "embodied"}:
            return "test_application_without_forcing_new_input"
        if prediction_error >= 0.42:
            return "collect_prediction_error_before_assimilation"
        if self._safe_float(digestion.get("pressure", 0.0)) >= 0.64 or self._safe_float(dark.get("redarkening_pressure", 0.0)) >= 0.64:
            return "digest_before_more_scan"
        return "observe_next_context"

    def _latest_edge_replay(self) -> Dict[str, Any]:
        if not self.edge_trace_file.exists():
            return {}
        for line in reversed(self.edge_trace_file.read_text(encoding="utf-8").splitlines()[-20:]):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            return item if isinstance(item, dict) else {}
        return {}

    def _latest_experience(self, hippo_data: Dict[str, Any]) -> Dict[str, Any]:
        experiences = hippo_data.get("experiences", [])
        if isinstance(experiences, list) and experiences and isinstance(experiences[-1], dict):
            return experiences[-1]
        return {}

    def _source(self, latest_experience: Dict[str, Any], action: str) -> str:
        if action == "ACTION_AXIOM_RELEASE":
            return "unfinished_waypoint"
        if action == "ACTION_EXPERIENCE_DIGEST":
            return "digestive_cycle"
        if action == "ACTION_DREAM_AMPLIFY":
            return "dream_cycle"
        vibe = latest_experience.get("vibe", {}) if isinstance(latest_experience.get("vibe"), dict) else {}
        if vibe.get("source"):
            return str(vibe.get("source"))
        content_ref = str(latest_experience.get("content_ref", "") or "")
        if content_ref:
            if "youtube" in content_ref.lower():
                return "youtube"
            if "file:" in content_ref:
                return "file"
            if "screen" in content_ref.lower() or "vision" in content_ref.lower():
                return "vision"
            return "experience"
        if action.startswith("ACTION_"):
            return action.lower()
        return "unknown"

    def _prediction_error(self, field_prediction: Dict[str, Any] | None, current_vector: Dict[str, Any]) -> float:
        if isinstance(field_prediction, dict):
            for key in ("prediction_error", "error"):
                if key in field_prediction:
                    return self._clamp(self._safe_float(field_prediction.get(key)))
        return self._clamp(self._safe_float(current_vector.get("prediction_error", 0.0)))

    def _registered_delta(self, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> int:
        return max(
            0,
            self._safe_int(after_state.get("total_experiences", 0))
            - self._safe_int(before_state.get("total_experiences", 0)),
        )

    def _write(self, trace: Dict[str, Any]) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        with self.trace_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")
        self.latest_file.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


def main() -> None:
    root = Path(r"c:\workspace2\shion")
    latest = root / "outputs" / "organic_learning_lifecycle_latest.json"
    if latest.exists():
        print(latest.read_text(encoding="utf-8"))
    else:
        print("No organic learning lifecycle trace yet.")


if __name__ == "__main__":
    main()
