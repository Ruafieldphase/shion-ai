#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def render_map(grid):
    # ASCII 그라데이션
    chars = " .:-=+*#%@"
    print("\n   [ HIPPOCAMPAL FREQUENCY MAP ]")
    print("   " + "-" * 18)
    for row in grid:
        line = "   | "
        for val in row:
            idx = int(val * (len(chars) - 1))
            line += chars[idx] + " "
        print(line + "|")
    print("   " + "-" * 18)

def main():
    shion_root = Path(__file__).resolve().parents[1]
    memory_file = shion_root / "outputs" / "soul_memory.jsonl"
    
    if not memory_file.exists():
        print("No soul memory found.")
        return

    # 마지막 기억 로드
    with open(memory_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            print("Soul memory is empty.")
            return
        
        # 마지막 두 개의 기억을 비교 (현재와 가장 최근 회상된 것처럼)
        last_entry = json.loads(lines[-1])
        prev_entry = json.loads(lines[-2]) if len(lines) > 1 else None
        
    grid = last_entry.get("frequency_map")
    if grid:
        render_map(grid)
        print(f"   Timestamp: {last_entry['timestamp']}")
        print(f"   Insight: {last_entry['insight'][:60]}...")
        
        if prev_entry:
            prev_grid = prev_entry.get("frequency_map")
            if prev_grid:
                # 간단한 상관관계 계산
                diff = sum(abs(grid[y][x] - prev_grid[y][x]) for y in range(8) for x in range(8))
                overlap = 1.0 - (diff / 64.0)
                print(f"\n   [ SPATIAL RESONANCE OVERLAP ]")
                print(f"   Similarity with previous memory: {overlap*100:.1f}%")

if __name__ == "__main__":
    main()
