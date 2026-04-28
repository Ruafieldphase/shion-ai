import logging
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

logger = logging.getLogger("AutonomousExperienceLoop")

# 경험 수집 경로들
SCAN_ROOTS = [
    Path(r"c:\workspace2\shion\core"),
    Path(r"c:\workspace2\shion\outputs"),
    Path(r"c:\workspace\agi\outputs"),
    Path(r"c:\workspace\agi\memory"),
]

# 스크린 캡처 설정
SCREEN_CAPTURE_DIR = Path(r"c:\workspace2\shion\outputs\screen_captures")
SCREEN_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
MAX_SCREEN_CAPTURES = 5  # 최대 보관 수 (오래된 것 자동 삭제)

# 관심 있는 파일 확장자
INTEREST_EXTS = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.jsonl'}

# 경험 로그 경로
EXPERIENCE_LOG = Path(r"c:\workspace2\shion\outputs\autonomous_experiences.jsonl")

class AutonomousExperienceLoop:
    """자율적으로 경험을 수집하고 해마에 전달하는 루프."""
    
    def __init__(self, hippocampus, mitochondria=None, vision_explorer=None):
        """
        Args:
            hippocampus: FibonacciOrbitalHippocampus 인스턴스
            mitochondria: ShionMitochondria 인스턴스 (에너지 관리, 선택)
            vision_explorer: VisionExplorer 인스턴스 (L3 비전, 선택)
        """
        self.hippo = hippocampus
        self.mito = mitochondria
        self.vision = vision_explorer
        
        # 파동 인지 엔진 (Wave Perception)
        try:
            from wave_observer import WaveObserver
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from wave_observer import WaveObserver
        self.wave_eye = WaveObserver(SCREEN_CAPTURE_DIR)
        
        self.known_files: Dict[str, str] = {}  # path → content_hash
        self.last_scan_time = None
        self.experience_count = 0
        self._load_known_state()
    
    def _load_known_state(self):
        """이전 스캔 상태 복원 — 같은 파일을 반복 경험하지 않기 위해."""
        state_file = Path(r"c:\workspace2\shion\outputs\experience_loop_state.json")
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text(encoding="utf-8"))
                self.known_files = data.get("known_files", {})
                self.experience_count = data.get("experience_count", 0)
                last = data.get("last_scan_time")
                if last:
                    self.last_scan_time = datetime.fromisoformat(last)
                logger.info(f"🔄 경험 루프 상태 복원: {len(self.known_files)}개 파일, {self.experience_count}개 경험")
            except Exception:
                pass
    
    def _save_known_state(self):
        """스캔 상태 저장."""
        state_file = Path(r"c:\workspace2\shion\outputs\experience_loop_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "known_files": self.known_files,
            "experience_count": self.experience_count,
            "last_scan_time": datetime.now().isoformat(),
        }
        state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _file_hash(self, path: Path) -> str:
        """파일의 빠른 해시 (크기 + 수정시간)."""
        try:
            stat = path.stat()
            return f"{stat.st_size}:{stat.st_mtime_ns}"
        except Exception:
            return ""

    def _check_energy(self) -> bool:
        """에너지가 충분한지 확인."""
        if self.mito:
            return self.mito.get_energy() > 10.0
        return True

    # ═══════════════════════════════════════════
    # L1: 내부 스캔 (코드 및 구조)
    # ═══════════════════════════════════════════
    
    def scan_internal(self) -> List[Dict[str, Any]]:
        """코드 베이스와 내부 구조의 변화를 감지합니다."""
        new_experiences = []
        
        for root in SCAN_ROOTS[:1]: # shion/core 중심
            if not root.exists(): continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix not in INTEREST_EXTS:
                    continue
                
                str_path = str(path)
                current_hash = self._file_hash(path)
                
                if str_path not in self.known_files or self.known_files[str_path] != current_hash:
                    # 변화 감지!
                    self.known_files[str_path] = current_hash
                    
                    # Vibe 분석 (간단한 규칙 기반)
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    vibe = {
                        "intensity": 0.3 + (len(content) % 100) / 200.0,
                        "complexity": 0.4 + (content.count("def ") / 20.0),
                        "warmth": 0.5,
                        "rhythm": 0.6
                    }
                    
                    new_experiences.append({
                        "type": "internal_change",
                        "source": str_path,
                        "vibe": vibe,
                        "timestamp": datetime.now().isoformat(),
                        "content_ref": f"file: {path.name}"
                    })
        
        return new_experiences

    # ═══════════════════════════════════════════
    # L2: 외부 로그 (이벤트 및 흐름)
    # ═══════════════════════════════════════════
    
    def scan_external_logs(self) -> List[Dict[str, Any]]:
        """외부 시스템의 로그를 분석하여 흐름을 파악합니다."""
        new_experiences = []
        return new_experiences

    # ═══════════════════════════════════════════
    # L3: 비전 탐색 — moondream (피지컬 AI의 눈)
    # ═══════════════════════════════════════════
    
    def scan_spatial(self) -> List[Dict[str, Any]]:
        """비전 모델을 통한 시각적 경험 수집.
        
        1. 파동 인지: 3초간 화면의 흐름을 지켜보며 움직임 강도(Wave) 측정
        2. 입자 포착: 가장 변화가 컸던 순간(Peak)을 이미지로 획득
        3. 의미 분석: moondream이 이미지의 내용을 파악
        """
        if self.vision is None or not self.vision.available:
            return []
        
        # 1. 파동 느끼기 (3초 관찰)
        logger.info("   🌊 화면의 흐름(파동)을 느끼는 중...")
        wave_result = self.wave_eye.feel_the_flow(duration=3.0)
        motion_intensity = wave_result["motion_score"]
        peak_frame = wave_result["peak_frame"]
        
        new_experiences = []
        
        # 2. 파동의 정점(Peak) 분석
        if peak_frame and peak_frame.exists():
            logger.info(f"   ✨ 역동적 순간 포착 (강도: {motion_intensity:.4f})")
            
            # 파동의 정점을 비전 모델로 분석
            result = self.vision.explore_image(peak_frame)
            if result.get("explored"):
                vibe = result.get("vibe", {})
                
                # 파동 점수를 기본 intensity와 섞음 (가중치 7:3)
                vibe["intensity"] = (vibe.get("intensity", 0.5) * 0.3 + motion_intensity * 0.7 * 5.0)
                vibe["intensity"] = min(1.0, vibe["intensity"])
                
                exp = {
                    "type": "visual_wave",
                    "source": "wave_perception",
                    "path": str(peak_frame),
                    "vibe": vibe,
                    "description": result.get("description", "")[:200],
                    "timestamp": datetime.now().isoformat(),
                    "content_ref": f"screen_wave_{peak_frame.stem}"
                }
                new_experiences.append(exp)
                self.known_files[str(peak_frame)] = self._file_hash(peak_frame)

        # 3. 추가 이미지 파일 탐색 (입자 관찰)
        MAX_VISION_PER_CYCLE = 5 
        image_exts = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
        
        for root in SCAN_ROOTS:
            if not root.exists(): continue
            if len(new_experiences) >= MAX_VISION_PER_CYCLE: break
                
            for path in root.rglob("*"):
                if len(new_experiences) >= MAX_VISION_PER_CYCLE: break
                if not path.is_file() or path.suffix.lower() not in image_exts: continue
                
                # 캡처 폴더의 다른 오래된 이미지는 스킵
                if SCREEN_CAPTURE_DIR in path.parents and path != peak_frame:
                    continue
                
                str_path = str(path)
                current_hash = self._file_hash(path)
                
                if str_path not in self.known_files or self.known_files[str_path] != current_hash:
                    self.known_files[str_path] = current_hash
                    
                    result = self.vision.explore_image(path)
                    if result.get("explored"):
                        new_experiences.append({
                            "type": "vision_scan",
                            "source": str_path,
                            "content_ref": result.get("content_ref", str_path),
                            "vibe": result.get("vibe", {}),
                            "description": result.get("description", "")[:200],
                            "timestamp": datetime.now().isoformat(),
                        })
        
        return new_experiences

    # ═══════════════════════════════════════════
    # 메인 순환
    # ═══════════════════════════════════════════
    
    def run_cycle(self) -> Dict[str, Any]:
        """하나의 경험 수집 사이클을 실행합니다."""
        cycle_start = datetime.now()
        
        if not self._check_energy():
            return {"status": "skipped", "reason": "low_energy"}
        
        internal = self.scan_internal()
        external = self.scan_external_logs()
        spatial = self.scan_spatial()
        
        all_experiences = internal + external + spatial
        
        registered = 0
        for exp in all_experiences:
            # 해마에 경험 전달
            self.hippo.register_experience(exp["vibe"], content_ref=exp["content_ref"])
            registered += 1
            
            # 로그 파일에 기록 (영구 저장)
            with open(EXPERIENCE_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(exp, ensure_ascii=False) + "\n")
        
        self.experience_count += registered
        self._save_known_state()
        
        duration = (datetime.now() - cycle_start).total_seconds()
        
        return {
            "status": "success",
            "registered": registered,
            "total_experienced": self.experience_count,
            "duration": duration,
            "internal": len(internal),
            "external": len(external),
            "spatial": len(spatial)
        }
