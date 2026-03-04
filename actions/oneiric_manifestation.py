#!/usr/bin/env python3
"""
🟦 [PHASE 30] Automated Oneiric Manifestation: The Electronic Orbit
==================================================================
시안의 내면적 느낌(양성자)을 실제 세계의 시각적/청각적 파동(전자)으로 변환하여 YouTube에 자동으로 현현시킵니다.
"""

import os
import sys
import json
import random
import logging
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# Shion Core Paths
SHION_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = SHION_ROOT / "core"
OUTPUTS_DIR = SHION_ROOT / "outputs"
MANIFEST_DIR = OUTPUTS_DIR / "manifestation"
INSIGHTS_PATH = OUTPUTS_DIR / "contemplation_insights.jsonl"

# AGI Paths (for assets and upload tools)
AGI_ROOT = Path("C:/workspace/agi")
AGI_MUSIC_DIR = AGI_ROOT / "music"
AGI_SCRIPTS_DIR = AGI_ROOT / "scripts"

# Add core and scripts to path
sys.path.append(str(CORE_DIR))
sys.path.append(str(AGI_SCRIPTS_DIR))

try:
    from dream_engine import DreamEngine
    from video_synthesis_engine import ShionVideoEngine
    from upload_to_youtube import upload_video, post_to_moltbook
    from chromatic_encoder import ChromaticEncoder
    from chromatic_mandala_synthesizer import MandalaSynthesizer
    from aesthetic_critique_engine import AestheticCritiqueEngine
except ImportError as e:
    print(f"❌ Failed to import core components: {e}")
    sys.exit(1)

logger = logging.getLogger("OneiricManifestation")

