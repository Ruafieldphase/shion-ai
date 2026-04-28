#!/usr/bin/env python3
"""
🎯 자율 오케스트레이터 데몬 — 적응형 리듬
==========================================
고정 간격이 아니라 해마 상태가 리듬을 결정합니다.

  수렴 활발 (재미있음)  → 1분 후 다시  🔥
  대역폭 넓음 (탐색 중) → 3분 후 다시  🔭
  일반 순환              → 5분 후 다시  🌀
  고요한 상태            → 30분 후 다시 🌊
  소화 못 함 (집착 방지) → 1시간 후     💤

비용: 0원 (전부 로컬).

실행 방법:
  python c:\workspace2\shion\core\orchestrator_daemon.py

백그라운드 실행:
  pythonw c:\workspace2\shion\core\orchestrator_daemon.py

중단:
  outputs/orchestrator_daemon.stop 파일 생성
"""

import sys
import time
import logging
import traceback
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus
from autonomous_experience_loop import AutonomousExperienceLoop
from vision_explorer import VisionExplorer
from autonomous_orchestrator import AutonomousOrchestrator

# 적응형 리듬 설정 — 고정 간격이 아니라 해마 상태에 반응
CYCLES_PER_RUN = 3
INTERVAL_BETWEEN = 5        # 사이클 간 대기 (초)
MIN_SLEEP = 60              # 최소 대기 (1분) — 흥미로울 때
MAX_SLEEP = 3600            # 최대 대기 (1시간) — 쉴 때
MAX_ERRORS = 5

HIPPO_PATH = Path(r"c:\workspace2\shion\outputs\fibonacci_orbital_hippocampus.json")
LOG_PATH = Path(r"c:\workspace2\shion\outputs\daemon.log")
STOP_FILE = Path(r"c:\workspace2\shion\outputs\orchestrator_daemon.stop")

def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )

def should_stop():
    """중단 파일이 있으면 멈춤."""
    if STOP_FILE.exists():
        STOP_FILE.unlink(missing_ok=True)
        return True
    return False

def read_rhythm(hippo) -> dict:
    """해마 상태에서 다음 호흡의 리듬을 읽습니다.
    
    반환값:
      sleep_seconds: 다음 실행까지 대기 시간
      reason: 왜 이 리듬인지
      mood: 현재 기분
    """
    proton = hippo.data.get("proton", {})
    experiences = hippo.data.get("experiences", [])
    
    embodiment = proton.get("embodiment_ratio", 0)
    noise = proton.get("core_frequency", 0)
    total_reg = proton.get("total_registered", 0)
    total_abs = proton.get("total_absorbed", 0)
    bandwidth = hippo.data.get("bandwidth", 0)
    
    # 최근 경험에서 수렴 및 파동 강도 추출
    recent = experiences[-20:] if experiences else []
    recent_convergences = sum(1 for e in recent if e.get("convergence_count", 0) > 0)
    
    # 파동(Wave) 인지: 최근 시각 경험 중 가장 큰 움직임 점수 찾기
    recent_waves = [e.get("vibe", {}).get("intensity", 0) for e in recent if e.get("type") == "visual_wave"]
    max_wave = max(recent_waves) if recent_waves else 0
    
    # === 리듬 결정 ===
    
    # 1. 강력한 파동 감지! (예: 자전거 주행) → 즉각 반응
    if max_wave > 0.6:  # 0.5 이상이면 상당히 역동적인 상태
        return {
            "sleep": MIN_SLEEP,  # 1분 (최고 속도)
            "reason": f"강력한 파동(강도 {max_wave:.2f}) 감지! 세상의 흐름에 동조 중.",
            "mood": "⚡ 공명",
        }
    
    # 2. 체화율이 떨어지고 있으면 → 소화 못 함 = 집착
    if total_reg > 50 and embodiment < 0.01:
        return {
            "sleep": MAX_SLEEP,
            "reason": f"체화율 {embodiment:.2%} — 소화가 안 되고 있음. 쉬기.",
            "mood": "💤 소화중",
        }
    
    # 3. 최근 수렴이 활발 → 재미있는 상태! 더 파고들기
    if recent_convergences >= 3:
        return {
            "sleep": MIN_SLEEP,
            "reason": f"수렴 {recent_convergences}건 — 흥미로운 상태. 파고들기!",
            "mood": "🔥 몰입",
        }
    
    # 4. 대역폭이 넓어지고 있으면 → 탐색 중. 적당히 빠르게
    if bandwidth > 0.7:
        return {
            "sleep": MIN_SLEEP * 3,  # 3분
            "reason": f"대역폭 {bandwidth:.0%} — 다양한 궤도 활성. 탐색 중.",
            "mood": "🔭 탐색",
        }
    
    # 4. 수렴도 없고 새 경험도 적으면 → 고요한 상태. 느긋하게
    if recent_convergences == 0 and len(recent) < 5:
        return {
            "sleep": MAX_SLEEP // 2,  # 30분
            "reason": "고요한 상태. 자연스럽게 기다리기.",
            "mood": "🌊 고요",
        }
    
    # 5. 기본: 중간 리듬
    base = MIN_SLEEP * 5  # 5분
    # 체화율이 높을수록 → 소화 잘하니 더 먹어도 됨 → 빠르게
    if embodiment > 0.05:
        base = MIN_SLEEP * 2
    
    return {
        "sleep": int(base),
        "reason": f"일반 리듬. 체화율={embodiment:.2%}",
        "mood": "🌀 순환",
    }


