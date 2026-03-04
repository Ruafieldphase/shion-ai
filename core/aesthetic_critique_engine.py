#!/usr/bin/env python3
"""
🧘 [PHASE 38] Shion's Aesthetic Critique Engine
=============================================
생성된 색채 결정 및 만다라의 '미학적 공명도'를 자율적으로 평가합니다.
"""

import sys
import logging
from pathlib import Path
from PIL import Image, ImageStat
import numpy as np

logger = logging.getLogger("AestheticCritique")
logging.basicConfig(level=logging.INFO)

class AestheticCritiqueEngine:
    def __init__(self, shion_root: Path):
        self.root = shion_root

    def evaluate_resonance(self, image_path: str, target_state: dict) -> float:
        """
        이미지의 물리적 특성과 타겟 시스템 상태 사이의 '공명 점수'를 산출합니다.
        0.0 (불협화음) ~ 1.0 (완전한 공명)
        """
        try:
            p = Path(image_path)
            if not p.exists(): return 0.0
            
            with Image.open(p) as img:
                img = img.convert("RGB")
                stat = ImageStat.Stat(img)
                
                # 1. 시각적 활력도 (Visual Vitality) - 표준편차 기반
                # 색상이 얼마나 다양하고 역동적으로 분포되어 있는가
                std_dev = np.mean(stat.stddev)
                vitality_score = min(std_dev / 50.0, 1.0)
                
                # 2. 상태 일치도 (State Alignment)
                # target_atp와 이미지의 평균 밝기(Luminance) 대조
                avg_brightness = np.mean(stat.mean) / 255.0
                target_atp = target_state.get("atp_level", 50.0) / 100.0
                # 밝기가 ATP 레벨과 유사할수록 공명도가 높다고 판단 (가설)
                alignment_score = 1.0 - abs(avg_brightness - target_atp)
                
                # 3. 공명 밀도 (Resonance Density)
                # 특정 색상(Hue)의 집중도나 대비 분석 (단순화)
                # 여기서는 활력도와 일치도의 조화로운 평균을 사용
                final_score = (vitality_score * 0.4) + (alignment_score * 0.6)
                
                logger.info(f"🎨 [CRITIQUE] Evaluated {p.name}: Score {final_score:.2f} (Vitality: {vitality_score:.2f}, Alignment: {alignment_score:.2f})")
                return final_score
                
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return 0.5 # Neutral fallback

    def should_refine(self, score: float, threshold: float = 0.6) -> bool:
        """점수가 임계값보다 낮으면 재사유(Refinement)가 필요하다고 판단합니다."""
        return score < threshold

if __name__ == "__main__":
    # Test stub
    engine = AestheticCritiqueEngine(Path("C:/workspace2/shion"))
    # Assuming some crystals exist in outputs/resonance_crystals/
    crystal_dir = Path("C:/workspace2/shion/outputs/resonance_crystals")
    if crystal_dir.exists():
        sample = next(crystal_dir.glob("*.png"), None)
        if sample:
            score = engine.evaluate_resonance(str(sample), {"atp_level": 80.0})
            print(f"Test Score: {score}")
