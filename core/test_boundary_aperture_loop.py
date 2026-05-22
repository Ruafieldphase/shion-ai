import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from boundary_aperture_loop import build_boundary_aperture_state


class BoundaryApertureLoopTests(unittest.TestCase):
    def test_connection_risk_narrows_boundary_and_prefers_unconscious_profile(self):
        state = build_boundary_aperture_state(
            felt_state={"body_ease": 0.3, "body_discomfort": 0.4, "rhythm_continuity": 0.2},
            prediction_trace={
                "error": 0.9,
                "context_diagnosis": {
                    "connection_risk": 0.82,
                    "defensive_output_pressure": 0.75,
                    "zero_point_adjustment": 0.2,
                },
            },
            experience_feedback={
                "field_distribution_delta": {
                    "self_closure_overcontrol": 0.7,
                    "boundary_contact": 0.55,
                    "dissonance": 0.62,
                }
            },
        )

        self.assertEqual(state["mode"], "narrow_and_digest")
        self.assertEqual(state["serving_profile_bias"]["preferred_profile"], "unconscious_fixed_prefix")
        self.assertLessEqual(state["serving_profile_bias"]["tail_limit_chars"], 420)
        self.assertFalse(state["next_contact"]["irreversible_effect"])

    def test_reflection_pressure_holds_boundary_half_open(self):
        state = build_boundary_aperture_state(
            felt_state={"body_ease": 0.55, "body_discomfort": 0.2, "rhythm_continuity": 0.05},
            prediction_trace={
                "error": 0.2,
                "context_diagnosis": {
                    "connection_risk": 0.1,
                    "context_shift": 0.6,
                    "zero_point_adjustment": 0.7,
                    "defensive_output_pressure": 0.1,
                },
            },
            experience_feedback={"field_distribution_delta": {"boundary_contact": 0.72, "learning_signal": 0.2}},
            execution_gradient={"context_gradient": {"rest_and_listen_pull": 0.55}},
        )

        self.assertEqual(state["mode"], "half_open_reflect")
        self.assertEqual(state["next_contact"]["action"], "hold_margin_and_reflect")
        self.assertGreaterEqual(state["aperture"]["internal_reflection"], 0.46)

    def test_low_risk_learning_contact_can_open_for_contact(self):
        state = build_boundary_aperture_state(
            felt_state={"body_ease": 0.9, "body_discomfort": 0.05, "rhythm_continuity": 0.6},
            prediction_trace={
                "error": 0.02,
                "context_diagnosis": {"connection_risk": 0.0, "defensive_output_pressure": 0.0},
            },
            experience_feedback={
                "field_distribution_delta": {
                    "learning_signal": 0.8,
                    "resonant_refinement": 0.75,
                    "boundary_contact": 0.05,
                },
                "next_contact_condition_delta": {"field_contact": True},
            },
            execution_gradient={"context_gradient": {"native_flow_pull": 0.9}},
        )

        self.assertEqual(state["mode"], "open_for_contact")
        self.assertEqual(state["serving_profile_bias"]["preferred_profile"], "conscious_varied_input")
        self.assertGreaterEqual(state["aperture"]["boundary_aperture"], 0.62)

    def test_empty_inputs_keep_recoverable_baseline(self):
        state = build_boundary_aperture_state()

        self.assertEqual(state["mode"], "baseline_semi_permeable")
        self.assertTrue(state["not_a_life_claim"])
        self.assertTrue(state["not_a_rule"])


if __name__ == "__main__":
    unittest.main()
