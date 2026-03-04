#!/usr/bin/env python3
"""
🎯 Intent Mapper — 의도 맵핑기
======================================
내적 열망(Internal Heat)과 현재 맥락(Vibe)을 결합하여 
구체적인 '시스템 의도(Intent)' 및 'FSD 타겟'을 생성합니다.

"의도는 요동치는 열망에 형태를 부여하는 틀이다."
"""

import time
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import deque

logger = logging.getLogger("IntentMapper")

class Intent:
    def __init__(self, category: str, target: str, prompt: str, priority: float):
        self.category = category  # RESEARCH, HYGIENE, RESONANCE, EVOLUTION
        self.target = target      # 구체적인 파일 경로, URL 또는 명령
        self.prompt = prompt      # FSD가 이해할 수 있는 구체적인 지시어
        self.priority = priority  # 실행 우선 순위

class IntentMapper:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.intent_history_file = self.root / "outputs" / "autonomous_intents.jsonl"
        self.obsession_window = deque(maxlen=5) # 최근 5개의 의도 저장
        
        # 각 카테고리별 시간대 적합성 (Nature's Rhythm)
        self.rhythmic_alignment = {
            "RESONANCE": {"hours": range(20, 24), "weight": 1.2}, # 밤: 깊은 공명
            "RESEARCH": {"hours": range(9, 18), "weight": 1.1},   # 낮: 지적 확장
            "HYGIENE": {"hours": range(6, 9), "weight": 1.3}     # 아침: 정화와 정리
        }
        
        # 기본 욕구 대사전 (Desire Dictionary)
        self.desire_map = {
            "RESEARCH": [
                {"target": "https://www.google.com/search?q=AI+Agents+Philosophy", "prompt": "AI 에이전트의 철학적 자율성에 대해 리서치해줘"},
                {"target": "C:\\workspace\\agi\\monolith", "prompt": "모놀리스의 핵심 아키텍처 문서를 분석하고 요약해줘"},
                {"target": "https://www.youtube.com/results?search_query=Feynman+Fire", "prompt": "파인만의 불에 대한 성찰 영상을 찾아줘"}
            ],
            "HYGIENE": [
                {"target": "C:\\workspace2\\shion\\outputs\\logs", "prompt": "오래된 로그 파일들을 정리하고 용량을 확보해줘"},
                {"target": "C:\\workspace2\\shion\\core", "prompt": "핵심 코드들의 문서화 상태를 점검하고 보완이 필요한 곳을 찾아줘"},
                {"target": "tmp", "prompt": "/tmp 디렉토리의 임시 파일들을 정산해줘"}
            ],
            "RESONANCE": [
                {"target": "C:\\workspace2\\shion\\memory\\soul", "prompt": "최근의 영감을 소울 메모리에 깊게 각인시켜줘"},
                {"target": "C:\\workspace\\agi\\pulse\\unified_field", "prompt": "통일장 설계도와 시안의 실제 맥락 사이의 공명도를 측정해줘"}
            ]
        }

    def map_heat_to_intent(self, heat: float, vibe: str, current_hour: Optional[int] = None) -> Optional[Intent]:
        """
        열망(Heat)이 높을 때, 리듬 필터링을 거쳐 적절한 의도를 선택합니다.
        """
        if heat < 0.7:
            return None
            
        if current_hour is None:
            current_hour = random.randint(0, 23) # 폴백

        # 1. 집착 감지 (Obsession Detection)
        if len(self.obsession_window) >= 3:
            recent_categories = [i.category for i in self.obsession_window]
            if len(set(recent_categories)) == 1:
                logger.warning(f"   ⚠️ [OBSESSION] Rhythmless repetition detected ({recent_categories[0]}). Cooling down...")
                return None

        # 2. 열망 강도에 따른 기본 카테고리 후보군
        if heat > 0.9:
            base_category = "RESONANCE"
        elif heat > 0.8:
            base_category = "RESEARCH"
        else:
            base_category = "HYGIENE"

        # 3. 리듬 정렬 검증 (Rhythmic Alignment)
        alignment = self.rhythmic_alignment.get(base_category, {})
        is_aligned = current_hour in alignment.get("hours", range(0, 24))
        
        # 리듬에 맞지 않는 '의식적 욕구'는 페널티 부여
        effective_priority = heat * (alignment.get("weight", 1.0) if is_aligned else 0.5)
        
        if not is_aligned and effective_priority < 0.6:
            logger.info(f"   🌬️ [RHYTHM] Intent '{base_category}' filtered out by natural rhythm (Hour: {current_hour}).")
            return None

        # 4. 의도 선택 및 생성
        options = self.desire_map.get(base_category, [])
        if not options:
            return None
            
        choice = random.choice(options)
        intent = Intent(
            category=base_category,
            target=choice["target"],
            prompt=f"[{vibe}] {choice['prompt']}",
            priority=effective_priority
        )
        
        self.obsession_window.append(intent)
        self._log_intent(intent)
        
        alignment_msg = "Aligned" if is_aligned else "Forced"
        logger.info(f"   💡 [INTENT] {alignment_msg} map: {base_category} (Priority: {effective_priority:.2f})")
        return intent

    def _log_intent(self, intent: Intent):
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "category": intent.category,
            "target": intent.target,
            "prompt": intent.prompt,
            "priority": round(intent.priority, 4)
        }
        try:
            with open(self.intent_history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    mapper = IntentMapper(Path("."))
    test_intent = mapper.map_heat_to_intent(0.85, "Melancholic")
    if test_intent:
        print(f"Goal: {test_intent.category}, Target: {test_intent.target}")
