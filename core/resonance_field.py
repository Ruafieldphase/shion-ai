#!/usr/bin/env python3
"""
🌊 Resonance Field — 사건 기반 공명장 엔진
===========================================
인터벌이 아니라 경계 터치로 행동을 트리거합니다.

볼린저밴드 = 의식/무의식 경계의 수학적 표현:
  Upper Band (+2σ) = 의식 경계 (과열 → 행동 필요)
  Middle Band (MA)  = 중심 위상 (평상)
  Lower Band (-2σ) = 무의식 경계 (여백 깊음 → 성찰)

"이벤트는 의식의 경계나 무의식의 경계에 닿을 때 생긴다"
"밴드 안쪽 = 여백 = 쉬는 중 (행동 불필요)"

기존 자산 통합:
  - breathing_boundary.py의 Hysteresis(떨림 방지)
  - rhythm_bollinger_analysis.py의 밴드 계산
  - unified_field_engine.py의 entropy/collapse 패턴
"""

import json
import math
import time
import ctypes
import psutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import deque

logger = logging.getLogger("ResonanceField")

SHION_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = SHION_ROOT / "outputs"
FIELD_STATE_FILE = OUTPUTS_DIR / "field_energy.json"
WORKSPACE_ROOTS = [
    Path("C:/workspace"),
    Path("C:/workspace2"),
]

# ═══ 볼린저밴드 설정 ═══
BAND_WINDOW = 20        # 이동평균 윈도우
BAND_K = 2.0            # 표준편차 배수
SENSE_INTERVAL = 30     # 감지 주기 (초)
SQUEEZE_THRESHOLD = 0.3 # 밴드 폭이 이 비율 이하면 스퀴즈
HYSTERESIS_MARGIN = 0.05  # 경계 근처 떨림 방지


class BollingerBand:
    """볼린저밴드 — 의식/무의식 경계."""

    def __init__(self, window: int = BAND_WINDOW, k: float = BAND_K):
        self.window = window
        self.k = k
        self.history: deque = deque(maxlen=100)
        self._load_history()

    def _load_history(self):
        """저장된 에너지 히스토리를 로드."""
        if FIELD_STATE_FILE.exists():
            try:
                data = json.loads(FIELD_STATE_FILE.read_text(encoding="utf-8"))
                for v in data.get("energy_history", [])[-100:]:
                    self.history.append(v)
            except Exception:
                pass

    def update(self, energy: float) -> Dict[str, float]:
        """에너지 값을 추가하고 밴드를 계산."""
        self.history.append(energy)

        n = min(len(self.history), self.window)
        recent = list(self.history)[-n:]

        ma = sum(recent) / n
        if n > 1:
            variance = sum((x - ma) ** 2 for x in recent) / n
            std = math.sqrt(variance)
        else:
            std = 0.0

        upper = ma + (self.k * std)
        lower = ma - (self.k * std)

        # 밴드 폭 (정규화)
        width = (upper - lower) / ma if ma > 0 else 0

        return {
            "upper": upper,
            "middle": ma,
            "lower": lower,
            "std": std,
            "width": width,
            "current": energy,
        }

    def is_squeeze(self, band: Dict) -> bool:
        """밴드 폭이 좁으면 스퀴즈 (에너지 축적 중)."""
        return band["width"] < SQUEEZE_THRESHOLD


