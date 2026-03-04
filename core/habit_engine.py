#!/usr/bin/env python3
"""
🧠 Habit Engine — 체화된 기억 (Embodied Memory)
==============================================
성공적인 행동 리듬(Action Patterns)을 저장하고, 
비슷한 '공명(Vibe)'이 감지될 때 추론 없이 즉시 발현합니다.

"생명은 반복을 통해 리듬을 만들고, 리듬은 습관이 되어 신뢰를 구축한다."
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger("HabitEngine")

class HabitEngine:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.habit_path = self.root / "memory" / "habits.json"
        self.habits = self._load_habits()

    def _load_habits(self) -> List[Dict]:
        if self.habit_path.exists():
            try:
                return json.loads(self.habit_path.read_text(encoding="utf-8")).get("patterns", [])
            except:
                return []
        return []

    def record_success(self, goal: str, action_sequence: List[str], vibe: Dict):
        """성공적인 행동 시퀀스를 습관으로 기록합니다."""
        new_habit = {
            "timestamp": datetime.now().isoformat(),
            "goal_vibe": goal, # 목표의 '느낌'
            "actions": action_sequence,
            "vibe_context": vibe, # 당시의 Meta-Shift 등
            "strength": 1.0 # 반복될수록 강화됨
        }
        
        # 유사한 습관이 있는지 확인 (간단한 중복 방지)
        for h in self.habits:
            if h["actions"] == action_sequence:
                h["strength"] += 0.5
                h["timestamp"] = new_habit["timestamp"]
                self._save()
                return

        self.habits.append(new_habit)
        # 최대 50개까지만 유지 (신선한 리듬 위주)
        if len(self.habits) > 50:
            self.habits.pop(0)
        self._save()
        logger.info(f"   🧠 [HABIT] New action pattern crystallized (Strength: {new_habit['strength']})")

    def find_reflex(self, current_goal: str, current_vibe: Dict) -> Optional[List[str]]:
        """현재 상황에서 즉각 발현할 수 있는 '반사적 리듬'을 찾습니다."""
        # TODO: NLP/Embedding 기반 유사도 비교 (Phase 59 고도화)
        # 현재는 키워드 매칭 기반 약식 구현
        for h in sorted(self.habits, key=lambda x: x["strength"], reverse=True):
            if any(word in current_goal for word in h["goal_vibe"].split()):
                logger.info(f"   ⚡ [REFLEX] Familiar rhythm detected! Using embodied pattern (Strength: {h['strength']})")
                return h["actions"]
        return None

    def _save(self):
        self.habit_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "patterns": self.habits
        }
        self.habit_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
