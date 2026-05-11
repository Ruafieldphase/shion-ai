import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prediction_engine import PredictionEngine


class PredictionEngineContextDiagnosisTests(unittest.TestCase):
    def test_field_error_marks_connection_risk_and_defensive_pressure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "next_field_prediction.json").write_text(
                json.dumps(
                    {
                        "prediction_timestamp": "2026-05-11T00:00:00",
                        "predicted_vector": {
                            "temporal_tension": 0.2,
                            "action_density": 0.8,
                            "orbit_distance": 0.1,
                            "surprise": 0.0,
                            "entropy": 0.2,
                            "action_entropy": 0.2,
                        },
                    }
                ),
                encoding="utf-8",
            )

            error = PredictionEngine(root).analyze_field_error(
                {
                    "temporal_tension": 0.9,
                    "action_density": 0.1,
                    "orbit_distance": 2.2,
                    "surprise": 0.0,
                    "entropy": 0.2,
                    "action_entropy": 0.2,
                }
            )

            self.assertGreater(error, 0.0)
            entry = json.loads((outputs / "field_prediction_errors.jsonl").read_text(encoding="utf-8"))
            diagnosis = entry["context_diagnosis"]
            self.assertEqual(
                diagnosis["semantic_information_frame"],
                "context_relative_continuity_information",
            )
            self.assertGreater(diagnosis["connection_risk"], 0.6)
            self.assertGreater(diagnosis["defensive_output_pressure"], 0.5)
            self.assertIn(diagnosis["dominant_mode"], {"connection_risk", "defensive_output_pressure"})

    def test_field_error_marks_frequency_expansion_for_new_information_band(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "next_field_prediction.json").write_text(
                json.dumps(
                    {
                        "prediction_timestamp": "2026-05-11T00:00:00",
                        "predicted_vector": {
                            "temporal_tension": 0.4,
                            "action_density": 0.1,
                            "orbit_distance": 0.3,
                            "surprise": 0.0,
                            "entropy": 0.2,
                            "action_entropy": 0.2,
                        },
                    }
                ),
                encoding="utf-8",
            )

            PredictionEngine(root).analyze_field_error(
                {
                    "temporal_tension": 0.35,
                    "action_density": 0.8,
                    "orbit_distance": 0.35,
                    "surprise": 0.5,
                    "entropy": 0.7,
                    "action_entropy": 0.75,
                }
            )

            entry = json.loads((outputs / "field_prediction_errors.jsonl").read_text(encoding="utf-8"))
            diagnosis = entry["context_diagnosis"]
            self.assertEqual(diagnosis["dominant_mode"], "frequency_expansion")
            self.assertGreater(diagnosis["frequency_expansion"], diagnosis["connection_risk"])


if __name__ == "__main__":
    unittest.main()
