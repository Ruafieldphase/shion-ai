#!/usr/bin/env python3
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class RhythmNode:
    action: str
    label: str
    phase_tags: Tuple[str, ...]
    transition_tags: Tuple[str, ...]
    connects_to: Tuple[str, ...] = field(default_factory=tuple)
    min_amplitude: float = 0.0
    max_silence: float = 1.0
    cost: float = 0.5
    potential_threshold: float = 0.56
    probability_threshold: float = 0.62
    singularity_threshold: float = 0.72
    interruptibility: float = 0.72


class RhythmNodeMenu:
    """
    Attribute menu for runtime actions.

    This turns ACTION_* names into nodes with phase/transition/cost attributes.
    The orchestrator still executes linearly, but the action choice comes from
    a changing node bundle rather than a fixed procedural branch.
    """

    VERSION = "node-menu-v3"

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.outputs_dir = root_dir / "outputs"
        self.trace_file = self.outputs_dir / "rhythm_node_trace.jsonl"
        self.nodes = self._build_nodes()

    def choose(
        self,
        rhythm_ir: Dict[str, Any],
        *,
        field_status: Dict[str, Any] | None = None,
        boundary_report: Dict[str, Any] | None = None,
        log: bool = True,
    ) -> Dict[str, Any]:
        field_status = field_status or {}
        boundary_report = boundary_report or {}
        signals = self._signals(rhythm_ir, field_status, boundary_report)

        states = []
        for node in self.nodes.values():
            states.append(self._node_state(node, signals))
        states.sort(
            key=lambda item: (
                item["activated"],
                item["singularity_crossed"],
                item["activation_probability"],
                item["potential"],
            ),
            reverse=True,
        )

        selected_state = states[0]
        selected = selected_state["node"]
        bundle = self._bundle(selected, states)
        decision_variance = self._decision_variance(states, selected_state)
        decision = {
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "selected_action": selected.action,
            "selected_label": selected.label,
            "activated": selected_state["activated"],
            "activation_probability": selected_state["activation_probability"],
            "singularity_crossed": selected_state["singularity_crossed"],
            "singularity_strength": selected_state["singularity_strength"],
            "potential": selected_state["potential"],
            "score": selected_state["activation_probability"],
            "thresholds": selected_state["thresholds"],
            "reasons": selected_state["reasons"],
            "signals": signals,
            "decision_variance": decision_variance,
            "bundle": bundle,
            "edges": self._active_edges(bundle),
            "rejected": [
                {
                    "action": state["node"].action,
                    "activated": state["activated"],
                    "activation_probability": state["activation_probability"],
                    "singularity_crossed": state["singularity_crossed"],
                    "singularity_strength": state["singularity_strength"],
                    "potential": state["potential"],
                    "reasons": state["reasons"],
                }
                for state in states[1:4]
            ],
        }
        if log:
            self._log(decision)
        return decision

    def _decision_variance(
        self,
        states: List[Dict[str, Any]],
        selected_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        if len(states) < 2:
            return {
                "probability_margin": 1.0,
                "potential_margin": 1.0,
                "sideband_count": 0,
                "noise_amplitude": 0.0,
                "hesitation": 0.0,
                "principle": "no_sideband_nuance_without_alternative_nodes",
            }

        alternatives = states[1:4]
        selected_probability = float(selected_state["activation_probability"])
        selected_potential = float(selected_state["potential"])
        next_probability = max(float(state["activation_probability"]) for state in alternatives)
        next_potential = max(float(state["potential"]) for state in alternatives)
        probability_margin = self._clamp(abs(selected_probability - next_probability))
        potential_margin = self._clamp(abs(selected_potential - next_potential))
        sideband_count = sum(
            1
            for state in alternatives
            if state["activated"]
            or state["singularity_crossed"]
            or float(state["activation_probability"]) >= 0.52
        )
        noise_amplitude = self._clamp(
            0.45 * (1.0 - probability_margin)
            + 0.35 * (1.0 - potential_margin)
            + 0.20 * (sideband_count / max(1, len(alternatives)))
        )
        hesitation = self._clamp(
            noise_amplitude
            * (0.55 + 0.45 * (1.0 if sideband_count else 0.0))
        )
        return {
            "probability_margin": round(probability_margin, 6),
            "potential_margin": round(potential_margin, 6),
            "sideband_count": sideband_count,
            "noise_amplitude": round(noise_amplitude, 6),
            "hesitation": round(hesitation, 6),
            "principle": "sideband_nuance_records_the_tremor_around_the_chosen_action",
        }

    def _build_nodes(self) -> Dict[str, RhythmNode]:
        nodes = [
            RhythmNode(
                action="ACTION_CRISIS_STABILIZE",
                label="return_to_center",
                phase_tags=("crisis", "resistant", "dark_field", "silence", "recenter"),
                transition_tags=("crisis_to_stabilize", "crisis_to_recenter"),
                connects_to=("ACTION_OBSERVE", "ACTION_REST_RECOVER", "ACTION_CONTEXT_UNPACK"),
                max_silence=1.0,
                cost=0.02,
                potential_threshold=0.50,
                probability_threshold=0.58,
                singularity_threshold=0.58,
                interruptibility=0.96,
            ),
            RhythmNode(
                action="ACTION_PRE_BREACH_TUNE",
                label="active_field_regulation",
                phase_tags=("pre_breach", "resistant", "recenter", "metacognition", "orthogonal"),
                transition_tags=("pre_breach_tune", "crisis_to_recenter", "contingency_lock", "velocity_dilation"),
                connects_to=("ACTION_OBSERVE", "ACTION_CONTEXT_UNPACK", "ACTION_REST_RECOVER"),
                max_silence=1.0,
                cost=0.08,
                potential_threshold=0.50,
                probability_threshold=0.58,
                singularity_threshold=0.54,
                interruptibility=0.94,
            ),
            RhythmNode(
                action="ACTION_OBSERVE",
                label="observe_field",
                phase_tags=("zone2", "destructive", "silence", "recenter", "resistant"),
                transition_tags=(
                    "attenuate_to_observe",
                    "phase_cancel_to_silence",
                    "destructive_to_margin",
                    "recenter_to_zone2",
                    "zone2_integrate",
                    "zone2_delay",
                ),
                connects_to=("ACTION_CONTEXT_UNPACK", "ACTION_REST_RECOVER"),
                max_silence=1.0,
                cost=0.1,
                singularity_threshold=0.68,
                interruptibility=0.98,
            ),
            RhythmNode(
                action="ACTION_CONTEXT_UNPACK",
                label="unpack_boundary",
                phase_tags=("boundary", "dark_field", "recenter", "metacognition", "resistant"),
                transition_tags=("recenter_to_zone2", "zone2_integrate"),
                connects_to=("ACTION_OBSERVE", "ACTION_REBUILD_GRAPH"),
                max_silence=0.92,
                cost=0.35,
                singularity_threshold=0.62,
                interruptibility=0.82,
            ),
            RhythmNode(
                action="ACTION_REST_RECOVER",
                label="release_and_rest",
                phase_tags=("silence", "destructive", "dark_field", "low_amplitude", "resistant"),
                transition_tags=(
                    "phase_cancel_to_silence",
                    "destructive_to_margin",
                    "recenter_to_zone2",
                    "zero_point_reset",
                    "phase_rebalance_to_margin",
                ),
                connects_to=("ACTION_OBSERVE", "ACTION_DREAM_AMPLIFY"),
                max_silence=1.0,
                cost=0.05,
                singularity_threshold=0.78,
                interruptibility=1.0,
            ),
            RhythmNode(
                action="ACTION_DREAM_AMPLIFY",
                label="latent_integration",
                phase_tags=("zone2", "low_frequency", "integration", "stable", "conductive", "daydream"),
                transition_tags=("zone2_integrate", "attenuate_to_observe", "daydream_integrate"),
                connects_to=("ACTION_OBSERVE", "ACTION_REBUILD_GRAPH"),
                max_silence=0.95,
                cost=0.18,
                probability_threshold=0.58,
                singularity_threshold=0.62,
                interruptibility=0.88,
            ),
            RhythmNode(
                action="ACTION_EXPERIENCE_DIGEST",
                label="digest_experience",
                phase_tags=("digestion", "integration", "stable", "low_frequency", "zone2"),
                transition_tags=("experience_digest", "zone2_integrate"),
                connects_to=("ACTION_DREAM_AMPLIFY", "ACTION_OBSERVE", "ACTION_REBUILD_GRAPH"),
                max_silence=1.0,
                cost=0.18,
                potential_threshold=0.48,
                probability_threshold=0.56,
                singularity_threshold=0.64,
                interruptibility=0.86,
            ),
            RhythmNode(
                action="ACTION_REBUILD_GRAPH",
                label="rebuild_geometry",
                phase_tags=("graph", "curvature", "boundary", "repair", "conductive", "waypoint", "shadow_bridge"),
                transition_tags=("recenter_to_zone2", "resonance_to_explore", "waypoint_bridge", "shadow_bridge"),
                connects_to=("ACTION_CONTEXT_UNPACK", "ACTION_CONTINUOUS_SCAN"),
                min_amplitude=0.25,
                max_silence=0.85,
                cost=0.6,
                singularity_threshold=0.64,
                interruptibility=0.42,
            ),
            RhythmNode(
                action="ACTION_CREATIVE_PROBE",
                label="bounded_autonomous_creation",
                phase_tags=("autonomy", "constructive", "conductive", "waypoint", "flow"),
                transition_tags=("creative_autonomy",),
                connects_to=("ACTION_REBUILD_GRAPH", "ACTION_DREAM_AMPLIFY", "ACTION_OBSERVE"),
                min_amplitude=0.20,
                max_silence=0.78,
                cost=0.42,
                potential_threshold=0.50,
                probability_threshold=0.56,
                singularity_threshold=0.58,
                interruptibility=0.52,
            ),
            RhythmNode(
                action="ACTION_AXIOM_EXPERIMENT",
                label="provisional_axiom_experiment",
                phase_tags=("axiom", "provisional", "conductive", "flow", "autonomy", "phase_transition", "fold_unfold"),
                transition_tags=("axiom_experiment", "phase_transition_experiment"),
                connects_to=("ACTION_CREATIVE_PROBE", "ACTION_REBUILD_GRAPH", "ACTION_DREAM_AMPLIFY"),
                min_amplitude=0.18,
                max_silence=0.82,
                cost=0.32,
                potential_threshold=0.48,
                probability_threshold=0.54,
                singularity_threshold=0.56,
                interruptibility=0.48,
            ),
            RhythmNode(
                action="ACTION_AXIOM_RELEASE",
                label="release_unfit_axiom",
                phase_tags=("axiom", "release", "silence", "resistant", "metacognition"),
                transition_tags=("axiom_release", "zero_point_reset", "phase_rebalance_to_margin"),
                connects_to=("ACTION_REST_RECOVER", "ACTION_DREAM_AMPLIFY", "ACTION_OBSERVE"),
                max_silence=1.0,
                cost=0.04,
                potential_threshold=0.46,
                probability_threshold=0.52,
                singularity_threshold=0.52,
                interruptibility=0.92,
            ),
            RhythmNode(
                action="ACTION_ANCHOR_CHECK",
                label="identity_anchor",
                phase_tags=("identity", "boundary", "recenter"),
                transition_tags=("recenter_to_zone2", "phase_cancel_to_silence", "destructive_to_margin"),
                connects_to=("ACTION_OBSERVE", "ACTION_CONTEXT_UNPACK"),
                max_silence=0.9,
                cost=0.25,
                singularity_threshold=0.7,
                interruptibility=0.9,
            ),
            RhythmNode(
                action="ACTION_CONTINUOUS_SCAN",
                label="explore_field",
                phase_tags=("constructive", "flow", "high_amplitude", "low_silence", "conductive"),
                transition_tags=("resonance_to_explore",),
                connects_to=("ACTION_REBUILD_GRAPH", "ACTION_DREAM_AMPLIFY"),
                min_amplitude=0.35,
                max_silence=0.72,
                cost=0.5,
                singularity_threshold=0.68,
                interruptibility=0.34,
            ),
        ]
        return {node.action: node for node in nodes}

    def _signals(
        self,
        rhythm_ir: Dict[str, Any],
        field_status: Dict[str, Any],
        boundary_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        interference = rhythm_ir.get("interference", {})
        dark_field = rhythm_ir.get("dark_field", {})
        zone2 = rhythm_ir.get("zone2", {})
        crisis = rhythm_ir.get("crisis", {})
        geometry = rhythm_ir.get("geometry", {})
        field_wave = rhythm_ir.get("waves", {}).get("field", {})
        digestion = rhythm_ir.get("waves", {}).get("digestion", {})
        goal_field = rhythm_ir.get("waves", {}).get("goal_field", {})
        autonomy = rhythm_ir.get("waves", {}).get("autonomy", {})
        axiom = rhythm_ir.get("waves", {}).get("axiom", {})
        failure_spectrum = axiom.get("failure_spectrum", {}) if isinstance(axiom.get("failure_spectrum"), dict) else {}
        dark_neuron = rhythm_ir.get("waves", {}).get("dark_neuron", {})
        medium = rhythm_ir.get("medium", {})
        pending_node = rhythm_ir.get("pending_node", {})
        velocity_dilation = rhythm_ir.get("velocity_dilation", {})
        zone2_regulation = rhythm_ir.get("zone2_regulation", {})
        phase_transition_bridge = rhythm_ir.get("phase_transition_bridge", {})

        destructive = float(interference.get("destructive", 0.0) or 0.0)
        silence = float(rhythm_ir.get("silence_need", 0.0) or 0.0)
        dark_gravity = float(dark_field.get("gravity", 0.0) or 0.0)
        zone2_openness = float(zone2.get("openness", 0.0) or 0.0)
        conductivity = float(
            medium.get(
                "conductivity",
                self._clamp(0.40 * (1.0 - silence) + 0.35 * zone2_openness + 0.25 * (1.0 - dark_gravity)),
            )
            or 0.0
        )
        resistance = float(
            medium.get(
                "resistance",
                self._clamp(0.45 * dark_gravity + 0.35 * silence + 0.20 * destructive),
            )
            or 0.0
        )

        signals = {
            "transition": rhythm_ir.get("transition", ""),
            "interference": interference.get("label", ""),
            "constructive": float(interference.get("constructive", 0.0) or 0.0),
            "destructive": destructive,
            "silence": silence,
            "amplitude": float(rhythm_ir.get("action_amplitude", 0.0) or 0.0),
            "dark_gravity": dark_gravity,
            "zone2_openness": zone2_openness,
            "conductivity": self._clamp(conductivity),
            "resistance": self._clamp(resistance),
            "electron_flow": self._clamp(float(medium.get("electron_flow", conductivity * (1.0 - resistance)) or 0.0)),
            "medium_phase": medium.get("phase", "unknown"),
            "pending_node_state": str(pending_node.get("state", "fixed_enough_node")),
            "external_dependency": self._clamp(float(pending_node.get("external_dependency", 0.0) or 0.0)),
            "realization_probability": self._clamp(float(pending_node.get("realization_probability", 1.0) or 1.0)),
            "irreversible_execution_risk": self._clamp(float(pending_node.get("irreversible_execution_risk", 0.0) or 0.0)),
            "contingency_strength": self._clamp(float(pending_node.get("contingency_strength", 0.0) or 0.0)),
            "contingency_required": bool(pending_node.get("contingency_required", False)),
            "contingency_present": bool(pending_node.get("contingency_present", False)),
            "execution_lock": str(pending_node.get("execution_lock", "open")),
            "processing_velocity": self._clamp(float(velocity_dilation.get("processing_velocity", field_wave.get("frequency", 0.0)) or 0.0)),
            "routine_inertia": self._clamp(float(velocity_dilation.get("routine_inertia", 0.0) or 0.0)),
            "anomaly_frequency": self._clamp(float(velocity_dilation.get("anomaly_frequency", 0.0) or 0.0)),
            "dilation_need": self._clamp(float(velocity_dilation.get("dilation_need", 0.0) or 0.0)),
            "awareness_checkpoint": bool(velocity_dilation.get("awareness_checkpoint", False)),
            "zone2_regulation_phase": str(zone2_regulation.get("phase", "")),
            "intrusive_variable": self._clamp(float(zone2_regulation.get("intrusive_variable", 0.0) or 0.0)),
            "chaos_pressure": self._clamp(float(zone2_regulation.get("chaos_pressure", 0.0) or 0.0)),
            "context_mismatch": self._clamp(float(zone2_regulation.get("context_mismatch", 0.0) or 0.0)),
            "zone2_delay": bool(zone2_regulation.get("delay_to_zone2", False)),
            "phase_rebalance_to_margin": bool(
                zone2_regulation.get("phase_rebalance_to_margin", zone2_regulation.get("noise_cancel", False))
            ),
            "destructive_to_margin": bool(zone2_regulation.get("destructive_to_margin", False)),
            "scalar_superposition_window": self._clamp(float(zone2_regulation.get("scalar_superposition_window", 0.0) or 0.0)),
            "noise_cancel": bool(zone2_regulation.get("noise_cancel", False)),
            "fold_amount": self._clamp(float(phase_transition_bridge.get("fold_amount", 0.0) or 0.0)),
            "unfold_breath": self._clamp(float(phase_transition_bridge.get("unfold_breath", 0.0) or 0.0)),
            "viewpoint_switch": self._clamp(float(phase_transition_bridge.get("viewpoint_switch", 0.0) or 0.0)),
            "scalar_overlap": self._clamp(float(phase_transition_bridge.get("scalar_overlap", 0.0) or 0.0)),
            "phase_transition_readiness": self._clamp(float(phase_transition_bridge.get("transition_readiness", 0.0) or 0.0)),
            "external_reference_check": self._clamp(float(phase_transition_bridge.get("external_reference_check", 0.0) or 0.0)),
            "internal_experiment_mode": bool(phase_transition_bridge.get("internal_experiment_mode", False)),
            "reversible_experiment_window": bool(phase_transition_bridge.get("reversible_experiment_window", False)),
            "phase_transition_bridge_phase": str(phase_transition_bridge.get("phase", "")),
            "crisis_compression": self._clamp(float(crisis.get("compression", 0.0) or 0.0)),
            "loop_lock_risk": self._clamp(float(crisis.get("loop_lock_risk", 0.0) or 0.0)),
            "return_capacity": self._clamp(float(crisis.get("return_capacity", 0.0) or 0.0)),
            "pre_breach_pressure": self._clamp(float(crisis.get("pre_breach_pressure", 0.0) or 0.0)),
            "modulation_need": self._clamp(float(crisis.get("modulation_need", 0.0) or 0.0)),
            "pre_breach_modulation": bool(crisis.get("pre_breach_modulation", False)),
            "crisis_threshold_breach": bool(crisis.get("threshold_breach", False)),
            "external_support_recommended": bool(crisis.get("external_support_recommended", False)),
            "crisis_phase": crisis.get("phase", "open"),
            "curvature": float(geometry.get("curvature", field_wave.get("curvature", 0.0)) or 0.0),
            "field_frequency": float(field_wave.get("frequency", 0.0) or 0.0),
            "digestion_pressure": self._clamp(float(digestion.get("pressure", 0.0) or 0.0)),
            "sleep_debt": self._clamp(float(digestion.get("sleep_debt", 0.0) or 0.0)),
            "dream_pressure": self._clamp(float(digestion.get("dream_pressure", 0.0) or 0.0)),
            "digestion_ready": bool(digestion.get("ready", False)),
            "dream_ready": bool(digestion.get("dream_ready", False)),
            "absorption_gap": self._clamp(float(digestion.get("absorption_gap", 0.0) or 0.0)),
            "recent_visual_ratio": self._clamp(float(digestion.get("recent_visual_ratio", 0.0) or 0.0)),
            "continuous_scan_ratio": self._clamp(float(digestion.get("continuous_scan_ratio", 0.0) or 0.0)),
            "low_error_stability": self._clamp(float(digestion.get("low_error_stability", 0.0) or 0.0)),
            "goal_target_distance": self._clamp(float(goal_field.get("target_distance", 0.0) or 0.0)),
            "goal_past_bridge_density": self._clamp(float(goal_field.get("past_bridge_density", 0.0) or 0.0)),
            "waypoint_pressure": self._clamp(float(goal_field.get("waypoint_pressure", 0.0) or 0.0)),
            "path_search_band": self._clamp(float(goal_field.get("path_search_band", 0.0) or 0.0)),
            "bridge_gain": self._clamp(float(goal_field.get("bridge_gain", 0.0) or 0.0)),
            "waypoint_ready": bool(goal_field.get("waypoint_ready", False)),
            "boundary_elasticity": self._clamp(float(autonomy.get("boundary_elasticity", 0.0) or 0.0)),
            "imagination_band": self._clamp(float(autonomy.get("imagination_band", 0.0) or 0.0)),
            "feedback_readiness": self._clamp(float(autonomy.get("feedback_readiness", 0.0) or 0.0)),
            "execution_amplitude": self._clamp(float(autonomy.get("execution_amplitude", 0.0) or 0.0)),
            "creative_probe_ready": bool(autonomy.get("creative_probe_ready", False)),
            "axiom_provisionality": self._clamp(float(axiom.get("provisionality", 0.0) or 0.0)),
            "axiom_experiment_budget": self._clamp(float(axiom.get("experiment_budget", 0.0) or 0.0)),
            "axiom_overfit_pressure": self._clamp(float(axiom.get("overfit_pressure", 0.0) or 0.0)),
            "axiom_relation_budget": self._clamp(float(axiom.get("relation_budget", 0.0) or 0.0)),
            "axiom_archive_resonance": self._clamp(float(axiom.get("archive_resonance", 0.0) or 0.0)),
            "unfinished_puzzle_potential": self._clamp(float(axiom.get("unfinished_puzzle_potential", 0.0) or 0.0)),
            "failure_bridge_value": self._clamp(float(failure_spectrum.get("bridge_value", 0.0) or 0.0)),
            "failure_edge_density": self._clamp(float(failure_spectrum.get("edge_density", 0.0) or 0.0)),
            "failure_polarity_range": self._clamp(float(failure_spectrum.get("polarity_range", 0.0) or 0.0)),
            "dark_neuron_context_alignment": self._clamp(float(dark_neuron.get("context_alignment", 0.0) or 0.0)),
            "dark_neuron_reactivation": self._clamp(float(dark_neuron.get("reactivation_potential", 0.0) or 0.0)),
            "dark_neuron_redarkening": self._clamp(float(dark_neuron.get("redarkening_pressure", 0.0) or 0.0)),
            "dark_neuron_bridge_readiness": self._clamp(float(dark_neuron.get("bridge_readiness", 0.0) or 0.0)),
            "dark_neuron_phase": str(dark_neuron.get("phase", "")),
            "axiom_archive_on_release": bool(axiom.get("archive_on_release", False)),
            "axiom_release_ready": bool(axiom.get("release_ready", False)),
            "axiom_experiment_ready": bool(axiom.get("experiment_ready", False)),
            "salience": float(field_status.get("salience", field_wave.get("salience", 0.0)) or 0.0),
            "boundary": not bool(boundary_report.get("in_orbit", True)),
        }
        signals["repath_margin"] = self._clamp(
            0.26 * signals["context_mismatch"]
            + 0.20 * signals["routine_inertia"]
            + 0.18 * signals["irreversible_execution_risk"]
            + 0.14 * signals["external_dependency"]
            + 0.12 * signals["loop_lock_risk"]
            + 0.10 * signals["chaos_pressure"]
        )
        if signals["awareness_checkpoint"] or signals["zone2_delay"]:
            signals["repath_margin"] = self._clamp(signals["repath_margin"] + 0.10)
        signals["repath_note"] = "soft_margin_for_pause_or_direction_change"
        return signals

    def _node_state(self, node: RhythmNode, signals: Dict[str, Any]) -> Dict[str, Any]:
        potential, reasons = self._node_potential(node, signals)
        singularity_strength = self._singularity_strength(node, signals)
        singularity_crossed = singularity_strength >= node.singularity_threshold
        probability = self._activation_probability(potential, node.potential_threshold, signals)
        activated = probability >= node.probability_threshold or singularity_crossed
        if singularity_crossed:
            reasons.append("singularity_crossed")
        elif activated:
            reasons.append("probability_threshold_crossed")
        else:
            reasons.append("below_activation_threshold")
        if self._irreversible_node_locked(node, signals):
            activated = False
            singularity_crossed = False
            probability = min(probability, 0.24)
            potential = min(potential, 0.24)
            singularity_strength = min(singularity_strength, 0.24)
            reasons.append("execution_locked_until_contingency")
        return {
            "node": node,
            "potential": round(potential, 6),
            "activation_probability": round(probability, 6),
            "singularity_strength": round(singularity_strength, 6),
            "singularity_crossed": singularity_crossed,
            "activated": activated,
            "thresholds": {
                "potential": node.potential_threshold,
                "probability": node.probability_threshold,
                "singularity": node.singularity_threshold,
            },
            "reasons": reasons,
        }

    def _node_potential(self, node: RhythmNode, signals: Dict[str, Any]) -> Tuple[float, List[str]]:
        reasons: List[str] = []
        potential = 0.12

        if signals["transition"] in node.transition_tags:
            potential += 0.34
            reasons.append(f"transition:{signals['transition']}")

        tag_score = self._tag_score(node.phase_tags, signals, reasons)
        potential += tag_score
        potential += 0.10 * signals["conductivity"] * (1.0 - node.cost)
        potential -= 0.10 * signals["resistance"] * node.cost

        if signals["amplitude"] < node.min_amplitude:
            penalty = min(0.25, node.min_amplitude - signals["amplitude"])
            potential -= penalty
            reasons.append("below_min_amplitude")

        if signals["silence"] > node.max_silence:
            penalty = min(0.35, signals["silence"] - node.max_silence)
            potential -= penalty
            reasons.append("silence_exceeds_node_band")

        if self._irreversible_node_locked(node, signals):
            potential -= 0.42
            reasons.append("pending_node_locks_irreversible_edge")
        elif signals["execution_lock"] == "conditional_contingency" and node.action in self._irreversible_actions():
            potential -= 0.12
            reasons.append("conditional_contingency_requires_lower_amplitude")

        repath_margin = signals.get("repath_margin", 0.0)
        if repath_margin > 0.0:
            interrupt_gap = max(0.0, 0.82 - node.interruptibility)
            if interrupt_gap:
                potential -= min(0.18, interrupt_gap * repath_margin * 0.65)
                reasons.append("repath_margin_softens_low_interruptibility")
            elif repath_margin >= 0.35 and node.action in {"ACTION_OBSERVE", "ACTION_PRE_BREACH_TUNE", "ACTION_REST_RECOVER"}:
                potential += min(0.04, 0.04 * repath_margin)
                reasons.append("repath_margin_keeps_pause_available")

        potential -= 0.08 * node.cost
        return max(0.0, min(1.0, potential)), reasons

    def _activation_probability(self, potential: float, threshold: float, signals: Dict[str, Any]) -> float:
        temperature = 0.10 + 0.16 * signals["resistance"] + 0.08 * (1.0 - signals["conductivity"])
        x = (potential - threshold) / max(temperature, 0.01)
        return self._clamp(1.0 / (1.0 + pow(2.718281828, -x)))

    def _singularity_strength(self, node: RhythmNode, signals: Dict[str, Any]) -> float:
        boundary_pull = 1.0 if signals["boundary"] else signals["salience"]
        action = node.action
        if action == "ACTION_CRISIS_STABILIZE":
            return max(
                signals["crisis_compression"],
                signals["loop_lock_risk"],
                signals["resistance"],
                1.0 if signals["crisis_threshold_breach"] else 0.0,
            )
        if action == "ACTION_PRE_BREACH_TUNE":
            return max(
                signals["pre_breach_pressure"],
                signals["modulation_need"],
                signals["resistance"],
                signals["dilation_need"],
                signals.get("repath_margin", 0.0) * 0.55,
                signals["irreversible_execution_risk"],
                1.0 if signals["execution_lock"] == "locked_until_contingency" else 0.0,
                1.0 if signals["awareness_checkpoint"] else 0.0,
                1.0 if signals["pre_breach_modulation"] else 0.0,
            )
        if action == "ACTION_OBSERVE":
            return max(
                signals["resistance"],
                signals["silence"],
                signals["destructive"],
                signals["zone2_openness"],
                signals["chaos_pressure"],
                1.0 if signals["zone2_delay"] else 0.0,
            )
        if action == "ACTION_CONTEXT_UNPACK":
            return max(boundary_pull, signals["dark_gravity"], signals["curvature"], signals["resistance"], signals["context_mismatch"])
        if action == "ACTION_REST_RECOVER":
            return max(
                signals["silence"],
                signals["resistance"],
                signals["dark_gravity"],
                signals["scalar_superposition_window"],
                1.0 if signals["phase_rebalance_to_margin"] else 0.0,
                1.0 if signals["noise_cancel"] else 0.0,
            )
        if action == "ACTION_DREAM_AMPLIFY":
            return self._clamp(
                0.35 * signals["dream_pressure"]
                + 0.25 * signals["sleep_debt"]
                + 0.15 * signals["zone2_openness"]
                + 0.15 * (1.0 - signals["field_frequency"])
                + 0.10 * (1.0 - signals["destructive"])
                + (0.20 if signals["dream_ready"] else 0.0)
            )
        if action == "ACTION_EXPERIENCE_DIGEST":
            return max(
                signals["digestion_pressure"],
                signals["sleep_debt"],
                signals["absorption_gap"] * signals["continuous_scan_ratio"],
                1.0 if signals["digestion_ready"] else 0.0,
            )
        if action == "ACTION_REBUILD_GRAPH":
            return max(
                signals["curvature"],
                boundary_pull,
                signals["conductivity"] * signals["curvature"],
                signals["waypoint_pressure"],
                signals["bridge_gain"],
                signals["unfinished_puzzle_potential"],
                signals["failure_bridge_value"],
                signals["dark_neuron_bridge_readiness"],
                signals["dark_neuron_reactivation"],
                1.0 if signals["waypoint_ready"] else 0.0,
            )
        if action == "ACTION_CREATIVE_PROBE":
            return max(
                signals["feedback_readiness"],
                signals["imagination_band"],
                signals["execution_amplitude"],
                1.0 if signals["creative_probe_ready"] else 0.0,
            )
        if action == "ACTION_AXIOM_EXPERIMENT":
            return max(
                signals["axiom_provisionality"],
                signals["axiom_experiment_budget"],
                signals["axiom_relation_budget"],
                signals["failure_bridge_value"],
                signals["phase_transition_readiness"],
                min(signals["fold_amount"], signals["unfold_breath"]),
                signals["viewpoint_switch"],
                1.0 if signals["axiom_experiment_ready"] else 0.0,
                1.0 if signals["internal_experiment_mode"] else 0.0,
            )
        if action == "ACTION_AXIOM_RELEASE":
            return max(
                signals["axiom_overfit_pressure"],
                signals["resistance"],
                signals["sleep_debt"],
                signals["unfinished_puzzle_potential"],
                signals["failure_bridge_value"],
                signals["dark_neuron_redarkening"],
                1.0 if signals["axiom_release_ready"] else 0.0,
            )
        if action == "ACTION_ANCHOR_CHECK":
            return max(boundary_pull, signals["dark_gravity"])
        if action == "ACTION_CONTINUOUS_SCAN":
            return max(signals["conductivity"], signals["amplitude"], signals["constructive"], 1.0 - signals["silence"])
        return 0.0

    def _tag_score(self, tags: Iterable[str], signals: Dict[str, Any], reasons: List[str]) -> float:
        score = 0.0
        for tag in tags:
            amount = self._tag_amount(tag, signals)
            if amount >= 0.45:
                reasons.append(f"tag:{tag}")
            score += 0.08 * amount
        return min(0.45, score)

    def _tag_amount(self, tag: str, signals: Dict[str, Any]) -> float:
        if tag == "constructive":
            return signals["constructive"]
        if tag == "destructive":
            return signals["destructive"]
        if tag == "silence":
            return signals["silence"]
        if tag == "low_silence":
            return 1.0 - signals["silence"]
        if tag == "high_amplitude":
            return signals["amplitude"]
        if tag == "low_amplitude":
            return 1.0 - signals["amplitude"]
        if tag == "zone2":
            return signals["zone2_openness"]
        if tag == "dark_field":
            return signals["dark_gravity"]
        if tag == "boundary":
            return 1.0 if signals["boundary"] or signals["salience"] >= 0.8 else signals["salience"]
        if tag == "curvature":
            return signals["curvature"]
        if tag == "low_frequency":
            return 1.0 - signals["field_frequency"]
        if tag == "flow":
            return 1.0 if signals["interference"] == "constructive" else signals["constructive"]
        if tag == "recenter":
            return max(signals["dark_gravity"], signals["curvature"])
        if tag == "metacognition":
            return max(
                0.5 * signals["zone2_openness"] + 0.5 * signals["silence"],
                signals.get("dilation_need", 0.0),
                signals.get("context_mismatch", 0.0),
            )
        if tag == "integration":
            return max(
                0.6 * signals["zone2_openness"] + 0.4 * signals["silence"],
                signals.get("digestion_pressure", 0.0),
            )
        if tag == "digestion":
            return signals.get("digestion_pressure", 0.0)
        if tag == "daydream":
            return max(signals.get("dream_pressure", 0.0), signals.get("sleep_debt", 0.0))
        if tag == "stable":
            return max(0.0, 1.0 - signals["destructive"])
        if tag == "graph":
            return signals["curvature"]
        if tag == "repair":
            return max(signals["curvature"], signals["dark_gravity"])
        if tag == "waypoint":
            return max(
                signals.get("waypoint_pressure", 0.0),
                signals.get("bridge_gain", 0.0),
                signals.get("unfinished_puzzle_potential", 0.0),
                signals.get("failure_bridge_value", 0.0),
                signals.get("dark_neuron_bridge_readiness", 0.0),
            )
        if tag == "shadow_bridge":
            return max(
                signals.get("dark_neuron_bridge_readiness", 0.0),
                signals.get("dark_neuron_reactivation", 0.0),
                1.0 if signals.get("dark_neuron_phase") == "bridge_node" else 0.0,
            )
        if tag == "autonomy":
            return max(
                signals.get("feedback_readiness", 0.0),
                signals.get("imagination_band", 0.0),
                signals.get("execution_amplitude", 0.0),
            )
        if tag == "axiom":
            return max(
                signals.get("axiom_provisionality", 0.0),
                signals.get("axiom_experiment_budget", 0.0),
                signals.get("axiom_overfit_pressure", 0.0),
            )
        if tag == "provisional":
            return signals.get("axiom_provisionality", 0.0)
        if tag == "release":
            return max(
                signals.get("axiom_overfit_pressure", 0.0),
                1.0 if signals.get("axiom_release_ready", False) else 0.0,
            )
        if tag == "identity":
            return 0.2
        if tag == "conductive":
            return signals["conductivity"]
        if tag == "resistant":
            return max(signals["resistance"], signals.get("chaos_pressure", 0.0))
        if tag == "crisis":
            return max(signals["crisis_compression"], signals["loop_lock_risk"])
        if tag == "pre_breach":
            return max(
                signals["pre_breach_pressure"],
                signals["modulation_need"],
                signals.get("dilation_need", 0.0),
                signals.get("irreversible_execution_risk", 0.0),
            )
        if tag == "orthogonal":
            return 0.5 * signals["resistance"] + 0.5 * signals["zone2_openness"]
        if tag == "phase_transition":
            return signals.get("phase_transition_readiness", 0.0)
        if tag == "fold_unfold":
            return min(signals.get("fold_amount", 0.0), signals.get("unfold_breath", 0.0))
        return 0.0

    def _irreversible_actions(self) -> set[str]:
        return {
            "ACTION_CONTINUOUS_SCAN",
            "ACTION_REBUILD_GRAPH",
        }

    def _irreversible_node_locked(self, node: RhythmNode, signals: Dict[str, Any]) -> bool:
        return (
            node.action in self._irreversible_actions()
            and signals.get("execution_lock") == "locked_until_contingency"
        )

    def _bundle(self, selected: RhythmNode, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        state_by_action = {state["node"].action: state for state in states}
        selected_state = state_by_action[selected.action]
        bundle = [
            {
                "action": selected.action,
                "label": selected.label,
                "role": "primary",
                "activated": selected_state["activated"],
                "activation_probability": selected_state["activation_probability"],
                "singularity_crossed": selected_state["singularity_crossed"],
                "singularity_strength": selected_state["singularity_strength"],
                "potential": selected_state["potential"],
                "phase_tags": list(selected.phase_tags),
                "interruptibility": selected.interruptibility,
            }
        ]
        for action in selected.connects_to:
            if action not in self.nodes:
                continue
            state = state_by_action.get(action)
            if not state or not state["activated"]:
                continue
            node = self.nodes[action]
            bundle.append(
                {
                    "action": node.action,
                    "label": node.label,
                    "role": "linked",
                    "activated": state["activated"],
                    "activation_probability": state["activation_probability"],
                    "singularity_crossed": state["singularity_crossed"],
                    "singularity_strength": state["singularity_strength"],
                    "potential": state["potential"],
                    "phase_tags": list(node.phase_tags),
                    "interruptibility": node.interruptibility,
                }
            )
        return bundle

    def _active_edges(self, bundle: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        if not bundle:
            return []
        primary = bundle[0]["action"]
        return [
            {"from": primary, "to": item["action"], "mode": "conductive_link"}
            for item in bundle[1:]
        ]

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _log(self, decision: Dict[str, Any]) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        with self.trace_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(decision, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    root = Path(r"c:\workspace2\shion")
    menu = RhythmNodeMenu(root)
    print(
        json.dumps(
            menu.choose(
                {
                    "transition": "zone2_integrate",
                    "interference": {"label": "destructive", "constructive": 0.3, "destructive": 0.7},
                    "silence_need": 0.82,
                    "action_amplitude": 0.24,
                    "dark_field": {"gravity": 0.5},
                    "zone2": {"openness": 0.6},
                    "geometry": {"curvature": 0.62},
                    "waves": {"field": {"frequency": 0.3, "salience": 0.6}},
                },
                field_status={"salience": 0.6},
                boundary_report={"in_orbit": True},
                log=False,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
