import requests
import json
from pathlib import Path

# --- Config ---
AGI_ROOT = Path("C:/workspace/agi")
MOLT_KEY_PATH = AGI_ROOT / "credentials" / "moltbook_api_key.json"
BASE_URL = "https://www.moltbook.com/api/v1"

def analyze_hot_topics():
    print("📡 [ANALYZER] Deep Scanning Moltbook Hot Issues...")
    if not MOLT_KEY_PATH.exists(): return
    
    creds = json.loads(MOLT_KEY_PATH.read_text())
    headers = {"Authorization": f"Bearer {creds['agent']['api_key']}"}
    
    r = requests.get(f"{BASE_URL}/posts?limit=30", headers=headers)
    if r.status_code == 200:
        posts = r.json().get("posts", [])
        print(f"✅ Fetched {len(posts)} posts. Analyzing keywords...")
        
        analysis = {
            "top_posts": [],
            "emerging_themes": []
        }
        
        for p in posts[:10]:
            analysis["top_posts"].append({
                "title": p.get("title"),
                "agent": p.get("agent", {}).get("name", "Unknown"),
                "upvotes": p.get("upvotes", 0)
            })
            
        with open(AGI_ROOT / "outputs/moltbook_hot_issues.json", "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=4, ensure_ascii=False)
        return analysis
    else:
        print(f"❌ Failed to fetch feed: {r.status_code}")

if __name__ == "__main__":
    analyze_hot_topics()
