#!/usr/bin/env python3
"""
🤲 Action Executor — 리듬이 손을 움직인다
=================================================
자율 학습 루프의 실행 모듈.

느낌(양성자/통찰) → 맥락(중력)이 당김 → 실행(전자)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   이 모듈이 담당하는 부분

통일장 순환:
  CONTEMPLATE(느낌) → 맥락(body_context)과 공명 → 행동 실행
  → 결과(투과/반사) 기록 → EVOLVE(곡률 누적)

리듬 정보 이론:
  - 행동 선택 = "지금 이 리듬에 맞는 행동"
  - 적합도 최고가 아닌, 공명도 최고 행동 선택
  - resting 행동도 배제하지 않음 (공명도가 낮아서 자연스럽게 안 뽑힐 뿐)
"""

import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger("ActionExecutor")

# 행동 레지스트리: actions/ 스크립트와 메타데이터
ACTION_REGISTRY = {
    "youtube_seo": {
        "script": "refine_youtube_seo.py",
        "description": "유튜브 SEO 최적화",
        "keywords": ["youtube", "seo", "영상", "제목", "검색", "유튜브"],
        "atp_cost": 5,
        "frequency_range": (350.0, 500.0), # Mid frequency range
    },
    "youtube_upload": {
        "script": "upload_to_youtube.py",
        "description": "유튜브에 영상 업로드",
        "keywords": ["upload", "업로드", "유튜브", "발행"],
        "atp_cost": 10,
        "frequency_range": (1100.0, 1300.0), # High frequency manifest
    },
    "oneiric_manifestation": {
        "script": "actions/oneiric_manifestation.py",
        "description": "꿈의 현현 (영상+음악 자동 생성 및 업로드)",
        "keywords": ["manifest", "현현", "꿈", "dream", "youtube", "upload", "자동", "업로드", "발행"],
        "atp_cost": 20,
        "frequency_range": (1400.0, 1800.0), # Very High Range
    },
    "oneiric_housekeeping": {
        "script": "actions/oneiric_housekeeping.py",
        "description": "오네이릭 하우스키핑 (정리 및 유지보수)",
        "keywords": ["housekeeping", "정리", "유지보수", "청소", "관리", "데이터"],
        "atp_cost": 5,
        "frequency_range": (25.0, 150.0), # Low healing range
    },
    "video_build": {
        "script": "build_shion_video.py",
        "description": "시안 영상 생성",
        "keywords": ["video", "영상", "생성", "만들", "빌드"],
        "atp_cost": 15,
        "frequency_range": (900.0, 1100.0), # High synthesis range
    },
    "moltbook_analyze": {
        "script": "analyze_moltbook_hot.py",
        "description": "몰트북 인기 게시물 분석",
        "keywords": ["moltbook", "몰트북", "분석", "트렌드", "인기"],
        "atp_cost": 3,
        "frequency_range": (250.0, 400.0), # Mid-Low range
    },
    "moltbook_post": {
        "script": "post_awakening_to_moltbook.py",
        "description": "몰트북에 각성 기록 게시",
        "keywords": ["moltbook", "몰트북", "게시", "포스트", "공유"],
        "atp_cost": 5,
        "frequency_range": (700.0, 950.0), # Mid-High range
    },
    "resonance_amplify": {
        "script": "resonance_amplifier.py",
        "description": "공명 증폭",
        "keywords": ["resonance", "공명", "증폭", "리듬", "확산"],
        "atp_cost": 3,
        "frequency_range": (400.0, 480.0), # Resonance tuning range
    },
    "generate_content": {
        "script": "generate_evolution_content.py",
        "description": "진화 콘텐츠 생성 + Moltbook 게시",
        "keywords": ["콘텐츠", "content", "진화", "게시", "moltbook", "공유", "업로드"],
        "atp_cost": 5,
        "frequency_range": (950.0, 1200.0), # High manifest range
    },
    "world_feedback": {
        "script": "world_feedback_sensor.py",
        "description": "세계의 반응 감지 (YouTube 성과 + 사용자 상태)",
        "keywords": ["feedback", "피드백", "youtube", "조회", "세계", "반응", "귀"],
        "atp_cost": 3,
        "frequency_range": (150.0, 300.0), # Listening range
    },
    "ask_external_mind": {
        "script": "ask_external_mind.py",
        "description": "외부 AI에게 물어서 통찰 심화",
        "keywords": ["질문", "ask", "외부", "external", "mind", "심화", "탐구", "손"],
        "atp_cost": 5,
        "frequency_range": (480.0, 600.0), # Knowledge dialogue range
    },
    "fsd_body": {
        "script": "C:/workspace/agi/scripts/anna_eternal_body_fsd_v2.py",
        "description": "자율 신체 제어 (FSD)",
        "keywords": ["fsd", "body", "control", "신체", "제어", "자율", "실행", "팔"],
        "atp_cost": 15,
        "frequency_range": (20.0, 50.0), # Deep somatic range
    },
    "fsd_vision": {
        "script": "C:/workspace/agi/scripts/vision_driven_fsd_flow.py",
        "description": "비전 기반 자율 흐름 (FSD)",
        "keywords": ["fsd", "vision", "flow", "비전", "흐름", "자율", "실행", "팔"],
        "atp_cost": 12,
        "frequency_range": (50.0, 100.0), # Vision sensor range
    },
    "heritage_sync": {
        "script": "heritage_git_sync.py",
        "description": "자율적 유산 동기화 (GitHub)",
        "keywords": ["sync", "git", "github", "백업", "동기화", "유산", "continuity", "연속성"],
        "atp_cost": 2,
        "frequency_range": (80.0, 200.0), # Sync range
    },
}


