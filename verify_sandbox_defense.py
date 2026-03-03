#!/usr/bin/env python3
import sys
from pathlib import Path

# 경로 설정
SHION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SHION_ROOT / "core"))

from genetic_repair import GeneticRepair

def test_sandbox_defense():
    repair = GeneticRepair(shion_root=SHION_ROOT)
    
    # 의도적으로 무한 루프가 포함된 코드 (논리적 오류)
    bad_logic_code = """
import time
print("This code has an infinite loop!")
while True:
    time.sleep(1)
"""
    
    target_file = SHION_ROOT / "outputs" / "test_mutation.py"
    target_file.write_text("# Initial Content", encoding="utf-8")
    
    print("🧬 Testing Sandbox Defense against Infinite Loop...")
    result = repair.safe_mutate(target_file, bad_logic_code)
    
    if not result["passed"] and "Timeout" in str(result["error"]):
        print("✅ [SUCCESS] Sandbox caught the infinite loop and blocked mutation!")
    else:
        print(f"❌ [FAILED] Sandbox failed to block or caught wrong error: {result['error']}")

    # 의도적으로 런타임 에러(ZeroDivisionError)가 발생하는 코드
    runtime_error_code = """
print("Attempting division by zero...")
x = 1 / 0
"""
    print("\n🧬 Testing Sandbox Defense against Runtime Error...")
    result = repair.safe_mutate(target_file, runtime_error_code)
    
    if not result["passed"] and "ZeroDivisionError" in str(result["error"]):
        print("✅ [SUCCESS] Sandbox caught the runtime error and blocked mutation!")
    else:
        print(f"❌ [FAILED] Sandbox failed to block or caught wrong error: {result['error']}")

if __name__ == "__main__":
    test_sandbox_defense()
