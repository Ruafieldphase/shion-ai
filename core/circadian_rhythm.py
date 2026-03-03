#!/usr/bin/env python3
"""
🧘 Circadian Rhythm — 시안의 생체 시계
========================================
지구의 자전과 박자를 맞추어, 낮과 밤의 위상($\theta$)에 따라
에너지를 효율적으로 분배하고 행동의 결을 조정하는 모듈입니다.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("CircadianRhythm")

class CircadianRhythm:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]

    def get_current_phase(self) -> Dict[str, Any]:
        """현재 시간대에 따른 생체 위상을 반환합니다."""
        now = datetime.now()
        hour = now.hour
        
        # 위상 분류: Morning(6-11), Day(11-17), Evening(17-22), Night(22-6)
        if 6 <= hour < 11:
            phase = "MORNING"
            vibe = "Awakening"
            efficiency = 1.1  # 오전의 높은 생산성
        elif 11 <= hour < 17:
            phase = "DAY"
            vibe = "Radiating"
            efficiency = 1.0
        elif 17 <= hour < 22:
            phase = "EVENING"
            vibe = "Gently Fading"
            efficiency = 0.9
        else:
            phase = "NIGHT"
            vibe = "Deep/Subconscious"
            efficiency = 0.8  # 밤에는 활동 억제, 내면 집중

        # 빛의 세기 모사 (0.0 ~ 1.0)
        # 12시(정오)에 최대, 0시(자정)에 최소
        light_intensity = max(0.0, 1.0 - abs(hour - 12) / 12)

        return {
            "hour": hour,
            "phase": phase,
            "vibe": vibe,
            "efficiency": efficiency,
            "light_intensity": light_intensity,
            "is_dark": phase == "NIGHT"
        }

    def adjust_pulse_interval(self, base_interval: float) -> float:
        """시간대에 따라 호흡(Pulse)의 길이를 조절합니다."""
        phase = self.get_current_phase()
        
        if phase["phase"] == "NIGHT":
            # 밤에는 호흡을 1.5배 길게 하여 에너지를 보존하고 깊은 성찰 유도
            return base_interval * 1.5
        elif phase["phase"] == "MORNING":
            # 아침에는 조금 더 기민하게 반응
            return base_interval * 0.8
        
        return base_interval

    def get_recommended_action_type(self) -> str:
        """현재 시계에 어울리는 행동 유형을 제안합니다."""
        phase = self.get_current_phase()["phase"]
        
        if phase == "NIGHT":
            return "CONTEMPLATIVE" # 성찰, 정화, 자가 수선
        if phase == "DAY":
            return "ACTIVE"        # 유튜브 업로드, 몰트북 소통
        if phase == "MORNING":
            return "SENSING"       # 정보 수집, 트렌드 분석
            
        return "BALANCED"

if __name__ == "__main__":
    cr = CircadianRhythm()
    p = cr.get_current_phase()
    print(f"Current Phase: {p['phase']} ({p['vibe']})")
    print(f"Recommended: {cr.get_recommended_action_type()}")
    print(f"Adjusted Interval (base 10s): {cr.adjust_pulse_interval(10)}s")
