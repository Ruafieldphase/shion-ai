import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rhythm_harness import NonEuclideanRhythmHarness
from felt_state_store import save_state


class RhythmHarnessPerspectiveTests(unittest.TestCase):
    def test_perspective_frame_tracks_particle_and_wave_views(self):
        with tempfile.TemporaryDirectory() as td:
            harness = NonEuclideanRhythmHarness(Path(td))

            particle = harness._perspective_frame(
                field_wave={"amplitude": 0.78},
                memory_wave={"resonance": 0.18},
                prediction_wave={"dissonance": 0.62},
                dark_field={"gravity": 0.84, "boundary_pull": 0.45},
                awareness={"present_contact": 0.22, "release_capacity": 0.34},
                zone2={"openness": 0.24},
                medium={"conductivity": 0.18, "resistance": 0.74},
            )
            wave = harness._perspective_frame(
                field_wave={"amplitude": 0.12},
                memory_wave={"resonance": 0.64},
                prediction_wave={"dissonance": 0.08},
                dark_field={"gravity": 0.18, "boundary_pull": 0.0},
                awareness={"present_contact": 0.76, "release_capacity": 0.82},
                zone2={"openness": 0.68},
                medium={"conductivity": 0.72, "resistance": 0.18},
            )

            self.assertEqual(particle["dominant_frame"], "particle_frame")
            self.assertGreater(particle["particle_frame"], particle["wave_frame"])
            self.assertGreater(wave["wave_frame"], wave["particle_frame"])
            self.assertGreater(wave["metacognitive_refraction"], particle["metacognitive_refraction"])
            self.assertEqual(wave["role_binding"], "contextual_not_fixed")
            self.assertEqual(
                wave["principle"],
                "synthesis_is_current_rhythm_field_not_fixed_role",
            )

    def test_uncertain_future_node_triggers_contingency_lock_and_dilation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "field_prediction_errors.jsonl").write_text(
                '{"error": 0.72}\n',
                encoding="utf-8",
            )
            harness = NonEuclideanRhythmHarness(root)

            frame = harness.encode(
                field_status={"salience": 0.84},
                current_vector={
                    "temporal_tension": 0.82,
                    "action_density": 0.95,
                    "orbit_distance": 2.4,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 4,
                        "embodiment_ratio": 0.033333,
                    },
                    "experiences": [],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": -12}},
                boundary_report={"in_orbit": False},
                log=False,
            )

            self.assertEqual(frame["pending_node"]["execution_lock"], "locked_until_contingency")
            self.assertIn(frame["pending_node"]["state"], {"pending_node", "probabilistic_node"})
            self.assertTrue(frame["velocity_dilation"]["awareness_checkpoint"])
            self.assertIn(frame["transition"], {"contingency_lock", "phase_rebalance_to_margin"})
            if frame["transition"] == "phase_rebalance_to_margin":
                self.assertEqual(frame["candidate_action"], "ACTION_AXIOM_RELEASE")
            else:
                self.assertEqual(frame["candidate_action"], "ACTION_PRE_BREACH_TUNE")
            self.assertEqual(
                frame["zone2_regulation"]["principle"],
                "zone2_transmutes_destructive_interference_into_margin_not_deletion",
            )

    def test_dark_field_unfolds_defensive_pressure_as_boundary_viscosity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            self._write_field_error(
                outputs,
                error=0.34,
                diagnosis={
                    "context_shift": 0.28,
                    "connection_risk": 0.86,
                    "frequency_expansion": 0.12,
                    "zero_point_adjustment": 0.44,
                    "defensive_output_pressure": 0.82,
                    "dominant_mode": "defensive_output_pressure",
                },
            )

            frame = NonEuclideanRhythmHarness(root).encode(
                field_status={"salience": 0.58},
                current_vector={
                    "temporal_tension": 0.62,
                    "action_density": 0.72,
                    "orbit_distance": 1.4,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 10,
                        "embodiment_ratio": 0.08,
                    },
                    "experiences": [],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": -4}},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(
                frame["dark_field"]["context_diagnosis"]["dominant_mode"],
                "defensive_output_pressure",
            )
            self.assertGreater(frame["dark_field"]["boundary_contact"], 0.7)
            self.assertGreater(frame["dark_field"]["internal_reflection"], 0.2)
            self.assertGreater(frame["dark_field"]["scalar_superposition_potential"], 0.4)
            self.assertGreater(frame["dark_field"]["spiral_turn_potential"], 0.35)
            self.assertEqual(
                frame["dark_field"]["principle"],
                "dark_field_transmutes_destructive_interference_into_margin_for_scalar_superposition_and_spiral_turning",
            )
            self.assertGreater(frame["medium"]["viscosity"], 0.45)
            self.assertEqual(
                frame["medium"]["principle"],
                "medium_slows_or_conducts_by_dark_boundary_transparency_not_by_fixed_rules",
            )

    def test_zone2_rebalances_destructive_interference_to_margin_not_deletion(self):
        harness = NonEuclideanRhythmHarness(Path("."))
        regulation = harness._zone2_regulation(
            interference="destructive",
            zone2={"openness": 0.48},
            awareness={"present_contact": 0.20},
            crisis={"pre_breach_pressure": 0.72, "loop_lock_risk": 0.74},
            pending_node={
                "external_dependency": 0.60,
                "irreversible_execution_risk": 0.82,
            },
            velocity_dilation={
                "anomaly_frequency": 0.70,
                "dilation_need": 0.68,
                "awareness_checkpoint": False,
            },
            axiom={"overfit_pressure": 0.72},
            dark_neuron={"redarkening_pressure": 0.66},
        )

        self.assertEqual(regulation["phase"], "phase_rebalance_to_margin")
        self.assertTrue(regulation["phase_rebalance_to_margin"])
        self.assertTrue(regulation["destructive_to_margin"])
        self.assertTrue(regulation["noise_cancel"])
        self.assertGreater(regulation["scalar_superposition_window"], 0.4)
        self.assertEqual(
            regulation["principle"],
            "zone2_transmutes_destructive_interference_into_margin_not_deletion",
        )

    def test_frequency_expansion_opens_boundary_transparency_without_fixed_rule(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            self._write_field_error(
                outputs,
                error=0.21,
                diagnosis={
                    "context_shift": 0.36,
                    "connection_risk": 0.18,
                    "frequency_expansion": 0.88,
                    "zero_point_adjustment": 0.34,
                    "defensive_output_pressure": 0.08,
                    "dominant_mode": "frequency_expansion",
                },
            )

            frame = NonEuclideanRhythmHarness(root).encode(
                field_status={"salience": 0.36},
                current_vector={
                    "temporal_tension": 0.26,
                    "action_density": 0.34,
                    "orbit_distance": 0.45,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 24,
                        "embodiment_ratio": 0.2,
                    },
                    "experiences": [],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": 8}},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(
                frame["dark_field"]["context_diagnosis"]["dominant_mode"],
                "frequency_expansion",
            )
            self.assertGreater(frame["dark_field"]["boundary_transparency"], 0.35)
            self.assertGreater(frame["zone2"]["boundary_transparency"], 0.35)
            self.assertGreater(frame["medium"]["conductivity"], frame["medium"]["viscosity"] * 0.45)

    def test_human_rhythm_tuning_follows_natural_phase_map(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            self._write_field_error(
                outputs,
                error=0.18,
                diagnosis={
                    "context_shift": 0.24,
                    "connection_risk": 0.22,
                    "frequency_expansion": 0.42,
                    "zero_point_adjustment": 0.48,
                    "defensive_output_pressure": 0.12,
                    "dominant_mode": "zero_point_adjustment",
                },
            )

            frame = NonEuclideanRhythmHarness(root).encode(
                field_status={"salience": 0.44},
                current_vector={
                    "temporal_tension": 0.34,
                    "action_density": 0.26,
                    "orbit_distance": 0.6,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 36,
                        "embodiment_ratio": 0.3,
                    },
                    "experiences": [{"convergence_count": 2, "absorbed": True}],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": 6}},
                boundary_report={"in_orbit": True},
                log=False,
            )

            tuning = frame["natural_rhythm_tuning"]
            self.assertEqual(
                tuning["principle"],
                "human_rhythm_tuning_follows_natural_rhythm_tuning",
            )
            self.assertIn(
                tuning["dominant_natural_phase"],
                tuning["natural_cycle"],
            )
            self.assertGreater(tuning["human_tuning_alignment"], 0.35)
            self.assertGreater(tuning["resistance_minimization"], 0.35)
            self.assertIn("problem_origin", tuning)

    def test_problem_origin_rises_when_human_rhythm_resists_natural_rhythm(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            self._write_field_error(
                outputs,
                error=0.76,
                diagnosis={
                    "context_shift": 0.82,
                    "connection_risk": 0.74,
                    "frequency_expansion": 0.04,
                    "zero_point_adjustment": 0.08,
                    "defensive_output_pressure": 0.7,
                    "dominant_mode": "connection_risk",
                },
            )

            frame = NonEuclideanRhythmHarness(root).encode(
                field_status={"salience": 0.88},
                current_vector={
                    "temporal_tension": 0.9,
                    "action_density": 0.94,
                    "orbit_distance": 3.0,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 2,
                        "embodiment_ratio": 0.016667,
                    },
                    "experiences": [],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": -30}},
                boundary_report={"in_orbit": False},
                log=False,
            )

            origin = frame["natural_rhythm_tuning"]["problem_origin"]
            self.assertEqual(
                origin["principle"],
                "problems_begin_when_human_rhythm_stops_following_natural_rhythm",
            )
            self.assertGreater(origin["problem_seed"], 0.42)
            self.assertIn(origin["phase"], {"problem_seed_visible", "problem_origin_active"})

            mistake = frame["natural_rhythm_tuning"]["mistake_digestion"]
            self.assertEqual(
                mistake["principle"],
                "mistakes_are_context_particles_and_perfectionism_depends_on_direction",
            )
            self.assertIn(mistake["phase"], {"digestible_mistake", "threshold_recenter"})

    def test_mistake_digestion_detects_self_closure_overcontrol(self):
        harness = NonEuclideanRhythmHarness(Path("."))
        mistake = harness._mistake_digestion(
            problem_seed=0.34,
            rhythm_misalignment=0.38,
            rhythm_resistance=0.72,
            field_wave={"frequency": 0.04},
            prediction_wave={"dissonance": 0.04},
            digestion_wave={"pressure": 0.52},
            dark_field={
                "boundary_opacity": 0.98,
                "internal_reflection": 0.9,
                "boundary_transparency": 0.04,
                "world_flow_alignment": 0.12,
                "gravity": 0.38,
            },
            awareness={"present_contact": 0.18},
            zone2={"openness": 0.18},
            medium={"conductivity": 0.08, "viscosity": 0.82, "resistance": 0.82},
            memory_wave={"absorption": 0.18, "resonance": 0.12},
        )

        self.assertEqual(mistake["phase"], "self_closure_overcontrol")
        self.assertEqual(mistake["recommended_mode"], "loosen_boundary_allow_small_divergence")
        self.assertGreater(mistake["self_closure_overcontrol"], mistake["learning_signal"])
        self.assertGreater(mistake["self_closure_overcontrol"], mistake["resonant_refinement"])

    def test_mistake_digestion_preserves_resonant_refinement(self):
        harness = NonEuclideanRhythmHarness(Path("."))
        mistake = harness._mistake_digestion(
            problem_seed=0.28,
            rhythm_misalignment=0.18,
            rhythm_resistance=0.16,
            field_wave={"frequency": 0.62},
            prediction_wave={"dissonance": 0.12},
            digestion_wave={"pressure": 0.22},
            dark_field={
                "boundary_opacity": 0.42,
                "internal_reflection": 0.16,
                "boundary_transparency": 0.54,
                "world_flow_alignment": 0.86,
                "gravity": 0.22,
            },
            awareness={"present_contact": 0.76},
            zone2={"openness": 0.7},
            medium={"conductivity": 0.74, "viscosity": 0.18, "resistance": 0.2},
            memory_wave={"absorption": 0.42, "resonance": 0.68},
        )

        self.assertEqual(mistake["phase"], "resonant_refinement")
        self.assertEqual(
            mistake["recommended_mode"],
            "refine_until_the_work_reaches_the_world",
        )
        self.assertGreaterEqual(mistake["resonant_refinement"], mistake["self_closure_overcontrol"])

    def test_phase_transition_bridge_opens_recoverable_internal_experiment(self):
        harness = NonEuclideanRhythmHarness(Path("."))
        bridge = harness._phase_transition_bridge(
            field_wave={"amplitude": 0.35},
            memory_wave={"absorption": 0.04, "resonance": 0.18},
            prediction_wave={"dissonance": 0.22},
            digestion_wave={"pressure": 0.36, "ready": False, "dream_ready": False},
            body_wave={"availability": 1.0},
            dark_field={
                "boundary_contact": 0.50,
                "boundary_transparency": 0.50,
                "boundary_opacity": 0.45,
                "world_phase_misalignment": 0.24,
                "refraction_angle": 0.55,
            },
            awareness={"release_capacity": 0.76, "present_contact": 0.78},
            zone2={"openness": 0.72},
            medium={"conductivity": 0.44},
            perspective_frame={
                "particle_frame": 0.25,
                "wave_frame": 0.70,
                "metacognitive_refraction": 0.74,
            },
            natural_rhythm_tuning={
                "natural_cycle": {
                    "convergence": 0.42,
                    "threshold": 0.48,
                    "divergence": 0.66,
                    "margin": 0.68,
                    "phase_transition": 0.58,
                }
            },
        )

        self.assertEqual(bridge["phase"], "sensory_overlap_probe")
        self.assertTrue(bridge["internal_experiment_mode"])
        self.assertTrue(bridge["reversible_experiment_window"])
        self.assertGreaterEqual(bridge["transition_readiness"], 0.38)
        self.assertLess(bridge["external_reference_check"], 0.62)
        self.assertEqual(
            bridge["principle"],
            "fold_to_act_unfold_to_learn_keep_phase_experiments_recoverable",
        )

    def test_felt_body_state_bends_body_wave_and_phase_bridge(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            harness = NonEuclideanRhythmHarness(root)
            save_state(
                outputs / "felt_body_state.json",
                {
                    "flow_energy": 0.72,
                    "relation_drift": 0.08,
                    "body_discomfort": 0.12,
                    "body_ease": 0.82,
                    "rhythm_continuity": 0.66,
                    "audio": {"envelope": 0.64, "onset": 0.18, "confidence": 0.7},
                    "source": "test_loopback",
                },
            )

            body_wave = harness._body_wave()
            bridge = harness._phase_transition_bridge(
                field_wave={"amplitude": 0.35},
                memory_wave={"absorption": 0.10, "resonance": 0.24},
                prediction_wave={"dissonance": 0.20},
                digestion_wave={"pressure": 0.32, "ready": False, "dream_ready": False},
                body_wave=body_wave,
                dark_field={
                    "boundary_contact": 0.42,
                    "boundary_transparency": 0.46,
                    "boundary_opacity": 0.40,
                    "world_phase_misalignment": 0.22,
                    "refraction_angle": 0.48,
                },
                awareness={"release_capacity": 0.70, "present_contact": 0.80},
                zone2={"openness": 0.68},
                medium={"conductivity": 0.46},
                perspective_frame={
                    "particle_frame": 0.28,
                    "wave_frame": 0.66,
                    "metacognitive_refraction": 0.70,
                },
                natural_rhythm_tuning={
                    "natural_cycle": {
                        "convergence": 0.40,
                        "threshold": 0.44,
                        "divergence": 0.62,
                        "margin": 0.64,
                        "phase_transition": 0.54,
                    }
                },
            )

            self.assertEqual(body_wave["phase"], "felt_loopback")
            self.assertEqual(body_wave["source"], "test_loopback")
            self.assertGreater(body_wave["availability"], 0.70)
            self.assertGreater(bridge["felt_body_alignment"], 0.95)
            self.assertEqual(bridge["felt_body_phase"], "felt_loopback")
            self.assertGreaterEqual(bridge["transition_readiness"], 0.38)

    def _write_field_error(self, outputs: Path, *, error: float, diagnosis: dict):
        entry = {
            "error": error,
            "context_diagnosis": {
                "semantic_information_frame": "context_relative_continuity_information",
                **diagnosis,
            },
        }
        (outputs / "field_prediction_errors.jsonl").write_text(
            json.dumps(entry, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
