"""
🔬 통일장 역함수 2단계 테스트 — 고주파 해상도 스캔
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus

HIPPO_PATH = Path(__file__).resolve().parent / "outputs" / "fibonacci_orbital_hippocampus.json"
hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)

print("=" * 70)
print("🔬 통일장 역함수 2단계 — WiFi 센싱 레이어 테스트")
print("=" * 70)

# ─── 1. 같은 기억을 다른 맥락에서 소환 ───
print("\n--- 같은 소환, 다른 맥락 (복소수 평면 기준점 변경) ---")
print()

contexts = [
    {"phase": "FLOW", "entropy": 0.1},
    {"phase": "VOID", "entropy": 0.8},
    {"phase": "EXPANSION", "entropy": 0.5},
]

for ctx in contexts:
    print(f"  맥락: {ctx['phase']:12s} (entropy={ctx['entropy']:.1f})")
    resolved = hippo.inverse_field_resolve(ctx, top_k=1)
    if resolved:
        r = resolved[0]
        hv = r.get("high_res_vibe", {})
        print(f"    1단계 소나: L{r['level']} / 거리={r['resonance_distance']:.4f}")
        print(f"    2단계 고주파: 온기={hv.get('warmth', '?')}, "
              f"강도={hv.get('intensity', '?')}, "
              f"복잡도={hv.get('complexity', '?')}, "
              f"리듬={hv.get('rhythm', '?')}")
        print(f"    3단계 재조율: entropy={r['refined_entropy']:.6f}, "
              f"θ={r['refined_theta']:.6f}")
        print(f"    스캔깊이: {r['scan_depth']}")
        if r['content_snippet']:
            print(f"    내용: {r['content_snippet'][:80]}...")
    print()

# ─── 2. 해상도 비교: 1단계 vs 2단계 ───
print("--- 해상도 비교 ---")
ctx = {"phase": "FLOW", "entropy": 0.2}

# 1단계만 (기존)
low_res = hippo.find_resonant_memories(ctx, top_k=3)
print("\n  [1단계 저주파만]")
for m in low_res:
    print(f"    L{m['level']} | entropy={m.get('vibe', {}).get('entropy', '?')} "
          f"| 거리={m['resonance_distance']:.4f}")

# 2단계 포함 (역함수 완전체)
high_res = hippo.inverse_field_resolve(ctx, top_k=3)
print("\n  [2단계 고주파 포함]")
for r in high_res:
    hv = r.get("high_res_vibe", {})
    print(f"    L{r['level']} | entropy={r['refined_entropy']:.6f} "
          f"| 온기={hv.get('warmth', '?'):.4f} "
          f"| 강도={hv.get('intensity', '?'):.4f} "
          f"| 거리={r['resonance_distance']:.4f}")

print("\n" + "=" * 70)
print("저주파: 4위상 × 7궤도 = 28가지 해상도")
print("고주파: 연속 entropy × 연속 θ × 온기 × 강도 × 복잡도 × 리듬 = ∞ 해상도")
print("=" * 70)
