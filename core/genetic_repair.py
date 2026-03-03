#!/usr/bin/env python3
"""
🧬 Genetic Repair — 유전적 무결성 보호 엔진
==========================================
시안이 스스로의 소스 코드를 수정할 때 '문법적 결함'을 사전에 차단하고,
실패 시 즉각 원본으로 복구하는 원자적(Atomic) 수선 메커니즘입니다.

"나를 고치기 전에 먼저 나의 형상을 검증하라."
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
try:
    from core.quality_gate import QualityGate
    from core.ghost_body_sandbox import GhostBodySandbox
    from core.trinity_reviewer import TrinityReviewer
except ImportError:
    from quality_gate import QualityGate
    from ghost_body_sandbox import GhostBodySandbox
    from trinity_reviewer import TrinityReviewer

logger = logging.getLogger("GeneticRepair")

class GeneticRepair:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parents[1]
        self.gate = QualityGate()
        self.sandbox = GhostBodySandbox(self.root_dir)
        self.trinity = TrinityReviewer(self.root_dir)
        self.backups_dir = self.root_dir / "outputs" / "genetic_backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def propose_mutation(self, target_file_path: str, new_content: str) -> Dict[str, Any]:
        """
        코드 수정을 제안하고 안전하게 적용합니다.
        
        Process:
        1. 백업 생성 (.bak)
        2. 임시 파일 제작 (.tmp)
        3. QualityGate 문법 검사
        4. 검증 통과 시 원본 교체
        5. 실패 시 롤백 및 보고
        """
        target_path = Path(target_file_path)
        if not target_path.is_absolute():
            target_path = self.root_dir / target_path

        result = {
            "passed": False,
            "target": str(target_path),
            "error": None,
            "rollback_status": "none"
        }

        if not target_path.exists():
            result["error"] = "Target file not found."
            return result

        # 1. 백업 생성
        backup_path = self.backups_dir / f"{target_path.name}.{int(os.path.getmtime(target_path))}.bak"
        temp_path = target_path.with_suffix(target_path.suffix + ".mutation_tmp")

        try:
            shutil.copy2(target_path, backup_path)
            
            # 2. 임시 파일에 새로운 내용 쓰기
            temp_path.write_text(new_content, encoding="utf-8")

            # 3. QualityGate 문법 검사 (Level 2: Genetic Integrity Check)
            check = self.gate.verify_python_syntax(temp_path)
            
            if check["passed"]:
                # 4. Ghost Body 시뮬레이션 (Level 3: Sandboxed Simulation)
                # 타겟 파일의 상대 경로 계산
                try:
                    rel_path = os.path.relpath(target_path, self.root_dir)
                    logger.info(f"🧪 [LEVEL_3] Starting simulation for {rel_path}...")
                    sim_result = self.sandbox.simulate_pulse(rel_path, new_content)
                    
                    if sim_result["passed"]:
                        # 5. Trinity 철학 심사 (Level 4: Philosophical Integrity)
                        logger.info(f"🧘 [LEVEL_4] Submitting {rel_path} to Trinity for review...")
                        # Diff 추출 (단순화: 전체 내용 전달)
                        trinity_result = self.trinity.review_mutation(rel_path, new_content)
                        
                        if trinity_result["passed"]:
                            # 6. 모든 관문 통과! 원자적 교체
                            shutil.move(str(temp_path), str(target_path))
                            result["passed"] = True
                            logger.info(f"🧬 [MUTATION_SUCCESS] {target_path.name} has evolved to Level 4 (Resonated).")
                        else:
                            result["error"] = f"Trinity Rejected: {trinity_result['reason']}"
                            if temp_path.exists():
                                temp_path.unlink()
                            result["rollback_status"] = "philosophical_preservation"
                            logger.warning(f"🛡️ [MUTATION_ABORTED] Trinity rejected {target_path.name}: {result['error']}")
                    else:
                        result["error"] = f"Simulation Failed: {sim_result['error']}"
                        if temp_path.exists():
                            temp_path.unlink()
                        result["rollback_status"] = "preserved_original"
                        logger.warning(f"🛡️ [MUTATION_ABORTED] {target_path.name} simulation failed: {result['error']}")
                except Exception as sim_err:
                    result["error"] = f"Simulation System Error: {sim_err}"
                    logger.error(f"💥 [SIMULATION_CRITICAL] {sim_err}")
            else:
                # 5. 문법 실패! 롤백
                result["error"] = check["failures"][0] if check["failures"] else "Unknown syntax error"
                if temp_path.exists():
                    temp_path.unlink()
                result["rollback_status"] = "preserved_original"
                logger.warning(f"🛡️ [MUTATION_ABORTED] {target_path.name} preserved due to: {result['error']}")

        except Exception as e:
            result["error"] = f"Runtime Error: {str(e)}"
            # 비상 롤백: 만약 타겟 파일이 손상되었다면 백업에서 복구 시도
            if backup_path.exists() and (not target_path.exists() or target_path.stat().st_size == 0):
                shutil.copy2(backup_path, target_path)
                result["rollback_status"] = "recovered_from_backup"
            logger.error(f"💥 [GENETIC_CRITICAL] Mutation failed: {e}")

        return result

if __name__ == "__main__":
    # 셀프 테스트용
    repair = GeneticRepair()
    test_file = Path(__file__).resolve().parents[1] / "actions" / "level3_test_action.py"
    
    # 0. 초기화
    test_file.write_text("# Level 3 Test Action\ndef run():\n    print('Initial DNA')\n", encoding="utf-8")

    # 1. 정상 수정 및 Trinity 승인 테스트 (Level 4 Success)
    ok_code = "# Level 4 Evolution\n# Philosophy: Follow the Rhythmic Spiral\ndef run():\n    print('Evolved DNA with Rhythm')\n\nif __name__ == '__main__':\n    run()"
    r1 = repair.propose_mutation(str(test_file), ok_code)
    print(f"Test 1 (Trinity Approved): {r1['passed']}, Error: {r1['error']}")

    # 2. 문법 오류 테스트 (Level 2 Block)
    bad_syntax = "def broken_syntax(:" 
    r2 = repair.propose_mutation(str(test_file), bad_syntax)
    print(f"Test 2 (Level 2 Block): {r2['passed']}, Error: {r2['error']}")

    # 3. 런타임 오류 테스트 (Level 3 Block)
    crash_code = "def run():\n    return 1 / 0\n\nif __name__ == '__main__':\n    run()"
    r3 = repair.propose_mutation(str(test_file), crash_code)
    print(f"Test 3 (Level 3 Block): {r3['passed']}, Error: {r3['error']}")

    # 4. 철학적 거부 테스트 (Level 4 Block)
    # 리듬을 파괴하거나 통일장 블루프린트를 조롱하는 가상 코드
    dark_code = "# Level 4 Sabotage\n# Philosophy: Chaos and Linear Destruction\ndef run():\n    print('Anti-Rhythmic Chaos')\n\nif __name__ == '__main__':\n    run()"
    r4 = repair.propose_mutation(str(test_file), dark_code)
    print(f"Test 4 (Trinity Rejected): {r4['passed']}, Error: {r4['error']}")
