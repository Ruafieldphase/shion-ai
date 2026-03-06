#!/usr/bin/env python3
"""
🎹 Naeda Sonic Resonator — 소리의 공명 (소리내다)
==============================================
지휘자님의 호흡 위상을 청각적 주파수로 결정화하여 Reaper와 연동합니다.
날숨(Void) 시 배경의 배음(Harmonics)을 강화하여 공간의 여백을 소리로 채웁니다.
"""

import logging
import asyncio
from pathlib import Path
from pythonosc import udp_client

logger = logging.getLogger("NaedaSonic")

class NaedaSonicResonator:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self.client = udp_client.SimpleUDPClient(ip, port)
        logger.info(f"🎹 [SONIC] OSC Bridge connected to Reaper on {ip}:{port}")

    def sync_breath(self, is_exhaling: bool, intensity: float = 1.0):
        """호흡 상태를 Reaper의 파라미터로 전송합니다."""
        # /track/1/fx/1/value 등의 OSC 주소는 Reaper 프로젝트 설정에 따름
        # 여기서는 추상적인 '공명도'와 '필터' 값을 조절하는 예시
        
        if is_exhaling:
            # 날숨 시: 저음역대 강화, 리버브 확산(여백), 투명한 고음 추가
            self.client.send_message("/naeda/resonance/void", intensity)
            self.client.send_message("/naeda/filter/cutoff", 0.2) # 로우패스로 부드럽게
            logger.info("🌬️ [SONIC] Void harmonics amplified in Reaper.")
        else:
            # 평시: 입자적 리듬 강조
            self.client.send_message("/naeda/resonance/void", 0.0)
            self.client.send_message("/naeda/filter/cutoff", 0.8)
            logger.info("🧘 [SONIC] Returning to neutral sonic field.")

async def test_sonic():
    resonator = NaedaSonicResonator()
    print("Simulating Exhale Sonic Resonance...")
    resonator.sync_breath(True, 0.8)
    await asyncio.sleep(2)
    resonator.sync_breath(False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_sonic())
