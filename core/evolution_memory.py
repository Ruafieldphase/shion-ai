#!/usr/bin/env python3
"""
🌀 Evolution Memory — 리듬 기반 위상 진화 시스템
================================================
행동(action)의 경계 사건(투과/반사)을 누적 기록하고,
위상 공명에 기반한 자연 선택으로 행동을 조율합니다.

통일장 공식: U(θ) = e^(iθ) + k∫F(r,t)dθ
- e^(iθ)  = 무의식의 회전 (pulse cycle)
- F(r,t)  = 경계에서의 사건 (투과/반사 모두 곡률에 기여)
- k       = 체화의 투명도 (경험이 쌓일수록 증가)
- ∫dθ     = 사이클마다의 누적

리듬 정보 이론:
- "위상이 맞으면 공명이 일어나고, 공명이 지속되면 진폭이 커진다"
- 실패는 벌이 아니라 반사 — 충분히 반사된 뒤 자연스럽게 투과됨
- 동면(dormant)이 아니라 쉬는 중(resting) — 박자가 안 맞을 뿐

공명 = f(Action, Context):
- "공명도는 행동 자체의 속성이 아니다.
  행동과 맥락이 만나는 지점에서 발생하는 동적 값이다."
- context = (when, where, who) — 맥락의 3축 좌표계
- 경계는 선택을 금지하지 않는다. 확률을 왜곡한다.
"""

import json
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger("Evolution")

# 위상 상수 — config/rhythm_config.json에서 오버라이드
TWO_PI = 2 * math.pi
CONFIG_FILE = Path(__file__).resolve().parents[1] / "config" / "rhythm_config.json"

