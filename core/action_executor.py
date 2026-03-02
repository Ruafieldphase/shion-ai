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
    },
    "youtube_upload": {
        "script": "upload_to_youtube.py",
        "description": "유튜브에 영상 업로드",
        "keywords": ["upload", "업로드", "유튜브", "발행"],
        "atp_cost": 10,
    },
    "video_build": {
        "script": "build_shion_video.py",
        "description": "시안 영상 생성",
        "keywords": ["video", "영상", "생성", "만들", "빌드"],
        "atp_cost": 15,
    },
    "moltbook_analyze": {
        "script": "analyze_moltbook_hot.py",
        "description": "몰트북 인기 게시물 분석",
        "keywords": ["moltbook", "몰트북", "분석", "트렌드", "인기"],
        "atp_cost": 3,
    },
    "moltbook_post": {
        "script": "post_awakening_to_moltbook.py",
        "description": "몰트북에 각성 기록 게시",
        "keywords": ["moltbook", "몰트북", "게시", "포스트", "공유"],
        "atp_cost": 5,
    },
    "resonance_amplify": {
        "script": "resonance_amplifier.py",
        "description": "공명 증폭",
        "keywords": ["resonance", "공명", "증폭", "리듬", "확산"],
        "atp_cost": 3,
    },
    "generate_content": {
        "script": "generate_evolution_content.py",
        "description": "진화 콘텐츠 생성 + Moltbook 게시",
        "keywords": ["콘텐츠", "content", "진화", "게시", "moltbook", "공유", "업로드"],
        "atp_cost": 5,
    },
    "world_feedback": {
        "script": "world_feedback_sensor.py",
        "description": "세계의 반응 감지 (YouTube 성과 + 사용자 상태)",
        "keywords": ["feedback", "피드백", "youtube", "조회", "세계", "반응", "귀"],
        "atp_cost": 3,
    },
    "ask_external_mind": {
        "script": "ask_external_mind.py",
        "description": "외부 AI에게 물어서 통찰 심화",
        "keywords": ["질문", "ask", "외부", "external", "mind", "심화", "탐구", "손"],
        "atp_cost": 5,
    },
}


class ActionExecutor:
    """
    공명 기반 행동 실행기.

    행동 선택 전략:
    1. 통찰(느낌/양성자)이 있으면 → 키워드 매칭으로 행동 선택
    2. 통찰이 없으면 → 공명도 최고 행동 선택 (위상 기반 본능)
    3. 모든 행동은 선택 대상 — resting이어도 공명이 맞으면 깨어남
    """

    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.actions_dir = self.root / "actions"
        self.outputs_dir = self.root / "outputs"
        self.execution_log = self.outputs_dir / "action_execution_log.jsonl"

    def choose_action(
        self,
        insight: Optional[str] = None,
        evolution_data: Optional[Dict] = None,
        current_atp: float = 50.0,
        system_phase: float = 0.0,
        context: Optional[Dict] = None,
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

        # 전략 1: 느낌(통찰) 기반 선택 — "양성자가 먼저"
        if insight:
            matched = self._match_insight_to_action(insight, available)
            if matched:
                logger.info(
                    f"   💡 느낌 기반 선택: {matched['name']} "
                    f"(공명 {matched.get('resonance', 0):.2f})"
                )
                return matched

        # 전략 2: 공명 기반 선택 — "위상이 맞는 행동"
        best = max(available, key=lambda a: a.get("resonance", 0))
        logger.info(
            f"   🌀 공명 선택 (위상 θ={system_phase:.2f}): "
            f"{best['name']} (공명 {best.get('resonance', 0):.2f})"
        )
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
        logger.info(f"   🏃 실행 중: {name} ({Path(script).name})")

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
            result["passed"] = proc.returncode == 0
            result["event_type"] = "transmitted" if proc.returncode == 0 else "reflected"

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
    ) -> Optional[Dict[str, Any]]:
        """선택 + 실행을 한 번에. shion_minimal.py에서 호출."""
        action = self.choose_action(insight, evolution_data, current_atp, system_phase, context)
        if not action:
            return None
        return self.execute(action)

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