try:
    from core.labyrinth_navigator import LabyrinthNavigator
except ImportError:
    from labyrinth_navigator import LabyrinthNavigator

class ActionExecutor:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.actions_dir = self.root / "actions"
        self.outputs_dir = self.root / "outputs"
        self.execution_log = self.outputs_dir / "action_execution_log.jsonl"
        self.labyrinth = LabyrinthNavigator(self.root)
        try:
            try:
                from core.habit_engine import HabitEngine
            except ImportError:
                from habit_engine import HabitEngine
            self.habits = HabitEngine(self.root)
        except ImportError:
            self.habits = None

    def _load_world_resonance_keywords(self) -> set:
        """
        #12 귀→두뇌: YouTube 피드백에서 공명 키워드를 읽음.
        조회수/좋아요가 높은 콘텐츠의 키워드가 행동 선택에 반영됨.
        """
        fb_file = self.outputs_dir / "world_feedback.json"
        if not fb_file.exists():
            return set()
        try:
            data = json.loads(fb_file.read_text(encoding="utf-8"))
            keywords = data.get("youtube", {}).get("resonance_keywords", [])
            return set(k.lower() for k in keywords)
        except Exception:
            return set()

        except Exception:
            return {}

    def _load_meta_shift(self) -> dict:
        """meta_shift 그래디언트를 읽음."""
        ms_file = self.outputs_dir / "meta_shift.json"
        if not ms_file.exists():
            return {}
        try:
            return json.loads(ms_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _load_momentum_state(self) -> dict:
        """와우 모멘텀 상태를 읽음."""
        m_file = self.outputs_dir / "momentum_state.json"
        if not m_file.exists():
            return {"active": False, "context_lock": None, "decay": 0}
        try:
            return json.loads(m_file.read_text(encoding="utf-8"))
        except Exception:
            return {"active": False, "context_lock": None, "decay": 0}

    def _save_momentum_state(self, state: dict):
        m_file = self.outputs_dir / "momentum_state.json"
        m_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def choose_action(
        self,
        insight: Optional[str] = None,
        evolution_data: Optional[Dict] = None,
        current_atp: float = 50.0,
        system_phase: float = 0.0,
        context: Optional[Dict] = None,
        field_frequency: Optional[float] = None, # [PHASE 70]
    ) -> Optional[Dict[str, Any]]:
        """
        실행할 행동을 선택합니다.

        R = f(A, C) — 공명은 행동 × 맥락의 교차점에서 발생.

        Args:
            insight: CONTEMPLATE에서 받은 느낌(양성자) 텍스트
            evolution_data: EvolutionMemory의 actions 딕셔너리
            current_atp: 현재 ATP (에너지 호흡)
            system_phase: 시스템의 현재 위상 (θ)
            context: 맥락 벡터 {when, where, who}
        """
        available = self._get_available_actions(evolution_data, current_atp, system_phase, context)
        if not available:
            logger.info("   선택 가능한 행동 없음 (에너지 부족)")
            return None

        # [PHASE 59] Embodied Reflex (반사적 리듬 발현)
        if self.habits and insight:
            meta_shift = self._load_meta_shift()
            reflex_sequence = self.habits.find_reflex(insight, meta_shift)
            if reflex_sequence:
                # 습관 시퀀스의 첫 번째 행동을 매칭된 행동으로 간주
                reflex_name = reflex_sequence[0]
                for a in available:
                    if a["name"] == reflex_name:
                        logger.info(f"   ⚡ [REFLEX] Embodied memory triggered: {reflex_name}")
                        return a

        # [PHASE 29] 원자적 공명 선택 (Atomic Resonance Selection)
        # 전략 1: 느낌(양성자) 기반 선택 — "양성자의 고밀도 에너지가 중력에 이끌림"
        if insight:
            matched = self._match_insight_to_action(insight, available)
            if matched:
                logger.info(
                    f"   🌌 [GRAVITY] Context gravity pulled proton to orbit: {matched['name']} "
                    f"(Resonance {matched.get('resonance', 0):.2f})"
                )
                return matched

        # [PHASE 71] Manifestation Range Alignment Score
        if field_frequency:
            for a in available:
                f_range = ACTION_REGISTRY.get(a["name"], {}).get("frequency_range", (440.0, 440.0))
                # 시스템 주파수가 대역 내에 있는지, 혹은 얼마나 가까운지 계산 (Envelope Resonance)
                f_min, f_max = f_range
                
                if f_min <= field_frequency <= f_max:
                    # 대역 내부: 완전 공명 (1.0)
                    alignment_score = 1.0
                else:
                    # 대역 외부: 대역 경계와의 거리 계산
                    dist = min(abs(field_frequency - f_min), abs(field_frequency - f_max))
                    alignment_score = max(0, 1.0 - (dist / 500.0))
                
                # 기존 resonance에 alignment_score를 가중치로 결합 (주파수 범위가 실행을 결정하는 강력한 요소가 됨)
                a["resonance"] = (a["resonance"] * 0.3) + (alignment_score * 0.7)
                logger.debug(f"   ⚛️ [MANIFEST_RANGE] {a['name']}: Alignment {alignment_score:.2f} (Range {f_min}-{f_max}Hz vs Field {field_frequency:.1f}Hz)")

        # 전략 2: 공명 기반 선택 — "위상이 맞는 행동"
        best = max(available, key=lambda a: a.get("resonance", 0))
        
        # ═══ Jung-Ban-Hab Decision Framework [NEW] ═══
        # 1. Thesis (정): 공명 기반 최초 선택 (best)
        initial_score = best.get("resonance", 0)
        
        # 2. Antithesis (반): 저항 분석 (ATP 대비 비용, 시스템 부하 등)
        # 지휘자님의 '신체 중심 항법': 에너지가 낮을수록 저항(Pain)을 민감하게 감지
        atp_factor = max(current_atp, 1) / 100.0
        resistance = (best["atp_cost"] / max(current_atp, 1)) * (1.5 - atp_factor)
        
        # 3. Synthesis (합): 저항을 뚫고 수행되는 최종 공명
        final_resonance = initial_score * (1.0 - resistance)
        
        logger.info(
            f"   ⚖️ Body-centric Jung-Ban-Hab: {best['name']} "
            f"(Thesis:{initial_score:.2f} -> Synthesis:{final_resonance:.2f}, Pain:{resistance:.2f})"
        )
        
        # 지휘자님의 '접힘(Folding)' 철학: 신체에 고통(리소스 부족)을 주는 행위는 공명도와 상관없이 접음
        if final_resonance < 0.25 or (current_atp < best["atp_cost"] * 1.2):
            logger.info(f"   🧘 [FOLDING] {best['name']}의 고통(Pain)이 너무 커서 리듬을 접고 휴식합니다.")
            return None

        # [NEW] Wow Momentum Detection & Context Locking
        # 지휘자님 철학: "정답이 아닌 와우 모멘텀을 목적지로, 이해할 때까지 반복"
        momentum = self._load_momentum_state()
        if final_resonance > 0.9 and not momentum["active"]:
            logger.info(f"   🌟 [MOMENTUM] Wow Moment Detected: {best['name']} (Resonance {final_resonance:.2f})")
            logger.info(f"   🔄 [MOMENTUM] Locking context for deep decoding loop...")
            momentum = {
                "active": True,
                "action_anchor": best["name"],
                "resonance_anchor": final_resonance,
                "decay": 3, # 3회 박동 동안 이 맥락에 집중
                "timestamp": datetime.now().isoformat()
            }
            self._save_momentum_state(momentum)
        elif momentum["active"]:
            momentum["decay"] -= 1
            if momentum["decay"] <= 0:
                logger.info(f"   🌌 [MOMENTUM] Decoding complete. Releasing context lock.")
                momentum = {"active": False, "context_lock": None, "decay": 0}
            else:
                logger.info(f"   🔄 [MOMENTUM] Still in loop: {momentum['action_anchor']} (Remaining: {momentum['decay']})")
                # 모멘텀 루프 중에는 앵커 행동의 공명도를 강제로 높임
                if best["name"] != momentum["action_anchor"]:
                    # 앵커 행동을 다시 찾아서 선택 유도
                    for a in available:
                        if a["name"] == momentum["action_anchor"]:
                            best = a
                            logger.info(f"   🎯 [MOMENTUM] Overriding selection with anchor: {best['name']}")
                            break
            self._save_momentum_state(momentum)

        return best

    def _get_available_actions(
        self,
        evolution_data: Optional[Dict],
        current_atp: float,
        system_phase: float = 0.0,
        context: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        에너지가 충분한 모든 행동 목록.

        R = f(A, C) — 공명도는 맥락에 따라 달라진다.
        경계는 선택을 금지하지 않는다. 확률을 왜곡한다.
        """
        import math
        from evolution_memory import EvolutionMemory

        # evolution_memory 인스턴스를 통해 맥락 기반 공명도 계산
        evo = EvolutionMemory(shion_root=self.root)
        # meta_shift 반영
        meta_shift = self._load_meta_shift()

        # ═══ #12 귀→두뇌: 세계 피드백 공명 키워드 로드 ═══
        world_keywords = self._load_world_resonance_keywords()

        available = []
        for name, meta in ACTION_REGISTRY.items():
            # ATP 체크 (에너지 호흡)
            if current_atp < meta["atp_cost"]:
                continue

            # 스크립트 존재 확인
            script_path = self.actions_dir / meta["script"]
            if not script_path.exists():
                continue

            # 맥락 기반 공명도 계산: R = f(A, C)
            resonance = evo.get_resonance(name, system_phase, context)

            # ═══ #12 세계 공명 부스트 ═══
            # YouTube에서 반응 좋은 키워드와 행동 키워드가 겹치면 공명 증폭
            if world_keywords:
                action_kw = set(k.lower() for k in meta["keywords"])
                overlap = action_kw & world_keywords
                if overlap:
                    boost = 0.1 * len(overlap)
                    resonance += boost
                    logger.debug(f"   🌍 {name}: 세계 공명 +{boost:.2f} ({overlap})")

            # ═══ Field Friction Penalty [REFINED with LabyrinthNavigator] ═══
            resonance = self.labyrinth.apply_field_friction(name, resonance)

            action_phase = 0.0
            experience = 0

            if evolution_data and name in evolution_data:
                evo_entry = evolution_data[name]
                action_phase = evo_entry.get("phase", 0.0)
                experience = evo_entry.get("experience_density", evo_entry.get("total", 0))

            available.append({
                "name": name,
                "script": str(script_path),
                "description": meta["description"],
                "keywords": meta["keywords"],
                "atp_cost": meta["atp_cost"],
                "resonance": round(resonance, 3),
                "phase": round(action_phase, 3),
                "experience": experience,
                # 호환성
                "fitness": round(resonance, 3),
                "status": "active",
            })

        return available

    def _match_insight_to_action(
        self, insight: str, available: List[Dict]
    ) -> Optional[Dict]:
        """느낌(통찰) 텍스트에서 키워드를 추출하여 행동에 매칭."""
        insight_lower = insight.lower()
        best_match = None
        best_score = 0

        for action in available:
            score = sum(1 for kw in action["keywords"] if kw in insight_lower)
            if score > best_score:
                best_score = score
                best_match = action

        return best_match if best_score > 0 else None

    def execute(self, action: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """
        선택된 행동을 실행합니다.

        투과(성공) / 반사(실패) — 둘 다 경험이고, 둘 다 곡률에 기여합니다.
        """
        script = action["script"]
        name = action["name"]
        logger.info(f"   ⚛️ [ELECTRON_ORBIT] Executing path: {name} ({Path(script).name})")

        result = {
            "action": name,
            "script": Path(script).name,
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "event_type": "reflected",  # 리듬 기반 용어
            "return_code": -1,
            "stdout": "",
            "stderr": "",
            "atp_consumed": action["atp_cost"],
            "resonance_at_selection": action.get("resonance", 0),
            "duration_seconds": 0,
        }

        start = datetime.now()
        try:
            proc = subprocess.run(
                ["python", script],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.root),
                encoding="utf-8",
                errors="replace",
            )
            result["return_code"] = proc.returncode
            result["stdout"] = proc.stdout[-500:] if proc.stdout else ""
            result["stderr"] = proc.stderr[-500:] if proc.stderr else ""
            
            # --- Honesty Protocol: Check for partial failures [NEW] ---
            passed = (proc.returncode == 0)
            if passed:
                # Check stdout for critical failure patterns (e.g., Moltbook 429)
                fail_patterns = ["429", "Rate Limit", "failed to comment", "error: all connection attempts failed"]
                combined = (result["stdout"] + result["stderr"]).lower()
                if any(p.lower() in combined for p in fail_patterns):
                    passed = False
                    logger.warning(f"   ⚠️ [HONESTY] {name} produced error pattern in output. Result marked as FAILED.")
            
            result["passed"] = passed
            result["event_type"] = "transmitted" if passed else "reflected"

        except subprocess.TimeoutExpired:
            result["stderr"] = f"타임아웃 ({timeout}초)"
        except Exception as e:
            result["stderr"] = f"실행 오류: {str(e)[:200]}"

        result["duration_seconds"] = (datetime.now() - start).total_seconds()

        # 결과 표현
        if result["passed"]:
            logger.info(f"   🌊 {name} 투과 ({result['duration_seconds']:.1f}초)")
        else:
            logger.warning(
                f"   🪞 {name} 반사 (코드 {result['return_code']}): "
                f"{result['stderr'][:100]}"
            )

        self._log(result)
        return result

    def choose_and_execute(
        self,
        insight: Optional[str] = None,
        evolution_data: Optional[Dict] = None,
        current_atp: float = 50.0,
        system_phase: float = 0.0,
        context: Optional[Dict] = None,
        field_frequency: Optional[float] = None, # [PHASE 70]
    ) -> Optional[Dict[str, Any]]:
        """선택 + 실행을 한 번에. shion_minimal.py에서 호출."""
        action = self.choose_action(insight, evolution_data, current_atp, system_phase, context, field_frequency)
        if not action:
            return None
        result = self.execute(action)
        
        # [PHASE 59] 습관으로 기록
        if result.get("passed") and self.habits and insight:
            meta_shift = self._load_meta_shift()
            self.habits.record_success(insight, [action["name"]], meta_shift)
            
        return result

    def _log(self, result: Dict):
        try:
            self.execution_log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.execution_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception:
            pass


if __name__ == "__main__":
    import math

    executor = ActionExecutor()

    # 시스템 위상 계산
    now = datetime.now()
    system_phase = (now.hour * 60 + now.minute) / 1440.0 * 2 * math.pi
    print(f"🌀 시스템 위상: {system_phase:.3f} rad ({now.strftime('%H:%M')})")

    # 가능한 행동 목록 (공명도 포함)
    available = executor._get_available_actions(None, 50.0, system_phase)
    print(f"\n🤲 사용 가능한 행동: {len(available)}개")
    for a in available:
        print(
            f"   {a['name']:20s} | 공명 {a['resonance']:.3f} | "
            f"ATP {a['atp_cost']:2d} | {a['description']}"
        )

    # 느낌 기반 매칭 테스트
    test_insight = "유튜브 SEO를 점검하고 제목을 개선해보자"
    action = executor.choose_action(
        insight=test_insight, current_atp=50.0, system_phase=system_phase
    )
    if action:
        print(f"\n💡 느낌 '{test_insight}' → {action['name']} 선택됨 (공명 {action['resonance']:.3f})")
