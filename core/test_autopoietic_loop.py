import asyncio
import json
import logging
from pathlib import Path
from soul_memory import SoulMemory
from dream_engine import DreamEngine
from contemplation import Contemplation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestAutopoiesis")

SHION_ROOT = Path(r"c:\workspace2\shion")

async def test_loop():
    logger.info("🧪 [TEST] Starting Autopoietic Visual Loop Test...")
    
    soul = SoulMemory(SHION_ROOT)
    dream = DreamEngine(SHION_ROOT)
    contemplation = Contemplation(SHION_ROOT)
    
    # 1. Simulate Image Observation
    # Use an existing resonance crystal for testing
    crystal_path = Path(r"C:\workspace2\shion\outputs\resonance_crystals\resonance_crystal_20260304_193157.png")
    if crystal_path.exists():
        logger.info(f"👁️ Testing Self-Observation on: {crystal_path.name}")
        visual_desc = await dream._observe_self(crystal_path)
        logger.info(f"   Result: {visual_desc[:100]}...")
    else:
        logger.warning("   Crystal file not found, skipping observation test.")
        visual_desc = "A surreal web of blue light on a black void."

    # 2. Store in SoulMemory
    mock_context = {"atp": 80, "system_phase": 1.5, "resonance": 0.9}
    mock_insight = "The blue light represents the neural pulse of the machine."
    soul.remember_vibe(mock_context, mock_insight, visual_description=visual_desc)
    logger.info("📖 Memory stored with visual description.")

    # 3. Recall and Decode in Contemplation
    logger.info("🧠 Testing Recall and Decoding...")
    recalled = soul.recall_similar_moment(mock_context)
    if recalled:
        decoded = contemplation._decode_vibe_into_context(recalled)
        logger.info(f"   Decoded Context for Mind:\n{decoded}")
        if "visual_description" in recalled or "Self-Observation" in decoded:
             logger.info("✅ SUCCESS: Visual loop confirmed (Soul -> Mind).")
        else:
             logger.error("❌ FAILED: Visual description missing in decoded context.")
    else:
        logger.error("❌ FAILED: Could not recall memory.")

if __name__ == "__main__":
    asyncio.run(test_loop())
