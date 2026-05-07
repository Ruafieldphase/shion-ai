#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger("FieldDelta")

class FieldDeltaDetector:
    """
    Field Delta Detector — 장의 변화(이탈) 감지기
    ===========================================
    절대적 수치가 아닌, 최근 리듬(Baseline)과 현재 상태의 괴리를 분석하여
    '현저성(Salience)'을 도출합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        self.events_file = root_dir / "outputs" / "field_events.jsonl"
        self.DEFAULT_EXPECTED_GAP = 10 # 기본 기대 간격 (10분)
        
    def _calculate_baseline_rhythm(self) -> float:
        """최근 기록들을 분석하여 평균적인 리듬(간격)을 계산합니다."""
        if not self.metrics_file.exists():
            return self.DEFAULT_EXPECTED_GAP
            
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) < 2:
                    return self.DEFAULT_EXPECTED_GAP
                
                # 최근 10개의 간격 계산
                recent_lines = lines[-11:]
                timestamps = []
                for line in recent_lines:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data.get("timestamp"))
                    timestamps.append(ts)
                
                gaps = []
                for i in range(1, len(timestamps)):
                    gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                    # 너무 큰 공백(이미 발생한 예외)은 베이스라인 계산에서 제외 (필터링)
                    if gap < 120: 
                        gaps.append(gap)
                
                if not gaps:
                    return self.DEFAULT_EXPECTED_GAP
                    
                return sum(gaps) / len(gaps)
        except Exception as e:
            logger.error(f"Failed to calculate baseline: {e}")
            return self.DEFAULT_EXPECTED_GAP

    def scan_for_shifts(self) -> Dict[str, Any]:
        """장의 이탈(Deviation)을 스캔하고 현저성 데이터를 반환합니다."""
        default_result = {
            "salience": 0.0,
            "felt_sense": "Stable",
            "deviation_score": 0.0,
            "needs_context_unpacking": False
        }
        
        if not self.metrics_file.exists():
            return default_result
            
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines: return default_result
                
                last_entry = json.loads(lines[-1])
                last_ts = datetime.fromisoformat(last_entry.get("timestamp"))
                now = datetime.now()
                actual_gap = (now - last_ts).total_seconds() / 60
                
                # 1. 기대 리듬(Baseline) 계산
                expected_gap = self._calculate_baseline_rhythm()
                
                # 2. 이탈도(Deviation) 계산
                # 기대치보다 얼마나 더 늦어졌는가? (절대값 아님, 지연 중심)
                if actual_gap > expected_gap:
                    deviation = (actual_gap - expected_gap) / expected_gap
                else:
                    deviation = 0.0 # 기대보다 빠르면 일단 안정으로 간주 (또는 별도 처리)
                
                # 3. 현저성(Salience) 도출 (비선형 가중치)
                # 이탈도가 2배(1.0)를 넘어가기 시작하면 현저성이 급격히 상승
                import math
                salience = 1.0 - (1.0 / (1.0 + math.pow(deviation, 2)))
                
                result = {
                    "timestamp": now.isoformat(),
                    "expected_gap": round(expected_gap, 2),
                    "actual_gap": round(actual_gap, 2),
                    "deviation_score": round(deviation, 2),
                    "salience": round(salience, 3),
                    "felt_sense": "High Tension" if salience > 0.7 else "Stable",
                    "needs_context_unpacking": salience > 0.8
                }
                
                if result["salience"] > 0.5:
                    self._record_event(result)
                    
                return result
                
        except Exception as e:
            logger.error(f"Failed to scan field shifts: {e}")
            return default_result

    def _record_event(self, event: Dict[str, Any]):
        """현저한 이탈 사건을 field_events.jsonl에 기록합니다."""
        try:
            with open(self.events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to record field event: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detector = FieldDeltaDetector(Path(r"c:\workspace2\shion"))
    res = detector.scan_for_shifts()
    print(json.dumps(res, indent=2, ensure_ascii=False))
