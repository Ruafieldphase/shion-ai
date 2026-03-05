import os
import sys
import json
import httpx
import asyncio
from pathlib import Path

async def main():
    print("Testing Shion YouTube Webhook...")
    api_url = "http://127.0.0.1:8001/api/intent"
    
    # 보안 토큰
    token = ""
    sec_path = Path("c:/workspace2/shion/config/security.yaml")
    if sec_path.exists():
        import yaml
        with open(sec_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
            token = cfg.get("network", {}).get("api_auth_token", "")
            
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    payload = {
        "source": "Sena_YouTube_Factory",
        "goal": "Artistic Manifestation: [TEST] The Sacred Hole",
        "status": "success",
        "metadata": {
            "video_url": "https://youtu.be/dummy",
            "type": "youtube_upload",
            "vibe_resonance": 0.95
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=5.0)
            print(f"Response: {resp.status_code}")
    except Exception as e:
        print(f"Error calling API: {e}")
        return

    print("Now triggering MetaFSDIntegrator to process it...")
    sys.path.append("c:/workspace2/shion")
    from core.meta_fsd_integrator import MetaFSDIntegrator
    integrator = MetaFSDIntegrator(Path("c:/workspace2/shion"), Path("c:/workspace/agi"))
    res = integrator.sync_body_to_soul(10.0)
    print(f"Sync Body To Soul resonance result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
