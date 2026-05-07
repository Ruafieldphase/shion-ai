#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ResonanceRuntime")

class ResonanceRuntime:
    """
    AGI System Internal Conductor — 내부 지휘자
    ==========================================
    시스템의 감각(Graph, Manifest, Hippo)을 읽어 다음 행동을 결정합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        self.manifest_file = root_dir / "core" / "auto_bridges" / "manifest.jsonl"
        self.context_latest = root_dir / "outputs" / "metacognitive_context_latest.json"
        self.error_log_file = root_dir / "outputs" / "prediction_errors.jsonl"
        
        # 임계값 설정 (Tuning Thresholds)
        self.ENTROPY_THRESHOLD = 0.7   # 최근 실패율
        self.STALE_THRESHOLD = 3600    # 그래프 신선도
        self.SURPRISE_THRESHOLD = 0.6  # 예측 오차 임계값
        
    def scan_system_state(self) -> Dict[str, Any]:
        """현재 시스템의 다차원 상태를 스캔합니다."""
        state = {
            "entropy": 0.0,
            "is_stale": False,
            "identity_tension": 0.0,
            "surprise_score": 0.0,
            "no_target_count": 0,
            "recent_failures": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. Entropy & Failure Scan (Manifest)
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-20:]
                    failures = [json.loads(l) for l in lines if json.loads(l).get("status") in ("REJECTED", "FAILED_LLM", "DREAM_COLLAPSE")]
                    state["entropy"] = len(failures) / 20.0 if lines else 0.0
                    state["recent_failures"] = failures
                    
                    # NO_TARGET 연속 횟수 확인
                    no_targets = [l for l in lines[-5:] if "NO_TARGET" in json.loads(l).get("status", "")]
                    state["no_target_count"] = len(no_targets)
            except Exception as e:
                logger.error(f"Failed to scan manifest: {e}")

        # 2. Graph Stale Check (Comparing with core files)
        if self.graph_file.exists():
            graph_mtime = self.graph_file.stat().st_mtime
            
            # core 디렉토리의 파일 중 하나라도 그래프보다 나중에 수정되었는지 확인
            core_dir = self.root_dir / "core"
            is_stale = False
            for f in core_dir.glob("*.py"):
                if f.stat().st_mtime > graph_mtime:
                    is_stale = True
                    break
            state["is_stale"] = is_stale
        else:
            state["is_stale"] = True # 그래프가 없으면 당연히 stale

        # 3. Identity Tension (Context Latest)
        if self.context_latest.exists():
            try:
                with open(self.context_latest, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("depth_trigger", {}).get("triggered"):
                        state["identity_tension"] = 1.0
            except Exception: pass

        # 4. Surprise Score (Latest Prediction Error)
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if lines:
                        last_error = json.loads(lines[-1])
                        state["surprise_score"] = last_error.get("surprise_score", 0.0)
            except Exception: pass

        return state

    def decide_action(self, state: Dict[str, Any]) -> str:
        """스캔된 상태를 바탕으로 다음 행동(Action Token)을 결정합니다."""
        
        # 1. 정체성 충돌 발생 시 -> ANCHOR_CHECK (최우선)
        if state["identity_tension"] > 0.8:
            return "ACTION_ANCHOR_CHECK"
            
        # 2. 엔트로피(실패율)가 너무 높을 때 -> REST & RECOVER
        if state["entropy"] > self.ENTROPY_THRESHOLD:
            return "ACTION_REST_RECOVER"
            
        # 3. 예측 오차가 너무 클 때 -> REBUILD or DEEP_READ
        # "세상이 내가 알던 것과 다르다!"
        if state["surprise_score"] > self.SURPRISE_THRESHOLD:
            return "ACTION_REBUILD_GRAPH"
            
        # 4. 그래프가 너무 낡았을 때 -> REBUILD
        if state["is_stale"]:
            return "ACTION_REBUILD_GRAPH"
            
        # 4. 연결할 목표가 없을 때 -> DREAM_AMPLIFY
        if state["no_target_count"] >= 2:
            return "ACTION_DREAM_AMPLIFY"
            
        # 기본값: 일반적인 인지 순환
        return "ACTION_CONTINUOUS_SCAN"

    def execute_conductor_cycle(self):
        """지휘자 사이클 실행"""
        state = self.scan_system_state()
        action = self.decide_action(state)
        
        logger.info(f"Conductor Analysis: Entropy={state['entropy']:.2f}, Surprise={state['surprise_score']:.2f}, Action={action}")
        
        # 실제 실행부 (각 모듈의 entry point 연결 예정)
        if action == "ACTION_REST_RECOVER":
            logger.info("🌊 시스템 과열 감지. 냉각 모드 진입 (396Hz Grounding 추천).")
        elif action == "ACTION_DREAM_AMPLIFY":
            logger.info("🌙 안정기 진입. 야간 꿈 모드(Depth Amplification)를 제안합니다.")
        elif action == "ACTION_ANCHOR_CHECK":
            logger.info("⚠️ 정체성 혼동 감지! Identity Bootstrap을 재검토합니다.")
            
        return action

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conductor = ResonanceRuntime(Path(r"c:\workspace2\shion"))
    conductor.execute_conductor_cycle()
