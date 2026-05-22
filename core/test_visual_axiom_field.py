import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from visual_axiom_field import build_ai_handoff_markdown, build_visual_axiom_field


class VisualAxiomFieldTests(unittest.TestCase):
    def test_sequence_preserves_order_and_non_proof_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "origin.png"
            second = Path(tmp) / "zen.png"
            first.write_bytes(b"origin")
            second.write_bytes(b"zen")

            state = build_visual_axiom_field(
                [
                    {"id": "origin", "path": str(first), "role": "root", "reading": "root", "maps_to": ["base"]},
                    {"id": "zen", "path": str(second), "role": "path", "reading": "path", "maps_to": ["curve"]},
                ],
                current_context="life rhythm image sequence",
            )

        self.assertEqual(state["sequence"][0]["id"], "origin")
        self.assertEqual(state["sequence"][1]["id"], "zen")
        self.assertEqual(state["coverage"]["existing"], 2)
        self.assertTrue(state["not_a_scientific_claim"])
        self.assertTrue(state["not_a_trading_signal"])
        self.assertIn("shared_visual_coordinate_for_ai_observers", state["handoff_contract"]["use_as"])

    def test_missing_images_are_kept_as_coordinates(self):
        state = build_visual_axiom_field(
            [{"id": "missing", "path": "C:/definitely/not/here.png", "role": "coordinate"}]
        )

        self.assertEqual(state["coverage"]["missing"], 1)
        self.assertFalse(state["sequence"][0]["exists"])
        self.assertEqual(state["sequence"][0]["role"], "coordinate")

    def test_handoff_markdown_keeps_visual_axiom_language(self):
        state = build_visual_axiom_field(
            [{"id": "origin", "path": "C:/missing.png", "role": "root", "reading": "life", "maps_to": ["curve"]}],
            current_context="read as life rhythm",
        )
        markdown = build_ai_handoff_markdown(state)

        self.assertIn("visual axioms", markdown)
        self.assertIn("not as a literal physics proof", markdown)
        self.assertIn("read as life rhythm", markdown)


if __name__ == "__main__":
    unittest.main()

