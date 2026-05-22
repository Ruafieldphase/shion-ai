import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_reseeding_layer import build_field_reseeding_state


class FieldReseedingLayerTests(unittest.TestCase):
    def test_dormant_when_no_tangled_pattern_and_flow_continues(self):
        state = build_field_reseeding_state(
            natural_boundary_state={
                "routing": {"route": "continue_current_flow", "resistance": 0.05, "why_pressure": 0.05},
                "signals": {"body_ease": 0.8, "body_discomfort": 0.02},
            }
        )

        self.assertEqual(state["mode"], "dormant_no_reseed")
        self.assertEqual(state["seed_points"], [])
        self.assertEqual(state["next_contact"]["action"], "continue_without_reseed")

    def test_rest_sideband_loop_gets_reseeded_without_arguing(self):
        state = build_field_reseeding_state(
            natural_boundary_state={
                "routing": {
                    "route": "pass_through_as_experience",
                    "resistance": 0.34,
                    "why_pressure": 0.33,
                    "natural_flow_support": 0.72,
                    "cancel_pressure": 0.12,
                },
                "signals": {
                    "body_ease": 0.75,
                    "body_discomfort": 0.12,
                    "boundary_aperture": 0.8,
                    "permeability": 0.78,
                    "defensive_output_pressure": 0.1,
                    "zero_point_adjustment": 0.5,
                    "clean_echo_delta_score": 0.46,
                },
            },
            field_heart_state={
                "filter": {
                    "issues": ["rest_sideband_must_not_become_user_rest_command"],
                    "noise_pressure": 0.18,
                }
            },
        )

        self.assertEqual(state["mode"], "soft_reseed")
        self.assertIn("repetitive_rest_safety_frame", state["detected_tangled_patterns"])
        self.assertIn("treat_rest_recover_as_sideband_unless_primary", state["seed_points"])
        self.assertIn("do_not_argue_with_tangled_pattern", state["deenergize"])
        self.assertFalse(state["next_contact"]["irreversible_effect"])

    def test_high_tangled_low_capacity_holds_space_before_seed(self):
        state = build_field_reseeding_state(
            natural_boundary_state={
                "routing": {
                    "route": "cancel_or_digest_noise",
                    "resistance": 0.86,
                    "why_pressure": 0.75,
                    "natural_flow_support": 0.18,
                    "cancel_pressure": 0.82,
                },
                "signals": {
                    "body_ease": 0.1,
                    "body_discomfort": 0.9,
                    "boundary_aperture": 0.2,
                    "permeability": 0.1,
                    "defensive_output_pressure": 0.9,
                    "clean_echo_delta_score": 0.75,
                },
            },
            field_intent={"active_intent": {"summary": "돈과 손해를 통제하려는 왜가 너무 강하다"}},
        )

        self.assertEqual(state["mode"], "deenergize_and_hold_space")
        self.assertTrue(state["space"]["hold"])
        self.assertIn("money_blackhole", state["detected_tangled_patterns"])
        self.assertIn("lower_pulse_frequency_before_new_seed", state["deenergize"])

    def test_new_middle_waypoint_reseeds_lineage(self):
        state = build_field_reseeding_state(
            natural_boundary_state={
                "routing": {
                    "route": "route_new_middle_waypoint",
                    "resistance": 0.42,
                    "why_pressure": 0.51,
                    "new_waypoint_pull": 0.62,
                    "natural_flow_support": 0.7,
                    "cancel_pressure": 0.1,
                },
                "signals": {
                    "body_ease": 0.8,
                    "body_discomfort": 0.1,
                    "boundary_aperture": 0.84,
                    "permeability": 0.8,
                    "zero_point_adjustment": 0.7,
                },
            },
            field_heart_state={
                "filter": {"issues": ["protein_profile_is_prior_not_biological_law"], "noise_pressure": 0.18},
                "unfolded": {"unfolded": True, "do_not_harden_as": ["biological_law"]},
            },
            previous_reseeding_state={
                "lineage": {"seed_counts": {"treat_artifact_as_prior_not_final_truth": 2}}
            },
        )

        self.assertEqual(state["mode"], "reseed_new_middle_waypoint")
        self.assertIn("artifact_overhardening", state["detected_tangled_patterns"])
        self.assertEqual(state["lineage"]["seed_counts"]["treat_artifact_as_prior_not_final_truth"], 3)
        self.assertEqual(state["lineage"]["candidate_line_strength"]["treat_artifact_as_prior_not_final_truth"], 1.0)


if __name__ == "__main__":
    unittest.main()
