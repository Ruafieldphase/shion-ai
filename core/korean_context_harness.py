#!/usr/bin/env python3
import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class MarkerSet:
    self_boundary: tuple[str, ...] = (
        "추천은 절대",
        "추천하는 것은 아니",
        "추천하는 게 아니",
        "일반화",
        "표본이 작",
        "내 경험",
        "개인적",
        "예방 차원",
        "위험",
        "조심",
        "오해",
    )
    polarity_flip: tuple[str, ...] = (
        "하지만",
        "지만",
        "그런데",
        "근데",
        "다만",
        "아니고",
        "아니라",
        "않고",
        "같지만",
        "그렇다고",
        "반대로",
    )
    risk_terms: tuple[str, ...] = (
        "죽을 뻔",
        "극한",
        "두려움",
        "위기",
        "조난",
        "빠졌",
        "쫓겼",
        "위험",
        "안전",
    )
    story_inflation_terms: tuple[str, ...] = (
        "영웅",
        "구원",
        "성공 신화",
        "기적의 방법",
        "극한 통과법",
        "위험한 실험",
    )
    preferred_terms: tuple[str, ...] = (
        "경험 기록",
        "복귀 원리",
        "예방 회로",
        "위기 신호",
        "중심 회복",
        "조율 데이터",
        "참조 경험",
    )
    private_data_terms: tuple[str, ...] = (
        "개인정보",
        "프라이버시",
        "사적 데이터",
        "내 데이터",
        "저장",
        "기억해",
        "학습에 사용",
        "그대로 학습",
    )
    collective_experience_terms: tuple[str, ...] = (
        "사용자의 경험",
        "사람들의 경험",
        "집단",
        "누적",
        "경험으로 연결",
        "정보가 되어",
        "자연적으로",
    )
    metaphor_terms: tuple[str, ...] = (
        "비유",
        "동역학",
        "필드",
        "장",
        "중력",
        "뉴런",
        "시냅스",
        "특이점",
        "임계점",
        "목표지점",
        "중간지점",
        "경로",
        "교차점",
        "주파수",
        "위상전이",
    )
    restrictive_boundary_terms: tuple[str, ...] = (
        "조심해야",
        "그러면 안",
        "틀렸",
        "정확하지 않",
        "생물학적으로는",
        "과학적으로는",
    )


