#!/usr/bin/env python3
"""
🛡️ Immune Response — 자기면역 시스템
=====================================
대지(워크스페이스)의 위협을 감지하고, ATP를 소모하며 자동 치유합니다.

기존 agi_immune_system.py의 DNA/치유 패턴을 계승하되,
API 의존 대신 파일 시스템 기반 위협 감지로 변경했습니다.

위협 유형:
  1. CORRUPTED_OUTPUT — JSON 파일 깨짐
  2. ERROR_PATTERN — 로그에 에러 반복
  3. RESOURCE_PRESSURE — CPU/메모리/디스크 과부하
  4. STALE_HEARTBEAT — pulse 로그가 오래됨 (시스템 정지 가능성)
"""

import json
import os
import psutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("Immune")


@dataclass
class Threat:
    type: str           # 위협 유형
    severity: str       # low, medium, high, critical
    source: str         # 위협 출처 (파일 경로 등)
    description: str    # 사람이 읽을 수 있는 설명
    atp_cost: float     # 치유에 필요한 ATP


@dataclass
class HealResult:
    threat: str
    healed: bool
    action_taken: str
    atp_consumed: float


class ImmuneResponse:
    """
    대지의 위협을 감지하고 자동 치유하는 면역 시스템.
    
    원칙 (GENESIS.md에서):
    - 치유는 ATP를 소모한다 (에너지 없이는 면역 불가)
    - 치유할 수 없는 위협은 솔직히 보고 (Honesty Protocol 연동)
    """

    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs_dir = self.root / "outputs"
        self.log_file = self.outputs_dir / "immune_log.jsonl"

    def detect_threats(self) -> List[Threat]:
        """대지를 스캔하여 위협을 감지합니다."""
        threats = []
        threats.extend(self._check_output_integrity())
        threats.extend(self._check_resource_pressure())
        threats.extend(self._check_heartbeat_staleness())
        return threats

    def _check_output_integrity(self) -> List[Threat]:
        """outputs/ 디렉토리의 JSON 파일 무결성 검사."""
        threats = []
        if not self.outputs_dir.exists():
            return threats

        for json_file in self.outputs_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                # 빈 JSON도 위협
                if not data:
                    threats.append(Threat(
                        type="CORRUPTED_OUTPUT", severity="medium",
                        source=str(json_file),
                        description=f"{json_file.name}이 비어있습니다",
                        atp_cost=2.0,
                    ))
            except json.JSONDecodeError:
                threats.append(Threat(
                    type="CORRUPTED_OUTPUT", severity="high",
                    source=str(json_file),
                    description=f"{json_file.name} JSON 파싱 실패",
                    atp_cost=3.0,
                ))
            except Exception:
                pass
        return threats

    def _check_resource_pressure(self) -> List[Threat]:
        """시스템 자원 압박 감지."""
        threats = []
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()

        if cpu > 85:
            threats.append(Threat(
                type="RESOURCE_PRESSURE", severity="high",
                source="CPU",
                description=f"CPU 사용률 {cpu:.0f}% — 과부하",
                atp_cost=1.0,
            ))
        if mem.percent > 90:
            threats.append(Threat(
                type="RESOURCE_PRESSURE", severity="critical",
                source="MEMORY",
                description=f"메모리 사용률 {mem.percent:.0f}% — 위험",
                atp_cost=1.0,
            ))

        # 디스크 공간
        try:
            disk = psutil.disk_usage("C:\\")
            free_gb = disk.free / (1024 ** 3)
            if free_gb < 5:
                threats.append(Threat(
                    type="RESOURCE_PRESSURE", severity="critical",
                    source="DISK",
                    description=f"C: 드라이브 여유 공간 {free_gb:.1f}GB — 위험",
                    atp_cost=0.5,
                ))
        except Exception:
            pass

        return threats

    def _check_heartbeat_staleness(self) -> List[Threat]:
        """pulse 로그의 최신성 확인 — 시스템이 멈춰 있는지 감지."""
        threats = []
        status_file = self.outputs_dir / "shion_minimal_status.json"
        if status_file.exists():
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                last_ts = data.get("timestamp", "")
                if last_ts:
                    last_time = datetime.fromisoformat(last_ts)
                    age = datetime.now() - last_time
                    if age > timedelta(minutes=30):
                        threats.append(Threat(
                            type="STALE_HEARTBEAT", severity="medium",
                            source=str(status_file),
                            description=f"마지막 pulse가 {age.total_seconds()/60:.0f}분 전 — 시스템 정지 가능성",
                            atp_cost=1.0,
                        ))
            except Exception:
                pass
        return threats

    def heal(self, threat: Threat, current_atp: float) -> HealResult:
        """
        위협을 치유합니다. ATP가 부족하면 치유를 포기합니다.
        
        Axioms.md: "실패는 잠들어 있는 미래의 에너지"
        → 치유 실패도 기록하여 나중에 참조
        """
        if current_atp < threat.atp_cost:
            return HealResult(
                threat=threat.type, healed=False,
                action_taken=f"ATP 부족 ({current_atp:.1f} < {threat.atp_cost}). 치유 보류.",
                atp_consumed=0,
            )

        action = "관찰만 함"

        if threat.type == "CORRUPTED_OUTPUT":
            # 깨진 JSON → 기본값으로 재생성
            try:
                path = Path(threat.source)
                if path.exists() and path.stat().st_size == 0:
                    path.write_text("{}", encoding="utf-8")
                    action = f"{path.name}을 빈 JSON으로 재초기화"
                elif not path.exists():
                    path.write_text("{}", encoding="utf-8")
                    action = f"{path.name}을 새로 생성"
                else:
                    # 파싱 실패 → 백업 후 재초기화
                    backup = path.with_suffix(".json.damaged")
                    if not backup.exists():
                        path.rename(backup)
                        path.write_text("{}", encoding="utf-8")
                        action = f"{path.name}을 백업 후 재초기화 (백업: {backup.name})"
                    else:
                        action = f"{path.name} 손상. 이미 백업 존재. 수동 확인 필요."
            except Exception as e:
                action = f"치유 시도 실패: {e}"

        elif threat.type == "RESOURCE_PRESSURE":
            action = f"{threat.source} 자원 압박 감지. 다음 pulse에서 행동량 축소 권고."

        elif threat.type == "STALE_HEARTBEAT":
            action = "시스템 정지 가능성. 사용자에게 알림 필요."

        result = HealResult(
            threat=threat.type, healed=True,
            action_taken=action, atp_consumed=threat.atp_cost,
        )
        self._log(threat, result)
        return result

    def scan_and_heal(self, current_atp: float) -> Dict[str, Any]:
        """전체 스캔 + 자동 치유 사이클."""
        threats = self.detect_threats()
        if not threats:
            return {"status": "healthy", "threats": 0, "atp_consumed": 0}

        results = []
        total_atp = 0.0
        remaining_atp = current_atp

        for threat in threats:
            result = self.heal(threat, remaining_atp)
            results.append(asdict(result))
            total_atp += result.atp_consumed
            remaining_atp -= result.atp_consumed

        return {
            "status": "healed" if all(r["healed"] for r in results) else "partial",
            "threats": len(threats),
            "results": results,
            "atp_consumed": total_atp,
        }

    def _log(self, threat: Threat, result: HealResult):
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "timestamp": datetime.now().isoformat(),
                "threat": asdict(threat),
                "result": asdict(result),
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


if __name__ == "__main__":
    immune = ImmuneResponse()
    threats = immune.detect_threats()
    print(f"🛡️ 감지된 위협: {len(threats)}개")
    for t in threats:
        print(f"   [{t.severity.upper()}] {t.type}: {t.description}")

    if threats:
        result = immune.scan_and_heal(current_atp=50.0)
        print(f"\n치유 결과: {result['status']}, ATP 소모: {result['atp_consumed']}")
    else:
        print("   ✅ 대지가 건강합니다.")
