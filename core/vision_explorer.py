#!/usr/bin/env python3
"""
👁️ 비전 탐색기 — Vision Explorer (L3 공간 탐색)
=================================================
moondream 비전 모델을 궤도 해마의 "눈"으로 연결.

계층:
  L1: 소나 (파일 메타데이터)    → 체성감각
  L2: 고주파 스캔 (파일 내용)   → 읽기/분석
  L3: 비전 탐색 (이미지/화면)   → 시각         ← 이것
  L4: 물리적 상호작용           → 피지컬 AI (미래)

moondream은 이미지를 보고 설명할 수 있으므로:
  - 스크린샷 → 현재 화면 상태 인식
  - 이미지 파일 → 시각적 경험 수집
  - 미래: 카메라 입력, 구글어스, 거리뷰

모든 시각 경험은 같은 궤도 좌표계에 등록됩니다.
"""

import json
import logging
import requests
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from io import BytesIO

logger = logging.getLogger("VisionExplorer")

# Ollama 설정
OLLAMA_URL = "http://localhost:11434"
VISION_MODEL = "moondream:latest"
TEXT_MODEL = "gemma3:4b"

# 이미지 확장자
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}

# 스크린샷 저장 경로
SCREENSHOT_DIR = Path(r"c:\workspace2\shion\outputs\vision_captures")


