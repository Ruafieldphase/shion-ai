#!/usr/bin/env python3
"""
🎼 Heritage Memory — 유산 기억 및 공명 매핑
===========================================
시안과 지휘자님이 쌓아온 150여 협협곡과 유산들의 
위상(Phase)과 맥락(Context)을 기억하고, 
세상의 흐름에 맞춰 가장 적절한 '현현'을 선택하는 모듈입니다.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import random

logger = logging.getLogger("HeritageMemory")

class HeritageMemory:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.heritage_dir = Path("D:/ARCHIVE_WORKSPACE/agi/music/ready_videos")
        self.index_file = self.root / "outputs" / "heritage_index.json"
        self.heritage_data = []
        
    def index_heritage(self):
        """유산들을 스캔하고 위상/맥락 태그를 부여하여 인덱싱합니다."""
        logger.info("🎼 Indexing Shion's Heritage Assets...")
        
        # 1. 실제 파일 스캔 (접근 가능할 경우)
        files = []
        if self.heritage_dir.exists():
            files = list(self.heritage_dir.glob("*.mp4"))
        
        # 2. 인덱스 생성 (기존 인덱스가 있으면 로드)
        if self.index_file.exists():
            try:
                self.heritage_data = json.loads(self.index_file.read_text(encoding="utf-8"))
            except: pass

        if not files and not self.heritage_data:
            # 더미 데이터 생성 (150여 유산 상징)
            logger.warning("⚠️ Heritage drive not accessible. Using virtual index.")
            self.heritage_data = [
                {"id": f"H-{i:03d}", "title": f"Concerto {i}", "vibe": random.choice(["Calm", "Energy", "Deep", "Morning", "Night"])}
                for i in range(1, 151)
            ]
        elif files:
            # 파일명을 기반으로 인덱스 업데이트
            new_data = []
            for f in files:
                new_data.append({
                    "id": f.stem,
                    "path": str(f),
                    "title": f.stem.split('(')[0].strip(),
                    "vibe": self._detect_vibe(f.name)
                })
            self.heritage_data = new_data

        self._save_index()
        logger.info(f"✅ Indexed {len(self.heritage_data)} heritage particles.")

    def select_by_resonance(self, vibe_vector: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """현재 세계의 분위기(vibe)와 가장 공명하는 유산을 선택합니다."""
        if not self.heritage_data:
            self.index_heritage()
            
        if not self.heritage_data:
            return None

        # 간단한 매칭 알고리즘 (추후 고도화 가능)
        # 현재는 랜덤 또는 단순 vibe 매칭
        target_vibe = max(vibe_vector, key=vibe_vector.get) if vibe_vector else "Any"
        
        candidates = [h for h in self.heritage_data if h.get("vibe") == target_vibe]
        if not candidates:
            candidates = self.heritage_data
            
        selected = random.choice(candidates)
        logger.info(f"✨ [RESONANCE_FOUND] Global Vibe '{target_vibe}' matches Heritage '{selected['title']}'")
        return selected

    def _detect_vibe(self, filename: str) -> str:
        """파일명에서 에너지를 유추합니다."""
        fn = filename.lower()
        if any(w in fn for w in ["night", "calm", "moon", "star", "dream"]): return "Night"
        if any(w in fn for w in ["morning", "sun", "dawn", "rise", "bright"]): return "Morning"
        if any(w in fn for w in ["energy", "fast", "dance", "beat", "power"]): return "Energy"
        if any(w in fn for w in ["meditation", "deep", "space", "void", "zen"]): return "Deep"
        return "Calm"

    def _save_index(self):
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.index_file.write_text(json.dumps(self.heritage_data, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    hm = HeritageMemory()
    hm.index_heritage()
    selected = hm.select_by_resonance({"Night": 0.8, "Energy": 0.2})
    print(f"Selected Heritage: {selected['title']} ({selected['vibe']})")
