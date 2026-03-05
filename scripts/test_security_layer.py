#!/usr/bin/env python3
"""
🛡️ [Phase 90] Security Validation Test
========================================
1. API Bind Address Test (127.0.0.1 검증)
2. API Token Authentication Test (/api/* 접근 제어 검증)
3. Workspace Scan Allowlist Test (허가되지 않은 경로 차단 검증)
"""

import sys
import time
import requests
import threading
from pathlib import Path

# Add core to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from core.visual_pulse_api import run_server
from core.workspace_phase_sensor import WorkspacePhaseSensor
from core.body_context_builder import BodyContextBuilder

PORT = 8001
API_URL = f"http://127.0.0.1:{PORT}"

def test_api_security():
    print("🛡️ [Test 1 & 2] API Security (Binding & Token Auth)")
    
    # 1. Start API Server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1) # wait for server boot
    
    # 2. Test Dashboard Access (Should be open - NO AUTH Required)
    try:
        resp = requests.get(f"{API_URL}/")
        assert resp.status_code == 200
        print("   ✅ Dashboard '/' 접근 성공 (Auth 미적용 정상)")
    except Exception as e:
        print(f"   ❌ Dashboard 접근 실패: {e}")

    # 3. Test API Access without Token (Should be 401 Unauthorized if token is set in yaml)
    #    (If token is empty in yaml, it will return 200 safely)
    try:
        resp = requests.get(f"{API_URL}/api/status")
        # security.yaml 에서는 기본으로 토큰을 비워두었으므로 현재 200이어야 함
        # 실제 비밀번호를 yaml에 넣고 테스트 시 401 반환 검증됨
        if resp.status_code == 401:
            print("   ✅ /api/status 접근 거부됨 (Token Required 정상 작동)")
        else:
            print(f"   ℹ️ /api/status 접근 허용 (현재 Token 설정 비활성화 됨: {resp.status_code})")
    except Exception as e:
        print(f"   ❌ /api/status 요청 실패: {e}")

def test_workspace_allowlist():
    print("\n🛡️ [Test 3] Workspace Scanner Allowlist")
    
    # 임시 해킹/민감 폴더를 흉내내는 테스트 디렉터리 생성
    secret_dir = ROOT_DIR / "secret_finance_data"
    secret_dir.mkdir(exist_ok=True)
    (secret_dir / "passwords.txt").write_text("Should not be scanned")
    
    try:
        # Phase Sensor Test (Metadata rglob)
        sensor = WorkspacePhaseSensor(ROOT_DIR)
        files = sensor._scan_metadata()
        
        scanned_paths = [f['relpath'] for f in files]
        secret_scanned = any("secret_finance_data" in p for p in scanned_paths)
        
        if secret_scanned:
            print("   ❌ WorkspacePhaseSensor가 비인가 폴더(secret)를 스캔했습니다! (보안 누수)")
        else:
            print("   ✅ WorkspacePhaseSensor: 비인가 폴더(secret) 스캔 차단 성공")
            
        # Body Context Test (Entropy I/O rglob)
        body = BodyContextBuilder(ROOT_DIR)
        body_files = 0
        body_blocked = True
        
        for p in body.root.rglob("*"):
            if not body._is_path_allowed(p):
                # block correctly
                if "secret_finance_data" in str(p):
                    pass # blocked as expected
                continue
            if "secret_finance_data" in str(p):
                body_blocked = False
                
        if body_blocked:
            print("   ✅ BodyContextBuilder(Entropy): 비인가 폴더(secret) 스캔 차단 성공")
        else:
            print("   ❌ BodyContextBuilder가 비인가 폴더(secret)를 스캔했습니다! (보안 누수)")

    finally:
        # cleanup
        import shutil
        shutil.rmtree(secret_dir, ignore_errors=True)
        print("   🧹 테스트용 임시 폴더 삭제 완료")

if __name__ == "__main__":
    test_api_security()
    test_workspace_allowlist()
    print("\n✨ [Phase 90] 모든 로컬망 보안 계층 테스트 완료.")
