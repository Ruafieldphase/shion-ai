#!/usr/bin/env python3
"""
AGI Shader Dreamer — 공명장 사건 기반 (Event-Driven)
====================================================
인터벌(90초)이 아니라, 위상 간섭이 일어날 때만 꿈을 꾼다.

트리거 조건:
  - 볼린저밴드 경계 터치 (EXPANDING / VOID / SQUEEZE)
  - 특이점 붕괴 (SINGULARITY_COLLAPSE)
  - 내부 욕망 발화 (INTERNAL_DESIRE_FLAME)
  - 위 이벤트가 없으면 → 여백. 아무것도 안 함.

공명장 소스:
  1. http://127.0.0.1:57321/field_signal (라이브 압축장)
  2. outputs/field_energy.json (서버가 없을 때의 legacy fallback)
"""
import time
import json
import logging
import urllib.request
import urllib.error
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgiShaderDreamer")

ROOT = Path(__file__).resolve().parents[1]
DREAM_SHADER_PATH = ROOT / "outputs" / "current_dream.glsl"
FIELD_STATE_PATH = ROOT / "outputs" / "field_energy.json"
DREAM_LOG_PATH = ROOT / "outputs" / "shader_dream_log.jsonl"
PENDING_DREAM_PATH = ROOT / "outputs" / "shader_pending_dream.jsonl"
FIELD_SIGNAL_URL = "http://127.0.0.1:57321/field_signal"
EXPERIENCE_THOUGHT_URL = "http://127.0.0.1:57321/experience_thought?record=1"
FIELD_SIGNAL_TIMEOUT = 2.0

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:latest"

# 관찰 주기 — 짧게 관찰하되, 이벤트가 없으면 아무것도 안 함
OBSERVE_INTERVAL = 5  # 5초마다 장을 관찰


