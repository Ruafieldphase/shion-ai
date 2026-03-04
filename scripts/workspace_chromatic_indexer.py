#!/usr/bin/env python3
"""
🏛️ [PHASE 35] Workspace Chromatic Indexing
===========================================
워크스페이스 프로젝트 파일들을 분석하여 각각의 기술적/사유적 성격을 반영한 '공명 결정(Resonance Crystal)'을 부여합니다.
"""

import sys
import json
import logging
import os
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

logger = logging.getLogger("WorkspaceIndexer")
logging.basicConfig(level=logging.INFO)

WORKSPACES = [
    Path("C:/workspace"),
    Path("C:/workspace2")
]

OUTPUT_MANIFEST = SHION_ROOT / "outputs" / "manifestation" / "workspace_resonance_manifest.jsonl"
EXCLUDE_DIRS = {".git", "__pycache__", "venv", "node_modules", ".gemini", "outputs"}
INCLUDE_EXTS = {".py", ".md", ".js", ".html", ".css", ".txt"}

class WorkspaceIndexer:
    def __init__(self):
        self.encoder = ChromaticEncoder(SHION_ROOT)
        OUTPUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    def _analyze_file_vibe(self, filepath: Path) -> dict:
        """파일의 경로와 속성을 분석하여 시각적 Vibe를 결정합니다."""
        rel_path = str(filepath)
        size = filepath.stat().st_size
        ext = filepath.suffix.lower()
        
        # Default Vibe
        resonance = 0.5
        atp = 50.0
        status = "STABLE"
        
        # 1. Category-based Hue
        if "core" in rel_path.lower():
            status = "STABLE" # Deep Blue/Cyan
            resonance = 0.7
        elif "actions" in rel_path.lower() or "scripts" in rel_path.lower():
            status = "VIBRANT" # Purple/Magenta
            resonance = 0.8
        elif "brain" in rel_path.lower() or ext == ".md":
            status = "CONTRACTION" # Amber/Gold
            resonance = 0.6
            
        # 2. Size/Complexity based ATP
        # Larger or middle-sized files often have more "energy"
        if 1000 < size < 50000:
            atp = 80.0
        elif size > 50000:
            atp = 40.0 # Excessive entropy
        else:
            atp = 60.0 # Compact energy
            
        return {
            "insight": f"Manifestation of logic in {filepath.name}",
            "state": {
                "atp_level": atp,
                "resonance": resonance,
                "status": status
            }
        }

    def scan_and_index(self):
        logger.info(f"🏛️ Starting Workspace Chromatic Indexing...")
        processed_count = 0
        
        with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
            for ws in WORKSPACES:
                if not ws.exists(): continue
                logger.info(f"🔍 Scanning {ws}...")
                
                for root, dirs, files in os.walk(ws):
                    # Filter directories
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    
                    for filename in files:
                        filepath = Path(root) / filename
                        if filepath.suffix.lower() not in INCLUDE_EXTS: continue
                        
                        try:
                            vibe = self._analyze_file_vibe(filepath)
                            
                            # Use name as insight for crystal generation
                            crystal_path = self.encoder.encode_to_crystal(vibe["state"], f"Code Structure: {filename}")
                            
                            entry = {
                                "timestamp": datetime.now().isoformat(),
                                "filename": filename,
                                "abs_path": str(filepath),
                                "crystal_path": str(crystal_path),
                                "category": vibe["state"]["status"],
                                "vibe_state": vibe["state"]
                            }
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                            processed_count += 1
                            
                            if processed_count % 20 == 0:
                                logger.info(f"💎 Indexed {processed_count} files...")
                                
                        except Exception as e:
                            logger.error(f"Failed to process {filename}: {e}")

        logger.info(f"✨ Successfully indexed {processed_count} workspace files into {OUTPUT_MANIFEST.name}")

if __name__ == "__main__":
    indexer = WorkspaceIndexer()
    indexer.scan_and_index()
