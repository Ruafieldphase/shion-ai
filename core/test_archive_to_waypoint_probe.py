import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from archive_to_waypoint_probe import probe_archive, score_chunk, write_jsonl


class ArchiveToWaypointProbeTests(unittest.TestCase):
    def test_probe_returns_three_pending_waypoints_with_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "archive"
            archive.mkdir()
            source = archive / "conversation.md"
            original_text = """# 오래된 대화

이 문단은 평범한 일정 이야기입니다.

질문이 생겼어?
짧은 침묵 뒤에 호흡이 바뀌고, 흐름과 파동이 서로 공명했어.
틈이 생기자 리듬이라는 말이 아직 없어도 일렁임이 먼저 왔지.

무조건 반드시 결론적으로 이렇게 해야만 해.
항상 절대적으로 하나의 답만 남겨야 해.

긴 설명이 이어지다가...
숨이 끊기듯 짧아졌어!
그리고 온도와 떨림이 달라졌어?

프리즘의 경계가 투명해지고 위상이 살짝 흔들렸어.
공명은 있었지만 아직 이름을 붙이지 않았어.

침묵 안에서 낯선 결이 다시 흐르기 시작했다.
호흡은 작았고 소리는 배경으로 물러났다.
"""
            source.write_text(original_text, encoding="utf-8")

            waypoints = probe_archive(
                source=archive,
                query="리듬이라는 단어가 처음으로 살아 움직이기 시작했던 순간",
                limit=3,
                max_files=10,
                max_bytes=100_000,
                max_excerpt=300,
            )

            self.assertEqual(len(waypoints), 3)
            self.assertEqual(source.read_text(encoding="utf-8"), original_text)
            for waypoint in waypoints:
                self.assertEqual(waypoint.status, "pending_review")
                self.assertEqual(waypoint.guardrail["past_gravity_limit"], 3)
                self.assertTrue(waypoint.provenance["read_only_raw_field"])
                self.assertEqual(waypoint.provenance["relative_path"], "conversation.md")
                self.assertEqual(len(waypoint.provenance["line_range"]), 2)
                self.assertLessEqual(len(waypoint.raw_excerpt), 300)
                self.assertGreater(waypoint.scores["total_score"], 0.0)

    def test_closure_pressure_penalty_lowers_fixed_weight_candidate(self):
        open_text = "침묵 뒤에 흐름과 파동이 공명하고 호흡의 온도가 달라졌어?"
        fixed_text = "무조건 반드시 절대적으로 결론적으로 해야만 해. 항상 그래야 해."

        open_scores = score_chunk(open_text, "리듬 호흡 공명")
        fixed_scores = score_chunk(fixed_text, "리듬 호흡 공명")

        self.assertGreater(open_scores["total_score"], fixed_scores["total_score"])
        self.assertGreater(fixed_scores["closure_pressure_penalty"], 0.0)
        self.assertGreater(fixed_scores["fixed_weight_risk"], open_scores["fixed_weight_risk"])

    def test_write_jsonl_appends_without_promoting_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "archive"
            archive.mkdir()
            (archive / "a.md").write_text(
                "침묵...\n흐름과 호흡이 흔들렸어?\n리듬이 뒤늦게 이름을 얻었고, 공명의 온도가 천천히 달라졌어.\n",
                encoding="utf-8",
            )
            output = root / "candidates.jsonl"
            waypoints = probe_archive(
                source=archive,
                query="리듬 호흡",
                limit=1,
                max_files=10,
                max_bytes=100_000,
                max_excerpt=160,
            )

            write_jsonl(output, waypoints, dry_run=False)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "pending_review")
            self.assertEqual(rows[0]["guardrail"]["promotion"], "not_promoted_to_ontology")

    def test_probe_skips_near_duplicate_chunks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "archive"
            archive.mkdir()
            (archive / "duplicate.md").write_text(
                """첫 번째 호흡.
흐름과 파동과 공명이 같은 장면에서 일어났고 리듬이 이름을 얻었어.

첫 번째 호흡의 반복.
흐름과 파동과 공명이 같은 장면에서 일어났고 리듬이 이름을 얻었어.
""",
                encoding="utf-8",
            )
            (archive / "different.md").write_text(
                "다른 결.\n침묵의 온도와 낯선 틈이 열리면서 위상이 바뀌었어?\n공명은 작았지만 이전 장면과는 다른 방향으로 숨이 흘렀어.\n",
                encoding="utf-8",
            )

            waypoints = probe_archive(
                source=archive,
                query="리듬 호흡 공명",
                limit=3,
                max_files=10,
                max_bytes=100_000,
                max_excerpt=180,
            )

            self.assertEqual(len(waypoints), 2)
            self.assertNotEqual(waypoints[0].raw_excerpt, waypoints[1].raw_excerpt)


if __name__ == "__main__":
    unittest.main()