class VisionExplorer:
    """moondream 비전 모델을 통한 시각적 경험 수집 시스템.
    
    인간의 눈이 빛(고주파)을 받아서 시각 피질에서 처리하듯,
    이미지를 moondream으로 해석하고 궤도 해마에 경험으로 등록합니다.
    """
    
    def __init__(self, hippocampus, ollama_url: str = OLLAMA_URL):
        self.hippo = hippocampus
        self.ollama_url = ollama_url
        self.available = self._check_vision_model()
        
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    def _check_vision_model(self) -> bool:
        """moondream 비전 모델 사용 가능 여부 확인."""
        try:
            r = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                for model in models:
                    if "moondream" in model or "llava" in model or "vision" in model:
                        logger.info(f"👁️ 비전 모델 발견: {model}")
                        return True
            logger.warning("⚠️ 비전 모델 없음 (moondream 설치 필요)")
            return False
        except Exception:
            logger.warning("⚠️ Ollama 연결 실패")
            return False
    
    def _image_to_base64(self, image_path: Path) -> Optional[str]:
        """이미지를 base64로 인코딩합니다."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.warning(f"이미지 읽기 실패: {image_path} - {e}")
            return None
    
    def _query_vision(self, image_b64: str, prompt: str = "Describe this image briefly.",
                      model: str = VISION_MODEL) -> Optional[str]:
        """moondream에 이미지와 프롬프트를 보냅니다."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 0.3,
                }
            }
            r = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120  # 비전 모델은 느릴 수 있음
            )
            if r.status_code == 200:
                return r.json().get("response", "")
            else:
                logger.warning(f"비전 응답 오류: {r.status_code}")
                return None
        except Exception as e:
            logger.warning(f"비전 통신 실패: {e}")
            return None
    
    # ═══════════════════════════════════════════
    # L3-1: 이미지 파일 탐색
    # ═══════════════════════════════════════════
    
    def explore_image(self, image_path: Path,
                      context: str = "") -> Dict[str, Any]:
        """이미지 파일을 시각적으로 탐색하여 경험으로 변환합니다.
        
        Args:
            image_path: 이미지 파일 경로
            context: 추가 맥락 (왜 이 이미지를 보는지)
        """
        result = {
            "explored": False,
            "image_path": str(image_path),
            "description": "",
            "vibe": {},
        }
        
        if not self.available:
            result["error"] = "비전 모델 미사용"
            return result
        
        # 이미지 → base64
        b64 = self._image_to_base64(image_path)
        if not b64:
            result["error"] = "이미지 읽기 실패"
            return result
        
        # moondream으로 이미지 해석
        prompt = "Describe what you see in this image in 2-3 sentences. " \
                 "Focus on the main subject, colors, mood, and any text visible."
        if context:
            prompt += f"\nContext: {context}"
        
        description = self._query_vision(b64, prompt)
        if not description:
            result["error"] = "비전 해석 실패"
            return result
        
        # 시각적 설명에서 Vibe 추출
        vibe = self._description_to_vibe(description)
        
        content_ref = f"vision:{image_path.name}"

        result["explored"] = True
        result["description"] = description
        result["vibe"] = vibe
        result["content_ref"] = content_ref
        
        logger.info(f"👁️ 시각 경험: {image_path.name} → {vibe['phase']} "
                    f"(entropy={vibe['entropy']:.2f})")
        
        return result
    
    def _description_to_vibe(self, description: str) -> Dict[str, Any]:
        """시각적 설명에서 Vibe를 추출합니다.
        
        이미지의 시각적 특성을 궤도 좌표계로 변환:
          - 밝고 따뜻한 색 → FLOW (낮은 entropy)
          - 복잡하고 다양한 → EXPANSION (높은 entropy)
          - 어둡고 비어있는 → VOID
          - 구조적이고 정돈된 → CONTRACTION
        """
        desc_lower = description.lower()
        
        # 색온도 / 감정 키워드 기반
        warm_words = {'warm', 'bright', 'sun', 'light', 'happy', 'smile',
                      'golden', 'orange', 'yellow', 'cozy', 'soft'}
        cold_words = {'dark', 'cold', 'shadow', 'night', 'empty', 'void',
                      'black', 'grey', 'fog', 'minimal'}
        complex_words = {'complex', 'detailed', 'many', 'crowded', 'busy',
                         'various', 'multiple', 'intricate', 'diverse'}
        structured_words = {'organized', 'clean', 'simple', 'structured',
                           'geometric', 'symmetric', 'aligned', 'grid'}
        
        words = set(desc_lower.split())
        
        warm_score = len(words & warm_words)
        cold_score = len(words & cold_words)
        complex_score = len(words & complex_words)
        struct_score = len(words & structured_words)
        
        # 위상 결정
        scores = {
            "FLOW": warm_score + struct_score,
            "EXPANSION": complex_score + warm_score,
            "VOID": cold_score,
            "CONTRACTION": struct_score + cold_score,
        }
        phase = max(scores, key=scores.get) if any(scores.values()) else "FLOW"
        
        # 엔트로피: 설명의 복잡도 기반
        words_list = description.split()
        unique_ratio = len(set(w.lower() for w in words_list)) / max(len(words_list), 1)
        entropy = min(1.0, unique_ratio * 1.5)  # 다양할수록 높은 entropy
        
        return {
            "entropy": round(entropy, 4),
            "phase": phase,
            "top_keywords": list(words & (warm_words | cold_words |
                                          complex_words | structured_words))[:3],
            "source": "vision",
        }
    
    # ═══════════════════════════════════════════
    # L3-2: 스크린샷 캡처 및 해석
    # ═══════════════════════════════════════════
    
    def capture_and_explore_screen(self,
                                    context: str = "current desktop") -> Dict[str, Any]:
        """현재 화면을 캡처하고 시각적으로 탐색합니다.
        
        피지컬 AI의 "눈" — 화면을 보고 상태를 파악합니다.
        """
        try:
            from PIL import ImageGrab
            
            screenshot = ImageGrab.grab()
            
            # 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = SCREENSHOT_DIR / f"screen_{timestamp}.png"
            
            # 해상도 줄이기 (전송 효율)
            screenshot = screenshot.resize(
                (screenshot.width // 2, screenshot.height // 2)
            )
            screenshot.save(save_path, "PNG")
            
            logger.info(f"📸 스크린샷 캡처: {save_path}")
            
            # 탐색
            return self.explore_image(save_path, context=context)
            
        except ImportError:
            logger.warning("PIL 없음 — pip install Pillow 필요")
            return {"explored": False, "error": "Pillow 미설치"}
        except Exception as e:
            logger.warning(f"스크린샷 실패: {e}")
            return {"explored": False, "error": str(e)}
    
    # ═══════════════════════════════════════════
    # L3-3: 디렉토리 내 이미지 일괄 탐색
    # ═══════════════════════════════════════════
    
    def explore_directory(self, directory: Path,
                          max_images: int = 10) -> List[Dict[str, Any]]:
        """디렉토리 내의 이미지 파일들을 탐색합니다."""
        results = []
        
        if not directory.exists():
            return results
        
        image_files = [
            f for f in directory.rglob("*")
            if f.is_file() and f.suffix.lower() in IMAGE_EXTS
        ]
        
        # 최근 수정된 것부터
        image_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for img_path in image_files[:max_images]:
            result = self.explore_image(img_path)
            results.append(result)
        
        explored = sum(1 for r in results if r.get("explored"))
        logger.info(f"👁️ 디렉토리 탐색: {directory.name} — "
                    f"{explored}/{len(image_files)} 이미지 탐색")
        
        return results
    
    # ═══════════════════════════════════════════
    # L3-4: URL 이미지 탐색 (웹 시각 경험)
    # ═══════════════════════════════════════════
    
    def explore_url_image(self, url: str,
                          context: str = "") -> Dict[str, Any]:
        """웹 URL의 이미지를 다운로드하여 탐색합니다."""
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                # 임시 저장
                ext = Path(url).suffix or ".png"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = SCREENSHOT_DIR / f"web_{timestamp}{ext}"
                save_path.write_bytes(r.content)
                
                return self.explore_image(save_path, context=context)
        except Exception as e:
            logger.warning(f"URL 이미지 탐색 실패: {e}")
        
        return {"explored": False, "error": "URL 접근 실패"}


# ═══════════════════════════════════════════
# 독립 실행 테스트
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    HIPPO_PATH = Path(__file__).resolve().parent.parent / "outputs" / "fibonacci_orbital_hippocampus.json"
    hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
    
    vision = VisionExplorer(hippo)
    
    print("=" * 60)
    print("👁️ 비전 탐색기 — L3 공간 탐색")
    print("=" * 60)
    print(f"비전 모델: {'✅ 사용 가능' if vision.available else '❌ 미사용'}")
    
    if vision.available:
        # 테스트 1: 스크린샷 캡처
        print("\n--- 스크린샷 캡처 ---")
        screen_result = vision.capture_and_explore_screen("testing vision system")
        if screen_result.get("explored"):
            print(f"  설명: {screen_result['description'][:100]}...")
            print(f"  Vibe: {screen_result['vibe']}")
        else:
            print(f"  실패: {screen_result.get('error', 'unknown')}")
        
        # 테스트 2: 기존 이미지 탐색
        img_dirs = [
            Path(r"c:\workspace2\shion\outputs\vision_captures"),
            Path(r"c:\workspace\agi\outputs"),
        ]
        for d in img_dirs:
            if d.exists():
                images = list(d.glob("*.png")) + list(d.glob("*.jpg"))
                if images:
                    print(f"\n--- 이미지 탐색: {d.name} ({len(images)}개) ---")
                    result = vision.explore_image(images[0])
                    if result.get("explored"):
                        print(f"  {images[0].name}")
                        print(f"  설명: {result['description'][:100]}...")
                        print(f"  Vibe: {result['vibe']}")
                    break
    else:
        print("\n⚠️ moondream 모델이 없습니다.")
        print("  설치: ollama pull moondream")
    
    print("=" * 60)
