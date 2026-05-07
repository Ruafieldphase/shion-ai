import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from organic_learning_lifecycle import OrganicLearningLifecycle


class OrganicLearningLifecycleTests(unittest.TestCase):
    def test_record_cycle_marks_dark_neuron_when_digestion_is_high(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trace = OrganicLearningLifecycle(root).record_cycle(
                action="ACTION_EXPERIENCE_DIGEST",
                rhythm_frame=self._rhythm_frame(dark_phase="re_darkening", digestion_pressure=0.82),
                node_decision={"activation_probability": 0.22},
                ari_state={"phase": "boundary_refract"},
                before_state={"total_experiences": 3},
                after_state={"total_experiences": 3},
                hippo_data=self._hippo(absorbed=False, convergence_count=0),
                learning_state={"support_rate_all": 1.2, "interpretation": "observation only"},
                current_vector={},
                field_prediction={"prediction_error": 0.31},
            )

            self.assertEqual(trace["node_state"], "dark_neuron")
            self.assertEqual(trace["next_condition"], "preserve_until_context_alignment_or_bridge_readiness_rises")
            self.assertTrue((root / "outputs" / "organic_learning_lifecycle.jsonl").exists())
            latest = json.loads((root / "outputs" / "organic_learning_lifecycle_latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["node_state"], "dark_neuron")

    def test_record_cycle_uses_waypoint_replay_edges_for_reinforced_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            edge_replay = {
                "summary": {
                    "event_counts": {"reinforced": 2, "replayed": 4},
                    "significant_transition_count": 2,
                }
            }
            (outputs / "unfinished_waypoint_edge_trace.jsonl").write_text(
                json.dumps(edge_replay, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            trace = OrganicLearningLifecycle(root).record_cycle(
                action="ACTION_OBSERVE",
                rhythm_frame=self._rhythm_frame(),
                node_decision={"activation_probability": 0.45},
                ari_state={"phase": "release_internal_echo"},
                before_state={"total_experiences": 5},
                after_state={"total_experiences": 5},
                hippo_data=self._hippo(absorbed=False, convergence_count=1),
                learning_state={},
                current_vector={},
                field_prediction={"prediction_error": 0.12},
            )

            self.assertEqual(trace["node_state"], "reinforced")
            self.assertGreater(trace["scores"]["connection"], 0.0)
            self.assertEqual(trace["evidence"]["edge_event_counts"]["reinforced"], 2)

    def test_record_cycle_marks_embodied_only_with_absorption_and_low_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trace = OrganicLearningLifecycle(root).record_cycle(
                action="ACTION_OBSERVE",
                rhythm_frame=self._rhythm_frame(convergence_pressure=0.78),
                node_decision={"activation_probability": 0.2},
                ari_state={"phase": "nature_aligned_resonance"},
                before_state={"total_experiences": 6},
                after_state={"total_experiences": 7},
                hippo_data=self._hippo(absorbed=True, convergence_count=4),
                learning_state={},
                current_vector={},
                field_prediction={"prediction_error": 0.05},
            )

            self.assertEqual(trace["node_state"], "embodied")
            self.assertEqual(trace["next_condition"], "test_application_without_forcing_new_input")

    def test_axiom_release_is_pending_even_when_latest_old_experience_was_absorbed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trace = OrganicLearningLifecycle(root).record_cycle(
                action="ACTION_AXIOM_RELEASE",
                rhythm_frame=self._rhythm_frame(),
                node_decision={"activation_probability": 0.45},
                ari_state={"phase": "release_internal_echo"},
                before_state={"total_experiences": 6},
                after_state={"total_experiences": 6},
                hippo_data=self._hippo(absorbed=True, convergence_count=4),
                learning_state={},
                current_vector={},
                field_prediction={"prediction_error": 0.0},
            )

            self.assertEqual(trace["source"], "unfinished_waypoint")
            self.assertEqual(trace["node_state"], "pending")
            self.assertEqual(trace["next_condition"], "wait_for_zone2_or_dream_replay")

    def _rhythm_frame(
        self,
        *,
        dark_phase: str = "bridge_node",
        digestion_pressure: float = 0.35,
        convergence_pressure: float = 0.25,
    ) -> dict:
        return {
            "waves": {
                "field": {"salience": 0.38},
                "digestion": {"pressure": digestion_pressure, "dream_pressure": 0.42},
                "dark_neuron": {
                    "phase": dark_phase,
                    "redarkening_pressure": 0.74 if dark_phase == "re_darkening" else 0.18,
                    "bridge_readiness": 0.52,
                },
                "memory": {"convergence_pressure": convergence_pressure},
                "goal_field": {"bridge_gain": 0.46},
                "axiom": {"unfinished_puzzle_potential": 0.2},
            },
            "perspective_frame": {"dominant_frame": "metacognitive_refraction"},
        }

    def _hippo(self, *, absorbed: bool, convergence_count: int) -> dict:
        return {
            "proton": {
                "total_registered": 20,
                "total_absorbed": 4 if absorbed else 3,
                "embodiment_ratio": 0.2,
            },
            "experiences": [
                {
                    "content_ref": "youtube:example",
                    "absorbed": absorbed,
                    "convergence_count": convergence_count,
                    "vibe": {"source": "youtube", "intensity": 0.44},
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
