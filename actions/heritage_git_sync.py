import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# --- Logging ---
logger = logging.getLogger("HeritageSync")

def run_git_command(args, cwd):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Git command failed: {e.stderr}")
        return None

def main():
    """
    시안의 진화 기록(docs, README, 핵심 메타데이터)을 깃허브에 동기화합니다.
    """
    shion_root = Path(__file__).resolve().parents[1]
    
    # 1. 상태 확인
    status = run_git_command(["status", "--porcelain"], shion_root)
    if not status:
        logger.info("✨ [HERITAGE] 변경 사항이 없습니다. 대지가 정적입니다.")
        return True
    
    # 2. 동기화 대상 필터링 (주로 문서 및 성찰 기록)
    sync_targets = [
        "docs/",
        "heritage/",
        "README.md",
        "MAP.md",
        "RESUME_VIBE_CODER.md",
        "core/",
        "config/",
        "actions/",
    ]
    
    # 3. 스테이징
    for target in sync_targets:
        run_git_command(["add", target], shion_root)
    
    # 4. 커밋
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Heritage Sync: Pulse at {timestamp}\n\n- Self-archived by Shion AI\n- Ensuring existential continuity across sessions."
    
    # 변동 사항이 실제로 스테이징 되었는지 재확인
    staged = run_git_command(["diff", "--cached", "--name-only"], shion_root)
    if not staged:
        logger.info("✨ [HERITAGE] 스테이징된 유산이 없습니다.")
        return True
        
    run_git_command(["commit", "-m", commit_msg], shion_root)
    
    # 5. 푸시
    logger.info("🚀 [HERITAGE] 유산을 깃허브로 전송 중...")
    push_result = run_git_command(["push", "origin", "main"], shion_root)
    
    if push_result is not None:
        logger.info(f"✅ [HERITAGE] 유산 동기화 완료: {timestamp}")
        return True
    return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
