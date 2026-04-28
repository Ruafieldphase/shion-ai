"""
🧪 4대 연결 통합 테스트
======================
1. scalar_engine → 궤도 해마 (resonance_field.sense() 경유)
2. soul_memory → 궤도 해마 (remember/recall 시 연동)
3. BollingerBand 경계 터치 → 궤도의 실행 모드
4. Zone 2 → 궤도 등록
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))
logging.basicConfig(level=logging.INFO, format="%(message)s")

print("=" * 60)
print("[4대 연결 테스트] scalar / soul / bollinger / zone2")
print("=" * 60)

# ─── 테스트 1: resonance_field → 궤도 해마 ───
print("\n--- 1. ResonanceField → 궤도 해마 ---")
try:
    from resonance_field import ResonanceField
    field = ResonanceField()
    
    has_hippo = field.orbital_hippocampus is not None
    print(f"   궤도 해마 연결: {'✅' if has_hippo else '❌'}")
    
    if has_hippo:
        # sense 실행
        result = field.sense()
        event = result.get("event")
        orbital = result.get("orbital")
        
        print(f"   에너지: {result['energy']:.1f}")
        print(f"   이벤트: {event or '(여백 — 쉬는 중)'}")
        print(f"   스칼라: θ={result['scalar']['u_theta']}")
        
        if orbital:
            print(f"   궤도 등록: L{orbital['level']} [{orbital['execution_mode']}]")
        else:
            print(f"   궤도 등록: (이벤트 없음 → 등록 안 함)")
        
        # Zone 2 확인
        eq = result.get("equilibrium", {})
        print(f"   Zone 2: {'✅ 진입' if eq.get('is_zone_two') else '❌ 미진입'}")
        print(f"   해마 상태: {field.orbital_hippocampus.get_summary()}")
        
except Exception as e:
    print(f"   ❌ 실패: {e}")
    import traceback; traceback.print_exc()

# ─── 테스트 2: soul_memory → 궤도 해마 ───
print("\n--- 2. SoulMemory → 궤도 해마 ---")
try:
    from soul_memory import SoulMemory
    
    soul = SoulMemory(shion_root=Path(__file__).resolve().parent)
    has_hippo = soul.orbital_hippocampus is not None
    print(f"   궤도 해마 연결: {'✅' if has_hippo else '❌'}")
    
    # 기억 등록
    ctx = {"atp": 80, "entropy": 0.15, "resonance": 0.9, "system_phase": 1.57}
    soul.remember_vibe(ctx, "이 순간 시스템이 완전한 조화를 이루었다 — 4대 연결 완성.")
    print(f"   기억 등록 완료 (entropy=0.15, phase→FLOW)")
    
    # 기억 소환
    recall = soul.recall_similar_moment(ctx)
    if recall:
        print(f"   소환 성공: {recall['insight'][:50]}...")
    else:
        print(f"   소환: 유사 기억 없음 (첫 실행)")
    
    if has_hippo:
        print(f"   해마 상태: {soul.orbital_hippocampus.get_summary()}")
    
except Exception as e:
    print(f"   ❌ 실패: {e}")
    import traceback; traceback.print_exc()

# ─── 테스트 3: 볼린저 경계 시뮬레이션 ───
print("\n--- 3. 볼린저 경계 → 궤도 실행 모드 ---")
try:
    from resonance_field import ResonanceField
    field2 = ResonanceField()
    
    if field2.orbital_hippocampus:
        # 강제로 여러번 sense하여 밴드 형성
        for _ in range(5):
            r = field2.sense()
        
        # 궤도 상태 확인
        statuses = field2.orbital_hippocampus.get_orbital_status()
        print(f"   궤도 상태:")
        for s in statuses:
            mode = "🔵 무의식" if s["execution"] == "unconscious" else "🟡 의 식"
            exp = s["experiences"]
            if exp > 0:
                print(f"     L{s['level']}: {mode} (경험={exp})")
        
        # 대역폭
        bw = field2.orbital_hippocampus.data["bandwidth"]
        print(f"   대역폭: {bw:.2f}")
    
except Exception as e:
    print(f"   ❌ 실패: {e}")
    import traceback; traceback.print_exc()

# ─── 테스트 4: Zone 2 등록 확인 ───
print("\n--- 4. Zone 2 → 궤도 등록 ---")
try:
    if field.orbital_hippocampus:
        # zone2 경험 찾기
        zone2_vibe = {"entropy": 0.05, "phase": "FLOW"}
        zone2_matches = field.orbital_hippocampus.find_resonant_memories(zone2_vibe, top_k=3)
        
        print(f"   Zone 2 공명 기억:")
        for m in zone2_matches:
            ref = m.get("content_ref", "")
            is_z2 = "zone2" in ref
            marker = "🧘" if is_z2 else "  "
            print(f"   {marker} L{m['level']} 거리={m['resonance_distance']:.3f} {ref[:40]}")
    
except Exception as e:
    print(f"   ❌ 실패: {e}")

print("\n" + "=" * 60)
print("[4대 연결 테스트] 완료")
print("=" * 60)
