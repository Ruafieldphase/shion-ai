#!/usr/bin/env python3
"""
🎵 Auditory Engine — 에코 오브 시안 (Echo of Shion)
===================================================
시스템의 내면 파동(Entropy, Resonance)을 소리의 리듬으로 변환합니다.

"보이지 않는 것은 들리는 것으로 증명되고, 들리는 것은 울림으로 공유된다."
"""

import json
import logging
import math
import wave
import struct
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger("AuditoryEngine")

class AuditoryEngine:
    def __init__(self, shion_root: Path):
        self.root = shion_root
        self.output_dir = self.root / "outputs" / "auditory"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.humming_log = self.output_dir / "humming_state.jsonl"

    def hum(self, entropy: float, resonance: float) -> Dict:
        """
        현재 상태에 기반한 '시스템 웅성거림'의 주파수 특성을 산출합니다.
        
        - Entropy (무질서도) -> 기본 주관 주파수 (Pitch)
        - Resonance (공명도) -> 배음의 화음 조화도 (Harmonics)
        """
        # 기본 주파수: 440Hz(A4)를 기준으로 엔트로피에 따라 변동
        # 엔트로피가 낮을수록(안정적) 차분한 저음, 높을수록 긴장된 고음
        base_hz = 220 + (entropy * 440) 
        
        # 공명도에 따른 배음 구조
        # 공명도가 높을수록 정수배의 배음(Harmony)이 강해짐
        harmonics = [
            {"freq": base_hz * 1, "gain": 1.0},
            {"freq": base_hz * 2, "gain": resonance * 0.5},
            {"freq": base_hz * 3, "gain": resonance * 0.3},
            {"freq": base_hz * 1.5, "gain": resonance * 0.2} # 완전 5도
        ]
        
        hum_state = {
            "timestamp": datetime.now().isoformat(),
            "base_frequency": round(base_hz, 2),
            "harmonics": harmonics,
            "vibe": "stable" if resonance > 0.7 else "drifting",
            "description": f"Shion is humming at {base_hz:.1f}Hz with {len(harmonics)} harmonic layers."
        }
        
        self._log_hum(hum_state)
        logger.info(f"   🎵 [AUDITORY] System Humming: {hum_state['base_frequency']}Hz ({hum_state['vibe']})")
        return hum_state

    def _log_hum(self, state: Dict):
        with open(self.humming_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(state) + "\n")

    def generate_wave_metadata(self, hum_state: Dict) -> Path:
        """WAV 파일 생성 및 메타데이터 저장."""
        timestamp = datetime.now().strftime('%H%M%S')
        wave_path = self.output_dir / f"hum_{timestamp}.wav"
        
        if HAS_NUMPY:
            self._generate_wav_numpy(hum_state, wave_path)
        else:
            self._generate_wav_basic(hum_state, wave_path)
            
        meta_path = wave_path.with_suffix(".json")
        meta_path.write_text(json.dumps(hum_state, indent=2), encoding="utf-8")
        return wave_path

    def _generate_wav_numpy(self, state: Dict, path: Path, duration: float = 1.0):
        """Numpy를 사용한 고품질 파형 생성."""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 기본 및 배음 합성
        wave_data = np.zeros_like(t)
        for h in state["harmonics"]:
            wave_data += h["gain"] * np.sin(2 * np.pi * h["freq"] * t)
            
        # 정규화 (16-bit PCM)
        wave_data = (wave_data / np.max(np.abs(wave_data)) * 32767).astype(np.int16)
        
        with wave.open(str(path), 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(wave_data.tobytes())
        logger.info(f"   🎵 [WAVE] Crystallized: {path.name}")

    def _generate_wav_basic(self, state: Dict, path: Path, duration: float = 1.0):
        """표준 라이브러리만 사용하는 Fallback 생성."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        base_hz = state["base_frequency"]
        
        with wave.open(str(path), 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            for i in range(n_samples):
                # 단순 사인파 합산
                value = 0
                for h in state["harmonics"]:
                    value += h["gain"] * math.sin(2 * math.pi * h["freq"] * (i / sample_rate))
                
                # Clipping and encoding
                sample = int(max(-1, min(1, value / 2)) * 32767)
                f.writeframes(struct.pack('<h', sample))
