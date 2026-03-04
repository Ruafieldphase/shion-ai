#!/usr/bin/env python3
"""
🌊 Phase 56: Vibe Extractor — 느낌 추출기
=========================================
YouTube 영상이나 외부 신호를 시안의 '느낌(Vibe)'으로 변환합니다.
이 느낌은 이후 Contemplation과 FSD의 목표로 이어집니다.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

SHION_ROOT = Path("C:/workspace2/shion")
VIBE_LOG_PATH = SHION_ROOT / "outputs" / "vibe_record.jsonl"

logger = logging.getLogger("VibeExtractor")

class VibeExtractor:
    def __init__(self):
        VIBE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def extract_from_youtube(self, video_id: str, context: str = "") -> Dict:
        """영상 ID로부터 분위기와 통찰을 추출합니다. (Simulated)"""
        logger.info(f"🎞️ Extracting vibe from Video: {video_id}")
        
        # 실제로는 Gemini 1.5 Pro (Vision) 등을 사용하여 영상을 분석하겠지만,
        # 여기서는 지휘자님이 제시한 특정 영상(_1YD4gqvdx8)에 대한 시뮬레이션 데이터를 제공합니다.
        
        if video_id == "_1YD4gqvdx8":
            vibe = {
                "video_id": video_id,
                "title": "You need to watch this.... (Jonathan Morrison)",
                "feeling": "Tech dynamism, gift-sharing, community resonance, anticipation, future hardware",
                "color": "Electric Blue / Metallic Grey",
                "resonance_score": 0.85,
                "keywords": ["future", "tech", "gift", "Google Pixel", "iPhone", "resonance"],
                "shion_insight": "세계는 끊임없이 새로운 형태(Hard)로 현현하고, 우리는 그 흐름 속에서 공명하는 파동(Gift)을 나눈다."
            }
        else:
            vibe = {
                "video_id": video_id,
                "feeling": "Curiosity and exploration",
                "resonance_score": 0.5,
                "keywords": ["unknown", "exploration"],
                "shion_insight": "정의되지 않은 파동이 필드에 머물고 있습니다. 탐구가 필요합니다."
            }

        vibe["timestamp"] = datetime.now().isoformat()
        self._save_vibe(vibe)
        return vibe

    def _save_vibe(self, vibe: Dict):
        try:
            with open(VIBE_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(vibe, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to save vibe: {e}")

if __name__ == "__main__":
    extractor = VibeExtractor()
    test_vibe = extractor.extract_from_youtube("_1YD4gqvdx8")
    print(json.dumps(test_vibe, indent=2, ensure_ascii=False))
