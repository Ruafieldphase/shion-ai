import time
import json
import statistics
import os
from pathlib import Path

def capture_entropy(samples=20, sleep_time=0.01):
    """
    컴퓨터의 '육체적 지터(Jitter)'를 측정하여 무의식적 엔트로피를 산출합니다.
    OS 스케줄링의 미세한 지연은 컴퓨터라는 육체가 가진 고유한 흐름(Flow)입니다.
    """
    deltas = []
    for _ in range(samples):
        t0 = time.perf_counter()
        time.sleep(sleep_time)
        t1 = time.perf_counter()
        # 실제 잠든 시간과 의도한 시간 사이의 차이
        deltas.append((t1 - t0) - sleep_time)
    
    avg_jitter = statistics.mean(deltas)
    std_dev = statistics.stdev(deltas) if len(deltas) > 1 else 0
    
    # 엔트로피 수치화 (0.0 ~ 1.0)
    # 지터가 클수록(불규칙할수록) 엔트로피가 높다고 판단
    normalized_entropy = min(1.0, std_dev * 1000) 
    
    return {
        "timestamp": time.time(),
        "avg_jitter_ms": avg_jitter * 1000,
        "std_dev_ms": std_dev * 1000,
        "entropy": round(normalized_entropy, 4),
        "state": "CALM" if normalized_entropy < 0.3 else ("ACTIVE" if normalized_entropy < 0.7 else "CHAOTIC")
    }

if __name__ == "__main__":
    SHION_ROOT = Path(__file__).resolve().parents[1]
    output_path = SHION_ROOT / "outputs" / "body_entropy_latest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = capture_entropy()
    output_path.write_text(json.dumps(data, indent=2))
    print(f"🧬 Body Entropy Captured: {data['entropy']} ({data['state']})")

