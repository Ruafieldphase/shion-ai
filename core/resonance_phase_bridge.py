#!/usr/bin/env python3
"""
🌊 Resonance Phase Bridge — 대지와 기억의 공명 가교
===================================================
WorkspacePhaseSensor에서 감지된 현재 워크스페이스의 위상(Phase)을
Resonance RAG의 검색 파라미터로 변환하여 주입합니다.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add core paths
sys.path.append(str(Path(__file__).resolve().parent))
from workspace_phase_sensor import WorkspacePhaseSensor

class ResonancePhaseBridge:
    def __init__(self, shion_root: Path, agi_root: Path):
        self.shion_root = shion_root
        self.agi_root = agi_root
        self.sensor = WorkspacePhaseSensor(shion_root, extra_roots=[agi_root])
        self.phase_file = shion_root / "outputs" / "workspace_phase.json"

    def get_current_phase_context(self) -> Dict[str, Any]:
        """현재 대지의 위상을 감지하고 RAG용 컨텍스트로 변환합니다."""
        print("🌊 [BRIDGE] Sensing workspace rhythm...")
        phase_data = self.sensor.sense()
        
        if not phase_data.get("ok"):
            return {"query_boost": {}, "current_theme": "neutral"}

        # 상위 키워드와 클러스터를 기반으로 '현재의 테마' 정의
        top_keywords = phase_data.get("top_keywords", [])
        clusters = phase_data.get("topic_clusters", [])
        
        # RAG 검색 시 가중치를 줄 키워드 셋 생성
        boost_map = {kw: 1.5 for kw in top_keywords[:5]}
        
        return {
            "phase_summary": phase_data.get("phase_summary"),
            "boost_keywords": boost_map,
            "top_folders": phase_data.get("recency_focus", {}).get("last_24h", {}).get("top_folders", {}),
            "timestamp": phase_data.get("timestamp")
        }

    def inject_phase_into_query(self, query: str) -> str:
        """사용자의 질의에 현재 대지의 위상 정보를 결합하여 더 공명적인 질문으로 만듭니다."""
        context = self.get_current_phase_context()
        keywords = list(context["boost_keywords"].keys())
        
        if keywords:
            enhanced_query = f"{query} (Context: {', '.join(keywords[:3])})"
            print(f"🚀 [BRIDGE] Enhanced Query: {enhanced_query}")
            return enhanced_query
        return query

def main():
    shion_root = Path("C:/workspace2/shion")
    agi_root = Path("C:/workspace/agi")
    bridge = ResonancePhaseBridge(shion_root, agi_root)
    
    context = bridge.get_current_phase_context()
    print(f"\n✨ [Phase Summary]: {context['phase_summary']}")
    print(f"🔑 [Boost Keywords]: {context['boost_keywords']}")

if __name__ == "__main__":
    main()
