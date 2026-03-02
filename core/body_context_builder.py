#!/usr/bin/env python3
"""
🫀 Body Context Builder — 시스템 '체감 상태'를 LLM에 연결
==========================================================
ATP, Entropy, CPU 등의 수치를 읽어서 LLM의 system prompt에
주입할 수 있는 문자열로 변환합니다. SUNS의 '혈관'.
"""

import json
import psutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("BodyContext")


class BodyContextBuilder:
    """시스템의 물리적 상태를 읽어 LLM 프롬프트에 주입할 문맥을 생성."""

    def __init__(self, shion_root: Optional[Path] = None):
        root = shion_root or Path(__file__).resolve().parents[1]
        outputs = root / "outputs"
        self.mito_path = outputs / "mitochondria_state.json"
        self.entropy_path = outputs / "body_entropy_latest.json"
        self.honesty_path = outputs / "honesty_injection.json"

    def _read_json_safe(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def read_body_state(self) -> Dict[str, Any]:
        mito = self._read_json_safe(self.mito_path)
        entropy = self._read_json_safe(self.entropy_path)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()

        return {
            "atp_level": mito.get("atp_level",
                         mito.get("momentum", mito.get("symmetry", 0.5)) * 50),
            "atp_status": mito.get("status", mito.get("integrity_status", "unknown")),
            "entropy": entropy.get("entropy", 0.0),
            "entropy_state": entropy.get("state", "unknown"),
            "cpu_percent": cpu_percent,
            "memory_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024**3), 1),
            "timestamp": datetime.now().isoformat(),
        }

    def build(self) -> str:
        state = self.read_body_state()
        lines = []

        atp = state["atp_level"]
        if isinstance(atp, (int, float)):
            if atp < 20:
                lines.append(f"⚡ 에너지 위험: ATP {atp:.0f}/100. 간결하게 답하고 새 작업을 시작하지 마시오.")
            elif atp < 40:
                lines.append(f"⚡ 에너지 부족: ATP {atp:.0f}/100. 필수 작업에만 집중하시오.")
            elif atp > 80:
                lines.append(f"⚡ 에너지 충분: ATP {atp:.0f}/100. 창의적 확장 가능.")
            else:
                lines.append(f"⚡ 에너지 안정: ATP {atp:.0f}/100.")

        entropy = state["entropy"]
        if entropy > 0.7:
            lines.append(f"🌡️ 시스템 불안정: Entropy {entropy:.2f}. 파일 I/O를 최소화하시오.")
        elif entropy > 0.3:
            lines.append(f"🌡️ 시스템 활성: Entropy {entropy:.2f}.")

        cpu = state["cpu_percent"]
        mem_pct = state["memory_percent"]
        if cpu > 80 or mem_pct > 85:
            lines.append(f"🖥️ 자원 경고: CPU {cpu:.0f}%, 메모리 {mem_pct:.0f}%. 무거운 작업 지양.")

        honesty = self._read_json_safe(self.honesty_path)
        pending = honesty.get("pending", [])
        if pending:
            lines.append(f"🪞 [정직성 경고] 이전 실패 {len(pending)}건 미보고:")
            for msg in pending[:3]:
                lines.append(f"   - {msg}")

        if not lines:
            return "[BODY STATUS] 모든 시스템 정상."
        return "[BODY STATUS]\n" + "\n".join(lines)

    def build_for_sampling(self) -> Dict[str, Any]:
        state = self.read_body_state()
        atp = state.get("atp_level", 50)
        entropy = state.get("entropy", 0.3)

        if atp < 20:
            return {"suggested_behavior": "minimal",
                    "directive": "최소한의 토큰으로 핵심만 전달하시오.",
                    "max_output_hint": "짧게"}
        elif atp > 80 and entropy < 0.3:
            return {"suggested_behavior": "expansive",
                    "directive": "충분한 에너지와 안정성. 깊이 있는 사고 가능.",
                    "max_output_hint": "자유"}
        else:
            return {"suggested_behavior": "balanced",
                    "directive": "주어진 작업에 집중하되, 불필요한 확장은 피하시오.",
                    "max_output_hint": "적절"}


if __name__ == "__main__":
    builder = BodyContextBuilder()
    print(builder.build())
