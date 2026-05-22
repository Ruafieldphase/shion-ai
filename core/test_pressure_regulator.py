import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from natural_boundary_router import build_natural_boundary_router_state
from pressure_regulator import build_pressure_regulator_state


class PressureRegulatorTests(unittest.TestCase):
    def test_low_pressure_continues_without_added_decompression(self):
        state = build_pressure_regulator_state(
            felt_state={"body_ease": 0.82, "body_discomfort": 0.03, "rhythm_continuity": 0.8},
            prediction_trace={"error": 0.02, "context_diagnosis": {"context_shift": 0.01}},
            boundary_state={"aperture": {"boundary_aperture": 0.82, "permeability": 0.8}},
        )

        self.assertEqual(state["handling"]["route"], "continue_current_rhythm")
        self.assertLess(state["pressure"]["total_pressure"], 0.18)
        self.assertTrue(state["contract"]["pressure_is_not_removed_by_default"])

    def test_conscious_simulation_pressure_decompresses_before_more_analysis(self):
        state = build_pressure_regulator_state(
            felt_state={"body_ease": 0.35, "body_discomfort": 0.55, "rhythm_continuity": 0.2},
            prediction_trace={
                "error": 0.72,
                "context_diagnosis": {
                    "context_shift": 0.68,
                    "connection_risk": 0.25,
                    "defensive_output_pressure": 0.86,
                    "zero_point_adjustment": 0.32,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.46, "permeability": 0.42, "internal_reflection": 0.7}},
            dark_field_state={"threshold": {"dark_field_pressure": 0.45, "dynamic_threshold": 0.5}},
            field_intent={
                "active_intent": {
                    "summary": "의식의 시뮬레이션이 강해져서 머리가 복잡하고 별별 생각이 다 난다"
                }
            },
        )

        self.assertEqual(state["handling"]["route"], "make_gap_for_decompression")
        self.assertEqual(state["handling"]["dominant_source"], "conscious_simulation_pressure")
        self.assertEqual(
            state["handling"]["action"],
            "decompress_conscious_simulation_into_body_or_external_field",
        )
        self.assertIn("forced_exercise", state["handling"]["do_not_harden_as"])

    def test_external_variable_can_be_routed_as_middle_waypoint(self):
        state = build_pressure_regulator_state(
            felt_state={"body_ease": 0.72, "body_discomfort": 0.18, "rhythm_continuity": 0.34},
            prediction_trace={
                "error": 0.36,
                "context_diagnosis": {
                    "context_shift": 0.76,
                    "connection_risk": 0.06,
                    "defensive_output_pressure": 0.03,
                    "zero_point_adjustment": 0.74,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.82, "permeability": 0.78, "internal_reflection": 0.18}},
            dark_field_state={"threshold": {"dark_field_pressure": 0.18, "dynamic_threshold": 0.72}},
            field_intent={"active_intent": {"summary": "날씨와 비 같은 외부 변수를 새 중간 목표지점으로 받아들인다"}},
        )

        self.assertEqual(state["handling"]["route"], "route_as_new_middle_waypoint")
        self.assertEqual(state["handling"]["dominant_source"], "natural_pressure")
        self.assertIn(
            state["scalar_flow"]["valve"],
            {"balanced_receive_and_unfold", "receive_gently_without_overfilling"},
        )

    def test_unconscious_boundary_pressure_holds_gap_before_interpretation(self):
        state = build_pressure_regulator_state(
            felt_state={"body_ease": 0.12, "body_discomfort": 0.88, "rhythm_continuity": 0.1},
            prediction_trace={
                "error": 0.58,
                "context_diagnosis": {
                    "context_shift": 0.46,
                    "connection_risk": 0.62,
                    "defensive_output_pressure": 0.32,
                    "zero_point_adjustment": 0.15,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.18, "permeability": 0.16, "internal_reflection": 0.84, "digestion_bias": 0.78}},
            dark_field_state={"threshold": {"dark_field_pressure": 0.86, "dynamic_threshold": 0.4}},
            field_heart_state={"filter": {"noise_pressure": 0.36}},
        )

        self.assertEqual(state["handling"]["route"], "hold_gap_before_interpretation")
        self.assertIn(state["handling"]["dominant_source"], {"unconscious_pressure", "boundary_collision_pressure"})
        self.assertEqual(state["handling"]["action"], "digest_without_forcing_meaning")

    def test_pressure_state_can_bias_natural_boundary_router_without_forcing_execution(self):
        pressure_state = build_pressure_regulator_state(
            felt_state={"body_ease": 0.75, "body_discomfort": 0.16, "rhythm_continuity": 0.35},
            prediction_trace={
                "error": 0.34,
                "context_diagnosis": {
                    "context_shift": 0.72,
                    "connection_risk": 0.05,
                    "defensive_output_pressure": 0.02,
                    "zero_point_adjustment": 0.76,
                },
            },
            boundary_state={"aperture": {"boundary_aperture": 0.84, "permeability": 0.8}},
            field_intent={"active_intent": {"summary": "비가 오면 노이즈가 아니라 새 중간 목표지점으로 둔다"}},
        )
        router = build_natural_boundary_router_state(
            field_heart_state={
                "echo": {"primary_action": "ACTION_OBSERVE", "salience": 0.62, "convergence": 0.58},
                "echo_delta": {"delta_score": 0.46, "curvature_delta": 0.56, "convergence_delta": 0.42},
                "filter": {"clean_delta_score": 0.46},
            },
            felt_state={"body_ease": 0.75, "body_discomfort": 0.16},
            prediction_trace={"error": 0.34, "context_diagnosis": {"context_shift": 0.72, "connection_risk": 0.05}},
            boundary_state={"aperture": {"boundary_aperture": 0.84, "permeability": 0.8}},
            pressure_state=pressure_state,
            field_intent={"active_intent": {"summary": "왜 비가 새 경계가 되었을까?"}},
        )

        self.assertEqual(router["pressure_handling"]["route"], "route_as_new_middle_waypoint")
        self.assertIn(router["routing"]["route"], {"route_new_middle_waypoint", "pass_through_as_experience"})
        self.assertFalse(router["next_contact"]["irreversible_effect"])


if __name__ == "__main__":
    unittest.main()
