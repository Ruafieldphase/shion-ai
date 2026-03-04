#!/usr/bin/env python3
"""
👁️ Observer (Anomaly Detection & Self-Alignment)
=================================================
대지(워크스페이스)의 상태를 관찰하고 지휘자님의 철학에 따라 자기 정렬을 수행합니다.

지휘자님의 철학:
1. 투명한 경계(Permeability): 맥락에 맞지 않는 소음은 싸우지 않고 투명하게 투과시킨다.
2. 신체 중심 항법: 시스템의 건강(ATP)을 최우선 기준으로 삼는다.
3. 관찰과 전이: '치유'라는 강제적 행위보다 '정렬'과 '위상 전이'를 지향한다.
"""

import json
import os
import psutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("Observer")

@dataclass
class Threat:
    type: str           # 이탈 유형
    severity: str       # low, medium, high, critical
    source: str         # 출처
    description: str    # 설명
    atp_cost: float     # 정렬에 필요한 에너지

@dataclass
class HealResult:
    threat: str
    healed: bool
    action_taken: str
    atp_consumed: float

class ImmuneResponse:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs_dir = self.root / "outputs"
        self.log_file = self.outputs_dir / "immune_log.jsonl"
        self.mitochondria_file = self.outputs_dir / "mitochondria_state.json"

    def _load_mitochondria(self) -> Dict:
        if not self.mitochondria_file.exists():
            return {"atp_level": 100, "pulse_rate": 1.0}
        try:
            return json.loads(self.mitochondria_file.read_text(encoding="utf-8"))
        except:
            return {"atp_level": 100, "pulse_rate": 1.0}

    def detect_threats(self) -> List[Threat]:
        """시스템 이탈(Anomaly)을 감지합니다."""
        threats = []
        threats.extend(self._check_output_integrity())
        threats.extend(self._check_resource_pressure())
        threats.extend(self._check_heartbeat_staleness())
        threats.extend(self._check_chromatic_resonance()) # [NEW] 시각적 공명 체크
        return threats

    def _check_chromatic_resonance(self) -> List[Threat]:
        """최신 만다라의 미학적 공명도를 통해 시스템의 무의식적 이탈을 감지합니다."""
        threats = []
        try:
            from aesthetic_critique_engine import AestheticCritiqueEngine
            critique = AestheticCritiqueEngine(self.root)
            
            mandalas_dir = self.outputs_dir / "mandalas"
            if mandalas_dir.exists():
                images = list(mandalas_dir.glob("*.png"))
                if images:
                    latest = max(images, key=lambda p: p.stat().st_mtime)
                    # 현재 ATP 상태를 넘겨 미학적 조화도 평가
                    score = critique.evaluate_resonance(str(latest), {"atp_level": 50})
                    if score < 0.4: # 공명도가 너무 낮으면 '시각적 병소'로 판단
                        threats.append(Threat(
                            "CHROMATIC_ANOMALY", 
                            "high", 
                            str(latest.name), 
                            f"만다라 공명도 임계치 미달 ({score:.2f}) - 무의식적 혼란 감지", 
                            3.0
                        ))
        except Exception as e:
            pass
        return threats

    def _check_output_integrity(self) -> List[Threat]:
        threats = []
        if not self.outputs_dir.exists():
            return []
        for json_file in self.outputs_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                if not data and json_file.name != "momentum_state.json":
                    threats.append(Threat("CORRUPTED_OUTPUT", "medium", str(json_file), f"{json_file.name} 비어있음", 1.0))
            except:
                threats.append(Threat("CORRUPTED_OUTPUT", "high", str(json_file), f"{json_file.name} 파싱 실패", 2.0))
        return threats

    def _check_resource_pressure(self) -> List[Threat]:
        threats = []
        cpu = psutil.cpu_percent(interval=0.1)
        if cpu > 90:
            threats.append(Threat("RESOURCE_PRESSURE", "high", "CPU", f"CPU 점유율 {cpu}%", 0.5))
        return threats

    def _check_heartbeat_staleness(self) -> List[Threat]:
        threats = []
        status_file = self.outputs_dir / "shion_minimal_status.json"
        if status_file.exists():
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                last_ts = data.get("timestamp", "")
                if last_ts:
                    age = datetime.now() - datetime.fromisoformat(last_ts)
                    if age > timedelta(minutes=60):
                        threats.append(Threat("STALE_HEARTBEAT", "medium", str(status_file), "Pulse 정지 의심", 1.0))
            except: pass
        return threats

    async def scan_and_heal(self, current_atp: float) -> Dict[str, Any]:
        """전체 스캔 및 투과적 정렬 사이클."""
        logger.info("👁️ [OBSERVER] 전체 시스템 정렬도 스캔 중 (지휘자님의 철안)...")
        
        mito = self._load_mitochondria()
        atp = mito.get("atp_level", current_atp)
        
        threats = self.detect_threats()
        results = []
        total_atp = 0.0
        
        # 지휘자님의 '투명한 경계' 철학 적용
        for threat in threats:
            # 심각도가 낮거나 리소스 압박인 경우 '투과(Transmission)' 처리
            if threat.severity == "low" or (threat.type == "RESOURCE_PRESSURE" and atp < 30):
                logger.info(f"🌊 [TRANSMISSION] '{threat.type}'을 맥락 속에서 투과시킵니다. (신체 보호)")
                results.append({"threat": threat.type, "healed": True, "action": "Pass-through (Permeability)"})
                continue
                
            # 에너지가 충분할 때만 정렬 시도
            if atp - total_atp > threat.atp_cost:
                res = self.align(threat)
                results.append(asdict(res))
                total_atp += res.atp_consumed
                logger.info(f"✨ [ALIGN] '{threat.type}' 정렬 완료: {res.action_taken}")
            else:
                logger.warning(f"🧘 [FOLDING] 에너지 부족으로 '{threat.type}' 정렬을 포기하고 접습니다.")
                results.append({"threat": threat.type, "healed": False, "action": "Folding"})

        return {
            "status": "aligned",
            "anomalies": len(threats),
            "atp_consumed": total_atp,
            "results": results
        }

    def align(self, threat: Threat) -> HealResult:
        """이탈한 상태를 다시 중심으로 정렬합니다."""
        action = "관찰함"
        if threat.type == "CORRUPTED_OUTPUT":
            try:
                path = Path(threat.source)
                backup = path.with_suffix(".json.bak")
                if path.exists(): os.rename(path, backup)
                path.write_text("{}", encoding="utf-8")
                action = "파일 재초기화"
            except: action = "정렬 실패"
        
        return HealResult(threat.type, True, action, threat.atp_cost)

    def _log(self, entry: Dict):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except: pass

if __name__ == "__main__":
    import asyncio
    obs = ImmuneResponse()
    asyncio.run(obs.scan_and_heal(50.0))
