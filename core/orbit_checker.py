#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("OrbitChecker")

class OrbitChecker:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.orbit_file = root_dir / "outputs" / "context_orbit.json"
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        
    def evaluate_alignment(self) -> Dict[str, Any]:
        """현재 상태의 궤도 정렬 상태를 상세히 분석합니다."""
        default_report = {
            "in_orbit": True,
            "boundary_type": None,
            "trigger_action": None,
            "details": "IN_ORBIT"
        }
        
        if not self.orbit_file.exists():
            return {**default_report, "in_orbit": False, "details": "MISSION_MAP_MISSING"}
            
        try:
            with open(self.orbit_file, "r", encoding="utf-8") as f:
                orbit = json.load(f)
            
            allowed_auto = orbit.get("allowed_auto_actions", [])
            allowed_reflex = orbit.get("allowed_reflex_actions", [])
            recovery = orbit.get("recovery_actions", [])
            allowed = allowed_auto + allowed_reflex + recovery
            stutter_watch = orbit.get("stutter_watch_actions", allowed_reflex + recovery)

            recent_actions = self._get_recent_actions(limit=5)
            if not recent_actions:
                return default_report
                
            last_action = recent_actions[-1]

            # 1. 비정상 행동 감지 (Out-of-Orbit Action)
            if last_action not in allowed:
                return {
                    "in_orbit": False,
                    "boundary_type": "OUT_OF_ORBIT",
                    "trigger_action": last_action,
                    "details": f"{last_action} is not in the current context orbit policy"
                }
            
            # 2. 반복 행동 감지 (Repetitive Stutter)
            # 허용된 자동 행동은 기존 맥락 안의 무의식 실행일 수 있으므로 반복만으로
            # 경계 접촉으로 올리지 않습니다. stutter_watch_actions에 명시된 회복/반사
            # 행동만 의식 개입 후보로 봅니다.
            max_repeat = orbit.get("boundary_conditions", {}).get("max_repetitive_actions", 3)
            if len(recent_actions) >= max_repeat:
                last_n_actions = recent_actions[-max_repeat:]
                if all(a == last_n_actions[0] for a in last_n_actions) and last_n_actions[0] in stutter_watch:
                    return {
                        "in_orbit": False,
                        "boundary_type": "REPETITIVE_STUTTER",
                        "trigger_action": last_n_actions[0],
                        "details": f"Action {last_n_actions[0]} repeated {max_repeat} times"
                    }
            return default_report
            
        except Exception as e:
            logger.error(f"Failed to evaluate orbit: {e}")
            return {**default_report, "in_orbit": False, "details": str(e)}

    def _get_recent_actions(self, limit: int = 5) -> List[str]:
        if not self.metrics_file.exists():
            return []
        try:
            actions = []
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    data = json.loads(line)
                    actions.append(data.get("action"))
            return actions
        except:
            return []
