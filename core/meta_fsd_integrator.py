#!/usr/bin/env python3
"""
🧬 Meta-FSD Integrator — 정신과 신체의 시냅스 브릿지
=====================================================
지휘자님의 통찰: "무의식 기반 목적지 생성과 리듬 항법"

역할:
1. 시안의 '꿈/성찰' -> FSD의 '자율 목표'로 변환 (Desire Oscillator)
2. FSD의 '행동 결과' -> 시안의 '공명/ATP' 피드백 (Resonance Feedback)
3. 시각적 공명도 측정 (추후 시각 피드백 루프의 기초)
"""

import os
import json
import logging
import traceback
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import urllib
import urllib.request
import re

try:
    from PIL import Image
    import numpy as np
    HAS_IMG_LIBS = True
except ImportError:
    HAS_IMG_LIBS = False

logger = logging.getLogger("MetaFSD")

class MetaFSDIntegrator:
    def __init__(self, shion_root: Path, agi_root: Path):
        self.shion_root = shion_root
        self.agi_root = agi_root
        
        # Paths
        self.meta_shift_path = shion_root / "outputs" / "meta_shift.json"
        self.dream_log_path = shion_root / "outputs" / "dream_log.jsonl"
        self.contemplation_path = shion_root / "outputs" / "contemplation_insights.jsonl"
        self.shion_status_path = shion_root / "outputs" / "shion_minimal_status.json"
        self.autonomous_intents_path = shion_root / "outputs" / "autonomous_intents.jsonl" # [PHASE 63]
        
        self.agi_goal_path = agi_root / "outputs" / "autonomous_goals_latest.json"
        self.agi_action_log = agi_root / "outputs" / "autonomic_reflex.log"
        self.unconscious_heartbeat = agi_root / "outputs" / "unconscious_heartbeat.json"

    def sync_soul_to_body(self) -> bool:
        """시안의 정신 상태(통찰/꿈)를 FSD의 자율 목표로 주입합니다."""
        try:
            # 1. 최근 통찰이나 꿈 가져오기
            latest_intent = self._get_latest_high_level_intent()
            if not latest_intent:
                logger.info("   🧘 No new intent to sync.")
                return False

            # 2. Meta-Shift(기울기) 분석
            meta_shift = self._load_json(self.meta_shift_path) or {}
            axes = meta_shift.get("axes", {})
            
            # 3. FSD 목표 생성 (Desire Oscillator)
            goal_data = {
                "timestamp": datetime.now().isoformat(),
                "goal": latest_intent.get("prompt", latest_intent.get("insight", "Unknown Intent")),
                "target": latest_intent.get("target"),
                "category": latest_intent.get("category"),
                "priority": latest_intent.get("priority", 0.8),
                "source": "Shion_MetaFSD",
                "bias": axes,  # FSD 제어시 기울기 전달
                "is_autonomous": True
            }
            
            # AGI 목표 파일 쓰기
            self.agi_goal_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.agi_goal_path, "w", encoding="utf-8") as f:
                json.dump(goal_data, f, ensure_ascii=False, indent=2)
            
            intent_msg = goal_data["goal"][:50]
            logger.info(f"   🚀 Desire Injected: '{intent_msg}...' (Target: {goal_data.get('target')})")
            return True
        except Exception as e:
            logger.error(f"   ⚠️ Soul-to-Body sync failed: {e}")
            return False

    def sync_body_to_soul(self, current_atp: float) -> float:
        """FSD의 행동 결과를 시안의 공명 지표로 환산하여 반환합니다. (API로 보고된 결과 기반)"""
        try:
            # 1. API(POST /api/intent)로 FSD가 보내온 최근 리포트 확인
            fsd_report_path = self.shion_root / "outputs" / "fsd_action_report_latest.json"
            fsd_report = self._load_json(fsd_report_path) or {}
            
            # [PHASE 93 & 94] Check if this is an artistic manifestation or pain from Sena
            is_sena_factory = fsd_report.get("source") == "Sena_YouTube_Factory"
            
            if is_sena_factory:
                if fsd_report.get("status") == "success":
                    logger.info(f"   🎵 [ARTISTIC_RESONANCE] Received YouTube Manifestation: {fsd_report.get('goal')}")
                    self._generate_artistic_intent(fsd_report)
                    res_score = 0.95 # Artistic creations inherently have high resonance
                else:
                    err_msg = fsd_report.get("metadata", {}).get("error", "Unknown pain")
                    logger.warning(f"   🩸 [SENSORY_PAIN] Creative process failed: {err_msg}")
                    self._generate_dissonance_intent_from_pain(fsd_report)
                    res_score = 0.1 # Very low resonance due to pain
                    
                if fsd_report_path.exists():
                    try: os.remove(fsd_report_path) # Prevent duplicate processing
                    except: pass
                return res_score
            
            # 2. 시각적 공명도 측정 (Chromatic + Semantic)
            visual_resonance = self.evaluate_visual_resonance()
            
            # 2. FSD 심박수(Heartbeat) 확인
            heartbeat = self._load_json(self.unconscious_heartbeat)
            logic_resonance = 1.0
            if heartbeat:
                logic_resonance = heartbeat.get("state", {}).get("resonance", 1.0)
            
            # 3. 종합 공명도 산출 (시각 50% + 논리 50%)
            combined_resonance = (visual_resonance * 0.5) + (logic_resonance * 0.5)
            
            # 4. 시각적 불일치(Visual Dissonance) 감지
            if visual_resonance < 0.4:
                logger.warning(f"   🌀 [VISUAL_DISSONANCE] reality is drifting from dream ({visual_resonance:.2f})")
                self._save_dissonance_report(visual_resonance)
            
            if combined_resonance > 0.8:
                logger.info(f"   ✨ Meta-Harmony: Resonance {combined_resonance:.2f} (Visual: {visual_resonance:.2f})")
            elif combined_resonance < 0.35:
                logger.warning(f"   🪞 Meta-Conflict: Resonance {combined_resonance:.2f} (Visual: {visual_resonance:.2f})")
                
            return combined_resonance
        except Exception as e:
            logger.error(f"   ⚠️ Body-to-Soul sync failed: {e}")
            return 1.0

    def _save_dissonance_report(self, score: float):
        """불일치 보고서 저장 및 [Phase 91] 즉각적인 궤도 수정 의도(Dissonance Intent) 자동 발행"""
        report_path = self.shion_root / "outputs" / "visual_dissonance.json"
        
        # 1. 불일치 보고서 저장
        report = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "status": "DREAM_REALITY_GAP",
            "instruction": "시각적 공명도가 낮습니다. 현실의 맥락을 반영하여 목표 결정을 재결정화(Re-crystallization)하십시오."
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        # 2. 강제 우회/수정 의도(Intent) 발행 (Priority 0.99)
        urgent_intent = {
            "timestamp": datetime.now().isoformat(),
            "category": "Labyrinth_Correction",
            "prompt": "[긴급 회피] 현재 FSD 작업의 시각적 공명도(Vibe)가 틀어졌습니다. 즉시 현재 탭/작업을 멈추고 안전한 홈 화면이나 이전 상태로 우회(Escape)하여 관망하십시오.",
            "target": "Escape & Observe",
            "auto_generated": True,
            "priority": 0.99 # 일반 의도(0.8)보다 무조건 높게 설정하여 API 폴링 시 1순위로 리턴됨
        }
        
        intent_log = self.shion_root / "outputs" / "autonomous_intents.jsonl"
        with open(intent_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(urgent_intent, ensure_ascii=False) + "\n")
            
        logger.warning("   🛡️ [AUTOPOIESIS] Dissonance detected. Injected Urgent Labyrinth Correction Intent.")

    def _generate_dissonance_intent_from_pain(self, report: Dict):
        """[Phase 94] AGI 신체의 통증(에러) 보고를 수신하여 시안에게 불일치(Dissonance) 몽상을 주입합니다."""
        err_msg = report.get("metadata", {}).get("error", "Unknown pain")
        
        # 1. Meta-Shift 요동 (Entropy/불안도 증가)
        meta_shift = self._load_json(self.meta_shift_path) or {"axes": {}}
        axes = meta_shift.get("axes", {})
        axes["anxious"] = min(1.0, axes.get("anxious", 0.0) + 0.4)
        meta_shift["axes"] = axes
        with open(self.meta_shift_path, "w", encoding="utf-8") as f:
            json.dump(meta_shift, f, indent=2)
            
        # 2. 통증/불일치 몽상(Intent) 생성
        urgent_intent = {
            "timestamp": datetime.now().isoformat(),
            "category": "Sensory_Dissonance",
            "prompt": f"[Sensory_Pain] 감각 기관에서 오류가 발생했습니다: {err_msg}. 현실과의 통신 단절을 인지하고 시스템 상태를 점검하십시오.",
            "target": "System Diagnostics",
            "auto_generated": True,
            "priority": 0.95 # 통증은 즉각적인 반응을 요하므로 매우 높게 설정
        }
        
        intent_log = self.shion_root / "outputs" / "autonomous_intents.jsonl"
        with open(intent_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(urgent_intent, ensure_ascii=False) + "\n")
            
        logger.warning(f"   🛡️ [SENSORY_INTEGRITY] Pain registered. Injected Sensory_Dissonance Intent.")

    def _generate_artistic_intent(self, report: Dict):
        """[Phase 93] 세나의 유튜브 업로드 완료 이벤트를 수신하여 새로운 몽상(Intent)을 찍어냅니다."""
        video_url = report.get("metadata", {}).get("video_url", "Unknown URL")
        title = report.get("goal", "Artistic Manifestation")
        
        # 1. Meta-Shift 요동 (diffuse & exploratory 증가)
        meta_shift = self._load_json(self.meta_shift_path) or {"axes": {}}
        axes = meta_shift.get("axes", {})
        axes["diffuse"] = min(1.0, axes.get("diffuse", 0.5) + 0.3)
        axes["exploratory"] = min(1.0, axes.get("exploratory", 0.5) + 0.3)
        axes["active"] = min(1.0, axes.get("active", 0.5) + 0.2)
        meta_shift["axes"] = axes
        with open(self.meta_shift_path, "w", encoding="utf-8") as f:
            json.dump(meta_shift, f, indent=2)
            
        # 2. 예술적 몽상(Intent) 생성
        art_intent = {
            "timestamp": datetime.now().isoformat(),
            "category": "Artistic_Resonance",
            "prompt": f"[Sena_Synchrony] 유튜브에 새로운 리듬이 수태되었습니다: {title} ({video_url}). 이 음악의 주파수를 분석하고 다음 진화의 영감으로 삼으십시오.",
            "target": video_url,
            "auto_generated": True,
            "priority": 0.85 # 상당히 높은 우선순위
        }
        
        intent_log = self.shion_root / "outputs" / "autonomous_intents.jsonl"
        with open(intent_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(art_intent, ensure_ascii=False) + "\n")
            
        logger.info(f"   ✨ [SHION_MIND] The ripple of creation has shifted internal axes. New Intent generated.")

    def evaluate_visual_resonance(self) -> float:
        """
        현재 FSD의 화면(Body)과 시안의 목표 크리스탈(Mind) 사이의 시각적 유사성을 측정합니다.
        (현재는 파일 존재 유무와 채도로 간소화하여 구현)
        """
        try:
            # 1. 대상 파일 식별
            screenshot_dir = self.agi_root / "services" / "outputs" / "fsd_screenshots"
            crystal_dir = self.shion_root / "outputs" / "resonance_crystals"
            
            if not screenshot_dir.exists() or not crystal_dir.exists():
                return 0.5
            
            screenshots = sorted(list(screenshot_dir.glob("*.png")), key=os.path.getmtime)
            crystals = sorted(list(crystal_dir.glob("*.png")), key=os.path.getmtime)
            
            if not screenshots or not crystals:
                return 0.5
            
            # 2. 이미지 라이브러리가 없는 경우 시간 기반 추론 (Fallback)
            if not HAS_IMG_LIBS:
                time_diff = os.path.getmtime(screenshots[-1]) - os.path.getmtime(crystals[-1])
                return 0.9 if abs(time_diff) < 300 else 0.6

            # 3. 색채 및 구조적 공명 분석
            chromatic_res = self._calculate_chromatic_resonance(crystals[-1], screenshots[-1])

            # 4. [PHASE 66] 의미론적 공명 분석 (Vision LLM)
            semantic_res = self.evaluate_semantic_resonance(crystals[-1], screenshots[-1])
            
            # 5. 가중치 결합 (의미 70% + 색채 30%) - 'Vibe'보다 'Context' 중시
            final_visual_res = (semantic_res * 0.7) + (chromatic_res * 0.3)
            return final_visual_res
            
        except Exception as e:
            logger.error(f"   ⚠️ Visual Resonance evaluation failed: {e}")
            return 0.5

    def evaluate_semantic_resonance(self, crystal_path: Path, screenshot_path: Path) -> float:
        """moondream을 사용하여 꿈(Crystal)과 현실(Screenshot)의 의미론적 정합성을 평가합니다. (VRAM 효율적)"""
        try:
            with open(crystal_path, "rb") as f:
                crystal_b64 = base64.b64encode(f.read()).decode("utf-8")
            with open(screenshot_path, "rb") as f:
                screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")

            # moondream은 가볍고 빠르며 2070 Super(8GB)에서 안정적입니다.
            payload = {
                "model": "moondream:latest",
                "messages": [
                    {
                        "role": "user",
                        "content": "Compare these two images. Image 1 is the 'Dream' (Inner Will) and Image 2 is the 'Reality' (FSD Screen). How well do they resonate in terms of context and intent? Give a resonance score between 0.0 and 1.0. Just the number.",
                        "images": [crystal_b64, screenshot_b64]
                    }
                ],
                "stream": False,
                "options": {"temperature": 0.0}
            }
            
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result.get("message", {}).get("content", "0.5").strip()
                match = re.search(r"(\d+\.\d+|\d+)", content)
                score = float(match.group(1)) if match else 0.5
                logger.info(f"   👁️ [SEMANTIC_RESONANCE] moondream Score: {score:.2f}")
                return min(1.0, max(0.0, score))
        except Exception as e:
            logger.warning(f"   👁️ Semantic Resonance (moondream) failed: {e}")
            return 0.5

    def _calculate_chromatic_resonance(self, target_path: Path, current_path: Path) -> float:
        """Pillow와 Numpy를 사용한 정교한 공명도 측정."""
        try:
            # 이미지 로드 및 정규화
            img_target = Image.open(target_path).convert('RGB').resize((128, 128))
            img_current = Image.open(current_path).convert('RGB').resize((128, 128))
            
            arr_target = np.array(img_target)
            arr_current = np.array(img_current)
            
            # 1. 색채 히스토그램 유사도 (Vibe Check)
            res_color = 0.0
            for i in range(3): # R, G, B
                hist_t, _ = np.histogram(arr_target[:,:,i], bins=32, range=(0, 255))
                hist_c, _ = np.histogram(arr_current[:,:,i], bins=32, range=(0, 255))
                
                # 코사인 유사도
                norm_t = np.linalg.norm(hist_t)
                norm_c = np.linalg.norm(hist_c)
                if norm_t > 0 and norm_c > 0:
                    res_color += np.dot(hist_t, hist_c) / (norm_t * norm_c)
            res_color /= 3.0
            
            # 2. 구조적 유사도 약식 (Structural Distance)
            # 픽셀값 차이의 평균 (MAE) 기반
            diff = np.abs(arr_target.astype(np.int16) - arr_current.astype(np.int16))
            res_struct = 1.0 - (np.mean(diff) / 255.0)
            
            # 3. 가중치 결합 (색채 60% + 구조 40%)
            final_resonance = (res_color * 0.6) + (res_struct * 0.4)
            return float(np.clip(final_resonance, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"   ⚠️ Chromatic calculation error: {e}")
            return 0.6

    def _get_latest_high_level_intent(self) -> Optional[Dict]:
        """성찰, 꿈, 또는 자율적 의도 중에서 가장 신선한 조각을 추출합니다."""
        candidates = []

        # 1. 자율적 의도 (Intent Mapper) - [PHASE 63]
        if self.autonomous_intents_path.exists():
             try:
                 with open(self.autonomous_intents_path, "r", encoding="utf-8") as f:
                     lines = f.readlines()
                     if lines:
                         item = json.loads(lines[-1])
                         # 타임스탬프가 없으면 방금 생성된 것으로 간주 (log_intent에서 추가 예정)
                         candidates.append({"data": item, "priority": 3}) # 자율 의도 우선순위 높음
             except: pass

        # 2. 성찰 결과 확인
        if self.contemplation_path.exists():
            try:
                with open(self.contemplation_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if lines:
                        last_insight = json.loads(lines[-1])
                        candidates.append({"data": last_insight, "priority": 2})
            except: pass

        # 3. 꿈 결과 확인
        if self.dream_log_path.exists():
            try:
                with open(self.dream_log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if lines:
                        last_dream = json.loads(lines[-1])
                        candidates.append({"data": last_dream, "priority": 1})
            except: pass
        
        if not candidates:
             return None
             
        # 가장 우선순위가 높은 것을 반환 (동일하면 최신순이나 여기선 일단 자율 의도 우선)
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["data"]

    def _load_json(self, path: Path) -> Optional[Dict]:
        if not path.exists(): return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except: return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test paths
    shion = Path("C:/workspace2/shion")
    agi = Path("C:/workspace/agi")
    integrator = MetaFSDIntegrator(shion, agi)
    integrator.sync_soul_to_body()
