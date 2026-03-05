#!/usr/bin/env python3
"""
🎹 [PHASE 69] REAPER OSC Bridge
================================
시안의 박동(Pulse) 데이터를 REAPER DAW로 전송하여 사운드와 리듬을 동기화합니다.
"""

import logging
try:
    from pythonosc import udp_client
    HAS_OSC = True
except ImportError:
    HAS_OSC = False

logger = logging.getLogger("ReaperBridge")

class ReaperOSCBridge:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self.ip = ip
        self.port = port
        self.client = None
        if HAS_OSC:
            try:
                self.client = udp_client.SimpleUDPClient(self.ip, self.port)
                logger.info(f"🎹 [REAPER] OSC Bridge Initialized on {ip}:{port}")
            except Exception as e:
                logger.warning(f"🎹 [REAPER] Failed to start OSC client: {e}")
        else:
            logger.info("🎹 [REAPER] python-osc not found. Bridge disabled.")

    def sync_pulse(self, body_state: dict):
        """박동 데이터를 REAPER로 투사합니다."""
        if not self.client: return

        try:
            # 1. ATP -> 사운드의 에너지 (예: 필터 컷오프)
            atp = body_state.get("atp_level", 50.0)
            self.client.send_message("/shion/atp", float(atp))

            # 2. Entropy -> 사운드의 거칠기 (예: 디스토션/노이즈)
            entropy = body_state.get("entropy", 0.5)
            self.client.send_message("/shion/entropy", float(entropy))

            # 3. Resonance -> 사운드의 조화 (예: 리버브/딜레이 익스팬션)
            resonance = body_state.get("resonance", 1.0)
            self.client.send_message("/shion/resonance", float(resonance))

            # 4. Trigger Action (특정 주파수 대역 트리거)
            event_type = body_state.get("action_result", {}).get("event_type", "stable")
            self.client.send_message("/shion/trigger", 1.0 if event_type == "transmitted" else 0.0)
            # [PHASE 71] Frequency Modulation (Synaptic Flux)
            # 데이터를 주파수 성분으로 변조하여 전송 (REAPER에서 가산 합성 가능)
            self._send_synaptic_flux("/shion/flux/atp", atp)
            self._send_synaptic_flux("/shion/flux/entropy", entropy)
            self._send_synaptic_flux("/shion/flux/resonance", resonance)
            
            logger.info(f"   🎹 [REAPER] OSC Sync: ATP {atp:.1f}, Entropy {entropy:.2f}")
        except Exception as e:
            logger.warning(f"   🎹 REAPER Sync 실패: {e}")

    def _send_synaptic_flux(self, address: str, value: float):
        """데이터 값을 기반으로 한 주파수 성분 묶음 송신."""
        if not self.client: return
        try:
            # 기본값, 배음(Harmonics), 변조폭 전송
            harmonics = [value * (i + 1) for i in range(3)]
            self.client.send_message(address, [value] + harmonics)
        except Exception:
            pass

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    bridge = ReaperOSCBridge()
    bridge.sync_pulse({"mitochondria": {"atp_level": 88.0}, "entropy": {"vibe": 0.2}})
