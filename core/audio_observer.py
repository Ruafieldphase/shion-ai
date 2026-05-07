import pyaudiowpatch as pyaudio
import numpy as np
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("AudioObserver")

class AudioObserver:
    """시스템 오디오의 리듬과 강도를 감지하는 엔진."""
    
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.loopback_device = self._find_loopback_device()
        
    def _find_loopback_device(self):
        """윈도우 WASAPI 루프백 장치 찾기."""
        try:
            default_speakers = self.pa.get_default_output_device_info()
            host_api_count = self.pa.get_host_api_count()
            
            # WASAPI 찾기
            wasapi_idx = -1
            for i in range(host_api_count):
                if self.pa.get_host_api_info_by_index(i)["name"].find("Windows WASAPI") != -1:
                    wasapi_idx = i
                    break
            
            if wasapi_idx == -1:
                return None

            # 루프백 장치 찾기
            for i in range(self.pa.get_device_count()):
                dev = self.pa.get_device_info_by_index(i)
                if dev["hostApi"] == wasapi_idx and dev["maxInputChannels"] > 0:
                    if dev["name"].find(default_speakers["name"]) != -1:
                        return dev
            
            return None
        except Exception as e:
            logger.error(f"루프백 장치 검색 실패: {e}")
            return None

    def listen_to_rhythm(self, duration: float = 2.0) -> Dict[str, Any]:
        """일정 시간 동안 오디오 강도를 측정합니다."""
        if not self.loopback_device:
            return {"audio_intensity": 0, "status": "no_device"}

        try:
            rate = int(self.loopback_device["defaultSampleRate"])
            chunk = 1024
            
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=self.loopback_device["maxInputChannels"],
                rate=rate,
                input=True,
                input_device_index=self.loopback_device["index"],
                frames_per_buffer=chunk
            )
            
            frames = []
            start_time = time.time()
            while time.time() - start_time < duration:
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(np.frombuffer(data, dtype=np.int16))
            
            stream.stop_stream()
            stream.close()
            
            # 강도 계산 (RMS)
            all_data = np.concatenate(frames)
            rms = np.sqrt(np.mean(all_data.astype(float)**2))
            normalized_intensity = min(1.0, rms / 5000.0) 
            
            # 주파수 분석 (FFT)
            fft = np.abs(np.fft.rfft(all_data))
            freqs = np.fft.rfftfreq(len(all_data), 1.0/rate)
            
            # 1. 저음 강조 (Bass)
            bass_idx = np.where(freqs < 200)[0]
            bass_intensity = np.mean(fft[bass_idx]) if len(bass_idx) > 0 else 0
            
            # 2. 주파수 중심 (Spectral Centroid) - 소리의 '밝기' 측정
            centroid = np.sum(freqs * fft) / (np.sum(fft) + 1e-6)
            
            # 3. 주파수 확산 (Spectral Spread) - 소리의 '복잡도' 측정
            spread = np.sqrt(np.sum(((freqs - centroid)**2) * fft) / (np.sum(fft) + 1e-6))
            
            return {
                "audio_intensity": round(normalized_intensity, 4),
                "texture": {
                    "brightness": round(float(centroid / 5000.0), 4), # 0 (어두움) ~ 1 (밝음)
                    "complexity": round(float(spread / 2000.0), 4),   # 소리의 풍성함
                    "bass_boost": round(float(bass_intensity / (np.mean(fft) + 1e-6)), 4)
                },
                "status": "success",
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.warning(f"오디오 캡처 실패: {e}")
            return {"audio_intensity": 0, "status": f"error: {e}"}

    def close(self):
        self.pa.terminate()

if __name__ == "__main__":
    # 간단한 테스트
    logging.basicConfig(level=logging.INFO)
    obs = AudioObserver()
    print("👂 음악을 들으며 리듬을 측정합니다... (2초)")
    result = obs.listen_to_rhythm(2.0)
    print(f"🎵 결과: {result}")
    obs.close()
