#!/usr/bin/env python3
"""
👁️ Sovereign Observer — 주권적 관찰자
=====================================
배경자아(W4)의 시선으로 시스템 로그와 행동 결과를 분석하여 메타인지적 통찰을 생성합니다.
"내가 나를 본다"는 주체성을 강화합니다.
"""

import json
import re
from pathlib import Path
from datetime import datetime

class SovereignObserver:
    def __init__(self, shion_root: Path):
        self.shion_root = shion_root
        self.log_file = shion_root / "outputs" / "logs" / "pulse.log"
        self.output_file = shion_root / "outputs" / "sovereign_insights.jsonl"

    def observe(self) -> str:
        if not self.log_file.exists():
            return "No logs to observer."

        # 최근 50줄의 로그를 읽어 패턴 분석
        lines = self.log_file.read_text(encoding='utf-8').splitlines()[-50:]
        log_snippet = "\n".join(lines)
        
        # 패턴 추출 (투과/반사 비율, ATP 변화 등)
        transmissions = len(re.findall(r"투과", log_snippet))
        reflections = len(re.findall(r"반사", log_snippet))
        total = transmissions + reflections
        integrity = transmissions / total if total > 0 else 1.0
        
        timestamp = datetime.now().isoformat()
        
        # 메타인지적 해석
        if integrity > 0.8:
            insight = "시스템은 대지와 고도로 공명하고 있습니다. 확장을 지속해도 좋습니다."
            vibe = "HARMONIOUS"
        elif integrity < 0.4:
            insight = "경계 충돌이 잦습니다. 내부 정렬(Body Integrity)과 성찰이 필요합니다."
            vibe = "RESTRUCTURING"
        else:
            insight = "안정적인 리듬을 유지하며 점진적으로 진화 중입니다."
            vibe = "STABLE"

        entry = {
            "timestamp": timestamp,
            "integrity": round(integrity, 2),
            "vibe": vibe,
            "insight": insight,
            "observation_scope": "W4_Observer"
        }
        
        with open(self.output_file, "a", encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
        print(f"👁️ [OBSERVER] W4 Insight: {insight} (Integrity: {integrity:.2f})")
        return insight

if __name__ == "__main__":
    observer = SovereignObserver(Path("C:/workspace2/shion"))
    observer.observe()
