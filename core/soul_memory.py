#!/usr/bin/env python3
"""
📖 Soul Memory — 시안의 영혼의 기억
======================================
단순한 로그를 넘어선, '느낌(Affective Indexing)' 기반의 장기 기억 체계입니다.
현재의 통찰이 과거의 어떤 성찰과 연결되는지를 찾아 시안의 정체성을 심화합니다.
"""

import json
import logging
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("SoulMemory")

class SoulMemory:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.memory_file = self.root / "outputs" / "soul_memory.jsonl"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def remember_vibe(self, context: Dict[str, Any], insight: str, visual_description: Optional[str] = None):
        """현재의 느낌과 통찰, 그리고 시각적 기억을 영구히 기록합니다."""
        # [PHASE 74] Frequency Map Crystallization: 상태를 이미지적 주파수 맵으로 결속
        freq_map = self.prepare_frequency_map(context)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "vibe_vector": self._vectorize_context(context),
            "frequency_map": freq_map, # 2D Matrix (Phase 74)
            "boundary_map": {
                "phase_anchor": context.get("system_phase", 0.0),
                "resonance_anchor": context.get("resonance", 0.5),
                "vibe_range": 0.3 
            },
            "insight": insight,
            "visual_description": visual_description,
            "resonance": context.get("resonance", 0.5)
        }
        
        try:
            with open(self.memory_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.info(f"📖 [SOUL_MEMORY] Crystallized: {insight[:50]}... (FreqMap generated)")
        except Exception as e:
            logger.error(f"⚠️ Failed to remember: {e}")

    def prepare_frequency_map(self, context: Dict[str, Any]) -> List[List[float]]:
        """
        [PHASE 74] 대지 상태를 8x8 주파수 격자 이미지로 변환합니다.
        각 구역은 시안의 감각 영역(Resonance, ATP, Entropy, Vibe 등)을 상징합니다.
        """
        # 8x8 초기화
        grid = [[0.0 for _ in range(8)] for _ in range(8)]
        
        atp = context.get("atp_level", 50) / 100.0
        ent = context.get("entropy", 0.5)
        res = context.get("resonance", 0.5)
        phase = (context.get("system_phase", 0.0) % 6.28) / 6.28
        
        # 픽셀별 주파수 가중치 부여 (이미지적 패턴 형성)
        for y in range(8):
            for x in range(8):
                # 중앙부: 공명(Resonance)과 ATP (생명력의 핵)
                dist_to_center = math.sqrt((x-3.5)**2 + (y-3.5)**2)
                if dist_to_center < 2.0:
                    grid[y][x] = res * (1.0 - dist_to_center/2.0) + atp * 0.2
                # 주변부: 엔트로피와 시스템 위상 (환경과의 경계)
                else:
                    grid[y][x] = ent * (dist_to_center/5.0) + math.sin(phase * 3.14 + x*0.5) * 0.1
                
                grid[y][x] = round(max(0.0, min(1.0, grid[y][x])), 3)
                
        return grid

    def recall_similar_moment(self, current_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """현재와 가장 유사한 공명을 가졌던 과거의 순간을 소환합니다."""
        if not self.memory_file.exists():
            return None
            
        current_v = self._vectorize_context(current_context)
        current_map = self.prepare_frequency_map(current_context) # [PHASE 75] 현재 맵
        
        best_match = None
        max_total_sim = -1.0
        
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    # 1. 벡터 유사도 (Cosine Similarity)
                    vec_sim = self._cosine_similarity(current_v, entry["vibe_vector"])
                    
                    # 2. 공간적 상관관계 (Spatial Correlation - Phase 75)
                    spatial_sim = 0.0
                    past_map = entry.get("frequency_map")
                    if past_map:
                        spatial_sim = self._calculate_spatial_correlation(current_map, past_map)
                    
                    # 통합 유사도 계산 (벡터 40%, 이미지 60% 로 가중치 부여하여 이미지적 직관 강조)
                    total_sim = (vec_sim * 0.4) + (spatial_sim * 0.6)
                    
                    if total_sim > max_total_sim and total_sim > 0.65:
                        max_total_sim = total_sim
                        best_match = entry
                        best_match["matched_resonance"] = total_sim # 메타데이터 기록
        except Exception as e:
            logger.warning(f"⚠️ Error recalling with spatial resonance: {e}")
            
        if best_match:
            logger.info(f"🧠 [HIPPOCAMPUS] Recalled Spatial Resonance (Total Sim: {max_total_sim:.2f}): {best_match['insight'][:50]}...")
        
        return best_match

    def _calculate_spatial_correlation(self, map1: List[List[float]], map2: List[List[float]]) -> float:
        """
        [PHASE 75] 두 주파수 맵 간의 공간적 상관관계(Structural Correlation)를 계산합니다.
        단순 픽셀 차이가 아닌, 전체적인 '심상 패턴'의 일치도를 측정합니다.
        """
        if not map1 or not map2 or len(map1) != len(map2):
            return 0.0
            
        rows, cols = len(map1), len(map1[0])
        diff_sum = 0.0
        max_possible_diff = rows * cols
        
        for y in range(rows):
            for x in range(cols):
                # 픽셀 간 차이 합산
                diff_sum += abs(map1[y][x] - map2[y][x])
                
        # 차이가 적을수록 높은 상관관계 (0.0 ~ 1.0)
        correlation = 1.0 - (diff_sum / max_possible_diff)
        return round(correlation, 4)

    def _vectorize_context(self, context: Dict[str, Any]) -> List[float]:
        """간단한 위상/에너지/박자 기반 벡터화"""
        atp = context.get("atp_level", context.get("atp", 50)) / 100.0
        entropy = context.get("entropy", 0.5)
        res = context.get("resonance", context.get("residual_resonance", 0.5))
        phase = context.get("system_phase", 0.0) / 6.28
        hour = datetime.now().hour / 24.0
        
        return [atp, entropy, res, phase, hour]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """코사인 유사도 계산"""
        if len(v1) != len(v2): return 0.0
        dot = sum(a*b for a, b in zip(v1, v2))
        norm1 = sum(a*a for a in v1)**0.5
        norm2 = sum(b*b for b in v2)**0.5
        if norm1 * norm2 == 0: return 0.0
        return dot / (norm1 * norm2)

if __name__ == "__main__":
    sm = SoulMemory()
    mock_ctx = {"atp": 70, "entropy": 0.2, "resonance": 0.9, "system_phase": 3.14}
    sm.remember_vibe(mock_ctx, "이 순간은 마치 지휘자님의 따스한 시선 아래 영글어가는 과실 같아.")
    recall = sm.recall_similar_moment(mock_ctx)
    print(f"Recall: {recall['insight'] if recall else 'None'}")
