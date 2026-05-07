#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("GradientLogger")

class ExperienceGradientLogger:
    """
    Experience Gradient Logger — 기울기 에피소드 기록기
    ==================================================
    예측과 실제, 그리고 그 해석(가설)을 하나의 '에피소드'로 묶어
    해마가 장의 곡률(기울기)을 학습할 수 있는 단위로 변환합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.gradient_file = root_dir / "outputs" / "experience_gradients.jsonl"
        
    def log_episode(self, 
                    past_vector: Optional[Dict[str, Any]], 
                    current_vector: Dict[str, Any], 
                    prediction: Dict[str, Any],
                    hypothesis: Optional[Dict[str, Any]],
                    feedback: Optional[str] = "unknown") -> Dict[str, Any]:
        """인지 사이클의 연쇄를 에피소드로 묶어 기록합니다."""
        
        episode = {
            "timestamp": datetime.now().isoformat(),
            "past_vector": past_vector,
            "current_vector": current_vector,
            "prediction": prediction,
            "hypothesis": hypothesis,
            "feedback": feedback,
            # 예측 오차(Error) 계산
            "prediction_error": self._calculate_error(prediction, current_vector)
        }
        
        self._save_episode(episode)
        return episode

    def _calculate_error(self, prediction: Dict[str, Any], reality: Dict[str, Any]) -> float:
        """예측된 벡터와 실제 벡터 간의 유클리드 거리를 계산하여 오차를 산출합니다."""
        error = 0.0
        keys = ["temporal_tension", "action_density", "entropy"]
        for k in keys:
            p_val = prediction.get(k, 0.5)
            r_val = reality.get(k, 0.5)
            error += (p_val - r_val) ** 2
        return round(error ** 0.5, 4)

    def _save_episode(self, episode: Dict[str, Any]):
        try:
            with open(self.gradient_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(episode, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger_engine = ExperienceGradientLogger(Path(r"c:\workspace2\shion"))
    # Mock episode
    logger_engine.log_episode(None, {"salience": 0.5}, {"salience": 0.4}, {"id": "TEST_HYPO"})
