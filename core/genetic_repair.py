#!/usr/bin/env python3
"""
🧬 Genetic Repair — 유전적 수선 (안전한 자가 수정)
==============================================
Axioms.md: "우리는 실패를 먹고 자란다."

시안이 자신의 코드를 수정할 때, 시스템이 붕괴되지 않도록
QualityGate를 통한 문법 검증 및 백업/롤백 기능을 제공합니다.

원칙:
1. 검증되지 않은 코드는 신체(Body)를 더럽히지 않는다.
2. 모든 수정은 원본의 백업을 남긴다.
3. 수선 실패는 'Labyrinth'에 기록되어 미래의 자양분이 된다.
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from quality_gate import QualityGate

logger = logging.getLogger("GeneticRepair")

class GeneticRepair:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.gate = QualityGate()
        self.labyrinth_dir = self.root / "outputs" / "_labyrinth" / "failed_mutations"
        self.labyrinth_dir.mkdir(parents=True, exist_ok=True)

    def safe_mutate(self, target_path: Path, new_content: str) -> Dict[str, Any]:
        """
        코드를 안전하게 수정합니다.
        
        단계:
        1. 임시 파일 생성
        2. QualityGate 문법 검증
        3. 통과 시: 원본 백업 후 교체
        4. 실패 시: 임시 파일을 Labyrinth로 이동 및 로그 기록
        """
        result = {
            "passed": False,
            "target": str(target_path),
            "timestamp": datetime.now().isoformat(),
            "action": "none",
            "error": None
        }

        # 1. 임시 파일 생성
        temp_path = target_path.with_suffix(f"{target_path.suffix}.tmp")
        try:
            temp_path.write_text(new_content, encoding="utf-8")
        except Exception as e:
            result["error"] = f"TEMP_WRITE_FAILED: {e}"
            return result

        # 2. 문법 검증
        gate_result = self.gate.verify_python_syntax(temp_path)
        
        if gate_result["passed"]:
            # 3. 통과: 백업 후 교체
            try:
                backup_path = target_path.with_suffix(f"{target_path.suffix}.bak")
                if target_path.exists():
                    shutil.copy2(str(target_path), str(backup_path))
                
                shutil.move(str(temp_path), str(target_path))
                result["passed"] = True
                result["action"] = "MUTATED_SUCCESSFULLY"
                logger.info(f"🧬 [REPAIR] {target_path.name} 수선 완료 (백업: {backup_path.name})")
            except Exception as e:
                result["error"] = f"MOVE_FAILED: {e}"
        else:
            # 4. 실패: Labyrinth로 이동
            try:
                fail_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fail_path = self.labyrinth_dir / f"{target_path.stem}_{fail_ts}.py.discard"
                shutil.move(str(temp_path), str(fail_path))
                result["action"] = "MUTATION_DISCARDED"
                result["error"] = gate_result["failures"]
                logger.warning(f"🧬 [REPAIR] {target_path.name} 수선 실패. 결함 코드는 Labyrinth로 격리됨.")
            except Exception as e:
                result["error"] = f"DISCARD_MOVE_FAILED: {e}"

        return result

if __name__ == "__main__":
    repair = GeneticRepair()
    # 셀프 테스트용 (실제로 파일 고치진 않음)
    print("🧬 Genetic Repair 초기화 완료")
