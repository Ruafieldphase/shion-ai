import json
import logging
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AmbientServer")

PORT = 8081
ROOT_DIR = Path(r"c:\workspace2\shion\outputs\ambient_presence")
ENTROPY_FILE = Path(r"c:\workspace2\shion\outputs\body_entropy_latest.json")
BODY_STATUS_FILE = Path(r"c:\workspace\agi\outputs\shion_body_status.json")

class AmbientHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API Endpoint
        if parsed.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Combine the two JSONs
            payload = {"entropy_data": {}, "body_status": {}}
            
            try:
                if ENTROPY_FILE.exists():
                    payload["entropy_data"] = json.loads(ENTROPY_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error reading entropy: {e}")
                
            try:
                if BODY_STATUS_FILE.exists():
                    payload["body_status"] = json.loads(BODY_STATUS_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error reading body status: {e}")
                
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return
            
        # Serve static files
        super().do_GET()

def run_server():
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AmbientHandler)
    logger.info(f"🌿 Ambient Presence Server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info("Server stopped.")

if __name__ == "__main__":
    run_server()
