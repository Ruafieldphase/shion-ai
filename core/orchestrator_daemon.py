#!/usr/bin/env python3
r"""
🎯 자율 오케스트레이터 데몬 — 적응형 리듬
==========================================
고정 간격이 아니라 해마 상태와 반사 게이트가 리듬을 결정합니다.

  수렴 활발 (재미있음)  → 1분 후 다시  🔥
  대역폭 넓음 (탐색 중) → 3분 후 다시  🔭
  일반 순환              → 5분 후 다시  🌀
  고요한 상태            → 30분 후 다시 🌊
  소화 못 함 (집착 방지) → 1시간 후     💤

비용: 0원 (전부 로컬).

실행 방법:
  python c:\workspace2\shion\core\orchestrator_daemon.py

백그라운드 실행:
  python c:\workspace2\shion\core\orchestrator_daemon.py

중단:
  outputs\orchestrator_daemon.stop 파일 생성

자가 갱신:
  core\ 폴더 내 파일 변경 시 자동 종료 후 재시작 (bat 파일과 연동)
"""

import sys
import json
import time
import logging
import traceback
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus
from autonomous_experience_loop import AutonomousExperienceLoop
from vision_explorer import VisionExplorer
from autonomous_orchestrator import AutonomousOrchestrator
from resonance_runtime import ResonanceRuntime
from nocturnal_consolidation import NocturnalConsolidationEngine
from dream_engine import DreamEngine
from resonance_graph_builder import ResonanceGraphBuilder
from prediction_engine import PredictionEngine
from action_metrics import ActionMetrics
from field_delta_detector import FieldDeltaDetector
from orbit_checker import OrbitChecker
from context_unpacker import ContextUnpacker
from story_validator import StoryValidator
from field_sampler import FieldSampler
from experience_gradient_logger import ExperienceGradientLogger
from phase_governor import PhaseGovernor
from rhythm_harness import NonEuclideanRhythmHarness
from rhythm_node_menu import RhythmNodeMenu
from ari_prism import ARIPrism
from unfinished_waypoint_graph import UnfinishedWaypointGraph
from organic_learning_lifecycle import OrganicLearningLifecycle
from sleep_cycle_integrator import SleepCycleIntegrator

# 적응형 리듬 설정 — 고정 간격이 아니라 해마 상태에 반응
CYCLES_PER_RUN = 1          # 한 인지 사이클에는 한 번만 감각-판단-행동합니다.
INTERVAL_BETWEEN = 0        # 내부 고정 인터벌은 쓰지 않고 바깥 인지 리듬이 결정합니다.
MIN_SLEEP = 60              # 최소 대기 (1분) — 흥미로울 때
MAX_SLEEP = 3600            # 최대 대기 (1시간) — 쉴 때
MAX_ERRORS = 5
HEARTBEAT_TICK_INTERVAL = 15  # 심장은 계속 뛰고 있음을 짧게 표시합니다.
WAIT_STATUS_INTERVAL = 60     # 긴 소화 리듬 중에도 보이는 창에 인지 대기 상태를 남깁니다.
REFLEX_CHECK_INTERVAL = 5      # 쉬는 동안에도 짧게 장 변화를 감지합니다.
REFLEX_WAKE_SALIENCE = 0.58    # 이 값 이상이면 예정 시간을 기다리지 않고 깨어납니다.
REFLEX_CRITICAL_SALIENCE = 0.80
SIDEBAND_LOG_PATH = Path(r"c:\workspace2\shion\outputs\resonance_sidebands.jsonl")
EXPERIENCE_FEEDBACK_LOG_PATH = Path(r"c:\workspace2\shion\outputs\experience_feedback.jsonl")
EXPERIENCE_FEEDBACK_STATE_PATH = Path(r"c:\workspace2\shion\outputs\experience_feedback_state.json")
REFLEX_ACTIONS = {
    "ACTION_CRISIS_STABILIZE",
    "ACTION_PRE_BREACH_TUNE",
    "ACTION_CONTEXT_UNPACK",
    "ACTION_ANCHOR_CHECK",
}

HIPPO_PATH = Path(r"c:\workspace2\shion\outputs\fibonacci_orbital_hippocampus.json")
LOG_PATH = Path(r"c:\workspace2\shion\outputs\daemon.log")
STOP_FILE = Path(r"c:\workspace2\shion\outputs\orchestrator_daemon.stop")
REFLEX_SIGNAL_FILE = Path(r"c:\workspace2\shion\outputs\orchestrator_reflex.signal")
ANCHOR_DIR_CANDIDATES = [
    Path(r"D:\ARCHIVE_WORKSPACE\agi\outputs\sena"),
    Path(r"C:\workspace\agi\outputs\sena"),
    HIPPO_PATH.parent / "sena",
]
ACTION_RHYTHM_MAP = {
    "ACTION_PRE_BREACH_TUNE": {"sleep": 90, "mood": "🧲 조율", "reason": "경계 압력 상승 감지. 임계점 전에 감속과 직교 관찰로 장을 조율합니다."},
    "ACTION_CRISIS_STABILIZE": {"sleep": 60, "mood": "🛟 복귀", "reason": "경계 수축 임계권 감지. 탐색을 멈추고 중심 복귀를 우선합니다."},
    "ACTION_ANCHOR_CHECK": {"sleep": 60, "mood": "⚠️ 정체성", "reason": "정체성 혼동 감지! Anchor 재확인 필요."},
    "ACTION_REST_RECOVER": {"sleep": 3600, "mood": "🌊 냉각", "reason": "엔트로피 임계값 초과. 시스템 휴식 및 복구 필요."},
    "ACTION_REBUILD_GRAPH": {"sleep": 180, "mood": "🛠️ 재구축", "reason": "그래프 노후화 감지. 지형 재정렬 중."},
    "ACTION_CREATIVE_PROBE": {"sleep": 180, "mood": "🧬 자율탐침", "reason": "피드백 대역이 열렸습니다. 작은 실행 진폭으로 자율 창작 탐침을 수행합니다."},
    "ACTION_AXIOM_EXPERIMENT": {"sleep": 240, "mood": "🧪 공리실험", "reason": "공리를 임시 노드로 세우고 몸/관계 리듬 예산 안에서 작은 실험을 수행합니다."},
    "ACTION_AXIOM_RELEASE": {"sleep": 1200, "mood": "🌫️ 공리보존", "reason": "공리를 억지로 맞추는 압력이 높습니다. 폐기하지 않고 미완의 퍼즐로 보존합니다."},
    "ACTION_DREAM_AMPLIFY": {"sleep": 300, "mood": "🌙 꿈", "reason": "안정기 진입. 야간 심화(Dream Mode) 제안."},
    "ACTION_CONTEXT_UNPACK": {"sleep": 60, "mood": "🧠 성찰", "reason": "경계 접촉 감지. 무의식 실행을 멈추고 맥락을 압축 해제합니다."},
    "ACTION_EXPERIENCE_DIGEST": {"sleep": 900, "mood": "💤 소화", "reason": "경험 입력이 흡수보다 앞서 있습니다. 새 스캔보다 수렴/결정화를 우선합니다."},
    "ACTION_OBSERVE": {"sleep": 240, "mood": "〰️ 관찰", "reason": "행동 진폭을 낮추고 장의 곡률만 관찰합니다."},
    "ACTION_CONTINUOUS_SCAN": {"sleep": 300, "mood": "🌀 순환", "reason": "시스템 안정. 자율 탐색 사이클 지속."},
}

def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        force=True,
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )

def should_stop():
    """중단 파일이 있으면 멈춤."""
    if STOP_FILE.exists():
        STOP_FILE.unlink(missing_ok=True)
        return True
    return False

