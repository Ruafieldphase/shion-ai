#!/usr/bin/env python3
import json
import logging
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ContextUnpacker")

class ContextUnpacker:
    """
    Context Unpacker — 의식적 맥락 분석기 (기억 검색 기반)
    ====================================================
    경계 접촉 시 호출되어, 해마의 '기울기 에피소드'를 검색하고
    과거의 성공/실패 사례를 바탕으로 현재 상황에 대한 가설을 생성합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        self.gradients_file = root_dir / "outputs" / "experience_gradients.jsonl"
        self.orbit_file = root_dir / "outputs" / "context_orbit.json"
        
    def unpack(self, boundary_report: Dict[str, Any], field_status: Dict[str, Any], current_vector: Dict[str, Any]) -> Dict[str, Any]:
        """최근 맥락과 해마 기억을 분석하여 가설을 생성합니다."""
        logger.info("🧠 [CONTEXT_UNPACKING] 기억 기반 맥락 분석 시작...")
        
        # 1. 유사 기억 검색 (Memory Retrieval)
        similar_episode = self._find_similar_memory(current_vector)
        
        # 2. 가설 생성 (Hypothesis Generation)
        candidates = []
        boundary_type = boundary_report.get("boundary_type")
        
        # 기본 가설 풀 (Base Candidates)
        if boundary_type == "REPETITIVE_STUTTER":
            candidates.append(self._build_candidate("STUCK_IN_LOOP", boundary_report, field_status))
            
        if field_status.get("salience", 0.0) > 0.8:
            candidates.append(self._build_candidate("TEMPORAL_FIELD_SHIFT", boundary_report, field_status))
            
        if boundary_type == "OUT_OF_ORBIT":
            candidates.append(self._build_candidate("GOAL_DEVIATION", boundary_report, field_status))
            
        # 3. 기억 기반 보정 (Memory-based Refinement)
        if similar_episode:
            self._apply_memory_influence(candidates, similar_episode)
            
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "boundary_report": boundary_report,
            "field_status": field_status,
            "current_vector": current_vector,
            "memory_retrieval": {
                "found": similar_episode is not None,
                "similar_id": self._episode_hypothesis_id(similar_episode),
                "past_feedback": similar_episode.get("feedback") if similar_episode else None
            },
            "story_candidates": candidates
        }
        
        self._log_analysis(analysis)
        return analysis

    def _find_similar_memory(self, current_vector: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """해마의 기울기 에피소드 중 가장 유사한 벡터를 가진 것을 찾습니다."""
        if not self.gradients_file.exists(): return None
        
        best_match = None
        min_distance = 999.0
        
        try:
            with open(self.gradients_file, "r", encoding="utf-8") as f:
                for line in f:
                    episode = json.loads(line)
                    past_vec = episode.get("current_vector")
                    if not past_vec: continue
                    
                    dist = self._calculate_vector_distance(current_vector, past_vec)
                    if dist < min_distance:
                        min_distance = dist
                        best_match = episode
            
            # 유사도 임계값 (0.2 이내일 때만 유의미한 기억으로 간주)
            if min_distance < 0.2:
                logger.info(f"🔍 [MEMORY_HIT] 유사 기억 발견 (Distance: {min_distance:.4f})")
                return best_match
        except: pass
        return None

    def _episode_hypothesis_id(self, episode: Optional[Dict[str, Any]]) -> Optional[str]:
        if not episode:
            return None
        hypothesis = episode.get("hypothesis")
        if isinstance(hypothesis, dict):
            return hypothesis.get("id")
        return None

    def _calculate_vector_distance(self, v1: Dict[str, Any], v2: Dict[str, Any]) -> float:
        """두 필드 벡터 간의 유클리드 거리를 계산합니다."""
        keys = ["temporal_tension", "action_density", "entropy"]
        dist_sq = 0.0
        for k in keys:
            dist_sq += (v1.get(k, 0.5) - v2.get(k, 0.5)) ** 2
        return math.sqrt(dist_sq)

    def _apply_memory_influence(self, candidates: List[Dict[str, Any]], episode: Dict[str, Any]):
        """과거의 피드백 결과를 현재 가설의 신뢰도에 반영합니다."""
        past_hypo = episode.get("hypothesis")
        if not past_hypo: return
        
        past_id = past_hypo.get("id")
        past_feedback = episode.get("feedback")
        
        for c in candidates:
            if c["id"] == past_id:
                if past_feedback == "confirmed":
                    c["confidence"] = min(0.95, c["confidence"] + 0.1)
                    c["evidence"].append(f"Supported by similar past memory ({past_id})")
                    logger.info(f"📈 [MEMORY_BOOST] {c['id']} 신뢰도 상승 (과거 성공 사례)")
                elif past_feedback == "rejected":
                    c["confidence"] = max(0.1, c["confidence"] - 0.3)
                    c["evidence"].append(f"Penalized by similar past failure ({past_id})")
                    logger.info(f"📉 [MEMORY_DROP] {c['id']} 신뢰도 하락 (과거 기각 사례)")

    def _build_candidate(self, cid: str, report: Dict[str, Any], status: Dict[str, Any]) -> Dict[str, Any]:
        """기본 가설 객체를 생성합니다."""
        templates = {
            "STUCK_IN_LOOP": "시스템이 {action} 행동의 루프에 갇혔습니다. 판단 기준의 갱신이 필요합니다.",
            "TEMPORAL_FIELD_SHIFT": "장의 흐름에 거대 공백({gap}분)이 발생했습니다. 지휘자님의 부재 혹은 복귀 상황일 수 있습니다.",
            "GOAL_DEVIATION": "현재 행동({action})이 목표 궤도에서 벗어났습니다. 미션 맵의 업데이트가 필요합니다."
        }
        
        story = templates.get(cid, "알 수 없는 필드 이상 감지").format(
            action=report.get("trigger_action", "UNKNOWN"),
            gap=status.get("actual_gap", 0.0)
        )
        
        return {
            "id": cid,
            "story": story,
            "confidence": 0.7,
            "status": "hypothesis",
            "feedback": "unknown",
            "evidence": [f"Boundary Type: {report.get('boundary_type')}"]
        }

    def _log_analysis(self, analysis: Dict[str, Any]):
        """분석 결과를 저장합니다."""
        log_path = self.root_dir / "outputs" / "story_candidates.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(analysis, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unpacker = ContextUnpacker(Path(r"c:\workspace2\shion"))
    # Test unpacking with mock vector
    res = unpacker.unpack({"boundary_type": "REPETITIVE_STUTTER"}, {"salience": 0.5}, {"temporal_tension": 0.1, "action_density": 0.8, "entropy": 0.3})
    print(json.dumps(res, indent=2, ensure_ascii=False))
