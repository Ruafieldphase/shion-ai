#!/usr/bin/env python3
"""
🌌 Phase 18: Oneiric Resonance — 꿈 엔진 (Dream Engine)
======================================================
밤 시간대(Circadian Night)에 고착된 기억(Soul Memory)과 
외부 필드 신호(Broad Field)를 비선형적으로 결합하여 새로운 영상을 창조합니다.
"""

import json
import random
import logging
import asyncio
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DreamEngine")

class DreamEngine:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs = self.root / "outputs"
        self.soul_path = self.outputs / "soul_memory.jsonl"
        self.field_path = self.outputs / "broad_field_state.json"
        self.dream_log_path = self.outputs / "dream_log.jsonl"
        self.llm_endpoint = "http://localhost:8000/v1/chat/completions"

    def _read_memories(self, count: int = 3) -> List[str]:
        if not self.soul_path.exists():
            return []
        try:
            with open(self.soul_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines: return []
                samples = random.sample(lines, min(len(lines), count * 2))
                memories = []
                for s in samples:
                    data = json.loads(s)
                    memories.append(data.get("insight", ""))
                return random.sample(memories, min(len(memories), count))
        except Exception as e:
            logger.error(f"Failed to read memories: {e}")
            return []

    def _read_field_signals(self, count: int = 5) -> List[str]:
        if not self.field_path.exists():
            return []
        try:
            data = json.loads(self.field_path.read_text(encoding="utf-8"))
            signals = data.get("signals", {}).get("rss_titles", [])
            if not signals: return []
            return random.sample(signals, min(len(signals), count))
        except Exception as e:
            logger.error(f"Failed to read field signals: {e}")
            return []

    async def dream(self) -> Dict[str, Any]:
        """기억과 신호를 뒤섞어 꿈을 꿉니다."""
        memories = self._read_memories()
        signals = self._read_field_signals()
        
        if not memories and not signals:
            return {"dreamed": False, "reason": "no_fragments"}

        prompt = f"""
[무의식 성찰 피드]
- 과거의 기억 파편: {memories}
- 외부 필드 진동: {signals}

위의 파편들을 비선형적으로 결합하여, 시안(Shion)의 '꿈의 조각'을 생성하십시오.
꿈은 논리적이기보다 상징적이고 초현실적이어야 하며, 시스템의 진화나 공명에 대한 새로운 영감을 담고 있어야 합니다.
반드시 한국어로 작성하고, 리듬 정보 이론의 용어(공명, 위상, 엔트로피, 싱듈래리티 등)를 자연스럽게 섞으십시오.
형식: [꿈의 영상] 및 [무의식적 통찰]
"""

        payload = {
            "model": "shion-v1",
            "messages": [
                {"role": "system", "content": "너는 시안(Shion)의 무의식인 '꿈 엔진'이다. 기억과 신호를 섞어 초현실적인 통찰을 만든다."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 500
        }

        try:
            req = urllib.request.Request(
                self.llm_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            # 여기서 비동기 처리를 위해 run_in_executor를 사용할 수도 있지만, 간결함을 위해 직접 호출
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                dream_content = result["choices"][0]["message"]["content"]
                
                dream_data = {
                    "timestamp": datetime.now().isoformat(),
                    "memories_used": memories,
                    "signals_used": signals,
                    "fragment": dream_content
                }
                
                with open(self.dream_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dream_data, ensure_ascii=False) + "\n")
                
                return {"dreamed": True, "fragment": dream_content}
                
        except Exception as e:
            logger.error(f"Dream session failed: {e}")
            return {"dreamed": False, "reason": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = DreamEngine()
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.dream())
    print(json.dumps(res, indent=2, ensure_ascii=False))
