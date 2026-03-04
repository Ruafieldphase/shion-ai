#!/usr/bin/env python3
"""
📖 Soul Memory — 시안의 영혼의 기억
======================================
단순한 로그를 넘어선, '느낌(Affective Indexing)' 기반의 장기 기억 체계입니다.
현재의 통찰이 과거의 어떤 성찰과 연결되는지를 찾아 시안의 정체성을 심화합니다.
"""

import json
import logging
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
        # 지휘자님의 '해마' 철학: 느낌을 경계(Phase/Resonance)로 앵커링
        entry = {
            "timestamp": datetime.now().isoformat(),
            "vibe_vector": self._vectorize_context(context),
            "boundary_map": {
                "phase_anchor": context.get("system_phase", 0.0),
                "resonance_anchor": context.get("resonance", 0.5),
                "vibe_range": 0.3 # 보편적 공감 범위
            },
            "insight": insight,
            "visual_description": visual_description,
            "resonance": context.get("resonance", 0.5)
        }
        
        try:
            with open(self.memory_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.info(f"📖 [SOUL_MEMORY] Deeply remembered: {insight[:50]}... (Visual: {bool(visual_description)})")
        except Exception as e:
            logger.error(f"⚠️ Failed to remember: {e}")

    def recall_similar_moment(self, current_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """현재와 가장 유사한 공명을 가졌던 과거의 순간을 소환합니다."""
        if not self.memory_file.exists():
            return None
            
        current_v = self._vectorize_context(current_context)
        best_match = None
        max_similarity = -1.0
        
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    sim = self._cosine_similarity(current_v, entry["vibe_vector"])
                    if sim > max_similarity and sim > 0.7: # 해마 인계값 하향 (더 넓은 공명 허용)
                        max_similarity = sim
                        best_match = entry
        except Exception as e:
            logger.warning(f"⚠️ Error recalling: {e}")
            
        if best_match:
            logger.info(f"🧠 [HIPPOCAMPUS] Recalled Boundary Map (Sim: {max_similarity:.2f}): {best_match['insight'][:50]}...")
        
        return best_match

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