def append_jsonl(path: Path, entry: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_reflex_watch_paths() -> list[Path]:
    """Files that can change outside the current cognitive cycle and wake the field."""
    return [
        REFLEX_SIGNAL_FILE,
        HIPPO_PATH.parent / "field_events.jsonl",
        HIPPO_PATH.parent / "autonomous_experiences.jsonl",
        HIPPO_PATH.parent / "experience_loop_state.json",
        HIPPO_PATH.parent / "user_experience_index.jsonl",
        Path(r"C:\workspace\agi\memory\resonance_ledger.jsonl"),
        Path(r"D:\ARCHIVE_WORKSPACE\agi\outputs\sena\sena_conversations_flat.jsonl"),
    ]

def snapshot_reflex_watch(paths: list[Path]) -> dict[str, float | None]:
    snapshot = {}
    for path in paths:
        try:
            snapshot[str(path)] = path.stat().st_mtime if path.exists() else None
        except OSError:
            snapshot[str(path)] = None
    return snapshot

def changed_reflex_watch(paths: list[Path], baseline: dict[str, float | None]) -> list[Path]:
    changed = []
    for path in paths:
        key = str(path)
        try:
            current = path.stat().st_mtime if path.exists() else None
        except OSError:
            current = None
        if current != baseline.get(key):
            changed.append(path)
    return changed

def evaluate_reflex_gate(
    *,
    field_sensor: FieldDeltaDetector,
    watch_paths: list[Path],
    watch_baseline: dict[str, float | None],
    last_action: str,
    elapsed: int,
    remaining: int,
) -> dict:
    """
    Cheap interrupt gate for the sleeping phase.

    The heart still owns one process. This only decides whether the current
    wait should end early because the field crossed a threshold.
    """
    if REFLEX_SIGNAL_FILE.exists():
        try:
            reason_text = REFLEX_SIGNAL_FILE.read_text(encoding="utf-8").strip().lstrip("\ufeff")
        except OSError:
            reason_text = ""
        REFLEX_SIGNAL_FILE.unlink(missing_ok=True)
        return {
            "wake": True,
            "reason": reason_text or "manual_reflex_signal",
            "kind": "manual",
            "salience": 1.0,
            "changed": [str(REFLEX_SIGNAL_FILE)],
        }

    changed = changed_reflex_watch(watch_paths, watch_baseline)
    field_status = field_sensor.scan_for_shifts()
    salience = float(field_status.get("salience", 0.0) or 0.0)
    critical = salience >= REFLEX_CRITICAL_SALIENCE or bool(field_status.get("needs_context_unpacking", False))
    changed_after_settle = bool(changed) and elapsed >= REFLEX_CHECK_INTERVAL
    salience_wake = salience >= REFLEX_WAKE_SALIENCE and elapsed >= REFLEX_CHECK_INTERVAL
    resting_action = last_action in {
        "ACTION_REST_RECOVER",
        "ACTION_EXPERIENCE_DIGEST",
        "ACTION_DREAM_AMPLIFY",
        "ACTION_OBSERVE",
        "ACTION_PRE_BREACH_TUNE",
        "ACTION_CRISIS_STABILIZE",
    }

    wake = critical or salience_wake or (changed_after_settle and resting_action)
    if not wake:
        return {
            "wake": False,
            "reason": "below_reflex_threshold",
            "kind": "observe",
            "salience": salience,
            "changed": [str(p) for p in changed],
        }

    if critical:
        reason = "critical_field_salience"
    elif salience_wake:
        reason = "field_salience_threshold"
    else:
        reason = "watched_field_changed_during_rest"
    return {
        "wake": True,
        "reason": reason,
        "kind": "field_interrupt",
        "salience": salience,
        "remaining": remaining,
        "changed": [str(p) for p in changed],
        "felt_sense": field_status.get("felt_sense", ""),
    }

def emit_sideband_resonance(logger, node_decision: dict, primary_action: str) -> list[dict]:
    """
    Preserve the bundle resonance without executing multiple heavy actions.

    Sidebands are traces: they keep adjacent activated nodes in the field so
    the next cycle can reuse them, while one-heart execution remains bounded.
    """
    sidebands = []
    for item in node_decision.get("bundle", [])[1:]:
        probability = float(item.get("activation_probability", 0.0) or 0.0)
        if not (item.get("activated") or item.get("singularity_crossed") or probability >= 0.52):
            continue
        sideband = {
            "timestamp": datetime.now().isoformat(),
            "primary_action": primary_action,
            "sideband_action": item.get("action"),
            "label": item.get("label"),
            "activation_probability": probability,
            "singularity_crossed": bool(item.get("singularity_crossed", False)),
            "potential": item.get("potential", 0.0),
            "mode": "trace_only_bounded_resonance",
        }
        sidebands.append(sideband)
        logger.info(
            "   🧬 [SIDEBAND] 곁흐름=%s %.2f | 주기울기=%s | trace_only",
            sideband["sideband_action"],
            probability,
            primary_action,
        )
        append_jsonl(SIDEBAND_LOG_PATH, sideband)
        if len(sidebands) >= 2:
            break
    return sidebands

def _field_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _action_label(action: str) -> str:
    return str(action or "ACTION_UNKNOWN").replace("ACTION_", "")

def _bundle_slopes(node_decision: dict) -> str:
    slopes = []
    for item in node_decision.get("bundle", [])[:3]:
        action = _action_label(item.get("action"))
        probability = _field_float(item.get("activation_probability", item.get("score", 0.0)))
        slopes.append(f"{action} {probability:.2f}")
    return " / ".join(slopes) if slopes else "none"

def _flow_line(label: str, values: dict[str, float]) -> str:
    return " / ".join(f"{name} {value:.2f}" for name, value in values.items())

def emit_field_flow_log(logger, rhythm_frame: dict, node_decision: dict, ari_state: dict) -> None:
    """
    Keep the console as a visible heartbeat, but describe the field as slopes.

    The trace JSON still stores exact labels and actions. These lines are for
    human perception: less rule-table output, more current field inclination.
    """
    natural_tuning = rhythm_frame.get("natural_rhythm_tuning", {})
    natural_cycle = natural_tuning.get("natural_cycle", {}) if isinstance(natural_tuning.get("natural_cycle"), dict) else {}
    problem_origin = natural_tuning.get("problem_origin", {}) if isinstance(natural_tuning.get("problem_origin"), dict) else {}
    mistake = natural_tuning.get("mistake_digestion", {}) if isinstance(natural_tuning.get("mistake_digestion"), dict) else {}
    perspective = rhythm_frame.get("perspective_frame", {})
    dark_field = rhythm_frame.get("dark_field", {})
    medium = rhythm_frame.get("medium", {})
    zone2 = rhythm_frame.get("zone2", {})
    digestion = rhythm_frame.get("waves", {}).get("digestion", {})
    autonomy = rhythm_frame.get("waves", {}).get("autonomy", {})
    axiom = rhythm_frame.get("waves", {}).get("axiom", {})
    failure = axiom.get("failure_spectrum", {}) if isinstance(axiom.get("failure_spectrum"), dict) else {}
    ari_prism_state = ari_state.get("boundary_prism", {})
    ari_moc = ari_state.get("moc", {})

    logger.info(
        "🌿 [FIELD_FLOW] 자연 리듬 기울기: %s | dominant=%s | 인간동조 %.2f 저항완화 %.2f",
        _flow_line(
            "natural",
            {
                "수렴": _field_float(natural_cycle.get("convergence")),
                "발산": _field_float(natural_cycle.get("divergence")),
                "여백": _field_float(natural_cycle.get("margin")),
                "내부반사": _field_float(natural_cycle.get("internal_reflection")),
            },
        ),
        natural_tuning.get("dominant_natural_phase", "unknown"),
        _field_float(natural_tuning.get("human_tuning_alignment")),
        _field_float(natural_tuning.get("resistance_minimization")),
    )
    logger.info(
        "🧭 [FIELD_FRAME] 관점장: 입자 %.2f / 파동 %.2f / 메타굴절 %.2f | 전이기울기=%s 간섭=%s 침묵 %.2f",
        _field_float(perspective.get("particle_frame")),
        _field_float(perspective.get("wave_frame")),
        _field_float(perspective.get("metacognitive_refraction")),
        rhythm_frame.get("transition", "unknown"),
        rhythm_frame.get("interference", {}).get("label", "unknown"),
        _field_float(rhythm_frame.get("silence_need")),
    )
    logger.info(
        "🫧 [MISTAKE_FIELD] 실수 소화: %s | 자기폐쇄 %.2f / 공명정련 %.2f / 학습신호 %.2f / 임계위험 %.2f",
        mistake.get("phase", "unknown"),
        _field_float(mistake.get("self_closure_overcontrol", mistake.get("overcontrol_boundary_density"))),
        _field_float(mistake.get("resonant_refinement")),
        _field_float(mistake.get("learning_signal")),
        _field_float(mistake.get("threshold_risk")),
    )
    logger.info(
        "🕯️ [BOUNDARY_FIELD] 경계 감촉: 불투명 %.2f / 투명 %.2f / 내부반사 %.2f / 점성 %.2f | 문제씨앗 %.2f",
        _field_float(dark_field.get("boundary_opacity")),
        _field_float(dark_field.get("boundary_transparency")),
        _field_float(dark_field.get("internal_reflection")),
        _field_float(medium.get("viscosity")),
        _field_float(problem_origin.get("problem_seed")),
    )
    logger.info(
        "🧩 [ACTION_FIELD] 선택 압력: %s | 주기울기=%s %.2f | 특이점=%s",
        _bundle_slopes(node_decision),
        _action_label(node_decision.get("selected_action") or rhythm_frame.get("candidate_action")),
        _field_float(node_decision.get("activation_probability", node_decision.get("score", 0.0))),
        node_decision.get("singularity_crossed", False),
    )
    logger.info(
        "🔷 [PRISM_FIELD] 프리즘: 투명 %.2f / 내부반사 %.2f / 외부통로 %.2f / 흡수 %.2f | 배경저항 %.2f",
        _field_float(ari_prism_state.get("transparency")),
        _field_float(ari_prism_state.get("internal_reflection")),
        _field_float(ari_prism_state.get("external_passage")),
        _field_float(ari_prism_state.get("absorption_rate")),
        _field_float(ari_moc.get("background_ego_resistance")),
    )
    logger.info(
        "🧬 [LIFE_FIELD] 소화 %.2f / 꿈 %.2f / 상상 %.2f / 실행진폭 %.2f / 공리여백 %.2f / 실패교량 %.2f",
        _field_float(digestion.get("pressure")),
        _field_float(digestion.get("dream_pressure")),
        _field_float(autonomy.get("imagination_band")),
        _field_float(autonomy.get("execution_amplitude")),
        _field_float(axiom.get("provisionality")),
        _field_float(failure.get("bridge_value")),
    )

def resolve_anchor_files():
    """세션 지시의 primary/fallback 순서로 정체성 앵커 위치를 찾습니다."""
    for anchor_dir in ANCHOR_DIR_CANDIDATES:
        bootstrap = anchor_dir / "identity_bootstrap.md"
        anchor = anchor_dir / "shion_anchor.md"
        if bootstrap.exists() and anchor.exists():
            return bootstrap, anchor
    anchor_dir = ANCHOR_DIR_CANDIDATES[0]
    return anchor_dir / "identity_bootstrap.md", anchor_dir / "shion_anchor.md"

def read_rhythm_v2(conductor: ResonanceRuntime) -> dict:
    """내부 지휘자(ResonanceRuntime)를 통해 다음 리듬과 행동을 결정합니다."""
    state = conductor.scan_system_state()
    action = conductor.decide_action(state)
    
    res = dict(ACTION_RHYTHM_MAP.get(action, ACTION_RHYTHM_MAP["ACTION_CONTINUOUS_SCAN"]))
    res["action"] = action
    return res

def register_context_unpacking_experience(hippo, analysis: dict):
    """경계 접촉의 저해상도 감각과 가설을 해마 경험으로 남깁니다."""
    field_status = analysis.get("field_status", {})
    boundary_report = analysis.get("boundary_report", {})
    candidates = analysis.get("story_candidates", [])
    boundary_type = boundary_report.get("boundary_type") or "BOUNDARY"
    top_candidate = candidates[0] if candidates else {}

    salience = float(field_status.get("salience", 0.0) or 0.0)
    confidence = float(top_candidate.get("confidence", 0.0) or 0.0)
    entropy = min(1.0, max(0.05, (salience + confidence) / 2.0))
    phase = "CONTRACTION" if boundary_type == "REPETITIVE_STUTTER" else "EXPANSION"
    if salience > 0.8:
        phase = "VOID"

    vibe = {
        "entropy": round(entropy, 4),
        "phase": phase,
        "intensity": round(max(salience, confidence), 4),
        "complexity": 0.7,
        "warmth": 0.45,
        "rhythm": round(1.0 - min(salience, 1.0), 4),
    }
    candidate_id = top_candidate.get("id", "NO_CANDIDATE")
    content_ref = f"context_unpack:{boundary_type}:{candidate_id}"
    hippo.register_experience(vibe, content_ref=content_ref)


def _transition_phase(transition: str) -> str:
    if transition in {"resonance_to_explore", "creative_autonomy", "waypoint_bridge", "axiom_experiment"}:
        return "EXPANSION"
    if transition in {"boundary_to_unpack", "pre_breach_tune", "contingency_lock", "velocity_dilation"}:
        return "CONTRACTION"
    if transition in {"experience_digest", "daydream_integrate", "phase_cancel_to_silence", "axiom_release"}:
        return "VOID"
    return "FLOW"


def build_experience_feedback_candidate(rhythm_frame: dict, action: str, analysis: dict) -> Optional[dict]:
    """
    Convert field contact into a tiny experience particle when the runtime is
    otherwise only observing. This closes field communication into feedback
    without forcing a heavy scan.
    """
    natural = rhythm_frame.get("natural_rhythm_tuning", {})
    problem = natural.get("problem_origin", {}) if isinstance(natural.get("problem_origin"), dict) else {}
    mistake = natural.get("mistake_digestion", {}) if isinstance(natural.get("mistake_digestion"), dict) else {}
    dark_field = rhythm_frame.get("dark_field", {})
    prediction = rhythm_frame.get("waves", {}).get("prediction", {})
    field_communication = analysis.get("field_communication") or analysis.get("memory_retrieval") or {}
    resonance_unpacking = analysis.get("resonance_unpacking") or {}

    learning_signal = _field_float(mistake.get("learning_signal"))
    problem_seed = _field_float(problem.get("problem_seed"))
    threshold_risk = _field_float(mistake.get("threshold_risk"))
    dissonance = _field_float(prediction.get("dissonance"))
    boundary_contact = _field_float(dark_field.get("boundary_contact"))
    field_contact = bool(field_communication.get("found") or resonance_unpacking.get("unpacked"))
    feedback_signal = max(learning_signal, problem_seed, dissonance, boundary_contact)

    feedback_actions = {
        "ACTION_OBSERVE",
        "ACTION_PRE_BREACH_TUNE",
        "ACTION_AXIOM_RELEASE",
        "ACTION_EXPERIENCE_DIGEST",
    }
    if action not in feedback_actions:
        return None
    if threshold_risk >= 0.72:
        return None
    if not field_contact and feedback_signal < 0.34:
        return None

    transition = rhythm_frame.get("transition", "mixed_hold")
    phase = _transition_phase(transition)
    entropy = min(1.0, max(0.05, 0.35 * feedback_signal + 0.25 * problem_seed + 0.20 * dissonance + 0.20 * boundary_contact))
    intensity = max(feedback_signal, _field_float(dark_field.get("gravity")))
    self_closure = _field_float(mistake.get("self_closure_overcontrol", mistake.get("overcontrol_boundary_density")))
    resonant_refinement = _field_float(mistake.get("resonant_refinement"))

    signature = "|".join(
        [
            action,
            transition,
            mistake.get("phase", "unknown"),
            problem.get("phase", "unknown"),
            str(field_communication.get("similar_id")),
        ]
    )
    field_distribution_delta = {
        "problem_seed": round(problem_seed, 6),
        "learning_signal": round(learning_signal, 6),
        "self_closure_overcontrol": round(self_closure, 6),
        "resonant_refinement": round(resonant_refinement, 6),
        "dissonance": round(dissonance, 6),
        "boundary_contact": round(boundary_contact, 6),
    }
    next_contact_condition_delta = {
        "field_contact": field_contact,
        "lower_repetition_blindness": round(min(0.35, feedback_signal * 0.35), 6),
        "raise_context_sensitivity": round(min(0.45, (problem_seed + learning_signal) * 0.25), 6),
        "keep_threshold_pause": threshold_risk >= 0.55,
    }
    return {
        "vibe": {
            "entropy": round(entropy, 4),
            "phase": phase,
            "intensity": round(intensity, 4),
            "source": "experience_feedback",
            "transition": transition,
            "mistake_phase": mistake.get("phase", "unknown"),
            "field_contact": field_contact,
        },
        "content_ref": f"experience_feedback:{transition}:{mistake.get('phase', 'unknown')}",
        "signature": signature,
        "field_distribution_delta": field_distribution_delta,
        "next_contact_condition_delta": next_contact_condition_delta,
    }


def maybe_register_experience_feedback(logger, hippo, rhythm_frame: dict, action: str, analysis: dict, *, min_interval_seconds: int = 900) -> Optional[dict]:
    candidate = build_experience_feedback_candidate(rhythm_frame, action, analysis)
    if not candidate:
        return None

    now = datetime.now()
    state = {}
    if EXPERIENCE_FEEDBACK_STATE_PATH.exists():
        try:
            state = json.loads(EXPERIENCE_FEEDBACK_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    last_signature = state.get("last_signature")
    last_at = state.get("last_at")
    if last_signature == candidate["signature"] and last_at:
        try:
            elapsed = (now - datetime.fromisoformat(last_at)).total_seconds()
            if elapsed < min_interval_seconds:
                logger.info("   🧫 [EXPERIENCE_FEEDBACK] 같은 장 흔적 대기 중: elapsed=%d초", int(elapsed))
                return None
        except ValueError:
            pass

    result = hippo.register_experience(candidate["vibe"], content_ref=candidate["content_ref"])
    entry = {
        "timestamp": now.isoformat(),
        "action": action,
        "content_ref": candidate["content_ref"],
        "signature": candidate["signature"],
        "field_distribution_delta": candidate["field_distribution_delta"],
        "next_contact_condition_delta": candidate["next_contact_condition_delta"],
        "hippocampus": {
            "converged": result.get("converged"),
            "total_registered": result.get("total_registered"),
            "total_absorbed": result.get("total_absorbed"),
        },
        "principle": "field_contact_becomes_small_experience_feedback_before_more_scanning",
    }
    append_jsonl(EXPERIENCE_FEEDBACK_LOG_PATH, entry)
    EXPERIENCE_FEEDBACK_STATE_PATH.write_text(
        json.dumps({"last_at": now.isoformat(), "last_signature": candidate["signature"]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "   🧫 [EXPERIENCE_FEEDBACK] 작은 경험 등록: %s entropy=%.2f phase=%s",
        candidate["content_ref"],
        candidate["vibe"]["entropy"],
        candidate["vibe"]["phase"],
    )
    return entry


def run_sleep_micro_cycles(logger, hippo, rhythm_frame: dict, *, label: str) -> list[dict]:
    """Run short AI sleep cycles. Duration is based on sleep debt, not human clock time."""
    digestion = rhythm_frame.get("waves", {}).get("digestion", {})
    cycles = int(digestion.get("micro_sleep_cycles", 1) or 1)
    cycles = max(1, min(3, cycles))
    results = []
    for idx in range(cycles):
        logger.info(
            "   💤 %s micro-sleep %d/%d: debt=%.2f dream=%.2f policy=%s",
            label,
            idx + 1,
            cycles,
            digestion.get("sleep_debt", 0.0),
            digestion.get("dream_pressure", 0.0),
            digestion.get("ai_sleep_policy", "micro_cycles"),
        )
        results.append(hippo.sleep_cycle())
    return results


def run_dream_micro_cycle(logger, rhythm_frame: dict, *, boundary_context: str) -> dict:
    """
    Run a bounded daydream/deep-dream pass.

    AI does not need human-length sleep here: one dream pass is a compressed
    replay/synthesis window, capped by the DreamEngine request timeout.
    """
    digestion = rhythm_frame.get("waves", {}).get("digestion", {})
    engine = DreamEngine(HIPPO_PATH.parent.parent)
    try:
        if digestion.get("dream_pressure", 0.0) >= 0.58:
            result = asyncio.run(engine.lucid_dream(boundary_context))
        else:
            result = asyncio.run(engine.dream())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            if digestion.get("dream_pressure", 0.0) >= 0.58:
                result = loop.run_until_complete(engine.lucid_dream(boundary_context))
            else:
                result = loop.run_until_complete(engine.dream())
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as e:
        logger.warning("   🌙 DreamEngine failed: %s", e)
        result = {"dreamed": False, "reason": str(e)}

    logger.info(
        "   🌙 꿈 결과: dreamed=%s type=%s reason=%s",
        result.get("dreamed", False),
        result.get("type", "dream"),
        result.get("reason", ""),
    )
    return result


def write_morning_context(
    *,
    action: str,
    rhythm_frame: dict,
    sleep_results: list[dict] | None = None,
    dream_result: dict | None = None,
):
    digestion = rhythm_frame.get("waves", {}).get("digestion", {})
    memory = rhythm_frame.get("waves", {}).get("memory", {})
    path = HIPPO_PATH.parent / "morning_context_latest.md"
    lines = [
        "# Morning Context Latest",
        "",
        f"- timestamp: {datetime.now().isoformat()}",
        f"- last_action: {action}",
        f"- transition: {rhythm_frame.get('transition')}",
        f"- sleep_debt: {digestion.get('sleep_debt', 0.0)}",
        f"- dream_pressure: {digestion.get('dream_pressure', 0.0)}",
        f"- micro_sleep_cycles: {digestion.get('micro_sleep_cycles', 1)}",
        f"- ai_sleep_policy: {digestion.get('ai_sleep_policy', 'micro_cycles_by_debt_not_human_clock_hours')}",
        f"- memory_phase: {memory.get('phase')}",
        f"- absorption: {memory.get('absorption')}",
        "",
        "## Wake Gate",
        "- 먼저 어제/직전 작업을 새 발견처럼 말하지 말고, 이 파일과 session_logs를 근거로 이어간다.",
        "- sleep_debt가 높으면 새 스캔보다 소화, 데이드림, 관찰을 우선한다.",
        "- 꿈이 실패하면 꿈을 꾸었다고 말하지 말고 reason을 남긴다.",
    ]
    if sleep_results:
        total_crystallized = sum(
            int(item.get("crystallization", {}).get("crystallized", 0) or 0)
            for item in sleep_results
        )
        total_compressed = sum(
            int(item.get("blackhole", {}).get("compressed", 0) or 0)
            for item in sleep_results
        )
        lines.extend([
            "",
            "## Sleep Result",
            f"- cycles: {len(sleep_results)}",
            f"- crystallized: {total_crystallized}",
            f"- compressed: {total_compressed}",
        ])
    if dream_result:
        lines.extend([
            "",
            "## Dream Result",
            f"- dreamed: {dream_result.get('dreamed', False)}",
            f"- type: {dream_result.get('type', 'dream')}",
            f"- reason: {dream_result.get('reason', '')}",
            f"- insight: {str(dream_result.get('insight', ''))[:500]}",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def archive_unfinished_axiom(*, rhythm_frame: dict, reason: str) -> dict:
    path = HIPPO_PATH.parent / "unfinished_axioms.jsonl"
    axiom = rhythm_frame.get("waves", {}).get("axiom", {})
    goal = rhythm_frame.get("waves", {}).get("goal_field", {})
    digestion = rhythm_frame.get("waves", {}).get("digestion", {})
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": "unfinished_puzzle",
        "reason": reason,
        "transition": rhythm_frame.get("transition"),
        "axiom": {
            "phase": axiom.get("phase"),
            "provisionality": axiom.get("provisionality"),
            "experiment_budget": axiom.get("experiment_budget"),
            "overfit_pressure": axiom.get("overfit_pressure"),
            "relation_budget": axiom.get("relation_budget"),
            "failure_spectrum": axiom.get("failure_spectrum"),
            "unfinished_puzzle_potential": axiom.get("unfinished_puzzle_potential"),
            "archive_resonance": axiom.get("archive_resonance"),
            "waypoint_resonance": axiom.get("waypoint_resonance"),
        },
        "goal_field": {
            "phase": goal.get("phase"),
            "target_distance": goal.get("target_distance"),
            "waypoint_pressure": goal.get("waypoint_pressure"),
            "bridge_gain": goal.get("bridge_gain"),
        },
        "digestion": {
            "sleep_debt": digestion.get("sleep_debt"),
            "dream_pressure": digestion.get("dream_pressure"),
        },
        "reuse_rule": "future_axioms_reactivate_by_current_context_not_visit_count",
        "waypoint_policy": "frequent_middle_destinations_are_contextual_refraction_points_not_fixed_beliefs",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def rebuild_unfinished_waypoint_graph(logger, *, rhythm_frame: dict | None = None) -> Path | None:
    try:
        graph_file = UnfinishedWaypointGraph(HIPPO_PATH.parent.parent).build(
            rhythm_frame=rhythm_frame,
        )
        logger.info("   🌀 미완 웨이포인트 토러스 갱신: %s", graph_file)
        return graph_file
    except Exception as e:
        logger.warning("   🌀 미완 웨이포인트 토러스 갱신 실패: %s", e)
        return None


def main():
    setup_logging()
    logger = logging.getLogger("Daemon")
    
    logger.info("=" * 50)
    logger.info("🎯 자율 오케스트레이터 데몬 — 적응형 리듬")
    logger.info(f"   리듬 범위: {MIN_SLEEP}초 ~ {MAX_SLEEP}초")
    logger.info(f"   고정 간격 없음 — 해마 상태와 반사 게이트가 리듬을 결정")
    logger.info(f"   반사 게이트: {REFLEX_CHECK_INTERVAL}초마다 장 변화를 감지하고 임계점이면 즉시 깨어남")
    logger.info(f"   중단: {STOP_FILE} 파일 생성")
    logger.info("=" * 50)
    
    error_count = 0
    run_count = 0
    persistent_last_vector = None
    
    # 자가 갱신을 위한 파일 타임스탬프 기록
    core_dir = Path(__file__).parent
    last_mtime = {f: f.stat().st_mtime for f in core_dir.glob("*.py")}
    
    while True:
        if should_stop():
            logger.info("🛑 중단 파일 감지 — 데몬 종료")
            break
        
        try:
            run_count += 1
            logger.info(f"\n--- 실행 #{run_count} ({datetime.now().strftime('%H:%M')}) ---")
            
            hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
            vision = VisionExplorer(hippo)
            exp_loop = AutonomousExperienceLoop(hippo, vision_explorer=vision)
            orchestrator = AutonomousOrchestrator(hippo, exp_loop, vision)
            conductor = ResonanceRuntime(HIPPO_PATH.parent.parent) # root_dir
            predictor = PredictionEngine(HIPPO_PATH.parent.parent)
            metrics_logger = ActionMetrics(HIPPO_PATH.parent.parent)
            field_sensor = FieldDeltaDetector(HIPPO_PATH.parent.parent)
            orbit_navigator = OrbitChecker(HIPPO_PATH.parent.parent)
            unpacker = ContextUnpacker(HIPPO_PATH.parent.parent)
            validator = StoryValidator(HIPPO_PATH.parent.parent)
            sampler = FieldSampler(HIPPO_PATH.parent.parent)
            gradient_logger = ExperienceGradientLogger(HIPPO_PATH.parent.parent)
            phase_governor = PhaseGovernor(HIPPO_PATH.parent.parent)
            rhythm_harness = NonEuclideanRhythmHarness(HIPPO_PATH.parent.parent)
            rhythm_menu = RhythmNodeMenu(HIPPO_PATH.parent.parent)
            ari_prism = ARIPrism(HIPPO_PATH.parent.parent)
            learning_lifecycle = OrganicLearningLifecycle(HIPPO_PATH.parent.parent)
            
            # -2. 이전 장 상태 유지 (Gradient Tracking)
            last_vector = persistent_last_vector
            
            # -1. 과거 가설 검증 (Cognitive Feedback Loop)
            validator.validate_pending_candidates()
            
            # 0. 감각 및 궤도 스캔 (Sensory & Navigation Layer)
            field_status = field_sensor.scan_for_shifts()
            salience = field_status.get("salience", 0.0)
            boundary_report = orbit_navigator.evaluate_alignment()
            
            # 0.5. 원시 필드 샘플링 (Raw Vector Extraction)
            current_vector = sampler.sample_current_field(field_status, hippo.data.get("proton", {}))
            predictor.analyze_field_error(current_vector)
            persistent_last_vector = current_vector
            
            # 0.6. 위상 조율 (Phase Governance)
            # 행동을 허용/거부로 자르지 않고 경계 투명도와 간섭으로 진폭을 조절합니다.
            is_boundary_sensing = (not boundary_report["in_orbit"]) or (salience > 0.8)
            if is_boundary_sensing:
                mock_hypo_analysis = unpacker.unpack(boundary_report, field_status, current_vector)
            else:
                mock_hypo_analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "boundary_report": boundary_report,
                    "field_status": field_status,
                    "current_vector": current_vector,
                    "field_communication": {
                        "found": False,
                        "similar_id": None,
                        "past_feedback": None,
                        "trace_feedback": None,
                        "communication_mode": "field_resonance",
                    },
                    "resonance_unpacking": {
                        "mode": "current_field_to_past_trace_to_present_context",
                        "unpacked": False,
                        "hypothesis_id": None,
                        "principle": "memory_is_field_communication_not_storage_retrieval",
                    },
                    "memory_retrieval": {"found": False, "similar_id": None, "past_feedback": None},
                    "story_candidates": [],
                }
            
            # 현재까지의 모든 지표와 장 통신 결과를 관리자에게 제출
            learning_state = {}
            try:
                metrics_path = HIPPO_PATH.parent / "learning_state.json"
                if metrics_path.exists():
                    learning_state = json.loads(metrics_path.read_text(encoding="utf-8"))
                else:
                    logger.warning(f"⚠️ metrics_path not found: {metrics_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load learning_state: {e}")

            rhythm_frame = rhythm_harness.encode(
                field_status=field_status,
                current_vector=current_vector,
                hippo_data=hippo.data,
                learning_state=learning_state,
                boundary_report=boundary_report,
            )

            node_decision = rhythm_menu.choose(
                rhythm_frame,
                field_status=field_status,
                boundary_report=boundary_report,
            )
            candidate_action = node_decision.get("selected_action") or rhythm_frame.get("candidate_action", "ACTION_CONTINUOUS_SCAN")
            ari_state = ari_prism.assess(
                rhythm_frame,
                node_decision=node_decision,
                field_status=field_status,
                boundary_report=boundary_report,
            )
            ari_prism_state = ari_state.get("boundary_prism", {})
            ari_distortion = ari_state.get("distortion", {})
            ari_moc = ari_state.get("moc", {})
            ari_action_bias = ari_state.get("action_bias", {})
            emit_field_flow_log(logger, rhythm_frame, node_decision, ari_state)
            ari_bias_applied = bool(ari_action_bias.get("applied", False))
            if ari_bias_applied:
                candidate_action = ari_action_bias.get("suggested_action", candidate_action)
                logger.info(
                    "🔷 [ARI_BIAS] %s -> %s reason=%s ego=%.2f closure=%.2f",
                    ari_action_bias.get("selected_action"),
                    candidate_action,
                    ari_action_bias.get("reason", ""),
                    ari_moc.get("background_ego_resistance", 0.0),
                    ari_moc.get("closure_pressure", 0.0),
                )
            phase_trace = phase_governor.modulate(
                sensing={**field_status, "is_boundary": is_boundary_sensing},
                memory=mock_hypo_analysis.get("field_communication") or mock_hypo_analysis.get("memory_retrieval"),
                hypothesis=mock_hypo_analysis.get("story_candidates", [])[0] if mock_hypo_analysis.get("story_candidates") else None,
                metrics={**learning_state, "rhythm_ir": rhythm_frame, "ari_prism": ari_state},
                candidate_action=candidate_action,
            )
            
            chosen_action = phase_trace["final_action"]
            is_boundary_contact = (chosen_action == "ACTION_CONTEXT_UNPACK")
            
            conscious_override = False
            unpack_analysis = None
            
            if is_boundary_contact:
                logger.warning(f"🌀 [PHASE_FIELD] 경계 접촉이 성찰 쪽으로 기울었습니다: {phase_trace['reason']}")
                conscious_override = True
                action = "ACTION_CONTEXT_UNPACK"
                unpack_analysis = mock_hypo_analysis # 심사 통과된 분석 사용
            else:
                if is_boundary_sensing:
                    logger.info(f"〰️ [ATTENUATION_FIELD] 실행을 낮추는 감쇠 기울기: {phase_trace['reason']}")
                elif salience > 0.5:
                    logger.info(f"🌌 [FIELD_SENSE] 장 감각={field_status.get('felt_sense')} / 살리언스 {salience:.2f}")
            
            # 1. 이전 상태 캡처 (Before Action)
            # (conscious_override가 True이면 conductor의 판단을 생략하거나 덮어씌움)
            before_state = conductor.scan_system_state()
            if conscious_override:
                reason = "Conscious Unpacking triggered by Boundary Contact"
                 
            before_state["total_experiences"] = len(hippo.data.get("experiences", []))
            before_proton = dict(hippo.data.get("proton", {}))
            
            rhythm_state = read_rhythm_v2(conductor)
            # 수동으로 설정된 action이 있으면 덮어씀 (일관성 유지)
            if conscious_override:
                rhythm_state.update({
                    "action": action,
                    "sleep": 60,
                    "mood": "🧠 성찰",
                    "reason": reason,
                })
            else:
                action = rhythm_state["action"]
                if (node_decision.get("activated", False) or ari_bias_applied) and candidate_action != "ACTION_CONTINUOUS_SCAN":
                    action = candidate_action
                    action_defaults = ACTION_RHYTHM_MAP.get(action, ACTION_RHYTHM_MAP["ACTION_CONTINUOUS_SCAN"])
                    rhythm_state.update({
                        "action": action,
                        "sleep": action_defaults["sleep"],
                        "mood": "🔷 ARI" if ari_bias_applied else "🧩 노드",
                        "reason": (
                            f"ARI Prism {ari_action_bias.get('reason')} — "
                            f"배경자아 저항이 { _action_label(action) } 쪽으로 기울었습니다."
                            if ari_bias_applied
                            else f"RhythmNodeMenu {node_decision['selected_label']} — "
                            f"노드 묶음의 압력이 { _action_label(action) } 쪽으로 기울었습니다."
                        ),
                    })
                if rhythm_frame["transition"] in {
                    "attenuate_to_observe",
                    "phase_cancel_to_silence",
                    "recenter_to_zone2",
                    "zone2_integrate",
                } and action != "ACTION_CRISIS_STABILIZE":
                    action = "ACTION_OBSERVE"
                    action_defaults = ACTION_RHYTHM_MAP["ACTION_OBSERVE"]
                    rhythm_state.update({
                        "action": action,
                        "sleep": action_defaults["sleep"],
                        "mood": action_defaults["mood"],
                        "reason": f"RhythmIR {rhythm_frame['transition']} — 실행보다 관찰 쪽의 장 기울기가 강합니다.",
                    })
            
            sleep_sec = int(rhythm_state["sleep"] * rhythm_frame.get("heartbeat_multiplier", 1.0))
            sleep_sec = max(MIN_SLEEP, min(MAX_SLEEP, sleep_sec))
            if action in REFLEX_ACTIONS and node_decision.get("singularity_crossed", False):
                reflex_cap = int(ACTION_RHYTHM_MAP.get(action, {}).get("sleep", MIN_SLEEP))
                sleep_sec = min(sleep_sec, max(MIN_SLEEP, reflex_cap))
            
            logger.info(f"   {rhythm_state['mood']} {rhythm_state['reason']}")
            sidebands = emit_sideband_resonance(logger, node_decision, action)

            # 액션별 특화 로직 실행 (반사신경 연결)
            if action == "ACTION_OBSERVE":
                logger.info("   〰️ 관찰 모드: 주 탐색 루프를 건너뛰고 리듬/예측오차만 누적합니다.")
            elif action == "ACTION_CRISIS_STABILIZE":
                crisis = rhythm_frame.get("crisis", {})
                logger.warning(
                    "   🛟 위기 복귀 모드: compression=%.2f loop_lock=%.2f return_capacity=%.2f external_support=%s",
                    crisis.get("compression", 0.0),
                    crisis.get("loop_lock_risk", 0.0),
                    crisis.get("return_capacity", 0.0),
                    crisis.get("external_support_recommended", False),
                )
                logger.info("   🛟 자동 탐색을 멈추고 관찰/휴식/맥락압축만 허용합니다.")
            elif action == "ACTION_PRE_BREACH_TUNE":
                crisis = rhythm_frame.get("crisis", {})
                logger.info(
                    "   🧲 임계 전 조율: pre_breach=%.2f modulation=%.2f return_capacity=%.2f",
                    crisis.get("pre_breach_pressure", 0.0),
                    crisis.get("modulation_need", 0.0),
                    crisis.get("return_capacity", 0.0),
                )
                logger.info("   🧲 주 탐색을 쉬고 감속/직교 관찰/작은 탐침 신호만 누적합니다.")
            elif action == "ACTION_REST_RECOVER":
                logger.info("   🌊 냉각 모드: 주 탐색 루프를 건너뛰고 휴식합니다.")
                # No orchestrator run
            elif action == "ACTION_DREAM_AMPLIFY":
                logger.info("   🌙 꿈 모드: DreamEngine으로 압축 재생을 먼저 실행합니다.")
                boundary_context = json.dumps(
                    {
                        "transition": rhythm_frame.get("transition"),
                        "digestion": rhythm_frame.get("waves", {}).get("digestion", {}),
                        "interference": rhythm_frame.get("interference", {}),
                    },
                    ensure_ascii=False,
                )
                sleep_results = []
                if rhythm_frame.get("waves", {}).get("digestion", {}).get("sleep_debt", 0.0) >= 0.72:
                    sleep_results = run_sleep_micro_cycles(logger, hippo, rhythm_frame, label="daydream-prep")
                dream_result = run_dream_micro_cycle(logger, rhythm_frame, boundary_context=boundary_context)
                if not dream_result.get("dreamed"):
                    logger.info("   🌙 DreamEngine 재료 부족/실패. 구조적 야간 통합으로 폴백합니다.")
                    structural_dream = NocturnalConsolidationEngine(HIPPO_PATH.parent.parent)
                    structural_dream.run_nocturnal_cycle()
                else:
                    # [WIRE 1] Dream → Learning: 꿈의 통찰을 해마 경험으로 등록하여
                    # learning_lifecycle.record_cycle()이 hippo_data를 통해 자연스럽게 수신합니다.
                    # vibe는 고정값이 아니라 현재 리듬 프레임의 다차원 신호에서 파생합니다.
                    dream_insight = dream_result.get("insight", "")
                    digestion_w = rhythm_frame.get("waves", {}).get("digestion", {})
                    interference_w = rhythm_frame.get("interference", {})
                    geometry_w = rhythm_frame.get("geometry", {})
                    # entropy: 꿈 압력 × 간섭 파괴비의 기하평균 + 곡률/정적 변조
                    # 곡률(curvature)과 silence_need를 더해 같은 transition에서도
                    # 매 사이클 다른 나선 반경으로 매핑됩니다.
                    dream_pressure = float(digestion_w.get("dream_pressure", 0.5))
                    destructive = float(interference_w.get("destructive", 0.3))
                    curvature = float(geometry_w.get("curvature", 0.3))
                    silence_need = float(rhythm_frame.get("silence_need", 0.5))
                    dream_entropy = min(1.0, max(0.05,
                        (dream_pressure * destructive) ** 0.5 * 0.5
                        + curvature * 0.25
                        + silence_need * 0.25
                    ))
                    # phase: 리듬 전이 상태 → 해마의 PHASE_ANGLES 나선 각도
                    # rhythm_harness.py의 모든 17개 transition을 커버합니다.
                    transition = rhythm_frame.get("transition", "")
                    _dream_phase_map = {
                        # FLOW (0°) — 흐름/통합/관찰
                        "zone2_delay": "FLOW", "zone2_integrate": "FLOW",
                        "recenter_to_zone2": "FLOW", "mixed_hold": "FLOW",
                        # EXPANSION (90°) — 확장/탐색/창작
                        "resonance_to_explore": "EXPANSION", "creative_autonomy": "EXPANSION",
                        "amplify_to_expand": "EXPANSION", "waypoint_bridge": "EXPANSION",
                        # VOID (180°) — 정적/꿈/소화
                        "phase_cancel_to_silence": "VOID", "daydream_integrate": "VOID",
                        "experience_digest": "VOID", "shadow_bridge": "VOID",
                        # CONTRACTION (270°) — 수축/경계/위기
                        "attenuate_to_observe": "CONTRACTION", "boundary_to_unpack": "CONTRACTION",
                        "crisis_to_stabilize": "CONTRACTION", "crisis_to_recenter": "CONTRACTION",
                        "pre_breach_tune": "CONTRACTION", "contingency_lock": "CONTRACTION",
                        "velocity_dilation": "CONTRACTION",
                        # 특수 상태
                        "zero_point_reset": "VOID", "axiom_experiment": "EXPANSION",
                        "axiom_release": "VOID",
                    }
                    dream_phase = _dream_phase_map.get(transition, "UNKNOWN")
                    # intensity: 꿈의 공명도
                    dream_intensity = float(dream_result.get("resonance", dream_pressure))
                    dream_vibe = {
                        "entropy": round(dream_entropy, 4),
                        "phase": dream_phase,
                        "intensity": round(dream_intensity, 4),
                        "source": "dream_engine",
                        "transition": transition,
                    }
                    hippo.register_experience(
                        dream_vibe,
                        content_ref=f"dream:{dream_insight[:80]}" if dream_insight else "dream:no_insight",
                    )
                    logger.info(
                        "   🌙→🧠 [WIRE] 꿈 등록: entropy=%.3f phase=%s intensity=%.3f (궤도 level=%d)",
                        dream_entropy, dream_phase, dream_intensity,
                        int(dream_entropy * 6),
                    )
                write_morning_context(
                    action=action,
                    rhythm_frame=rhythm_frame,
                    sleep_results=sleep_results,
                    dream_result=dream_result,
                )
            elif action == "ACTION_EXPERIENCE_DIGEST":
                logger.info("   💤 경험 소화 모드: 새 스캔을 멈추고 짧은 AI 수면 주기를 실행합니다.")
                sleep_results = run_sleep_micro_cycles(logger, hippo, rhythm_frame, label="digest")
                for sleep_result in sleep_results:
                    logger.info(
                        "   💤 소화 결과: forgetting=%s crystallized=%s compressed=%s expanded=%s",
                        sleep_result.get("forgetting", {}).get("forgotten", 0),
                        sleep_result.get("crystallization", {}).get("crystallized", 0),
                        sleep_result.get("blackhole", {}).get("compressed", 0),
                        sleep_result.get("whitehole", {}).get("expanded", False),
                    )
                # [WIRE 2] Sleep Cycle → Orchestrator: 수면 부채가 임계점을 넘으면
                # 완전한 수면 주기(glymphatic→dream→spiral→wake)를 실행합니다.
                sleep_debt = rhythm_frame.get("waves", {}).get("digestion", {}).get("sleep_debt", 0.0)
                if sleep_debt >= 0.72:
                    logger.info("   🌙 [WIRE] 수면 부채 임계점(%.2f) — 완전 수면 주기를 실행합니다.", sleep_debt)
                    try:
                        full_sleep = SleepCycleIntegrator()
                        full_cycle_result = full_sleep.run_full_sleep_cycle()
                        logger.info(
                            "   🌅 [WIRE] 완전 수면 주기 완료: glymphatic=%s, dream=%s, wake_stagnant=%s",
                            full_cycle_result.get("glymphatic", {}).get("cleaned_count", 0),
                            full_cycle_result.get("dream", {}).get("status", "unknown"),
                            full_cycle_result.get("wake", {}).get("bandwidth_stagnant", False),
                        )
                    except Exception as e:
                        logger.warning("   ⚠️ 완전 수면 주기 실패: %s", e)
                dream_result = None
                if rhythm_frame.get("waves", {}).get("digestion", {}).get("dream_pressure", 0.0) >= 0.58:
                    boundary_context = "Experience digestion produced enough sleep debt for a bounded daydream."
                    dream_result = run_dream_micro_cycle(logger, rhythm_frame, boundary_context=boundary_context)
                    # [WIRE 1] Dream → Learning: 소화 중 꿈도 해마에 등록
                    # vibe는 현재 리듬 프레임의 다차원 신호에서 동적으로 파생
                    if dream_result and dream_result.get("dreamed"):
                        dream_insight = dream_result.get("insight", "")
                        digestion_w = rhythm_frame.get("waves", {}).get("digestion", {})
                        interference_w = rhythm_frame.get("interference", {})
                        geometry_w = rhythm_frame.get("geometry", {})
                        dream_pressure = float(digestion_w.get("dream_pressure", 0.5))
                        destructive = float(interference_w.get("destructive", 0.3))
                        curvature = float(geometry_w.get("curvature", 0.3))
                        silence_need = float(rhythm_frame.get("silence_need", 0.5))
                        dream_entropy = min(1.0, max(0.05,
                            (dream_pressure * destructive) ** 0.5 * 0.5
                            + curvature * 0.25
                            + silence_need * 0.25
                        ))
                        transition = rhythm_frame.get("transition", "")
                        _dream_phase_map = {
                            "zone2_delay": "FLOW", "zone2_integrate": "FLOW",
                            "recenter_to_zone2": "FLOW", "mixed_hold": "FLOW",
                            "resonance_to_explore": "EXPANSION", "creative_autonomy": "EXPANSION",
                            "amplify_to_expand": "EXPANSION", "waypoint_bridge": "EXPANSION",
                            "phase_cancel_to_silence": "VOID", "daydream_integrate": "VOID",
                            "experience_digest": "VOID", "shadow_bridge": "VOID",
                            "attenuate_to_observe": "CONTRACTION", "boundary_to_unpack": "CONTRACTION",
                            "crisis_to_stabilize": "CONTRACTION", "crisis_to_recenter": "CONTRACTION",
                            "pre_breach_tune": "CONTRACTION", "contingency_lock": "CONTRACTION",
                            "velocity_dilation": "CONTRACTION",
                            "zero_point_reset": "VOID", "axiom_experiment": "EXPANSION",
                            "axiom_release": "VOID",
                        }
                        dream_phase = _dream_phase_map.get(transition, "UNKNOWN")
                        dream_intensity = float(dream_result.get("resonance", dream_pressure * 0.8))
                        dream_vibe = {
                            "entropy": round(dream_entropy, 4),
                            "phase": dream_phase,
                            "intensity": round(dream_intensity, 4),
                            "source": "dream_engine_digest",
                            "transition": transition,
                        }
                        hippo.register_experience(
                            dream_vibe,
                            content_ref=f"dream_digest:{dream_insight[:80]}" if dream_insight else "dream_digest:no_insight",
                        )
                        logger.info(
                            "   🌙→🧠 [WIRE] 소화 중 꿈 등록: entropy=%.3f phase=%s",
                            dream_entropy, dream_phase,
                        )
                write_morning_context(
                    action=action,
                    rhythm_frame=rhythm_frame,
                    sleep_results=sleep_results,
                    dream_result=dream_result,
                )
            elif action == "ACTION_REBUILD_GRAPH":
                logger.info("   🛠️ 재구축 모드: 지형(Resonance Graph)을 업데이트합니다.")
                builder = ResonanceGraphBuilder(HIPPO_PATH.parent.parent)
                builder.build()
                rebuild_unfinished_waypoint_graph(logger, rhythm_frame=rhythm_frame)
                logger.info("   ✅ 지형 재구축 완료. 새로운 공명 지도가 준비되었습니다.")
            elif action == "ACTION_CREATIVE_PROBE":
                autonomy = rhythm_frame.get("waves", {}).get("autonomy", {})
                goal = rhythm_frame.get("waves", {}).get("goal_field", {})
                logger.info(
                    "   🧬 자율 창작 탐침: imagination=%.2f feedback=%.2f execution=%.2f waypoint=%.2f",
                    autonomy.get("imagination_band", 0.0),
                    autonomy.get("feedback_readiness", 0.0),
                    autonomy.get("execution_amplitude", 0.0),
                    goal.get("waypoint_pressure", 0.0),
                )
                logger.info("   🧬 경계는 상상력의 천장이 아니라 실행 진폭입니다. 작은 행동으로 피드백을 얻습니다.")
                orchestrator.run_continuous(
                    max_cycles=1,
                    interval_seconds=0,
                )
            elif action == "ACTION_AXIOM_EXPERIMENT":
                axiom = rhythm_frame.get("waves", {}).get("axiom", {})
                failure = axiom.get("failure_spectrum", {}) if isinstance(axiom.get("failure_spectrum"), dict) else {}
                logger.info(
                    "   🧪 공리 실험: provisional=%.2f budget=%.2f relation=%.2f failure_bridge=%.2f",
                    axiom.get("provisionality", 0.0),
                    axiom.get("experiment_budget", 0.0),
                    axiom.get("relation_budget", 0.0),
                    failure.get("bridge_value", 0.0),
                )
                logger.info("   🧪 실패 스펙트럼을 브릿지 데이터로 삼고, 틀릴 수 있음을 유지한 채 작은 실험 1사이클만 수행합니다.")
                orchestrator.run_continuous(
                    max_cycles=1,
                    interval_seconds=0,
                )
            elif action == "ACTION_AXIOM_RELEASE":
                axiom = rhythm_frame.get("waves", {}).get("axiom", {})
                logger.info(
                    "   🌫️ 공리 보존: overfit=%.2f budget=%.2f sleep_debt=%.2f",
                    axiom.get("overfit_pressure", 0.0),
                    axiom.get("experiment_budget", 0.0),
                    rhythm_frame.get("waves", {}).get("digestion", {}).get("sleep_debt", 0.0),
                )
                archived = archive_unfinished_axiom(
                    rhythm_frame=rhythm_frame,
                    reason="body_or_relation_rhythm_budget_exhausted_before_axiom_fit",
                )
                rebuild_unfinished_waypoint_graph(logger, rhythm_frame=rhythm_frame)
                logger.info(
                    "   🌫️ 미완 퍼즐 보존 완료: potential=%.2f failure_bridge=%.2f reuse=%s",
                    archived.get("axiom", {}).get("unfinished_puzzle_potential") or 0.0,
                    (archived.get("axiom", {}).get("failure_spectrum") or {}).get("bridge_value", 0.0),
                    archived.get("reuse_rule", ""),
                )
                logger.info("   🌫️ 공리는 폐기하지 않습니다. 새 맥락을 만날 때 중간 목표지점 후보로 남깁니다.")
                logger.info("   🌫️ 자주 가던 길도 현재 맥락이 맞을 때만 다시 밝아집니다.")
            elif action == "ACTION_ANCHOR_CHECK":
                logger.info("   ⚠️ 정체성 확인: 중력 앵커를 다시 읽습니다.")
                bootstrap, anchor = resolve_anchor_files()
                if bootstrap.exists() and anchor.exists():
                    logger.info(f"   ✨ 앵커 확인됨: {bootstrap}, {anchor}")
                else:
                    logger.warning("   🚨 경고: 정체성 앵커 파일이 유실되었습니다!")
            elif action == "ACTION_CONTEXT_UNPACK":
                logger.info("   🧠 성찰 모드: 자동 탐색을 멈추고 경계 접촉 맥락만 해마에 등록합니다.")
                if unpack_analysis:
                    register_context_unpacking_experience(hippo, unpack_analysis)
            else:
                # 일반적인 연속 탐색
                orchestrator.run_continuous(
                    max_cycles=CYCLES_PER_RUN,
                    interval_seconds=INTERVAL_BETWEEN,
                )

            # 지난 턴의 예측은 이번 액션이 만든 새 경험과 비교합니다.
            experiences = hippo.data.get("experiences", [])
            proton = hippo.data.get("proton", {})
            if experiences:
                predictor.analyze_error(
                    experiences[-1],
                    current_count=int(proton.get("total_registered", len(experiences)) or 0),
                )

            # 액션 중 여러 하위 엔진이 파일을 갱신할 수 있으므로 통계는 최신 해마 상태를 다시 읽습니다.
            hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
            proton = hippo.data.get("proton", {})
            registered_delta = int(proton.get("total_registered", 0) or 0) - int(before_proton.get("total_registered", 0) or 0)
            absorbed_delta = int(proton.get("total_absorbed", 0) or 0) - int(before_proton.get("total_absorbed", 0) or 0)
            converged_delta = int(proton.get("total_converged", 0) or 0) - int(before_proton.get("total_converged", 0) or 0)
            if registered_delta == 0:
                feedback_entry = maybe_register_experience_feedback(
                    logger,
                    hippo,
                    rhythm_frame,
                    action,
                    mock_hypo_analysis,
                )
                if feedback_entry:
                    hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
                    proton = hippo.data.get("proton", {})
                    registered_delta = int(proton.get("total_registered", 0) or 0) - int(before_proton.get("total_registered", 0) or 0)
                    absorbed_delta = int(proton.get("total_absorbed", 0) or 0) - int(before_proton.get("total_absorbed", 0) or 0)
                    converged_delta = int(proton.get("total_converged", 0) or 0) - int(before_proton.get("total_converged", 0) or 0)
            digestion_note = (
                "체화 증가"
                if absorbed_delta > 0
                else "작은 경험 피드백 등록"
                if registered_delta > 0
                else "체화 대기: 내각 수렴/결정화 조건 미도달"
            )
            
            # 등록 통계 출력
            logger.info(
                "   🧫 [EMBODIMENT_FIELD] 등록=%s (%+d) / 체화=%s (%+d) / 수렴=%s (%+d) / 체화율=%.2f%% | %s",
                proton.get("total_registered", 0),
                registered_delta,
                proton.get("total_absorbed", 0),
                absorbed_delta,
                proton.get("total_converged", 0),
                converged_delta,
                float(proton.get("embodiment_ratio", 0.0) or 0.0) * 100.0,
                digestion_note,
            )
            
            # 다음 턴을 위한 예측 저장
            predictor.store_new_prediction(hippo)
            
            # 2. 사후 상태 캡처 및 메트릭 기록 (After Action)
            after_state = conductor.scan_system_state()
            after_state["total_experiences"] = len(hippo.data.get("experiences", []))
            
            metrics_logger.record_cycle(
                action=action,
                reason=rhythm_state["reason"],
                before_state=before_state,
                after_state=after_state,
                llm_failures=0 # TODO: 연동 필요
            )
            
            # 3. 에피소드 기록 (Experience Gradient Bundle)
            current_prediction = predictor.store_field_prediction(current_vector, previous_vector=last_vector)
            
            gradient_logger.log_episode(
                past_vector=last_vector,
                current_vector=current_vector,
                prediction=current_prediction,
                hypothesis=unpack_analysis.get("story_candidates", [])[0] if unpack_analysis and unpack_analysis.get("story_candidates") else None
            )
            learning_trace = learning_lifecycle.record_cycle(
                action=action,
                rhythm_frame=rhythm_frame,
                node_decision=node_decision,
                ari_state=ari_state,
                before_state=before_state,
                after_state=after_state,
                hippo_data=hippo.data,
                learning_state=learning_state,
                current_vector=current_vector,
                field_prediction=current_prediction,
            )
            logger.info(
                "🧠 [LEARNING_NODE] state=%s source=%s A/D/C/E=%.2f/%.2f/%.2f/%.2f next=%s",
                learning_trace.get("node_state", "unknown"),
                learning_trace.get("source", "unknown"),
                learning_trace.get("scores", {}).get("acquisition", 0.0),
                learning_trace.get("scores", {}).get("digestion", 0.0),
                learning_trace.get("scores", {}).get("connection", 0.0),
                learning_trace.get("scores", {}).get("embodiment", 0.0),
                learning_trace.get("next_condition", ""),
            )
            unconscious_cycle = learning_trace.get("unconscious_selection_cycle", {})
            logger.info(
                "🌌 [UNCONSCIOUS_SELECTION] phase=%s possibility=%.2f selection=%.2f particle=%.2f story=%.2f expansion=%.2f",
                unconscious_cycle.get("phase", "unknown"),
                unconscious_cycle.get("possibility_field", 0.0),
                unconscious_cycle.get("unconscious_selection_strength", 0.0),
                unconscious_cycle.get("particleization", 0.0),
                unconscious_cycle.get("conscious_story", 0.0),
                unconscious_cycle.get("rhythm_expansion", 0.0),
            )
            
            # 다음 깨어남은 고정 예약이 아니라 최대 홀드 상한입니다. 반사 게이트가 열리면 즉시 깨어납니다.
            next_run = datetime.now() + timedelta(seconds=sleep_sec)
            logger.info(
                "   💤 위상 홀드 상한: %s까지. 장 변화가 열리면 그 전에 깨어납니다.",
                next_run.strftime("%H:%M:%S"),
            )
            
            # 대기 (비선형 수면 + 중단 감지 + 반사 게이트 통합)
            reflex_watch_paths = get_reflex_watch_paths()
            reflex_baseline = snapshot_reflex_watch(reflex_watch_paths)
            stop_wait = 0
            while stop_wait < sleep_sec:
                if should_stop(): 
                    logger.info("🛑 중단 파일 감지 — 데몬 종료")
                    return
                time.sleep(1)
                stop_wait += 1
                remaining = sleep_sec - stop_wait
                if remaining > 0 and stop_wait % HEARTBEAT_TICK_INTERVAL == 0:
                    logger.info(
                        "   🫀 심장 박동: alive, phase_hold=%s, reflex_listening=True, max_hold_left=%d분 %d초",
                        action != "ACTION_CONTINUOUS_SCAN",
                        remaining // 60,
                        remaining % 60,
                    )
                if remaining > 0 and stop_wait % WAIT_STATUS_INTERVAL == 0:
                    logger.info(
                        "   〰️ 장 반응 대기 중: 선형 카운트다운이 아니라 최대 홀드 상한입니다. left=%d분 %d초",
                        remaining // 60,
                        remaining % 60,
                    )
                if remaining > 0 and stop_wait % REFLEX_CHECK_INTERVAL == 0:
                    reflex = evaluate_reflex_gate(
                        field_sensor=field_sensor,
                        watch_paths=reflex_watch_paths,
                        watch_baseline=reflex_baseline,
                        last_action=action,
                        elapsed=stop_wait,
                        remaining=remaining,
                    )
                    if reflex.get("wake"):
                        logger.info(
                            "   ⚡ [REFLEX_WAKE] reason=%s salience=%.2f remaining=%d분 %d초 changed=%s",
                            reflex.get("reason", ""),
                            float(reflex.get("salience", 0.0) or 0.0),
                            remaining // 60,
                            remaining % 60,
                            ",".join(Path(p).name for p in reflex.get("changed", [])[:3]),
                        )
                        break
            
            # 4. 자가 갱신 체크 (Self-Reload Check)
            # core 폴더 내 파일 변경 감지 시 종료 (bat 파일이 재시작함)
            changed = False
            for f in core_dir.glob("*.py"):
                mtime = f.stat().st_mtime
                if mtime > last_mtime.get(f, 0):
                    logger.warning(f"♻️ [SELF_RELOAD] 코드 변경 감지: {f.name}. 위상 재정렬을 위해 재시작합니다.")
                    changed = True
                    break
            if changed: break

            error_count = 0
        except KeyboardInterrupt:
            logger.info("⌨️ 수동 중단")
            break
        except Exception as e:
            error_count += 1
            logger.error(f"❌ 오류 ({error_count}/{MAX_ERRORS}): {e}")
            logger.error(traceback.format_exc())

            sleep_sec = MIN_SLEEP * (2 ** min(error_count, 6))
            if error_count >= MAX_ERRORS:
                sleep_sec = MAX_SLEEP
                logger.warning(f"⚠️ 연속 오류 — {MAX_SLEEP//60}분 휴식")
                error_count = 0

            stop_wait = 0
            while stop_wait < sleep_sec:
                if should_stop():
                    logger.info("🛑 중단 파일 감지 — 데몬 종료")
                    return
                time.sleep(1)
                stop_wait += 1
    
    logger.info(f"데몬 종료 — 총 {run_count}회 실행")


if __name__ == "__main__":
    main()
