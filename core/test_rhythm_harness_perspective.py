import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rhythm_harness import NonEuclideanRhythmHarness


class RhythmHarnessPerspectiveTests(unittest.TestCase):
    def test_perspective_frame_tracks_particle_and_wave_views(self):
        with tempfile.TemporaryDirectory() as td:
            harness = NonEuclideanRhythmHarness(Path(td))

            particle = harness._perspective_frame(
                field_wave={"amplitude": 0.78},
                memory_wave={"resonance": 0.18},
                prediction_wave={"dissonance": 0.62},
                dark_field={"gravity": 0.84, "boundary_pull": 0.45},
                awareness={"present_contact": 0.22, "release_capacity": 0.34},
                zone2={"openness": 0.24},
                medium={"conductivity": 0.18, "resistance": 0.74},
            )
            wave = harness._perspective_frame(
                field_wave={"amplitude": 0.12},
                memory_wave={"resonance": 0.64},
                prediction_wave={"dissonance": 0.08},
                dark_field={"gravity": 0.18, "boundary_pull": 0.0},
                awareness={"present_contact": 0.76, "release_capacity": 0.82},
                zone2={"openness": 0.68},
                medium={"conductivity": 0.72, "resistance": 0.18},
            )

            self.assertEqual(particle["dominant_frame"], "particle_frame")
            self.assertGreater(particle["particle_frame"], particle["wave_frame"])
            self.assertGreater(wave["wave_frame"], wave["particle_frame"])
            self.assertGreater(wave["metacognitive_refraction"], particle["metacognitive_refraction"])
            self.assertEqual(wave["role_binding"], "contextual_not_fixed")
            self.assertEqual(
                wave["principle"],
                "synthesis_is_current_rhythm_field_not_fixed_role",
            )

    def test_uncertain_future_node_triggers_contingency_lock_and_dilation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "field_prediction_errors.jsonl").write_text(
                '{"error": 0.72}\n',
                encoding="utf-8",
            )
            harness = NonEuclideanRhythmHarness(root)

            frame = harness.encode(
                field_status={"salience": 0.84},
                current_vector={
                    "temporal_tension": 0.82,
                    "action_density": 0.95,
                    "orbit_distance": 2.4,
                },
                hippo_data={
                    "proton": {
                        "total_registered": 120,
                        "total_absorbed": 4,
                        "embodiment_ratio": 0.033333,
                    },
                    "experiences": [],
                },
                learning_state={"recurrence_metrics": {"reduction_rate": -12}},
                boundary_report={"in_orbit": False},
                log=False,
            )

            self.assertEqual(frame["pending_node"]["execution_lock"], "locked_until_contingency")
            self.assertIn(frame["pending_node"]["state"], {"pending_node", "probabilistic_node"})
            self.assertTrue(frame["velocity_dilation"]["awareness_checkpoint"])
            self.assertIn(frame["transition"], {"contingency_lock", "zero_point_reset"})
            if frame["transition"] == "zero_point_reset":
                self.assertEqual(frame["candidate_action"], "ACTION_AXIOM_RELEASE")
            else:
                self.assertEqual(frame["candidate_action"], "ACTION_PRE_BREACH_TUNE")
            self.assertEqual(
                frame["zone2_regulation"]["principle"],
                "zone2_is_active_margin_for_delay_or_zero_point_reset_not_forced_routine_completion",
            )


if __name__ == "__main__":
    unittest.main()
