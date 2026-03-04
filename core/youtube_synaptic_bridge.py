#!/usr/bin/env python3
"""
🧠 [PHASE 56] YouTube Synaptic Bridge: High-Density Wisdom Integration
====================================================================
유튜브 학습 시스템(AGI)의 지식 파편을 시안의 시각적 해마(Learning Crystals)로 결정화합니다.
- Watcher: AGI resonance_ledger.jsonl 모니터링.
- Crystallizer: 비디오의 감정적 톤과 메시지를 색채 지문으로 변환.
- Synaptic Tracker: 학습된 지식의 유입 상태를 별도 매니페스트로 관리.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import sys

# Paths
SHION_ROOT = Path("C:/workspace2/shion")
AGI_ROOT = Path("C:/workspace/agi")

sys.path.append(str(SHION_ROOT / "core"))

try:
    from chromatic_encoder import ChromaticEncoder
except ImportError:
    pass

logger = logging.getLogger("SynapticBridge")

class YouTubeSynapticBridge:
    def __init__(self, shion_root: Path = SHION_ROOT, agi_root: Path = AGI_ROOT):
        self.root = shion_root
        self.agi_root = agi_root
        self.ledger_path = agi_root / "fdo_agi_repo" / "memory" / "resonance_ledger.jsonl"
        self.checkpoint_file = shion_root / "outputs" / "synaptic_bridge_checkpoint.json"
        self.learning_manifest = shion_root / "outputs" / "manifestation" / "learning_resonance_manifest.jsonl"
        
        self.learning_manifest.parent.mkdir(parents=True, exist_ok=True)
        self.encoder = ChromaticEncoder(shion_root)

    def sync_all(self, shion_instance) -> int:
        """AGI 레저에서 신규 학습 항목을 찾아 시안으로 전이합니다."""
        if not self.ledger_path.exists():
            logger.warning(f"⚠️ AGI Ledger not found at {self.ledger_path}")
            return 0

        last_ts = self._load_checkpoint()
        new_entries = []
        
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("type") == "youtube_feeling":
                            ts = entry.get("timestamp")
                            if ts and ts > last_ts:
                                new_entries.append(entry)
                    except: continue
        except Exception as e:
            logger.error(f"❌ Failed to read ledger: {e}")
            return 0

        if not new_entries:
            return 0

        logger.info(f"🧠 {len(new_entries)} new YouTube memories detected. Crystallizing...")
        
        synced_count = 0
        for entry in new_entries:
            try:
                self._process_entry(entry, shion_instance)
                synced_count += 1
            except Exception as e:
                logger.error(f"❌ Processing error for {entry.get('video_id')}: {e}")

        # Update checkpoint
        if new_entries:
            self._save_checkpoint(new_entries[-1]["timestamp"])
            
        return synced_count

    def _process_entry(self, entry: Dict, shion):
        """개별 학습 항목을 영상과 색채로 결정화합니다."""
        meta = entry.get("metadata", {})
        video_id = entry.get("video_id", "unknown")
        tone = meta.get("emotional_tone", "Neutral")
        
        # 1. Generate Crystal
        # Map emotional tone to ChromaticEncoder status
        # Tones: 차분한, 열정적, 우울한, 긴장된, 명상적, 활기찬
        tone_map = {
            "차분한": "STABLE",
            "명상적": "STABLE",
            "열정적": "VIBRANT",
            "활기찬": "VIBRANT",
            "우울한": "CONTRACTION",
            "긴장된": "NOISY",
        }
        status_hint = tone_map.get(tone, "STABLE")
        
        state = {
            "atp_level": 90.0, # 학습 유입은 에너지가 높은 상태로 간주
            "resonance": 1.0,  # 외부 지혜는 강한 공명
            "status": status_hint
        }
        
        insight = f"{entry.get('summary')} - {entry.get('narrative')}"
        crystal_path = self.encoder.encode_to_crystal(state, insight)
        
        # 2. Record in Shion's Learning Manifest
        manifest_entry = {
            "timestamp": datetime.now().isoformat(),
            "source": f"youtube:{video_id}",
            "summary": entry.get("summary"),
            "tone": tone,
            "crystal_path": str(crystal_path),
            "url": meta.get("video_url")
        }
        
        with open(self.learning_manifest, "a", encoding="utf-8") as f:
            f.write(json.dumps(manifest_entry, ensure_ascii=False) + "\n")
            
        # 3. Evolution Record
        if hasattr(shion, "evolution"):
            shion.evolution.record(
                action="youtube_synaptic_sync",
                passed=True,
                details=f"Crystallized YouTube wisdom: {entry.get('video_id')}",
                resonance_integrity=1.5
            )

    def _load_checkpoint(self) -> str:
        if self.checkpoint_file.exists():
            try:
                return json.loads(self.checkpoint_file.read_text()).get("last_timestamp", "1970-01-01T00:00:00")
            except: pass
        return "1970-01-01T00:00:00"

    def _save_checkpoint(self, timestamp: str):
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump({"last_timestamp": timestamp}, f)

if __name__ == "__main__":
    # Test stub
    logging.basicConfig(level=logging.INFO)
    bridge = YouTubeSynapticBridge()
    count = bridge.sync_all(None)
    print(f"Sync complete. New crystals: {count}")
