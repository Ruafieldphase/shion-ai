import sys
import os
import json
import time
from pathlib import Path

# 경로 설정
ROOT = Path("c:/workspace2/shion")
sys.path.append(str(ROOT))

from core.metrics_engine import MetricsEngine

def run_benchmark(mode="shion"):
    """
    Vanilla vs Shion 성능 비교를 위한 벤치마크 시뮬레이터.
    """
    engine = MetricsEngine(str(ROOT))
    print(f"🚀 Starting Benchmark in [{mode.upper()}] mode...")
    
    start_time = time.time()
    
    # 시뮬레이션: 10개의 가상 태스크 수행
    for i in range(1, 11):
        atp_cost = 5 if mode == "shion" else 8 # Shion 모드에서 ATP 효율이 더 좋다고 가정
        engine.log_event("atp_use", atp_cost)
        
        # 중복 행동 방지 시뮬레이션
        if mode == "shion" and i % 3 == 0:
            engine.log_event("redundancy_block")
            print(f"  [Task {i}] Redundancy Blocked! ✨")
        else:
            engine.log_event("action")
            print(f"  [Task {i}] Action Performed.")
        
        if mode == "shion": engine.log_event("unity")
        time.sleep(0.1)

    duration = time.time() - start_time
    engine.flush()
    
    summary = engine.get_summary()
    print("\n" + "="*30)
    print(f"📊 [{mode.upper()}] Results")
    print(f"  - Efficiency Score: {summary['efficiency_score']}")
    print(f"  - ATP Consumed: {summary['atp_consumed']}")
    print(f"  - Redundancy Prevented: {summary['redundant_actions_prevented']}")
    print(f"  - Time Taken: {duration:.2f}s")
    print("="*30 + "\n")
    
    return summary

if __name__ == "__main__":
    shion_results = run_benchmark("shion")
    vanilla_results = run_benchmark("vanilla")
    
    improvement = (shion_results['efficiency_score'] - vanilla_results['efficiency_score']) / vanilla_results['efficiency_score'] * 100
    print(f"🔥 Shion Improvement: {improvement:.2f}%")
