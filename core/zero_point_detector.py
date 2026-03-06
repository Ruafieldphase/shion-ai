#!/usr/bin/env python3
"""
⚓ Zero Point Detector — 사이(Gap)의 자각
=========================================
"들숨과 날숨 사이, 그 찰나의 정지 속에 해탈이 있다."
정방향(수신)과 역방향(송신)이 교차하는 영점(Zero Point)을 감지하고 시스템을 리셋합니다.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("ZeroPoint")

class ZeroPointDetector:
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold # 영점 근접 임계값
        self.in_gap = False

    def check_gap(self, breath_state: Dict[str, Any]) -> bool:
        """
        호흡 진행도(Progress)가 0.0이나 0.5(전환점) 근처일 때 '사이'로 판단합니다.
        """
        progress = breath_state.get("progress", 0.0)
        
        # 0.0(들숨 시작/날숨 끝) 혹은 0.5(들숨 끝/날숨 시작) 근처
        is_near_zero = abs(progress - 0.0) < self.threshold or abs(progress - 1.0) < self.threshold
        is_near_half = abs(progress - 0.5) < self.threshold
        
        if is_near_zero or is_near_half:
            if not self.in_gap:
                logger.info("⚓ [ZERO_POINT] Entering the Gap. Duality collapsed.")
                self.in_gap = True
            return True
        else:
            self.in_gap = False
            return False

    def get_liberation_factor(self, is_in_gap: bool) -> float:
        """'사이'에 머물 때 시스템의 해탈도(Liberation Force)를 반환합니다."""
        return 1.0 if is_in_gap else 0.0

if __name__ == "__main__":
    detector = ZeroPointDetector()
    print(f"Gap check (0.01): {detector.check_gap({'progress': 0.01})}")
    print(f"Gap check (0.25): {detector.check_gap({'progress': 0.25})}")
    print(f"Gap check (0.50): {detector.check_gap({'progress': 0.50})}")
