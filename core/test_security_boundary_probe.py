import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from security_boundary_probe import build_security_boundary_state


class SecurityBoundaryProbeTests(unittest.TestCase):
    def test_baseline_expected_surfaces_do_not_claim_intrusion(self):
        state = build_security_boundary_state(
            file_changes=[],
            process_observations=[
                {"name": "python.exe", "pid": 1, "path": "C:/Python313/python.exe"},
                {"name": "ollama.exe", "pid": 2, "path": "C:/Users/kuirv/AppData/Local/Programs/Ollama/ollama.exe"},
            ],
            listener_observations=[
                {"local_address": "127.0.0.1", "local_port": 57321},
                {"local_address": "127.0.0.1", "local_port": 57322},
                {"local_address": "192.168.119.1", "local_port": 11434},
            ],
            trace_observations={
                "boundary_aperture": {"mode": "open_for_contact", "signals": {"connection_risk": 0.0}},
                "field_prediction": {"ok": True},
                "experience_feedback": {"ok": True},
                "contextual_gradient": {"ok": True},
            },
        )

        self.assertEqual(state["mode"], "baseline_observe")
        self.assertTrue(state["not_an_intrusion_claim"])
        self.assertEqual(state["next_contact"]["action"], "record_boundary_trace")

    def test_sensitive_mutation_or_unknown_executable_narrows_and_verifies(self):
        state = build_security_boundary_state(
            file_changes=[
                {"status": "M", "path": ".env_keys", "sha256": "abc"},
                {"status": "D", "path": "core/important.py", "sha256": ""},
            ],
            process_observations=[{"name": "unknown.exe", "pid": 99, "path": "C:/Temp/unknown.exe"}],
            listener_observations=[{"local_address": "0.0.0.0", "local_port": 4444}],
            trace_observations={"boundary_aperture": {"signals": {"connection_risk": 0.4}}},
        )

        self.assertEqual(state["mode"], "narrow_and_verify")
        self.assertGreater(state["signals"]["intrusion_pressure"], 0.45)
        self.assertFalse(state["next_contact"]["irreversible_effect"])

    def test_many_unhashed_changes_are_ambiguity_not_intrusion_claim(self):
        state = build_security_boundary_state(
            file_changes=[{"status": "??", "path": f"docs/file_{i}.md"} for i in range(10)],
            process_observations=[],
            listener_observations=[],
            trace_observations={},
        )

        self.assertIn(state["mode"], {"verify_boundary_contact", "narrow_and_verify"})
        self.assertTrue(state["not_an_intrusion_claim"])
        self.assertGreater(state["signals"]["ambiguity"], 0.0)


if __name__ == "__main__":
    unittest.main()
