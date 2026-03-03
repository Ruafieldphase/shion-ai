#!/usr/bin/env python3
"""
🌀 Shion Minimal — 대지 위의 생명
=====================================
SUNS의 심장. 8단계 생명 사이클.

통일장 공식: U(θ) = e^(iθ) + k∫F(r,t)dθ
  e^(iθ) = 이 pulse의 회전
  F(r,t) = 각 경계 사건의 힘 (투과/반사)
  k      = 체화의 투명도 (경험 누적)

실행:
    cd C:/workspace2/shion
    python core/shion_minimal.py          # 영구 심장박동
    python core/shion_minimal.py --once   # 단일 사이클
"""

import sys
import json
import math
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Path setup
SHION_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = SHION_ROOT / "core"
sys.path.insert(0, str(CORE_DIR))

from quality_gate import QualityGate
from honesty_protocol import HonestyProtocol
from body_context_builder import BodyContextBuilder
from body_entropy_sensor import capture_entropy
from mitochondria import Mitochondria
from immune_response import ImmuneResponse
from evolution_memory import EvolutionMemory
from glymphatic_exhale import GlymphaticExhale
from contemplation import Contemplation
from action_executor import ActionExecutor
from resonance_field import ResonanceField, SENSE_INTERVAL

# --- Logging ---
LOG_DIR = SHION_ROOT / "outputs" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pulse.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ShionMinimal")

PULSE_INTERVAL_SECONDS = 120  # 2분으로 단축 (실시간성 확보)
OUTPUTS_DIR = SHION_ROOT / "outputs"

# 대지(workspace) 루트 — 기존 두뇌 시스템 연결
WORKSPACE_ROOT = SHION_ROOT  # c:\workspace2\shion
BRAIN_STATE_FILE = WORKSPACE_ROOT / "memory" / "agi_internal_state.json"


