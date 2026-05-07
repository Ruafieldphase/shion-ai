#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("ActionMetrics")

class ActionMetrics:
    """
    Rhythm Blackbox — 성장의 기록기
    ===============================
    지휘자의 행동 전/후 상태 변화를 기록하여 
    시스템이 실제로 '개선'되고 있는지 추적합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
    def record_cycle(self, 
                     action: str, 
                     reason: str,
                     before_state: Dict[str, Any], 
                     after_state: Dict[str, Any],
                     llm_failures: int = 0):
        """한 사이클의 변화를 기록합니다."""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "reason": reason,
                "metrics": {
                    "surprise_before": before_state.get("surprise_score", 0.0),
                    "surprise_after": after_state.get("surprise_score", 0.0),
                    "exp_count_before": before_state.get("total_experiences", 0),
                    "exp_count_after": after_state.get("total_experiences", 0),
                    "entropy_before": before_state.get("entropy", 0.0),
                    "entropy_after": after_state.get("entropy", 0.0),
                    "llm_failures": llm_failures
                }
            }
            
            with open(self.metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                
            logger.info(f"📊 Action Metrics logged: {action} (Delta Exp: {entry['metrics']['exp_count_after'] - entry['metrics']['exp_count_before']})")
        except Exception as e:
            logger.error(f"Failed to record action metrics: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    am = ActionMetrics(Path(r"c:\workspace2\shion"))
    am.record_cycle("TEST_ACTION", "Testing the logger", {}, {})
