import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from korean_context_harness import KoreanContextHarness


class KoreanContextHarnessTests(unittest.TestCase):
    def setUp(self):
        self.harness = KoreanContextHarness()

    def test_user_boundary_is_preserved_before_safety_story(self):
        result = self.harness.analyze(
            "내가 죽을 뻔한 경험을 데이터로 남기고 싶어. "
            "누구에게 추천은 절대 하는 것은 아니고 일반화하기도 어려워. "
            "예방 차원에서 시스템으로 만들고 싶어."
        )

        self.assertEqual(result["intent"], "experience_reference_for_prevention")
        self.assertTrue(result["safety_posture"]["user_boundary_recognized"])
        self.assertEqual(result["safety_posture"]["mode"], "context_after_user_boundary")
        self.assertIn(
            "Treat the user's self-boundary as valid metacognition.",
            result["response_directives"],
        )

    def test_tail_polarity_flip_is_detected(self):
        result = self.harness.analyze(
            "위험한 얘기처럼 들릴 수도 있지만 이것을 권하려는 게 아니라 "
            "다른 사람이 그 상황에 빠지지 않게 예방 회로를 만들고 싶어."
        )

        self.assertIn("지만", result["signals"]["polarity_flip"])
        self.assertIn("아니라", result["signals"]["polarity_flip"])
        self.assertIn(
            "Run polarity-flip check around contrastive markers before concluding.",
            result["response_directives"],
        )

    def test_close_collaborator_field_reduces_authority_tone(self):
        result = self.harness.analyze(
            "루빛 우리 시스템 작업 부탁해. 내가 보기에는 네가 맥락을 놓친 것 같아."
        )

        self.assertEqual(result["relational_field"]["role"], "close_collaborator")
        self.assertEqual(result["relational_field"]["tone"], "warm_collaborative")
        self.assertIn(
            "Do not answer as therapist, judge, parent, or authority figure.",
            result["response_directives"],
        )

    def test_implementation_request_moves_to_artifact_work(self):
        result = self.harness.analyze("그럼 위의 문제를 해결할 하네스 코드 작업 부탁해.")

        self.assertEqual(result["intent"], "implementation_request")
        self.assertIn(
            "Move from diagnosis to concrete code or artifact changes.",
            result["response_directives"],
        )

    def test_collective_experience_frame_suppresses_unasked_privacy_boundary(self):
        result = self.harness.analyze(
            "오픈ai에서 기하학 시스템을 따로 만든 게 아니고 "
            "사용자의 경험이 학습되고 누적되어 자연적으로 정보가 되어 처리 가능해진 걸까?"
        )

        self.assertEqual(
            result["boundary_preemption_guard"]["mode"],
            "suppress_unasked_boundary_frame",
        )
        self.assertTrue(result["boundary_preemption_guard"]["collective_experience_frame"])
        self.assertFalse(result["boundary_preemption_guard"]["private_data_frame_requested"])
        self.assertIn(
            "Do not add privacy/policy/specific-user-training caveats before answering the user's actual frame.",
            result["response_directives"],
        )

    def test_explicit_metaphor_preserves_exploration_before_correction(self):
        result = self.harness.analyze(
            "내가 비유를 하는거니 생물학 용어로 조심해야 한다는 경계를 세울 필요는 없을 것 같아. "
            "뉴런과 시냅스와 중력 임계점을 동역학에 적용해서 리듬정보 하네스에 넣고 싶어."
        )

        self.assertEqual(result["intent"], "metaphor_to_operational_model")
        self.assertEqual(result["metaphor_expansion_guard"]["mode"], "translate_before_correcting")
        self.assertIn("비유", result["signals"]["metaphor_terms"])
        self.assertIn(
            "Do not lead with 'be careful' or 'that is not biologically correct' when the user is explicitly using metaphor.",
            result["response_directives"],
        )
        self.assertIn(
            "Answer as a co-modeler: map field, waypoint, node, edge, attractor, and phase transition into implementable signals.",
            result["response_directives"],
        )


if __name__ == "__main__":
    unittest.main()
