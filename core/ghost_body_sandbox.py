#!/usr/bin/env python3
"""
👻 Ghost Body Sandbox — 가상 시나리오 시뮬레이션 엔진
===================================================
Level 3 진화의 핵심인 '가상 신체' 구축 모듈입니다.
수정된 코드가 실제 시스템에 반영되기 전, 고립된 환경에서 
미리 1회 박동(Pulse)을 실행하여 안정성을 리허설합니다.
"""

import os
import shutil
import subprocess
import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("GhostBody")

class GhostBodySandbox:
    def __init__(self, original_root: Optional[Path] = None):
        self.original_root = original_root or Path(__file__).resolve().parents[1]
        self.sandbox_root = Path("C:/tmp/shion_sandbox")
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        
    def create_ghost_body(self):
        """본체의 주요 구조를 샌드박스로 복제합니다."""
        logger.info(f"👻 Creating Ghost Body in {self.sandbox_root}...")
        
        # 복제할 핵심 폴더 목록
        core_folders = ["core", "actions", "config", "scripts"]
        
        for folder in core_folders:
            src = self.original_root / folder
            dst = self.sandbox_root / folder
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        
        # outputs 폴더는 최소 구조만 생성 (이전 기록 오염 방지)
        (self.sandbox_root / "outputs" / "logs").mkdir(parents=True, exist_ok=True)
        
        # 대지 상태 파일 및 더미 환경 구축 (필요 시)
        logger.info("✅ Ghost Body structure prepared.")

    def simulate_pulse(self, target_file_rel_path: str, mutated_content: str, timeout: int = 60) -> Dict[str, Any]:
        """수정된 코드로 가상 박동을 시뮬레이션합니다."""
        self.create_ghost_body()
        
        # 1. 수정된 코드 반영
        mutated_path = self.sandbox_root / target_file_rel_path
        mutated_path.write_text(mutated_content, encoding="utf-8")
        
        result = {
            "passed": False,
            "metrics": {},
            "error": None,
            "stdout": "",
            "stderr": ""
        }
        
        # 2. 가상 박동 또는 파일 직접 실행
        logger.info(f"🧪 Simulating execution for {target_file_rel_path}...")
        try:
            # 타겟이 actions/ 폴더에 있으면 직접 실행, 그렇지 않으면 shion_minimal 실행
            if target_file_rel_path.startswith("actions"):
                cmd = [sys.executable, str(self.sandbox_root / target_file_rel_path)]
            else:
                cmd = [sys.executable, str(self.sandbox_root / "core" / "shion_minimal.py"), "--once"]
            
            # PYTHONPATH를 샌드박스 루트로 설정하여 독립 실행 보장
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.sandbox_root)
            
            proc = subprocess.run(
                cmd, 
                cwd=str(self.sandbox_root), 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                env=env,
                encoding="utf-8",
                errors="replace"
            )
            
            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr
            
            if proc.returncode == 0:
                result["passed"] = True
                logger.info("✨ Ghost Body Pulse SUCCESS. Stability verified.")
                # 시뮬레이션 후 생성된 메트릭 분석 (예: ATP 소모량 등)
                result["metrics"] = self._analyze_sandbox_outputs()
            else:
                result["error"] = f"Runtime Crash in Sandbox: {proc.stderr[:300]}"
                logger.warning(f"🛡️ Ghost Body Pulse FAILED. Mutation rejected: {result['error']}")

        except subprocess.TimeoutExpired:
            result["error"] = "TIMEOUT: Possible infinite loop detected in mutated code."
            logger.error("🛑 Ghost Body Pulse TIMEOUT. CRITICAL mutation rejected.")
        except Exception as e:
            result["error"] = f"Simulation Error: {str(e)}"
            logger.error(f"💥 Simulation failed: {e}")

        return result

    def _analyze_sandbox_outputs(self) -> Dict[str, Any]:
        """샌드박스 실행 결과 생성된 파일들을 분석하여 미세 튜닝의 근거를 찾습니다."""
        metrics = {}
        # 예: 가상 ATP 상태 확인
        mito_file = self.sandbox_root / "outputs" / "mitochondria_state.json"
        if mito_file.exists():
            try:
                metrics["atp"] = json.loads(mito_file.read_text(encoding="utf-8"))
            except: pass
        return metrics

if __name__ == "__main__":
    # 셀프 테스트
    sandbox = GhostBodySandbox()
    # 정상 시뮬레이션 테스트
    test_content = Path("C:/workspace2/shion/core/shion_minimal.py").read_text(encoding="utf-8")
    test_content += "\n# Ghost Body Test Comment"
    r = sandbox.simulate_pulse("core/shion_minimal.py", test_content)
    print(f"Simulation Result: {r['passed']}, Error: {r['error']}")
