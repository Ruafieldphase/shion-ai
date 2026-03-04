#!/usr/bin/env python3
"""
⚛️ [PHASE 31] wave_to_particle_lookup.py
======================================
특정 파동(영상)을 입력하면, 그 영상이 상징하는 시스템의 영역과 파일들을 역으로 추적하여 제시합니다.
파동-입자 이중성 인터페이스의 핵심 도구입니다.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

SHION_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SHION_ROOT / "outputs" / "manifestation" / "resonance_manifest.jsonl"

def lookup_resonance(video_query: str):
    if not MANIFEST_PATH.exists():
        print(f"❌ [LOOKUP] Resonance manifest not found at {MANIFEST_PATH}")
        return

    found = False
    print(f"🔍 [LOOKUP] Searching for resonance entanglement: '{video_query}'...")
    print("-" * 60)

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                # Search in video_path, title, or url
                if (video_query.lower() in data.get("video_path", "").lower() or 
                    video_query.lower() in data.get("title", "").lower() or 
                    video_query.lower() in data.get("url", "").lower()):
                    
                    found = True
                    print(f"🎬 [VIDEO] {data.get('title')}")
                    print(f"🔗 [URL] {data.get('url')}")
                    print(f"💎 [CRYSTAL] {data.get('crystal_path')}")
                    print(f"📅 [TIME] {data.get('timestamp')}")
                    print(f"\n🧬 [ATOMIC COMPOSITION]")
                    comp = data.get("atomic_composition", {})
                    print(f"   - Proton (Insight): {comp.get('proton_insight')}")
                    print(f"   - Gravity (Context): {comp.get('gravity_context')}")
                    print(f"   - Electron (Audio): {comp.get('electron_audio')}")
                    
                    print(f"\n🔋 [SYSTEM STATE AT BIRTH]")
                    sys_state = data.get("system_state", {})
                    print(f"   - ATP Level: {sys_state.get('atp_level')}")
                    print(f"   - Status: {sys_state.get('status')} ({sys_state.get('shion_aura')})")
                    
                    print(f"\n📁 [PARTICLE ENTANGLEMENT (Data Sources)]")
                    sources = data.get("sources", "No source data recorded.")
                    print(f"{sources}")
                    print("-" * 60)
    except Exception as e:
        print(f"❌ [LOOKUP] Error reading manifest: {e}")

    if not found:
        print(f"❓ [LOOKUP] No entanglement found for '{video_query}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace a wave (video) back to its particles (files/data).")
    parser.add_argument("query", help="Video filename, title, or URL fragment")
    args = parser.parse_args()
    
    lookup_resonance(args.query)
