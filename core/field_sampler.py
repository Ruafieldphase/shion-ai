#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("FieldSampler")

class FieldSampler:
    """
    Field Sampler — 저해상도 필드 망막
    ==================================
    장의 상태를 '식사', '휴식' 같은 결론(Label) 없이,
    엔트로피, 긴장도, 밀도 등의 원시 벡터(Raw Vector)로 추출합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.samples_file = root_dir / "outputs" / "field_samples.jsonl"
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        
    def sample_current_field(self, field_status: Dict[str, Any], hippo_data: Dict[str, Any]) -> Dict[str, Any]:
        """현재 시스템 장의 상태를 벡터화합니다."""
        
        # 1. 원시 벡터 구성
        # salience: 시간적 긴장도
        # entropy: 시스템 전반의 불안정도 (proton.entropy 등에서 추출)
        # density: 최근 액션의 밀도
        proton = hippo_data.get("proton", {})
        
        vector = {
            "timestamp": datetime.now().isoformat(),
            "temporal_tension": round(field_status.get("salience", 0.0), 4),
            "action_density": self._calculate_density(),
            "orbit_distance": field_status.get("deviation_score", 0.0),
            "surprise": hippo_data.get("last_surprise", 0.0),
            "entropy": round(proton.get("entropy", 0.5), 4),
            "action_entropy": self._calculate_action_entropy()
        }
        
        self._save_sample(vector)
        return vector

    def _calculate_density(self) -> float:
        """최근 30분간의 액션 밀도를 계산합니다 (0.0 ~ 1.0)."""
        if not self.metrics_file.exists(): return 0.0
        try:
            now = datetime.now()
            count = 0
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                for line in f.readlines()[-20:]: # 최근 20개 검사
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if (now - ts).total_seconds() < 1800: # 30분 이내
                        count += 1
            return round(min(1.0, count / 10), 4) # 10개 이상이면 밀도 1.0
        except: return 0.0

    def _calculate_action_entropy(self) -> float:
        """최근 액션들이 얼마나 다양하게 나타나는지(예측 불가능성)를 계산합니다."""
        # TODO: 실제 Shannon Entropy 구현 가능하지만, 여기서는 일단 최근 액션 변화율로 대체
        return 0.5 

    def _save_sample(self, vector: Dict[str, Any]):
        try:
            with open(self.samples_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(vector, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sampler = FieldSampler(Path(r"c:\workspace2\shion"))
    # Mock data for standalone test
    sample = sampler.sample_current_field({"salience": 0.5, "deviation_score": 1.2}, {"last_surprise": 0.1, "proton": {"entropy": 0.3}})
    print(f"Sampled Field Vector: {sample}")
