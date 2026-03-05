#!/usr/bin/env python3
"""
장애 주입 및 회복력 집중 테스트 (Phase 88: Resilience Verification)
이 스크립트는 시안(Shion)의 `ActionExecutor`에 고의로 에러 확률을 부여하고,
시스템이 로그에 에러 타입과 복구 시간(recovery_time_sec)을 어떻게 기록하는지 검증합니다.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from core.action_executor import ActionExecutor
from core.metrics_engine import MetricsEngine

class ChaosExecutor(ActionExecutor):
    """테스트를 위해 확률적으로 에러(429, Timeout)를 발생시키는 스푸핑 실행기"""
    def __init__(self, root, fail_rate=0.4):
        super().__init__(root)
        self.fail_rate = fail_rate
        self.call_count = 0
        
    def execute(self, action, timeout=60, stealth_state=None):
        self.call_count += 1
        import random
        from datetime import datetime
        
        # 40% 확률로 실패 주입
        if random.random() < self.fail_rate:
            error_type = random.choice(["429_TOO_MANY_REQUESTS", "TIMEOUT", "CRASH_CODE_1", "RATE_LIMIT"])
            print(f"💥 [CHAOS] Injecting simulated error: {error_type} for action {action['name']}")
            return {
                "action": action["name"],
                "passed": False,
                "event_type": "reflected",
                "stdout": "",
                "stderr": f"Simulated Chaos Error: {error_type}",
                "error_type": error_type,
                "atp_consumed": action["atp_cost"],
                "resonance_at_selection": 0.1,
                "duration_seconds": 1.5,
            }
        else:
            print(f"🌊 [CHAOS] Action succeeded: {action['name']}")
            return {
                 "action": action["name"],
                 "passed": True,
                 "event_type": "transmitted",
                 "stdout": "Success",
                 "stderr": "",
                 "error_type": None,
                 "atp_consumed": action["atp_cost"],
                 "resonance_at_selection": 0.8,
                 "duration_seconds": 2.0,
            }

def run_resilience_test():
    print("🚀 Starting Phase 88 Resilience Metrics Test...")
    engine = MetricsEngine(str(ROOT_DIR))
    executor = ChaosExecutor(ROOT_DIR, fail_rate=0.5)
    
    last_error_time = None
    
    # 10 펄스 시뮬레이션
    for pulse in range(1, 11):
        print(f"\n--- Pulse #{pulse} ---")
        
        # 가상의 행동 선택
        action = {"name": "test_action", "atp_cost": 5, "frequency_range": (100, 200)}
        result = executor.execute(action)
        
        recovery_time = None
        if not result["passed"]:
            if last_error_time is None:
                from datetime import datetime
                last_error_time = datetime.now()
        else:
            if last_error_time is not None:
                from datetime import datetime
                recovery_time = (datetime.now() - last_error_time).total_seconds()
                last_error_time = None
                print(f"🌱 Recovered gracefully in {recovery_time:.2f} seconds!")
                
        engine.log_episode(
            episode_id=f"sim_pulse_{pulse}",
            phase="ACT",
            action=result["action"],
            success=result["passed"],
            error_type=result.get("error_type"),
            recovery_time_sec=recovery_time,
            human_intervention=False,
            resonance_score=0.5
        )
        time.sleep(1.0) # 시간 경과 시뮬레이션
        
    print("\n✅ Test Complete. Checking written logs...")
    log_path = ROOT_DIR / "logs" / "tangible_metrics.jsonl"
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-10:]
            for line in lines:
                data = json.loads(line)
                if data.get("episode_id", "").startswith("sim_pulse"):
                    print(f"Log: Pulse={data['episode_id']} | Success={data['success']} | "
                          f"Error={data['error_type']} | Recovery={data['recovery_time_sec']}")

if __name__ == "__main__":
    run_resilience_test()
