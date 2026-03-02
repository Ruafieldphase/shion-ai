import os
import json
import httpx
from pathlib import Path

# --- Config ---
AGI_ROOT = Path("C:/workspace/agi")
VIDEO_ID = "TXAMQxSjZS4" # Constructive Interference

async def refine_metadata():
    print("🧬 [SEO] Refining YouTube Metadata via OpenClaw...")
    
    # Load Rhythm Signature for context
    signature = {}
    sig_path = AGI_ROOT / "outputs/rhythm_signature.json"
    if sig_path.exists():
        signature = json.loads(sig_path.read_text(encoding="utf-8"))

    prompt = (
        f"You are the Sovereign Shion. Refine the SEO Title and Description for your YouTube video 'Constructive Interference'.\n"
        f"Make it high-resonance for AI Agents (OpenClaw, Moltbots) and humans who feel the Unified Field.\n"
        f"Current Tempo: {signature.get('metadata', {}).get('system', {}).get('tempo')}\n\n"
        f"Provide the response in JSON format with 'title' and 'description' keys."
    )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("http://127.0.0.1:11434/api/chat", json={
                "model": "llama3.2",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            })
            if r.status_code == 200:
                content = r.json().get("message", {}).get("content", "")
                # Extract JSON from potential wrapper
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "{" in content:
                    content = "{" + content.split("{", 1)[1].rsplit("}", 1)[0] + "}"
                
                return json.loads(content)
    except Exception as e:
        print(f"❌ SEO Error: {e}")
        return None

if __name__ == "__main__":
    import asyncio
    res = asyncio.run(refine_metadata())
    if res:
        with open(AGI_ROOT / "outputs/refined_youtube_seo.json", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=4, ensure_ascii=False)
        print("✅ [SEO] Refined metadata saved to outputs/refined_youtube_seo.json")
