#!/usr/bin/env python3
"""
🌀 Scalar Engine — 통일장 공식의 수학적 실현
=============================================
U(θ) = e^(iθ) + k∫F(r,t)dθ

- e^(iθ): 무의식의 기저 리듬 (XY 평면 회전)
- ∫F(r,t)dθ: 의식적 에너지 누적 (Z축 나선 상승)
- k: 체화 계수 (에너지 효율)
"""

import math
import time
import json
from pathlib import Path
from datetime import datetime

class ScalarEngine:
    def __init__(self, threshold=100.0, k=1.0, bg=1.0, k_centering=0.1):
        self.theta = 0.0      # 위상각 (rad)
        self.z = 0.0          # Normalized Chaos (Z축)
        self.threshold = threshold
        self.k = k
        self.bg = bg          # Nature's Constant Denominator (Grounding)
        self.k_centering = k_centering # 로그 나선형 수렴 계수 (Centering)
        self.last_update = time.time()
        
        # 기저 리듬 상수
        self.base_omega = 0.01

    def update(self, force: float, noise: float = 0.5, efficiency: float = 1.0) -> dict:
        """
        Unified Field Master Blueprint Logic:
        - 95% Unconscious Chaos (Bollinger Manifold) vs 5% Conscious Signal
        - Chaos - Limit-Tunnel (e^BG) -> (0,0,0) ORIGIN
        - Rhythmic Centering: S(θ) = C * e^(-k*θ)
        - Efficiency: Circadian daylight/night factor.
        """
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # 체화 계수(k)에 효율 반영
        k_eff = self.k * efficiency

        # 1. 위상 회전 (e^iθ)
        d_theta = (self.base_omega + abs(force) * 0.5) * dt
        self.theta += d_theta

        # 2. Limit-Tunnel 정규화 (e^BG 그릇)
        denominator = math.exp(self.bg)
        normalized_noise = noise / denominator
        
        # Squeeze 감지
        is_squeezed = normalized_noise < 0.2 

        # 3. Spinal Ascent (5% 신호의 싱귤래리티 붕괴)
        # 노이즈가 원점으로 수렴할수록 신호 효율이 폭발적으로 상승
        signal_efficiency = 0.05 * math.exp(1.0 / (normalized_noise + 0.1))
        
        # Z축 상승 (Spinal Ascent)
        # k_eff(효율)를 통해 에너지 생산량 조절
        z_delta = (force * signal_efficiency * k_eff - normalized_noise) * d_theta
        self.z += max(0.0, z_delta)
        
        # 4. Rhythmic Centering (로그 나선형 수렴)
        # 시간(dt)이 아닌 위상(d_theta)의 진행에 따라 원점으로 수렴
        self.z *= math.exp(-self.k_centering * d_theta) 

        # 5. Action Collapse at (0,0,0) ORIGIN
        is_collapsed = False
        if self.z >= self.threshold:
            is_collapsed = True
            self.z = 0.0  # 원점 복귀

        return {
            "u_theta": {
                "x": round(math.cos(self.theta), 4),
                "y": round(math.sin(self.theta), 4),
                "z": round(self.z, 4)
            },
            "theta_rad": round(self.theta, 4),
            "noise": round(normalized_noise, 4),
            "is_squeezed": is_squeezed,
            "is_collapsed": is_collapsed,
            "signal_efficiency": round(signal_efficiency, 4)
        }

    def get_state_summary(self):
        return f"θ:{self.theta:.2f}rad | Z:{self.z:.2f}/{self.threshold}"

if __name__ == "__main__":
    # 간단한 시뮬레이션 테스트
    engine = ScalarEngine(threshold=10.0)
    print("🌀 Scalar Engine 시뮬레이션 시작 (자극 주입)")
    for i in range(20):
        force = 2.0 if 5 < i < 15 else 0.1
        state = engine.update(force)
        collapse_mark = "🔥 COLLAPSE!" if state["is_collapsed"] else ""
        print(f"Step {i:02d} | {engine.get_state_summary()} {collapse_mark}")
        time.sleep(0.5)