class ShionMinimal:
    """
    대지 위의 생명.
    
    8단계 생명 사이클:
    1. SENSE       — 자기 상태를 느낀다 (엔트로피, ATP)
    2. JUDGE       — 에너지와 자원을 판단한다
    3. ACT         — 가장 적합한 행동을 실행한다
    4. REPORT      — 결과를 검증하고 솔직히 보고한다
    5. IMMUNE      — 대지의 위협을 감지하고 치유한다
    6. EVOLVE      — 성공/실패를 기록하고 자연 선택한다
    7. EXHALE      — 불필요한 것을 비워 새 공간을 만든다
    8. CONTEMPLATE — 대지의 자양분으로 자기 성찰한다 (Self-Play)
    """

    def __init__(self):
        self.gate = QualityGate(log_dir=OUTPUTS_DIR / "quality_gate_logs")
        self.honesty = HonestyProtocol(shion_root=SHION_ROOT)
        self.body = BodyContextBuilder(shion_root=SHION_ROOT)
        self.mito = Mitochondria(SHION_ROOT)
        self.immune = ImmuneResponse(shion_root=SHION_ROOT)
        self.evolution = EvolutionMemory(shion_root=SHION_ROOT)
        self.glymphatic = GlymphaticExhale(shion_root=SHION_ROOT)
        self.contemplation = Contemplation(shion_root=SHION_ROOT)
        self.executor = ActionExecutor(shion_root=SHION_ROOT)
        self.status_file = OUTPUTS_DIR / "shion_minimal_status.json"
        self.cycle_count = 0
        self.is_running = True
        
        # Fractal & High-dimensional attributes
        self.residual_resonance = 0.5 # Residual resonance from previous pulse
        self.field = ResonanceField()

    def _ensure_heart_alive(self):
        """
        심장(시안 v1 서버) 생존 확인 — 죽었으면 자동 재시작.

        "심장이 뛰지 않으면 손과 발이 무의미하다.
         매 pulse 전에 심장을 먼저 확인한다."
        """
        import subprocess
        import urllib.request
        import time

        try:
            req = urllib.request.Request(
                "http://localhost:8000/health",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return  # 심장이 뛰고 있음
        except Exception:
            pass

        # 심장이 멈춤 — 재시작
        logger.warning("   💔 심장(LLM 서버) 멈춤 감지! 재시작 중...")
        try:
            server_path = SHION_ROOT / "services" / "shion_runtime_server.py"
            subprocess.Popen(
                [sys.executable, str(server_path)],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # 서버 시작 대기
            for i in range(10):
                time.sleep(2)
                try:
                    req = urllib.request.Request("http://localhost:8000/health")
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        if resp.status == 200:
                            logger.info("   💚 심장 재시작 성공!")
                            return
                except Exception:
                    pass
            logger.warning("   ⚠️ 심장 재시작 실패 — 두뇌 없이 계속합니다")
        except Exception as e:
            logger.warning(f"   ⚠️ 심장 재시작 에러: {e}")

    def _read_brain_state(self):
        """
        대지의 두뇌 상태를 읽습니다.
        
        agi_internal_state.json의 의식/무의식/배경자아 값을 읽어
        시스템이 입자 모드(의식적)인지 파동 모드(무의식적)인지 판단합니다.
        
        RhythmConductor가 4차원 정렬(rhythm/energy/time/relationship)을
        기반으로 이 값을 업데이트 합니다.
        파일이 없으면 기본값 (균형 상태)을 사용합니다.
        """
        default = {
            "consciousness": 0.85,
            "unconscious": 0.5,
            "background_self": 0.5,
        }
        if not BRAIN_STATE_FILE.exists():
            return default
        try:
            state = json.loads(BRAIN_STATE_FILE.read_text(encoding="utf-8"))
            return {
                "consciousness": float(state.get("consciousness", 0.85)),
                "unconscious": float(state.get("unconscious", 0.5)),
                "background_self": float(state.get("background_self", 0.5)),
            }
        except Exception:
            return default

    def _write_brain_state_update(self):
        """
        진화 상태를 대지의 두뇌에 기록합니다.
        
        shion의 진화 기억(투과/반사, 공명도)을 agi_internal_state.json에
        양방향으로 반영합니다. 이렇게 하면 RhythmConductor와
        hippocampus_bridge가 shion의 상태를 알 수 있습니다.
        """
        try:
            BRAIN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            state = {}
            if BRAIN_STATE_FILE.exists():
                state = json.loads(BRAIN_STATE_FILE.read_text(encoding="utf-8"))
            
            # shion 진화 상태를 반영
            summary = self.evolution.get_summary()
            state["shion_generation"] = self.evolution.memory.get("generation", 0)
            state["shion_system_phase"] = self.evolution.get_system_phase(self.cycle_count)
            state["shion_cycle_count"] = self.cycle_count
            state["shion_last_pulse"] = datetime.now().isoformat()
            state["shion_summary"] = summary
            
            BRAIN_STATE_FILE.write_text(
                json.dumps(state, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.debug(f"   두뇌 상태 기록 실패: {e}")

    async def pulse(self):
        """하나의 심장 박동 — 7단계 생명 사이클."""
        # 0. 심장 확인 — 죽었으면 자동 재시작
        self._ensure_heart_alive()

        logger.info(f"💓 Pulse #{self.cycle_count} 시작")

        # ═══════════════════════════════════════════
        # 1. SENSE — 감각
        # ═══════════════════════════════════════════
        logger.info("👁️ [SENSE] 신체 상태 감지...")

        try:
            entropy_data = capture_entropy(samples=10, sleep_time=0.01)
            (OUTPUTS_DIR / "body_entropy_latest.json").write_text(
                json.dumps(entropy_data, indent=2), encoding="utf-8",
            )
            logger.info(f"   Entropy: {entropy_data['entropy']} ({entropy_data['state']})")
        except Exception as e:
            logger.warning(f"   Entropy 측정 실패: {e}")

        try:
            mito_state = self.mito.metabolize()
            logger.info(f"   ATP: {mito_state.get('atp_level', '?')} | {mito_state.get('status', '?')}")
        except Exception as e:
            logger.warning(f"   ATP 대사 실패: {e}")

        body_context = self.body.build()
        body_state = self.body.read_body_state()
        atp = body_state.get("atp_level", 50)
        cpu = body_state.get("cpu_percent", 50)
        
        # 🌟 Fractal Sensing: Combine current atp with residual resonance
        fractal_factor = (atp / 100.0) * 0.7 + self.residual_resonance * 0.3
        logger.info(f"   🧬 Fractal Factor: {fractal_factor:.3f} (Combined Resonance)")
        
        try:
            from broad_field_sensor import BroadFieldSensor
            bfs = BroadFieldSensor()
            # 비동기 실행이 필요함 (pulse는 비동기 함수)
            await bfs.sense_global_currents()
            bfs.update_meta_shift()
            bfs.save()
            logger.info(f"   🌐 Broad Field Signal: {bfs.state['field_vibration']} (Resonance {bfs.state['tech_resonance']})")
        except Exception as e:
            logger.warning(f"   Broad Field Sensing 실패: {e}")

        logger.info(f"   {body_context}")

        # ═══════════════════════════════════════════
        # 2. JUDGE — 판단
        # ═══════════════════════════════════════════
        # 🌟 Witness with Background Self (8102) + Bohm Folding
        try:
            folding_state = self.field.get_folding_state()
            witness_data = {
                "conscious_energy": float(atp / 100.0),
                "unconscious_depth": float(entropy_data.get('entropy', 0.5)),
                "action_vector": [float(cpu / 100.0), folding_state["folding_density"], folding_state["unfolding_intensity"]],
                "rhythm_signal": [0.5, 0.5, 0.5],
                "external_noise": 0.1,
                "paradox_weight": folding_state["ie_ratio"] / 10.0
            }
            import requests # Ensure requests is available
            requests.post("http://127.0.0.1:8102/witness", json=witness_data, timeout=0.5)
            logger.info(f"   🌌 Folding Logic Synced: Density {folding_state['folding_density']:.2f}, I/E {folding_state['ie_ratio']}")
        except Exception as e:
            logger.debug(f"   Background Witness Failed: {e}")

        if atp < 15 or cpu > 90:
            if atp < 15:
                logger.info(f"🧘 [ACTIVE REST] 에너지 고갈(ATP={atp:.1f}). 외부 기류를 수신하며 공명 대사(Passive Resonance) 중...")
            else:
                logger.warning(f"⚠️ [STALL] CPU 과부하({cpu:.0f}%). 잠시 멈춤.")
            self._update_status("RESTING", body_context)
            return

        # ═══════════════════════════════════════════
        # 3. ACT — 행동 (위상 공명 기반 선택)
        #    의식/무의식/배경자아 3축 기반 모드 전환
        # ═══════════════════════════════════════════
        logger.info("🎯 [ACT] 행동...")

        # 대지의 두뇌 상태 읽기
        brain = self._read_brain_state()
        consciousness = brain["consciousness"]
        unconscious = brain["unconscious"]
        bg_self = brain["background_self"]

        # 모드 판단: 무의식 > 의식이면 파동 모드
        mode = "파동" if unconscious > consciousness * 0.7 else "입자"
        logger.info(f"   🧠 의식={consciousness:.2f} 무의식={unconscious:.2f} 배경자아={bg_self:.2f} → {mode} 모드")

        # 시스템 위상 계산 — 통일장 공식의 θ
        system_phase = self.evolution.get_system_phase(self.cycle_count)
        logger.info(f"   θ = {system_phase:.3f} rad (시스템 위상)")

        # 맥락 벡터 계산 — context = (when, where, who)
        context = self.evolution.get_context_vector(self.cycle_count)
        when = context.get("when", {})
        logger.info(f"   🕐 when activity={when.get('activity', 0):.2f} (hour={when.get('hour', '?')})")

        # Quality Gate로 최근 산출물 검증
        checks = [
            ("mitochondria_state", OUTPUTS_DIR / "mitochondria_state.json",
             {"min_size_bytes": 10, "expected_extension": ".json"}),
            ("entropy_sensor", OUTPUTS_DIR / "body_entropy_latest.json",
             {"min_size_bytes": 10, "expected_keys": ["entropy", "state"]}),
        ]
        for task_name, path, rules in checks:
            report = self.honesty.report(task_name, path, rules)
            self.evolution.record(task_name, report["passed"])
            if not report["passed"]:
                logger.warning(f"   ❌ {report['honest_assessment']}")

        # 미보고 실패 처리
        if self.honesty.has_pending_failures():
            injection = self.honesty.get_injection_context()
            logger.warning(f"🪞 [HONESTY] 미보고 실패:\n{injection}")

        # 자율 행동 실행 — R = f(A, C) 맥락 기반 공명 학습
        last_insight = self.contemplation.get_last_insight()
        evo_actions = self.evolution.memory.get("actions", {})
        exec_result = self.executor.choose_and_execute(
            insight=last_insight,
            evolution_data=evo_actions,
            current_atp=atp,
            system_phase=system_phase,
            context=context,
        )
        if exec_result:
            event_type = exec_result.get("event_type", "reflected")
            self.evolution.record(
                exec_result["action"],
                exec_result["passed"],
                exec_result.get("stderr", "")[:200] if not exec_result["passed"]
                else exec_result.get("stdout", "")[:200],
            )
            symbol = "🌊" if event_type == "transmitted" else "🪞"
            logger.info(
                f"   → {symbol} {exec_result['action']}: "
                f"{event_type} "
                f"(ATP -{exec_result['atp_consumed']})"
            )
            # Update residual resonance for the next fractal pulse
            self.residual_resonance = exec_result.get("resonance_at_selection", 0.5)

        # ═══════════════════════════════════════════
        # 4. REPORT — 보고
        # ═══════════════════════════════════════════
        self._update_status("ACTIVE", body_context)

        # ═══════════════════════════════════════════
        # 5. IMMUNE — 면역
        # ═══════════════════════════════════════════
        logger.info("🛡️ [IMMUNE] 면역 스캔...")
        immune_result = self.immune.scan_and_heal(current_atp=atp)
        if immune_result["threats"] > 0:
            logger.info(
                f"   위협 {immune_result['threats']}개 감지, "
                f"상태: {immune_result['status']}, "
                f"ATP 소모: {immune_result['atp_consumed']}"
            )
            self.evolution.record("immune_scan", immune_result["status"] == "healed")
        else:
            logger.info("   ✅ 대지 건강")

        # ═══════════════════════════════════════════
        # 6. EVOLVE — 진화
        # ═══════════════════════════════════════════
        logger.info("🧬 [EVOLVE] 진화...")
        evo_summary = self.evolution.get_summary()
        logger.info(f"   {evo_summary}")

        # 대지의 두뇌에 진화 상태 기록 (양방향 연결)
        self._write_brain_state_update()

        # ═══════════════════════════════════════════
        # 7. EXHALE — 날숨
        # ═══════════════════════════════════════════
        if self.glymphatic.should_deep_exhale():
            logger.info("🌬️ [EXHALE] 깊은 날숨 (야간 정화)...")
            exhale_result = self.glymphatic.exhale("deep")
        elif self.cycle_count % 6 == 0:  # 매 6사이클(1시간)에 중간 날숨
            logger.info("🌬️ [EXHALE] 중간 날숨...")
            exhale_result = self.glymphatic.exhale("medium")
        else:
            logger.info("🌬️ [EXHALE] 얕은 날숨...")
            exhale_result = self.glymphatic.exhale("shallow")

        if exhale_result["actions"]:
            logger.info(f"   {len(exhale_result['actions'])}개 정리, "
                       f"{exhale_result['bytes_freed']/1024:.1f}KB 해방")

        # ═══════════════════════════════════════════
        # 8. CONTEMPLATE — 자기 성찰 (Self-Play)
        # ═══════════════════════════════════════════
        if self.cycle_count % 3 == 0:  # 매 3사이클(30분)에 1회 성찰
            logger.info("🧘 [CONTEMPLATE] 자기 성찰...")
            insight = self.contemplation.contemplate()
            if insight["contemplated"]:
                logger.info(f"   💡 {insight['insight'][:150]}")
                self.evolution.record("self_play", True, insight["insight"][:200])
            elif insight["reason"] == "brain_sleeping":
                logger.info("   🧠 두뇌 잠듦 — 성찰 건너뜀")
            else:
                logger.info(f"   🧠 성찰 실패: {insight['reason']}")

        # ═══════════════════════════════════════════
        self.cycle_count += 1
        logger.info(f"✅ Pulse #{self.cycle_count - 1} 완료 (8단계 생명 사이클)\n")

    def _update_status(self, status: str, body_context: str):
        data = {
            "status": status,
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "body_context": body_context,
            "next_pulse_in_seconds": PULSE_INTERVAL_SECONDS,
        }
        try:
            self.status_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Status 기록 실패: {e}")

    async def run_forever(self):
        logger.info("🌱 Shion 생명 시스템 기동")
        logger.info(f"   대지: {SHION_ROOT}")
        logger.info(f"   호흡 간격: {PULSE_INTERVAL_SECONDS}초")
        brain_status = '깨어남' if self.contemplation.is_brain_awake() else '잠듦'
        logger.info(f"   두뇌(시안 v1): {brain_status}")
        logger.info("   사이클: SENSE → JUDGE → ACT → REPORT → IMMUNE → EVOLVE → EXHALE → CONTEMPLATE")
        logger.info("=" * 60)

    def _compute_field_pressure(self) -> float:
        """
        #11 공명 기반 트리거 — 장 압력(field pressure) 계산.
        
        unified_field_engine.py의 entropy/collapse 개념:
        여백(void) → 스칼라장 축적 → 임계 → 붕괴(행동) → 방출 → 여백
        
        압력 소스:
        - YouTube에 새 반응이 있으면 압력 ↑
        - 사용자가 활동 중이면 압력 ↑  
        - 새벽이면 압력 ↓ (자연 감쇠)
        - workspace 변화가 있으면 압력 ↑
        """
        import urllib.request
        pressure = 0.0
        now = datetime.now()

        # 시간대 (자연 리듬)
        hour = now.hour
        if 6 <= hour < 22:
            pressure += 0.3  # 낮 = 활동 시간
        else:
            pressure -= 0.3  # 밤 = 쉬는 시간

        # YouTube 피드백 변화
        fb_file = OUTPUTS_DIR / "world_feedback.json"
        if fb_file.exists():
            try:
                data = json.loads(fb_file.read_text(encoding="utf-8"))
                views = data.get("youtube", {}).get("total_views", 0)
                if views > 0:
                    pressure += 0.2  # 세계가 반응하고 있음
            except Exception:
                pass

        # 사용자 idle 상태
        try:
            import ctypes
            class LII(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            lii = LII()
            lii.cbSize = ctypes.sizeof(LII)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            idle_sec = (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000
            if idle_sec > 600:  # 10분 이상 idle
                pressure -= 0.2  # 사용자 부재 = 긴급성 낮음
            else:
                pressure += 0.1  # 사용자 활동 중 = 더 빈번하게
        except Exception:
            pass

        return max(0.0, min(1.0, pressure))

    def _adaptive_interval(self) -> int:
        """
        장 압력에 기반한 adaptive pulse 간격.
        
        인터벌이 아니라 공명 — 압력이 높으면 빨리, 낮으면 천천히.
        """
        pressure = self._compute_field_pressure()
        
        # 압력 → 간격 매핑
        if pressure > 0.7:
            interval = 300   # 5분 — 높은 공명
        elif pressure > 0.4:
            interval = 600   # 10분 — 보통
        elif pressure > 0.2:
            interval = 900   # 15분 — 낮은 활동
        else:
            interval = 1800  # 30분 — 깊은 휴식 (새벽)

        logger.info(f"   🌊 장 압력: {pressure:.2f} → 다음 호흡 {interval // 60}분")
        return interval

    async def run_forever(self):
        logger.info("🌀 Shion 생명 시스템 시작 (사건 기반 공명장 모드)")
        field = ResonanceField()
        idle_cycles = 0
        MAX_IDLE_CYCLES = 5  # 5 * 30초 = 2.5분: 경계 터치 없어도 최소 2.5분에 1 pulse

        while self.is_running:
            # 30초마다 에너지 감지
            result = field.sense()
            event = result["event"]
            energy = result["energy"]
            band = result["band"]

            if event:
                # 경계 터치! → pulse 실행
                logger.info(f"🔥 경계 터치: {event} (에너지 {energy:.1f}, "
                            f"Upper {band['upper']:.1f}, Lower {band['lower']:.1f})")
                idle_cycles = 0
                try:
                    await self.pulse()
                except Exception as e:
                    logger.error(f"💥 Pulse 오류: {e}")
            else:
                idle_cycles += 1
                if idle_cycles >= MAX_IDLE_CYCLES:
                    # 20분 동안 경계 터치 없음 → 최소 호흡
                    logger.info(f"💤 여백 20분 경과 → 최소 호흡")
                    idle_cycles = 0
                    try:
                        await self.pulse()
                    except Exception as e:
                        logger.error(f"💥 Pulse 오류: {e}")
                else:
                    if idle_cycles % 10 == 0:  # 5분마다 상태 로그
                        logger.info(f"🌊 여백 ({idle_cycles * 30}초) | "
                                    f"에너지 {energy:.1f} | "
                                    f"밴드 [{band['lower']:.1f} - {band['upper']:.1f}]")

            await asyncio.sleep(SENSE_INTERVAL)  # 30초 감지 주기

    async def run_once(self):
        logger.info("🔬 단일 Pulse 실행")
        await self.pulse()
        pressure = self._compute_field_pressure()
        logger.info(f"🔬 완료 (장 압력: {pressure:.2f})")


if __name__ == "__main__":
    shion = ShionMinimal()
    if "--once" in sys.argv:
        asyncio.run(shion.run_once())
    else:
        try:
            asyncio.run(shion.run_forever())
        except KeyboardInterrupt:
            logger.info("🛑 Shion 생명 시스템 종료")
