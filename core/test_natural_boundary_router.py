import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from natural_boundary_router import build_natural_boundary_router_state


class NaturalBoundaryRouterTests(unittest.TestCase):
    def test_low_resistance_continues_current_flow(self):
        state = build_natural_boundary_router_state(
            field_heart_state={"echo_delta": {"delta_score": 0.02}},
            felt_state={"body_ease": 0.8, "body_discomfort": 0.02},
            prediction_trace={"error": 0.01, "context_diagnosis": {"context_shift": 0.01}},
            boundary_state={"aperture": {"boundary_aperture": 0.8, "permeability": 0.8}},
        )

        self.assertEqual(state["routing"]["route"], "continue_current_flow")
        self.assertFalse(state["middle_waypoint"]["active"])

    def test_high_pressure_cancels_or_digests_before_reentry(self):
        state = build_natural_boundary_router_state(
            field_heart_state={"echo_delta": {"delta_score": 0.7}},
            felt_state={"body_ease": 0.1, "body_discomfort": 0.9},
            prediction_trace={
                "error": 0.9,
                "context_diagnosis": {
                    "context_shift": 0.8,
                    "connection_risk": 0.95,
                    "defensive_output_pressure": 0.9,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.2, "permeability": 0.1, "digestion_bias": 0.8}},
            dark_field_state={"threshold": {"dark_field_pressure": 0.9, "dynamic_threshold": 0.4}},
        )

        self.assertEqual(state["routing"]["route"], "cancel_or_digest_noise")
        self.assertEqual(state["next_contact"]["action"], "digest_before_reentry")

    def test_resistance_and_why_can_route_new_middle_waypoint(self):
        state = build_natural_boundary_router_state(
            field_heart_state={
                "echo": {"primary_action": "ACTION_AXIOM_RELEASE", "salience": 0.72, "convergence": 0.55},
                "echo_delta": {
                    "delta_score": 0.74,
                    "curvature_delta": 0.8,
                    "convergence_delta": 0.7,
                    "action_changed": True,
                    "artifact_changed": True,
                },
                "filter": {"clean_delta_score": 0.68, "issues": ["protein_profile_is_prior_not_biological_law"]},
                "unfolded": {
                    "unfolded": True,
                    "unfolded_context": "protein_structure_dialogue_converged_into_aqp4_prism_prior",
                    "implementation_direction": "connect_as_bounded_runtime_prior_not_biological_law",
                    "do_not_harden_as": ["biological_law"],
                },
            },
            felt_state={"body_ease": 0.78, "body_discomfort": 0.12},
            prediction_trace={
                "error": 0.32,
                "context_diagnosis": {
                    "context_shift": 0.55,
                    "connection_risk": 0.05,
                    "defensive_output_pressure": 0.02,
                    "zero_point_adjustment": 0.65,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.78, "permeability": 0.74, "internal_reflection": 0.34}},
            dark_field_state={"threshold": {"dark_field_pressure": 0.18, "dynamic_threshold": 0.72}},
            field_intent={"active_intent": {"summary": "왜 이 경계가 새 목표지점으로 기울었을까?"}},
        )

        self.assertEqual(state["routing"]["route"], "route_new_middle_waypoint")
        self.assertTrue(state["middle_waypoint"]["active"])
        self.assertEqual(
            state["middle_waypoint"]["candidate"],
            "protein_structure_dialogue_converged_into_aqp4_prism_prior",
        )
        self.assertIn("biological_law", state["middle_waypoint"]["do_not_harden_as"])

    def test_mid_resistance_passes_through_as_experience(self):
        state = build_natural_boundary_router_state(
            field_heart_state={"echo_delta": {"delta_score": 0.22, "curvature_delta": 0.2}},
            felt_state={"body_ease": 0.65, "body_discomfort": 0.18},
            prediction_trace={
                "error": 0.2,
                "context_diagnosis": {"context_shift": 0.18, "connection_risk": 0.08, "defensive_output_pressure": 0.05},
            },
            boundary_state={"aperture": {"boundary_aperture": 0.65, "permeability": 0.62, "internal_reflection": 0.1}},
        )

        self.assertIn(state["routing"]["route"], {"pass_through_as_experience", "continue_current_flow"})
        self.assertTrue(state["contract"]["resistance_is_signal_not_error"])


if __name__ == "__main__":
    unittest.main()
