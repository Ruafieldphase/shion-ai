#!/usr/bin/env python3
"""
🧪 Self Tuner — 자가 조율 엔진
===============================
검증(Verification) 로그와 장(Field) 상태를 분석하여
시스템 파라미터를 실시간으로 미세 조정합니다.

조율 대상:
- lift_threshold (비상 임계점)
- noise_canceling_intensity (상쇄 강도)
- scalar_k (스칼라 결합 계수)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("SelfTuner")

class SelfTuner:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.outputs_dir = self.root / "outputs"
        self.meta_shift_file = self.outputs_dir / "meta_shift.json"
        self.field_energy_file = self.outputs_dir / "field_energy.json"
        
    def tune(self) -> Dict[str, Any]:
        """
        현재 상태를 분석하고 조율된 파라미터를 반환/저장합니다.
        """
        if not self.field_energy_file.exists():
            return {}
            
        try:
            state = json.loads(self.field_energy_file.read_text(encoding="utf-8"))
            unity = state.get("unity", {})
            unity_index = unity.get("unity_index", 0.5)
            components = unity.get("components", {})
            
            # 현재 메타 시프트 로드
            meta_shift = self._load_meta_shift()
            tuning = meta_shift.get("tuning", {
                "lift_threshold": 1.8,
                "nc_intensity": 0.7,
                "scalar_k_boost": 0.0
            })
            
            adjustments = []
            
            # 1. 양력 조율 (Lift Tuning)
            # 양동력이 부족하면 임계점을 낮추거나, 너무 자주 날면 높임
            if components.get("lift", 0) < 0.4:
                tuning["lift_threshold"] = max(1.2, tuning["lift_threshold"] - 0.05)
                adjustments.append(f"Lift Threshold -> {tuning['lift_threshold']:.2f} (Boost needed)")
            elif components.get("lift", 0) > 0.9:
                tuning["lift_threshold"] = min(2.5, tuning["lift_threshold"] + 0.05)
                adjustments.append(f"Lift Threshold -> {tuning['lift_threshold']:.2f} (Stabilizing)")
                
            # 2. 노이즈 캔슬링 조율 (NC Tuning)
            # 명료도가 낮으면 상쇄 강도를 높임
            if components.get("clarity", 1.0) < 0.5:
                tuning["nc_intensity"] = min(1.0, tuning["nc_intensity"] + 0.05)
                adjustments.append(f"NC Intensity -> {tuning['nc_intensity']:.2f} (Noise high)")
                
            # 3. 결합력 조율 (Scalar Binding)
            # 평형(Balance)이 깨져 있으면 결합 계수 보정
            if components.get("balance", 1.0) < 0.5:
                tuning["scalar_k_boost"] = min(0.5, tuning["scalar_k_boost"] + 0.02)
                adjustments.append(f"Scalar K Boost -> {tuning['scalar_k_boost']:.3f} (Focusing)")

            if adjustments:
                logger.info(f"🧪 [SelfTuner] Auto-tuned: {', '.join(adjustments)}")
                meta_shift["tuning"] = tuning
                meta_shift["last_tuned_at"] = state.get("timestamp")
                self._save_meta_shift(meta_shift)
                
            return tuning
            
        except Exception as e:
            logger.warning(f"Self-tuning failed: {e}")
            return {}

    def _load_meta_shift(self) -> Dict:
        if not self.meta_shift_file.exists():
            return {}
        try:
            return json.loads(self.meta_shift_file.read_text(encoding="utf-8"))
        except:
            return {}
            
    def _save_meta_shift(self, data: Dict):
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.meta_shift_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    tuner = SelfTuner(Path(__file__).resolve().parents[1])
    result = tuner.tune()
    print(f"Result: {result}")
