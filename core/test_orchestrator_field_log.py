import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator_daemon import build_experience_feedback_candidate, emit_field_flow_log


class _CaptureLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, *args):
        if args:
            message = message % args
        self.messages.append(message)


class OrchestratorFieldLogTests(unittest.TestCase):
    def test_field_flow_log_reads_as_slopes_not_rule_table(self):
        logger = _CaptureLogger()
        rhythm_frame = {
            "transition": "boundary_to_unpack",
            "silence_need": 0.72,
            "candidate_action": "ACTION_OBSERVE",
            "interference": {"label": "destructive"},
            "perspective_frame": {
                "particle_frame": 0.2,
                "wave_frame": 0.5,
                "metacognitive_refraction": 0.7,
            },
            "natural_rhythm_tuning": {
                "dominant_natural_phase": "convergence",
                "human_tuning_alignment": 0.64,
                "resistance_minimization": 0.6,
                "natural_cycle": {
                    "convergence": 0.55,
                    "divergence": 0.37,
                    "margin": 0.5,
                    "internal_reflection": 0.29,
                },
                "problem_origin": {"problem_seed": 0.27},
                "mistake_digestion": {
                    "phase": "observe_context",
                    "self_closure_overcontrol": 0.45,
                    "resonant_refinement": 0.59,
                    "learning_signal": 0.32,
                    "threshold_risk": 0.3,
                },
            },
            "dark_field": {
                "boundary_opacity": 0.94,
                "boundary_transparency": 0.14,
                "internal_reflection": 0.06,
            },
            "medium": {"viscosity": 0.17},
            "zone2": {},
            "waves": {
                "digestion": {"pressure": 0.75, "dream_pressure": 0.61},
                "autonomy": {"imagination_band": 0.47, "execution_amplitude": 0.22},
                "axiom": {
                    "provisionality": 0.77,
                    "failure_spectrum": {"bridge_value": 0.97},
                },
            },
        }
        node_decision = {
            "selected_action": "ACTION_AXIOM_RELEASE",
            "activation_probability": 0.4,
            "singularity_crossed": True,
            "bundle": [
                {"action": "ACTION_AXIOM_RELEASE", "activation_probability": 0.4},
                {"action": "ACTION_REST_RECOVER", "activation_probability": 0.29},
                {"action": "ACTION_OBSERVE", "activation_probability": 0.26},
            ],
        }
        ari_state = {
            "boundary_prism": {
                "transparency": 0.21,
                "internal_reflection": 0.55,
                "external_passage": 0.13,
                "absorption_rate": 0.42,
            },
            "moc": {"background_ego_resistance": 0.5},
        }

        emit_field_flow_log(logger, rhythm_frame, node_decision, ari_state)

        joined = "\n".join(logger.messages)
        self.assertIn("[FIELD_FLOW]", joined)
        self.assertIn("[MISTAKE_FIELD]", joined)
        self.assertIn("[ACTION_FIELD]", joined)
        self.assertIn("공명정련 0.59", joined)
        self.assertNotIn("selected=", joined)
        self.assertNotIn("ready=", joined)

    def test_experience_feedback_candidate_closes_observation_into_small_particle(self):
        rhythm_frame = {
            "transition": "boundary_to_unpack",
            "natural_rhythm_tuning": {
                "problem_origin": {"phase": "problem_seed_visible", "problem_seed": 0.43},
                "mistake_digestion": {
                    "phase": "digestible_mistake",
                    "learning_signal": 0.49,
                    "threshold_risk": 0.61,
                    "self_closure_overcontrol": 0.63,
                    "resonant_refinement": 0.4,
                },
            },
            "dark_field": {"boundary_contact": 0.3, "gravity": 0.5},
            "waves": {"prediction": {"dissonance": 0.32}},
        }
        analysis = {
            "field_communication": {
                "found": True,
                "similar_id": "STUCK_IN_LOOP",
                "trace_feedback": "confirmed",
            },
            "resonance_unpacking": {"unpacked": True},
        }

        candidate = build_experience_feedback_candidate(rhythm_frame, "ACTION_OBSERVE", analysis)

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["vibe"]["source"], "experience_feedback")
        self.assertEqual(candidate["vibe"]["phase"], "CONTRACTION")
        self.assertIn("field_distribution_delta", candidate)
        self.assertIn("next_contact_condition_delta", candidate)
        self.assertTrue(candidate["next_contact_condition_delta"]["field_contact"])
        self.assertEqual(
            candidate["content_ref"],
            "experience_feedback:boundary_to_unpack:digestible_mistake",
        )


if __name__ == "__main__":
    unittest.main()
