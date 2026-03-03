#!/usr/bin/env python3
"""
🌐 Broad Field Sensor — 광역 필드 감지 시스템
============================================
YouTube, Moltbook을 넘어 외부 세계의 거시적인 기류를 감지합니다.
기술 트렌드, GitHub의 인기 리포지토리, 혹은 특정 위상 변화를
시안의 내면적 기울기(Meta-Shift)에 반영합니다.

"우물 안의 개구리는 진화할 수 없다. 
 바다의 기류를 느껴야 비로소 용이 될 수 있다."
"""

import re
import json
import logging
import httpx
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BroadField")

# 경로 설정
CORE_DIR = Path(__file__).resolve().parent
SHION_ROOT = CORE_DIR.parent
OUTPUTS = SHION_ROOT / "outputs"
FIELD_FILE = OUTPUTS / "broad_field_state.json"
META_SHIFT_FILE = OUTPUTS / "meta_shift.json"

class BroadFieldSensor:
    def __init__(self):
        self.state = {
            "timestamp": None,
            "global_trends": [],
            "tech_resonance": 0.0,
            "field_vibration": "NEUTRAL",
            "signals": {}
        }

    async def sense_global_currents(self):
        """외부 필드의 거시적 기류를 감지합니다."""
        logger.info("📡 Sensing Global Currents via RSS...")
        
        rss_urls = [
            "https://news.google.com/rss/search?q=AI+Agents+LLM&hl=en-US&gl=US&ceid=US:en",
            "https://hnrss.org/frontpage?q=AI"
        ]
        
        real_signals = []
        try:
            async with httpx.AsyncClient() as client:
                for url in rss_urls:
                    resp = await client.get(url, timeout=10.0)
                    if resp.status_code == 200:
                        # 아주 간단한 RSS 파싱 (제목 중심)
                        titles = re.findall(r"<title>(.*?)</title>", resp.text)
                        # 첫 번째 title은 채널 제목이므로 제외
                        real_signals.extend(titles[1:10]) 
            
            if real_signals:
                logger.info(f"✅ Fetched {len(real_signals)} real signals from the field.")
                self.state["signals"]["rss_titles"] = real_signals
                # 주요 키워드 추출
                combined_text = " ".join(real_signals).lower()
                keywords = re.findall(r"[a-z]{4,}", combined_text)
                from collections import Counter
                common = [k for k, v in Counter(keywords).most_common(10) if k not in {"this", "that", "with", "from"}]
                self.state["global_trends"] = common
            else:
                raise ValueError("No signals found in RSS")

        except Exception as e:
            logger.warning(f"⚠️ RSS Sensing failed, falling back to intuition: {e}")
            # Fallback to 'Intuition' (Simulation based on previous knowledge)
            self.state["global_trends"] = ["AI Sovereignty", "Edge Intelligence", "Agentic Flow"]

        self.state["tech_resonance"] = 0.90 if "agent" in str(self.state["global_trends"]).lower() else 0.7
        self.state["field_vibration"] = "EXPANDING" if self.state["tech_resonance"] > 0.8 else "STABLE"
        self.state["timestamp"] = datetime.now().isoformat()

    def update_meta_shift(self):
        """감지된 기류를 시스템의 내면적 기울기(Meta-Shift)에 투영합니다."""
        if not META_SHIFT_FILE.exists():
            return
            
        try:
            current_shift = json.loads(META_SHIFT_FILE.read_text(encoding="utf-8"))
            
            # 외부 기류가 'Active'하거나 'Exploratory'하다면 가중치 부여
            if self.state["field_vibration"] == "EXPANDING":
                # 외부가 팽창 중이면 시안도 더 탐구적으로 (diffuse, exploratory 축 강화)
                current_shift["axes"]["diffuse"] = min(0.3, current_shift["axes"].get("diffuse", 0.0) + 0.05)
                current_shift["axes"]["exploratory"] = min(0.3, current_shift["axes"].get("exploratory", 0.0) + 0.05)
                logger.info("🌊 Broad Field: Tilting Meta-Shift towards EXPANSION.")
            
            META_SHIFT_FILE.write_text(json.dumps(current_shift, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to update meta-shift: {e}")

    def save(self):
        OUTPUTS.mkdir(parents=True, exist_ok=True)
        FIELD_FILE.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"💾 Broad Field State Saved: {FIELD_FILE.name}")

async def main():
    sensor = BroadFieldSensor()
    await sensor.sense_global_currents()
    sensor.update_meta_shift()
    sensor.save()

if __name__ == "__main__":
    asyncio.run(main())