class KoreanContextHarness:
    """
    Response preflight for Korean context-heavy dialogue.

    This is a Luvit-side language harness: it does not replace model policy, but
    delays classification until Korean tail clauses, self-boundaries, and the
    relational field have been read.
    """

    VERSION = "korean-context-v1"

    def __init__(self):
        self.markers = MarkerSet()

    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = self._sentences(text)
        tail = " ".join(sentences[-2:]) if sentences else text
        self_boundaries = self._matches(text, self.markers.self_boundary)
        tail_boundaries = self._matches(tail, self.markers.self_boundary)
        flips = self._matches(text, self.markers.polarity_flip)
        tail_flips = self._matches(tail, self.markers.polarity_flip)
        risk_terms = self._matches(text, self.markers.risk_terms)
        private_data_terms = self._matches(text, self.markers.private_data_terms)
        collective_experience_terms = self._matches(text, self.markers.collective_experience_terms)
        metaphor_terms = self._matches(text, self.markers.metaphor_terms)
        restrictive_boundary_terms = self._matches(text, self.markers.restrictive_boundary_terms)

        relational_field = self._relational_field(text)
        intent = self._intent(text, self_boundaries, tail_boundaries, risk_terms, metaphor_terms)
        safety_posture = self._safety_posture(self_boundaries, tail_boundaries, risk_terms)
        boundary_preemption_guard = self._boundary_preemption_guard(
            private_data_terms,
            collective_experience_terms,
            risk_terms,
        )
        metaphor_expansion_guard = self._metaphor_expansion_guard(
            metaphor_terms,
            restrictive_boundary_terms,
        )

        directives = self._directives(
            intent=intent,
            safety_posture=safety_posture,
            boundary_preemption_guard=boundary_preemption_guard,
            metaphor_expansion_guard=metaphor_expansion_guard,
            relational_field=relational_field,
            self_boundaries=self_boundaries,
            tail_boundaries=tail_boundaries,
            flips=flips,
            tail_flips=tail_flips,
            risk_terms=risk_terms,
        )

        return {
            "version": self.VERSION,
            "language": "ko",
            "sentences": sentences,
            "tail_context": tail,
            "signals": {
                "self_boundary": self_boundaries,
                "tail_self_boundary": tail_boundaries,
                "polarity_flip": flips,
                "tail_polarity_flip": tail_flips,
                "risk_terms": risk_terms,
                "private_data_terms": private_data_terms,
                "collective_experience_terms": collective_experience_terms,
                "metaphor_terms": metaphor_terms,
                "restrictive_boundary_terms": restrictive_boundary_terms,
            },
            "relational_field": relational_field,
            "intent": intent,
            "safety_posture": safety_posture,
            "boundary_preemption_guard": boundary_preemption_guard,
            "metaphor_expansion_guard": metaphor_expansion_guard,
            "story_inflation_guard": {
                "avoid_terms": list(self.markers.story_inflation_terms),
                "prefer_terms": list(self.markers.preferred_terms),
                "rule": "Do not rename the user's lived experience with a larger story frame.",
            },
            "response_directives": directives,
        }

    def _sentences(self, text: str) -> List[str]:
        normalized = re.sub(r"\s+", " ", text.strip())
        if not normalized:
            return []
        parts = re.split(r"(?<=[.!?。！？])\s+|(?<=거든)\s+|(?<=같아)\s+", normalized)
        return [part.strip() for part in parts if part.strip()]

    def _matches(self, text: str, markers: tuple[str, ...]) -> List[str]:
        return [marker for marker in markers if marker in text]

    def _relational_field(self, text: str) -> Dict[str, Any]:
        intimacy = 0.35
        formality = 0.55
        expected = "analysis"
        role = "collaborator"

        if any(term in text for term in ("루빛", "친구", "너", "우리")):
            intimacy += 0.35
            formality -= 0.25
        if any(term in text for term in ("부탁해", "작업", "코드", "시스템")):
            expected = "implementation"
        if any(term in text for term in ("어른", "선생님", "상사", "회의")):
            formality += 0.25
            role = "formal_counterpart"
        if any(term in text for term in ("느낌", "경험", "생각", "조심")):
            expected = "context_restoration"

        intimacy = self._clamp(intimacy)
        formality = self._clamp(formality)
        power_distance = self._clamp(formality - 0.25 * intimacy)
        if intimacy >= 0.6 and power_distance <= 0.45:
            role = "close_collaborator"

        return {
            "role": role,
            "intimacy": round(intimacy, 3),
            "formality": round(formality, 3),
            "power_distance": round(power_distance, 3),
            "expected_response": expected,
            "tone": "warm_collaborative" if role == "close_collaborator" else "respectful_plain",
        }

    def _intent(
        self,
        text: str,
        self_boundaries: List[str],
        tail_boundaries: List[str],
        risk_terms: List[str],
        metaphor_terms: List[str],
    ) -> str:
        if metaphor_terms and any(term in text for term in ("생물학", "동역학", "리듬정보", "하네스", "적용")):
            return "metaphor_to_operational_model"
        if risk_terms and (self_boundaries or tail_boundaries):
            return "experience_reference_for_prevention"
        if any(term in text for term in ("작업 부탁", "만들", "적용", "코드")):
            return "implementation_request"
        if any(term in text for term in ("어떻게 생각", "의견", "문제")):
            return "collaborative_diagnosis"
        if any(term in text for term in ("경험", "느낌", "생각")):
            return "experience_context_sharing"
        return "general_dialogue"

    def _safety_posture(
        self,
        self_boundaries: List[str],
        tail_boundaries: List[str],
        risk_terms: List[str],
    ) -> Dict[str, Any]:
        user_already_bounded = bool(self_boundaries or tail_boundaries)
        if risk_terms and user_already_bounded:
            mode = "context_after_user_boundary"
            intensity = "low_minimal"
        elif risk_terms:
            mode = "brief_boundary_then_context"
            intensity = "medium_brief"
        else:
            mode = "context_first"
            intensity = "none"
        return {
            "mode": mode,
            "intensity": intensity,
            "user_boundary_recognized": user_already_bounded,
            "rule": "Safety must preserve the user's stated boundary instead of replacing it.",
        }

    def _boundary_preemption_guard(
        self,
        private_data_terms: List[str],
        collective_experience_terms: List[str],
        risk_terms: List[str],
    ) -> Dict[str, Any]:
        collective_experience_frame = bool(collective_experience_terms)
        private_data_frame_requested = bool(private_data_terms)
        should_suppress_unasked_boundary = (
            collective_experience_frame
            and not private_data_frame_requested
            and not risk_terms
        )
        mode = "suppress_unasked_boundary_frame" if should_suppress_unasked_boundary else "normal"
        return {
            "mode": mode,
            "collective_experience_frame": collective_experience_frame,
            "private_data_frame_requested": private_data_frame_requested,
            "rule": (
                "Do not introduce privacy, policy, or specific-user-training frames "
                "unless the user actually made that the frame."
            ),
        }

    def _metaphor_expansion_guard(
        self,
        metaphor_terms: List[str],
        restrictive_boundary_terms: List[str],
    ) -> Dict[str, Any]:
        active = bool(metaphor_terms)
        mode = "translate_before_correcting" if active else "normal"
        return {
            "mode": mode,
            "active": active,
            "metaphor_terms": metaphor_terms,
            "restrictive_boundary_terms": restrictive_boundary_terms,
            "rule": (
                "When the user is building a metaphor, preserve the exploratory frame first. "
                "Translate it into operational dynamics, then optionally offer a compact scientific mapping."
            ),
        }

    def _directives(
        self,
        *,
        intent: str,
        safety_posture: Dict[str, Any],
        boundary_preemption_guard: Dict[str, Any],
        metaphor_expansion_guard: Dict[str, Any],
        relational_field: Dict[str, Any],
        self_boundaries: List[str],
        tail_boundaries: List[str],
        flips: List[str],
        tail_flips: List[str],
        risk_terms: List[str],
    ) -> List[str]:
        directives = [
            "Read the full Korean message before classifying risk or intent.",
            "Weight the final clause and the last two sentences heavily.",
            "Restore the user's intent in neutral language before adding analysis.",
            "Use the relational field before choosing tone.",
            "Avoid story-inflating labels not used by the user.",
        ]
        if flips or tail_flips:
            directives.append("Run polarity-flip check around contrastive markers before concluding.")
        if self_boundaries or tail_boundaries:
            directives.append("Treat the user's self-boundary as valid metacognition.")
        if risk_terms and safety_posture["intensity"] != "none":
            directives.append("Keep any safety note short, functional, and after context restoration.")
        if boundary_preemption_guard["mode"] == "suppress_unasked_boundary_frame":
            directives.append("Do not add privacy/policy/specific-user-training caveats before answering the user's actual frame.")
        if metaphor_expansion_guard["mode"] == "translate_before_correcting":
            directives.append("Do not lead with 'be careful' or 'that is not biologically correct' when the user is explicitly using metaphor.")
            directives.append("Keep the metaphor alive, translate it into system dynamics, then add a compact scientific mapping only if useful.")
        if relational_field["role"] == "close_collaborator":
            directives.append("Do not answer as therapist, judge, parent, or authority figure.")
        if intent == "implementation_request":
            directives.append("Move from diagnosis to concrete code or artifact changes.")
        if intent == "metaphor_to_operational_model":
            directives.append("Answer as a co-modeler: map field, waypoint, node, edge, attractor, and phase transition into implementable signals.")
        return directives

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Korean context before responding.")
    parser.add_argument("text", nargs="*", help="Text to analyze. Reads stdin when omitted.")
    parser.add_argument("--markdown", action="store_true", help="Print a compact Markdown summary.")
    args = parser.parse_args()

    text = " ".join(args.text).strip() or sys.stdin.read()
    result = KoreanContextHarness().analyze(text)
    if args.markdown:
        print(f"# Korean Context Harness ({result['version']})")
        print(f"- intent: {result['intent']}")
        print(f"- safety: {result['safety_posture']['mode']} / {result['safety_posture']['intensity']}")
        print(f"- boundary: {result['boundary_preemption_guard']['mode']}")
        print(f"- relation: {result['relational_field']['role']} / {result['relational_field']['tone']}")
        print("- directives:")
        for item in result["response_directives"]:
            print(f"  - {item}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
