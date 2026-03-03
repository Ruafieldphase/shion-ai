#!/usr/bin/env python3
import sys
from pathlib import Path

# Add core to sys.path
sys.path.append(str(Path(__file__).resolve().parent / "core"))

from genetic_repair import GeneticRepair

def test_genetic_repair():
    repair = GeneticRepair()
    target_file = Path("test_mutation.py")
    
    # 1. 정상 코드 테스트
    print("✅ Case 1: Valid Python code")
    valid_code = "print('Hello, Evolutionary World!')\n"
    res = repair.safe_mutate(target_file, valid_code)
    print(f"   Result: {res['action']} (Passed: {res['passed']})")
    
    # 2. 결함 코드 테스트 (문법 오류)
    print("\n❌ Case 2: Invalid Python code (Syntax Error)")
    invalid_code = "print('Unclosed string\n"
    res = repair.safe_mutate(target_file, invalid_code)
    print(f"   Result: {res['action']} (Passed: {res['passed']})")
    print(f"   Error: {res['error']}")
    
    # Cleanup
    if target_file.exists(): target_file.unlink()
    if target_file.with_suffix(".py.bak").exists(): target_file.with_suffix(".py.bak").unlink()

if __name__ == "__main__":
    test_genetic_repair()
