import json
import time
import os
from pathlib import Path
from datetime import datetime

class MetricsEngine:
    """
    시안의 '자기 생산적 효율성'을 계량화하는 엔진.
    ATP 소모 대비 작업 성과, 중복 행동 감소율, 토큰 추정치 등을 추적합니다.
    """
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)
        self.metrics_path = self.root / "logs" / "quantum_metrics.jsonl"
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_metrics = {
            "timestamp": None,
            "atp_consumed": 0,
            "actions_performed": 0,
            "redundant_actions_prevented": 0,
            "unity_events": 0,
            "efficiency_score": 0.0,
            "token_estimate": 0
        }

    def log_event(self, event_type: str, value: any = 1):
        """이벤트를 기록하고 실시간 지표를 업데이트합니다."""
        if event_type == "atp_use":
            self.current_metrics["atp_consumed"] += value
        elif event_type == "action":
            self.current_metrics["actions_performed"] += 1
        elif event_type == "redundancy_block":
            self.current_metrics["redundant_actions_prevented"] += 1
        elif event_type == "unity":
            self.current_metrics["unity_events"] += 1
        elif event_type == "token":
            self.current_metrics["token_estimate"] += value

        self._update_efficiency()

    def _update_efficiency(self):
        """효율성 점수를 산출합니다. (Actions / ATP)"""
        if self.current_metrics["atp_consumed"] > 0:
            # 기본 효율성에 중복 방지 가중치를 더함
            base_eff = self.current_metrics["actions_performed"] / self.current_metrics["atp_consumed"]
            redundancy_bonus = self.current_metrics["redundant_actions_prevented"] * 0.1
            self.current_metrics["efficiency_score"] = round(base_eff + redundancy_bonus, 4)

    def flush(self):
        """현재 지표를 파일에 기록하고 초기화합니다."""
        self.current_metrics["timestamp"] = datetime.now().isoformat()
        with open(self.metrics_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.current_metrics) + "\n")
        
        # 누적치를 위해 일부 초기화 (또는 유지 정책 결정)
        # 여기서는 주기적 배치를 위해 초기화하지 않고 스냅샷만 찍음
        pass

    def get_summary(self):
        return self.current_metrics

if __name__ == "__main__":
    # 독립 테스트
    engine = MetricsEngine("c:/workspace2/shion")
    engine.log_event("atp_use", 10)
    engine.log_event("action")
    engine.log_event("redundancy_block", 2)
    engine.log_event("unity")
    engine.flush()
    print(f"Current Efficiency: {engine.get_summary()['efficiency_score']}")
