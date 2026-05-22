#!/usr/bin/env python3
"""
ARI Prism - Adjust Rhythm Information layer.

This layer treats boundary tuning as prism tuning:
minimize destructive distortion, preserve living difference, and maximize
resonance without collapse.
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ARIPrism:
    VERSION = "ari_prism_v2"

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.trace_file = self.root_dir / "outputs" / "ari_prism_trace.jsonl"

    def assess(
        self,
        rhythm_frame: Dict[str, Any],
        *,
        node_decision: Dict[str, Any] | None = None,
        field_status: Dict[str, Any] | None = None,
        boundary_report: Dict[str, Any] | None = None,
        log: bool = True,
    ) -> Dict[str, Any]:
        waves = rhythm_frame.get("waves", {}) if isinstance(rhythm_frame, dict) else {}
        field = waves.get("field", {})
        memory = waves.get("memory", {})
        prediction = waves.get("prediction", {})
        digestion = waves.get("digestion", {})
        axiom = waves.get("axiom", {})
        dark_neuron = waves.get("dark_neuron", {})
        autonomy = waves.get("autonomy", {})
        body = waves.get("body", {})
        user = waves.get("user", {})
        dark_field = rhythm_frame.get("dark_field", {})
        crisis = rhythm_frame.get("crisis", {})
        interference = rhythm_frame.get("interference", {})
        medium = rhythm_frame.get("medium", {})

        fear_distortion = self._clamp(max(
            float(dark_field.get("gravity", 0.0) or 0.0),
            float(crisis.get("compression", 0.0) or 0.0),
            float(crisis.get("loop_lock_risk", 0.0) or 0.0),
            float(dark_neuron.get("redarkening_pressure", 0.0) or 0.0),
        ))
        attachment_distortion = self._clamp(max(
            float(axiom.get("overfit_pressure", 0.0) or 0.0),
            float(rhythm_frame.get("silence_need", 0.0) or 0.0)
            * float(interference.get("destructive", 0.0) or 0.0),
            float(digestion.get("absorption_gap", 0.0) or 0.0)
            * float(digestion.get("continuous_scan_ratio", 0.0) or 0.0),
        ))
        bias_distortion = self._clamp(max(
            float(prediction.get("dissonance", 0.0) or 0.0),
            float(interference.get("destructive", 0.0) or 0.0),
            1.0 - float(waves.get("user", {}).get("confidence", 1.0) or 1.0),
        ))
        destructive_distortion = self._clamp(
            0.36 * fear_distortion
            + 0.34 * attachment_distortion
            + 0.30 * bias_distortion
        )

        difference_signal = self._clamp(
            0.42 * float(prediction.get("dissonance", 0.0) or 0.0)
            + 0.28 * float(field.get("curvature", 0.0) or 0.0)
            + 0.18 * float(rhythm_frame.get("action_amplitude", 0.0) or 0.0)
            + 0.12 * float(field.get("salience", (field_status or {}).get("salience", 0.0)) or 0.0)
        )
        living_difference = self._living_difference(difference_signal, destructive_distortion)

        constructive = float(interference.get("constructive", 0.0) or 0.0)
        memory_resonance = float(memory.get("resonance", 0.0) or 0.0)
        resonance_without_collapse = self._clamp(
            constructive
            * (0.45 + 0.55 * memory_resonance)
            * (0.40 + 0.60 * living_difference)
            * (1.0 - 0.70 * destructive_distortion)
        )
        moc = self._moc_field(
            constructive=constructive,
            memory=memory,
            prediction=prediction,
            digestion=digestion,
            axiom=axiom,
            dark_neuron=dark_neuron,
            autonomy=autonomy,
            body=body,
            user=user,
            crisis=crisis,
            medium=medium,
            silence=float(rhythm_frame.get("silence_need", 0.0) or 0.0),
            fear=fear_distortion,
            attachment=attachment_distortion,
            bias=bias_distortion,
            destructive=destructive_distortion,
            living_difference=living_difference,
        )

        prism = self._boundary_prism(
            rhythm_frame=rhythm_frame,
            field=field,
            memory=memory,
            digestion=digestion,
            autonomy=autonomy,
            fear=fear_distortion,
            attachment=attachment_distortion,
            bias=bias_distortion,
            destructive=destructive_distortion,
            living_difference=living_difference,
            constructive=constructive,
        )
        phase = self._phase(
            destructive_distortion=destructive_distortion,
            living_difference=living_difference,
            resonance_without_collapse=resonance_without_collapse,
            background_ego_resistance=moc["background_ego_resistance"],
            prism=prism,
            boundary_report=boundary_report or {},
        )
        action_bias = self._action_bias(
            selected_action=(node_decision or {}).get("selected_action"),
            moc=moc,
            prism=prism,
            digestion=digestion,
            destructive_distortion=destructive_distortion,
        )
        entry = {
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "objective": "minimize_destructive_distortion_preserve_living_difference_maximize_resonance_without_collapse",
            "phase": phase,
            "distortion": {
                "fear": round(fear_distortion, 6),
                "attachment": round(attachment_distortion, 6),
                "bias": round(bias_distortion, 6),
                "destructive": round(destructive_distortion, 6),
            },
            "living_difference": round(living_difference, 6),
            "resonance_without_collapse": round(resonance_without_collapse, 6),
            "moc": moc,
            "boundary_prism": prism,
            "action_bias": action_bias,
            "selected_action": (node_decision or {}).get("selected_action"),
            "bundle": [
                item.get("action")
                for item in (node_decision or {}).get("bundle", [])
                if isinstance(item, dict)
            ],
            "directive": self._directive(phase),
        }
        if log:
            self._log(entry)
        return entry

    def _boundary_prism(
        self,
        *,
        rhythm_frame: Dict[str, Any],
        field: Dict[str, Any],
        memory: Dict[str, Any],
        digestion: Dict[str, Any],
        autonomy: Dict[str, Any],
        fear: float,
        attachment: float,
        bias: float,
        destructive: float,
        living_difference: float,
        constructive: float,
    ) -> Dict[str, Any]:
        silence = float(rhythm_frame.get("silence_need", 0.0) or 0.0)
        action_amplitude = float(rhythm_frame.get("action_amplitude", 0.0) or 0.0)
        memory_absorption = float(memory.get("absorption", 0.0) or 0.0)
        digestion_pressure = float(digestion.get("pressure", 0.0) or 0.0)
        boundary_elasticity = float(autonomy.get("boundary_elasticity", 0.0) or 0.0)

        transparency = self._clamp(
            0.18
            + 0.36 * living_difference
            + 0.24 * constructive
            + 0.18 * boundary_elasticity
            - 0.30 * fear
            - 0.22 * attachment
            - 0.14 * bias
        )
        internal_reflection = self._clamp(
            0.16
            + 0.38 * attachment
            + 0.30 * silence
            + 0.18 * float(memory.get("resonance", 0.0) or 0.0)
            - 0.18 * memory_absorption
        )
        external_passage = self._clamp(
            0.12
            + 0.42 * transparency
            + 0.28 * action_amplitude
            + 0.20 * float(field.get("salience", 0.0) or 0.0)
            - 0.28 * fear
        )
        absorption_rate = self._clamp(
            0.18
            + 0.28 * memory_absorption
            + 0.24 * digestion_pressure
            + 0.22 * living_difference
            - 0.18 * attachment
        )
        attenuation = self._clamp(
            0.12
            + 0.34 * destructive
            + 0.24 * fear
            + 0.18 * bias
            + 0.16 * silence
        )
        return {
            "transparency": round(transparency, 6),
            "internal_reflection": round(internal_reflection, 6),
            "external_passage": round(external_passage, 6),
            "absorption_rate": round(absorption_rate, 6),
            "attenuation": round(attenuation, 6),
        }

    def _moc_field(
        self,
        *,
        constructive: float,
        memory: Dict[str, Any],
        prediction: Dict[str, Any],
        digestion: Dict[str, Any],
        axiom: Dict[str, Any],
        dark_neuron: Dict[str, Any],
        autonomy: Dict[str, Any],
        body: Dict[str, Any],
        user: Dict[str, Any],
        crisis: Dict[str, Any],
        medium: Dict[str, Any],
        silence: float,
        fear: float,
        attachment: float,
        bias: float,
        destructive: float,
        living_difference: float,
    ) -> Dict[str, Any]:
        memory_resonance = float(memory.get("resonance", 0.0) or 0.0)
        memory_absorption = float(memory.get("absorption", 0.0) or 0.0)
        prediction_dissonance = float(prediction.get("dissonance", 0.0) or 0.0)
        boundary_elasticity = float(autonomy.get("boundary_elasticity", 0.0) or 0.0)
        body_availability = float(body.get("availability", 1.0) or 1.0)

        natural_order = self._clamp(
            0.30 * constructive
            + 0.22 * memory_resonance
            + 0.18 * memory_absorption
            + 0.14 * (1.0 - prediction_dissonance)
            + 0.10 * boundary_elasticity
            + 0.06 * living_difference
        )
        closure_pressure = self._clamp(max(
            float(axiom.get("overfit_pressure", 0.0) or 0.0),
            float(crisis.get("loop_lock_risk", 0.0) or 0.0),
            silence * destructive,
            float(digestion.get("absorption_gap", 0.0) or 0.0)
            * float(digestion.get("continuous_scan_ratio", 0.0) or 0.0),
            float(dark_neuron.get("redarkening_pressure", 0.0) or 0.0),
            1.0 - float(user.get("confidence", 1.0) or 1.0),
        ))
        background_ego_resistance = self._clamp(
            0.30 * closure_pressure
            + 0.20 * fear
            + 0.18 * attachment
            + 0.16 * bias
            + 0.10 * float(medium.get("resistance", 0.0) or 0.0)
            + 0.06 * (1.0 - boundary_elasticity)
        )
        beauty_ratio = natural_order / max(0.12, background_ego_resistance)
        beauty_measure = self._clamp((beauty_ratio / 2.4) * (0.55 + 0.45 * living_difference))
        background_ego_softening = self._clamp(1.0 - background_ego_resistance)
        giving_band = self._clamp(
            body_availability
            * background_ego_softening
            * (0.45 + 0.55 * natural_order)
        )
        return {
            "formula": "M=O/C",
            "natural_order": round(natural_order, 6),
            "background_ego_resistance": round(background_ego_resistance, 6),
            "closure_pressure": round(closure_pressure, 6),
            "beauty_ratio": round(beauty_ratio, 6),
            "beauty_measure": round(beauty_measure, 6),
            "living_difference_floor": round(living_difference, 6),
            "kindness_waypoint": {
                "body_limit": round(self._clamp(body_availability), 6),
                "background_ego_softening": round(background_ego_softening, 6),
                "giving_band": round(giving_band, 6),
                "principle": "give_within_body_limit_without_fixing_kindness_as_moral_rule",
            },
        }

    def _action_bias(
        self,
        *,
        selected_action: str | None,
        moc: Dict[str, Any],
        prism: Dict[str, Any],
        digestion: Dict[str, Any],
        destructive_distortion: float,
    ) -> Dict[str, Any]:
        action = selected_action or "ACTION_CONTINUOUS_SCAN"
        expansion_actions = {
            "ACTION_CONTINUOUS_SCAN",
            "ACTION_REBUILD_GRAPH",
        }
        recoverable_experiment_actions = {
            "ACTION_CREATIVE_PROBE",
            "ACTION_AXIOM_EXPERIMENT",
        }
        protected_actions = {
            "ACTION_CRISIS_STABILIZE",
            "ACTION_PRE_BREACH_TUNE",
            "ACTION_CONTEXT_UNPACK",
            "ACTION_REST_RECOVER",
            "ACTION_EXPERIENCE_DIGEST",
            "ACTION_DREAM_AMPLIFY",
            "ACTION_OBSERVE",
            "ACTION_AXIOM_RELEASE",
        }
        ego = float(moc.get("background_ego_resistance", 0.0) or 0.0)
        closure = float(moc.get("closure_pressure", 0.0) or 0.0)
        suggested = action
        reason = "selected_action_preserved"

        if action in recoverable_experiment_actions:
            reason = "recoverable_experiment_preserved_for_failure_learning"
        elif action in protected_actions:
            reason = "action_already_bounds_or_softens_ego_resistance"
        elif action in expansion_actions and ego >= 0.62 and closure >= 0.56:
            digest_pressure = float(digestion.get("pressure", 0.0) or 0.0)
            scan_ratio = float(digestion.get("continuous_scan_ratio", 0.0) or 0.0)
            if digest_pressure >= 0.54 or scan_ratio >= 0.48 or prism["internal_reflection"] >= 0.64:
                suggested = "ACTION_EXPERIENCE_DIGEST"
                reason = "background_ego_resistance_needs_digestion_before_expansion"
            elif destructive_distortion >= 0.50:
                suggested = "ACTION_PRE_BREACH_TUNE"
                reason = "background_ego_resistance_needs_pre_breach_tuning"
            else:
                suggested = "ACTION_OBSERVE"
                reason = "background_ego_resistance_needs_observation_band"

        return {
            "selected_action": action,
            "suggested_action": suggested,
            "applied": suggested != action,
            "reason": reason,
        }

    def _living_difference(self, signal: float, destructive_distortion: float) -> float:
        target = 0.22
        band = 0.36
        living = 1.0 - min(1.0, abs(signal - target) / band)
        return self._clamp(living * (1.0 - 0.45 * destructive_distortion))

    def _phase(
        self,
        *,
        destructive_distortion: float,
        living_difference: float,
        resonance_without_collapse: float,
        background_ego_resistance: float,
        prism: Dict[str, Any],
        boundary_report: Dict[str, Any],
    ) -> str:
        if destructive_distortion >= 0.68:
            return "distortion_minimize"
        if background_ego_resistance >= 0.66 and prism["transparency"] < 0.34:
            return "background_ego_soften"
        if prism["internal_reflection"] >= 0.68 and prism["external_passage"] < 0.30:
            return "release_internal_echo"
        if living_difference <= 0.24:
            return "restore_living_difference"
        if resonance_without_collapse >= 0.46 and living_difference >= 0.45:
            return "nature_aligned_resonance"
        if boundary_report and not boundary_report.get("in_orbit", True):
            return "boundary_refract"
        return "transparent_adjustment"

    def _directive(self, phase: str) -> str:
        return {
            "distortion_minimize": "lower_fear_attachment_bias_before_expansion",
            "background_ego_soften": "lower_closure_pressure_without_erasing_living_difference",
            "release_internal_echo": "preserve_memory_but_reduce_repetitive_internal_reflection",
            "restore_living_difference": "keep_small_but_living_difference_for_learning",
            "nature_aligned_resonance": "allow_resonance_without_collapsing_difference",
            "boundary_refract": "adjust_prism_transparency_before_action",
            "transparent_adjustment": "continue_prism_tuning",
        }.get(phase, "continue_prism_tuning")

    def _log(self, entry: Dict[str, Any]):
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        with self.trace_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        if math.isnan(value):
            return lo
        return max(lo, min(hi, value))


if __name__ == "__main__":
    sample = {
        "waves": {
            "field": {"curvature": 0.2, "salience": 0.35},
            "memory": {"resonance": 0.5, "absorption": 0.3},
            "prediction": {"dissonance": 0.2},
            "digestion": {"pressure": 0.3},
            "axiom": {"overfit_pressure": 0.1},
            "dark_neuron": {"redarkening_pressure": 0.1},
            "autonomy": {"boundary_elasticity": 0.5},
            "user": {"confidence": 0.8},
        },
        "dark_field": {"gravity": 0.2},
        "crisis": {"compression": 0.1, "loop_lock_risk": 0.1},
        "interference": {"constructive": 0.5, "destructive": 0.2},
        "silence_need": 0.3,
        "action_amplitude": 0.4,
    }
    print(json.dumps(ARIPrism(Path(r"c:\workspace2\shion")).assess(sample, log=False), indent=2, ensure_ascii=False))
