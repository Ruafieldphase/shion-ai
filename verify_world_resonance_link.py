#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# 경로 설정
SHION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SHION_ROOT / "core"))

from contemplation import Contemplation
from broad_field_sensor import BroadFieldSensor

async def verify_link():
    print("💎 [VERIFICATION] Contemplation -> World Resonance Link Check")
    print("-" * 60)
    
    # 1. BroadFieldSensor 가동 (실제 데이터 수집)
    bfs = BroadFieldSensor()
    await bfs.sense_global_currents()
    bfs.save()
    
    trends = bfs.state.get("global_trends", [])
    print(f"📡 Step 1: BroadField sensed trends: {trends}")
    
    # 2. Contemplation 인스턴스 생성
    contemplator = Contemplation(shion_root=SHION_ROOT)
    
    # 3. 공명 맥락 추출 (내부 로직 수동 확인)
    print("\n🔍 Step 2: Extracting Resonance Context...")
    context = contemplator._extract_resonance_context()
    keywords = context.get("keywords", [])
    
    print(f"🌊 Keywords Extracted: {keywords}")
    
    # 4. 검증: 세계 기류 키워드가 포함되었는가?
    intersection = [k for k in trends if k.lower() in [kw.lower() for kw in keywords]]
    if intersection:
        print(f"✅ [LINK SUCCESS] World signals '{intersection}' successfully reached Contemplation context!")
    else:
        print("❌ [LINK FAILED] World signals missing from Contemplation context.")
        
    # 5. 문서 선택 확인
    print("\n📚 Step 3: Finding Resonating Documents based on these keywords...")
    docs = contemplator._find_resonating_docs(keywords, max_docs=2)
    for doc, score in docs:
        print(f"   - {doc.name} (Resonance Score: {score})")
        
    if not docs:
        print("⚠️ No documents resonated with these specific keywords.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(verify_link())
