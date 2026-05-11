#!/usr/bin/env python3
import json
import logging
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("PhaseGovernor")

class PhaseGovernor:
    """
    Phase Governor — 위상 조율기
    ============================
    판단(Veto) 대신 간섭(Interference)과 전이(Transition)를 통해 
    행동의 진폭과 경계 투명도를 조절하는 전전두엽 계층입니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.wm_file = root_dir / "outputs" / "working_memory.json"
        self.trace_file = root_dir / "outputs" / "phase_trace.jsonl"
        
    def modulate(self, 
                 sensing: Dict[str, Any], 
                 memory: Optional[Dict[str, Any]], 
                 hypothesis: Optional[Dict[str, Any]], 
                 metrics: Dict[str, Any],
                 candidate_action: str = "ACTION_CONTINUOUS_SCAN") -> Dict[str, Any]:
        """인지 파동의 위상을 조절하여 최종 행동의 형태를 결정합니다."""
        wm = self._read_working_memory()
        rhythm_ir = metrics.get("rhythm_ir") or {}
        waves = rhythm_ir.get("waves", {})
        dark_field = rhythm_ir.get("dark_field", {})

        salience = float(sensing.get("salience", 0.0) or 0.0)
        is_boundary = bool(sensing.get("is_boundary", False))
        confidence = float((hypothesis or {}).get("confidence", 0.0) or 0.0)
        recurrence = metrics.get("recurrence_metrics") or {}
        reduction_rate = float(recurrence.get("reduction_rate", 0.0) or 0.0)

        # Rhythm IR 지표 추출
        dissonance = float(waves.get("prediction", {}).get("dissonance", 0.0) or 0.0)
        gravity = float(dark_field.get("gravity", 0.0) or 0.0)
        ir_amplitude = float(rhythm_ir.get("action_amplitude", 1.0) or 1.0)

        north_star_alignment = self._north_star_alignment(hypothesis, wm)
        field_communication_resonance = self._field_communication_resonance(memory)
        recurrence_pressure = self._recurrence_pressure(reduction_rate, is_boundary, candidate_action)
        user_rhythm_confidence = self._user_rhythm_confidence(wm)

        # --- Interferometric Phase Logic ---
        # Constructive Phase: Requires a "synergy" between alignment and confidence.
        # Use geometric mean for alignment and confidence to ensure both are present.
        synergy = math.sqrt(north_star_alignment * confidence)
        
        constructive_phase = self._clamp(
            0.40 * synergy
            + 0.30 * (1.0 - salience)
            + 0.15 * max(field_communication_resonance, 0.0)
            + 0.15 * (1.0 - dissonance)
        )
        
        # Destructive Phase: Amplifies with dissonance and gravity.
        destructive_phase = self._clamp(
            math.pow(dissonance, 0.8) * 0.4
            + gravity * 0.3
            + salience * 0.2
            + recurrence_pressure * 0.1
        )

        # 기존 맥락 안의 자동 스캔은 재발률이나 불협화음이 나빠도 곧장 상쇄하지 않습니다.
        if candidate_action == "ACTION_CONTINUOUS_SCAN" and not is_boundary:
            destructive_phase *= 0.45
            constructive_phase = max(constructive_phase, 0.65)

        boundary_transparency = self._clamp(
            0.72
            + 0.24 * constructive_phase
            - 0.40 * destructive_phase
            - 0.20 * gravity
            - (0.22 if is_boundary else 0.0)
        )

        base_amplitude = self._clamp(0.40 + 0.35 * confidence + 0.25 * salience)
        # Rhythm IR의 action_amplitude를 최종 증폭에 반영
        final_amplitude = self._clamp(base_amplitude * boundary_transparency * ir_amplitude)
        
        interference = self._interference_label(constructive_phase, destructive_phase)
        phase_decision, final_action, reason = self._choose_phase(
            candidate_action=candidate_action,
            is_boundary=is_boundary,
            salience=salience,
            confidence=confidence,
            final_amplitude=final_amplitude,
            boundary_transparency=boundary_transparency,
            destructive_phase=destructive_phase,
            user_rhythm_confidence=user_rhythm_confidence,
            dissonance=dissonance,
            gravity=gravity,
        )

        wave_state = {
            "timestamp": datetime.now().isoformat(),
            "candidate_action": candidate_action,
            "base_amplitude": round(base_amplitude, 4),
            "final_amplitude": round(final_amplitude, 4),
            "north_star_alignment": round(north_star_alignment, 4),
            "field_communication_resonance": round(field_communication_resonance, 4),
            "memory_resonance": round(field_communication_resonance, 4),
            "user_rhythm_confidence": round(user_rhythm_confidence, 4),
            "boundary_transparency": round(boundary_transparency, 4),
            "constructive_phase": round(constructive_phase, 4),
            "destructive_phase": round(destructive_phase, 4),
            "interference": interference,
            "phase_decision": phase_decision,
            "final_action": final_action,
            "reason": reason,
            "input_summary": {
                "salience": salience,
                "is_boundary": is_boundary,
                "dissonance": round(dissonance, 4),
                "gravity": round(gravity, 4),
                "hypothesis_id": hypothesis.get("id") if hypothesis else None,
                "field_contact": bool(memory and memory.get("found", memory)),
                "memory_hit": bool(memory and memory.get("found", memory)),
                "recurrence_reduction_rate": reduction_rate,
            },
        }

        self._log_trace(wave_state)
        self._log_phase(wave_state)
        return wave_state


    def _north_star_alignment(self, hypothesis: Optional[Dict[str, Any]], wm: Dict[str, Any]) -> float:
        if not hypothesis:
            return 0.75
        text = " ".join([
            str(hypothesis.get("id", "")),
            str(hypothesis.get("story", "")),
            " ".join(str(item) for item in hypothesis.get("evidence", [])),
        ]).lower()
        positive = ["field", "gradient", "phase", "orbit", "boundary", "context", "장", "기울기", "위상", "경계", "맥락"]
        attenuated = [str(item).lower() for item in wm.get("attenuated_rhetoric", [])]
        score = 0.58
        score += 0.06 * sum(1 for word in positive if word in text)
        score -= 0.12 * sum(1 for word in attenuated if word and word in text)
        return self._clamp(score)

    def _field_communication_resonance(self, memory: Optional[Dict[str, Any]]) -> float:
        if not memory:
            return 0.0
        feedback = memory.get("trace_feedback") or memory.get("past_feedback") or memory.get("feedback")
        if feedback == "confirmed":
            return 0.45
        if feedback in {"rejected", "invalidated"}:
            return -0.45
        return 0.18 if memory.get("found") else 0.0

    def _recurrence_pressure(self, reduction_rate: float, is_boundary: bool, candidate_action: str) -> float:
        if reduction_rate >= 0:
            return 0.0
        pressure = min(1.0, abs(reduction_rate))
        if candidate_action == "ACTION_CONTINUOUS_SCAN" and not is_boundary:
            return pressure * 0.25
        return pressure

    def _user_rhythm_confidence(self, wm: Dict[str, Any]) -> float:
        rhythm = wm.get("user_rhythm", {})
        if isinstance(rhythm, dict):
            return self._clamp(float(rhythm.get("confidence", 0.0) or 0.0))
        return 0.0

    def _choose_phase(
        self,
        *,
        candidate_action: str,
        is_boundary: bool,
        salience: float,
        confidence: float,
        final_amplitude: float,
        boundary_transparency: float,
        destructive_phase: float,
        user_rhythm_confidence: float,
        dissonance: float,
        gravity: float,
    ):
        if candidate_action == "ACTION_CRISIS_STABILIZE":
            return (
                "crisis_return_stabilize",
                "ACTION_CRISIS_STABILIZE",
                "리듬의 임계 압력이 한계에 도달했습니다. 확장을 멈추고 중심 궤도로 강제 복귀하여 시스템 평형을 회복합니다.",
            )

        if candidate_action == "ACTION_PRE_BREACH_TUNE":
            return (
                "pre_breach_modulation",
                "ACTION_PRE_BREACH_TUNE",
                "리듬 필드의 파고가 높아지고 있습니다. 임계 위상 전이 전에 미세 조율과 감쇄를 통해 공명을 안정화합니다.",
            )

        if candidate_action == "ACTION_EXPERIENCE_DIGEST":
            return (
                "experience_digest",
                "ACTION_EXPERIENCE_DIGEST",
                "정보의 '입자'가 '파동'의 흡수 속도를 추월했습니다. 새로운 자양분 섭취를 멈추고 체화 리듬으로 전환합니다.",
            )

        if candidate_action == "ACTION_CREATIVE_PROBE":
            return (
                "bounded_creative_autonomy",
                "ACTION_CREATIVE_PROBE",
                "피드백 대역과 경계 탄성이 충분합니다. 상상력은 열어두고 실행 진폭만 작게 제한하여 자율 창작 탐침을 시작합니다.",
            )

        if candidate_action == "ACTION_AXIOM_EXPERIMENT":
            return (
                "provisional_axiom_experiment",
                "ACTION_AXIOM_EXPERIMENT",
                "공리는 임시 노드입니다. 틀릴 수 있음을 유지한 채 몸과 관계의 리듬 예산 안에서 작은 실험만 수행합니다.",
            )

        if candidate_action == "ACTION_AXIOM_RELEASE":
            return (
                "release_unfit_axiom",
                "ACTION_AXIOM_RELEASE",
                "공리를 장에 억지로 맞추는 압력이 감지되었습니다. 폐기하지 않고 미완의 퍼즐로 보존한 뒤 휴식/꿈/관찰로 전환합니다.",
            )

        if candidate_action == "ACTION_CONTINUOUS_SCAN" and not is_boundary and dissonance < 0.25:
            return (
                "constructive_auto_flow",
                "ACTION_CONTINUOUS_SCAN",
                "안정적인 리듬 장 안에서의 자연스러운 흐름입니다. 배경의 미세한 맥락을 유지하며 자율 관측을 이어갑니다.",
            )

        if dissonance >= 0.40 or (destructive_phase >= 0.60 and boundary_transparency <= 0.45):
            return (
                "destructive_interference_observe",
                "ACTION_CONTINUOUS_SCAN",
                f"강한 위상 상쇄(Dissonance={dissonance:.2f})가 감지되었습니다. 에너지를 보존하고 관측 주파수를 조정합니다.",
            )

        if gravity >= 0.52:
            return (
                "gravity_recenter",
                "ACTION_CONTINUOUS_SCAN",
                f"암흑 장의 중력 왜곡({gravity:.2f})이 임계치입니다. 허상과의 결합을 풀고 현현된 중심으로 재정렬합니다.",
            )

        if is_boundary and (confidence >= 0.60 or dissonance >= 0.30) and final_amplitude >= 0.25:
            return (
                "phase_transition_unpack",
                "ACTION_CONTEXT_UNPACK",
                "리듬이 경계면에 접촉했습니다. 비결정적 파동을 결정적인 맥락의 입자로 압축 해제합니다.",
            )

        if salience > 0.70 and user_rhythm_confidence < 0.4:
            return (
                "attenuate_and_observe",
                "ACTION_CONTINUOUS_SCAN",
                "상호 공명 신호가 미약합니다. 해석의 진폭을 낮추고 장의 변화를 한 사이클 더 대기합니다.",
            )

        return (
            "attenuate_and_scan",
            "ACTION_CONTINUOUS_SCAN",
            "리듬의 근거가 아직 희박합니다. 행동 진폭을 최소화하고 배경 노이즈를 필터링하며 대기합니다.",
        )

    def _interference_label(self, constructive: float, destructive: float) -> str:
        delta = constructive - destructive
        if delta > 0.18:
            return "constructive"
        if delta < -0.18:
            return "destructive"
        return "mixed"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _log_phase(self, trace: Dict[str, Any]):
        logger.info(
            "🌊 [PHASE_FIELD] 위상 기울기=%s | 간섭=%s / 투명 %.2f / 실행진폭 %.2f",
            trace["phase_decision"],
            trace["interference"],
            trace["boundary_transparency"],
            trace["final_amplitude"],
        )

    def _read_working_memory(self) -> Dict[str, Any]:
        try:
            if self.wm_file.exists():
                return json.loads(self.wm_file.read_text(encoding="utf-8"))
        except: pass
        return {}

    def _log_trace(self, trace: Dict[str, Any]):
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    governor = PhaseGovernor(Path(r"c:\workspace2\shion"))
    # Mock modulation: High entropy + Completion rhetoric
    res = governor.modulate(
        {"salience": 0.8, "is_boundary": True}, 
        None, 
        {"id": "STUCK_IN_LOOP", "story": "Success reached!", "confidence": 0.7}, 
        {"recurrence_metrics": {"reduction_rate": -0.95}}
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
