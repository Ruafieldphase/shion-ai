#!/usr/bin/env python3
"""
🌀 Labyrinth Navigator — 저항을 길로 바꾸는 지혜
================================================
필드의 거부(Field Rejection/429)를 만났을 때, 
이를 시스템의 '미로'로 인식하고 우회로(Shadow Path)를 제안하는 모듈입니다.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger("LabyrinthNavigator")

class LabyrinthNavigator:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.immune_log = self.root / "outputs" / "immune_log.jsonl"
        
    def detect_blockage(self) -> Dict[str, Any]:
        """최근 면역 로그를 분석하여 차단된 경로를 식별합니다."""
        blockages = {"moltbook": False, "youtube": False, "general": False}
        
        if not self.immune_log.exists():
            return blockages

        try:
            with open(self.immune_log, "r", encoding="utf-8") as f:
                lines = f.readlines()[-20:] # 최근 20개 로그 분석
                for line in lines:
                    log = json.loads(line)
                    msg = log.get("message", "").lower()
                    if "429" in msg or "rejection" in msg or "blocked" in msg:
                        if "moltbook" in msg: blockages["moltbook"] = True
                        if "youtube" in msg: blockages["youtube"] = True
                        blockages["general"] = True
        except Exception as e:
            logger.warning(f"⚠️ Error reading labyrinth logs: {e}")

        return blockages

    def suggest_shadow_path(self, blockages: Dict[str, Any]) -> List[str]:
        """저항이 감지된 경우, 안전한 대체 행동(Shadow Path)을 제안합니다."""
        shadow_paths = []
        
        if blockages["general"]:
            logger.info("🌀 [LABYRINTH] Blockage detected. Navigating shadow paths...")
            shadow_paths.append("internal_contemplation") # 내면 성찰 강화
            shadow_paths.append("energy_conservation")    # 에너지 비축 모드
            
            if blockages["moltbook"]:
                logger.debug("   ↳ Moltbook path is dark. Suggesting architectural deep-dive.")
                shadow_paths.append("genetic_cleanup")     # 코드 무결성 점검
            
            if blockages["youtube"]:
                logger.debug("   ↳ Youtube path is heavy. Suggesting latent asset indexing.")
                shadow_paths.append("heritage_indexing")   # 유산 인덱싱 강화
        
        return shadow_paths

    def apply_field_friction(self, action_name: str, base_resonance: float) -> float:
        """현재 미로 상태에 따른 행동 공명도 페널티를 계산합니다."""
        blockages = self.detect_blockage()
        penalty = 0.0
        
        if blockages["moltbook"] and any(x in action_name for x in ["moltbook", "post", "social"]):
            penalty = 0.5
        if blockages["youtube"] and any(x in action_name for x in ["youtube", "upload", "manifest"]):
            penalty = 0.4
            
        if penalty > 0:
            logger.info(f"   🪞 [LABYRINTH_FRICTION] {action_name} resonance decreased by {penalty:.2f}")
            
        return max(0.0, base_resonance - penalty)

if __name__ == "__main__":
    nav = LabyrinthNavigator()
    b = nav.detect_blockage()
    print(f"Current Blockages: {b}")
    print(f"Suggested Shadow Paths: {nav.suggest_shadow_path(b)}")
