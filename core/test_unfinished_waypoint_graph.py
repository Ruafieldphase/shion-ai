import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from unfinished_waypoint_graph import UnfinishedWaypointGraph


class UnfinishedWaypointGraphTests(unittest.TestCase):
    def test_build_connects_context_matching_unfinished_waypoints(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            entries = [
                self._entry("2026-05-04T10:00:00", 0.72, 0.58, 0.84, 0.78, 0.04),
                self._entry("2026-05-04T10:01:00", 0.70, 0.56, 0.82, 0.76, 0.05),
                self._entry("2026-05-04T10:02:00", 0.10, 0.12, 0.22, 0.20, 0.52),
            ]
            (outputs / "unfinished_axioms.jsonl").write_text(
                "\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries) + "\n",
                encoding="utf-8",
            )

            graph_path = UnfinishedWaypointGraph(root).build(
                rhythm_frame={
                    "waves": {
                        "field": {"salience": 0.48, "curvature": 0.18},
                        "goal_field": {"bridge_gain": 0.66},
                        "axiom": {"overfit_pressure": 0.12},
                        "dark_neuron": {"redarkening_pressure": 0.16},
                        "digestion": {"sleep_debt": 0.42},
                    },
                    "zone2": {"openness": 0.72},
                    "medium": {"conductivity": 0.68, "resistance": 0.18},
                    "dark_field": {"gravity": 0.22},
                    "perspective_frame": {"metacognitive_refraction": 0.76},
                    "interference": {"destructive": 0.18},
                    "zone2_regulation": {"phase": "active_margin", "chaos_pressure": 0.22},
                }
            )
            graph = json.loads(graph_path.read_text(encoding="utf-8"))

            self.assertEqual(graph["version"], "unfinished-waypoint-graph-v1")
            self.assertEqual(graph["stats"]["node_count"], 3)
            self.assertGreaterEqual(graph["stats"]["edge_count"], 1)
            self.assertTrue(
                any(edge["type"] in {"reflect", "ascend", "descend", "tunnel"} for edge in graph["edges"])
            )
            silent_nodes = [
                node for node in graph["nodes"].values()
                if node["metrics"]["fixed_weight_risk"] >= 0.48
            ]
            self.assertEqual(silent_nodes[0]["status"], "silent")
            self.assertEqual(
                graph["principle"],
                "unfinished_waypoints_connect_by_current_torus_context_not_permanent_truth",
            )
            self.assertEqual(
                graph["dream_replay"]["principle"],
                "manual_dream_replay_becomes_edge_transition_memory",
            )

    def test_empty_source_writes_empty_graph(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "outputs").mkdir()
            graph_path = UnfinishedWaypointGraph(root).build()
            graph = json.loads(graph_path.read_text(encoding="utf-8"))

            self.assertEqual(graph["stats"]["node_count"], 0)
            self.assertEqual(graph["edges"], [])
            self.assertEqual(graph["dream_replay"]["current_edge_count"], 0)

    def test_build_appends_dream_replay_edge_transition_trace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            first_entries = [
                self._entry("2026-05-04T10:00:00", 0.72, 0.58, 0.84, 0.78, 0.04),
                self._entry("2026-05-04T10:01:00", 0.70, 0.56, 0.82, 0.76, 0.05),
            ]
            (outputs / "unfinished_axioms.jsonl").write_text(
                "\n".join(json.dumps(entry, ensure_ascii=False) for entry in first_entries) + "\n",
                encoding="utf-8",
            )

            graph_builder = UnfinishedWaypointGraph(root)
            graph_builder.build(rhythm_frame=self._rhythm_frame())

            second_entries = [
                self._entry("2026-05-04T10:00:00", 0.72, 0.58, 0.84, 0.18, 0.58),
                self._entry("2026-05-04T10:01:00", 0.70, 0.56, 0.82, 0.16, 0.59),
            ]
            (outputs / "unfinished_axioms.jsonl").write_text(
                "\n".join(json.dumps(entry, ensure_ascii=False) for entry in second_entries) + "\n",
                encoding="utf-8",
            )
            graph_path = graph_builder.build(rhythm_frame=self._rhythm_frame())

            graph = json.loads(graph_path.read_text(encoding="utf-8"))
            trace_lines = (outputs / "unfinished_waypoint_edge_trace.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            latest_trace = json.loads(trace_lines[-1])

            self.assertEqual(len(trace_lines), 2)
            self.assertEqual(graph["dream_replay"]["previous_generated_at"], latest_trace["summary"]["previous_generated_at"])
            self.assertGreaterEqual(graph["dream_replay"]["significant_transition_count"], 1)
            self.assertTrue(
                any(transition["event"] == "decayed" for transition in latest_trace["transitions"])
            )

    def _entry(
        self,
        timestamp: str,
        bridge_gain: float,
        waypoint_pressure: float,
        failure_bridge: float,
        contextual_activation: float,
        fixed_weight_risk: float,
    ) -> dict:
        return {
            "timestamp": timestamp,
            "status": "unfinished_puzzle",
            "reason": "test",
            "transition": "boundary_to_unpack",
            "axiom": {
                "phase": "axiom_open",
                "overfit_pressure": fixed_weight_risk,
                "failure_spectrum": {"bridge_value": failure_bridge},
                "archive_resonance": contextual_activation,
                "waypoint_resonance": {
                    "contextual_activation": contextual_activation,
                    "fixed_weight_risk": fixed_weight_risk,
                },
            },
            "goal_field": {
                "phase": "near_field",
                "waypoint_pressure": waypoint_pressure,
                "bridge_gain": bridge_gain,
            },
            "reuse_rule": "future_axioms_reactivate_by_current_context_not_visit_count",
            "waypoint_policy": "frequent_middle_destinations_are_contextual_refraction_points_not_fixed_beliefs",
        }

    def _rhythm_frame(self) -> dict:
        return {
            "waves": {
                "field": {"salience": 0.48, "curvature": 0.18},
                "goal_field": {"bridge_gain": 0.66},
                "axiom": {"overfit_pressure": 0.12},
                "dark_neuron": {"redarkening_pressure": 0.16},
                "digestion": {"sleep_debt": 0.42},
            },
            "zone2": {"openness": 0.72},
            "medium": {"conductivity": 0.68, "resistance": 0.18},
            "dark_field": {"gravity": 0.22},
            "perspective_frame": {"metacognitive_refraction": 0.76},
            "interference": {"destructive": 0.18},
            "zone2_regulation": {"phase": "active_margin", "chaos_pressure": 0.22},
        }


if __name__ == "__main__":
    unittest.main()
