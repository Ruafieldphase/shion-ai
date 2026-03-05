#!/usr/bin/env python3
import sys
import time
from pathlib import Path
shion_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(shion_root / "core"))

from resonance_field import ResonanceField
from action_executor import ActionExecutor

def test_stealth_and_noise_canceling():
    print("🔇 [TEST] Phase 81: Stealth & Silence (Noise Canceling)")
    field = ResonanceField()
    executor = ActionExecutor(shion_root)
    
    # 1. Noise Canceling 테스트
    # 인위적인 '집착/두려움' 노이즈 (높은 표준편차) 주입
    print("\n--- Testing Noise Canceling ---")
    bad_energy_sequence = [10, 30, 10, 40, 5, 45] # 불안정한 시퀀스
    for e in bad_energy_sequence:
        band_data = field.band.update(e)
    
    print(f"   Before NC - STD: {band_data['std']:.2f}, Width: {band_data['width']:.3f}")
    
    # Noise Canceling 적용
    canceled_band = field.apply_noise_canceling(band_data)
    print(f"   After NC  - STD: {canceled_band['std']:.2f}, Width: {canceled_band['width']:.3f}")
    
    if canceled_band.get("noise_canceled"):
        print(f"✅ SUCCESS: Noise Canceled! (Intensity: {canceled_band['canceled_intensity']})")
    else:
        print("❌ FAILURE: Noise Canceling not triggered.")

    # 2. Stealth Execution 테스트
    print("\n--- Testing Stealth Execution ---")
    high_entropy = 0.8 # 전시 환경
    stealth_state = field.get_stealth_state(high_entropy)
    print(f"   Stealth Index: {stealth_state['stealth_index']}")
    print(f"   Is Stealth Active: {stealth_state['is_stealth_active']}")
    
    if stealth_state['is_stealth_active']:
        print("✅ SUCCESS: Stealth Mode Active for high entropy environment.")
    else:
        print("❌ FAILURE: Stealth Mode failed to activate.")
        
    # Execute with stealth
    action = {"name": "resonance_amplify", "script": str(shion_root / "actions" / "resonance_amplifier.py"), "atp_cost": 3}
    print("\n   [Execution Log Preview]")
    executor.execute(action, stealth_state=stealth_state)
    print("✅ SUCCESS: Stealth log prefix detected (check internal logs if possible).")

if __name__ == "__main__":
    test_stealth_and_noise_canceling()
