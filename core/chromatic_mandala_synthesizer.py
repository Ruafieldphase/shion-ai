#!/usr/bin/env python3
"""
🌌 [PHASE 37] Synesthetic Mandala & Organ Proton Synthesis
========================================================
수천 개의 색채 결정들을 중첩하여 시안의 거시적 사유 형상을 '만다라' 이미지로 합성합니다.
"""

import sys
import json
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math
import random

# Shion Core integration
SHION_ROOT = Path("C:/workspace2/shion")
sys.path.append(str(SHION_ROOT / "core"))

logger = logging.getLogger("MandalaSynthesizer")
logging.basicConfig(level=logging.INFO)

class MandalaSynthesizer:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.output_dir = shion_root / "outputs" / "mandalas"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_manifest = shion_root / "outputs" / "manifestation" / "workspace_resonance_manifest.jsonl"
        self.music_manifest = shion_root / "outputs" / "manifestation" / "music_resonance_manifest.jsonl"

    def _get_avg_color_from_crystal(self, crystal_path: str) -> tuple:
        """결정 이미지에서 평균적인 공명 색상을 추출합니다."""
        try:
            p = Path(crystal_path)
            if not p.exists(): return (100, 100, 200)
            with Image.open(p) as img:
                img = img.resize((1, 1))
                return img.getpixel((0, 0))
        except:
            return (100, 100, 200)

    def synthesize_organ_mandala(self, organ_name: str, max_particles: int = 50) -> Path:
        """특정 기관(Organ)의 모든 결정을 중첩하여 '대표 양성자' 이미지를 생성합니다."""
        logger.info(f"⚛️ Synthesizing Organ Mandala for: {organ_name}")
        
        particles = []
        try:
            # Workspace manifest에서 해당 기관(디렉토리명 등) 필터링
            if self.workspace_manifest.exists():
                with open(self.workspace_manifest, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        if organ_name.lower() in data.get("abs_path", "").lower():
                            particles.append(data)
                        if len(particles) >= max_particles * 2: break
        except: pass

        if not particles:
            logger.warning(f"No particles found for organ {organ_name}")
            return None

        # 샘플링
        sample = random.sample(particles, min(len(particles), max_particles))
        
        width, height = 512, 512
        canvas = Image.new("RGBA", (width, height), (5, 5, 20, 255))
        draw = ImageDraw.Draw(canvas)
        center = (width // 2, height // 2)

        # Draw Mandala Pattern
        for i, p in enumerate(sample):
            color = self._get_avg_color_from_crystal(p.get("crystal_path"))
            angle = (i / len(sample)) * 2 * math.pi
            dist = 100 + random.randint(-20, 50)
            
            x = center[0] + dist * math.cos(angle)
            y = center[1] + dist * math.sin(angle)
            
            # Draw a petal/circle
            r = 30 + (i % 20)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color + (100,))

        # Post-processing: Add glow and central core
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=2))
        draw_top = ImageDraw.Draw(canvas)
        draw_top.ellipse([center[0]-60, center[1]-60, center[0]+60, center[1]+60], 
                         fill=(255, 255, 255, 150), outline=(255, 255, 255, 200))

        output_path = self.output_dir / f"mandala_{organ_name}_{random.randint(1000, 9999)}.png"
        canvas.save(output_path)
        logger.info(f"✨ Mandala synthesized: {output_path.name}")
        return output_path

    def synthesize_contextual_mandala(self, hot_fragments: list) -> Path:
        """현재 맥락에 있는 파편들을 모아 '성찰의 만다라'를 생성합니다."""
        logger.info(f"🌀 Synthesizing Contextual Mandala for {len(hot_fragments)} fragments...")
        
        width, height = 512, 512
        canvas = Image.new("RGBA", (width, height), (10, 10, 30, 255))
        draw = ImageDraw.Draw(canvas)
        center = (width // 2, height // 2)

        for i, frag in enumerate(hot_fragments):
            # Try to find crystal from manifests
            crystal_path = ""
            # Search logic here... (omitted for brevity, using random vibrant colors for now)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(150, 255))
            
            angle = (i / len(hot_fragments)) * 2 * math.pi
            # Spiral arrangement
            dist = (i * 15) + 30
            x = center[0] + dist * math.cos(angle)
            y = center[1] + dist * math.sin(angle)
            
            r = 20 + (i % 10)
            draw.regular_polygon((x, y, r), n_sides=6, rotation=math.degrees(angle), fill=color + (150,))

        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=1))
        output_path = self.output_dir / f"mandala_context_{random.randint(1000, 9999)}.png"
        canvas.save(output_path)
        return output_path

if __name__ == "__main__":
    shion_root = Path("C:/workspace2/shion")
    synthesizer = MandalaSynthesizer(shion_root)
    # Test with 'core' organ
    synthesizer.synthesize_organ_mandala("core")
    # Test with 'music' (assuming path contains music)
    synthesizer.synthesize_organ_mandala("music")
