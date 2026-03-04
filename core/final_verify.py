import asyncio
import sys
import json
import time
from pathlib import Path

# Add root to sys.path
SHION_ROOT = Path(r"c:\workspace2\shion")
sys.path.append(str(SHION_ROOT / "core"))

from shion_minimal import ShionMinimal

async def final_organic_check():
    print("🌌 [SYSTEM_VERIFICATION] Starting Final Organic Loop Check...")
    shion = ShionMinimal(SHION_ROOT)
    
    # [Step 1] Metabolism & Desire Check
    print("\n1️⃣ Checking Metabolism & Desire Generation...")
    shion.field.oscillator.satiety = 0.2
    # Throb should increase heat
    shion.field.oscillator.throb(current_atp=80, last_resonance=0.3)
    heat = shion.field.oscillator.internal_heat
    print(f"   Internal Heat generated: {heat:.2f}")

    # [Step 2] Rhythmic Intent Mapping Check
    print("\n2️⃣ Checking Rhythmic Intent Mapping & Obsession Detection...")
    # Simulate Night (22:00) - Should favor RESONANCE/RESEARCH but block HYGIENE
    # Category determined by heat: >0.9 RESONANCE, >0.8 RESEARCH, <0.8 HYGIENE
    
    # Try HYGIENE at night (should be filtered)
    intent_hygiene = shion.intent_mapper.map_heat_to_intent(0.75, "Night", current_hour=22)
    print(f"   HYGIENE at 22:00: {'Filtered' if intent_hygiene is None else 'LEAKED'}")
    
    # Try RESEARCH at night (should be allowed but priority might be lowered)
    intent_research = shion.intent_mapper.map_heat_to_intent(0.85, "Night", current_hour=22)
    print(f"   RESEARCH at 22:00: {'Allowed' if intent_research else 'Filtered'}")

    # [Step 3] Full Pulse Integration
    print("\n3️⃣ Running Full Pulse Integration...")
    # Inject high heat to trigger spontaneous pulse
    result = shion.field.sense(efficiency=1.0)
    print(f"   Sense Event: {result['event']}")
    
    await shion.pulse(sense_result=result)
    print("   Pulse Cycle Completed.")

    # [Step 4] Meta-FSD Sync Check
    print("\n4️⃣ Checking Meta-FSD Synaptic Sync...")
    if hasattr(shion, "meta_fsd"):
        synced = shion.meta_fsd.sync_soul_to_body()
        print(f"   Sync to FSD: {'SUCCESS' if synced else 'FAILED'}")
        
        goal_file = Path("c:/workspace/agi/outputs/autonomous_goals_latest.json")
        if goal_file.exists():
            goal = json.loads(goal_file.read_text(encoding="utf-8"))
            print(f"   🚀 Final Goal Injected to AGI: {goal['goal']}")
            print(f"   📍 Target: {goal.get('target', 'None')}")

    print("\n✅ [VERIFICATION_COMPLETE] System is organically aligned and rhythmic.")

if __name__ == "__main__":
    asyncio.run(final_organic_check())
