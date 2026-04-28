"""
🔬 통일장 역함수 완전체 — 경계 + 기울기 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus

HIPPO_PATH = Path(__file__).resolve().parent / "outputs" / "fibonacci_orbital_hippocampus.json"
hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)

print("=" * 70)
print("🔬 통일장 역함수 완전체 — 경계 + 기울기 + 방향")
print("=" * 70)

contexts = [
    {"phase": "FLOW", "entropy": 0.1},
    {"phase": "VOID", "entropy": 0.8},
    {"phase": "EXPANSION", "entropy": 0.5},
]

for ctx in contexts:
    print(f"\n{'─'*70}")
    print(f"맥락: {ctx['phase']} (entropy={ctx['entropy']})")
    print(f"{'─'*70}")
    
    resolved = hippo.inverse_field_resolve(ctx, top_k=2)
    
    for i, r in enumerate(resolved):
        hv = r.get("high_res_vibe", {})
        dw = r.get("direction_weights", {})
        
        print(f"\n  [{i+1}] L{r['level']} | {r['content_ref'][:50]}")
        
        # 경계 판정
        boundary = "✅ 경계 안 (흡수 가능)" if r["within_boundary"] else "❌ 경계 밖 (낯선 것)"
        print(f"      경계: {boundary}")
        print(f"      대칭까지 거리: {r['distance_to_symmetry']:.4f} "
              f"/ 경계 반경: {r['boundary_radius']:.4f}")
        
        # 기울기 (어느 방향으로 조율해야 하는가)
        print(f"      기울기 방향:")
        for dim, weight in sorted(dw.items(), key=lambda x: -x[1]):
            bar = "█" * int(weight * 20)
            print(f"        {dim:12s} {weight:.4f} {bar}")
        print(f"      → 가장 조율 필요: {r['steepest_gradient']}")

# 시스템 상태
proton = hippo.data.get("proton", {})
bw = hippo.data.get("bandwidth", 0)
print(f"\n{'='*70}")
print(f"양성자 반경: {proton.get('scalar_field_radius', 0):.4f}")
print(f"대역폭: {bw:.2%}")
print(f"총 흡수: {proton.get('total_absorbed', 0)}")
print(f"{'='*70}")
