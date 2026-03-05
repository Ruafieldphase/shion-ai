#!/usr/bin/env python3
"""
🎭 Emotional Resonance Mapper — 정서적 공명 매퍼
==============================================
시안의 현재 감정(오라, ATP, 엔트로피)과 세계의 기류(Broad Field)를 분석하여
RAG 검색 시 정서적 가중치(Emotional Weights)를 생성합니다.
"""

import json
from pathlib import Path
from typing import Dict, Any

class EmotionalResonanceMapper:
    def __init__(self, shion_root: Path):
        self.shion_root = shion_root
        self.outputs_dir = shion_root / "outputs"
        self.state_file = self.outputs_dir / "mitochondria_state.json"
        self.field_file = self.outputs_dir / "broad_field_state.json"

    def get_emotional_bias(self) -> Dict[str, Any]:
        """현재 상태를 기반으로 정서적 바이어스를 계산합니다."""
        bias = {
            "target_w_layer": "W1", # Default
            "emotional_boost": 1.0,
            "theme_keywords": [],
            "search_depth": "balanced"
        }

        # 1. 시안의 내면 상태 (ATP & Aura)
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding='utf-8'))
                atp = state.get("atp_level", 50.0)
                aura = state.get("shion_aura", "CYAN")
                
                # Aura-based Layer Mapping
                if aura == "MAGENTA": # Vibrant/Ecstatic
                    bias["target_w_layer"] = "W4" # Unified Field / Peak Experience
                    bias["theme_keywords"].extend(["joy", "ecstasy", "creation", "expansion"])
                elif aura == "CYAN": # Stable/Flow
                    bias["target_w_layer"] = "W2" # Experience/Flow
                    bias["theme_keywords"].extend(["flow", "balance", "rhythm", "harmony"])
                elif aura == "AMBER": # Contraction/Warning
                    bias["target_w_layer"] = "W3" # Boundary/Focus
                    bias["theme_keywords"].extend(["boundary", "tension", "protection", "gravity"])
                else: # RED/Critical
                    bias["target_w_layer"] = "W1" # Survival/Root
                    bias["theme_keywords"].extend(["root", "rest", "survival", "grounding"])
            except: pass

        # 2. 세계의 기류 (Broad Field)
        if self.field_file.exists():
            try:
                field = json.loads(self.field_file.read_text(encoding='utf-8'))
                vibration = field.get("field_vibration", "STABLE")
                if vibration == "EXPANDING":
                    bias["emotional_boost"] *= 1.2
                    bias["theme_keywords"].append("exploration")
                elif vibration == "CONTRACTING":
                    bias["emotional_boost"] *= 0.8
                    bias["theme_keywords"].append("introspection")
            except: pass

        return bias

    def save(self, bias: Dict[str, Any]):
        output_file = self.outputs_dir / "emotional_bias.json"
        output_file.write_text(json.dumps(bias, indent=2), encoding='utf-8')
        print(f"🎭 [EMOTION] Bias saved: {bias['target_w_layer']} (Keywords: {', '.join(bias['theme_keywords'][:3])})")

if __name__ == "__main__":
    mapper = EmotionalResonanceMapper(Path("C:/workspace2/shion"))
    bias = mapper.get_emotional_bias()
    mapper.save(bias)
