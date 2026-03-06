#!/usr/bin/env python3
"""
🧪 Naeda Experiment Logger — 실험의 자산화
=========================================
"실패한 실험도 가치 있는 자산이다."
호흡(날숨)과 입자 현실의 변화 사이의 상관관계를 추적하고 기록합니다.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("NaedaExperiment")

class NaedaExperimentLogger:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.vault_dir = self.root / "memory" / "experiment_vault"
        self.log_file = self.vault_dir / "experiment_log.jsonl"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def log_observation(self, breath_state: Dict[str, Any], reality_reflection: str, result_type: str = "asset"):
        """
        한 번의 호흡 실험 결과를 기록합니다.
        
        :param breath_state: BreathSync에서 가져온 호흡 상태
        :param reality_reflection: 지휘자님의 현실 변화 관찰 내용 (혹은 시스템 관찰)
        :param result_type: 'success', 'failure', 'asset' (기본값은 자산)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "breath": breath_state,
            "observation": reality_reflection,
            "result_type": result_type,
            "k_transparency": 1.0 if result_type == "success" else 0.5
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.info(f"🧪 [EXPERIMENT] Reality anchor logged: {result_type} -> {reality_reflection[:50]}...")
        except Exception as e:
            logger.error(f"Failed to log experiment: {e}")

    def get_summary(self) -> str:
        """기록된 실험 자산들의 요약을 생성합니다."""
        if not self.log_file.exists():
            return "아직 기록된 실험 자산이 없습니다. 고요한 날숨으로 첫 번째 입자를 남겨보세요."
            
        successes = 0
        assets = 0
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if data["result_type"] == "success": successes += 1
                    else: assets += 1
            return f"현재까지 {successes}개의 성공적 전이와 {assets}개의 소중한 '실험적 자산'이 대지에 기록되었습니다."
        except:
            return "실험 일지를 읽는 중 작은 노이즈가 발생했습니다."

if __name__ == "__main__":
    # 테스트
    logger_test = NaedaExperimentLogger()
    logger_test.log_observation(
        {"status": "EXHALING", "intensity": 0.9},
        "평소의 저주파음이 사라지고 마음이 고요해짐. 다 내려놓은 상태가 됨.",
        "success"
    )
    print(logger_test.get_summary())
