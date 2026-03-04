import json
import urllib.request
import base64
from pathlib import Path
import re

def test_moondream_simple():
    print("Testing Moondream (moondream:latest) with Simple Prompt...")
    crystal_path = Path(r"C:\workspace2\shion\outputs\resonance_crystals\resonance_crystal_20260304_193157.png")

    if not crystal_path.exists():
        print(f"File not found: {crystal_path}")
        return

    with open(crystal_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "moondream:latest",
        "messages": [
            {
                "role": "user",
                "content": "Describe this image in one word.",
                "images": [img_b64]
            }
        ],
        "stream": False
    }

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("message", {}).get("content", "").strip()
            print(f"Moondream Simple Result: '{content}'")
    except Exception as e:
        print(f"Moondream Error: {e}")

if __name__ == "__main__":
    test_moondream_simple()
