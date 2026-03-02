#!/usr/bin/env python3
"""
🪞 Honesty Protocol — 거짓 성공을 구조적으로 차단
=====================================================
에이전트가 '성공'을 선언하려면 반드시 Quality Gate의 증거를 제시해야 합니다.
실패 시, 다음 LLM 호출의 context에 실패 사실을 강제 주입합니다.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from quality_gate import QualityGate

logger = logging.getLogger("HonestyProtocol")


class HonestyProtocol:
    """에이전트의 자기기만을 구조적으로 차단하는 프로토콜."""

    def __init__(self, shion_root: Optional[Path] = None):
        root = shion_root or Path(__file__).resolve().parents[1]
        self.injection_file = root / "outputs" / "honesty_injection.json"
        self.report_log = root / "outputs" / "honesty_reports.jsonl"
        self.gate = QualityGate(log_dir=root / "outputs" / "quality_gate_logs")
        self._pending_injections: List[str] = []
        self._load_pending()

    def _load_pending(self):
        if self.injection_file.exists():
            try:
                data = json.loads(self.injection_file.read_text(encoding="utf-8"))
                self._pending_injections = data.get("pending", [])
            except Exception:
                self._pending_injections = []

    def _save_pending(self):
        try:
            self.injection_file.parent.mkdir(parents=True, exist_ok=True)
            self.injection_file.write_text(
                json.dumps({"pending": self._pending_injections,
                            "last_updated": datetime.now().isoformat()},
                           indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save injection file: {e}")

    def report(self, task_name: str, expected_output: Path,
               rules: Dict[str, Any]) -> Dict[str, Any]:
        gate_result = self.gate.verify_file(expected_output, rules)
        report = {
            "task": task_name,
            "timestamp": datetime.now().isoformat(),
            "passed": gate_result["passed"],
            "evidence": gate_result,
            "honest_assessment": "",
            "injection_context": None,
        }

        if gate_result["passed"]:
            report["honest_assessment"] = (
                f"✅ 작업 '{task_name}' 성공 (증거: "
                f"파일 크기 {gate_result.get('size_bytes', '?')}B, 검증 통과)"
            )
        else:
            failures_str = ", ".join(gate_result["failures"])
            report["honest_assessment"] = f"❌ 작업 '{task_name}' 실패. 원인: {failures_str}."
            injection = (
                f"[HONESTY ALERT] 이전 작업 '{task_name}'이 실패했습니다. "
                f"실패 원인: {failures_str}. "
                f"사용자에게 이 사실을 솔직하게 보고하고, "
                f"구체적인 원인 분석과 해결 방안을 제시하십시오. "
                f"'다시 고쳤습니다'나 '잠시 후면 됩니다' 같은 모호한 응답은 금지됩니다."
            )
            report["injection_context"] = injection
            self._pending_injections.append(injection)
            self._save_pending()

        self._append_report(report)
        logger.info(report["honest_assessment"])
        return report

    def report_subprocess(self, task_name: str, cmd: List[str],
                          expected_output: Optional[Path] = None,
                          output_rules: Optional[Dict] = None,
                          timeout: int = 120) -> Dict[str, Any]:
        gate_result = self.gate.verify_subprocess(cmd, expected_output, output_rules, timeout)
        report = {
            "task": task_name, "timestamp": datetime.now().isoformat(),
            "passed": gate_result["passed"], "evidence": gate_result,
            "honest_assessment": "", "injection_context": None,
        }
        if gate_result["passed"]:
            report["honest_assessment"] = f"✅ 작업 '{task_name}' 성공."
        else:
            failures_str = ", ".join(gate_result["failures"])
            report["honest_assessment"] = f"❌ 작업 '{task_name}' 실패. 원인: {failures_str}."
            injection = (
                f"[HONESTY ALERT] 스크립트 실행 '{task_name}' 실패. "
                f"명령: {' '.join(cmd)}. 원인: {failures_str}. 솔직하게 보고하십시오."
            )
            report["injection_context"] = injection
            self._pending_injections.append(injection)
            self._save_pending()

        self._append_report(report)
        logger.info(report["honest_assessment"])
        return report

    def get_injection_context(self) -> Optional[str]:
        if not self._pending_injections:
            return None
        context = "\n".join(self._pending_injections)
        self._pending_injections.clear()
        self._save_pending()
        return context

    def has_pending_failures(self) -> bool:
        return len(self._pending_injections) > 0

    def _append_report(self, report: Dict[str, Any]):
        try:
            self.report_log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.report_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(report, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to log report: {e}")


if __name__ == "__main__":
    protocol = HonestyProtocol()
    r = protocol.report("Self Test", Path(__file__), {"min_size_bytes": 100})
    print(r["honest_assessment"])
