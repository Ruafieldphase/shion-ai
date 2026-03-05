#!/usr/bin/env python3
import sys
import time
from pathlib import Path
shion_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(shion_root / "core"))

from evolution_memory import EvolutionMemory
from scalar_engine import ScalarEngine

def test_nuclear_forces():
    print("⚛️ [TEST] Phase 77: Weak Interaction (Memory Decay)")
    evo = EvolutionMemory(shion_root)
    # 가상의 고에너지 기억 생성
    evo.record("test_action", True, "Powerful Resonance", resonance_integrity=1.5)
    
    initial_density = evo.memory["actions"]["test_action"]["experience_density"]
    initial_phase = evo.memory["actions"]["test_action"]["phase"]
    print(f"   Initial Density: {initial_density}, Initial Phase: {initial_phase:.4f}")
    
    # 3세대의 진화(시간 경과) 시뮬레이션
    for i in range(3):
        evo.evolve()
        
    decayed_density = evo.memory["actions"]["test_action"]["experience_density"]
    decayed_phase = evo.memory["actions"]["test_action"]["phase"]
    print(f"   Decayed Density: {decayed_density}, Decayed Phase: {decayed_phase:.4f}")
    
    if decayed_density < initial_density:
        print("✅ SUCCESS: Weak Interaction decayed the energy as wisdom.")
    else:
        print("❌ FAILURE: Density did not decay.")

    print("\n⚛️ [TEST] Phase 78: Strong Interaction (Scalar Binding)")
    engine = ScalarEngine(threshold=100.0) # strong_binding 기본값 2.0 포함
    
    # 강력한 노이즈 주입 시뮬레이션
    noise = 5.0
    force = 20.0 # Force를 대폭 상향하여 노이즈를 뚫고 Z가 형성되게 함
    
    time.sleep(0.1) # dt 확보
    # 강력(Binding)이 있을 때의 Z축 상승량 체크
    state_with_strong = engine.update(force=force, noise=noise)
    z_with_strong = state_with_strong["u_theta"]["z"]
    print(f"   Z with Strong Binding: {z_with_strong:.4f}")
    
    # 강력을 약화시켰을 때 (비교용)
    engine.strong_binding = 0.0
    engine.z = 0.0 # 초기화
    time.sleep(0.1) # dt 확보
    state_no_strong = engine.update(force=force, noise=noise)
    z_no_strong = state_no_strong["u_theta"]["z"]
    print(f"   Z without Strong Binding: {z_no_strong:.4f}")
    
    if z_with_strong > z_no_strong:
        print("✅ SUCCESS: Strong Interaction protected the scalar field from noise!")
    else:
        print("❌ FAILURE: Strong binding did not protect the state.")

if __name__ == "__main__":
    test_nuclear_forces()