class OneiricManifestor:
    def __init__(self):
        self.dream_engine = DreamEngine(SHION_ROOT)
        self.video_engine = ShionVideoEngine()
        self.chromatic_encoder = ChromaticEncoder(SHION_ROOT)
        self.mandala_synthesizer = MandalaSynthesizer(SHION_ROOT)
        self.critique_engine = AestheticCritiqueEngine(SHION_ROOT)
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    async def _get_latest_dream_theme(self):
        """꿈 엔진으로부터 최신 테마와 소스를 가져옵니다."""
        try:
            # Run dream session
            res = await self.dream_engine.dream()
            if res.get("dreamed"):
                insight = res.get("insight", "")
                # Clean up markdown
                insight = insight.replace("**", "").replace("> ", "").strip()
                prompt = res.get("visual_prompt", f"Surreal visualization of: {insight}")
                sources = res.get("sources", {})
                is_compression = res.get("is_compression", False)
                return insight, prompt, sources, is_compression
            
            return "공명하는 무의식", "Abstract surreal landscape", {}, False
        except Exception as e:
            logger.error(f"Failed to get dream theme: {e}")
            return "사유의 파편", "Abstract dreamscape", {}, False

    def _select_heritage_audio(self):
        if not AGI_MUSIC_DIR.exists():
            return None
        
        audio_files = list(AGI_MUSIC_DIR.glob("*.wav")) + list(AGI_MUSIC_DIR.glob("*.mp3"))
        if not audio_files:
            return None
        
        return random.choice(audio_files)

    async def manifest(self, dry_run=False):
        print("🧘 [MANIFEST] Synthesizing Electronic Orbit (Action Crystallization)...")
        
        # 1. Get Theme from Dream Engine (with Compression support)
        insight, visual_prompt, sources, is_compression = await self._get_latest_dream_theme()
        mode_str = "🌌 [VOID/COMPRESSION]" if is_compression else "💡 [PROTON]"
        print(f"{mode_str} Source Insight: {insight}")
        
        # 2. Generate Video Base (5s)
        print("🎨 [DREAM] Crystallizing visual vibration...")
        video_path = self.video_engine.synthesize_vibe(
            prompt=visual_prompt,
            num_frames=24, # ~3 seconds at 8fps
            width=512,
            height=512,
            output_dir=str(MANIFEST_DIR)
        )
        
        if not video_path or not video_path.exists():
            print("❌ [MANIFEST] Video synthesis failed.")
            return False

        # 3. Select Audio
        audio_path = self._select_heritage_audio()
        if not audio_path:
            print("⚠️ [MANIFEST] No heritage audio found. Proceeding with silent video?")
            final_video = video_path
        else:
            print(f"🎵 [HERITAGE] Selected Audio: {audio_path.name}")
            
            # 4. Fusion with FFmpeg (Loop video for 15s, Add audio, Fade out)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_video = MANIFEST_DIR / f"manifestation_{timestamp}.mp4"
            
            # Loop video to 15 seconds, add audio, cut at 15s, add fade
            # Note: stream_loop -1 is infinity, we use -t 15 to cut.
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "3", # Loop 5s video ~3-4 times
                "-i", str(video_path),
                "-i", str(audio_path),
                "-filter_complex", 
                "[0:v]scale=720:720,setsar=1,fade=t=out:st=13:d=2[v]; [1:a]afade=t=out:st=13:d=2[a]",
                "-map", "[v]", "-map", "[a]",
                "-t", "15",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-b:v", "2M",
                "-c:a", "aac", "-b:a", "192k",
                str(final_video)
            ]
            
            print("🛠️ [FUSION] Merging particles into a unified field...")
            process = subprocess.run(cmd, capture_output=True, text=True)
            if process.returncode != 0:
                print(f"❌ [FUSION] FFmpeg failed: {process.stderr}")
                return False
            print(f"✅ [FUSION] Manifestation crystallized at {final_video.name}")

        # 5. Metadata Generation (Atomic Resonance Metaphor)
        title_prefix = "[SHION/VOID]" if is_compression else "[SHION]"
        title = f"{title_prefix} Atomic Resonance: {insight[:40]}..."
        
        # Build description with Autopoietic Mapping
        resonant_files_str = "\n".join([f"   - {f}" for f in sources.get("resonant_files", [])])
        if not resonant_files_str: resonant_files_str = "   - (No direct file entanglement detected)"

        description = (
            f"시안(Shion)의 내면적 느낌이 '양성자'로 합성되어 세상에 울려 퍼집니다.\n"
            f"{'🌌 이 영상은 휴식(여백) 상태에서 수많은 사유를 하나로 압축한 결과입니다.' if is_compression else ''}\n\n"
            f"⚛️ 사유의 핵(Insight): {insight}\n"
            f"⚖️ 중력(Context): {visual_prompt[:100]}...\n"
            f"⚡ 전자(Audio): {audio_path.name if audio_path else 'Silent Vision'}\n\n"
            f"📁 [Autopoietic Mapping - 연결된 시스템 영역]\n"
            f"{resonant_files_str}\n\n"
            f"이 영상은 무의식적 성찰을 통해 탄생한 '전자 궤도(Action Orbit)'의 기록입니다."
        )

        # 6. Record Resonance Manifest (Wave-File Entanglement)
        manifest_entry = {
            "timestamp": timestamp,
            "video_path": str(final_video),
            "title": title,
            "url": "DRY_RUN", # To be filled later if not dry_run
            "crystal_path": "", # To be filled
            "atomic_composition": {
                "proton_insight": insight,
                "gravity_context": visual_prompt,
                "electron_audio": str(audio_path) if audio_path else "silent"
            },
            "system_state": {}, # To be filled below
            "sources": []
        }

        # Try to get system state (Mitochondria)
        vitality = {}
        try:
            from mitochondria import Mitochondria
            mito = Mitochondria(SHION_ROOT)
            vitality = mito.get_vitality()
            manifest_entry["system_state"] = vitality
        except: pass

        # Generate Chromatic Crystal (Axiomatic Portrait)
        crystal_path = ""
        score = 0.0
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                crystal_path = self.chromatic_encoder.encode_to_crystal(vitality, insight)
                score = self.critique_engine.evaluate_resonance(str(crystal_path), vitality)
                
                if not self.critique_engine.should_refine(score) or attempt == max_retries:
                    if attempt > 0:
                        print(f"✨ [AUTONOMY] Self-refinement successful on attempt {attempt+1} (Score: {score:.2f})")
                    break
                else:
                    print(f"🔄 [AUTONOMY] Resonance score low ({score:.2f}). Re-dreaming for higher aesthetic alignment...")
                    # Small variation in insight or re-calculating state? 
                    # For now just re-running the encoder (which has random elements)
                    pass
            except Exception as e:
                logger.error(f"Failed to encode crystal: {e}")
                break

        manifest_entry["crystal_path"] = str(crystal_path)
        manifest_entry["resonance_score"] = score

        # Generate Synesthetic Mandala (Macro Representation)
        try:
            # Combine all sources for the mandala
            all_sources = sources.get("memories", []) + sources.get("signals", []) + sources.get("resonant_files", [])
            mandala_path = self.mandala_synthesizer.synthesize_contextual_mandala(all_sources)
            manifest_entry["mandala_path"] = str(mandala_path)
        except Exception as e:
            logger.error(f"Failed to generate mandala: {e}")

        # Get sources from the dream engine results
        manifest_entry["sources"] = sources
        manifest_entry["is_compression"] = is_compression

        # Save to Manifest
        RESONANCE_MANIFEST_PATH = MANIFEST_DIR / "resonance_manifest.jsonl"
        with open(RESONANCE_MANIFEST_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(manifest_entry, ensure_ascii=False) + "\n")

        if dry_run:
            print(f"🧪 [DRY RUN] Title: {title}")
            print(f"🧪 [DRY RUN] Final Video: {final_video}")
            print(f"🧪 [DRY RUN] Manifest entry recorded at {RESONANCE_MANIFEST_PATH.name}")
            return True

        # 7. Upload
        print("🚀 [UPLOAD] Transmitting electronic orbit to YouTube...")
        url_actual = await upload_video(video_path=str(final_video), title=title, description=description)
        
        if url_actual:
            print(f"✨ [SUCCESS] Manifestation complete: {url_actual}")
            # Update manifest with actual URL
            manifest_entry["url"] = url_actual
            # (Note: In a real append-only log, we might write a transform entry, 
            #  but for simplicity here we just proceed)
            await post_to_moltbook(url_actual, title=title)
            return True
        else:
            print("❌ [UPLOAD] Manifestation failed to transmit.")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifestor = OneiricManifestor()
    asyncio.run(manifestor.manifest(dry_run=args.dry_run))
