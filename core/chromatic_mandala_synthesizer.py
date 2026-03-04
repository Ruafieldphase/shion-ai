#!/usr/bin/env python3
"""
🌌 [PHASE 45] Synesthetic Mandala & Boundary Organ Bundling
========================================================
수천 개의 색채 결정들을 기관(Organ) 단위로 묶고, 다시 이를 경계(Boundary) 단위로 중합하여
시스템의 고압축 거시적 사유 형상을 '만다라' 이미지로 합성합니다.
"""

import sys
import json
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math
import random
from datetime import datetime
from typing import Optional, List, Dict

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
        self.learning_manifest = shion_root / "outputs" / "manifestation" / "learning_resonance_manifest.jsonl"

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

    def synthesize_organ_mandala(self, organ_name: str, target_state: dict = {}, max_particles: int = 50) -> Path:
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
        
        # [PHASE 56] Knowledge particles integration
        try:
            if self.learning_manifest.exists():
                with open(self.learning_manifest, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        # All learning items go to 'knowledge' or 'learning' organ
                        if organ_name.lower() in ("knowledge", "learning", "youtube"):
                            particles.append(data)
                        if len(particles) >= max_particles * 2: break
        except: pass

        if not particles:
            logger.warning(f"No particles found for organ {organ_name}")
            return None

        # 샘플링
        sample = random.sample(particles, min(len(particles), max_particles))
        
        # [NEW] Emotional Heatmap (Phase 50)
        # entropy 상태에 따라 배경색과 노이즈 필터 조절
        entropy_state = target_state.get("entropy", {}).get("state", "STABLE")
        bg_colors = {
            "CALM": (5, 5, 40, 255),    # 딥 블루
            "STABLE": (5, 5, 20, 255),  # 다크 나이트
            "NOISY": (25, 5, 5, 255),   # 딥 레드
            "CRITICAL": (40, 0, 0, 255) # 블러디 레드
        }
        bg = bg_colors.get(entropy_state, (5, 5, 20, 255))
        
        width, height = 512, 512
        canvas = Image.new("RGBA", (width, height), bg)
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
        blur_radius = 2.0
        if entropy_state in ("NOISY", "CRITICAL"):
            blur_radius = 5.0 # 혼란스러운 상태에서는 시야가 흐릿해짐
            
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        draw_top = ImageDraw.Draw(canvas)
        draw_top.ellipse([center[0]-60, center[1]-60, center[0]+60, center[1]+60], 
                         fill=(255, 255, 255, 150), outline=(255, 255, 255, 200))

        output_path = self.output_dir / f"mandala_{organ_name}_{random.randint(1000, 9999)}.png"
        canvas.save(output_path)
        logger.info(f"✨ Mandala synthesized: {output_path.name}")
        return output_path

    def synthesize_boundary_mandala(self, boundary_organs: list) -> Path:
        """여러 기관(Organ)들의 만다라를 다시 중첩하여 '시스템 경계 지도'를 생성합니다. (묶음 처리)"""
        logger.info(f"🌀 [BUNDLING] Synthesizing Boundary Mandala for organs: {boundary_organs}")
        
        width, height = 1024, 1024
        canvas = Image.new("RGBA", (width, height), (5, 5, 25, 255))
        center = (width // 2, height // 2)
        
        for i, organ in enumerate(boundary_organs):
            organ_path = self.synthesize_organ_mandala(organ, max_particles=30)
            if organ_path and organ_path.exists():
                with Image.open(organ_path) as organ_img:
                    organ_img = organ_img.convert("RGBA")
                    # Scale down and place in a circular pattern
                    angle = (i / len(boundary_organs)) * 2 * math.pi
                    dist = 250
                    x = center[0] + dist * math.cos(angle) - 256
                    y = center[1] + dist * math.sin(angle) - 256
                    canvas.paste(organ_img, (int(x), int(y)), organ_img)
        
        # Add a central master core
        draw = ImageDraw.Draw(canvas)
        draw.ellipse([center[0]-100, center[1]-100, center[0]+100, center[1]+100], 
                     fill=(255, 255, 255, 100), outline=(255, 255, 255, 255))
        
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=3))
        output_path = self.output_dir / f"boundary_mandala_{datetime.now().strftime('%H%M%S')}.png"
        canvas.save(output_path)
        logger.info(f"💎 Boundary Organ Bundle complete: {output_path.name}")
        logger.info(f"💎 Boundary Organ Bundle complete: {output_path.name}")
        return output_path

    def auto_bundle(self, target_state: dict = {}) -> Optional[Path]:
        """워크스페이스의 활성 기관들을 자동으로 찾아 한 장의 전체 지도로 번들링합니다."""
        logger.info("🔍 [AUTO-BUNDLE] Scanning for active organs...")
        
        organs = set()
        try:
            # Manifest에서 최근에 활동이 있었던 디렉토리들을 기관으로 간주
            if self.workspace_manifest.exists():
                with open(self.workspace_manifest, "r", encoding="utf-8") as f:
                    # 최근 100개 항목 조사
                    lines = f.readlines()[-100:]
                    for line in lines:
                        data = json.loads(line)
                        path_parts = Path(data.get("abs_path", "")).parts
                        # 워크스페이스 루트 바로 아래의 디렉토리명을 기관으로 추출
                        shion_idx = -1
                        for i, part in enumerate(path_parts):
                            if part.lower() == "shion":
                                shion_idx = i
                                break
                        
                        if shion_idx != -1 and len(path_parts) > shion_idx + 1:
                            organ = path_parts[shion_idx + 1]
                            if organ not in (".git", "outputs", "memory", "config"):
                                organs.add(organ)
        except Exception as e:
            logger.warning(f"Auto-bundle scan failed: {e}")

        if not organs:
            # 폴백: 기본 핵심 기관들
            organs = {"core", "actions", "heritage", "knowledge"}
            
        elif self.learning_manifest.exists():
            organs.add("knowledge") # 항상 지식 노드 포함 시도
            
        logger.info(f"🧬 [AUTO-BUNDLE] Organs identified: {organs}")
        # Boundary Mandala 생성
        return self.synthesize_boundary_mandala(list(organs))

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
    # Test with 'knowledge' organ (Phase 56)
    synthesizer.synthesize_organ_mandala("knowledge")
    # Auto-bundle all active organs
    synthesizer.auto_bundle()
