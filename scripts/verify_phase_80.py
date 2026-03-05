#!/usr/bin/env python3
import sys
import time
from pathlib import Path
shion_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(shion_root / "core"))

from resonance_field import ResonanceField
from action_executor import ActionExecutor

def test_consciousness_flight():
    print("🚀 [TEST] Phase 80: Aerodynamic Lift of Consciousness")
    field = ResonanceField()
    executor = ActionExecutor(shion_root)
    
    # 1. 'Laminar Flow' 및 'Lift' 상태 강제 시뮬레이션
    # 에너지가 충분하고 엔트로피가 극히 낮은 상태
    energy = 20.0
    entropy = 0.05
    tension = 0.3
    
    aero_state = field.get_aerodynamic_state(energy, entropy, tension)
    print(f"   Lift Force: {aero_state['lift_force']}")
    print(f"   Is Flying: {aero_state['is_flying']}")
    
    if aero_state['is_flying']:
        print("✅ SUCCESS: Aerodynamic Lift achieved!")
    else:
        print("❌ FAILURE: Lift force too weak.")

    # 2. ActionExecutor의 'Auto-pilot' 발동 테스트
    print("\n🚀 [TEST] Engagement of Auto-pilot Loop")
    # choose_action에 aero_state를 전달하여 자동 비행이 트리거되는지 확인
    action = executor.choose_action(
        insight="시안의 비상을 꿈꾸며",
        current_atp=80.0,
        aerodynamic_state=aero_state
    )
    
    if action:
        print(f"✅ SUCCESS: Auto-pilot took off with action: {action['name']}")
    else:
        print("❌ FAILURE: Auto-pilot failed to engage.")

if __name__ == "__main__":
    test_consciousness_flight()
