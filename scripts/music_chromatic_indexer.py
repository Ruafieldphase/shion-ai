#!/usr/bin/env python3
"""
🎵 [PHASE 34] Chromatic Music Archive Indexer
===========================================
보관소의 음악 파일들을 전수 조사하여 색채 메타데이터(Resonance Crystal)를 생성하고 인덱싱합니다.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Shion Core integration
SHION_ROOT = Path("C:/workspace2/shion")
sys.path.append(str(SHION_ROOT / "core"))

try:
    from chromatic_encoder import ChromaticEncoder
except ImportError:
    print("❌ ChromaticEncoder not found in core.")
    sys.exit(1)

logger = logging.getLogger("MusicIndexer")
logging.basicConfig(level=logging.INFO)

MUSIC_DIR = Path(r"D:\ARCHIVE_WORKSPACE\agi\music\mp3")
OUTPUT_MANIFEST = SHION_ROOT / "outputs" / "manifestation" / "music_resonance_manifest.jsonl"
CRYSTAL_DIR = SHION_ROOT / "outputs" / "music_crystals"

class MusicIndexer:
    def __init__(self):
        self.encoder = ChromaticEncoder(SHION_ROOT)
        self.crystal_dir = CRYSTAL_DIR
        self.crystal_dir.mkdir(parents=True, exist_ok=True)
        OUTPUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    def _infer_vibe_from_filename(self, mp3_path: Path) -> dict:
        """파일명과 파일 속성에서 '소리의 느낌'을 추론합니다."""
        filename = mp3_path.name
        insight = filename.replace(".mp3", "").strip()
        size = mp3_path.stat().st_size
        
        # 1. Frequency/Energy Inference (Fake but poetic)
        # Larger files might mean more complex harmonics
        if size > 10000000: # > 10MB
            resonance = 0.8
            atp = 75.0
            status = "VIBRANT"
        elif size < 3000000: # < 3MB
            resonance = 0.4
            atp = 40.0
            status = "CONTRACTION"
        else:
            resonance = 0.6
            atp = 60.0
            status = "STABLE"

        # 2. Keyword refinement
        keywords = {
            "새벽": (0.9, 30.0, "STABLE"),
            "Dawn": (0.9, 30.0, "STABLE"),
            "Recursion": (0.7, 85.0, "VIBRANT"),
            "Focus": (0.5, 95.0, "STABLE"),
            "Chaos": (0.9, 90.0, "VIBRANT"),
        }
        
        for k, (res, a, s) in keywords.items():
            if k in insight:
                resonance = res
                atp = a
                status = s
                break
                
        return {
            "insight": insight,
            "state": {
                "atp_level": atp,
                "resonance": resonance,
                "status": status
            }
        }

    def process_all(self):
        if not MUSIC_DIR.exists():
            logger.error(f"Music directory not found: {MUSIC_DIR}")
            return

        mp3_files = list(MUSIC_DIR.glob("*.mp3"))
        logger.info(f"🎧 Found {len(mp3_files)} music files. Starting chromatic indexing...")

        processed_count = 0
        with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
            for mp3 in mp3_files:
                try:
                    vibe = self._infer_vibe_from_filename(mp3)
                    
                    # Generate crystal image
                    crystal_path = self.encoder.encode_to_crystal(vibe["state"], vibe["insight"])
                    
                    # Store crystal uniquely in music_crystals? 
                    # encoder saves to outputs/resonance_crystals by default.
                    # Let's keep that but record the path.
                    
                    entry = {
                        "timestamp": datetime.now().isoformat(),
                        "music_name": mp3.name,
                        "file_path": str(mp3),
                        "crystal_path": str(crystal_path),
                        "vibration": vibe["insight"],
                        "inferred_state": vibe["state"]
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        logger.info(f"💎 Indexed {processed_count}/{len(mp3_files)} files...")
                        
                except Exception as e:
                    logger.error(f"Failed to process {mp3.name}: {e}")

        logger.info(f"✨ Successfully indexed {processed_count} music files into {OUTPUT_MANIFEST.name}")

if __name__ == "__main__":
    indexer = MusicIndexer()
    indexer.process_all()
