import json
import urllib.request
import base64
from pathlib import Path

def test_ollama_vision():
    print("Testing Ollama Vision (llama3.2-vision)...")
    crystal_path = Path(r"C:\workspace2\shion\outputs\resonance_crystals\resonance_crystal_20260304_193157.png")
    screenshot_path = Path(r"C:\workspace\agi\services\outputs\fsd_screenshots\final_20251208_202833.png")

    if not crystal_path.exists() or not screenshot_path.exists():
        print(f"File not found: {crystal_path.exists()}, {screenshot_path.exists()}")
        return

    with open(crystal_path, "rb") as f:
        crystal_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(screenshot_path, "rb") as f:
        screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "moondream:latest",
        "messages": [
            {
                "role": "user",
                "content": "Compare these two images. Respond with just a resonance score from 0.0 to 1.0.",
                "images": [crystal_b64, screenshot_b64]
            }
        ],
        "stream": False,
        "options": {"temperature": 0.0}
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
            print(f"Vision Result: {result.get('message', {}).get('content')}")
    except Exception as e:
        print(f"Vision Error: {e}")

def test_ollama_thinking():
    print("\nTesting Ollama Thinking (shion-v1)...")
    payload = {
        "model": "shion-v1",
        "messages": [
            {"role": "user", "content": "What is the essence of rhythm in the unified field?"}
        ],
        "stream": False,
        "options": {
            "thinking": True
        }
    }
    
    # Try 11434 first for shion-v1
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"Thinking Result: {result.get('message', {}).get('content')}")
    except Exception as e:
        print(f"Thinking Error (11434): {e}")

if __name__ == "__main__":
    test_ollama_vision()
    test_ollama_thinking()
