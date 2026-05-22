import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from felt_state_store import load_state, normalize_felt_state, save_state


class FeltStateStoreTests(unittest.TestCase):
    def test_normalize_clamps_felt_fields_without_dropping_audio_membrane(self):
        state = normalize_felt_state(
            {
                "flow_energy": 1.4,
                "relation_drift": -0.2,
                "body_discomfort": "0.25",
                "body_ease": None,
                "rhythm_continuity": 0.75,
                "audio": {"envelope": 0.9, "onset": 2.0, "brightness": "bad"},
                "source": "test",
            }
        )

        self.assertEqual(state["flow_energy"], 1.0)
        self.assertEqual(state["relation_drift"], 0.0)
        self.assertEqual(state["body_discomfort"], 0.25)
        self.assertEqual(state["body_ease"], 0.6)
        self.assertEqual(state["rhythm_continuity"], 0.75)
        self.assertEqual(state["audio"]["envelope"], 0.9)
        self.assertEqual(state["audio"]["onset"], 1.0)
        self.assertEqual(state["audio"]["brightness"], 0.0)
        self.assertEqual(state["source"], "test")

    def test_save_and_load_state_uses_persisted_membrane(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outputs" / "felt_body_state.json"
            saved = save_state(
                path,
                {
                    "flow_energy": 0.7,
                    "relation_drift": 0.1,
                    "body_discomfort": 0.2,
                    "body_ease": 0.8,
                    "rhythm_continuity": 0.64,
                    "audio": {"envelope": 0.62, "confidence": 0.5},
                },
            )

            self.assertTrue(path.exists())
            self.assertFalse(path.with_name("felt_body_state.json.tmp").exists())
            self.assertEqual(load_state(path)["flow_energy"], saved["flow_energy"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["audio"]["envelope"], 0.62)


if __name__ == "__main__":
    unittest.main()