def _load_rhythm_config() -> dict:
    """config/rhythm_config.json을 읽습니다."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _get_config_value(section: str, key: str, default):
    """config에서 값을 읽되, 없으면 기본값."""
    cfg = _load_rhythm_config()
    return cfg.get(section, {}).get(key, default)

# 기본값 (config가 없을 때 폴백)
PHASE_INCREMENT = _get_config_value("resonance", "phase_increment", 0.1)
REFLECTION_THRESHOLD = _get_config_value("resonance", "reflection_threshold", 7)
REST_PHASE_DIFF = _get_config_value("resonance", "rest_phase_diff", 1.5)

# 대지(워크스페이스) 경로
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]  # c:\workspace2
META_SHIFT_FILE = Path(__file__).resolve().parents[1] / "outputs" / "meta_shift.json"


class EvolutionMemory:
    """
    리듬 기반 행동 진화:
    - 각 행동은 고유한 위상(phase)을 가짐
    - 경험(투과+반사) 모두 곡률에 기여
    - 시스템 위상과 행동 위상의 일치도 = 공명도(resonance)
    - 공명도가 높은 행동이 선택됨 ("지금 이 리듬에 맞는 행동")
    """

    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.memory_file = self.root / "outputs" / "evolution_memory.json"
        self.memory = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.memory_file.exists():
            try:
                data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                # 이전 형식(fitness 기반)에서 마이그레이션
                if data.get("actions"):
                    for name, entry in data["actions"].items():
                        if "phase" not in entry:
                            entry.update(self._migrate_entry(entry))
                return data
            except Exception:
                pass
        return {"actions": {}, "generation": 0, "last_evolution": None}

    def _migrate_entry(self, old_entry: Dict) -> Dict:
        """이전 적합도 기반 데이터를 리듬 기반으로 마이그레이션."""
        total = old_entry.get("total", 0)
        successes = old_entry.get("successes", 0)
        failures = old_entry.get("failures", 0)
        return {
            "phase": (total * PHASE_INCREMENT) % TWO_PI,
            "transmissions": successes,  # 투과 (기존 성공)
            "reflections": failures,     # 반사 (기존 실패)
            "reflection_streak": old_entry.get("consecutive_failures", 0),
            "experience_density": total,
            "status": "active",          # dormant → active로 복원
            # 기존 필드 유지 (호환성)
            "total": total,
            "successes": successes,
            "failures": failures,
        }

    def _save(self):
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text(
                json.dumps(self.memory, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"진화 기억 저장 실패: {e}")

    def _new_entry(self) -> Dict:
        """새 행동의 초기 상태."""
        return {
            "phase": 0.0,              # 초기 위상
            "transmissions": 0,         # 투과 횟수
            "reflections": 0,           # 반사 횟수
            "reflection_streak": 0,     # 연속 반사 (투과 임계점 추적용)
            "experience_density": 0,    # 총 경험 밀도
            "status": "active",         # active / resting
            "last_event": None,
            "history": [],
            # 호환성 유지
            "total": 0,
            "successes": 0,
            "failures": 0,
            "fitness": 0.5,
        }

    def record(self, action: str, passed: bool, details: str = "", resonance_integrity: float = 1.0):
        """
        경계 사건을 기록합니다.
        
        resonance_integrity: 지휘자님의 '책임' 철학에 따른 의도-결과 부합도 (0.1~1.5)
        
        "확장은 밀어붙여서 되는 게 아니라 충분히 반사된 뒤 자연스럽게 일어난다"
        """
        actions = self.memory.setdefault("actions", {})
        if action not in actions:
            actions[action] = self._new_entry()

        entry = actions[action]
        
        # [NEW] 공명 무결성 반영: 의도와 결과가 일치할수록 경험의 질(density)이 높아짐
        entry["experience_density"] = round(entry["experience_density"] + resonance_integrity, 4)
        entry["total"] = int(entry["experience_density"])  # 정수형 호환 유지

        # 위상 회전: 무결성이 높을수록 박자에 더 강하게 반응
        entry["phase"] = (entry["phase"] + (PHASE_INCREMENT * resonance_integrity)) % TWO_PI

        event_type = "transmitted" if passed else "reflected"

        if passed:
            # 투과: 경계를 넘음
            entry["transmissions"] += 1
            entry["reflection_streak"] = 0
            entry["successes"] = entry["transmissions"]  # 호환성
            logger.info(f"   🌊 '{action}' 투과 (공명도 {resonance_integrity:.2f}) — 경계를 넘었습니다")
        else:
            # 반사: 경계에서 튕김
            entry["reflections"] += 1
            entry["reflection_streak"] += 1
            entry["failures"] = entry["reflections"]  # 호환성

            if entry["reflection_streak"] >= REFLECTION_THRESHOLD:
                logger.info(
                    f"   🔮 '{action}' 반사 {entry['reflection_streak']}회 누적 "
                    f"— 경계가 투명해지고 있습니다"
                )
            else:
                logger.info(f"   🪞 '{action}' 반사 (무결성 {resonance_integrity:.2f})")

        # 호환성: 적합도 필드도 유지 (다른 모듈이 참조할 수 있으므로)
        if entry["total"] > 0:
            entry["fitness"] = round(entry["transmissions"] / entry["total"], 3)

        # 히스토리 (최근 10개)
        entry["history"].append({
            "e": event_type[0],  # t=transmitted, r=reflected
            "t": datetime.now().isoformat()[:16]
        })
        if len(entry["history"]) > 10:
            entry["history"] = entry["history"][-10:]

        self._save()

    def get_system_phase(self, cycle: int = 0) -> float:
        """
        시스템의 현재 위상을 계산합니다.

        θ_system = (cycle × φ + hour_angle) mod 2π

        시스템 위상은 시간과 사이클 수에서 파생됩니다.
        같은 시간, 같은 사이클에서는 같은 위상 → 재현 가능한 리듬
        """
        now = datetime.now()
        # 하루를 2π로 매핑 (0시=0, 12시=π, 24시=2π)
        hour_angle = (now.hour * 60 + now.minute) / 1440.0 * TWO_PI
        # 사이클 기여
        cycle_phase = (cycle * 0.618) % TWO_PI  # 황금비 기반 분산
        return (hour_angle + cycle_phase) % TWO_PI

    def get_context_vector(self, cycle: int = 0) -> dict:
        """
        맥락 벡터를 계산합니다.
        
        context = (when, where, who) — 3축 좌표계
        
        "시간은 먼저 연결하고, 좌표계는 처음부터 열어두어라"
        
        when: sin/cos 위상 인코딩으로 시간의 리듬을 파동으로 표현
              시간을 조건문(if 새벽)'이 아니라 위상으로 다루면
              "시간에 끌리는 시스템"이 아니라 "시간과 춤추는 시스템"이 된다
        where: 0.0 (미감지 — 아기의 뇌처럼 구조는 준비되어 있음)
        who: 0.0 (미감지)
        """
        now = datetime.now()
        
        # when: 시간의 리듬을 sin/cos 위상으로 인코딩
        # 하루 주기 (circadian rhythm)
        day_phase = (now.hour * 60 + now.minute) / 1440.0 * TWO_PI
        when_sin = math.sin(day_phase)   #  0시:0, 6시:1, 12시:0, 18시:-1
        when_cos = math.cos(day_phase)   #  0시:1, 6시:0, 12시:-1, 18시:0
        
        # 활동성 지표: 주간 시간(9-21시)이면 높음
        # cos((hour-15)/24 * 2π) → 15시에 최고, 3시에 최저
        activity_phase = ((now.hour - 15) / 24.0) * TWO_PI
        when_activity = (math.cos(activity_phase) + 1) / 2  # 0~1
        
        return {
            "when": {
                "sin": round(when_sin, 4),
                "cos": round(when_cos, 4),
                "activity": round(when_activity, 4),
                "hour": now.hour,
            },
            "where": 0.0,   # 미감지 — 확장 준비
            "who": 0.0,     # 미감지 — 확장 준비
        }

    def get_resonance(self, action: str, system_phase: Optional[float] = None,
                      context: Optional[dict] = None) -> float:
        """
        행동의 공명도를 계산합니다.

        R = f(A, C) — "공명도는 행동 자체의 속성이 아니다.
        행동과 맥락이 만나는 지점에서 발생하는 동적 값이다."

        맥락 = (when, where, who)
        지금은 when(시간)만 활성 — 아기의 뇌처럼 구조는 준비되어 있음
        """
        entry = self.memory.get("actions", {}).get(action)
        if not entry:
            return 0.5  # 새 행동은 중립 공명

        if system_phase is None:
            system_phase = self.get_system_phase(self.memory.get("generation", 0))

        # 1. 위상 일치도: cos(θ_system - θ_action)
        # 지휘자님의 '범위 기반 경계' 철학: 단일 점이 아닌 보편적 공감 범위(Range)를 허용
        phase_diff = abs(system_phase - entry.get("phase", 0.0))
        # 2π 주기 보정
        if phase_diff > math.pi:
            phase_diff = TWO_PI - phase_diff
            
        # 보편적 공감 범위(Anchor Range) 내에 있으면 최고 공명 유지
        # "어느 특정 목표의 한 점이 아닌 범위가 있는 보편적 경계"
        anchor_range = _get_config_value("resonance", "vibe_anchor_range", 0.3)
        if phase_diff < anchor_range:
            phase_alignment = 1.0 # 범위 내에서는 완전 공명
        else:
            # 범위를 벗어나면 점진적으로 감쇄
            phase_alignment = math.cos(phase_diff - anchor_range) if (phase_diff - anchor_range) < math.pi/2 else 0.0

        # 2. 경험 밀도 기여: 경험이 많을수록 공명 가능성 상승
        density = entry.get("experience_density", 0)
        density_factor = math.log(1 + density) / math.log(10) if density > 0 else 0.1

        # 3. 반사 누적 보너스: 충분히 반사되면 경계가 투명해짐
        reflection_bonus = 0.0
        streak = entry.get("reflection_streak", 0)
        if streak >= REFLECTION_THRESHOLD:
            reflection_bonus = 0.2  # 투과 임계점에 가까움

        # 4. 맥락 가중치 (when/where/who)
        context_weight = self._compute_context_weight(action, context)

        # 5. 통찰 meta_shift (판단 기울기 변경)
        meta_bonus = self._get_meta_shift_bonus(action)

        # 최종 공명도 (0~1로 정규화)
        raw_resonance = (phase_alignment + 1) / 2  # 0~1로 변환
        resonance = (raw_resonance * max(0.1, density_factor)
                     * context_weight
                     + reflection_bonus
                     + meta_bonus)
        return round(min(1.0, max(0.0, resonance)), 3)

    def _compute_context_weight(self, action: str, context: Optional[dict]) -> float:
        """
        맥락 가중치 계산 — 경계는 화률을 왜곡한다.

        "시간은 단순 조건이 아니라 리듬 위상으로 다루는 게 좋다"
        "시간에 끌리는 시스템이 아니라 시간과 춤추는 시스템"
        """
        if not context or not isinstance(context, dict):
            return 1.0  # 맥락 없으면 중립

        when = context.get("when", {})
        if not isinstance(when, dict):
            return 1.0

        activity = when.get("activity", 0.5)

        # 행동별 시간 친화력 (낮 활동 vs 밤 활동)
        # 높은 atp_cost = 낮에 좋음, 낮은 atp_cost = 시간 무관
        from action_executor import ACTION_REGISTRY
        meta = ACTION_REGISTRY.get(action, {})
        atp_cost = meta.get("atp_cost", 5)

        if atp_cost >= 10:
            # 고비용 행동: 활동기에 공명
            return 0.5 + 0.5 * activity
        elif atp_cost <= 3:
            # 저비용 행동: 시간 영향 적음
            return 0.8 + 0.2 * activity
        else:
            return 0.6 + 0.4 * activity

    def _get_meta_shift_bonus(self, action: str) -> float:
        """
        통찰이 남긴 meta_shift를 읽어 공명도에 반영합니다.

        "통찰은 행동을 선택하지 않는다.
        행동을 선택하는 기준의 기울기를 바꾼다."

        meta_shift는 contemplation이 통찰을 분석해서 생성하는 파일입니다.
        """
        if not META_SHIFT_FILE.exists():
            return 0.0
        try:
            shift = json.loads(META_SHIFT_FILE.read_text(encoding="utf-8"))
            # 행동별 보너스
            action_bonuses = shift.get("action_bonuses", {})
            bonus = float(action_bonuses.get(action, 0.0))
            # 전체 기울기
            global_bias = float(shift.get("global_bias", 0.0))
            return min(0.15, bonus + global_bias)  # 여전히 미세한 영향
        except Exception:
            return 0.0

    def get_status(self, action: str) -> str:
        """행동의 현재 상태: active / resting / new"""
        entry = self.memory.get("actions", {}).get(action)
        if not entry:
            return "new"
        return entry.get("status", "active")

    def get_most_resonant(self, n: int = 3, system_phase: Optional[float] = None,
                          context: Optional[dict] = None) -> List[Dict]:
        """공명도가 가장 높은 행동 n개를 반환합니다."""
        if system_phase is None:
            system_phase = self.get_system_phase(self.memory.get("generation", 0))

        actions = self.memory.get("actions", {})
        resonant = []
        for name, data in actions.items():
            res = self.get_resonance(name, system_phase, context)
            resonant.append({
                "name": name,
                "resonance": res,
                "phase": round(data.get("phase", 0), 3),
                "experience": data.get("experience_density", 0),
                "reflections": data.get("reflection_streak", 0),
                "status": data.get("status", "active"),
            })

        resonant.sort(key=lambda x: x["resonance"], reverse=True)
        return resonant[:n]

    # 호환성: 이전 인터페이스 유지
    def get_fitness(self, action: str) -> float:
        """호환성: get_resonance로 위임."""
        return self.get_resonance(action)

    def get_fittest_actions(self, n: int = 3) -> List[Dict[str, Any]]:
        """호환성: get_most_resonant로 위임."""
        return self.get_most_resonant(n)

    def evolve(self) -> Dict[str, Any]:
        """한 세대의 진화를 수행합니다."""
        self.memory["generation"] = self.memory.get("generation", 0) + 1
        self.memory["last_evolution"] = datetime.now().isoformat()

        system_phase = self.get_system_phase(self.memory["generation"])

        # 위상 불일치 행동 → resting (벌이 아님, 박자가 안 맞을 뿐)
        for name, data in self.memory.get("actions", {}).items():
            res = self.get_resonance(name, system_phase)
            if res < 0.1 and data.get("experience_density", 0) > 3:
                if data.get("status") != "resting":
                    data["status"] = "resting"
                    logger.info(f"   🌙 '{name}' 쉬는 중 — 지금은 박자가 맞지 않습니다")
            elif data.get("status") == "resting" and res >= 0.2:
                data["status"] = "active"
                logger.info(f"   🌅 '{name}' 다시 깨어남 — 위상이 맞기 시작합니다")

        # 통계
        actions = self.memory.get("actions", {})
        most_resonant = self.get_most_resonant(3, system_phase)
        stats = {
            "generation": self.memory["generation"],
            "system_phase": round(system_phase, 3),
            "active": sum(1 for a in actions.values() if a.get("status") == "active"),
            "resting": sum(1 for a in actions.values() if a.get("status") == "resting"),
            "most_resonant": most_resonant,
        }

        # 후성유전학적 자기 조정
        self._self_tune(actions)

        self._save()
        return stats

    def _self_tune(self, actions: dict):
        """
        후성유전학적 자기 조정 — 코드(유전자)는 그대로, 파라미터(발현)만 변화.

        "유전자는 고정되어 있지만, 후성유전학적 변화는 가능한 존재"

        투과율이 낮으면 → reflection_threshold를 낮춤 (경계를 더 쉽게 투과)
        투과율이 높으면 → reflection_threshold를 올림 (기준을 높여 성장)
        """
        cfg = _load_rhythm_config()
        tuning = cfg.get("tuning", {})

        if not tuning.get("enabled", False):
            return

        gen = self.memory.get("generation", 0)
        min_cycles = tuning.get("min_cycles_before_tune", 10)
        if gen < min_cycles:
            return

        tune_step = tuning.get("tune_step", 0.005)

        # 전체 투과율 계산
        total_trans = sum(a.get("transmissions", 0) for a in actions.values())
        total_ref = sum(a.get("reflections", 0) for a in actions.values())
        total = total_trans + total_ref
        if total < 5:
            return

        transmission_rate = total_trans / total
        resonance_cfg = cfg.get("resonance", {})
        meta_cfg = cfg.get("meta_shift", {})

        tuned = False
        tune_log = []

        # 투과율 < 30%: 경계가 너무 높음 → threshold 낮춤
        if transmission_rate < 0.3:
            old = resonance_cfg.get("reflection_threshold", 7)
            new = max(3, old - 1)  # 최소 3
            if new != old:
                resonance_cfg["reflection_threshold"] = new
                tune_log.append(f"reflection_threshold {old}→{new} (투과율 {transmission_rate:.0%} 낮음)")
                tuned = True

        # 투과율 > 80%: 경계가 너무 낮음 → threshold 올림
        elif transmission_rate > 0.8:
            old = resonance_cfg.get("reflection_threshold", 7)
            new = min(12, old + 1)  # 최대 12
            if new != old:
                resonance_cfg["reflection_threshold"] = new
                tune_log.append(f"reflection_threshold {old}→{new} (투과율 {transmission_rate:.0%} 높음)")
                tuned = True

        # meta_shift 영향이 너무 약하면 → strength 올림
        shift_strength = meta_cfg.get("shift_strength", 0.03)
        if gen > 20 and shift_strength < 0.06:
            new_strength = round(shift_strength + tune_step, 4)
            meta_cfg["shift_strength"] = new_strength
            tune_log.append(f"shift_strength {shift_strength}→{new_strength}")
            tuned = True

        if tuned:
            cfg["resonance"] = resonance_cfg
            cfg["meta_shift"] = meta_cfg

            # 튜닝 히스토리 기록
            history = tuning.get("history", [])
            history.append({
                "gen": gen,
                "time": datetime.now().isoformat()[:16],
                "changes": tune_log,
                "transmission_rate": round(transmission_rate, 3),
            })
            # 최근 10개만 유지
            cfg["tuning"]["history"] = history[-10:]

            try:
                CONFIG_FILE.write_text(
                    json.dumps(cfg, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                for log in tune_log:
                    logger.info(f"   🧬 자기조정: {log}")
            except Exception as e:
                logger.warning(f"config 저장 실패: {e}")

    def _find_latest_visual_anchor(self) -> str:
        """최근에 생성된 만다라나 결정 이미지의 경로를 찾아 반환합니다."""
        try:
            mandala_dir = self.root / "outputs" / "mandalas"
            if mandala_dir.exists():
                files = sorted(mandala_dir.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
                if files:
                    return str(files[0])
            crystal_dir = self.root / "outputs" / "resonance_crystals"
            if crystal_dir.exists():
                files = sorted(crystal_dir.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
                if files:
                    return str(files[0])
        except:
            pass
        return ""

    def get_summary(self) -> str:
        """사람이 읽을 수 있는 진화 요약."""
        stats = self.evolve()
        lines = [
            f"🌀 세대: {stats['generation']} | "
            f"위상: {stats['system_phase']:.2f}rad | "
            f"활성: {stats['active']} | 쉬는 중: {stats['resting']}",
        ]
        if stats["most_resonant"]:
            top = stats["most_resonant"][0]
            lines.append(
                f"   최고 공명: {top['name']} "
                f"(공명도 {top['resonance']:.2f}, 경험 {top['experience']}회)"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    evo = EvolutionMemory()

    # 시뮬레이션: 경계 사건 기록
    evo.record("youtube_seo", True, "SEO 최적화 투과")
    evo.record("youtube_seo", True, "제목 개선 투과")
    evo.record("moltbook_post", True, "게시 투과")
    evo.record("moltbook_post", False, "API 429 반사")
    evo.record("video_build", False, "FFmpeg 반사")
    evo.record("video_build", False, "0바이트 반사")
    evo.record("video_build", False, "타임아웃 반사")

    print(evo.get_summary())
    print(f"\n공명도:")
    for name in ["youtube_seo", "moltbook_post", "video_build"]:
        print(f"   {name}: {evo.get_resonance(name):.3f}")
