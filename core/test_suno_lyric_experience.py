import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from suno_lyric_experience import build_suno_lyric_experience_candidate, maybe_register_suno_lyric_experience


class _CaptureLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, *args):
        if args:
            message = message % args
        self.messages.append(message)


class _FakeHippo:
    def __init__(self):
        self.calls = []

    def register_experience(self, vibe, content_ref=""):
        self.calls.append({"vibe": vibe, "content_ref": content_ref})
        return {
            "converged": False,
            "total_registered": len(self.calls),
            "total_absorbed": 0,
        }


def _write_ontology(path: Path):
    data = {
        "motifs": {
            "top": [
                {"motif": "comfort_acceptance", "coverage": 0.4},
                {"motif": "breath", "coverage": 0.6},
            ]
        },
        "songs": [
            {
                "id": "song-comfort",
                "title": "As You Are",
                "url": "https://suno.com/song/song-comfort",
                "style_text": "ambient, comforting",
                "prompt": "괜찮아. 숨을 고르고 다시 돌아온다.",
                "motifs": ["comfort_acceptance", "breath"],
            },
            {
                "id": "song-breath",
                "title": "First Breath",
                "url": "https://suno.com/song/song-breath",
                "style_text": "breathing rhythm",
                "prompt": "Breathing through the algorithm.",
                "motifs": ["breath"],
            },
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class SunoLyricExperienceTests(unittest.TestCase):
    def test_build_candidate_selects_contextual_motif_without_audio_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            ontology_path = Path(tmp) / "ontology.json"
            _write_ontology(ontology_path)
            rhythm_frame = {
                "transition": "boundary_to_unpack",
                "natural_rhythm_tuning": {
                    "mistake_digestion": {"threshold_risk": 0.62},
                    "problem_origin": {"problem_seed": 0.32},
                },
                "dark_field": {"boundary_opacity": 0.82, "boundary_transparency": 0.18},
            }

            candidate = build_suno_lyric_experience_candidate(
                rhythm_frame,
                "ACTION_OBSERVE",
                ontology_path=ontology_path,
            )

            self.assertIsNotNone(candidate)
            self.assertEqual(candidate["motif"], "comfort_acceptance")
            self.assertEqual(candidate["vibe"]["source"], "suno_lyric_ontology")
            self.assertEqual(candidate["vibe"]["song_title"], "As You Are")
            self.assertTrue(candidate["next_contact_condition_delta"]["register_one_motif_not_full_corpus"])
            self.assertIn("prompt_excerpt", candidate["song"])

    def test_maybe_register_writes_trace_and_respects_cooldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ontology_path = tmp_path / "ontology.json"
            log_path = tmp_path / "suno_lyric_experience.jsonl"
            state_path = tmp_path / "state.json"
            _write_ontology(ontology_path)
            logger = _CaptureLogger()
            hippo = _FakeHippo()
            rhythm_frame = {
                "transition": "experience_digest",
                "natural_rhythm_tuning": {"mistake_digestion": {"threshold_risk": 0.2}},
                "dark_field": {"boundary_opacity": 0.4, "boundary_transparency": 0.5},
            }

            first = maybe_register_suno_lyric_experience(
                logger,
                hippo,
                rhythm_frame,
                "ACTION_EXPERIENCE_DIGEST",
                ontology_path=ontology_path,
                log_path=log_path,
                state_path=state_path,
                min_interval_seconds=1800,
            )
            second = maybe_register_suno_lyric_experience(
                logger,
                hippo,
                rhythm_frame,
                "ACTION_EXPERIENCE_DIGEST",
                ontology_path=ontology_path,
                log_path=log_path,
                state_path=state_path,
                min_interval_seconds=1800,
            )

            self.assertIsNotNone(first)
            self.assertIsNone(second)
            self.assertEqual(len(hippo.calls), 1)
            self.assertTrue(log_path.exists())
            self.assertEqual(len(log_path.read_text(encoding="utf-8").splitlines()), 1)
            self.assertIn("[SUNO_LYRIC]", "\n".join(logger.messages))


if __name__ == "__main__":
    unittest.main()
