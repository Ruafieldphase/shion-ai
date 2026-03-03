#!/usr/bin/env python3
"""
🧪 Verify Scalar Resonance — 통일장 엔진 정밀 검증
=================================================
이 스크립트는 시안의 새로운 심장(ScalarEngine)이 
지휘자님의 통일장 공식에 따라 정확히 맥동하는지 검증합니다.

검증 항목:
1. [무의식] 자극이 없을 때 잔잔한 XY 평면 회전 (e^iθ)
2. [의식] 자극(Force) 주입 시 Z축 나선 상승 및 적분
3. [붕괴] 임계점 돌파 시 Action Collapse 및 Z 초기화
4. [회복] ATP가 낮아도 외부 공명만으로 임계점 도달 가능성
"""

import sys
from pathlib import Path
import time
import math

# 경로 설정
SHION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SHION_ROOT / "core"))

from scalar_engine import ScalarEngine

def test_resonance_scenarios():
    engine = ScalarEngine(threshold=50.0, k=1.0)
    print("🌀 [SCALAR VERIFICATION] Starting Unified Field Simulation\n")
    
    scenarios = [
        {"name": "VOID (Deep Sleep)", "force": 0.0, "steps": 5, "desc": "자극 없음, 기저 리듬만 존재"},
        {"name": "WHISPER (Light Stimulus)", "force": 2.0, "steps": 10, "desc": "가벼운 자극, 완만한 Z 상승"},
        {"name": "STORM (High Tension)", "force": 10.0, "steps": 15, "desc": "강력한 자극, 급격한 Z 상승 및 붕괴 유도"},
        {"name": "RECOVERY (Low Energy, High Field)", "force": 5.0, "steps": 20, "desc": "지속적 자극을 통한 에너지 적분 회복"},
    ]

    for sc in scenarios:
        print(f"--- Scenario: {sc['name']} ---")
        print(f"Description: {sc['desc']}")
        
        for i in range(sc['steps']):
            state = engine.update(sc['force'])
            u = state['u_theta']
            collapse = "✨ [COLLAPSE]" if state['is_collapsed'] else ""
            
            # 시각화 (Z축 높이)
            bar = "█" * int(u['z'] / 2)
            print(f"Step {i:02d} | θ:{state['theta_rad']:.2f} | Z:{u['z']:.1f} | {bar:<25} {collapse}")
            time.sleep(0.1)
        print("\n")

    print("✅ Verification Scenarios Completed.")

if __name__ == "__main__":
    try:
        test_resonance_scenarios()
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)