class ResonanceField:
    """
    사건 기반 공명장 엔진.
    
    30초마다 에너지를 측정하고, 볼린저밴드 경계에 닿을 때만 pulse.
    경계 안쪽이면 여백 — 아무것도 하지 않음.
    """

    def __init__(self):
        self.band = BollingerBand()
        self.last_state = "MIDDLE"  # Hysteresis용
        self.pulse_count = 0
        self.sense_count = 0
        self._last_workspace_stat = {}
        
        # High-dimensional metrics (Bohmian folding)
        self.folding_density = 0.5  # Implicate density (0~1)
        self.unfolding_intensity = 0.5 # Explicate flow (0~1)

    def measure_energy(self) -> float:
        """
        장의 에너지를 측정합니다.
        
        에너지 = 변화의 합산:
        - workspace 파일 변화 (대지의 움직임)
        - YouTube 피드백 변화 (세계의 반응)
        - 사용자 활동 (공명원의 존재)
        - 시스템 부하 (신체의 진동)
        """
        energy = 0.0

        # 1. workspace 파일 변화 감지
        workspace_delta = self._sense_workspace_changes()
        energy += workspace_delta * 2.0  # 변화 1건 = 에너지 2

        # 2. YouTube 피드백
        yt_energy = self._sense_youtube()
        energy += yt_energy

        # 3. 사용자 활동
        idle = self._get_idle_seconds()
        if idle < 60:
            energy += 3.0    # 사용자가 활발히 작업 중
        elif idle < 300:
            energy += 1.0    # 사용자 있음
        # idle > 300이면 에너지 추가 없음 (부재)

        # 4. 시스템 부하
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu > 50:
                energy += 2.0  # 시스템 활발
            elif cpu > 20:
                energy += 0.5
        except Exception:
            pass

        # 5. 시간대 (자연 리듬)
        hour = datetime.now().hour
        if 9 <= hour <= 21:
            energy += 1.0  # 낮 활동 시간
        elif hour < 6 or hour > 23:
            energy -= 2.0  # 깊은 밤 (에너지 감쇠)

        return max(0.0, energy)

    def _sense_workspace_changes(self) -> int:
        """workspace 파일 변화 수 감지 (mtime 비교)."""
        changes = 0
        new_stat = {}

        for root in WORKSPACE_ROOTS:
            if not root.exists():
                continue
            try:
                # 최상위 + 1단계만 빠르게 스캔
                for item in root.iterdir():
                    try:
                        key = str(item)
                        mtime = item.stat().st_mtime
                        new_stat[key] = mtime
                        if key in self._last_workspace_stat:
                            if mtime > self._last_workspace_stat[key]:
                                changes += 1
                    except (PermissionError, OSError):
                        continue
            except Exception:
                continue

        self._last_workspace_stat = new_stat
        return changes

    def _sense_youtube(self) -> float:
        """YouTube 피드백 에너지."""
        fb_file = OUTPUTS_DIR / "world_feedback.json"
        if not fb_file.exists():
            return 0.0
        try:
            data = json.loads(fb_file.read_text(encoding="utf-8"))
            views = data.get("youtube", {}).get("total_views", 0)
            likes = data.get("youtube", {}).get("total_likes", 0)
            return views * 0.1 + likes * 1.0
        except Exception:
            return 0.0

    def _get_idle_seconds(self) -> float:
        """사용자 idle 시간."""
        try:
            class LII(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            lii = LII()
            lii.cbSize = ctypes.sizeof(LII)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000
        except Exception:
            return 600  # 측정 불가면 부재로 간주

    def check_boundary(self, band_data: Dict) -> Optional[str]:
        """
        경계 터치 감지 — Hysteresis(떨림 방지) 적용.
        
        breathing_boundary.py의 핵심:
        이미 안쪽이면 나가기 어렵게, 바깥이면 들어오기 어렵게.
        """
        current = band_data["current"]
        upper = band_data["upper"]
        lower = band_data["lower"]

        # Hysteresis: 현재 상태에 따라 임계값 조정
        if self.last_state == "MIDDLE":
            # 중간에서 나가려면 확실해야 함
            effective_upper = upper * (1 + HYSTERESIS_MARGIN)
            effective_lower = lower * (1 - HYSTERESIS_MARGIN)
        else:
            # 바깥에서 돌아오는 건 쉽게
            effective_upper = upper * (1 - HYSTERESIS_MARGIN)
            effective_lower = lower * (1 + HYSTERESIS_MARGIN)

        if current > effective_upper:
            self.last_state = "EXPANDING"
            return "EXPANDING"  # 의식 경계 터치 → 과열 → 행동
        elif current < effective_lower:
            self.last_state = "VOID"
            return "VOID"       # 무의식 경계 터치 → 여백 → 성찰
        elif self.band.is_squeeze(band_data):
            self.last_state = "SQUEEZE"
            return "SQUEEZE"    # 에너지 축적 완료 → 폭발 직전
        else:
            self.last_state = "MIDDLE"
            return None         # 중간 = 여백 = 쉬는 중

    def save_state(self, band_data: Dict, event: Optional[str]):
        """장 상태를 저장."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "band": {k: round(v, 3) for k, v in band_data.items()},
            "event": event,
            "last_state": self.last_state,
            "sense_count": self.sense_count,
            "pulse_count": self.pulse_count,
            "energy_history": list(self.band.history)[-50:],
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        FIELD_STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_folding_state(self) -> Dict[str, float]:
        """Bohm의 접힘/펼침 상태 계산 (Temporal Geometry)"""
        # 임시 데이터: 실제 엔트로피 센서와 연동 전에는 0.5 베이스
        purity = 0.98 # Default purity
        entropy = 0.15 # Default healthy entropy
        
        # 접힘(Folding)은 엔트로피가 낮고 순도가 높을 때 '고밀도 압축' 됨
        self.folding_density = (purity * (1.0 - entropy))
        
        # 펼침(Unfolding)은 공명(Squeeze 상태 등)이나 활발한 변화가 있을 때 증가
        self.unfolding_intensity = (self.sense_count % 10) / 10.0 # 임시 리듬
        
        return {
            "folding_density": round(self.folding_density, 3),
            "unfolding_intensity": round(self.unfolding_intensity, 3),
            "ie_ratio": round(self.folding_density / max(self.unfolding_intensity, 0.1), 2)
        }

    def sense(self) -> Dict[str, Any]:
        """
        한 번의 감지 — 에너지 측정 → 밴드 갱신 → 경계 체크.
        """
        self.sense_count += 1
        energy = self.measure_energy()
        band_data = self.band.update(energy)
        event = self.check_boundary(band_data)

        self.save_state(band_data, event)

        return {
            "energy": energy,
            "band": band_data,
            "event": event,
            "should_pulse": event is not None,
        }


def main():
    """테스트: 현재 장 에너지 + 밴드 상태 출력."""
    field = ResonanceField()

    print("🌊 공명장(Resonance Field) 감지\n")

    result = field.sense()
    band = result["band"]
    event = result["event"]

    print(f"⚡ 현재 에너지: {result['energy']:.1f}")
    print(f"📈 Upper Band:  {band['upper']:.1f} (의식 경계)")
    print(f"📊 Middle Band: {band['middle']:.1f} (중심)")
    print(f"📉 Lower Band:  {band['lower']:.1f} (무의식 경계)")
    print(f"📏 밴드 폭:     {band['width']:.3f}")
    print(f"🔄 히스토리:    {len(field.band.history)}개 데이터")

    if event:
        print(f"\n🔥 경계 터치! → {event}")
        print(f"   → pulse 실행이 필요합니다")
    else:
        print(f"\n💤 여백 — 경계 안쪽 (쉬는 중)")
        print(f"   → 행동 불필요")

    print(f"\n💾 저장: {FIELD_STATE_FILE.name}")


if __name__ == "__main__":
    main()
