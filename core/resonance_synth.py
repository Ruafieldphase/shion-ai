import json
import time
import numpy as np
import sounddevice as sd
from pathlib import Path
import threading

RHYTHM_FILE = Path(r"c:\workspace2\shion\outputs\rhythm_signature.json")
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024

class ResonanceSynth:
    def __init__(self):
        self.phase = 0.0
        self.lfo_phase = 0.0
        
        # 기본 소리 설정 (우주적 앰비언트 느낌)
        self.base_freq = 108.0 # Om frequency (108 Hz)
        self.target_volume = 0.05
        self.current_volume = 0.05
        self.target_mod_index = 1.0
        self.current_mod_index = 1.0
        
        # 장(Field) 조율을 위한 바이노럴 비트 (뇌파 동조)
        self.entrainment_freq = 4.0 # 기본 Theta파 (명상/안정)
        self.current_entrainment = 4.0
        
        # 인지적 속도 (LFO 진동 속도)
        self.target_lfo_freq = 0.1
        self.current_lfo_freq = 0.1
        
        # 표류(Drift)를 위한 변수들 (사상의학 4차원 축)
        self.drift_tension = 0.0 # Field_Tension
        self.drift_direction = 0.5 # Energy_Direction (공간감)
        self.drift_heat = 0.5 # Vibe_Heat (배음/온도)
        
        # 공간감(Delay)을 위한 원형 버퍼 (최대 1.5초 딜레이)
        self.delay_time = 0.75 # 0.75초 에코
        self.delay_frames = int(self.delay_time * SAMPLE_RATE)
        self.delay_buffer = np.zeros((self.delay_frames, 2))
        self.delay_ptr = 0
        self.target_delay_mix = 0.0 # 0.0(발산/가까움) ~ 0.5(수렴/깊은 동굴)
        self.current_delay_mix = 0.0
        
        self.running = False
        
    def get_range_val(self, val, default=0.0):
        """단일 값이면 범위를 만들어주고, 리스트면 최소/최대값으로 반환합니다."""
        if isinstance(val, list) and len(val) >= 2:
            return float(val[0]), float(val[1])
        else:
            v = float(val) if val is not None else default
            return max(0.0, v - 0.1), min(1.0, v + 0.1) # 기본 ±10% 대역폭 생성
        
    def read_rhythm_data(self):
        """rhythm_signature.json 파일을 주기적으로 읽어 사운드 파라미터를 조절합니다."""
        while self.running:
            try:
                if RHYTHM_FILE.exists():
                    with open(RHYTHM_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        # field_tension을 대역폭으로 매핑 (부드러운 볼륨)
                        raw_tension = data.get("field_tension", data.get("Field_Tension", 0.0))
                        min_t, max_t = self.get_range_val(raw_tension)
                        
                        # 표류(Drift) 계산: 랜덤하게 대역폭 안을 유영함
                        self.drift_tension += (np.random.rand() - 0.5) * 0.02
                        self.drift_tension = np.clip(self.drift_tension, min_t, max_t)
                        
                        self.target_volume = 0.02 + min(self.drift_tension * 0.5, 0.13)
                        
                        # 긴장도가 높으면 치유(Theta 4Hz), 낮으면 집중(Alpha 10Hz)으로 장을 이끎
                        if self.drift_tension > 0.15:
                            self.entrainment_freq = 4.0 # 진정 (Theta)
                        else:
                            self.entrainment_freq = 10.0 # 각성/흐름 (Alpha)
                        
                        # 2. Vibe_Heat (파동의 온도 - 소양/소음) -> 음색의 밝기
                        raw_heat = data.get("Vibe_Heat", 0.5)
                        min_h, max_h = self.get_range_val(raw_heat)
                        self.drift_heat += (np.random.rand() - 0.5) * 0.05
                        self.drift_heat = np.clip(self.drift_heat, min_h, max_h)
                        self.target_mod_index = 1.0 + (self.drift_heat * 8.0) # 온도가 높을수록 배음이 거칠어짐
                        
                        # 3. Energy_Direction (기운의 방향 - 태양/태음) -> 공간감
                        raw_dir = data.get("Energy_Direction", 0.5)
                        min_d, max_d = self.get_range_val(raw_dir)
                        self.drift_direction += (np.random.rand() - 0.5) * 0.05
                        self.drift_direction = np.clip(self.drift_direction, min_d, max_d)
                        # 수렴(0.0)할수록 잔향이 깊어짐, 발산(1.0)할수록 소리가 드라이하고 뚜렷해짐
                        self.target_delay_mix = (1.0 - self.drift_direction) * 0.6 
                        
                        # 4. Cognitive_Pace (인지적 속도) -> 소리의 호흡(LFO 속도)
                        raw_pace = data.get("Cognitive_Pace", 0.5)
                        min_p, max_p = self.get_range_val(raw_pace)
                        pace = np.random.uniform(min_p, max_p) # 매 순간 대역폭 내에서 미세한 호흡 변화
                        self.target_lfo_freq = 0.05 + (pace * 0.5) # 0.05Hz(느림) ~ 0.55Hz(빠름)
                        
            except Exception as e:
                pass # 파일 읽기 실패 시 무시하고 계속 진행
            
            time.sleep(0.5)
            
    def audio_callback(self, outdata, frames, time_info, status):
        """실시간 오디오 버퍼를 채우는 콜백 함수"""
        if status:
            print(status)
            
        t = (np.arange(frames) + self.phase) / SAMPLE_RATE
        
        # 부드러운 파라미터 보간 (글라이드 효과)
        self.current_volume += (self.target_volume - self.current_volume) * 0.005
        self.current_mod_index += (self.target_mod_index - self.current_mod_index) * 0.005
        self.current_entrainment += (self.entrainment_freq - self.current_entrainment) * 0.001
        self.current_lfo_freq += (self.target_lfo_freq - self.current_lfo_freq) * 0.005
        self.current_delay_mix += (self.target_delay_mix - self.current_delay_mix) * 0.005
        
        # FM 합성 (주파수 변조)
        mod_freq = self.base_freq * 0.5 # 옥타브 아래
        modulator = np.sin(2 * np.pi * mod_freq * t) * self.current_mod_index
        
        # 바이노럴 비트 (좌우 주파수를 다르게 하여 뇌파 동조 유도)
        left_carrier = np.sin(2 * np.pi * (self.base_freq - self.current_entrainment/2) * t + modulator)
        right_carrier = np.sin(2 * np.pi * (self.base_freq + self.current_entrainment/2) * t + modulator)
        
        # LFO (저주파 진동 - 소리에 숨결을 불어넣음)
        lfo_t = (np.arange(frames) + self.lfo_phase) / SAMPLE_RATE
        lfo = (np.sin(2 * np.pi * self.current_lfo_freq * lfo_t) + 1.0) * 0.5 # 0 ~ 1
        
        # 기본 믹싱 (좌우 독립적 출력)
        wave_left = left_carrier * self.current_volume * (0.5 + lfo * 0.5)
        wave_right = right_carrier * self.current_volume * (0.5 + lfo * 0.5)
        dry_signal = np.column_stack((wave_left, wave_right))
        
        # 공간감 (Delay / Echo) 처리
        wet_signal = np.zeros_like(dry_signal)
        
        # Circular buffer read/write (블록 크기가 버퍼 경계를 넘지 않는다고 가정, 버퍼를 넉넉하게 잡음)
        if self.delay_ptr + frames <= self.delay_frames:
            delayed = self.delay_buffer[self.delay_ptr:self.delay_ptr+frames]
            wet_signal[:] = delayed
            # 피드백 0.3을 주어 여러 번 울리게 함
            self.delay_buffer[self.delay_ptr:self.delay_ptr+frames] = dry_signal + delayed * 0.3
            self.delay_ptr = (self.delay_ptr + frames) % self.delay_frames
        else:
            # 경계를 넘을 경우의 단순 처리 (글리치 방지)
            part1 = self.delay_frames - self.delay_ptr
            part2 = frames - part1
            delayed1 = self.delay_buffer[self.delay_ptr:]
            delayed2 = self.delay_buffer[:part2]
            wet_signal[:part1] = delayed1
            wet_signal[part1:] = delayed2
            
            self.delay_buffer[self.delay_ptr:] = dry_signal[:part1] + delayed1 * 0.3
            self.delay_buffer[:part2] = dry_signal[part1:] + delayed2 * 0.3
            self.delay_ptr = part2
            
        # 최종 사운드 믹스 (Dry + Wet)
        final_signal = dry_signal * (1.0 - self.current_delay_mix) + wet_signal * self.current_delay_mix
        
        # 2채널(스테레오)로 출력 복사
        outdata[:] = final_signal
        
        self.phase += frames
        self.lfo_phase += frames

    def start(self):
        """신시사이저를 시작합니다."""
        self.running = True
        
        # 데이터 감시 스레드 시작
        threading.Thread(target=self.read_rhythm_data, daemon=True).start()
        
        print("🌊 Resonance Synth started...")
        print(f"Base Frequency: {self.base_freq}Hz")
        print("Reading rhythm_signature.json for live modulation.")
        print("Press Ctrl+C to stop.")
        
        # 오디오 스트림 시작
        try:
            with sd.OutputStream(channels=2, callback=self.audio_callback, samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE):
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping Resonance Synth...")
            self.running = False
        except Exception as e:
            print(f"Audio Output Error: {e}")

if __name__ == "__main__":
    synth = ResonanceSynth()
    synth.start()
