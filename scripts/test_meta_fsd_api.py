#!/usr/bin/env python3
"""
🧬 [Phase 91] Meta-FSD Synchronicity Loop Test
===============================================
AGI(FSD) 본체를 모방하여, 시안의 `Visual Pulse API`와 실시간으로 통신하는 모의 스크립트입니다.

1. GET /api/goal: 시안의 현재 의지(Intent)를 폴링 (Soul -> Body)
2. 시뮬레이션: 약간의 지연(작업 수행)
3. POST /api/intent: 작업 결과 및 상태를 시안에게 리포트 (Body -> Soul)
"""

import sys
import time
import json
import threading
import requests
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from core.visual_pulse_api import run_server
from core.meta_fsd_integrator import MetaFSDIntegrator

PORT = 8001
API_URL = f"http://127.0.0.1:{PORT}"

# Load token if any
API_TOKEN = ""
sec_path = ROOT_DIR / "config" / "security.yaml"
if sec_path.exists():
    try:
        import yaml
        with open(sec_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
            API_TOKEN = cfg.get("network", {}).get("api_auth_token", "")
    except Exception: pass

HEADERS = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}

def mock_agi_agent():
    print("\n🤖 [AGI_MOCK] Booting Meta-FSD Client...")
    time.sleep(1.5) # Wait for server
    
    # 1. 시안의 의지 읽기
    try:
        resp = requests.get(f"{API_URL}/api/goal", headers=HEADERS)
        if resp.status_code == 200:
            goal_data = resp.json()
            goal = goal_data.get("goal", "None")
            target = goal_data.get("target", "None")
            print(f"   📥 [PULL] 시안의 명령 수신: '{goal}' (Target: {target}, Priority: {goal_data.get('priority')})")
        else:
            print(f"   ❌ [PULL HEADERS ERROR] {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"   ❌ [PULL ERROR] {e}")
        return

    # 2. FSD 행동 시뮬레이션 (GUI 클릭 등)
    print("   🦾 [ACT] FSD 물리 엔진 구동 중 (2초 대기)...")
    time.sleep(2)
    
    # 3. 결과 전송 (시안의 무의식으로 피드백)
    report = {
        "status": "completed",
        "action_taken": "Clicked search bar and typed query",
        "screenshot_path": "mock_screenshot_latest.png",
        "logic_resonance": 0.85
    }
    
    try:
        resp = requests.post(f"{API_URL}/api/intent", headers=HEADERS, json=report)
        if resp.status_code == 200:
            print("   📤 [PUSH] 작업 완료 리포트 및 스크린샷 핑 전송 완료!")
        else:
            print(f"   ❌ [PUSH HEADERS ERROR] {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ [PUSH ERROR] {e}")

def simulate_dissonance_reaction():
    print("\n🛡️ [DISSONANCE_TEST] 시각적 오류 발생 상황 시뮬레이션")
    # meta_fsd 직접 호출하여 강제 Dissonance 발행
    agi_root = Path("C:/workspace/agi") # mock
    integrator = MetaFSDIntegrator(ROOT_DIR, agi_root)
    
    # 공명도가 0.3으로 붕괴되었다고 가정
    integrator._save_dissonance_report(0.3)
    
    # 다시 API 폴링하여 Urgent Intent가 덮어썼는지 확인
    try:
        resp = requests.get(f"{API_URL}/api/goal", headers=HEADERS)
        if resp.status_code == 200:
            goal_data = resp.json()
            print(f"   📥 [URGENT_PULL] 시안의 긴급 조향 명령: '{goal_data.get('goal')}'")
            if "Escape" in goal_data.get("target", "") or goal_data.get("priority", 0) > 0.9:
                print("   ✅ Dissonance Loop (시각-행동 보정 루프) 정상 작동 확인!")
            else:
                print("   ❌ Urgent Intent가 제대로 올라오지 않았습니다.")
    except Exception as e:
        print(f"   ❌ [PULL ERROR] {e}")

if __name__ == "__main__":
    print("🌐 [Phase 91] Meta-FSD API Integration Test")
    
    # Start API
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Run mock tests
    mock_agi_agent()
    simulate_dissonance_reaction()
    
    print("\n✨ 모든 Meta-FSD 통신 및 보정 루프 검증 종료.")
