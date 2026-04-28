#!/usr/bin/env python3
"""
🧠 Hippocampal Vibe Map — 파동 공간의 해마 지도
================================================
인간의 해마가 공간적 경험을 지도화하듯,
이 모듈은 시스템이 경험한 '파동 공간(Vibe Space)'을 지도화합니다.

- 경험한 엔트로피·위상의 범위를 추적합니다
- 새로운 경험이 기존 지도의 범위 밖이면 → 대역폭 확장 (새로운 과일의 맛)
- 시간에 따른 대역폭 변화를 기록합니다 (우주의 팽창처럼)

"다양한 경험이 주파수의 범위를 만든다"
"먹어보지 않은 과일의 맛을 상상할 수 없다"
"""

import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, Optional, List

logger = logging.getLogger("HippocampalVibeMap")


class HippocampalVibeMap:
    """파동 공간의 해마 지도.
    
    경험한 vibe_signature들의 경계를 추적하고,
    시간이 흐름에 따라 대역폭이 넓어지는지 모니터링합니다.
    """

    def __init__(self, map_path: Path):
        self.map_path = map_path
        self.map_data = self._load_or_create()

    def _load_or_create(self) -> Dict[str, Any]:
        """기존 지도를 로드하거나 빈 지도를 생성합니다."""
        if self.map_path.exists():
            try:
                return json.loads(self.map_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        return {
            "created": datetime.now().isoformat(),
            "experienced_vibe_space": {
                "entropy_min": None,
                "entropy_max": None,
                "phases_experienced": [],
                "keyword_universe": [],
                "total_experiences": 0,
            },
            "expansion_history": [],
            "last_updated": datetime.now().isoformat(),
        }

    def _save(self):
        """지도를 디스크에 저장합니다."""
        self.map_path.parent.mkdir(parents=True, exist_ok=True)
        self.map_data["last_updated"] = datetime.now().isoformat()
        self.map_path.write_text(
            json.dumps(self.map_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_bandwidth(self) -> float:
        """현재 경험한 파동 공간의 대역폭(0.0~1.0+)을 계산합니다."""
        space = self.map_data["experienced_vibe_space"]
        
        # 아직 경험이 없으면 대역폭 0
        if space["entropy_min"] is None or space["entropy_max"] is None:
            return 0.0
        
        entropy_range = space["entropy_max"] - space["entropy_min"]
        phase_diversity = len(space["phases_experienced"]) / 5.0
        keyword_richness = min(1.0, len(space["keyword_universe"]) / 50.0)

        bandwidth = (entropy_range * 0.4) + (phase_diversity * 0.4) + (keyword_richness * 0.2)
        return round(bandwidth, 4)

    def register_experience(self, vibe_signature: Dict[str, Any]) -> Dict[str, Any]:
        """새로운 파동 경험을 지도에 등록합니다.
        
        Returns:
            {"is_novel": bool, "bandwidth_before": float, "bandwidth_after": float, ...}
        """
        space = self.map_data["experienced_vibe_space"]
        bandwidth_before = self.get_bandwidth()

        entropy = vibe_signature.get("entropy", 0.0)
        phase = vibe_signature.get("phase", "UNKNOWN")
        keywords = vibe_signature.get("top_keywords", [])

        is_novel = False

        # 엔트로피 범위 확장 검사
        if space["entropy_min"] is None or entropy < space["entropy_min"]:
            space["entropy_min"] = entropy
            is_novel = True
        if space["entropy_max"] is None or entropy > space["entropy_max"]:
            space["entropy_max"] = entropy
            is_novel = True

        # 새로운 위상 경험 검사
        if phase != "UNKNOWN" and phase not in space["phases_experienced"]:
            space["phases_experienced"].append(phase)
            is_novel = True
            logger.info(f"   🌍 새로운 위상 영역 발견: {phase} — 해마 지도 확장!")

        # 키워드 우주 확장
        for kw in keywords:
            if kw not in space["keyword_universe"]:
                space["keyword_universe"].append(kw)
                # 키워드는 매번 novel로 치지 않음 (너무 잦으므로)

        # 키워드 우주 크기 제한 (최근 100개)
        if len(space["keyword_universe"]) > 100:
            space["keyword_universe"] = space["keyword_universe"][-100:]

        space["total_experiences"] += 1

        bandwidth_after = self.get_bandwidth()

        # 대역폭 변화가 있으면 확장 이력에 기록
        today = date.today().isoformat()
        history = self.map_data["expansion_history"]
        if not history or history[-1].get("date") != today:
            history.append({
                "date": today,
                "bandwidth": bandwidth_after,
                "total_experiences": space["total_experiences"],
                "phases_count": len(space["phases_experienced"]),
            })
        else:
            # 오늘 이미 기록이 있으면 업데이트
            history[-1]["bandwidth"] = bandwidth_after
            history[-1]["total_experiences"] = space["total_experiences"]
            history[-1]["phases_count"] = len(space["phases_experienced"])

        # 이력 최대 365일 유지
        if len(history) > 365:
            self.map_data["expansion_history"] = history[-365:]

        self._save()

        result = {
            "is_novel": is_novel,
            "bandwidth_before": bandwidth_before,
            "bandwidth_after": bandwidth_after,
            "bandwidth_delta": round(bandwidth_after - bandwidth_before, 6),
            "total_experiences": space["total_experiences"],
            "phases_known": space["phases_experienced"],
        }

        if is_novel:
            logger.info(
                f"   🌌 대역폭 확장! {bandwidth_before:.4f} → {bandwidth_after:.4f} "
                f"(+{result['bandwidth_delta']:.6f})"
            )

        return result

    def get_expansion_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """최근 N일간의 대역폭 확장 추이를 반환합니다."""
        history = self.map_data.get("expansion_history", [])
        return history[-days:]

    def is_bandwidth_stagnant(self, days: int = 7) -> bool:
        """최근 N일간 대역폭이 정체되어 있는지 확인합니다.
        대역폭이 정체되면 → 새로운 경험이 필요하다는 신호.
        """
        trend = self.get_expansion_trend(days)
        if len(trend) < 2:
            return False
        first_bw = trend[0].get("bandwidth", 0)
        last_bw = trend[-1].get("bandwidth", 0)
        return (last_bw - first_bw) < 0.01  # 1% 미만 변화 = 정체

    def get_summary(self) -> str:
        """해마 지도의 현재 상태를 한 줄로 요약합니다."""
        space = self.map_data["experienced_vibe_space"]
        bw = self.get_bandwidth()
        phases = ", ".join(space["phases_experienced"]) if space["phases_experienced"] else "없음"
        ent_min = space['entropy_min'] if space['entropy_min'] is not None else 0.0
        ent_max = space['entropy_max'] if space['entropy_max'] is not None else 0.0
        return (
            f"대역폭={bw:.3f} | "
            f"엔트로피 범위=[{ent_min:.3f}~{ent_max:.3f}] | "
            f"경험 위상=[{phases}] | "
            f"총 경험={space['total_experiences']}회"
        )