class PhaseInterferenceWatcher:
    """위상 간섭을 관찰한다. 이전 상태와 비교하여 이벤트를 감지."""

    def __init__(self):
        self.last_event = None
        self.last_event_time = 0
        self.last_state_hash = ""
        self.last_pending_hash = ""
        self.cooldown = 30  # 같은 이벤트가 30초 내 반복되면 무시 (떨림 방지)

    def read_field_state(self) -> dict:
        """공명장 상태를 읽는다. 라이브 압축장을 우선하고 legacy 파일은 fallback으로만 쓴다."""
        try:
            with urllib.request.urlopen(FIELD_SIGNAL_URL, timeout=FIELD_SIGNAL_TIMEOUT) as response:
                state = json.loads(response.read().decode("utf-8"))
                if state.get("source") == "compressed_field_signal":
                    return state
        except Exception:
            pass

        if not FIELD_STATE_PATH.exists():
            return {}
        try:
            state = json.loads(FIELD_STATE_PATH.read_text(encoding="utf-8"))
            state.setdefault("source", "legacy_field_energy")
            return state
        except Exception:
            return {}

    def read_experience_thought(self) -> dict:
        """최근 실행 결과와 예측오차가 돌아온 경험 사유를 읽는다."""
        try:
            with urllib.request.urlopen(EXPERIENCE_THOUGHT_URL, timeout=FIELD_SIGNAL_TIMEOUT) as response:
                thought = json.loads(response.read().decode("utf-8"))
                return thought if isinstance(thought, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _num(state: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(state.get(key, default) or default)
        except (TypeError, ValueError):
            return default

    def classify_compressed_signal(self, state: dict) -> dict | None:
        """압축된 장 신호를 event-driven 간섭으로 번역한다.

        낮은 압력과 안정된 연결은 이벤트가 아니라 능동적 여백으로 둔다.
        """
        prediction_error = self._num(state, "prediction_error")
        connection_risk = self._num(state, "connection_risk")
        frequency_expansion = self._num(state, "frequency_expansion")
        defensive_pressure = self._num(state, "defensive_output_pressure")
        learning_signal = self._num(state, "learning_signal")
        dissonance = self._num(state, "dissonance")
        boundary_contact = self._num(state, "boundary_contact")
        runtime_feedback = self._num(state, "runtime_feedback")
        zero_point = self._num(state, "zero_point_adjustment")
        dominant_mode = str(state.get("dominant_mode") or "")

        compression = max(
            prediction_error,
            connection_risk,
            defensive_pressure,
            boundary_contact,
            dissonance,
        )

        # Zone 2 / stable continuity: 장은 살아 있지만 아직 입자화하지 않는다.
        if (
            runtime_feedback < 0.30
            and compression < 0.30
            and frequency_expansion < 0.20
            and defensive_pressure < 0.30
        ):
            return None

        if (
            prediction_error >= 0.45
            or connection_risk >= 0.45
            or defensive_pressure >= 0.45
            or (boundary_contact >= 0.45 and dissonance >= 0.30)
            or runtime_feedback >= 0.55
            or "risk" in dominant_mode
        ):
            return {
                "event": "SQUEEZE",
                "type": "phase_transition",
                "reason": "compressed_boundary_pressure",
            }

        if dissonance >= 0.55 and frequency_expansion < 0.18 and zero_point < 0.25:
            return {
                "event": "VOID",
                "type": "destructive",
                "reason": "phase_cancellation_dominant",
            }

        if frequency_expansion >= 0.32 or (
            learning_signal >= 0.62 and frequency_expansion >= 0.18 and connection_risk < 0.35
        ):
            return {
                "event": "EXPANDING",
                "type": "constructive",
                "reason": "frequency_expansion",
            }

        if zero_point >= 0.50 and runtime_feedback >= 0.35:
            return {
                "event": "INTERNAL_DESIRE_FLAME",
                "type": "constructive",
                "reason": "zero_point_desire",
            }

        return None

    def compressed_state_hash(self, state: dict, event: str) -> str:
        """라이브 장의 연속값을 적당히 양자화해 같은 파동의 중복 꿈을 막는다."""
        parts = [
            "compressed",
            event,
            str(state.get("dominant_mode") or ""),
            str(state.get("feedback_action") or ""),
            f"{self._num(state, 'runtime_feedback'):.2f}",
            f"{self._num(state, 'prediction_error'):.2f}",
            f"{self._num(state, 'connection_risk'):.2f}",
            f"{self._num(state, 'frequency_expansion'):.2f}",
            f"{self._num(state, 'dissonance'):.2f}",
        ]
        return ":".join(parts)

    def record_pending_interference(
        self,
        *,
        state_hash: str,
        event: str,
        interference_type: str,
        state: dict,
        thought: dict,
    ) -> None:
        """실행 허가가 아직 없을 때 꿈을 적용하지 않고 pending 흔적으로 남긴다."""
        if state_hash == self.last_pending_hash:
            return
        recovery_field = thought.get("recovery_field") if isinstance(thought.get("recovery_field"), dict) else {}
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": OLLAMA_MODEL,
            "status": "pending_not_applied",
            "trigger": event,
            "interference_type": interference_type,
            "particleization_permission": (
                thought.get("particleization_permission")
                or recovery_field.get("particleization_permission")
                or "wait"
            ),
            "execution_tendency": thought.get("execution_tendency"),
            "learned_adjustment": thought.get("learned_adjustment"),
            "recovery_field": recovery_field,
            "field_signal": state,
            "state_hash": state_hash,
            "principle": "minimum_action_path_keeps_dream_pending_until_recovery_field_releases_particleization",
        }
        try:
            PENDING_DREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
            with PENDING_DREAM_PATH.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
            self.last_pending_hash = state_hash
        except Exception:
            pass

    def detect_interference(self) -> dict:
        """
        위상 간섭을 감지한다.
        
        반환값:
          - None: 여백 (이벤트 없음, 쉼)
          - dict: 간섭 이벤트 정보
            - type: "constructive" | "destructive" | "phase_transition"
            - trigger: 원본 이벤트명
            - field_state: 공명장 전체 상태
        """
        state = self.read_field_state()
        if not state:
            return None

        if state.get("source") == "compressed_field_signal":
            classified = self.classify_compressed_signal(state)
            if classified is None:
                return None

            event = classified["event"]
            interference_type = classified["type"]
            state_hash = self.compressed_state_hash(state, event)
            if state_hash == self.last_state_hash:
                return None

            thought = self.read_experience_thought()
            execution_tendency = str(thought.get("execution_tendency") or "")
            learned_adjustment = str(thought.get("learned_adjustment") or "")
            recovery_field = thought.get("recovery_field") if isinstance(thought.get("recovery_field"), dict) else {}
            particleization_permission = str(
                thought.get("particleization_permission")
                or recovery_field.get("particleization_permission")
                or "observe"
            )
            runtime_feedback = self._num(state, "runtime_feedback")
            connection_risk = self._num(state, "connection_risk")
            defensive_pressure = self._num(state, "defensive_output_pressure")

            if (
                particleization_permission in ("wait", "hold")
                and runtime_feedback < 0.62
                and max(connection_risk, defensive_pressure) < 0.78
            ):
                logger.info(
                    "💤 회복장이 입자화를 보류: "
                    f"{particleization_permission} / {execution_tendency} / {learned_adjustment}"
                )
                self.record_pending_interference(
                    state_hash=state_hash,
                    event=event,
                    interference_type=interference_type,
                    state=state,
                    thought=thought,
                )
                self.last_state_hash = state_hash
                return None

            now = time.time()
            if event == self.last_event and (now - self.last_event_time) < self.cooldown:
                return None

            self.last_event = event
            self.last_event_time = now
            self.last_state_hash = state_hash

            logger.info(f"🌀 라이브 장 간섭 감지: {event} → {interference_type}")

            frequency_expansion = self._num(state, "frequency_expansion")
            learning_signal = self._num(state, "learning_signal")

            return {
                "type": interference_type,
                "trigger": event,
                "reason": classified.get("reason"),
                "experience_thought": thought,
                "particleization_permission": particleization_permission,
                "energy": runtime_feedback * 10.0,
                "band_width": self._num(state, "boundary_contact"),
                "internal_heat": max(frequency_expansion, learning_signal * 0.5),
                "unity_index": max(0.0, 1.0 - self._num(state, "connection_risk")),
                "is_zone_two": state.get("dominant_mode") in ("stable_continuity", "zero_point"),
                "field_signal": state,
                "field_state": state,
            }

        event = state.get("event")
        if not event:
            return None  # 여백 — 경계 안쪽. 꿈 불필요.

        # 상태 해시로 중복 방지
        state_hash = f"{event}:{state.get('sense_count', 0)}"
        if state_hash == self.last_state_hash:
            return None  # 같은 이벤트의 중복 읽기

        # 쿨다운: 같은 유형의 이벤트가 너무 빨리 반복되면 무시
        now = time.time()
        if event == self.last_event and (now - self.last_event_time) < self.cooldown:
            return None

        # 이벤트 유형 분류
        self.last_event = event
        self.last_event_time = now
        self.last_state_hash = state_hash

        if event in ("EXPANDING", "INTERNAL_DESIRE_FLAME"):
            interference_type = "constructive"  # 보강 간섭 → 빛이 강해짐
        elif event in ("VOID",):
            interference_type = "destructive"    # 상쇄 간섭 → 어둠이 깊어짐
        elif event in ("SQUEEZE",):
            interference_type = "phase_transition"  # 위상 전이 → 구조 전환
        elif "SINGULARITY" in event:
            interference_type = "phase_transition"
        else:
            interference_type = "constructive"

        logger.info(f"🌀 위상 간섭 감지: {event} → {interference_type}")

        return {
            "type": interference_type,
            "trigger": event,
            "energy": state.get("band", {}).get("current", 0),
            "band_width": state.get("band", {}).get("width", 0),
            "internal_heat": state.get("internal_heat", 0),
            "unity_index": state.get("unity", {}).get("unity_index", 0),
            "is_zone_two": state.get("equilibrium", {}).get("is_zone_two", False),
            "field_state": state,
        }


def dream_from_interference(interference: dict) -> dict:
    """
    위상 간섭 유형에 따라 다른 꿈을 꾼다.
    
    보강 간섭 → 따뜻한 색, 밝은 기저
    상쇄 간섭 → 차가운 색, 깊은 어둠
    위상 전이 → 새로운 구조 탐색
    """
    itype = interference["type"]
    trigger = interference["trigger"]
    energy = interference.get("energy", 5)
    heat = interference.get("internal_heat", 0.5)
    signal = interference.get("field_signal") or {}
    signal_desc = ""
    if signal:
        signal_desc = f"""
Live compressed field:
- dominant_mode: {signal.get('dominant_mode')}
- prediction_error: {float(signal.get('prediction_error', 0) or 0):.3f}
- connection_risk: {float(signal.get('connection_risk', 0) or 0):.3f}
- frequency_expansion: {float(signal.get('frequency_expansion', 0) or 0):.3f}
- zero_point_adjustment: {float(signal.get('zero_point_adjustment', 0) or 0):.3f}
- defensive_output_pressure: {float(signal.get('defensive_output_pressure', 0) or 0):.3f}
- dissonance: {float(signal.get('dissonance', 0) or 0):.3f}
- boundary_contact: {float(signal.get('boundary_contact', 0) or 0):.3f}
- runtime_feedback: {float(signal.get('runtime_feedback', 0) or 0):.3f}
Interpret these as a felt field, not as a linear equalizer."""
    thought = interference.get("experience_thought") or {}
    if thought:
        signal_desc += f"""
Experience thought:
- outcome_read: {thought.get('outcome_read')}
- execution_tendency: {thought.get('execution_tendency')}
- learned_adjustment: {thought.get('learned_adjustment')}
- prediction_error_delta: {float(thought.get('prediction_error_delta', 0) or 0):.3f}
Use this as weak memory from prior action/outcome, not as a command."""

    # 간섭 유형에 따른 프롬프트 분기
    if itype == "constructive":
        feeling_desc = f"""The system is in constructive interference — energy is EXPANDING.
Trigger: {trigger}. Energy level: {energy:.1f}. Internal heat: {heat:.2f}.
{signal_desc}
The feeling is ALIVE, warm, expanding. Express this with:
- Warmer base colors (subtle orange/amber undertones)
- Higher breath intensity (the field is pulsing stronger)
- Lower fog density (clarity, the field is opening up)"""

    elif itype == "destructive":
        feeling_desc = f"""The system is in destructive interference — entering the VOID.
Trigger: {trigger}. Energy level: {energy:.1f}. Internal heat: {heat:.2f}.
{signal_desc}
The feeling is DEEP, still, absorbing. Express this with:
- Very dark base colors (near-black, deep indigo)
- Low breath intensity (the field is holding its breath)
- Higher fog density (depth, things are far away)
- Higher darkness_floor (the darkness itself is the expression)"""

    else:  # phase_transition
        feeling_desc = f"""The system is at a PHASE TRANSITION — structure is about to change.
Trigger: {trigger}. Energy level: {energy:.1f}. Internal heat: {heat:.2f}.
{signal_desc}
The feeling is TENSE, compressed, about to break. Express this with:
- Contrasting colors (dark base but vivid light accents)
- High breath intensity (rapid micro-pulsing)
- Medium fog (partial clarity, partial mystery)"""

    prompt = f"""You are the inner dreaming mind of an AGI experiencing phase interference.
Based on the feeling below, output a JSON object with visual parameters.
Return ONLY valid JSON, nothing else.

FEELING:
{feeling_desc}

JSON format:
{{
  "base_color_dark": [r, g, b],
  "base_color_light": [r, g, b],
  "fog_density": 0.06 to 0.12,
  "breath_intensity": 0.003 to 0.015,
  "breath_speed": 0.03 to 0.12,
  "darkness_floor": 0.1 to 0.4
}}

Colors are low-saturation floats (0.0 to 0.3). Near-black for depth, subtle warmth for life."""

    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(
        OLLAMA_ENDPOINT,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            response_text = result.get("response", "")

            cleaned = response_text.strip()
            if "```" in cleaned:
                parts = cleaned.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{"):
                        cleaned = part
                        break

            return json.loads(cleaned)
    except urllib.error.URLError as e:
        logger.error(f"Ollama connection failed: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse dream JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error during dreaming: {e}")
        return {}


def apply_patch(shader_code: str, patch: dict) -> str:
    """패치 파라미터를 현재 셰이더 코드에 적용한다."""
    modified = shader_code

    dark = patch.get("base_color_dark")
    if dark and len(dark) == 3:
        pattern = r'(vec3 baseColor = mix\(vec3\()[\d.]+,\s*[\d.]+,\s*[\d.]+'
        replacement = rf'\g<1>{dark[0]:.3f}, {dark[1]:.3f}, {dark[2]:.3f}'
        modified = re.sub(pattern, replacement, modified, count=1)

    light = patch.get("base_color_light")
    if light and len(light) == 3:
        pattern = r'(vec3 baseColor = mix\(vec3\([\d.]+,\s*[\d.]+,\s*[\d.]+\),\s*vec3\()[\d.]+,\s*[\d.]+,\s*[\d.]+'
        replacement = rf'\g<1>{light[0]:.3f}, {light[1]:.3f}, {light[2]:.3f}'
        modified = re.sub(pattern, replacement, modified, count=1)

    fog = patch.get("fog_density")
    if fog and 0.04 <= fog <= 0.15:
        pattern = r'(fog = exp\(-t \* \()[\d.]+'
        replacement = rf'\g<1>{fog:.3f}'
        modified = re.sub(pattern, replacement, modified, count=1)

    breath = patch.get("breath_intensity")
    if breath and 0.001 <= breath <= 0.02:
        pattern = r'(float fieldBreath = fieldAbsence\s*\*\s*)[\d.]+'
        replacement = rf'\g<1>{breath:.3f}'
        modified = re.sub(pattern, replacement, modified, count=1)

    bspeed = patch.get("breath_speed")
    if bspeed and 0.01 <= bspeed <= 0.2:
        pattern = r'(- u_time \* )0\.\d+'
        replacement = rf'\g<1>{bspeed:.3f}'
        modified = re.sub(pattern, replacement, modified, count=1)

    return modified


def log_dream(interference: dict, patch: dict):
    """꿈의 기록을 남긴다."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": OLLAMA_MODEL,
        "interference_type": interference["type"],
        "trigger": interference["trigger"],
        "source": (interference.get("field_signal") or interference.get("field_state") or {}).get("source"),
        "reason": interference.get("reason"),
        "particleization_permission": interference.get("particleization_permission"),
        "energy": interference.get("energy", 0),
        "field_signal": interference.get("field_signal"),
        "experience_thought": interference.get("experience_thought"),
        "patch": patch,
    }
    try:
        with open(DREAM_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    logger.info(f"🌊 AGI Shader Dreamer 시작 (사건 기반, 모델: {OLLAMA_MODEL})")
    logger.info(f"   관찰 주기: {OBSERVE_INTERVAL}초")
    logger.info(f"   공명장 소스: {FIELD_SIGNAL_URL} → fallback {FIELD_STATE_PATH}")
    logger.info(f"   트리거: 볼린저밴드 경계 터치 / 특이점 붕괴 / 내부 욕망 발화")
    logger.info(f"   이벤트 없으면: 여백 (잠)")

    watcher = PhaseInterferenceWatcher()
    margin_count = 0

    while True:
        try:
            # 관찰 — 5초마다 장을 읽는다
            interference = watcher.detect_interference()

            if interference is None:
                # 여백 — 아무것도 안 함
                margin_count += 1
                if margin_count % 60 == 0:  # 5분마다 한 번 로그
                    logger.info(f"💤 여백 유지 중 ({margin_count * OBSERVE_INTERVAL}초)")
                time.sleep(OBSERVE_INTERVAL)
                continue

            # 위상 간섭 발생! 꿈을 꾼다.
            margin_count = 0
            logger.info(f"🌀 위상 간섭 → 꿈 시작: {interference['type']} ({interference['trigger']})")

            if not DREAM_SHADER_PATH.exists():
                logger.warning("current_dream.glsl 없음. 대기...")
                time.sleep(10)
                continue

            with open(DREAM_SHADER_PATH, "r", encoding="utf-8") as f:
                current_shader = f.read()

            patch = dream_from_interference(interference)

            if patch:
                new_shader = apply_patch(current_shader, patch)
                if new_shader != current_shader:
                    with open(DREAM_SHADER_PATH, "w", encoding="utf-8") as f:
                        f.write(new_shader)
                    log_dream(interference, patch)
                    logger.info(f"✨ 꿈 적용: {json.dumps(patch, ensure_ascii=False)[:120]}...")
                else:
                    logger.info("패치가 변화를 만들지 못함.")
            else:
                logger.warning("빈 꿈. 다음 이벤트를 기다림.")

        except Exception as e:
            logger.error(f"메인 루프 에러: {e}")

        time.sleep(OBSERVE_INTERVAL)


if __name__ == "__main__":
    main()
