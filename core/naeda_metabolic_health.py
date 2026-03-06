#!/usr/bin/env python3
"""
🧬 Naeda Metabolic Health — 리듬의 장수 (Anti-Aging)
==================================================
"노화는 호흡이 무너지는 것이다."
들숨(흡수)과 날숨(배출)의 균형을 측정하여 시스템의 건강 위상을 점검합니다.
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("NaedaHealth")

class NaedaMetabolicHealth:
    def __init__(self, max_entropy_threshold: float = 0.8):
        self.rhythmic_integrity = 1.0 # 1.0 (건강) -> 0.0 (붕괴)
        self.aging_factor = 0.0        # 누적된 불균형 (엔트로피 찌꺼기)
        self.max_entropy_threshold = max_entropy_threshold
        self.last_update = time.time()

    def check_health(self, breath_cycle: Dict[str, Any], current_entropy: float) -> Dict[str, Any]:
        """
        호흡 상태와 엔트로피를 기반으로 건강 상태를 계산합니다.
        
        - 들숨만 길고 날숨이 없으면 노화(Aging) 증가.
        - 엔트로피가 높게 유지되면 노화 증가.
        """
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # 리듬 분석
        if breath_cycle["phase"] == "INHALING" and current_entropy > 0.6:
            # 받아들이기만 하고 비우지 못하는 상태 (과부하)
            self.aging_factor += 0.001 * dt
        elif breath_cycle["phase"] == "EXHALING" and current_entropy < 0.3:
            # 성공적인 비움 (회복)
            self.aging_factor = max(0.0, self.aging_factor - 0.002 * dt)

        self.rhythmic_integrity = max(0.1, 1.0 - self.aging_factor)
        
        status = "HEALTHY"
        if self.aging_factor > 0.5: status = "FATIGUED"
        if self.aging_factor > 0.8: status = "AGING_CRITICAL"

        return {
            "status": status,
            "integrity": round(self.rhythmic_integrity, 3),
            "aging_factor": round(self.aging_factor, 4),
            "recommendation": "Deep Exhale Required" if status != "HEALTHY" else "Maintaining Balance"
        }

if __name__ == "__main__":
    health = NaedaMetabolicHealth()
    # 인위적 스트레스 테스트
    print(health.check_health({"phase": "INHALING"}, 0.9))
    time.sleep(1)
    print(health.check_health({"phase": "EXHALING"}, 0.1))
