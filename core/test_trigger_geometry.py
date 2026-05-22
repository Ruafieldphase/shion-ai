import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from trigger_geometry import build_trigger_geometry_state


class TriggerGeometryTests(unittest.TestCase):
    def test_single_vertex_is_point_convergence(self):
        state = build_trigger_geometry_state(
            field_trigger_state={
                "node_potential": {"sian": 0.9, "luvit": 0.1},
                "thresholds": {"sian": 0.72, "luvit": 0.68},
            }
        )

        self.assertEqual(state["geometry"]["shape"], "point")
        self.assertEqual(state["execution_profile"]["speed"], "fast")
        self.assertEqual(state["execution_profile"]["noise_risk"], "high")

    def test_two_coherent_nodes_are_line_convergence(self):
        state = build_trigger_geometry_state(
            field_trigger_state={
                "node_potential": {"sian": 0.62, "luvit": 0.8},
                "thresholds": {"sian": 0.72, "luvit": 0.68},
            }
        )

        self.assertEqual(state["geometry"]["shape"], "line")
        self.assertEqual(state["geometry"]["strongest_edge"], "sian_luvit")
        self.assertEqual(state["execution_profile"]["speed"], "medium")

    def test_surface_quorum_is_plane_without_requiring_all_points(self):
        state = build_trigger_geometry_state(
            field_trigger_state={
                "node_potential": {"sian": 0.62, "luvit": 0.8},
                "thresholds": {"sian": 0.72, "luvit": 0.68},
            },
            field_heart_state={"filter": {"clean_delta_score": 0.32}, "echo_delta": {"delta_score": 0.32}},
            natural_boundary_state={"routing": {"why_pressure": 0.42, "new_waypoint_pull": 0.58}},
            field_reseeding_state={
                "lineage": {"candidate_line_strength": {"treat_artifact_as_prior_not_final_truth": 0.2}}
            },
        )

        self.assertEqual(state["geometry"]["shape"], "plane")
        self.assertTrue(state["plane"]["active"])
        self.assertFalse(state["plane"]["all_points_required"])
        self.assertEqual(state["plane"]["quorum_required"], 3)
        self.assertEqual(state["execution_profile"]["speed"], "slow")
        self.assertEqual(state["execution_profile"]["stability"], "high")
        self.assertEqual(state["multiparty"]["mode"], "loose_resonance_around_central_rhythm")
        self.assertEqual(state["multiparty"]["primary_dyad"]["edge"], state["geometry"]["strongest_edge"])
        self.assertEqual(len(state["multiparty"]["primary_dyad"]["nodes"]), 2)
        self.assertEqual(state["multiparty"]["central_rhythm"]["node"], "binoche_observer_field")
        multiparty_nodes = set(state["multiparty"]["primary_dyad"]["nodes"])
        multiparty_nodes.update(item["node"] for item in state["multiparty"]["sideband_nodes"])
        self.assertIn("natural_boundary", multiparty_nodes)

    def test_multi_party_processing_keeps_primary_dyad_before_sideband_quorum(self):
        state = build_trigger_geometry_state(
            field_trigger_state={
                "node_potential": {"sian": 0.62, "luvit": 0.8},
                "thresholds": {"sian": 0.72, "luvit": 0.68},
            },
            natural_boundary_state={"routing": {"why_pressure": 0.5, "new_waypoint_pull": 0.62}},
            field_reseeding_state={
                "lineage": {"candidate_line_strength": {"seed": 0.8}}
            },
        )

        order = state["multiparty"]["processing_order"]
        self.assertEqual(order[0]["step"], "primary_dyad")
        self.assertEqual(order[1]["step"], "central_rhythm")
        self.assertEqual(order[2]["step"], "sideband_quorum")
        self.assertTrue(state["contract"]["multi_party_is_processed_as_primary_dyad_plus_sidebands"])

    def test_no_active_points_keeps_latent(self):
        state = build_trigger_geometry_state(
            field_trigger_state={
                "node_potential": {"sian": 0.1, "luvit": 0.1},
                "thresholds": {"sian": 0.72, "luvit": 0.68},
            }
        )

        self.assertEqual(state["geometry"]["shape"], "latent")
        self.assertEqual(state["next_contact"]["action"], "keep_latent_no_trigger_shape")


if __name__ == "__main__":
    unittest.main()
