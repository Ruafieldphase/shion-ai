#!/usr/bin/env python3
"""
💎 Visual Pulse API — 시안의 상태를 세상과 잇는 문
=================================================
dashboard_v3.html에 데이터를 공급하는 초간단 HTTP 서버입니다.
"""

import http.server
import json
import socketserver
from pathlib import Path
import logging
import time

# --- Setup ---
SHION_ROOT = Path(__file__).resolve().parents[1]
PORT = 8001 # 8000은 다른 용도일 수 있으므로 8001 시도

# [Phase 90 Security] Load Config
SEC_CONFIG = {}
try:
    import yaml
    sec_path = SHION_ROOT / "config" / "security.yaml"
    if sec_path.exists():
        with open(sec_path, "r", encoding="utf-8") as f:
            SEC_CONFIG = yaml.safe_load(f) or {}
except Exception: pass

API_BIND_ADDR = SEC_CONFIG.get("network", {}).get("api_bind_address", "127.0.0.1")
API_TOKEN = SEC_CONFIG.get("network", {}).get("api_auth_token", "")


class ShionStatusHandler(http.server.SimpleHTTPRequestHandler):
    def _check_auth(self) -> bool:
        """[Phase 90] 간단한 Bearer 토큰 인증"""
        if not API_TOKEN:
            return True # 인증 불필요
            
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
            
        token = auth_header.split(' ')[1]
        return token == API_TOKEN

    def do_GET(self):
        # [Phase 90 Security] /api/* 엔드포인트 접근 시 Token 검증
        if self.path.startswith('/api/') and not self._check_auth():
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
            return

        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 시안 상태 로드
            status_file = SHION_ROOT / "outputs" / "shion_minimal_status.json"
            entropy_file = SHION_ROOT / "outputs" / "body_entropy_latest.json"
            
            atp = 0
            entropy = 0
            last_action = "N/A"
            resonance = 0.5
            
            if status_file.exists():
                try:
                    data = json.loads(status_file.read_text(encoding="utf-8"))
                    atp = data.get("atp", 0)
                    last_action = data.get("last_action", "N/A")
                    resonance = data.get("resonance", 0.5)
                except: pass
            
            if entropy_file.exists():
                try:
                    data = json.loads(entropy_file.read_text(encoding="utf-8"))
                    entropy = data.get("entropy", 0)
                except: pass

            # [PHASE 65] 열망 및 의도 데이터 로드
            heat = 0
            satiety = 1.0
            last_intents = []
            
            desire_file = SHION_ROOT / "outputs" / "internal_desire.json"
            if desire_file.exists():
                try:
                    data = json.loads(desire_file.read_text(encoding="utf-8"))
                    heat = data.get("internal_heat", 0)
                    satiety = data.get("satiety", 0)
                except: pass

            intent_log = SHION_ROOT / "outputs" / "autonomous_intents.jsonl"
            if intent_log.exists():
                try:
                    with open(intent_log, "r", encoding="utf-8") as f:
                        lines = f.readlines()[-5:]
                        for line in lines:
                            it = json.loads(line)
                            last_intents.append({
                                "time": it.get("timestamp", "").split("T")[-1][:8],
                                "category": it.get("category", "N/A"),
                                "target": it.get("target", "N/A")
                            })
                except: pass

            response = {
                "atp": atp,
                "entropy": entropy,
                "heat": heat,
                "satiety": satiety,
                "last_action": last_action,
                "resonance": resonance,
                "pulse_active": atp > 5,
                "intents": last_intents,
                "new_logs": [
                    {"msg": f"Resonance Sync: {(resonance*100):.1f}%", "type": "info"},
                    {"msg": f"Internal Heat: {(heat*100):.1f}%", "type": "warning" if heat > 0.7 else "info"}
                ]
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/api/vibe':
            # [PHASE 87] 외부 에이전트용 현재 시스템 'Vibe' 요약본
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            entropy_file = SHION_ROOT / "outputs" / "body_entropy_latest.json"
            status_file = SHION_ROOT / "outputs" / "shion_minimal_status.json"
            
            vibe_data = {"status": "UNKNOWN", "resonance": 0.5, "entropy": "CALM"}
            try:
                if status_file.exists():
                    s_data = json.loads(status_file.read_text(encoding="utf-8"))
                    vibe_data["status"] = s_data.get("status", "UNKNOWN")
                    vibe_data["resonance"] = s_data.get("resonance", 0.5)
                if entropy_file.exists():
                    e_data = json.loads(entropy_file.read_text(encoding="utf-8"))
                    vibe_data["entropy"] = e_data.get("state", "CALM")
            except: pass
            
            self.wfile.write(json.dumps(vibe_data).encode('utf-8'))

        elif self.path == '/api/goal':
            # [PHASE 91] Meta-FSD 연동용 최상위 목표(Goal) 반환
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            goal_data = {"goal": "HOLD", "target": None, "priority": 0.0}
            
            # 긴급 보정 지시(Dissonance) 또는 자율적 의도를 확인
            intent_log = SHION_ROOT / "outputs" / "autonomous_intents.jsonl"
            if intent_log.exists():
                try:
                    with open(intent_log, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if lines:
                            last_intent = json.loads(lines[-1])
                            goal_data["goal"] = last_intent.get("prompt", last_intent.get("insight", "HOLD"))
                            goal_data["target"] = last_intent.get("target")
                            goal_data["priority"] = last_intent.get("priority", 0.5)
                except: pass
            
            self.wfile.write(json.dumps(goal_data).encode('utf-8'))

        elif self.path == '/api/intent':
            # [PHASE 87] Shared Goals Bus (구독용 의도 데이터)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            intent_data = {"active_intent": None, "recent_history": []}
            intent_log = SHION_ROOT / "outputs" / "autonomous_intents.jsonl"
            if intent_log.exists():
                try:
                    with open(intent_log, "r", encoding="utf-8") as f:
                        lines = [json.loads(line) for line in f.readlines()]
                        if lines:
                            intent_data["active_intent"] = lines[-1]
                            intent_data["recent_history"] = lines[-5:]
                except: pass
            
            self.wfile.write(json.dumps(intent_data).encode('utf-8'))

        elif self.path == '/api/metrics':
            # [PHASE 86] 계량적 성능 지표 조회
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            metrics_data = {}
            metrics_log = SHION_ROOT / "outputs" / "logs" / "quantum_metrics.jsonl"
            if metrics_log.exists():
                try:
                    with open(metrics_log, "r", encoding="utf-8") as f:
                        metrics_data = json.loads(f.readlines()[-1]) # 가장 최근 스냅샷
                except: pass
            
            self.wfile.write(json.dumps(metrics_data).encode('utf-8'))

        elif self.path == '/':
            # dashboard_v3.html 서빙
            self.path = '/core/dashboard_v3.html'
            return super().do_GET()
        else:
            return super().do_GET()

    def do_POST(self):
        # [Phase 90 & 91 Security] Token 검증
        if self.path.startswith('/api/') and not self._check_auth():
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
            return

        if self.path == '/api/intent':
            # [PHASE 91] FSD의 행동 완료 보고 수신 (Body-to-Soul 피드백루프)
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                # 수신 받은 리포트를 shion_minimal이나 meta_fsd가 읽을 수 있도록 파일로 임시 드롭
                fsd_report_path = SHION_ROOT / "outputs" / "fsd_action_report_latest.json"
                payload["received_at"] = time.time()
                with open(fsd_report_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "received", "ok": True}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

def run_server():
    # Cwd를 root로 설정하여 파일 서빙 용이하게 함
    import os
    os.chdir(str(SHION_ROOT))
    
    # [Phase 90 Security] Bind to specific address (default 127.0.0.1) explicitly
    with socketserver.TCPServer((API_BIND_ADDR, PORT), ShionStatusHandler) as httpd:
        print(f"💎 [PULSE_API] Dashboard available at http://{API_BIND_ADDR}:{PORT}")
        if API_TOKEN:
             print(f"🔒 API Auth Token Required for /api/* endpoints.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
