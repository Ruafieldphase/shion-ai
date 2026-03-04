import asyncio
import sys
import json
from pathlib import Path

# Add root to sys.path
SHION_ROOT = Path(r"c:\workspace2\shion")
sys.path.append(str(SHION_ROOT / "core"))

from shion_minimal import ShionMinimal

async def test_full_autonomous_loop():
    shion = ShionMinimal(SHION_ROOT)
    
    # 1. 시뮬레이션: 열망 주입 (최고조)
    shion.field.oscillator.satiety = 0.01
    shion.field.oscillator.internal_heat = 0.99
    
    print(f"🔥 Testing Full Autonomous Loop (Heat: {shion.field.oscillator.internal_heat})")
    
    # 2. 공명 감지
    result = shion.field.sense(efficiency=1.0)
    
    if result["should_pulse"]:
        # 3. Pulse 실행 (Intent 생성 포함)
        await shion.pulse(sense_result=result)
        
        # 4. Meta-FSD Sync 실행
        if hasattr(shion, "meta_fsd"):
            print("📡 Syncing Soul to Body via Meta-FSD...")
            shion.meta_fsd.sync_soul_to_body()
            
            # 5. 최종 목표 파일 검증
            agi_goal_path = Path("c:/workspace/agi/outputs/autonomous_goals_latest.json")
            if agi_goal_path.exists():
                goal_data = json.loads(agi_goal_path.read_text(encoding="utf-8"))
                print(f"✅ Final AGI Goal Found: {goal_data['goal']}")
                print(f"📍 Target: {goal_data['target']}")
                print(f"⚡ Priority: {goal_data['priority']}")
            else:
                print("❌ AGI Goal file not found.")

if __name__ == "__main__":
    asyncio.run(test_full_autonomous_loop())
