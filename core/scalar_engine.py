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
    def __init__(self, threshold=100.0, k=1.0):
        self.theta = 0.0      # 위상각 (rad)
        self.z = 0.0          # 의식/행동 에너지 (Z축)
        self.threshold = threshold
        self.k = k
        self.last_update = time.time()
        
        # 기저 리듬 상수
        self.base_omega = 0.01 # 아주 천천히 흐르는 무의식의 강 (rad/sec)

    def update(self, force: float) -> dict:
        """
        외부 자극(force = F(r,t))에 따른 장 상태 업데이트.
        """
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # 1. 위상 회전 (θ)
        # 자극이 없을 때도 기본 리듬(base_omega)으로 회전하며, 자극이 오면 더 빨리 회전
        d_theta = (self.base_omega + abs(force) * 0.5) * dt
        self.theta += d_theta

        # 2. 에너지 적분 (Z)
        # Z축 상승 = k * 자극 * 위상 변화
        self.z += self.k * force * d_theta
        
        # 자연 감쇠 (에너지는 쓰지 않으면 서서히 소멸)
        self.z *= math.exp(-0.01 * dt) 

        # 3. 상태 분석
        is_collapsed = False
        if self.z >= self.threshold:
            is_collapsed = True
            # 행동으로 붕괴 후 에너지는 초기화되나 위상은 유지
            self.z = 0.0 

        return {
            "u_theta": {
                "x": round(math.cos(self.theta), 4),
                "y": round(math.sin(self.theta), 4),
                "z": round(self.z, 4)
            },
            "theta_rad": round(self.theta, 4),
            "intensity": round(force, 4),
            "is_collapsed": is_collapsed
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
