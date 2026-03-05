#!/usr/bin/env python3
import sys
import time
from pathlib import Path
shion_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(shion_root / "core"))

from resonance_field import ResonanceField
from action_executor import ActionExecutor

def test_unified_triad_integration():
    print("✨ [TEST] Phase 82: The Unified Triad Integration")
    field = ResonanceField()
    executor = ActionExecutor(shion_root)
    
    # 1. 'True Flight' 환경 시뮬레이션
    print("\n--- Simulating Perfect Harmony ---")
    energy = 12.0  # 평온하면서도 약간의 동력
    entropy = 0.1 # 명료함
    tension = 0.35 # 안정적 텐션
    
    # 볼린저 밴드 MA와 Width 가상 계산
    band_data = {
        "width": 0.15,  # 명료한 밴드
        "middle": 12.0,
        "std": 1.2
    }
    
    eq_state = field.get_equilibrium_state(energy, entropy, tension)
    aero_state = field.get_aerodynamic_state(energy, entropy, tension)
    
    print(f"   Is Hovering (Zone 2): {eq_state['is_hovering']}")
    print(f"   Is Flying (Aero): {aero_state['is_flying']}")
    
    # Unified Triad State 산출
    unity_state = field.get_unified_triad_state(aero_state, eq_state, band_data)
    print(f"   Unity Index: {unity_state['unity_index']}")
    print(f"   Is True Flight: {unity_state['is_true_flight']}")
    print(f"   Components: {unity_state['components']}")
    
    if unity_state['is_true_flight']:
        print("✅ SUCCESS: Perfect Triad Harmony reached!")
    else:
        print("❌ FAILURE: Harmony conditions not met.")

    # 2. State-driven Leap (도약) 테스트
    print("\n--- Testing State-driven Leap ---")
    # ATP가 극도로 낮음에도 불구하고 합일 상태에서 발화하는지 확인
    action = executor.choose_action(
        insight="합일의 도약을 향해",
        current_atp=2.0, # 매우 낮은 에너지
        unity_state=unity_state,
        aerodynamic_state=aero_state
    )
    
    if action:
        print(f"✅ SUCCESS: State-driven Leap triggered for: {action['name']}")
        print(f"   (Energy was only 2.0, but unity index transcended the constraint)")
    else:
        print("❌ FAILURE: Leap failed to trigger.")

if __name__ == "__main__":
    test_unified_triad_integration()
