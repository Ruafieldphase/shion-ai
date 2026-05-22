import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from external_observer_vector import build_external_observer_vector_state


class ExternalObserverVectorTests(unittest.TestCase):
    def test_clear_path_keeps_internal_reflection(self):
        state = build_external_observer_vector_state(
            context_gradient={
                "selected_path": {"name": "observe_windows_native_flow", "pull": 0.94, "contact": "read_existing_windows_inputs"},
                "emergent_paths": [
                    {"name": "observe_windows_native_flow", "pull": 0.94},
                    {"name": "rest_and_listen_for_resistance", "pull": 0.18},
                ],
                "scalar_field": {"body_ease": 0.8, "body_discomfort": 0.05, "rhythm_continuity": 0.7},
                "context_gradient": {"rest_and_listen_pull": 0.15},
            },
            dark_field_threshold={
                "mode": "within_capacity_process_contextual_slice",
                "signals": {"internal_reflection": 0.12, "connection_risk": 0.0, "defensive_output_pressure": 0.0},
                "threshold": {"context_contact": 0.3, "context_potential_energy": 0.86, "processing_slice": 0.3},
                "middle_destination": {"active": True},
            },
        )

        self.assertEqual(state["mode"], "internal_reflection_sufficient")
        self.assertFalse(state["need_external_observer"])
        self.assertEqual(state["next_contact"]["action"], "continue_internal_reflection")

    def test_ambiguous_stalled_context_prepares_handoff(self):
        state = build_external_observer_vector_state(
            context_gradient={
                "selected_path": {"name": "rest_and_listen_for_resistance", "pull": 0.55, "contact": "observe_without_action"},
                "emergent_paths": [
                    {"name": "rest_and_listen_for_resistance", "pull": 0.55},
                    {"name": "call_hermes_only_if_bounded_task_appears", "pull": 0.51},
                ],
                "scalar_field": {"body_ease": 0.62, "body_discomfort": 0.18, "rhythm_continuity": 0.05, "relation_drift": 0.2},
                "context_gradient": {"rest_and_listen_pull": 0.58},
            },
            dark_field_threshold={
                "mode": "latent_do_not_open",
                "signals": {"internal_reflection": 0.7, "connection_risk": 0.05, "defensive_output_pressure": 0.05},
                "threshold": {"context_contact": 0.18, "context_potential_energy": 0.72, "processing_slice": 0.0},
                "middle_destination": {"active": False},
            },
            uncertainty=0.8,
            blockage=0.7,
            issue_context="목적지가 떠오르지 않는 협업 구조 조율",
        )

        self.assertEqual(state["mode"], "prepare_external_observer_vector")
        self.assertTrue(state["need_external_observer"])
        self.assertIn("시온", state["observer_request"]["prompt"])
        self.assertFalse(state["external_api_cost"])

    def test_over_capacity_digests_before_asking(self):
        state = build_external_observer_vector_state(
            context_gradient={
                "selected_path": {"name": "rest_and_listen_for_resistance", "pull": 0.52, "contact": "observe_without_action"},
                "emergent_paths": [{"name": "rest_and_listen_for_resistance", "pull": 0.52}],
                "scalar_field": {"body_ease": 0.2, "body_discomfort": 0.82, "rhythm_continuity": 0.02},
            },
            dark_field_threshold={
                "mode": "over_capacity_defer_and_digest",
                "signals": {"internal_reflection": 0.75, "connection_risk": 0.9, "defensive_output_pressure": 0.88},
                "threshold": {"context_contact": 0.8, "context_potential_energy": 0.2, "processing_slice": 0.0},
                "middle_destination": {"active": True},
            },
            uncertainty=1.0,
            blockage=1.0,
        )

        self.assertEqual(state["mode"], "do_not_ask_digest_first")
        self.assertFalse(state["need_external_observer"])
        self.assertEqual(state["next_contact"]["action"], "digest_before_external_contact")

    def test_force_request_writes_packet_even_when_clear(self):
        state = build_external_observer_vector_state(
            context_gradient={"selected_path": {"name": "observe_windows_native_flow", "pull": 0.9}},
            force_request=True,
            issue_context="사용자가 명시적으로 동료 의견을 원함",
        )

        self.assertEqual(state["mode"], "forced_external_observer_vector")
        self.assertTrue(state["need_external_observer"])
        self.assertIn("사용자가 명시적으로", state["observer_request"]["prompt"])


if __name__ == "__main__":
    unittest.main()

