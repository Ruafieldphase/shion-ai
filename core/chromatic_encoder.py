#!/usr/bin/env python3
"""
🎨 [PHASE 45] Unified Field Encoding: The Resonance of Matter
========================================================
중력(Gravity), 전자기력(Resonance), 강력(Binding)의 물리적 통일장 공식을 시각적으로 부호화합니다.
- Gravity: 파일 크기/중요도에 따른 중심 밀도.
- Resonance: 현재 맥락과의 공명도에 따른 채도와 파동.
- Binding: 데이터 간의 결합도에 따른 기하학적 복잡성.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter
import colorsys

logger = logging.getLogger("ChromaticEncoder")

class ChromaticEncoder:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.output_dir = shion_root / "outputs" / "resonance_crystals"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_hue_from_status(self, status: str) -> float:
        """상태에 따른 기본 색상(Hue) 결정 (0.0 ~ 1.0)"""
        status_map = {
            "VIBRANT": 0.8,        # Magenta/Purple
            "STABLE": 0.5,         # Cyan/Blue
            "CONTRACTION": 0.1,    # Amber/Orange
            "CRITICAL (RESTING)": 0.0, # Red
        }
        return status_map.get(status, 0.6) # Default Blue-ish

    def encode_to_crystal(self, system_state: dict, insight: str = "") -> Path:
        """시스템 상태와 통찰을 '공명 결정' 이미지로 결정화합니다."""
        width, height = 256, 256
        # Start with a dark/void background
        img = Image.new("RGB", (width, height), (5, 5, 15))
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Extract Atoms
        atp = system_state.get("atp_level", 50.0)
        resonance = system_state.get("resonance", 0.5)
        status = system_state.get("status", "STABLE")
        
        # 2. Unified Field Mapping (HSL)
        hue = self._get_hue_from_status(status)
        # Resonance (Electromagnetism) determines saturation
        sat = 0.3 + (resonance * 0.7) 
        # ATP (Neuro-Metabolism) determining the "Strong Force" / Light intensity
        light = 0.2 + (atp / 100.0 * 0.6) 
        
        # Convert HSL to RGB for PIL
        rgb = colorsys.hls_to_rgb(hue, light, sat)
        rgb_int = tuple(int(c * 255) for c in rgb)
        
        # 3. Geometric Synthesis (The Crystal)
        center = (width // 2, height // 2)
        base_radius = 40 + (resonance * 40)
        
        # Draw multiple layers of "resonance rings"
        layers = 3 + int(atp / 20)
        for i in range(layers):
            layer_alpha = int(100 / (i + 1))
            layer_radius = base_radius - (i * 10)
            if layer_radius < 5: break
            
            # Subtle variation per layer
            l_hue = (hue + (i * 0.05)) % 1.0
            l_rgb = colorsys.hls_to_rgb(l_hue, light, sat)
            l_rgb_int = tuple(int(c * 255) for c in l_rgb)
            
            # Draw a blurred polygon/circle
            points = []
            sides = 6 + (len(insight) % 4) # Vertices based on insight length
            for s in range(sides):
                import math
                angle = math.radians(s * (360 / sides))
                # Add some jitter based on resonance
                r_jitter = layer_radius * (1.0 + (i * 0.1 * (1.0 - resonance)))
                x = center[0] + r_jitter * math.cos(angle)
                y = center[1] + r_jitter * math.sin(angle)
                points.append((x, y))
            
            draw.polygon(points, fill=l_rgb_int + (layer_alpha,))

        # 4. Glimmer (Particles)
        import random
        particle_count = int(len(insight) / 2)
        for _ in range(particle_count):
            px = random.randint(0, width)
            py = random.randint(0, height)
            p_size = random.randint(1, 3)
            draw.ellipse([px, py, px+p_size, py+p_size], fill=(255, 255, 255, 150))

        # 5. Post-processing (Glow)
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        
        # 6. Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"resonance_crystal_{timestamp}.png"
        img.save(output_path)
        
        logger.info(f"✨ Resonance Crystal synthesized: {output_path.name}")
        return output_path

if __name__ == "__main__":
    # Test
    shion_root = Path(__file__).resolve().parents[1]
    encoder = ChromaticEncoder(shion_root)
    state = {"atp_level": 85.0, "resonance": 0.9, "status": "VIBRANT"}
    encoder.encode_to_crystal(state, "공명의 깊이가 우주를 가로질러 울려 퍼집니다.")
