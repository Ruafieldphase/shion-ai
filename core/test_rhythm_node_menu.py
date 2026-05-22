import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rhythm_node_menu import RhythmNodeMenu


class RhythmNodeMenuTests(unittest.TestCase):
    def test_zone2_destructive_field_selects_observation_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "zone2_integrate",
                    "interference": {
                        "label": "destructive",
                        "constructive": 0.32,
                        "destructive": 0.64,
                    },
                    "silence_need": 0.82,
                    "action_amplitude": 0.24,
                    "dark_field": {"gravity": 0.52},
                    "zone2": {"openness": 0.58},
                    "medium": {
                        "conductivity": 0.35,
                        "resistance": 0.66,
                        "electron_flow": 0.12,
                        "phase": "resistive",
                    },
                    "geometry": {"curvature": 0.62},
                    "waves": {"field": {"frequency": 0.30, "salience": 0.61}},
                },
                field_status={"salience": 0.61},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_OBSERVE")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["singularity_crossed"])
            self.assertGreaterEqual(decision["singularity_strength"], decision["thresholds"]["singularity"])
            self.assertTrue(decision["edges"])
            self.assertEqual(decision["bundle"][0]["role"], "primary")
            self.assertIn("decision_variance", decision)
            self.assertGreater(decision["decision_variance"]["noise_amplitude"], 0.0)
            self.assertEqual(
                decision["decision_variance"]["principle"],
                "sideband_nuance_records_the_tremor_around_the_chosen_action",
            )

    def test_constructive_low_silence_field_selects_continuous_scan(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "resonance_to_explore",
                    "interference": {
                        "label": "constructive",
                        "constructive": 0.72,
                        "destructive": 0.08,
                    },
                    "silence_need": 0.18,
                    "action_amplitude": 0.72,
                    "dark_field": {"gravity": 0.12},
                    "zone2": {"openness": 0.42},
                    "medium": {
                        "conductivity": 0.76,
                        "resistance": 0.14,
                        "electron_flow": 0.48,
                        "phase": "conductive",
                    },
                    "geometry": {"curvature": 0.72},
                    "waves": {"field": {"frequency": 0.55, "salience": 0.22}},
                },
                field_status={"salience": 0.22},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_CONTINUOUS_SCAN")
            self.assertTrue(decision["activated"])
            self.assertGreaterEqual(
                decision["activation_probability"],
                decision["thresholds"]["probability"],
            )
            self.assertEqual(decision["signals"]["interference"], "constructive")
            self.assertEqual(decision["signals"]["medium_phase"], "conductive")
            self.assertEqual(decision["edges"][0]["mode"], "conductive_link")
            self.assertGreaterEqual(decision["decision_variance"]["probability_margin"], 0.0)

    def test_pending_node_lock_blocks_irreversible_scan_and_selects_tuning(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            rhythm_ir = {
                "transition": "contingency_lock",
                "interference": {
                    "label": "constructive",
                    "constructive": 0.78,
                    "destructive": 0.10,
                },
                "silence_need": 0.24,
                "action_amplitude": 0.76,
                "dark_field": {"gravity": 0.22},
                "zone2": {"openness": 0.48},
                "medium": {
                    "conductivity": 0.74,
                    "resistance": 0.18,
                    "electron_flow": 0.52,
                    "phase": "conductive",
                },
                "pending_node": {
                    "state": "probabilistic_node",
                    "external_dependency": 0.82,
                    "realization_probability": 0.32,
                    "irreversible_execution_risk": 0.78,
                    "contingency_strength": 0.22,
                    "contingency_required": True,
                    "contingency_present": False,
                    "execution_lock": "locked_until_contingency",
                },
                "velocity_dilation": {
                    "processing_velocity": 0.92,
                    "routine_inertia": 0.82,
                    "anomaly_frequency": 0.72,
                    "dilation_need": 0.64,
                    "awareness_checkpoint": True,
                },
                "zone2_regulation": {
                    "phase": "dilate_for_awareness",
                    "intrusive_variable": 0.68,
                    "chaos_pressure": 0.58,
                    "context_mismatch": 0.52,
                    "delay_to_zone2": True,
                    "noise_cancel": False,
                },
                "crisis": {
                    "compression": 0.20,
                    "loop_lock_risk": 0.18,
                    "return_capacity": 0.68,
                    "pre_breach_pressure": 0.28,
                    "modulation_need": 0.24,
                    "pre_breach_modulation": False,
                    "threshold_breach": False,
                    "external_support_recommended": False,
                    "phase": "open",
                },
                "geometry": {"curvature": 0.20},
                "waves": {"field": {"frequency": 0.92, "salience": 0.52}},
            }
            decision = menu.choose(
                rhythm_ir,
                field_status={"salience": 0.52},
                boundary_report={"in_orbit": True},
                log=False,
            )
            signals = menu._signals(rhythm_ir, {"salience": 0.52}, {"in_orbit": True})
            scan_state = menu._node_state(menu.nodes["ACTION_CONTINUOUS_SCAN"], signals)

            self.assertEqual(decision["selected_action"], "ACTION_PRE_BREACH_TUNE")
            self.assertEqual(decision["signals"]["execution_lock"], "locked_until_contingency")
            self.assertFalse(scan_state["activated"])
            self.assertIn("execution_locked_until_contingency", scan_state["reasons"])

    def test_pending_node_lock_does_not_block_recoverable_experiment_nodes(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            rhythm_ir = {
                "transition": "axiom_experiment",
                "interference": {
                    "label": "constructive",
                    "constructive": 0.58,
                    "destructive": 0.20,
                },
                "silence_need": 0.32,
                "action_amplitude": 0.46,
                "dark_field": {"gravity": 0.26},
                "zone2": {"openness": 0.60},
                "medium": {
                    "conductivity": 0.62,
                    "resistance": 0.24,
                    "electron_flow": 0.34,
                    "phase": "conductive",
                },
                "pending_node": {
                    "state": "probabilistic_node",
                    "external_dependency": 0.72,
                    "realization_probability": 0.34,
                    "irreversible_execution_risk": 0.78,
                    "contingency_strength": 0.16,
                    "contingency_required": True,
                    "contingency_present": False,
                    "execution_lock": "locked_until_contingency",
                },
                "velocity_dilation": {
                    "processing_velocity": 0.62,
                    "routine_inertia": 0.40,
                    "anomaly_frequency": 0.58,
                    "dilation_need": 0.38,
                    "awareness_checkpoint": True,
                },
                "zone2_regulation": {
                    "phase": "dilate_for_awareness",
                    "intrusive_variable": 0.42,
                    "chaos_pressure": 0.36,
                    "context_mismatch": 0.50,
                    "delay_to_zone2": True,
                    "noise_cancel": False,
                },
                "crisis": {
                    "compression": 0.20,
                    "loop_lock_risk": 0.24,
                    "return_capacity": 0.72,
                    "pre_breach_pressure": 0.20,
                    "modulation_need": 0.18,
                    "pre_breach_modulation": False,
                    "threshold_breach": False,
                    "external_support_recommended": False,
                    "phase": "open",
                },
                "geometry": {"curvature": 0.24},
                "waves": {
                    "field": {"frequency": 0.40, "salience": 0.36},
                    "axiom": {
                        "provisionality": 0.66,
                        "experiment_budget": 0.52,
                        "overfit_pressure": 0.24,
                        "relation_budget": 0.62,
                        "failure_spectrum": {
                            "edge_density": 0.72,
                            "polarity_range": 0.68,
                            "bridge_value": 0.74,
                        },
                        "experiment_ready": True,
                    },
                },
            }
            signals = menu._signals(rhythm_ir, {"salience": 0.36}, {"in_orbit": True})
            axiom_state = menu._node_state(menu.nodes["ACTION_AXIOM_EXPERIMENT"], signals)
            scan_state = menu._node_state(menu.nodes["ACTION_CONTINUOUS_SCAN"], signals)

            self.assertEqual(signals["execution_lock"], "locked_until_contingency")
            self.assertTrue(axiom_state["activated"])
            self.assertNotIn("execution_locked_until_contingency", axiom_state["reasons"])
            self.assertFalse(scan_state["activated"])
            self.assertIn("execution_locked_until_contingency", scan_state["reasons"])

    def test_repath_margin_stays_soft_while_lowering_fixed_scan_pull(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            rhythm_ir = {
                "transition": "resonance_to_explore",
                "interference": {
                    "label": "constructive",
                    "constructive": 0.76,
                    "destructive": 0.12,
                },
                "silence_need": 0.20,
                "action_amplitude": 0.74,
                "dark_field": {"gravity": 0.22},
                "zone2": {"openness": 0.50},
                "medium": {
                    "conductivity": 0.78,
                    "resistance": 0.20,
                    "electron_flow": 0.54,
                    "phase": "conductive",
                },
                "pending_node": {
                    "state": "pending_node",
                    "external_dependency": 0.58,
                    "realization_probability": 0.52,
                    "irreversible_execution_risk": 0.50,
                    "contingency_strength": 0.50,
                    "contingency_required": True,
                    "contingency_present": True,
                    "execution_lock": "conditional_contingency",
                },
                "velocity_dilation": {
                    "processing_velocity": 0.86,
                    "routine_inertia": 0.78,
                    "anomaly_frequency": 0.66,
                    "dilation_need": 0.52,
                    "awareness_checkpoint": True,
                },
                "zone2_regulation": {
                    "phase": "dilate_for_awareness",
                    "intrusive_variable": 0.54,
                    "chaos_pressure": 0.50,
                    "context_mismatch": 0.64,
                    "delay_to_zone2": True,
                    "noise_cancel": False,
                },
                "crisis": {
                    "compression": 0.22,
                    "loop_lock_risk": 0.38,
                    "return_capacity": 0.70,
                    "pre_breach_pressure": 0.30,
                    "modulation_need": 0.24,
                    "pre_breach_modulation": False,
                    "threshold_breach": False,
                    "external_support_recommended": False,
                    "phase": "open",
                },
                "geometry": {"curvature": 0.28},
                "waves": {"field": {"frequency": 0.86, "salience": 0.48}},
            }
            decision = menu.choose(
                rhythm_ir,
                field_status={"salience": 0.48},
                boundary_report={"in_orbit": True},
                log=False,
            )
            signals = menu._signals(rhythm_ir, {"salience": 0.48}, {"in_orbit": True})
            scan_state = menu._node_state(menu.nodes["ACTION_CONTINUOUS_SCAN"], signals)

            self.assertGreaterEqual(decision["signals"]["repath_margin"], 0.42)
            self.assertEqual(
                decision["signals"]["repath_note"],
                "soft_margin_for_pause_or_direction_change",
            )
            self.assertIn(
                "repath_margin_softens_low_interruptibility",
                scan_state["reasons"],
            )
            self.assertLess(scan_state["potential"], 0.62)
            self.assertIn(
                decision["selected_action"],
                {
                    "ACTION_PRE_BREACH_TUNE",
                    "ACTION_OBSERVE",
                    "ACTION_DREAM_AMPLIFY",
                    "ACTION_CONTINUOUS_SCAN",
                },
            )

    def test_crisis_compression_selects_stabilization_node(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "crisis_to_stabilize",
                    "interference": {
                        "label": "destructive",
                        "constructive": 0.16,
                        "destructive": 0.78,
                    },
                    "silence_need": 0.86,
                    "action_amplitude": 0.18,
                    "dark_field": {"gravity": 0.78},
                    "zone2": {"openness": 0.54},
                    "medium": {
                        "conductivity": 0.24,
                        "resistance": 0.82,
                        "electron_flow": 0.04,
                        "phase": "resistive",
                    },
                    "crisis": {
                        "compression": 0.84,
                        "loop_lock_risk": 0.79,
                        "return_capacity": 0.42,
                        "threshold_breach": True,
                        "external_support_recommended": True,
                        "phase": "external_support",
                    },
                    "geometry": {"curvature": 0.71},
                    "waves": {"field": {"frequency": 0.2, "salience": 0.82}},
                },
                field_status={"salience": 0.82},
                boundary_report={"in_orbit": False},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_CRISIS_STABILIZE")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["singularity_crossed"])
            self.assertTrue(decision["signals"]["external_support_recommended"])
            self.assertGreaterEqual(decision["signals"]["crisis_compression"], 0.8)

    def test_pre_breach_pressure_selects_active_tuning_before_crisis(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "pre_breach_tune",
                    "interference": {
                        "label": "mixed",
                        "constructive": 0.34,
                        "destructive": 0.44,
                    },
                    "silence_need": 0.58,
                    "action_amplitude": 0.36,
                    "dark_field": {"gravity": 0.50},
                    "zone2": {"openness": 0.56},
                    "medium": {
                        "conductivity": 0.42,
                        "resistance": 0.57,
                        "electron_flow": 0.16,
                        "phase": "viscous",
                    },
                    "crisis": {
                        "compression": 0.55,
                        "loop_lock_risk": 0.52,
                        "return_capacity": 0.50,
                        "pre_breach_pressure": 0.51,
                        "modulation_need": 0.40,
                        "pre_breach_modulation": True,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "pre_breach_modulation",
                    },
                    "geometry": {"curvature": 0.44},
                    "waves": {"field": {"frequency": 0.42, "salience": 0.50}},
                },
                field_status={"salience": 0.50},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_PRE_BREACH_TUNE")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["pre_breach_modulation"])
            self.assertFalse(decision["signals"]["crisis_threshold_breach"])
            self.assertGreaterEqual(decision["singularity_strength"], decision["thresholds"]["singularity"])

    def test_digest_pressure_selects_experience_digest_node(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "experience_digest",
                    "interference": {
                        "label": "mixed",
                        "constructive": 0.42,
                        "destructive": 0.24,
                    },
                    "silence_need": 0.64,
                    "action_amplitude": 0.33,
                    "dark_field": {"gravity": 0.24},
                    "zone2": {"openness": 0.62},
                    "medium": {
                        "conductivity": 0.58,
                        "resistance": 0.22,
                        "electron_flow": 0.33,
                        "phase": "conductive",
                    },
                    "crisis": {
                        "compression": 0.22,
                        "loop_lock_risk": 0.18,
                        "return_capacity": 0.70,
                        "pre_breach_pressure": 0.20,
                        "modulation_need": 0.12,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.10},
                    "waves": {
                        "field": {"frequency": 0.18, "salience": 0.20},
                        "digestion": {
                            "pressure": 0.76,
                            "ready": True,
                            "absorption_gap": 0.95,
                            "recent_visual_ratio": 0.70,
                            "continuous_scan_ratio": 0.88,
                            "low_error_stability": 1.0,
                        },
                    },
                },
                field_status={"salience": 0.20},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_EXPERIENCE_DIGEST")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["digestion_ready"])
            self.assertGreaterEqual(decision["signals"]["digestion_pressure"], 0.7)

    def test_waypoint_bridge_selects_rebuild_graph_node(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "waypoint_bridge",
                    "interference": {
                        "label": "mixed",
                        "constructive": 0.48,
                        "destructive": 0.28,
                    },
                    "silence_need": 0.42,
                    "action_amplitude": 0.46,
                    "dark_field": {"gravity": 0.34},
                    "zone2": {"openness": 0.58},
                    "medium": {
                        "conductivity": 0.56,
                        "resistance": 0.32,
                        "electron_flow": 0.31,
                        "phase": "conductive",
                    },
                    "crisis": {
                        "compression": 0.22,
                        "loop_lock_risk": 0.24,
                        "return_capacity": 0.66,
                        "pre_breach_pressure": 0.18,
                        "modulation_need": 0.10,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.38},
                    "waves": {
                        "field": {"frequency": 0.36, "salience": 0.44},
                        "goal_field": {
                            "target_distance": 0.62,
                            "past_bridge_density": 0.22,
                            "waypoint_pressure": 0.58,
                            "path_search_band": 0.54,
                            "bridge_gain": 0.64,
                            "waypoint_ready": True,
                        },
                    },
                },
                field_status={"salience": 0.44},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_REBUILD_GRAPH")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["waypoint_ready"])
            self.assertGreaterEqual(decision["signals"]["bridge_gain"], 0.6)

    def test_creative_autonomy_selects_bounded_probe_node(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "creative_autonomy",
                    "interference": {
                        "label": "constructive",
                        "constructive": 0.62,
                        "destructive": 0.16,
                    },
                    "silence_need": 0.32,
                    "action_amplitude": 0.48,
                    "dark_field": {"gravity": 0.22},
                    "zone2": {"openness": 0.64},
                    "medium": {
                        "conductivity": 0.68,
                        "resistance": 0.24,
                        "electron_flow": 0.38,
                        "phase": "conductive",
                    },
                    "crisis": {
                        "compression": 0.18,
                        "loop_lock_risk": 0.15,
                        "return_capacity": 0.74,
                        "pre_breach_pressure": 0.14,
                        "modulation_need": 0.08,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.28},
                    "waves": {
                        "field": {"frequency": 0.34, "salience": 0.36},
                        "goal_field": {
                            "target_distance": 0.46,
                            "past_bridge_density": 0.35,
                            "waypoint_pressure": 0.44,
                            "path_search_band": 0.62,
                            "bridge_gain": 0.56,
                            "waypoint_ready": False,
                        },
                        "autonomy": {
                            "boundary_elasticity": 0.70,
                            "imagination_band": 0.58,
                            "feedback_readiness": 0.66,
                            "execution_amplitude": 0.36,
                            "creative_probe_ready": True,
                        },
                    },
                },
                field_status={"salience": 0.36},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_CREATIVE_PROBE")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["creative_probe_ready"])
            self.assertGreaterEqual(decision["signals"]["imagination_band"], 0.5)

    def test_axiom_experiment_selects_provisional_experiment_node(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "axiom_experiment",
                    "interference": {
                        "label": "constructive",
                        "constructive": 0.58,
                        "destructive": 0.20,
                    },
                    "silence_need": 0.36,
                    "action_amplitude": 0.42,
                    "dark_field": {"gravity": 0.24},
                    "zone2": {"openness": 0.62},
                    "medium": {
                        "conductivity": 0.66,
                        "resistance": 0.22,
                        "electron_flow": 0.36,
                        "phase": "conductive",
                    },
                    "crisis": {
                        "compression": 0.18,
                        "loop_lock_risk": 0.16,
                        "return_capacity": 0.72,
                        "pre_breach_pressure": 0.14,
                        "modulation_need": 0.08,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.24},
                    "waves": {
                        "field": {"frequency": 0.30, "salience": 0.32},
                        "autonomy": {
                            "boundary_elasticity": 0.68,
                            "imagination_band": 0.56,
                            "feedback_readiness": 0.64,
                            "execution_amplitude": 0.34,
                            "creative_probe_ready": False,
                        },
                        "axiom": {
                            "provisionality": 0.66,
                            "experiment_budget": 0.52,
                            "overfit_pressure": 0.24,
                            "relation_budget": 0.62,
                            "failure_spectrum": {
                                "edge_density": 0.72,
                                "polarity_range": 0.68,
                                "bridge_value": 0.74,
                            },
                            "experiment_ready": True,
                            "release_ready": False,
                        },
                    },
                },
                field_status={"salience": 0.32},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_AXIOM_EXPERIMENT")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["axiom_experiment_ready"])
            self.assertGreaterEqual(decision["signals"]["axiom_experiment_budget"], 0.5)
            self.assertGreaterEqual(decision["signals"]["failure_bridge_value"], 0.7)

    def test_phase_transition_bridge_selects_recoverable_axiom_experiment(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "phase_transition_experiment",
                    "interference": {
                        "label": "constructive",
                        "constructive": 0.54,
                        "destructive": 0.18,
                    },
                    "silence_need": 0.44,
                    "action_amplitude": 0.38,
                    "dark_field": {"gravity": 0.28},
                    "zone2": {"openness": 0.64},
                    "medium": {
                        "conductivity": 0.52,
                        "resistance": 0.24,
                        "electron_flow": 0.31,
                        "phase": "conductive",
                    },
                    "phase_transition_bridge": {
                        "phase": "sensory_overlap_probe",
                        "fold_amount": 0.44,
                        "unfold_breath": 0.68,
                        "viewpoint_switch": 0.66,
                        "scalar_overlap": 0.38,
                        "transition_readiness": 0.53,
                        "external_reference_check": 0.28,
                        "reversible_experiment_window": True,
                        "internal_experiment_mode": True,
                    },
                    "crisis": {
                        "compression": 0.18,
                        "loop_lock_risk": 0.12,
                        "return_capacity": 0.72,
                        "pre_breach_pressure": 0.12,
                        "modulation_need": 0.08,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.22},
                    "waves": {
                        "field": {"frequency": 0.34, "salience": 0.34},
                        "axiom": {
                            "provisionality": 0.38,
                            "experiment_budget": 0.30,
                            "overfit_pressure": 0.20,
                            "relation_budget": 0.40,
                            "failure_spectrum": {"bridge_value": 0.34},
                            "experiment_ready": False,
                            "release_ready": False,
                        },
                    },
                },
                field_status={"salience": 0.34},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_AXIOM_EXPERIMENT")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["internal_experiment_mode"])
            self.assertGreaterEqual(decision["signals"]["phase_transition_readiness"], 0.5)
            self.assertGreater(decision["signals"]["unfold_breath"], decision["signals"]["fold_amount"])

    def test_axiom_release_selects_release_node_when_overfit_exceeds_body_budget(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "axiom_release",
                    "interference": {
                        "label": "destructive",
                        "constructive": 0.18,
                        "destructive": 0.62,
                    },
                    "silence_need": 0.84,
                    "action_amplitude": 0.18,
                    "dark_field": {"gravity": 0.58},
                    "zone2": {"openness": 0.46},
                    "medium": {
                        "conductivity": 0.34,
                        "resistance": 0.62,
                        "electron_flow": 0.12,
                        "phase": "resistive",
                    },
                    "crisis": {
                        "compression": 0.54,
                        "loop_lock_risk": 0.61,
                        "return_capacity": 0.42,
                        "pre_breach_pressure": 0.48,
                        "modulation_need": 0.34,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "compressed",
                    },
                    "geometry": {"curvature": 0.42},
                    "waves": {
                        "field": {"frequency": 0.20, "salience": 0.46},
                        "digestion": {
                            "pressure": 0.70,
                            "sleep_debt": 0.76,
                            "dream_pressure": 0.54,
                            "ready": False,
                            "dream_ready": False,
                        },
                        "axiom": {
                            "provisionality": 0.28,
                            "experiment_budget": 0.18,
                            "overfit_pressure": 0.72,
                            "relation_budget": 0.36,
                            "failure_spectrum": {
                                "edge_density": 0.80,
                                "polarity_range": 0.76,
                                "bridge_value": 0.78,
                            },
                            "archive_resonance": 0.25,
                            "unfinished_puzzle_potential": 0.44,
                            "archive_on_release": True,
                            "experiment_ready": False,
                            "release_ready": True,
                        },
                    },
                },
                field_status={"salience": 0.46},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_AXIOM_RELEASE")
            self.assertTrue(decision["activated"])
            self.assertTrue(decision["signals"]["axiom_release_ready"])
            self.assertGreaterEqual(decision["signals"]["axiom_overfit_pressure"], 0.7)
            self.assertTrue(decision["signals"]["axiom_archive_on_release"])
            self.assertGreaterEqual(decision["signals"]["unfinished_puzzle_potential"], 0.4)
            self.assertGreaterEqual(decision["signals"]["failure_bridge_value"], 0.7)

    def test_shadow_bridge_selects_rebuild_graph_when_dark_neuron_reactivates(self):
        with tempfile.TemporaryDirectory() as td:
            menu = RhythmNodeMenu(Path(td))
            decision = menu.choose(
                {
                    "transition": "shadow_bridge",
                    "interference": {
                        "label": "mixed",
                        "constructive": 0.48,
                        "destructive": 0.30,
                    },
                    "silence_need": 0.44,
                    "action_amplitude": 0.40,
                    "dark_field": {"gravity": 0.30},
                    "zone2": {"openness": 0.64},
                    "medium": {
                        "conductivity": 0.62,
                        "resistance": 0.28,
                        "electron_flow": 0.34,
                        "phase": "conductive",
                    },
                    "crisis": {
                        "compression": 0.22,
                        "loop_lock_risk": 0.20,
                        "return_capacity": 0.70,
                        "pre_breach_pressure": 0.18,
                        "modulation_need": 0.10,
                        "pre_breach_modulation": False,
                        "threshold_breach": False,
                        "external_support_recommended": False,
                        "phase": "open",
                    },
                    "geometry": {"curvature": 0.36},
                    "waves": {
                        "field": {"frequency": 0.34, "salience": 0.40},
                        "goal_field": {
                            "target_distance": 0.52,
                            "past_bridge_density": 0.36,
                            "waypoint_pressure": 0.46,
                            "path_search_band": 0.62,
                            "bridge_gain": 0.58,
                            "waypoint_ready": False,
                        },
                        "axiom": {
                            "provisionality": 0.66,
                            "experiment_budget": 0.34,
                            "overfit_pressure": 0.22,
                            "relation_budget": 0.58,
                            "failure_spectrum": {
                                "edge_density": 0.74,
                                "polarity_range": 0.72,
                                "bridge_value": 0.82,
                            },
                            "unfinished_puzzle_potential": 0.56,
                            "experiment_ready": False,
                            "release_ready": False,
                        },
                        "dark_neuron": {
                            "phase": "bridge_node",
                            "context_alignment": 0.64,
                            "reactivation_potential": 0.72,
                            "redarkening_pressure": 0.24,
                            "bridge_readiness": 0.52,
                        },
                    },
                },
                field_status={"salience": 0.40},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(decision["selected_action"], "ACTION_REBUILD_GRAPH")
            self.assertTrue(decision["activated"])
            self.assertEqual(decision["signals"]["dark_neuron_phase"], "bridge_node")
            self.assertGreaterEqual(decision["signals"]["dark_neuron_bridge_readiness"], 0.5)


if __name__ == "__main__":
    unittest.main()