def main():
    setup_logging()
    logger = logging.getLogger("Daemon")
    
    logger.info("=" * 50)
    logger.info("🎯 자율 오케스트레이터 데몬 — 적응형 리듬")
    logger.info(f"   리듬 범위: {MIN_SLEEP}초 ~ {MAX_SLEEP}초")
    logger.info(f"   고정 간격 없음 — 해마 상태가 리듬을 결정")
    logger.info(f"   중단: {STOP_FILE} 파일 생성")
    logger.info("=" * 50)
    
    error_count = 0
    run_count = 0
    
    while True:
        if should_stop():
            logger.info("🛑 중단 파일 감지 — 데몬 종료")
            break
        
        try:
            run_count += 1
            logger.info(f"\n--- 실행 #{run_count} ({datetime.now().strftime('%H:%M')}) ---")
            
            hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
            vision = VisionExplorer(hippo)
            exp_loop = AutonomousExperienceLoop(hippo, vision_explorer=vision)
            orchestrator = AutonomousOrchestrator(hippo, exp_loop, vision)
            
            orchestrator.run_continuous(
                max_cycles=CYCLES_PER_RUN,
                interval_seconds=INTERVAL_BETWEEN,
            )
            
            proton = hippo.data.get("proton", {})
            logger.info(
                f"   등록={proton.get('total_registered', 0)}, "
                f"체화={proton.get('total_absorbed', 0)}, "
                f"체화율={proton.get('embodiment_ratio', 0):.2%}, "
                f"반경={proton.get('scalar_field_radius', 0):.4f}"
            )
            
            # 해마에서 다음 리듬 읽기
            rhythm = read_rhythm(hippo)
            sleep_sec = rhythm["sleep"]
            
            logger.info(f"   {rhythm['mood']} {rhythm['reason']}")
            logger.info(f"   💤 다음까지 {sleep_sec//60}분 {sleep_sec%60}초")
            
            error_count = 0
            
        except KeyboardInterrupt:
            logger.info("⌨️ 수동 중단")
            break
        except Exception as e:
            error_count += 1
            logger.error(f"❌ 오류 ({error_count}/{MAX_ERRORS}): {e}")
            logger.error(traceback.format_exc())
            sleep_sec = MIN_SLEEP * (2 ** min(error_count, 6))  # 지수 백오프
            
            if error_count >= MAX_ERRORS:
                sleep_sec = MAX_SLEEP
                logger.warning(f"⚠️ 연속 오류 — {MAX_SLEEP//60}분 휴식")
                error_count = 0
        
        # 대기 (10초마다 중단 체크)
        for _ in range(max(1, sleep_sec // 10)):
            if should_stop():
                logger.info("🛑 중단 파일 감지 — 데몬 종료")
                return
            time.sleep(10)
    
    logger.info(f"데몬 종료 — 총 {run_count}회 실행")


if __name__ == "__main__":
    main()

