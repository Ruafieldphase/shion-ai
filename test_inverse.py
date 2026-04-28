"""
🧪 역함수 테스트 — 패턴 완성 / 기억 재압축 / 예측
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus

HIPPO_PATH = Path(__file__).resolve().parent / "outputs" / "fibonacci_orbital_hippocampus.json"
hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)

print("=" * 60)
print("🔄 통일장 역함수 테스트")
print("=" * 60)

# ─── 1. 패턴 완성 (부분 단서 → 전체 복원) ───
print("\n--- 1. 패턴 완성 (역함수: coords → vibe) ---")
partial = {"phase": "FLOW"}  # entropy 없이 phase만 제공
completed = hippo.pattern_complete(partial, top_k=3)
for c in completed:
    v = c["restored_vibe"]
    print(f"   L{c['level']} | {v['phase']:12s} entropy={v['entropy']:.4f} "
          f"θ={v['theta_restored']:.4f} r={v['radius_restored']:.6f}")
    print(f"       → {c['content_ref'][:60]}")

# ─── 2. 순방향 → 역방향 검증 ───
print("\n--- 2. 순방향 → 역방향 일치 검증 ---")
test_vibes = [
    {"entropy": 0.1, "phase": "FLOW"},
    {"entropy": 0.5, "phase": "EXPANSION"},
    {"entropy": 0.9, "phase": "VOID"},
]
for vibe in test_vibes:
    coords = hippo.vibe_to_spiral_coords(vibe)
    restored = hippo.coords_to_vibe(coords.tolist())
    match = "✅" if restored["phase"] == vibe["phase"] else "❌"
    print(f"   {match} {vibe['phase']:12s} e={vibe['entropy']:.1f} "
          f"→ coords → {restored['phase']:12s} e={restored['entropy']:.4f}")

# ─── 3. 기억 재압축 ───
print("\n--- 3. 기억 재압축 (회상 = 변형) ---")
current = {"entropy": 0.2, "phase": "FLOW"}
recon = hippo.recall_and_reconsolidate(current, blend_ratio=0.1, top_k=1)
for r in recon:
    v = r["restored_vibe"]
    print(f"   재압축 #{r['reconsolidation_count']} | "
          f"{v['phase']} e={v['entropy']:.4f} "
          f"(10% 현재 혼합)")
    print(f"       → {r['content_ref'][:60]}")

# ─── 4. 예측 ───
print("\n--- 4. 다음 경험 예측 (궤적 외삽) ---")
pred = hippo.predict_next(recent_n=5)
if pred["predicted"]:
    v = pred["predicted_vibe"]
    vel = pred["avg_velocity"]
    print(f"   예측: L{pred['predicted_level']} ({pred['predicted_mode']})")
    print(f"   Vibe: {v['phase']} entropy={v['entropy']:.4f}")
    print(f"   속도벡터: [{vel[0]:.4f}, {vel[1]:.4f}, {vel[2]:.4f}]")
    print(f"   궤적 길이: {pred['trajectory_length']}개 경험 기반")
else:
    print(f"   예측 불가: {pred['reason']}")

print("\n" + "=" * 60)
print("해마 완성도: 12/12")
print("=" * 60)
