import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from llm_serving_profiles import default_serving_profiles, normalize_tail, tail_fingerprints


class LLMServingProfilesTests(unittest.TestCase):
    def test_unconscious_profile_keeps_stable_prefix_fingerprint_across_tails(self):
        profile = default_serving_profiles()["unconscious_fixed_prefix"]
        first = profile.build_prompt("Cycle A: calm body.")
        second = profile.build_prompt("Cycle B: slight drift.")

        self.assertIn(profile.stable_prefix, first)
        self.assertIn(profile.stable_prefix, second)
        self.assertEqual(profile.stable_prefix_fingerprint, profile.stable_prefix_fingerprint)
        self.assertNotEqual(first, second)

    def test_openai_messages_keep_prefix_in_system_message(self):
        profile = default_serving_profiles()["conscious_varied_input"]
        messages = profile.build_openai_messages("Explain the current blocker.")

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], profile.stable_prefix)
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("Explain the current blocker.", messages[1]["content"])

    def test_tail_normalization_caps_long_variable_context(self):
        normalized = normalize_tail("x " * 2000, limit=40)

        self.assertLessEqual(len(normalized), 40)
        self.assertTrue(normalized.endswith("..."))

    def test_tail_fingerprints_are_stable_after_whitespace_normalization(self):
        self.assertEqual(tail_fingerprints(["a   b"]), tail_fingerprints(["a b"]))


if __name__ == "__main__":
    unittest.main()
