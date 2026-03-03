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

class ShionStatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
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

            response = {
                "atp": atp,
                "entropy": entropy,
                "last_action": last_action,
                "resonance": resonance,
                "pulse_active": atp > 5, # 에너지가 있으면 박동
                "new_logs": [
                    {"msg": f"Resonance Sync: {(resonance*100):.1f}%", "type": "info"},
                    {"msg": f"Labyrinth Navigation: ACTIVE", "type": "success"}
                ]
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/':
            # dashboard_v3.html 서빙
            self.path = '/core/dashboard_v3.html'
            return super().do_GET()
        else:
            return super().do_GET()

def run_server():
    # Cwd를 root로 설정하여 파일 서빙 용이하게 함
    import os
    os.chdir(str(SHION_ROOT))
    
    with socketserver.TCPServer(("", PORT), ShionStatusHandler) as httpd:
        print(f"💎 [PULSE_API] Dashboard available at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
