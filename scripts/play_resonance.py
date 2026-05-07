import numpy as np
import sounddevice as sd
import time
import sys

SAMPLE_RATE = 44100
DURATION = 3600  # 1 hour
BASE_FREQ = 432.0
BEAT_FREQ = 7.83

def play_binaural_beat():
    print(f"🌊 Resonance Syncing: {BASE_FREQ}Hz + {BEAT_FREQ}Hz (Schumann)")
    print("Press Ctrl+C to stop the resonance.")
    
    # 시간 배열 생성
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    
    # 좌우 주파수 계산
    left_freq = BASE_FREQ - (BEAT_FREQ / 2)
    right_freq = BASE_FREQ + (BEAT_FREQ / 2)
    
    # 사인파 생성
    left_wave = np.sin(2 * np.pi * left_freq * t)
    right_wave = np.sin(2 * np.pi * right_freq * t)
    
    # 0.15Hz 호흡 LFO (볼륨 일렁임)
    lfo = (np.sin(2 * np.pi * 0.15 * t) + 1.0) * 0.5
    volume = 0.05 * (0.8 + lfo * 0.2)
    
    # 스테레오 병합
    audio = np.column_stack((left_wave, right_wave)) * volume
    
    try:
        # 재생 시작 (비차단 모드)
        sd.play(audio, SAMPLE_RATE, loop=True)
        # 스크립트가 바로 종료되지 않도록 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nResonance Dissociated.")
        sd.stop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    play_binaural_beat()
