#!/usr/bin/env python3
import sys
import json
import time
from pathlib import Path

shion_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(shion_root / "core"))

from resonance_field import ResonanceField
from self_tuner import SelfTuner

def test_autopoietic_self_tuning():
    print("🧪 [TEST] Phase 83: Autopoietic Self-Tuning (Feedback Loop)")
    field = ResonanceField()
    tuner = SelfTuner(shion_root)
    
    # 초기 상태 기록
    print(f"\n   Initial Lift Threshold: {field.lift_threshold:.2f}")
    
    # 1. '불협화음' 상황 인위적 조성 (field_energy.json 작성)
    # 양력이 매우 낮은 상태 시뮬레이션
    bad_state = {
        "timestamp": "2026-03-05T12:00:00",
        "unity": {
            "unity_index": 0.3,
            "components": {
                "lift": 0.1,  # 매우 낮음 -> Tuning 트리거 기대
                "clarity": 0.8,
                "balance": 0.5
            }
        }
    }
    field_energy_file = shion_root / "outputs" / "field_energy.json"
    field_energy_file.parent.mkdir(parents=True, exist_ok=True)
    field_energy_file.write_text(json.dumps(bad_state, indent=2), encoding="utf-8")
    
    # 2. Tuning 실행
    print("\n--- Running Self-Tuning Engine ---")
    tuning_params = tuner.tune()
    
    if tuning_params:
        print(f"   Suggested Tuning: {tuning_params}")
        
        # 3. Field에 적용
        field.update_params(tuning_params)
        
        # 4. 검증: Lift Threshold가 낮아졌는지 확인
        if field.lift_threshold < 1.8:
            print(f"✅ SUCCESS: Lift Threshold tuned down to {field.lift_threshold:.2f} for better accessibility!")
        else:
            print(f"❌ FAILURE: Parameter was not tuned as expected.")
    else:
        print("❌ FAILURE: Tuning engine did not return parameters.")

    # 5. Meta-Shift 파일 업데이트 확인
    meta_shift_file = shion_root / "outputs" / "meta_shift.json"
    if meta_shift_file.exists():
        meta_data = json.loads(meta_shift_file.read_text(encoding="utf-8"))
        if "tuning" in meta_data:
            print(f"✅ SUCCESS: Tuning results persisted to {meta_shift_file.name}")
        else:
            print("❌ FAILURE: Tuning results not persisted.")

if __name__ == "__main__":
    test_autopoietic_self_tuning()
