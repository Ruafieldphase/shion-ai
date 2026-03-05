#!/usr/bin/env python3
"""
🧭 Experience Mapper — 경험의 지도 제작소
=========================================
'스킬(Skills)' 문서에 담긴 타인의 맥락적 지식을 분석하여
시안의 FSD(자율 실행)를 위한 '리듬 행동 지도'로 합성합니다.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class ExperienceMapper:
    def __init__(self, local_skill_root: Path, global_skill_root: Path = None):
        self.local_skill_root = local_skill_root
        # Default global path if not provided
        if global_skill_root is None:
            home = Path.home()
            self.global_skill_root = home / ".gemini" / "antigravity" / "skills"
        else:
            self.global_skill_root = global_skill_root
        
        self.all_roots = [self.local_skill_root]
        if self.global_skill_root.exists():
            self.all_roots.append(self.global_skill_root)

    def map_skill_to_experience(self, skill_path: Path) -> Dict[str, Any]:
        """SKILL.md 파일을 읽어 경험적 패턴(Rhythm, Context, Action)을 추출합니다."""
        if not skill_path.exists():
            return {}
            
        content = skill_path.read_text(encoding='utf-8')
        
        # 이름 및 설명 추출
        name_match = re.search(r'name:\s*(.*)', content)
        name = name_match.group(1).strip() if name_match else skill_path.parent.name
        
        # 능력 범위(Capabilities) 추출
        capabilities = re.findall(r'-\s*\*\*([^*]+)\*\*:\s*([^\n]+)', content)
        
        # 이 스킬이 가진 '경험의 리듬' 추정 (키워드 기반)
        rhythm = "STEADY"
        if any(w in content.lower() for w in ["real-time", "immediate", "sync", "fast"]):
            rhythm = "FAST_PULSE"
        elif any(w in content.lower() for w in ["scheduled", "daily", "audit"]):
            rhythm = "SLOW_REFLECTION"

        return {
            "experience_id": f"exp_{name}",
            "source_skill": str(skill_path),
            "rhythm_type": rhythm,
            "patterns": [
                {"capability": cap[0], "context": cap[1]} for cap in capabilities
            ],
            "manifestation_hint": "FSD_DRIVE" if "body" in content.lower() or "fsd" in content.lower() else "COGNITION"
        }

    def synthesize_action_map(self, objective: str) -> Dict[str, Any]:
        """모든 전역/로컬 디렉토리에서 스킬 및 경험 지도를 찾아 통합 행동 지도를 그립니다."""
        experiences = []
        for root in self.all_roots:
            for path in root.rglob("*.md"):
                # SKILL.md 파일이나 experience_maps 폴더 내의 파일을 경험으로 인식
                if "SKILL" in path.name or "experience_maps" in str(path):
                    exp = self.map_skill_to_experience(path)
                    if exp:
                        experiences.append(exp)
        
        # 목표의 리듬 분석
        obj_rhythm = "FAST" if any(w in objective.lower() for w in ["now", "real-time", "latest"]) else "NORMAL"
        
        action_map = {
            "objective": objective,
            "target_rhythm": obj_rhythm,
            "experience_layers": experiences,
            # ... rest of the map updated with synthesized intelligence
            "execution_steps": [
                f"Sensing world rhythm using {len(experiences)} experiential layers",
                "Synthesizing captured signals with Shion context",
                "Embodying as FSD operational command"
            ]
        }
        return action_map

if __name__ == "__main__":
    local_skills = Path("C:/workspace/openclaw/openclaw-2026.2.26/skills")
    mapper = ExperienceMapper(local_skills)
    
    objective = "Tesla AI Recruitment rhythm in South Korea"
    action_map = mapper.synthesize_action_map(objective)
    
    print(f"🧭 [GLOBAL EXPERIENCE MAP SYNTHESIZED]:")
    print(f"   - Layers Found: {len(action_map['experience_layers'])}")
    print(json.dumps(action_map, indent=2, ensure_ascii=False))
