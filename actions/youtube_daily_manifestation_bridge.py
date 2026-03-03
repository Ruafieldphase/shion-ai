import os
import subprocess
from pathlib import Path

# Paths
AGI_SCRIPTS_DIR = Path("C:/workspace/agi/scripts")
YOUTUBE_SCRIPT = AGI_SCRIPTS_DIR / "youtube_daily_manifestation.py"

def run_manifestation():
    """
    Calls the YouTube manifestation script from the AGI workspace.
    """
    print(f"🎬 [ACTION] Starting YouTube Daily Manifestation...")
    
    if not YOUTUBE_SCRIPT.exists():
        print(f"❌ [ACTION] Error: YouTube script not found at {YOUTUBE_SCRIPT}")
        return False
        
    try:
        # Run with python within the AGI environment (assuming same python interpreter)
        result = subprocess.run(
            ["python", str(YOUTUBE_SCRIPT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ [ACTION] Warnings/Errors:\n{result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ [ACTION] Unexpected error during manifestation: {e}")
        return False

if __name__ == "__main__":
    run_manifestation()
