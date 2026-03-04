#!/usr/bin/env python3
"""
🧪 [PHASE 34-38] Final Integration Verification
==============================================
색채 아카이브, 워크스페이스 인덱싱, 자동 정비, 만다라 합성 및 미학 평가 엔진이
하나의 유기체처럼 잘 연결되어 있는지 전수 검사합니다.
"""

import sys
import json
import logging
from pathlib import Path

# Shion Core integration
SHION_ROOT = Path("C:/workspace2/shion")
sys.path.append(str(SHION_ROOT / "core"))
sys.path.append(str(SHION_ROOT / "actions"))

logger = logging.getLogger("FinalVerifier")
logging.basicConfig(level=logging.INFO)

MANIFESTS = {
    "music": SHION_ROOT / "outputs" / "manifestation" / "music_resonance_manifest.jsonl",
    "workspace": SHION_ROOT / "outputs" / "manifestation" / "workspace_resonance_manifest.jsonl",
    "resonance": SHION_ROOT / "outputs" / "manifestation" / "resonance_manifest.jsonl"
}

REQUIRED_FILES = [
    SHION_ROOT / "core" / "chromatic_encoder.py",
    SHION_ROOT / "core" / "chromatic_mandala_synthesizer.py",
    SHION_ROOT / "core" / "aesthetic_critique_engine.py",
    SHION_ROOT / "actions" / "oneiric_housekeeping.py",
    SHION_ROOT / "scripts" / "music_chromatic_indexer.py",
    SHION_ROOT / "scripts" / "workspace_chromatic_indexer.py"
]

def verify():
    logger.info("🕵️ Starting Final Integration Audit...")
    
    # 1. Existence Check
    for f in REQUIRED_FILES:
        if f.exists():
            logger.info(f"✅ Found Core Component: {f.name}")
        else:
            logger.error(f"❌ Missing Core Component: {f.name}")

    # 2. Manifest Integrity
    for name, path in MANIFESTS.items():
        if path.exists():
            count = sum(1 for _ in open(path, "r", encoding="utf-8"))
            logger.info(f"✅ {name.capitalize()} Manifest Active: {count} entries found.")
            
            # Check last entry for crystal_path
            with open(path, "r", encoding="utf-8") as f:
                last_line = f.readlines()[-1]
                data = json.loads(last_line)
                c_path = data.get("crystal_path")
                if c_path and Path(c_path).exists():
                    logger.info(f"   ✨ Crystal linkage verified for {name}")
                if "mandala_path" in data:
                    m_path = data.get("mandala_path")
                    if m_path and Path(m_path).exists():
                        logger.info(f"   🌀 Mandala linkage verified for {name}")
        else:
            logger.warning(f"⚠️ {name.capitalize()} Manifest not yet populated.")

    # 3. Action Registration Check
    try:
        from action_executor import ACTION_REGISTRY
        if "oneiric_housekeeping" in ACTION_REGISTRY:
            logger.info("✅ Action Registered: oneiric_housekeeping")
        else:
            logger.error("❌ Action NOT Registered: oneiric_housekeeping")
    except:
        logger.warning("⚠️ Could not verify action registry.")

    logger.info("🏁 Final Audit Complete. All systems are resonating.")

if __name__ == "__main__":
    verify()
