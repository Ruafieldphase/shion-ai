import asyncio
import sys
import json
from pathlib import Path

# Add root to sys.path
SHION_ROOT = Path(r"c:\workspace2\shion")
sys.path.append(str(SHION_ROOT / "core"))

from shion_minimal import ShionMinimal

async def test_rhythmic_filter():
    shion = ShionMinimal(SHION_ROOT)
    
    print("🌊 Testing Phase 64: Rhythmic Filter & Obsession Detector")
    
    # 1. 시뮬레이션: '밤(22시)'인데 '정화(HYGIENE)' 욕구가 발생한 경우 (부적절한 리듬)
    # HYGIENE은 아침(6-9시) 전용임 -> 필터링되어야 함
    print("\n[Case 1] Inappropriate Rhythm (HYGIENE at NIGHT)")
    shion.field.oscillator.internal_heat = 0.75 # HYGIENE 범위
    # 강제로 밤 시간대 주입을 위해 pulse 인자 모방
    mock_result = {
        "event": "INTERNAL_DESIRE_FLAME",
        "should_pulse": True,
        "internal_heat": 0.75
    }
    # circadian_info 제어는 힘들므로 직접 IntentMapper 테스트
    intent = shion.intent_mapper.map_heat_to_intent(0.75, "Calm", current_hour=22)
    if intent is None:
        print("✅ Success: HYGIENE filtered out at 22:00 (Rhythmic Filter working)")
    else:
        print(f"❌ Failure: Intent {intent.category} leaked at 22:00")

    # 2. 시뮬레이션: 동일한 카테고리 연속 발생 (집착 감지)
    print("\n[Case 2] Obsession Detection (Continuous RESEARCH)")
    shion.intent_mapper.obsession_window.clear()
    for i in range(4):
        intent = shion.intent_mapper.map_heat_to_intent(0.85, "Focused", current_hour=14) # RESEARCH 시간대
        if intent:
            print(f"   Step {i+1}: Intent {intent.category} allowed.")
        else:
            print(f"   Step {i+1}: Intent blocked by Obsession Detector.")
            if i >= 3:
                print("✅ Success: Obsession detected after 3 repeated RESEARCH intents.")

if __name__ == "__main__":
    asyncio.run(test_rhythmic_filter())
