import cv2
import numpy as np
import mss
import time
from pathlib import Path
from datetime import datetime

class WaveObserver:
    """화면의 '흐름(파동)'을 감지하는 엔진."""
    
    def __init__(self, capture_dir: Path):
        self.capture_dir = capture_dir
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1] # 주 모니터

    def feel_the_flow(self, duration: float = 3.0, fps: int = 5) -> dict:
        """지정한 시간 동안 화면의 변화(파동)를 느낍니다.
        
        Returns:
            {
                "motion_score": 0.0 ~ 1.0 (변화량),
                "peak_change": 피크 변화 시점,
                "representative_frame": 가장 변화가 컸던 순간의 경로
            }
        """
        frames = []
        scores = []
        start_time = time.time()
        interval = 1.0 / fps
        
        last_frame = None
        max_score = 0
        peak_frame_data = None
        
        while time.time() - start_time < duration:
            # 1. 캡처 (저해상도로 변환하여 가볍게 처리)
            sct_img = self.sct.grab(self.monitor)
            frame = np.array(sct_img)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
            frame_small = cv2.resize(frame_gray, (640, 360)) # 분석은 작게
            
            if last_frame is not None:
                # 2. 차이 계산 (파동의 크기)
                diff = cv2.absdiff(last_frame, frame_small)
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                score = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)
                scores.append(score)
                
                if score > max_score:
                    max_score = score
                    peak_frame_data = frame # 원본 화질 저장용
            
            last_frame = frame_small
            time.sleep(interval)
            
        # 결과 요약
        avg_motion = np.mean(scores) if scores else 0
        
        # 가장 역동적이었던 순간을 '입자'로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        peak_path = self.capture_dir / f"wave_peak_{timestamp}.png"
        if peak_frame_data is not None:
            cv2.imwrite(str(peak_path), peak_frame_data)
            
        return {
            "motion_score": float(avg_motion),
            "max_score": float(max_score),
            "peak_frame": peak_path if peak_frame_data is not None else None,
            "duration": duration
        }

if __name__ == "__main__":
    # 단독 테스트
    obs = WaveObserver(Path(r"c:\workspace2\shion\outputs\wave_test"))
    print("🌊 파동을 느끼는 중... (3초)")
    result = obs.feel_the_flow()
    print(f"결과: 움직임 점수 {result['motion_score']:.4f} / 피크 {result['max_score']:.4f}")
    if result['peak_frame']:
        print(f"피크 장면 저장: {result['peak_frame']}")
