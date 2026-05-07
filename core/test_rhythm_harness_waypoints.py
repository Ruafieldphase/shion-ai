import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rhythm_harness import NonEuclideanRhythmHarness


class RhythmHarnessWaypointTests(unittest.TestCase):
    def test_unfinished_waypoints_reactivate_by_context_not_visit_count(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            path = outputs / "unfinished_axioms.jsonl"
            entries = [
                {
                    "status": "unfinished_puzzle",
                    "goal_field": {"bridge_gain": 0.62, "waypoint_pressure": 0.58},
                    "axiom": {"failure_spectrum": {"bridge_value": 0.82}},
                },
                {
                    "status": "unfinished_puzzle",
                    "goal_field": {"bridge_gain": 0.60, "waypoint_pressure": 0.56},
                    "axiom": {"failure_spectrum": {"bridge_value": 0.80}},
                },
                {
                    "status": "unfinished_puzzle",
                    "goal_field": {"bridge_gain": 0.64, "waypoint_pressure": 0.60},
                    "axiom": {"failure_spectrum": {"bridge_value": 0.78}},
                },
            ]
            path.write_text(
                "\n".join(json.dumps(entry) for entry in entries) + "\n",
                encoding="utf-8",
            )

            harness = NonEuclideanRhythmHarness(root)
            aligned = harness._unfinished_waypoint_resonance(
                limit=3,
                goal_field={"bridge_gain": 0.61, "waypoint_pressure": 0.57},
                zone2={"openness": 0.70},
                medium={"conductivity": 0.66, "resistance": 0.22},
                awareness={"present_contact": 0.68},
                failure_spectrum={"bridge_value": 0.81},
            )
            mismatched = harness._unfinished_waypoint_resonance(
                limit=3,
                goal_field={"bridge_gain": 0.10, "waypoint_pressure": 0.12},
                zone2={"openness": 0.24},
                medium={"conductivity": 0.18, "resistance": 0.74},
                awareness={"present_contact": 0.20},
                failure_spectrum={"bridge_value": 0.18},
            )

            self.assertEqual(aligned["visit_frequency"], 1.0)
            self.assertGreater(aligned["contextual_activation"], mismatched["contextual_activation"])
            self.assertGreater(mismatched["fixed_weight_risk"], aligned["fixed_weight_risk"])
            self.assertEqual(
                aligned["principle"],
                "frequent_waypoints_reactivate_by_context_not_permanent_weight",
            )


if __name__ == "__main__":
    unittest.main()
