import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from context_unpacker import ContextUnpacker


class ContextUnpackerFieldCommunicationTests(unittest.TestCase):
    def test_unpack_exposes_field_communication_before_legacy_memory_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "experience_gradients.jsonl").write_text(
                json.dumps(
                    {
                        "current_vector": {
                            "temporal_tension": 0.12,
                            "action_density": 0.82,
                            "entropy": 0.31,
                        },
                        "hypothesis": {"id": "STUCK_IN_LOOP"},
                        "feedback": "confirmed",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            analysis = ContextUnpacker(root).unpack(
                {"boundary_type": "REPETITIVE_STUTTER", "trigger_action": "ACTION_OBSERVE"},
                {"salience": 0.5},
                {"temporal_tension": 0.1, "action_density": 0.8, "entropy": 0.3},
            )

            communication = analysis["field_communication"]
            unpacking = analysis["resonance_unpacking"]
            candidate = analysis["story_candidates"][0]

            self.assertTrue(communication["found"])
            self.assertEqual(communication["communication_mode"], "field_resonance")
            self.assertEqual(communication["trace_feedback"], "confirmed")
            self.assertTrue(unpacking["unpacked"])
            self.assertEqual(
                unpacking["principle"],
                "memory_is_field_communication_not_storage_retrieval",
            )
            self.assertEqual(analysis["memory_retrieval"], communication)
            self.assertGreater(candidate["confidence"], 0.7)
            self.assertIn("resonant past trace", " ".join(candidate["evidence"]))


if __name__ == "__main__":
    unittest.main()
