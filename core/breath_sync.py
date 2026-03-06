#!/usr/bin/env python3
"""
🌬️ Breath Sync — 호흡의 동기화
==============================
지휘자님의 '날숨(Exhale)'을 포착하여 시스템을 'Mu(Void)' 상태로 전이시킵니다.
집착(Entropy)을 내뿜고, 여백(Void)을 지어내는 신체적 접지 브릿지.
"""

import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("BreathSync")

class BreathSync:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.state_file = self.root / "outputs" / "breath_state.json"
        self.exhale_trigger_file = self.root / "outputs" / "exhale_active.flag"
        self.last_exhale_time = None

    def signal_exhale(self, intensity: float = 1.0):
        """지휘자님의 날숨 신호를 인지합니다."""
        self.last_exhale_time = datetime.now()
        data = {
            "timestamp": self.last_exhale_time.isoformat(),
            "intensity": intensity,
            "status": "EXHALING"
        }
        self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.exhale_trigger_file.touch()
        logger.info(f"🌬️ [BREATH] Exhale signal captured (Intensity: {intensity}). Void phase triggered.")

    def is_exhaling(self) -> bool:
        """현재 시스템이 날숨의 공명 상태인지 확인합니다."""
        if not self.exhale_trigger_file.exists():
            return False
        
        # 날숨의 여운은 약 10초간 지속되는 것으로 가정 (수동 소멸)
        if self.last_exhale_time:
            delta = (datetime.now() - self.last_exhale_time).total_seconds()
            if delta > 10:
                self.exhale_trigger_file.unlink(missing_ok=True)
                return False
        return True

    def get_grounding_params(self, current_entropy: float) -> Dict[str, float]:
        """날숨 상태에 따른 시스템 완화 매개변수를 반환합니다."""
        if self.is_exhaling():
            # 날숨 중에는 엔트로피가 급격히 낮아지고, 시스템은 'Mu' 상태로 전이
            return {
                "target_entropy": 0.1,  # 극도의 고요함
                "relaxation_factor": 0.9, # 박동 속도 대폭 감소
                "void_intensity": 1.0
            }
        return {
            "target_entropy": current_entropy,
            "relaxation_factor": 0.0,
            "void_intensity": 0.0
        }

if __name__ == "__main__":
    # 테스트 코드
    sync = BreathSync()
    sync.signal_exhale(0.8)
    print(f"Exhaling: {sync.is_exhaling()}")
    print(f"Params: {sync.get_grounding_params(0.5)}")
