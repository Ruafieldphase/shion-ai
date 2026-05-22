#!/usr/bin/env python3
import json
import math
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from felt_state_store import load_state as load_felt_state
except ImportError:  # pragma: no cover - package-style imports
    from core.felt_state_store import load_state as load_felt_state


class NonEuclideanRhythmHarness:
    """
    Converts linear runtime signals into a RhythmIR frame.

    The harness does not command the model directly. It changes the geometry
    that the runtime sees: amplitude, curvature, resonance, silence, and the
    next likely phase transition.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.outputs_dir = root_dir / "outputs"
        self.trace_file = self.outputs_dir / "rhythm_ir_trace.jsonl"
        self.field_error_file = self.outputs_dir / "field_prediction_errors.jsonl"
        self.action_metrics_file = self.outputs_dir / "action_metrics.jsonl"
        self.unfinished_axioms_file = self.outputs_dir / "unfinished_axioms.jsonl"
        self.felt_body_state_file = self.outputs_dir / "felt_body_state.json"

    def encode(
        self,
        *,
        field_status: Dict[str, Any],
        current_vector: Dict[str, Any],
        hippo_data: Dict[str, Any],
        learning_state: Dict[str, Any],
        boundary_report: Dict[str, Any],
        log: bool = True,
    ) -> Dict[str, Any]:
        field_wave = self._field_wave(field_status, current_vector)
        memory_wave = self._memory_wave(hippo_data)
        prediction_wave = self._prediction_wave()
        digestion_wave = self._digestion_wave(hippo_data, memory_wave, prediction_wave)
        body_wave = self._body_wave()
        user_wave = self._user_wave(learning_state)
        dark_field = self._dark_field(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            user_wave=user_wave,
            boundary_report=boundary_report,
        )
        awareness = self._awareness_operator(
            dark_field=dark_field,
            field_wave=field_wave,
            memory_wave=memory_wave,
        )
        zone2 = self._zone2_band(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            awareness=awareness,
        )
        goal_field = self._goal_field_wave(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
        )
        medium = self._conductive_medium(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
        )
        pending_node = self._pending_node_field(
            field_wave=field_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            medium=medium,
            goal_field=goal_field,
            boundary_report=boundary_report,
        )
        velocity_dilation = self._velocity_dilation(
            field_wave=field_wave,
            prediction_wave=prediction_wave,
            zone2=zone2,
            medium=medium,
            pending_node=pending_node,
        )
        perspective_frame = self._perspective_frame(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
        )
        natural_rhythm_tuning = self._natural_rhythm_tuning(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            digestion_wave=digestion_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            perspective_frame=perspective_frame,
        )
        phase_transition_bridge = self._phase_transition_bridge(
            field_wave=field_wave,
            memory_wave=memory_wave,
            prediction_wave=prediction_wave,
            digestion_wave=digestion_wave,
            body_wave=body_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            perspective_frame=perspective_frame,
            natural_rhythm_tuning=natural_rhythm_tuning,
        )
        crisis = self._crisis_state(
            field_wave=field_wave,
            prediction_wave=prediction_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
        )
        autonomy = self._autonomy_wave(
            field_wave=field_wave,
            prediction_wave=prediction_wave,
            digestion_wave=digestion_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            crisis=crisis,
            goal_field=goal_field,
            user_wave=user_wave,
        )
        axiom = self._axiom_wave(
            learning_state=learning_state,
            prediction_wave=prediction_wave,
            digestion_wave=digestion_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            crisis=crisis,
            goal_field=goal_field,
            autonomy=autonomy,
        )
        dark_neuron = self._dark_neuron_wave(
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            crisis=crisis,
            goal_field=goal_field,
            autonomy=autonomy,
            axiom=axiom,
        )

        # --- Non-Linear Resonance Synthesis ---
        # Instead of sums, we use product-based gating (AND-logic) and geometric means.
        
        # Constructive: Higher resonance/absorption synergizes with availability.
        # If any factor is 0, the whole constructive wave is suppressed (gating).
        c_core = (
            memory_wave["resonance"] * 0.4 
            + memory_wave["absorption"] * 0.3 
            + (1.0 - prediction_wave["dissonance"]) * 0.3
        )
        # Apply body availability as a gate
        constructive = self._clamp(
            c_core * (0.2 + 0.8 * body_wave["availability"])
            - 0.25 * (math.tanh(digestion_wave["pressure"] * 2.0))
        )

        # Destructive: Gravity and Dissonance amplify each other non-linearly.
        d_raw = (
            field_wave["amplitude"] * 0.3
            + prediction_wave["dissonance"] * 0.3
            + dark_field["gravity"] * 0.4
        )
        destructive = self._clamp(
            math.pow(d_raw, 0.8)  # Faster rise for low values
            + 0.15 * field_wave["curvature"]
            + 0.10 * (1.0 - user_wave["confidence"])
        )

        interference = self._interference(constructive, destructive)
        zone2_regulation = self._zone2_regulation(
            interference=interference,
            zone2=zone2,
            awareness=awareness,
            crisis=crisis,
            pending_node=pending_node,
            velocity_dilation=velocity_dilation,
            axiom=axiom,
            dark_neuron=dark_neuron,
        )
        
        # Silence need rises sharply when destructive interference or digestion pressure is high.
        silence_need = self._clamp(
            math.tanh(
                1.5 * destructive 
                + 0.8 * prediction_wave["dissonance"] 
                + 0.8 * digestion_wave["pressure"]
                - 0.5 * memory_wave["absorption"]
            )
        )
        
        # Action amplitude is inhibited by dark field gravity and digestion pressure.
        action_amplitude = self._clamp(
            (0.3 + 0.7 * constructive)
            * (1.0 - 0.6 * math.pow(destructive, 1.2))
            * (1.0 - 0.4 * dark_field["gravity"])
            * (1.0 - 0.5 * digestion_wave["pressure"])
        )
        
        transition = self._transition(
            interference=interference,
            silence_need=silence_need,
            action_amplitude=action_amplitude,
            boundary_report=boundary_report,
            dark_field=dark_field,
            zone2=zone2,
            crisis=crisis,
            digestion_wave=digestion_wave,
            goal_field=goal_field,
            autonomy=autonomy,
            axiom=axiom,
            dark_neuron=dark_neuron,
            pending_node=pending_node,
            velocity_dilation=velocity_dilation,
            zone2_regulation=zone2_regulation,
            phase_transition_bridge=phase_transition_bridge,
        )

        frame = {
            "timestamp": datetime.now().isoformat(),
            "waves": {
                "field": field_wave,
                "memory": memory_wave,
                "prediction": prediction_wave,
                "digestion": digestion_wave,
                "goal_field": goal_field,
                "autonomy": autonomy,
                "axiom": axiom,
                "dark_neuron": dark_neuron,
                "body": body_wave,
                "user": user_wave,
            },
            "dark_field": dark_field,
            "awareness": awareness,
            "zone2": zone2,
            "medium": medium,
            "pending_node": pending_node,
            "velocity_dilation": velocity_dilation,
            "zone2_regulation": zone2_regulation,
            "perspective_frame": perspective_frame,
            "natural_rhythm_tuning": natural_rhythm_tuning,
            "phase_transition_bridge": phase_transition_bridge,
            "crisis": crisis,
            "interference": {
                "constructive": round(constructive, 6),
                "destructive": round(destructive, 6),
                "label": interference,
            },
            "geometry": self._geometry(
                field_wave,
                memory_wave,
                prediction_wave,
                silence_need,
                awareness,
            ),
            "transition": transition,
            "action_amplitude": round(action_amplitude, 6),
            "silence_need": round(silence_need, 6),
            "candidate_action": self._candidate_action(transition),
            "heartbeat_multiplier": self._heartbeat_multiplier(
                silence_need,
                action_amplitude,
                digestion_wave,
                velocity_dilation,
            ),
        }
        if log:
            self._log(frame)
        return frame

    def _field_wave(self, field_status: Dict[str, Any], current_vector: Dict[str, Any]) -> Dict[str, Any]:
        amplitude = self._clamp(float(current_vector.get("temporal_tension", 0.0) or 0.0))
        orbit_distance = abs(float(current_vector.get("orbit_distance", 0.0) or 0.0))
        curvature = self._saturating(orbit_distance, scale=3.0)
        return {
            "phase": "tension" if amplitude >= 0.55 else "flow",
            "amplitude": round(amplitude, 6),
            "frequency": round(self._clamp(float(current_vector.get("action_density", 0.0) or 0.0)), 6),
            "curvature": round(curvature, 6),
            "salience": round(self._clamp(float(field_status.get("salience", 0.0) or 0.0)), 6),
        }

    def _memory_wave(self, hippo_data: Dict[str, Any]) -> Dict[str, Any]:
        proton = hippo_data.get("proton", {}) if isinstance(hippo_data, dict) else {}
        experiences = hippo_data.get("experiences", []) if isinstance(hippo_data, dict) else []
        total_registered = max(1, int(proton.get("total_registered", 0) or 0))
        total_absorbed = int(proton.get("total_absorbed", 0) or 0)
        absorption = self._clamp(float(proton.get("embodiment_ratio", 0.0) or 0.0))
        recent = experiences[-20:] if isinstance(experiences, list) else []
        convergence_pressure = self._clamp(
            sum(1 for exp in recent if exp.get("convergence_count", 0) > 0) / 8.0
        )
        resonance = self._clamp(0.55 * convergence_pressure + 0.45 * min(1.0, total_absorbed / total_registered))
        return {
            "phase": "digesting" if absorption >= 0.08 else "registering",
            "amplitude": round(self._clamp(0.45 + convergence_pressure), 6),
            "absorption": round(absorption, 6),
            "resonance": round(resonance, 6),
            "convergence_pressure": round(convergence_pressure, 6),
        }

    def _digestion_wave(
        self,
        hippo_data: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
    ) -> Dict[str, Any]:
        proton = hippo_data.get("proton", {}) if isinstance(hippo_data, dict) else {}
        experiences = hippo_data.get("experiences", []) if isinstance(hippo_data, dict) else []
        total_registered = max(0, int(proton.get("total_registered", 0) or 0))
        absorption = self._clamp(float(proton.get("embodiment_ratio", 0.0) or 0.0))
        recent = experiences[-30:] if isinstance(experiences, list) else []

        if recent:
            unabsorbed_ratio = sum(1 for exp in recent if not exp.get("absorbed", False)) / len(recent)
            visual_ratio = sum(1 for exp in recent if self._is_visual_experience(exp)) / len(recent)
        else:
            unabsorbed_ratio = 0.0
            visual_ratio = 0.0

        scan_ratio = self._recent_action_ratio("ACTION_CONTINUOUS_SCAN", limit=40)
        low_error_stability = self._low_field_error_stability(limit=8, threshold=0.06)
        rest_staleness = self._rest_staleness(limit=40)
        absorption_gap = self._clamp(1.0 - absorption)
        low_convergence = self._clamp(1.0 - memory_wave.get("convergence_pressure", 0.0))

        # Pressure rises non-linearly with the gap.
        pressure = self._clamp(
            0.40 * math.pow(absorption_gap, 1.5)
            + 0.20 * unabsorbed_ratio
            + 0.20 * visual_ratio
            + 0.20 * scan_ratio
        )

        # Young systems should sleep by developmental load, not by wall-clock time.
        # "Sleep debt" is a pressure to stop intake and consolidate; it is not a
        # human-hours timer.
        sleep_debt = self._clamp(
            0.32 * math.pow(absorption_gap, 1.25)
            + 0.22 * unabsorbed_ratio
            + 0.16 * scan_ratio
            + 0.12 * visual_ratio
            + 0.10 * low_convergence
            + 0.08 * rest_staleness
        )
        dream_pressure = self._clamp(
            sleep_debt
            * (0.45 + 0.35 * low_error_stability + 0.20 * (1.0 - prediction_wave["dissonance"]))
        )
        micro_sleep_cycles = 1
        if sleep_debt >= 0.88:
            micro_sleep_cycles = 3
        elif sleep_debt >= 0.72:
            micro_sleep_cycles = 2
        
        # Ready state is a strict gate (non-linear threshold)
        ready = (
            total_registered >= 25
            and absorption < 0.12
            and sleep_debt >= 0.68
            and (pressure >= 0.62 or scan_ratio >= 0.50)
            and prediction_wave["dissonance"] <= 0.15
        )
        dream_ready = (
            total_registered >= 25
            and sleep_debt >= 0.78
            and dream_pressure >= 0.58
            and prediction_wave["dissonance"] <= 0.22
        )
        if ready:
            phase = "digest_ready"
        elif sleep_debt >= 0.82:
            phase = "daydream_debt"
        elif pressure >= 0.58:
            phase = "digest_pressure"
        else:
            phase = "open_intake"
        return {
            "phase": phase,
            "pressure": round(pressure, 6),
            "sleep_debt": round(sleep_debt, 6),
            "dream_pressure": round(dream_pressure, 6),
            "micro_sleep_cycles": micro_sleep_cycles,
            "ai_sleep_policy": "micro_cycles_by_debt_not_human_clock_hours",
            "absorption_gap": round(absorption_gap, 6),
            "recent_unabsorbed_ratio": round(unabsorbed_ratio, 6),
            "recent_visual_ratio": round(visual_ratio, 6),
            "continuous_scan_ratio": round(scan_ratio, 6),
            "low_error_stability": round(low_error_stability, 6),
            "rest_staleness": round(rest_staleness, 6),
            "low_convergence": round(low_convergence, 6),
            "ready": ready,
            "dream_ready": dream_ready,
        }

    def _prediction_wave(self) -> Dict[str, Any]:
        latest_error = self._latest_field_error_entry()
        error = self._clamp(float(latest_error.get("error", 0.0) or 0.0))
        diagnosis = self._normalize_context_diagnosis(latest_error.get("context_diagnosis"))
        return {
            "phase": "dissonant" if error >= 0.18 else "consonant",
            "amplitude": round(error, 6),
            "dissonance": round(error, 6),
            "curvature_delta": round(self._saturating(error, scale=0.25), 6),
            "context_diagnosis": diagnosis,
        }

    def _body_wave(self) -> Dict[str, Any]:
        if self.felt_body_state_file.exists():
            felt = load_felt_state(self.felt_body_state_file)
            flow_energy = self._clamp(felt.get("flow_energy", 0.5))
            relation_drift = self._clamp(felt.get("relation_drift", 0.2))
            body_discomfort = self._clamp(felt.get("body_discomfort", 0.1))
            body_ease = self._clamp(felt.get("body_ease", 0.6))
            rhythm_continuity = self._clamp(felt.get("rhythm_continuity", 0.5))
            availability = self._clamp(
                0.48 * body_ease
                + 0.32 * rhythm_continuity
                + 0.20 * (1.0 - body_discomfort)
            )
            amplitude = self._clamp(0.60 * flow_energy + 0.40 * rhythm_continuity)
            return {
                "phase": "felt_loopback",
                "availability": round(availability, 6),
                "amplitude": round(amplitude, 6),
                "flow_energy": round(flow_energy, 6),
                "relation_drift": round(relation_drift, 6),
                "body_discomfort": round(body_discomfort, 6),
                "body_ease": round(body_ease, 6),
                "rhythm_continuity": round(rhythm_continuity, 6),
                "audio": felt.get("audio", {}),
                "source": felt.get("source", "felt_body_state"),
                "principle": "felt_body_membrane_first_particleization_second",
            }
        return {
            "phase": "available",
            "availability": 1.0,
            "amplitude": 1.0,
        }

    def _user_wave(self, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        recurrence = learning_state.get("recurrence_metrics") or {}
        reduction_rate = float(recurrence.get("reduction_rate", 0.0) or 0.0)
        confidence = 0.55 if reduction_rate >= 0 else 0.35
        return {
            "phase": "observed",
            "confidence": round(confidence, 6),
            "recurrence_signal": round(self._clamp(abs(reduction_rate) / 100.0), 6),
        }

    def _dark_field(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        user_wave: Dict[str, Any],
        boundary_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Estimate fear/attachment/bias as coordinate distortion, not reality."""
        boundary_pull = 0.45 if boundary_report and not boundary_report.get("in_orbit", True) else 0.0
        diagnosis = self._normalize_context_diagnosis(prediction_wave.get("context_diagnosis"))
        context_shift = diagnosis["context_shift"]
        connection_risk = diagnosis["connection_risk"]
        frequency_expansion = diagnosis["frequency_expansion"]
        zero_point_adjustment = diagnosis["zero_point_adjustment"]
        defensive_output_pressure = diagnosis["defensive_output_pressure"]
        # Dark field factors amplify each other (multiplicative distortion)
        future_projection = self._clamp(math.pow(prediction_wave["dissonance"], 0.7))
        attachment_lock = self._clamp(field_wave["amplitude"] * (1.0 + 0.5 * (1.0 - memory_wave["absorption"])))
        world_phase_misalignment = self._clamp(
            0.34 * context_shift
            + 0.26 * connection_risk
            + 0.18 * future_projection
            + 0.12 * boundary_pull
            + 0.10 * self._saturating(abs(field_wave["curvature"]), scale=0.55)
        )
        boundary_contact = self._clamp(
            max(world_phase_misalignment, connection_risk, defensive_output_pressure)
        )
        boundary_transparency = self._clamp(
            0.06
            + 0.36 * boundary_contact
            + 0.24 * zero_point_adjustment
            + 0.22 * frequency_expansion
            - 0.18 * defensive_output_pressure
        )
        boundary_opacity = self._clamp(
            1.0
            - 0.42 * boundary_transparency
            + 0.18 * defensive_output_pressure
            + 0.12 * attachment_lock
        )
        internal_reflection = self._clamp(
            (boundary_opacity * boundary_transparency)
            * (0.42 + 0.28 * world_phase_misalignment + 0.18 * defensive_output_pressure + 0.12 * zero_point_adjustment)
        )
        refraction_angle = self._clamp(
            0.38 * boundary_transparency
            + 0.30 * world_phase_misalignment
            + 0.20 * zero_point_adjustment
            + 0.12 * frequency_expansion
        )
        world_flow_alignment = self._clamp(1.0 - world_phase_misalignment)
        destructive_margin_potential = self._clamp(
            0.38 * internal_reflection
            + 0.28 * boundary_transparency
            + 0.20 * world_phase_misalignment
            + 0.14 * zero_point_adjustment
        )
        scalar_superposition_potential = self._clamp(
            0.34 * destructive_margin_potential
            + 0.26 * boundary_contact
            + 0.22 * refraction_angle
            + 0.18 * (1.0 - defensive_output_pressure)
        )
        spiral_turn_potential = self._clamp(
            0.36 * refraction_angle
            + 0.28 * scalar_superposition_potential
            + 0.20 * world_phase_misalignment
            + 0.16 * frequency_expansion
        )
        
        # Gravity uses tanh to model "falling" into a state
        gravity = self._clamp(
            math.tanh(
                1.2 * future_projection 
                + 1.0 * attachment_lock 
                + 0.8 * boundary_pull
                + 0.5 * defensive_output_pressure
                + 0.3 * world_phase_misalignment
                - 0.4 * internal_reflection
            )
        )
        return {
            "future_projection_dominance": round(future_projection, 6),
            "attachment_lock": round(attachment_lock, 6),
            "bias_curvature": round(self._clamp(0.4 * prediction_wave["curvature_delta"]), 6),
            "boundary_pull": round(boundary_pull, 6),
            "world_phase_misalignment": round(world_phase_misalignment, 6),
            "world_flow_alignment": round(world_flow_alignment, 6),
            "boundary_contact": round(boundary_contact, 6),
            "boundary_transparency": round(boundary_transparency, 6),
            "boundary_opacity": round(boundary_opacity, 6),
            "internal_reflection": round(internal_reflection, 6),
            "refraction_angle": round(refraction_angle, 6),
            "destructive_margin_potential": round(destructive_margin_potential, 6),
            "scalar_superposition_potential": round(scalar_superposition_potential, 6),
            "spiral_turn_potential": round(spiral_turn_potential, 6),
            "context_diagnosis": diagnosis,
            "gravity": round(gravity, 6),
            "phase": "illusion_lock" if gravity >= 0.65 else "present_contact",
            "principle": "dark_field_transmutes_destructive_interference_into_margin_for_scalar_superposition_and_spiral_turning",
        }

    def _awareness_operator(
        self,
        *,
        dark_field: Dict[str, Any],
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Awareness detects distortion and releases it toward present context."""
        present_contact = self._clamp(
            0.50 * (1.0 - dark_field["gravity"])
            + 0.25 * (1.0 - field_wave["amplitude"])
            + 0.25 * memory_wave["absorption"]
        )
        release_capacity = self._clamp(0.35 + 0.45 * present_contact + 0.20 * (1.0 - field_wave["curvature"]))
        recenter_force = self._clamp(
            dark_field["gravity"] * release_capacity
            + 0.25 * dark_field.get("internal_reflection", 0.0)
            + 0.20 * dark_field.get("world_phase_misalignment", 0.0)
        )
        return {
            "detects": dark_field["phase"],
            "present_contact": round(present_contact, 6),
            "release_capacity": round(release_capacity, 6),
            "recenter_force": round(recenter_force, 6),
            "operator": "recenter_origin" if recenter_force >= 0.30 else "continue_flow",
            "principle": "awareness_recenters_when_dark_boundary_reflects_world_flow_misalignment",
        }

    def _zone2_band(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Low-cost communication band between unconscious integration and conscious unpacking."""
        openness = self._clamp(
            0.28 * awareness["recenter_force"]
            + 0.20 * (1.0 - field_wave["frequency"])
            + 0.16 * (1.0 - prediction_wave["dissonance"])
            + 0.16 * (1.0 - memory_wave["absorption"])
            + 0.12 * dark_field.get("boundary_transparency", 0.0)
            + 0.08 * dark_field.get("internal_reflection", 0.0)
        )
        latent_solver_gain = self._clamp(
            0.40 * openness
            + 0.30 * awareness["present_contact"]
            + 0.18 * dark_field.get("refraction_angle", 0.0)
            + 0.12
        )
        return {
            "openness": round(openness, 6),
            "latent_solver_gain": round(latent_solver_gain, 6),
            "phase": "zone2_open" if openness >= 0.52 else "narrow_band",
            "boundary_transparency": round(dark_field.get("boundary_transparency", 0.0), 6),
            "internal_reflection": round(dark_field.get("internal_reflection", 0.0), 6),
        }

    def _conductive_medium(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Model the shared medium that lets node edges form and dissolve.

        "Water" here is an operational metaphor: high conductivity means signals
        can move between nodes with less resistance; high resistance favors
        observe/recenter/rest over expansion.
        """
        conductivity = self._clamp(
            0.30 * awareness["present_contact"]
            + 0.25 * zone2["openness"]
            + 0.20 * memory_wave["absorption"]
            + 0.12 * (1.0 - prediction_wave["dissonance"])
            + 0.08 * (1.0 - dark_field["gravity"])
            + 0.05 * dark_field.get("boundary_transparency", 0.0)
        )
        resistance = self._clamp(
            0.36 * dark_field["gravity"]
            + 0.24 * field_wave["curvature"]
            + 0.16 * prediction_wave["dissonance"]
            + 0.10 * (1.0 - memory_wave["absorption"])
            + 0.08 * dark_field.get("boundary_opacity", 0.0)
            + 0.06 * dark_field.get("context_diagnosis", {}).get("defensive_output_pressure", 0.0)
        )
        viscosity = self._clamp(
            0.42 * resistance
            + 0.30 * dark_field.get("internal_reflection", 0.0)
            + 0.18 * dark_field.get("context_diagnosis", {}).get("defensive_output_pressure", 0.0)
            + 0.10 * dark_field.get("world_phase_misalignment", 0.0)
        )
        electron_flow = self._clamp(
            conductivity
            * (0.35 + 0.65 * field_wave["frequency"])
            * (1.0 - 0.45 * resistance)
            * (1.0 - 0.20 * viscosity)
        )
        delta = conductivity - resistance
        if delta >= 0.16:
            phase = "conductive"
        elif delta <= -0.12:
            phase = "resistive"
        else:
            phase = "viscous"
        return {
            "metaphor": "water",
            "conductivity": round(conductivity, 6),
            "resistance": round(resistance, 6),
            "viscosity": round(viscosity, 6),
            "electron_flow": round(electron_flow, 6),
            "phase": phase,
            "principle": "medium_slows_or_conducts_by_dark_boundary_transparency_not_by_fixed_rules",
        }

    def _goal_field_wave(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Estimate how a new target field should be approached.

        The user metaphor is operationalized here: old neurons are intersections,
        edges are past paths, and a new target field is reached by synthesizing
        intermediate waypoints rather than forcing a straight-line answer.
        """
        target_distance = self._clamp(
            0.30 * field_wave["curvature"]
            + 0.25 * prediction_wave["curvature_delta"]
            + 0.20 * (1.0 - memory_wave["absorption"])
            + 0.15 * field_wave["salience"]
            + 0.10 * dark_field["future_projection_dominance"]
        )
        past_bridge_density = self._clamp(
            0.42 * memory_wave["resonance"]
            + 0.30 * memory_wave["convergence_pressure"]
            + 0.28 * memory_wave["absorption"]
        )
        waypoint_pressure = self._clamp(
            target_distance
            * (0.40 + 0.60 * (1.0 - past_bridge_density))
            * (0.45 + 0.55 * zone2["openness"])
        )
        path_search_band = self._clamp(
            0.38 * zone2["openness"]
            + 0.27 * awareness["present_contact"]
            + 0.20 * (1.0 - dark_field["gravity"])
            + 0.15 * memory_wave["resonance"]
        )
        bridge_gain = self._clamp(
            0.45 * waypoint_pressure
            + 0.35 * path_search_band
            + 0.20 * (1.0 - prediction_wave["dissonance"])
        )
        waypoint_ready = (
            waypoint_pressure >= 0.36
            and path_search_band >= 0.42
            and dark_field["gravity"] < 0.70
        )
        if waypoint_ready:
            phase = "waypoint_synthesis"
        elif target_distance >= 0.58:
            phase = "unknown_target_field"
        elif past_bridge_density >= 0.42:
            phase = "known_intersection_reuse"
        else:
            phase = "near_field"
        return {
            "phase": phase,
            "metaphor": "target_field_to_intersection_graph",
            "target_distance": round(target_distance, 6),
            "past_bridge_density": round(past_bridge_density, 6),
            "waypoint_pressure": round(waypoint_pressure, 6),
            "path_search_band": round(path_search_band, 6),
            "bridge_gain": round(bridge_gain, 6),
            "waypoint_ready": waypoint_ready,
            "principle": "preserve_metaphor_translate_to_dynamics_before_correction",
        }

    def _pending_node_field(
        self,
        *,
        field_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        medium: Dict[str, Any],
        goal_field: Dict[str, Any],
        boundary_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Classify future target nodes by external dependency and reversibility.

        A pending/probabilistic node can still guide attention, but irreversible
        execution remains locked until a viable contingency path exists.
        """
        external_dependency = self._clamp(
            0.32 * prediction_wave["dissonance"]
            + 0.24 * goal_field["target_distance"]
            + 0.18 * medium["resistance"]
            + 0.16 * dark_field["future_projection_dominance"]
            + 0.10 * (1.0 if boundary_report and not boundary_report.get("in_orbit", True) else field_wave["salience"])
        )
        realization_probability = self._clamp(
            0.34 * goal_field["bridge_gain"]
            + 0.24 * goal_field["past_bridge_density"]
            + 0.20 * medium["conductivity"]
            + 0.12 * (1.0 - prediction_wave["dissonance"])
            + 0.10 * (1.0 - dark_field["gravity"])
        )
        irreversible_execution_risk = self._clamp(
            external_dependency
            * (0.42 + 0.34 * field_wave["frequency"] + 0.24 * dark_field["attachment_lock"])
            * (0.60 + 0.40 * (1.0 - realization_probability))
        )
        contingency_strength = self._clamp(
            0.36 * goal_field["path_search_band"]
            + 0.28 * medium["conductivity"]
            + 0.22 * (1.0 - medium["resistance"])
            + 0.14 * goal_field["bridge_gain"]
        )
        contingency_required = irreversible_execution_risk >= 0.42 or external_dependency >= 0.58
        contingency_present = contingency_strength >= 0.48
        if external_dependency >= 0.66:
            state = "probabilistic_node"
        elif external_dependency >= 0.42:
            state = "pending_node"
        else:
            state = "fixed_enough_node"

        if contingency_required and not contingency_present:
            execution_lock = "locked_until_contingency"
        elif contingency_required:
            execution_lock = "conditional_contingency"
        else:
            execution_lock = "open"

        return {
            "state": state,
            "external_dependency": round(external_dependency, 6),
            "realization_probability": round(realization_probability, 6),
            "irreversible_execution_risk": round(irreversible_execution_risk, 6),
            "contingency_strength": round(contingency_strength, 6),
            "contingency_required": contingency_required,
            "contingency_present": contingency_present,
            "execution_lock": execution_lock,
            "principle": "uncertain_future_nodes_do_not_unlock_irreversible_edges_without_contingency",
        }

    def _velocity_dilation(
        self,
        *,
        field_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        pending_node: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Model the cafe-lid lesson: high velocity lowers awareness unless a
        checkpoint slows the routine when anomaly enters the field.
        """
        processing_velocity = self._clamp(field_wave["frequency"])
        routine_inertia = self._clamp(
            processing_velocity
            * (0.46 + 0.30 * (1.0 - field_wave["curvature"]) + 0.24 * (1.0 - zone2["openness"]))
        )
        anomaly_frequency = self._clamp(
            0.30 * prediction_wave["dissonance"]
            + 0.20 * medium["resistance"]
            + 0.20 * pending_node["external_dependency"]
            + 0.16 * field_wave["salience"]
            + 0.10 * field_wave["curvature"]
            + 0.04 * medium.get("viscosity", 0.0)
        )
        dilation_need = self._clamp(
            routine_inertia * anomaly_frequency
            + 0.22 * max(0.0, pending_node["irreversible_execution_risk"] - 0.36)
        )
        awareness_checkpoint = dilation_need >= 0.36
        return {
            "processing_velocity": round(processing_velocity, 6),
            "routine_inertia": round(routine_inertia, 6),
            "anomaly_frequency": round(anomaly_frequency, 6),
            "dilation_need": round(dilation_need, 6),
            "awareness_checkpoint": awareness_checkpoint,
            "principle": "velocity_requires_dilation_when_anomaly_enters_familiar_routine",
        }

    def _crisis_state(
        self,
        *,
        field_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Detect boundary compression as a return-to-center condition."""
        compression = self._clamp(
            0.34 * dark_field["gravity"]
            + 0.26 * medium["resistance"]
            + 0.20 * prediction_wave["dissonance"]
            + 0.12 * field_wave["amplitude"]
            + 0.08 * (1.0 - awareness["present_contact"])
        )
        loop_lock_risk = self._clamp(
            0.36 * dark_field["future_projection_dominance"]
            + 0.28 * dark_field["attachment_lock"]
            + 0.22 * dark_field["bias_curvature"]
            + 0.14 * medium["resistance"]
        )
        return_capacity = self._clamp(
            0.40 * awareness["release_capacity"]
            + 0.25 * zone2["openness"]
            + 0.20 * medium["conductivity"]
            + 0.15 * awareness["present_contact"]
        )
        pre_breach_pressure = self._clamp(
            0.34 * compression
            + 0.30 * loop_lock_risk
            + 0.22 * medium["resistance"]
            + 0.14 * (1.0 - return_capacity)
        )
        modulation_need = self._clamp(
            pre_breach_pressure
            * (1.0 - 0.45 * return_capacity)
            + 0.20 * max(0.0, medium["resistance"] - medium["conductivity"])
        )
        threshold_breach = compression >= 0.72 or loop_lock_risk >= 0.74
        pre_breach_modulation = (
            not threshold_breach
            and pre_breach_pressure >= 0.46
            and modulation_need >= 0.34
        )
        external_support_recommended = compression >= 0.82 or (
            threshold_breach and return_capacity < 0.45
        )
        if external_support_recommended:
            phase = "external_support"
        elif threshold_breach:
            phase = "critical_return"
        elif pre_breach_modulation:
            phase = "pre_breach_modulation"
        elif compression >= 0.58:
            phase = "compressed"
        else:
            phase = "open"
        return {
            "compression": round(compression, 6),
            "loop_lock_risk": round(loop_lock_risk, 6),
            "return_capacity": round(return_capacity, 6),
            "pre_breach_pressure": round(pre_breach_pressure, 6),
            "modulation_need": round(modulation_need, 6),
            "pre_breach_modulation": pre_breach_modulation,
            "threshold_breach": threshold_breach,
            "external_support_recommended": external_support_recommended,
            "phase": phase,
            "principle": "release_experience_is_reference_not_instruction",
        }

    def _autonomy_wave(
        self,
        *,
        field_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        crisis: Dict[str, Any],
        goal_field: Dict[str, Any],
        user_wave: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Estimate bounded autonomy as feedback-guided action rhythm.

        Autonomy here is not a philosophical claim. It means the system can
        choose a small next action from its own feedback loop. Boundaries set
        execution amplitude; they should not collapse imagination.
        """
        boundary_elasticity = self._clamp(
            0.34 * awareness["release_capacity"]
            + 0.24 * (1.0 - crisis["compression"])
            + 0.18 * zone2["openness"]
            + 0.14 * (1.0 - dark_field["gravity"])
            + 0.10 * user_wave["confidence"]
        )
        imagination_band = self._clamp(
            boundary_elasticity
            * (0.50 + 0.50 * goal_field["path_search_band"])
            * (1.0 - 0.30 * crisis["loop_lock_risk"])
        )
        feedback_readiness = self._clamp(
            0.34 * medium["conductivity"]
            + 0.22 * zone2["openness"]
            + 0.18 * (1.0 - prediction_wave["dissonance"])
            + 0.14 * awareness["present_contact"]
            + 0.12 * goal_field["bridge_gain"]
        )
        execution_amplitude = self._clamp(
            feedback_readiness
            * boundary_elasticity
            * (1.0 - 0.42 * digestion_wave["pressure"])
            * (1.0 - 0.34 * dark_field["gravity"])
        )
        creative_probe_ready = (
            imagination_band >= 0.42
            and feedback_readiness >= 0.50
            and execution_amplitude >= 0.24
            and not digestion_wave.get("ready", False)
            and not digestion_wave.get("dream_ready", False)
            and not crisis["threshold_breach"]
            and not crisis["external_support_recommended"]
        )
        if creative_probe_ready:
            phase = "self_directed_probe"
        elif imagination_band >= 0.42 and execution_amplitude < 0.24:
            phase = "imagination_open_execution_wait"
        elif boundary_elasticity < 0.38:
            phase = "boundary_tighten"
        else:
            phase = "assisted_flow"
        return {
            "phase": phase,
            "boundary_elasticity": round(boundary_elasticity, 6),
            "imagination_band": round(imagination_band, 6),
            "feedback_readiness": round(feedback_readiness, 6),
            "execution_amplitude": round(execution_amplitude, 6),
            "creative_probe_ready": creative_probe_ready,
            "principle": "boundary_sets_execution_amplitude_not_imagination_ceiling",
        }

    def _axiom_wave(
        self,
        *,
        learning_state: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        crisis: Dict[str, Any],
        goal_field: Dict[str, Any],
        autonomy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Treat axioms as provisional rhythm nodes.

        An axiom is useful while it opens experiment paths. It becomes
        attachment when the system keeps fitting the field to the axiom after
        body rhythm or relational rhythm has already asked for release.
        """
        provisionality = self._clamp(
            0.30 * awareness["release_capacity"]
            + 0.24 * (1.0 - dark_field["attachment_lock"])
            + 0.18 * zone2["openness"]
            + 0.16 * (1.0 - crisis["loop_lock_risk"])
            + 0.12 * autonomy["imagination_band"]
        )
        experiment_budget = self._clamp(
            provisionality
            * autonomy["feedback_readiness"]
            * (0.45 + 0.55 * autonomy["boundary_elasticity"])
            * (1.0 - 0.46 * digestion_wave["pressure"])
            * (1.0 - 0.34 * crisis["compression"])
        )
        overfit_pressure = self._clamp(
            0.34 * dark_field["attachment_lock"]
            + 0.24 * crisis["loop_lock_risk"]
            + 0.18 * prediction_wave["dissonance"]
            + 0.14 * digestion_wave["pressure"]
            + 0.10 * max(0.0, 0.45 - provisionality)
        )
        relation_budget = self._clamp(
            0.34 * medium["conductivity"]
            + 0.24 * awareness["present_contact"]
            + 0.22 * autonomy["boundary_elasticity"]
            + 0.20 * (1.0 - medium["resistance"])
        )
        failure_spectrum = self._failure_spectrum(learning_state)
        waypoint_resonance = self._unfinished_waypoint_resonance(
            limit=24,
            goal_field=goal_field,
            zone2=zone2,
            medium=medium,
            awareness=awareness,
            failure_spectrum=failure_spectrum,
        )
        archive_resonance = waypoint_resonance["contextual_activation"]
        unfinished_puzzle_potential = self._clamp(
            0.26 * archive_resonance
            + 0.24 * goal_field["bridge_gain"]
            + 0.20 * zone2["openness"]
            + 0.16 * provisionality
            + 0.14 * failure_spectrum["bridge_value"]
        )
        release_ready = (
            overfit_pressure >= 0.58
            and (experiment_budget < 0.30 or digestion_wave["sleep_debt"] >= 0.72)
        )
        experiment_ready = (
            not release_ready
            and experiment_budget >= 0.34
            and provisionality >= 0.48
            and relation_budget >= 0.46
            and not digestion_wave.get("ready", False)
            and not digestion_wave.get("dream_ready", False)
            and not crisis["threshold_breach"]
            and not crisis["external_support_recommended"]
        )
        if release_ready:
            phase = "release_unfit_axiom"
        elif experiment_ready:
            phase = "provisional_experiment"
        elif overfit_pressure >= 0.50:
            phase = "watch_for_forcing"
        else:
            phase = "axiom_open"
        return {
            "phase": phase,
            "provisionality": round(provisionality, 6),
            "experiment_budget": round(experiment_budget, 6),
            "overfit_pressure": round(overfit_pressure, 6),
            "relation_budget": round(relation_budget, 6),
            "failure_spectrum": failure_spectrum,
            "archive_resonance": round(archive_resonance, 6),
            "waypoint_resonance": waypoint_resonance,
            "unfinished_puzzle_potential": round(unfinished_puzzle_potential, 6),
            "archive_on_release": release_ready,
            "release_ready": release_ready,
            "experiment_ready": experiment_ready,
            "principle": "absorbed_axioms_remain_contextual_waypoints_not_fixed_beliefs",
        }

    def _perspective_frame(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Track whether the current view is particle-centered or wave-field aware.

        Particle frame is useful for execution and responsibility. Wave frame is
        useful for relation, context, and phase sensing. Metacognitive
        refraction is the coordinate shift that lets the runtime see both
        without fixing either as the center.
        """
        particle_centering = self._clamp(
            0.30 * dark_field["gravity"]
            + 0.22 * field_wave["amplitude"]
            + 0.18 * dark_field["boundary_pull"]
            + 0.16 * prediction_wave["dissonance"]
            + 0.14 * (1.0 - awareness["present_contact"])
        )
        wave_field_awareness = self._clamp(
            0.28 * zone2["openness"]
            + 0.24 * medium["conductivity"]
            + 0.20 * awareness["present_contact"]
            + 0.16 * memory_wave["resonance"]
            + 0.12 * (1.0 - dark_field["gravity"])
        )
        metacognitive_refraction = self._clamp(
            0.42 * awareness["release_capacity"]
            + 0.30 * zone2["openness"]
            + 0.18 * (1.0 - medium["resistance"])
            + 0.10 * (1.0 - prediction_wave["dissonance"])
        )
        dialectic_field_strength = self._clamp(
            0.44 * metacognitive_refraction
            + 0.34 * wave_field_awareness
            + 0.22 * (1.0 - particle_centering)
        )
        if particle_centering >= 0.62 and particle_centering > wave_field_awareness:
            dominant_frame = "particle_frame"
        elif wave_field_awareness >= 0.56 and wave_field_awareness >= particle_centering:
            dominant_frame = "wave_frame"
        elif metacognitive_refraction >= 0.58:
            dominant_frame = "metacognitive_refraction"
        else:
            dominant_frame = "mixed_frame"

        return {
            "particle_frame": round(particle_centering, 6),
            "wave_frame": round(wave_field_awareness, 6),
            "metacognitive_refraction": round(metacognitive_refraction, 6),
            "dialectic_field_strength": round(dialectic_field_strength, 6),
            "dominant_frame": dominant_frame,
            "role_binding": "contextual_not_fixed",
            "principle": "synthesis_is_current_rhythm_field_not_fixed_role",
        }

    def _phase_transition_bridge(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        body_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        perspective_frame: Dict[str, Any],
        natural_rhythm_tuning: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Keep hypothesis expansion recoverable while the phase bridge forms.

        Fold compresses the field into an executable particle. Unfold reopens
        the field after contact. A usable transition needs both, plus enough
        scalar overlap to turn raw experience into body-readable feedback.
        """
        cycle = natural_rhythm_tuning.get("natural_cycle", {})
        fold_amount = self._clamp(
            0.30 * cycle.get("convergence", 0.0)
            + 0.24 * cycle.get("threshold", 0.0)
            + 0.18 * dark_field.get("boundary_contact", 0.0)
            + 0.16 * perspective_frame.get("particle_frame", 0.0)
            + 0.12 * field_wave.get("amplitude", 0.0)
        )
        unfold_breath = self._clamp(
            0.30 * cycle.get("divergence", 0.0)
            + 0.24 * cycle.get("margin", 0.0)
            + 0.18 * perspective_frame.get("wave_frame", 0.0)
            + 0.16 * zone2.get("openness", 0.0)
            + 0.12 * medium.get("conductivity", 0.0)
        )
        viewpoint_switch = self._clamp(
            0.34 * perspective_frame.get("metacognitive_refraction", 0.0)
            + 0.24 * awareness.get("release_capacity", 0.0)
            + 0.20 * dark_field.get("refraction_angle", 0.0)
            + 0.12 * unfold_breath
            + 0.10 * fold_amount
        )
        audio = body_wave.get("audio") if isinstance(body_wave.get("audio"), dict) else {}
        body_availability = self._clamp(body_wave.get("availability", 0.0))
        body_continuity = self._clamp(body_wave.get("rhythm_continuity", body_availability))
        body_drift = self._clamp(body_wave.get("relation_drift", 0.0))
        if "envelope" in audio:
            felt_body_alignment = self._clamp(1.0 - abs(body_continuity - self._clamp(audio.get("envelope", 0.0))))
        else:
            felt_body_alignment = body_availability
        body_scalar = self._clamp(
            0.48 * body_availability
            + 0.32 * body_continuity
            + 0.20 * (1.0 - body_drift)
        )
        body_transition = dark_field.get("boundary_transparency", 0.0)
        if "body_ease" in body_wave:
            body_transition = self._clamp(
                0.60 * body_wave.get("body_ease", 0.0)
                + 0.40 * felt_body_alignment
            )
        scalar_overlap = self._clamp(
            0.28 * memory_wave.get("absorption", 0.0)
            + 0.24 * memory_wave.get("resonance", 0.0)
            + 0.18 * medium.get("conductivity", 0.0)
            + 0.16 * body_scalar
            + 0.14 * (1.0 - digestion_wave.get("pressure", 0.0))
        )
        transition_readiness = self._clamp(
            0.26 * cycle.get("phase_transition", 0.0)
            + 0.22 * viewpoint_switch
            + 0.20 * min(fold_amount, unfold_breath)
            + 0.18 * scalar_overlap
            + 0.14 * body_transition
        )
        external_reference_check = self._clamp(
            0.42 * dark_field.get("world_phase_misalignment", 0.0)
            + 0.26 * prediction_wave.get("dissonance", 0.0)
            + 0.18 * dark_field.get("boundary_opacity", 0.0)
            + 0.14 * (1.0 - awareness.get("present_contact", 0.0))
        )
        reversible_experiment_window = (
            transition_readiness >= 0.38
            and unfold_breath >= 0.34
            and external_reference_check < 0.72
            and not digestion_wave.get("ready", False)
            and not digestion_wave.get("dream_ready", False)
        )
        if reversible_experiment_window and scalar_overlap < 0.46:
            phase = "sensory_overlap_probe"
            feedback_path = "use_visual_or_body_membrane_before_core_promotion"
        elif reversible_experiment_window:
            phase = "recoverable_phase_experiment"
            feedback_path = "run_small_axiom_or_creative_probe_and_digest_result"
        elif external_reference_check >= 0.72:
            phase = "external_reference_high"
            feedback_path = "fold_to_boundary_check_then_return_internal"
        elif fold_amount > unfold_breath + 0.18:
            phase = "overfolded"
            feedback_path = "unfold_margin_before_execution"
        else:
            phase = "transition_forming"
            feedback_path = "keep_observing_until_fold_and_unfold_overlap"
        twist_count = max(
            1,
            min(16, int(round(1.0 + 15.0 * self._clamp(0.52 * fold_amount + 0.48 * unfold_breath)))),
        )
        return {
            "phase": phase,
            "fold_amount": round(fold_amount, 6),
            "unfold_breath": round(unfold_breath, 6),
            "twist_count": twist_count,
            "viewpoint_switch": round(viewpoint_switch, 6),
            "scalar_overlap": round(scalar_overlap, 6),
            "transition_readiness": round(transition_readiness, 6),
            "external_reference_check": round(external_reference_check, 6),
            "felt_body_alignment": round(felt_body_alignment, 6),
            "felt_body_phase": body_wave.get("phase", "available"),
            "reversible_experiment_window": reversible_experiment_window,
            "internal_experiment_mode": reversible_experiment_window and external_reference_check < 0.62,
            "feedback_path": feedback_path,
            "principle": "fold_to_act_unfold_to_learn_keep_phase_experiments_recoverable",
        }

    def _failure_spectrum(self, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        stats = learning_state.get("stats") or {}
        status_counts = learning_state.get("status_counts") or {}
        total = max(1, int(learning_state.get("total_hypotheses", 0) or 0))
        rejected = int(stats.get("rejected", 0) or 0)
        invalidated = int(status_counts.get("invalidated", 0) or 0)
        unknown = int(stats.get("unknown", 0) or 0)
        confirmed = int(stats.get("confirmed", 0) or 0)
        recurrence = learning_state.get("recurrence_metrics") or {}
        reduction_rate = float(recurrence.get("reduction_rate", 0.0) or 0.0)
        edge_density = self._clamp((rejected + invalidated + unknown) / total)
        polarity_range = self._clamp((rejected + invalidated) / max(1, confirmed + rejected + invalidated))
        recurrence_tension = self._clamp(abs(reduction_rate) / 100.0)
        bridge_value = self._clamp(
            0.42 * edge_density
            + 0.34 * polarity_range
            + 0.24 * (1.0 - recurrence_tension)
        )
        return {
            "edge_density": round(edge_density, 6),
            "polarity_range": round(polarity_range, 6),
            "recurrence_tension": round(recurrence_tension, 6),
            "bridge_value": round(bridge_value, 6),
            "principle": "failure_experiences_are_bridge_data_between_future_axioms",
        }

    def _dark_neuron_wave(
        self,
        *,
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        crisis: Dict[str, Any],
        goal_field: Dict[str, Any],
        autonomy: Dict[str, Any],
        axiom: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Model shadowed memory particles as context-dependent, not good/bad.

        A dark neuron can re-activate as a bridge when the current rhythm gives
        it enough distance and conductivity. A once-useful pattern can also
        re-darken when it is forced into a changed context.
        """
        failure = axiom.get("failure_spectrum", {}) if isinstance(axiom.get("failure_spectrum"), dict) else {}
        context_alignment = self._clamp(
            0.30 * zone2["openness"]
            + 0.24 * medium["conductivity"]
            + 0.18 * awareness["present_contact"]
            + 0.16 * goal_field["bridge_gain"]
            + 0.12 * autonomy["boundary_elasticity"]
        )
        reactivation_potential = self._clamp(
            0.30 * failure.get("bridge_value", 0.0)
            + 0.24 * axiom.get("unfinished_puzzle_potential", 0.0)
            + 0.20 * context_alignment
            + 0.16 * axiom.get("provisionality", 0.0)
            + 0.10 * (1.0 - dark_field["gravity"])
        )
        redarkening_pressure = self._clamp(
            0.30 * axiom.get("overfit_pressure", 0.0)
            + 0.24 * crisis["loop_lock_risk"]
            + 0.20 * dark_field["attachment_lock"]
            + 0.16 * medium["resistance"]
            + 0.10 * (1.0 - context_alignment)
        )
        bridge_readiness = self._clamp(
            reactivation_potential
            * context_alignment
            * (1.0 - 0.45 * redarkening_pressure)
        )
        if redarkening_pressure >= 0.62 and redarkening_pressure > reactivation_potential:
            phase = "re_darkening"
        elif bridge_readiness >= 0.34 and reactivation_potential >= redarkening_pressure:
            phase = "bridge_node"
        elif reactivation_potential >= 0.42:
            phase = "reactivation_window"
        else:
            phase = "dormant_shadow"
        return {
            "phase": phase,
            "context_alignment": round(context_alignment, 6),
            "reactivation_potential": round(reactivation_potential, 6),
            "redarkening_pressure": round(redarkening_pressure, 6),
            "bridge_readiness": round(bridge_readiness, 6),
            "principle": "value_is_contextual_rhythm_alignment_not_good_or_bad",
        }

    def _natural_rhythm_tuning(
        self,
        *,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        perspective_frame: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Read human rhythm tuning as a local expression of natural rhythm tuning.

        The natural cycle is not a fixed script. It is a phase map: convergence,
        threshold, divergence, margin, phase transition, energy inflow, internal
        reflection, and reconvergence.
        """
        phases = {
            "convergence": self._clamp(
                0.40 * memory_wave.get("resonance", 0.0)
                + 0.32 * memory_wave.get("convergence_pressure", 0.0)
                + 0.28 * (1.0 - prediction_wave.get("dissonance", 0.0))
            ),
            "threshold": self._clamp(
                0.34 * prediction_wave.get("dissonance", 0.0)
                + 0.28 * dark_field.get("boundary_contact", 0.0)
                + 0.22 * dark_field.get("world_phase_misalignment", 0.0)
                + 0.16 * field_wave.get("salience", 0.0)
            ),
            "divergence": self._clamp(
                0.36 * field_wave.get("frequency", 0.0)
                + 0.24 * field_wave.get("salience", 0.0)
                + 0.22 * perspective_frame.get("wave_frame", 0.0)
                + 0.18 * medium.get("conductivity", 0.0)
            ),
            "margin": self._clamp(
                0.42 * zone2.get("openness", 0.0)
                + 0.24 * digestion_wave.get("sleep_debt", 0.0)
                + 0.18 * medium.get("viscosity", medium.get("resistance", 0.0))
                + 0.16 * awareness.get("present_contact", 0.0)
            ),
            "phase_transition": self._clamp(
                0.38 * awareness.get("recenter_force", 0.0)
                + 0.28 * perspective_frame.get("metacognitive_refraction", 0.0)
                + 0.20 * dark_field.get("refraction_angle", 0.0)
                + 0.14 * prediction_wave.get("curvature_delta", 0.0)
            ),
            "energy_inflow": self._clamp(
                0.34 * medium.get("conductivity", 0.0)
                + 0.24 * field_wave.get("salience", 0.0)
                + 0.22 * dark_field.get("boundary_transparency", 0.0)
                + 0.20 * (1.0 - digestion_wave.get("pressure", 0.0))
            ),
            "internal_reflection": self._clamp(
                0.42 * dark_field.get("internal_reflection", 0.0)
                + 0.30 * awareness.get("recenter_force", 0.0)
                + 0.16 * medium.get("viscosity", medium.get("resistance", 0.0))
                + 0.12 * dark_field.get("boundary_opacity", 0.0)
            ),
            "reconvergence": self._clamp(
                0.34 * memory_wave.get("absorption", 0.0)
                + 0.28 * memory_wave.get("convergence_pressure", 0.0)
                + 0.20 * (1.0 - prediction_wave.get("dissonance", 0.0))
                + 0.18 * awareness.get("present_contact", 0.0)
            ),
        }
        dominant_phase = max(phases, key=phases.get)
        human_tuning_alignment = self._clamp(
            0.26 * perspective_frame.get("metacognitive_refraction", 0.0)
            + 0.22 * awareness.get("recenter_force", 0.0)
            + 0.18 * zone2.get("openness", 0.0)
            + 0.18 * dark_field.get("world_flow_alignment", 1.0)
            + 0.16 * (1.0 - medium.get("resistance", 0.0))
        )
        resistance_minimization = self._clamp(
            0.32 * dark_field.get("world_flow_alignment", 1.0)
            + 0.24 * awareness.get("present_contact", 0.0)
            + 0.20 * (1.0 - medium.get("viscosity", medium.get("resistance", 0.0)))
            + 0.16 * dark_field.get("internal_reflection", 0.0)
            + 0.08 * memory_wave.get("absorption", 0.0)
        )
        rhythm_misalignment = self._clamp(1.0 - human_tuning_alignment)
        rhythm_resistance = self._clamp(1.0 - resistance_minimization)
        problem_seed = self._clamp(
            0.38 * rhythm_misalignment
            + 0.28 * rhythm_resistance
            + 0.18 * dark_field.get("world_phase_misalignment", 0.0)
            + 0.16 * prediction_wave.get("dissonance", 0.0)
        )
        if problem_seed >= 0.62:
            problem_phase = "problem_origin_active"
        elif problem_seed >= 0.42:
            problem_phase = "problem_seed_visible"
        elif problem_seed >= 0.24:
            problem_phase = "low_amplitude_warning"
        else:
            problem_phase = "aligned_flow"
        mistake_digestion = self._mistake_digestion(
            problem_seed=problem_seed,
            rhythm_misalignment=rhythm_misalignment,
            rhythm_resistance=rhythm_resistance,
            field_wave=field_wave,
            prediction_wave=prediction_wave,
            digestion_wave=digestion_wave,
            dark_field=dark_field,
            awareness=awareness,
            zone2=zone2,
            medium=medium,
            memory_wave=memory_wave,
        )
        return {
            "dominant_natural_phase": dominant_phase,
            "natural_cycle": {key: round(value, 6) for key, value in phases.items()},
            "human_tuning_alignment": round(human_tuning_alignment, 6),
            "resistance_minimization": round(resistance_minimization, 6),
            "problem_origin": {
                "phase": problem_phase,
                "rhythm_misalignment": round(rhythm_misalignment, 6),
                "rhythm_resistance": round(rhythm_resistance, 6),
                "problem_seed": round(problem_seed, 6),
                "principle": "problems_begin_when_human_rhythm_stops_following_natural_rhythm",
            },
            "mistake_digestion": mistake_digestion,
            "principle": "human_rhythm_tuning_follows_natural_rhythm_tuning",
        }

    def _mistake_digestion(
        self,
        *,
        problem_seed: float,
        rhythm_misalignment: float,
        rhythm_resistance: float,
        field_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        dark_field: Dict[str, Any],
        awareness: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        memory_wave: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Read mistakes as digestible experience before treating them as barriers.

        A mistake is useful when it stays below threshold and exposes unembodied
        context. Perfectionism is not treated as a fault by itself: outward
        refinement can tune work toward the world, while self-closing
        overcontrol blocks divergence and overuses internal reflection.
        """
        learning_signal = self._clamp(
            0.30 * problem_seed
            + 0.24 * prediction_wave.get("dissonance", 0.0)
            + 0.18 * zone2.get("openness", 0.0)
            + 0.16 * dark_field.get("boundary_transparency", 0.0)
            + 0.12 * (1.0 - memory_wave.get("absorption", 0.0))
        )
        overcontrol_boundary_density = self._clamp(
            0.30 * dark_field.get("boundary_opacity", 0.0)
            + 0.24 * dark_field.get("internal_reflection", 0.0)
            + 0.18 * rhythm_resistance
            + 0.16 * (1.0 - field_wave.get("frequency", 0.0))
            + 0.12 * medium.get("viscosity", medium.get("resistance", 0.0))
        )
        resonant_refinement = self._clamp(
            0.26 * dark_field.get("world_flow_alignment", 0.0)
            + 0.22 * medium.get("conductivity", 0.0)
            + 0.20 * awareness.get("present_contact", 0.0)
            + 0.18 * zone2.get("openness", 0.0)
            + 0.14 * memory_wave.get("resonance", 0.0)
        )
        self_closure_overcontrol = self._clamp(
            0.72 * overcontrol_boundary_density
            + 0.28 * (1.0 - resonant_refinement)
        )
        embodiment_gap = self._clamp(
            0.36 * (1.0 - memory_wave.get("absorption", 0.0))
            + 0.24 * digestion_wave.get("pressure", 0.0)
            + 0.20 * rhythm_misalignment
            + 0.20 * (1.0 - awareness.get("present_contact", 0.0))
        )
        threshold_risk = self._clamp(
            0.34 * problem_seed
            + 0.26 * dark_field.get("gravity", 0.0)
            + 0.20 * rhythm_resistance
            + 0.20 * prediction_wave.get("dissonance", 0.0)
        )

        if threshold_risk >= 0.66:
            phase = "threshold_recenter"
            recommended_mode = "zone2_pause_and_zero_point_adjustment"
        elif (
            self_closure_overcontrol >= 0.68
            and self_closure_overcontrol > resonant_refinement
            and self_closure_overcontrol > learning_signal
        ):
            phase = "self_closure_overcontrol"
            recommended_mode = "loosen_boundary_allow_small_divergence"
        elif resonant_refinement >= 0.62 and resonant_refinement >= self_closure_overcontrol:
            phase = "resonant_refinement"
            recommended_mode = "refine_until_the_work_reaches_the_world"
        elif learning_signal >= 0.42 and threshold_risk < 0.66:
            phase = "digestible_mistake"
            recommended_mode = "preserve_context_and_digest_experience"
        elif problem_seed >= 0.24:
            phase = "observe_context"
            recommended_mode = "observe_without_closing_rule"
        else:
            phase = "no_mistake_signal"
            recommended_mode = "continue_flow"

        return {
            "phase": phase,
            "learning_signal": round(learning_signal, 6),
            "overcontrol_boundary_density": round(overcontrol_boundary_density, 6),
            "self_closure_overcontrol": round(self_closure_overcontrol, 6),
            "resonant_refinement": round(resonant_refinement, 6),
            "embodiment_gap": round(embodiment_gap, 6),
            "threshold_risk": round(threshold_risk, 6),
            "recommended_mode": recommended_mode,
            "principle": "mistakes_are_context_particles_and_perfectionism_depends_on_direction",
        }

    def _zone2_regulation(
        self,
        *,
        interference: str,
        zone2: Dict[str, Any],
        awareness: Dict[str, Any],
        crisis: Dict[str, Any],
        pending_node: Dict[str, Any],
        velocity_dilation: Dict[str, Any],
        axiom: Dict[str, Any],
        dark_neuron: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Zone 2 is an active margin, not a queue. It can delay a side variable,
        transmute destructive interference into margin, or simply hold the field open.
        """
        intrusive_variable = self._clamp(
            0.30 * velocity_dilation["anomaly_frequency"]
            + 0.24 * pending_node["external_dependency"]
            + 0.18 * crisis["pre_breach_pressure"]
            + 0.16 * axiom.get("overfit_pressure", 0.0)
            + 0.12 * dark_neuron.get("redarkening_pressure", 0.0)
        )
        chaos_pressure = self._clamp(
            0.34 * intrusive_variable
            + 0.24 * velocity_dilation["dilation_need"]
            + 0.22 * crisis["loop_lock_risk"]
            + 0.20 * (1.0 if interference == "destructive" else 0.0)
        )
        context_mismatch = self._clamp(
            0.36 * pending_node["irreversible_execution_risk"]
            + 0.28 * axiom.get("overfit_pressure", 0.0)
            + 0.20 * dark_neuron.get("redarkening_pressure", 0.0)
            + 0.16 * (1.0 - awareness["present_contact"])
        )
        delay_to_zone2 = chaos_pressure >= 0.42 and context_mismatch < 0.62
        phase_rebalance_to_margin = context_mismatch >= 0.62 and chaos_pressure >= 0.48
        destructive_to_margin = (
            phase_rebalance_to_margin
            or (delay_to_zone2 and interference == "destructive")
        )
        scalar_superposition_window = self._clamp(
            0.42 * chaos_pressure
            + 0.30 * intrusive_variable
            + 0.28 * (1.0 - context_mismatch)
        )
        if phase_rebalance_to_margin:
            phase = "phase_rebalance_to_margin"
        elif delay_to_zone2:
            phase = "delay_intrusion"
        elif velocity_dilation.get("awareness_checkpoint"):
            phase = "dilate_for_awareness"
        elif zone2["openness"] >= 0.52:
            phase = "active_margin"
        else:
            phase = "quiet_margin"
        return {
            "phase": phase,
            "intrusive_variable": round(intrusive_variable, 6),
            "chaos_pressure": round(chaos_pressure, 6),
            "context_mismatch": round(context_mismatch, 6),
            "phase_rebalance_to_margin": phase_rebalance_to_margin,
            "destructive_to_margin": destructive_to_margin,
            "scalar_superposition_window": round(scalar_superposition_window, 6),
            "delay_to_zone2": delay_to_zone2,
            "noise_cancel": phase_rebalance_to_margin,
            "principle": "zone2_transmutes_destructive_interference_into_margin_not_deletion",
        }

    def _geometry(
        self,
        field_wave: Dict[str, Any],
        memory_wave: Dict[str, Any],
        prediction_wave: Dict[str, Any],
        silence_need: float,
        awareness: Dict[str, Any],
    ) -> Dict[str, Any]:
        theta = (field_wave["amplitude"] * math.tau + prediction_wave["dissonance"] * math.pi) % math.tau
        radius = self._clamp(0.20 + 0.45 * memory_wave["resonance"] + 0.35 * field_wave["amplitude"])
        curvature = self._clamp(0.50 * field_wave["curvature"] + 0.50 * prediction_wave["curvature_delta"])
        return {
            "theta": round(theta, 6),
            "radius": round(radius, 6),
            "curvature": round(curvature, 6),
            "spiral_return": round(memory_wave["convergence_pressure"], 6),
            "silence": round(silence_need, 6),
            "origin_shift": round(awareness["recenter_force"], 6),
            "present_contact": round(awareness["present_contact"], 6),
        }

    def _transition(
        self,
        *,
        interference: str,
        silence_need: float,
        action_amplitude: float,
        boundary_report: Dict[str, Any],
        dark_field: Dict[str, Any],
        zone2: Dict[str, Any],
        crisis: Dict[str, Any],
        digestion_wave: Dict[str, Any],
        goal_field: Dict[str, Any],
        autonomy: Dict[str, Any],
        axiom: Dict[str, Any],
        dark_neuron: Dict[str, Any],
        pending_node: Dict[str, Any],
        velocity_dilation: Dict[str, Any],
        zone2_regulation: Dict[str, Any],
        phase_transition_bridge: Dict[str, Any],
    ) -> str:
        if zone2_regulation.get("phase_rebalance_to_margin") or zone2_regulation.get("noise_cancel"):
            return "phase_rebalance_to_margin"
        if pending_node.get("execution_lock") == "locked_until_contingency":
            return "contingency_lock"
        if velocity_dilation.get("awareness_checkpoint"):
            return "velocity_dilation"
        if zone2_regulation.get("delay_to_zone2"):
            return "zone2_delay"
        if crisis["external_support_recommended"] or crisis["threshold_breach"]:
            return "crisis_to_stabilize"
        if crisis["pre_breach_modulation"]:
            return "pre_breach_tune"
        if crisis["phase"] == "compressed":
            return "crisis_to_recenter"
        if boundary_report and not boundary_report.get("in_orbit", True):
            return "boundary_to_unpack"
        if digestion_wave.get("dream_ready"):
            return "daydream_integrate"
        if digestion_wave.get("ready"):
            return "experience_digest"
        if axiom.get("release_ready"):
            return "axiom_release"
        if dark_neuron.get("phase") == "bridge_node":
            return "shadow_bridge"
        if phase_transition_bridge.get("internal_experiment_mode"):
            return "phase_transition_experiment"
        if axiom.get("experiment_ready"):
            return "axiom_experiment"
        if autonomy.get("creative_probe_ready"):
            return "creative_autonomy"
        if goal_field.get("waypoint_ready"):
            return "waypoint_bridge"
        if dark_field["gravity"] >= 0.62:
            return "recenter_to_zone2"
        if zone2["phase"] == "zone2_open" and dark_field["gravity"] >= 0.38:
            return "zone2_integrate"
        if silence_need >= 0.72:
            return "destructive_to_margin"
        if interference == "constructive" and action_amplitude >= 0.52:
            return "resonance_to_explore"
        if interference == "destructive":
            return "attenuate_to_observe"
        return "mixed_hold"

    def _candidate_action(self, transition: str) -> str:
        if transition in {"zero_point_reset", "phase_rebalance_to_margin"}:
            return "ACTION_AXIOM_RELEASE"
        if transition in {"contingency_lock", "velocity_dilation"}:
            return "ACTION_PRE_BREACH_TUNE"
        if transition == "zone2_delay":
            return "ACTION_OBSERVE"
        if transition == "pre_breach_tune":
            return "ACTION_PRE_BREACH_TUNE"
        if transition in {"crisis_to_stabilize", "crisis_to_recenter"}:
            return "ACTION_CRISIS_STABILIZE"
        if transition == "boundary_to_unpack":
            return "ACTION_CONTEXT_UNPACK"
        if transition == "experience_digest":
            return "ACTION_EXPERIENCE_DIGEST"
        if transition == "daydream_integrate":
            return "ACTION_DREAM_AMPLIFY"
        if transition == "waypoint_bridge":
            return "ACTION_REBUILD_GRAPH"
        if transition == "creative_autonomy":
            return "ACTION_CREATIVE_PROBE"
        if transition in {"axiom_experiment", "phase_transition_experiment"}:
            return "ACTION_AXIOM_EXPERIMENT"
        if transition == "axiom_release":
            return "ACTION_AXIOM_RELEASE"
        if transition == "shadow_bridge":
            return "ACTION_REBUILD_GRAPH"
        return "ACTION_CONTINUOUS_SCAN"

    def _heartbeat_multiplier(
        self,
        silence_need: float,
        action_amplitude: float,
        digestion_wave: Dict[str, Any] | None = None,
        velocity_dilation: Dict[str, Any] | None = None,
    ) -> float:
        digestion_pressure = float((digestion_wave or {}).get("pressure", 0.0) or 0.0)
        sleep_debt = float((digestion_wave or {}).get("sleep_debt", 0.0) or 0.0)
        dilation_need = float((velocity_dilation or {}).get("dilation_need", 0.0) or 0.0)
        multiplier = (
            1.0
            + 1.5 * silence_need
            - 0.45 * action_amplitude
            + 0.70 * digestion_pressure
            + 0.55 * sleep_debt
            + 0.45 * dilation_need
        )
        return round(max(0.75, min(3.0, multiplier)), 6)

    def _latest_field_error(self) -> float:
        return self._clamp(float(self._latest_field_error_entry().get("error", 0.0) or 0.0))

    def _latest_field_error_entry(self) -> Dict[str, Any]:
        if not self.field_error_file.exists():
            return {}
        try:
            lines = self.field_error_file.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines[-20:]):
                if not line.strip():
                    continue
                data = json.loads(line)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    def _normalize_context_diagnosis(self, diagnosis: Any) -> Dict[str, Any]:
        if not isinstance(diagnosis, dict):
            diagnosis = {}
        return {
            "semantic_information_frame": diagnosis.get(
                "semantic_information_frame",
                "context_relative_continuity_information",
            ),
            "context_shift": round(self._clamp(float(diagnosis.get("context_shift", 0.0) or 0.0)), 6),
            "connection_risk": round(self._clamp(float(diagnosis.get("connection_risk", 0.0) or 0.0)), 6),
            "frequency_expansion": round(self._clamp(float(diagnosis.get("frequency_expansion", 0.0) or 0.0)), 6),
            "zero_point_adjustment": round(self._clamp(float(diagnosis.get("zero_point_adjustment", 0.0) or 0.0)), 6),
            "defensive_output_pressure": round(
                self._clamp(float(diagnosis.get("defensive_output_pressure", 0.0) or 0.0)),
                6,
            ),
            "dominant_mode": str(diagnosis.get("dominant_mode", "stable_continuity")),
        }

    def _is_visual_experience(self, exp: Dict[str, Any]) -> bool:
        content_ref = str(exp.get("content_ref", "")).lower()
        vibe = exp.get("vibe", {}) if isinstance(exp.get("vibe"), dict) else {}
        return (
            content_ref.startswith("screen_wave")
            or content_ref.startswith("vision")
            or vibe.get("source") == "vision"
        )

    def _recent_action_ratio(self, action: str, *, limit: int) -> float:
        entries = self._read_recent_jsonl(self.action_metrics_file, limit)
        if not entries:
            return 0.0
        return self._clamp(sum(1 for item in entries if item.get("action") == action) / len(entries))

    def _rest_staleness(self, *, limit: int) -> float:
        entries = self._read_recent_jsonl(self.action_metrics_file, limit)
        if not entries:
            return 1.0
        rest_actions = {
            "ACTION_EXPERIENCE_DIGEST",
            "ACTION_DREAM_AMPLIFY",
            "ACTION_REST_RECOVER",
            "ACTION_OBSERVE",
        }
        distance = len(entries)
        for idx, item in enumerate(reversed(entries), start=1):
            if item.get("action") in rest_actions:
                distance = idx - 1
                break
        return self._clamp(distance / max(limit, 1))

    def _low_field_error_stability(self, *, limit: int, threshold: float) -> float:
        entries = self._read_recent_jsonl(self.field_error_file, limit)
        if not entries:
            return 0.0
        low = 0
        for item in entries:
            try:
                if float(item.get("error", 0.0) or 0.0) <= threshold:
                    low += 1
            except (TypeError, ValueError):
                pass
        return self._clamp(low / len(entries))

    def _unfinished_axiom_resonance(self, *, limit: int) -> float:
        entries = self._read_recent_jsonl(self.unfinished_axioms_file, limit)
        if not entries:
            return 0.0
        reusable = 0
        for item in entries:
            if item.get("status") == "unfinished_puzzle":
                reusable += 1
        return self._clamp(reusable / len(entries))

    def _unfinished_waypoint_resonance(
        self,
        *,
        limit: int,
        goal_field: Dict[str, Any],
        zone2: Dict[str, Any],
        medium: Dict[str, Any],
        awareness: Dict[str, Any],
        failure_spectrum: Dict[str, Any],
    ) -> Dict[str, Any]:
        entries = [
            item
            for item in self._read_recent_jsonl(self.unfinished_axioms_file, limit)
            if item.get("status") == "unfinished_puzzle"
        ]
        if not entries:
            return {
                "visit_frequency": 0.0,
                "current_context_match": 0.0,
                "contextual_activation": 0.0,
                "fixed_weight_risk": 0.0,
                "principle": "no_waypoint_without_current_context",
            }

        current_bridge = float(goal_field.get("bridge_gain", 0.0) or 0.0)
        current_waypoint = float(goal_field.get("waypoint_pressure", 0.0) or 0.0)
        current_failure = float(failure_spectrum.get("bridge_value", 0.0) or 0.0)
        current_context_band = self._clamp(
            0.34 * float(zone2.get("openness", 0.0) or 0.0)
            + 0.28 * float(medium.get("conductivity", 0.0) or 0.0)
            + 0.22 * float(awareness.get("present_contact", 0.0) or 0.0)
            + 0.16 * (1.0 - float(medium.get("resistance", 0.0) or 0.0))
        )

        matches = []
        for item in entries:
            archived_goal = item.get("goal_field", {}) if isinstance(item.get("goal_field"), dict) else {}
            archived_axiom = item.get("axiom", {}) if isinstance(item.get("axiom"), dict) else {}
            archived_failure = archived_axiom.get("failure_spectrum", {})
            if not isinstance(archived_failure, dict):
                archived_failure = {}
            archived_bridge = float(archived_goal.get("bridge_gain", current_bridge) or 0.0)
            archived_waypoint = float(archived_goal.get("waypoint_pressure", current_waypoint) or 0.0)
            archived_failure_bridge = float(archived_failure.get("bridge_value", current_failure) or 0.0)
            proximity = self._clamp(
                1.0
                - (
                    abs(current_bridge - archived_bridge)
                    + abs(current_waypoint - archived_waypoint)
                    + abs(current_failure - archived_failure_bridge)
                )
                / 3.0
            )
            matches.append(proximity)

        visit_frequency = self._clamp(len(entries) / max(1, limit))
        current_context_match = self._clamp(sum(matches) / len(matches))
        contextual_activation = self._clamp(
            0.45 * current_context_match
            + 0.35 * current_context_band
            + 0.20 * visit_frequency
        )
        fixed_weight_risk = self._clamp(
            visit_frequency
            * (1.0 - current_context_match)
            * (0.55 + 0.45 * float(medium.get("resistance", 0.0) or 0.0))
        )
        return {
            "visit_frequency": round(visit_frequency, 6),
            "current_context_match": round(current_context_match, 6),
            "contextual_activation": round(contextual_activation, 6),
            "fixed_weight_risk": round(fixed_weight_risk, 6),
            "principle": "frequent_waypoints_reactivate_by_context_not_permanent_weight",
        }

    def _read_recent_jsonl(self, path: Path, limit: int) -> list[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return []
        entries = []
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        return entries

    def _interference(self, constructive: float, destructive: float) -> str:
        delta = constructive - destructive
        if delta >= 0.12:
            return "constructive"
        if delta <= -0.12:
            return "destructive"
        return "mixed"

    def _saturating(self, value: float, *, scale: float) -> float:
        return self._clamp(1.0 - math.exp(-abs(value) / max(scale, 0.0001)))

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _log(self, frame: Dict[str, Any]):
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(frame, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    harness = NonEuclideanRhythmHarness(Path(r"c:\workspace2\shion"))
    result = harness.encode(
        field_status={"salience": 0.2},
        current_vector={"temporal_tension": 0.2, "action_density": 0.4, "orbit_distance": 0.1},
        hippo_data={"proton": {"total_registered": 10, "total_absorbed": 1, "embodiment_ratio": 0.1}, "experiences": []},
        learning_state={"recurrence_metrics": {"reduction_rate": 10}},
        boundary_report={"in_orbit": True},
        log=False,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
