import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dark_field_threshold import build_dark_field_threshold_state


class DarkFieldThresholdTests(unittest.TestCase):
    def test_low_context_contact_keeps_coordinate_latent(self):
        state = build_dark_field_threshold_state(
            felt_state={"body_ease": 0.8, "body_discomfort": 0.05},
            prediction_trace={"error": 0.01, "context_diagnosis": {"context_shift": 0.02}},
            boundary_state={"aperture": {"boundary_aperture": 0.8, "permeability": 0.8}},
        )

        self.assertEqual(state["mode"], "latent_do_not_open")
        self.assertFalse(state["middle_destination"]["active"])
        self.assertEqual(state["next_contact"]["tail_limit_chars"], 0)

    def test_over_capacity_defer_when_pressure_exceeds_dynamic_threshold(self):
        state = build_dark_field_threshold_state(
            felt_state={"body_ease": 0.15, "body_discomfort": 0.9, "relation_drift": 0.4},
            prediction_trace={
                "error": 0.9,
                "context_diagnosis": {
                    "context_shift": 0.8,
                    "connection_risk": 0.95,
                    "zero_point_adjustment": 0.1,
                    "defensive_output_pressure": 0.95,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.2, "permeability": 0.1, "digestion_bias": 0.8}},
        )

        self.assertEqual(state["mode"], "over_capacity_defer_and_digest")
        self.assertGreater(state["threshold"]["dark_field_pressure"], state["threshold"]["dynamic_threshold"])
        self.assertEqual(state["next_contact"]["action"], "close_and_digest_before_reentry")

    def test_within_capacity_processes_only_bounded_slice(self):
        state = build_dark_field_threshold_state(
            felt_state={"body_ease": 0.9, "body_discomfort": 0.02, "relation_drift": 0.1},
            prediction_trace={
                "error": 0.22,
                "context_diagnosis": {
                    "context_shift": 0.35,
                    "connection_risk": 0.05,
                    "zero_point_adjustment": 0.65,
                    "defensive_output_pressure": 0.04,
                },
            },
            boundary_state={
                "aperture": {
                    "boundary_aperture": 0.9,
                    "permeability": 0.88,
                    "digestion_bias": 0.16,
                    "internal_reflection": 0.52,
                }
            },
            execution_gradient={"context_gradient": {"native_flow_pull": 0.8}},
        )

        self.assertEqual(state["mode"], "within_capacity_process_contextual_slice")
        self.assertGreater(state["threshold"]["dynamic_threshold"], state["threshold"]["dark_field_pressure"])
        self.assertGreaterEqual(state["threshold"]["processing_slice"], 0.22)
        self.assertLess(state["threshold"]["processing_slice"], 1.0)

    def test_edge_near_threshold_opens_small_slice(self):
        state = build_dark_field_threshold_state(
            felt_state={"body_ease": 0.42, "body_discomfort": 0.38, "relation_drift": 0.2},
            prediction_trace={
                "error": 0.48,
                "context_diagnosis": {
                    "context_shift": 0.52,
                    "connection_risk": 0.44,
                    "zero_point_adjustment": 0.42,
                    "defensive_output_pressure": 0.48,
                },
            },
            boundary_state={
                "aperture": {
                    "boundary_aperture": 0.56,
                    "permeability": 0.48,
                    "digestion_bias": 0.4,
                    "internal_reflection": 0.42,
                }
            },
        )

        self.assertEqual(state["mode"], "edge_process_small_slice")
        self.assertEqual(state["next_contact"]["action"], "process_small_slice_then_close")
        self.assertGreater(state["threshold"]["context_contact"], 0.16)


if __name__ == "__main__":
    unittest.main()
