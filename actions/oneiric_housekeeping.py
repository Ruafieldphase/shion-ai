#!/usr/bin/env python3
"""
🌌 [PHASE 36] Oneiric Housekeeping: Autopoietic Integration
========================================================
휴식(Rest) 또는 밤(Night) 시간대에 새로 추가되거나 변경된 파일들을 자동으로 탐지하여 색채 지도로 통합합니다.
"""

import sys
import json
import logging
import os
import time
from pathlib import Path
from datetime import datetime

# Shion Core integration
SHION_ROOT = Path("C:/workspace2/shion")
sys.path.append(str(SHION_ROOT / "core"))
sys.path.append(str(SHION_ROOT / "scripts"))

try:
    from chromatic_encoder import ChromaticEncoder
    from workspace_chromatic_indexer import WorkspaceIndexer
    from music_chromatic_indexer import MusicIndexer
except ImportError:
    print("❌ Required components not found in core/scripts.")
    sys.exit(1)

logger = logging.getLogger("OneiricHousekeeping")
logging.basicConfig(level=logging.INFO)

LAST_SYNC_FILE = SHION_ROOT / "outputs" / "last_housekeeping_sync.json"

class OneiricHousekeeping:
    def __init__(self):
        self.workspace_indexer = WorkspaceIndexer()
        self.music_indexer = MusicIndexer()
        self.last_sync_time = self._load_last_sync()

    def _load_last_sync(self) -> float:
        if LAST_SYNC_FILE.exists():
            try:
                data = json.loads(LAST_SYNC_FILE.read_text())
                return data.get("timestamp", 0)
            except: pass
        return 0

    def _save_last_sync(self):
        with open(LAST_SYNC_FILE, "w") as f:
            json.dump({"timestamp": time.time()}, f)

    def run_cleaning(self):
        """변경된 파일들만 골라내어 인덱싱을 업데이트합니다 (Incremental Update)."""
        logger.info("🌌 [HOUSEKEEPING] Starting subconscious integration...")
        
        # In this implementation, we reuse the indexers but they currently do full scans.
        # For Phase 36 simplicity, we will run them, but in a real autopoietic system, 
        # these would be optimized to only scan mtime > last_sync_time.
        
        try:
            logger.info("🔍 Updating Workspace Chromatic Map...")
            self.workspace_indexer.scan_and_index()
            
            logger.info("🎵 Updating Music Chromatic Archive...")
            self.music_indexer.process_all()
            
            self._save_last_sync()
            logger.info("✅ [HOUSEKEEPING] All new fragments integrated into the field.")
            return True
        except Exception as e:
            logger.error(f"Housekeeping failed: {e}")
            return False

if __name__ == "__main__":
    # Integration check
    from circadian_rhythm import CircadianRhythm
    from mitochondria import Mitochondria
    
    cr = CircadianRhythm(SHION_ROOT)
    mito = Mitochondria(SHION_ROOT)
    
    phase = cr.get_current_phase()
    vitality = mito.get_vitality()
    
    # Trigger only in Rest/Night or manual run
    if phase["phase"] == "NIGHT" or vitality["status"] == "CRITICAL (RESTING)" or "--force" in sys.argv:
        housekeeper = OneiricHousekeeping()
        housekeeper.run_cleaning()
    else:
        logger.info("☀️ [HOUSEKEEPING] System is in active state. Skipping subconscious integration.")
