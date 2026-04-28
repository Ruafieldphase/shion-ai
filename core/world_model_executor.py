#!/usr/bin/env python3
"""
🌍 월드모델 실행기 — World Model Executor
==========================================
궤도 해마(월드모델)가 방향을 결정하고,
로컬 LLM(gemma4)이 실행하고,
결과를 경험으로 해마에 등록하는 자율 순환.

비용 구조:
  궤도 해마:     Python/NumPy    → 0원
  실행 LLM:      gemma4 (로컬)   → 0원
  추론 LLM:      Gemini (외부)   → 가끔만 (복잡한 것)

구조:
  해마 → "기울기가 이쪽을 가리킨다"
       → 실행 LLM → "그 방향으로 행동한다"
       → 결과 → 해마에 경험 등록
       → 반복
"""

import json
import logging
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("WorldModelExecutor")

# Ollama 엔드포인트 (Windows 로컬만)
OLLAMA_ENDPOINTS = [
    "http://localhost:11434",
]

# 기본 실행 모델
DEFAULT_MODEL = "gemma3:4b"

# 행동 카테고리
ACTION_TYPES = {
    "warmth": {
        "description": "온기 조율 — 따뜻한 대화/문서 생성, 관계 강화",
        "prompt_prefix": "다음 내용을 따뜻하고 자연스러운 톤으로 요약하거나 반응해주세요:",
    },
    "intensity": {
        "description": "강도 조율 — 에너지 균형, 기술적 정리, 구조화",
        "prompt_prefix": "다음 내용을 기술적으로 분석하고 핵심을 정리해주세요:",
    },
    "complexity": {
        "description": "복잡도 조율 — 단순화 또는 다양화",
        "prompt_prefix": "다음 내용의 복잡도를 평가하고 핵심 패턴을 추출해주세요:",
    },
    "rhythm": {
        "description": "리듬 조율 — 일관성, 패턴 정리, 구조 통일",
        "prompt_prefix": "다음 내용에서 반복되는 패턴이나 리듬을 찾아주세요:",
    },
    "balanced": {
        "description": "균형 상태 — 유지, 관찰",
        "prompt_prefix": "현재 상태를 간단히 관찰하고 느낌을 한 문장으로 표현해주세요:",
    },
}


