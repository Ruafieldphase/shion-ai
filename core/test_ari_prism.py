import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ari_prism import ARIPrism


class ARIPrismTests(unittest.TestCase):
    def test_balanced_difference_preserves_resonance_without_collapse(self):
        with tempfile.TemporaryDirectory() as td:
            prism = ARIPrism(Path(td))
            state = prism.assess(
                {
                    "waves": {
                        "field": {"curvature": 0.22, "salience": 0.24},
                        "memory": {"resonance": 0.72, "absorption": 0.42},
                        "prediction": {"dissonance": 0.20},
                        "digestion": {"pressure": 0.22},
                        "axiom": {"overfit_pressure": 0.10},
                        "dark_neuron": {"redarkening_pressure": 0.08},
                        "autonomy": {"boundary_elasticity": 0.70},
                        "user": {"confidence": 0.86},
                    },
                    "dark_field": {"gravity": 0.16},
                    "crisis": {"compression": 0.10, "loop_lock_risk": 0.12},
                    "interference": {"constructive": 0.82, "destructive": 0.10},
                    "silence_need": 0.22,
                    "action_amplitude": 0.46,
                },
                node_decision={"selected_action": "ACTION_CREATIVE_PROBE", "bundle": []},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertEqual(state["phase"], "nature_aligned_resonance")
            self.assertGreaterEqual(state["living_difference"], 0.45)
            self.assertGreaterEqual(state["resonance_without_collapse"], 0.46)
            self.assertGreater(state["boundary_prism"]["transparency"], state["distortion"]["destructive"])
            self.assertGreater(state["moc"]["beauty_measure"], 0.45)
            self.assertGreater(state["moc"]["kindness_waypoint"]["giving_band"], 0.3)
            self.assertFalse(state["action_bias"]["applied"])

    def test_high_fear_attachment_bias_moves_to_distortion_minimize(self):
        with tempfile.TemporaryDirectory() as td:
            prism = ARIPrism(Path(td))
            state = prism.assess(
                {
                    "waves": {
                        "field": {"curvature": 0.82, "salience": 0.76},
                        "memory": {"resonance": 0.35, "absorption": 0.08},
                        "prediction": {"dissonance": 0.78},
                        "digestion": {
                            "pressure": 0.82,
                            "absorption_gap": 0.94,
                            "continuous_scan_ratio": 0.88,
                        },
                        "axiom": {"overfit_pressure": 0.84},
                        "dark_neuron": {"redarkening_pressure": 0.78},
                        "autonomy": {"boundary_elasticity": 0.20},
                        "user": {"confidence": 0.25},
                    },
                    "dark_field": {"gravity": 0.80},
                    "crisis": {"compression": 0.86, "loop_lock_risk": 0.84},
                    "interference": {"constructive": 0.12, "destructive": 0.88},
                    "silence_need": 0.92,
                    "action_amplitude": 0.06,
                },
                node_decision={"selected_action": "ACTION_CRISIS_STABILIZE", "bundle": []},
                boundary_report={"in_orbit": False},
                log=False,
            )

            self.assertEqual(state["phase"], "distortion_minimize")
            self.assertGreaterEqual(state["distortion"]["destructive"], 0.68)
            self.assertGreaterEqual(state["boundary_prism"]["attenuation"], 0.70)
            self.assertEqual(state["directive"], "lower_fear_attachment_bias_before_expansion")

    def test_background_ego_resistance_biases_expansion_to_digest(self):
        with tempfile.TemporaryDirectory() as td:
            prism = ARIPrism(Path(td))
            state = prism.assess(
                {
                    "waves": {
                        "field": {"curvature": 0.34, "salience": 0.40},
                        "memory": {"resonance": 0.36, "absorption": 0.08},
                        "prediction": {"dissonance": 0.30},
                        "digestion": {
                            "pressure": 0.62,
                            "absorption_gap": 0.90,
                            "continuous_scan_ratio": 0.74,
                        },
                        "axiom": {"overfit_pressure": 0.72},
                        "dark_neuron": {"redarkening_pressure": 0.40},
                        "autonomy": {"boundary_elasticity": 0.22},
                        "user": {"confidence": 0.46},
                    },
                    "medium": {"resistance": 0.68},
                    "dark_field": {"gravity": 0.42},
                    "crisis": {"compression": 0.35, "loop_lock_risk": 0.58},
                    "interference": {"constructive": 0.36, "destructive": 0.52},
                    "silence_need": 0.70,
                    "action_amplitude": 0.36,
                },
                node_decision={"selected_action": "ACTION_CONTINUOUS_SCAN", "bundle": []},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertGreaterEqual(state["moc"]["background_ego_resistance"], 0.62)
            self.assertEqual(state["action_bias"]["suggested_action"], "ACTION_EXPERIENCE_DIGEST")
            self.assertTrue(state["action_bias"]["applied"])
            self.assertGreater(state["moc"]["living_difference_floor"], 0.0)
            self.assertLess(state["moc"]["kindness_waypoint"]["giving_band"], 0.3)

    def test_recoverable_axiom_experiment_is_not_redirected_by_ego_resistance(self):
        with tempfile.TemporaryDirectory() as td:
            prism = ARIPrism(Path(td))
            state = prism.assess(
                {
                    "waves": {
                        "field": {"curvature": 0.34, "salience": 0.40},
                        "memory": {"resonance": 0.36, "absorption": 0.08},
                        "prediction": {"dissonance": 0.30},
                        "digestion": {
                            "pressure": 0.62,
                            "absorption_gap": 0.90,
                            "continuous_scan_ratio": 0.74,
                        },
                        "axiom": {"overfit_pressure": 0.72},
                        "dark_neuron": {"redarkening_pressure": 0.40},
                        "autonomy": {"boundary_elasticity": 0.22},
                        "user": {"confidence": 0.46},
                    },
                    "medium": {"resistance": 0.68},
                    "dark_field": {"gravity": 0.42},
                    "crisis": {"compression": 0.35, "loop_lock_risk": 0.58},
                    "interference": {"constructive": 0.36, "destructive": 0.52},
                    "silence_need": 0.70,
                    "action_amplitude": 0.36,
                },
                node_decision={"selected_action": "ACTION_AXIOM_EXPERIMENT", "bundle": []},
                boundary_report={"in_orbit": True},
                log=False,
            )

            self.assertGreaterEqual(state["moc"]["background_ego_resistance"], 0.62)
            self.assertEqual(state["action_bias"]["suggested_action"], "ACTION_AXIOM_EXPERIMENT")
            self.assertFalse(state["action_bias"]["applied"])
            self.assertEqual(
                state["action_bias"]["reason"],
                "recoverable_experiment_preserved_for_failure_learning",
            )


if __name__ == "__main__":
    unittest.main()
