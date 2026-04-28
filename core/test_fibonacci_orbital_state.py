import json
import threading
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fibonacci_orbital_hippocampus import BASE_RADIUS, FibonacciOrbitalHippocampus
from autonomous_experience_loop import AutonomousExperienceLoop
from vision_explorer import VisionExplorer


class FakeVision:
    available = True

    def explore_image(self, path):
        return {
            "explored": True,
            "content_ref": f"vision:{Path(path).name}",
            "vibe": {"entropy": 0.42, "phase": "EXPANSION"},
            "description": "structured bright image",
        }


class HippocampusStateTests(unittest.TestCase):
    def test_legacy_state_is_repaired_without_collapsing_absorbed_into_registered(self):
        with tempfile.TemporaryDirectory() as td:
            map_path = Path(td) / "hippo.json"
            legacy = {
                "created": "2026-01-01T00:00:00",
                "proton": {
                    "total_absorbed": 7,
                    "scalar_field_radius": 0.1,
                    "core_frequency": 0.0,
                },
                "experiences": [
                    {
                        "timestamp": "2026-01-01T00:00:00",
                        "coords": [0.1, 0.0, 0.0],
                        "level": 0,
                        "entropy": 0.1,
                        "phase": "FLOW",
                        "content_ref": "legacy",
                    }
                ],
            }
            map_path.write_text(json.dumps(legacy), encoding="utf-8")

            hippo = FibonacciOrbitalHippocampus(map_path)

            self.assertEqual(hippo.data["proton"]["total_registered"], 7)
            self.assertEqual(hippo.data["proton"]["total_absorbed"], 7)
            self.assertTrue(hippo.data["proton"]["absorption_repair_approximate"])
            self.assertIn("vibe", hippo.data["experiences"][0])
            self.assertEqual(hippo.data["experiences"][0]["vibe"]["phase"], "FLOW")

    def test_registration_and_absorption_are_separate_and_radius_grows_on_absorption(self):
        with tempfile.TemporaryDirectory() as td:
            hippo = FibonacciOrbitalHippocampus(Path(td) / "hippo.json")

            first = hippo.register_experience({"entropy": 0.4, "phase": "FLOW"}, "repeat")
            self.assertEqual(first["total_registered"], 1)
            self.assertEqual(first["total_absorbed"], 0)
            self.assertEqual(hippo.data["proton"]["scalar_field_radius"], BASE_RADIUS)

            for _ in range(3):
                result = hippo.register_experience({"entropy": 0.4, "phase": "FLOW"}, "repeat")

            self.assertTrue(result["converged"])
            self.assertEqual(hippo.data["proton"]["total_registered"], 4)
            self.assertEqual(hippo.data["proton"]["total_absorbed"], 1)
            self.assertGreater(hippo.data["proton"]["scalar_field_radius"], BASE_RADIUS)
            self.assertAlmostEqual(
                hippo.data["proton"]["embodiment_ratio"],
                0.25,
                places=6,
            )

    def test_vision_explorer_is_pure_perception_and_loop_registers_once(self):
        with tempfile.TemporaryDirectory() as td:
            map_path = Path(td) / "hippo.json"
            hippo = FibonacciOrbitalHippocampus(map_path)

            explorer = VisionExplorer.__new__(VisionExplorer)
            explorer.hippo = hippo
            explorer.available = True
            explorer._image_to_base64 = lambda path: "abc"
            explorer._query_vision = lambda image_b64, prompt, model=None: "bright structured image"

            image_path = Path(td) / "sample.png"
            image_path.write_bytes(b"fake")

            before = len(hippo.data["experiences"])
            result = explorer.explore_image(image_path)
            after = len(hippo.data["experiences"])

            self.assertTrue(result["explored"])
            self.assertEqual(before, after)

            loop = AutonomousExperienceLoop(hippo, vision_explorer=FakeVision())
            import autonomous_experience_loop as ael
            ael.SCAN_ROOTS = [Path(td)]

            cycle = loop.run_cycle()

            self.assertEqual(cycle["registered"], 1)
            self.assertEqual(len(hippo.data["experiences"]), 1)
            self.assertEqual(hippo.data["proton"]["total_registered"], 1)

    def test_concurrent_writers_keep_valid_json_and_monotonic_registered_count(self):
        with tempfile.TemporaryDirectory() as td:
            map_path = Path(td) / "hippo.json"
            hippo_a = FibonacciOrbitalHippocampus(map_path)
            hippo_b = FibonacciOrbitalHippocampus(map_path)

            def writer(instance, phase):
                for _ in range(10):
                    instance.register_experience({"entropy": 0.6, "phase": phase}, f"writer:{phase}")

            t1 = threading.Thread(target=writer, args=(hippo_a, "EXPANSION"))
            t2 = threading.Thread(target=writer, args=(hippo_b, "CONTRACTION"))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            data = json.loads(map_path.read_text(encoding="utf-8"))
            self.assertEqual(data["proton"]["total_registered"], 20)
            self.assertIn("experiences", data)


if __name__ == "__main__":
    unittest.main()