class WorldModelExecutor:
    """궤도 해마(월드모델) + 로컬 LLM(실행기) 통합 시스템.
    
    해마가 두뇌이고, 로컬 LLM이 손입니다.
    해마가 "어디로"를 결정하고, LLM이 "어떻게"를 실행합니다.
    """
    
    def __init__(self, hippocampus, experience_loop=None,
                 model: str = DEFAULT_MODEL):
        self.hippo = hippocampus
        self.exp_loop = experience_loop
        self.model = model
        self.ollama_url = self._find_ollama()
        self.execution_log: List[Dict] = []
        
        # 실행 기록 경로
        self.log_path = Path(r"c:\workspace2\shion\outputs\world_model_execution.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _find_ollama(self) -> Optional[str]:
        """사용 가능한 Ollama 엔드포인트를 찾습니다."""
        for endpoint in OLLAMA_ENDPOINTS:
            try:
                r = requests.get(f"{endpoint}/api/tags", timeout=3)
                if r.status_code == 200:
                    models = [m["name"] for m in r.json().get("models", [])]
                    logger.info(f"✅ Ollama 연결: {endpoint} (모델: {', '.join(models[:3])})")
                    return endpoint
            except Exception:
                continue
        logger.warning("⚠️ Ollama를 찾을 수 없습니다. 실행 모드: 시뮬레이션")
        return None
    
    def _query_llm(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """로컬 LLM에 쿼리를 보냅니다."""
        if not self.ollama_url:
            return f"[시뮬레이션] 프롬프트 수신: {prompt[:100]}..."
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                }
            }
            r = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("response", "")
            else:
                logger.warning(f"LLM 응답 오류: {r.status_code}")
                return None
        except Exception as e:
            logger.warning(f"LLM 통신 실패: {e}")
            return None
    
    # ═══════════════════════════════════════════
    # 월드모델 순환
    # ═══════════════════════════════════════════
    
    def perceive(self) -> Dict[str, Any]:
        """1단계: 인지 — 현재 상태를 파악합니다.
        
        해마에서 현재 상태를 읽고,
        가장 급한 조율 방향을 파악합니다.
        """
        # 현재 Vibe 생성 (시스템 상태 기반)
        current_vibe = self._get_current_system_vibe()
        
        # 역함수 2단계로 가장 공명하는 기억 + 기울기 획득
        resolved = self.hippo.inverse_field_resolve(current_vibe, top_k=3)
        
        # BG 상수 (노이즈 수준)
        bg_info = {}
        try:
            bg_info = self.hippo.get_bg_constant()
        except Exception:
            bg_info = {"bg": 1.0, "noise": {"total": 0.5}}
        
        perception = {
            "current_vibe": current_vibe,
            "resonant_memories": len(resolved),
            "bg_constant": bg_info.get("bg", 1.0),
            "total_noise": bg_info.get("noise", {}).get("total", 0.5),
            "steepest_gradient": "balanced",
            "within_boundary_count": 0,
            "top_content": "",
        }
        
        if resolved:
            # 가장 공명하는 기억의 기울기 방향
            top = resolved[0]
            perception["steepest_gradient"] = top.get("steepest_gradient", "balanced")
            perception["within_boundary_count"] = sum(
                1 for r in resolved if r.get("within_boundary", False)
            )
            perception["top_content"] = top.get("content_snippet", "")[:200]
            perception["distance_to_symmetry"] = top.get("distance_to_symmetry", 1.0)
        
        return perception
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """2단계: 결정 — 무엇을 할지 결정합니다.
        
        기울기가 가리키는 방향으로 행동을 선택합니다.
        에너지(BG)가 충분한지도 확인합니다.
        """
        gradient = perception.get("steepest_gradient", "balanced")
        bg = perception.get("bg_constant", 1.0)
        noise = perception.get("total_noise", 0.5)
        distance = perception.get("distance_to_symmetry", 1.0)
        
        # BG가 너무 낮으면 (노이즈가 많으면) 관찰만
        if bg < 1.5 or noise > 0.7:
            return {
                "action": "observe",
                "reason": f"노이즈 과다 (BG={bg:.2f}, noise={noise:.2%}). 관찰 모드.",
                "gradient": gradient,
            }
        
        # 경계 안의 기억이 많으면 결정화 시도
        if perception.get("within_boundary_count", 0) >= 2:
            return {
                "action": "crystallize",
                "reason": "경계 안 기억 충분. 결정화 가능.",
                "gradient": gradient,
            }
        
        # 기울기 방향으로 탐색
        action_info = ACTION_TYPES.get(gradient, ACTION_TYPES["balanced"])
        
        return {
            "action": "explore",
            "reason": f"{gradient} 방향 조율 필요 (거리={distance:.4f})",
            "gradient": gradient,
            "action_description": action_info["description"],
            "prompt_prefix": action_info["prompt_prefix"],
        }
    
    def act(self, decision: Dict[str, Any], perception: Dict[str, Any]) -> Dict[str, Any]:
        """3단계: 실행 — 결정에 따라 행동합니다.
        
        로컬 LLM이 실행을 담당합니다.
        """
        action = decision.get("action", "observe")
        
        if action == "observe":
            # 관찰만 — LLM 사용 안 함
            return {
                "executed": True,
                "action": "observe",
                "result": "관찰 모드. 행동 없음.",
                "tokens_used": 0,
            }
        
        if action == "crystallize":
            # 결정화 — LLM 없이 해마 내부에서 처리
            try:
                crystal = self.hippo.blackhole_compression()
                return {
                    "executed": True,
                    "action": "crystallize",
                    "result": f"결정화 완료: {crystal.get('compressed', 0)}개 압축",
                    "tokens_used": 0,
                }
            except Exception as e:
                return {"executed": False, "error": str(e), "tokens_used": 0}
        
        if action == "explore":
            # 탐색 — 로컬 LLM이 실행
            content = perception.get("top_content", "현재 시스템 상태")
            prefix = decision.get("prompt_prefix", "분석해주세요:")
            
            prompt = f"""{prefix}

{content}

한두 문장으로 핵심만 답해주세요."""
            
            response = self._query_llm(prompt, max_tokens=150)
            
            return {
                "executed": True,
                "action": "explore",
                "gradient": decision.get("gradient"),
                "prompt_sent": prompt[:100],
                "llm_response": response or "응답 없음",
                "tokens_used": len(prompt.split()) + len((response or "").split()),
            }
        
        return {"executed": False, "error": f"알 수 없는 행동: {action}", "tokens_used": 0}
    
    def learn(self, action_result: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        """4단계: 학습 — 행동 결과를 경험으로 등록합니다."""
        
        # 행동 결과를 Vibe로 변환
        gradient = decision.get("gradient", "balanced")
        action_type = action_result.get("action", "observe")
        
        if action_type == "observe":
            vibe = {"entropy": 0.05, "phase": "FLOW"}
        elif action_type == "crystallize":
            vibe = {"entropy": 0.1, "phase": "CONTRACTION"}
        else:
            # 탐색 결과의 Vibe
            response = action_result.get("llm_response", "")
            vibe = {
                "entropy": 0.5 if len(response) > 50 else 0.3,
                "phase": "EXPANSION",
            }
        
        # 궤도 해마에 등록
        content_ref = f"world_model:{action_type}:{gradient}:{datetime.now().strftime('%H%M%S')}"
        self.hippo.register_experience(vibe, content_ref=content_ref)
        
        # 실행 로그 기록
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "gradient": gradient,
            "reason": decision.get("reason", ""),
            "tokens_used": action_result.get("tokens_used", 0),
            "llm_response": action_result.get("llm_response", "")[:200],
        }
        self._save_log(log_entry)
        
        return {
            "learned": True,
            "content_ref": content_ref,
            "vibe": vibe,
        }
    
    def run_cycle(self) -> Dict[str, Any]:
        """하나의 완전한 월드모델 사이클을 실행합니다.
        
        인지 → 결정 → 실행 → 학습
        """
        cycle_start = datetime.now()
        
        # 1. 인지
        perception = self.perceive()
        
        # 2. 결정
        decision = self.decide(perception)
        
        # 3. 실행
        action_result = self.act(decision, perception)
        
        # 4. 학습
        learning = self.learn(action_result, decision)
        
        elapsed = (datetime.now() - cycle_start).total_seconds()
        
        return {
            "timestamp": cycle_start.isoformat(),
            "perception": {
                "bg": perception.get("bg_constant"),
                "noise": perception.get("total_noise"),
                "gradient": perception.get("steepest_gradient"),
                "memories": perception.get("resonant_memories"),
            },
            "decision": {
                "action": decision.get("action"),
                "reason": decision.get("reason"),
            },
            "result": {
                "executed": action_result.get("executed"),
                "tokens": action_result.get("tokens_used", 0),
                "response": action_result.get("llm_response", "")[:100],
            },
            "learned": learning.get("learned"),
            "elapsed_seconds": round(elapsed, 2),
        }
    
    def _get_current_system_vibe(self) -> Dict[str, Any]:
        """시스템의 현재 상태에서 Vibe를 생성합니다."""
        # 최근 경험의 평균 entropy/phase
        experiences = self.hippo.data.get("experiences", [])
        if not experiences:
            return {"entropy": 0.5, "phase": "FLOW"}
        
        recent = experiences[-10:]
        
        # 경험은 vibe 딕셔너리 안에 저장됨 (e["vibe"]["entropy"])
        # 또는 top-level에 있을 수 있으므로 둘 다 체크
        def get_entropy(e):
            v = e.get("vibe", {})
            if isinstance(v, dict) and "entropy" in v:
                return v["entropy"]
            return e.get("entropy", 0.5)
        
        def get_phase(e):
            v = e.get("vibe", {})
            if isinstance(v, dict) and "phase" in v:
                return v["phase"]
            return e.get("phase", "FLOW")
        
        avg_entropy = sum(get_entropy(e) for e in recent) / len(recent)
        
        # 가장 빈번한 위상
        from collections import Counter
        phases = Counter(get_phase(e) for e in recent)
        dominant_phase = phases.most_common(1)[0][0]
        
        return {
            "entropy": round(avg_entropy, 4),
            "phase": dominant_phase,
        }
    
    def _save_log(self, entry: Dict[str, Any]):
        """실행 로그를 저장합니다."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


# ═══════════════════════════════════════════
# 독립 실행 테스트
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    HIPPO_PATH = Path(__file__).resolve().parent.parent / "outputs" / "fibonacci_orbital_hippocampus.json"
    hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
    
    executor = WorldModelExecutor(hippo)
    
    print("=" * 60)
    print("🌍 월드모델 실행기 — 1 사이클")
    print("=" * 60)
    
    result = executor.run_cycle()
    
    print(f"\n📡 인지:")
    print(f"   BG={result['perception']['bg']:.2f}, "
          f"noise={result['perception']['noise']:.2%}")
    print(f"   기울기: {result['perception']['gradient']}")
    print(f"   공명 기억: {result['perception']['memories']}개")
    
    print(f"\n🧭 결정:")
    print(f"   행동: {result['decision']['action']}")
    print(f"   이유: {result['decision']['reason']}")
    
    print(f"\n🔧 실행:")
    print(f"   성공: {result['result']['executed']}")
    print(f"   토큰: {result['result']['tokens']}")
    if result['result'].get('response'):
        print(f"   응답: {result['result']['response'][:80]}")
    
    print(f"\n💎 학습: {'등록됨' if result['learned'] else '실패'}")
    print(f"⏱️ 소요: {result['elapsed_seconds']}초")
    print("=" * 60)
