"""
External AI Bridge - 범용 외부 AI 통신 모듈
Trinity가 다양한 외부 AI (ChatGPT, Claude, Comet, Browser)와 대화합니다.
"""
import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

import pyautogui
import pyperclip
import pygetwindow as gw
import numpy as np
from PIL import Image
from services.model_selector import ModelSelector
from services.config import RESONANCE_LEDGER, WINDOWS_AGI_ROOT

logger = logging.getLogger("ExternalAIBridge")

# Aura 색상
AURA_COLOR_ACTIVE = "#FF00FF"  # 마젠타 (대화 중)
AURA_COLOR_WAITING = "#00FFFF"  # Shion (대기 중)


class AITarget(Enum):
    """지원되는 AI 대상"""
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    COMET = "comet"
    PERPLEXITY = "perplexity"
    BROWSER = "browser"
    OLLAMA = "ollama"
    ZHIPU = "zhipu"
    GEMINI = "gemini"


# 대상별 설정
TARGET_CONFIGS = {
    AITarget.CHATGPT: {
        "window_title": "ChatGPT",
        "app_name": "ChatGPT",
        "is_browser": False,
    },
    AITarget.CLAUDE: {
        "window_title": "Claude",
        "app_name": "Claude",
        "is_browser": False,
    },
    AITarget.COMET: {
        "window_title": "Comet",
        "browser_name": "Comet",
        "is_browser": True,
    },
    AITarget.PERPLEXITY: {
        "window_title": "Perplexity",
        "url": "https://www.perplexity.ai",
        "is_browser": True,
    },
    AITarget.OLLAMA: {
        "url": "http://localhost:11434/api/chat",
        "model": "llama3.2:latest",
        "is_api": True,
    },
    AITarget.ZHIPU: {
        "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4-flash",
        "is_api": True,
    },
    AITarget.GEMINI: {
        "model": "gemini-1.5-flash",
        "is_api": True,
    },
}


class ExternalAIBridge:
    """
    범용 외부 AI 통신 브리지
    여러 AI 대상을 통합된 인터페이스로 관리합니다.
    """
    
    def __init__(self):
        self.screenshot_dir = WINDOWS_AGI_ROOT / "outputs" / "external_ai_screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        self.model_selector = ModelSelector(logger=logger)
        
        # 세션 추적
        self.active_sessions: Dict[AITarget, Any] = {}  # 열린 창들
        self.last_used_target: Optional[AITarget] = None
        

        # Aura 프로세스
        self.aura_process = None
        
        # Resonance Ledger
        self.resonance_ledger_path = RESONANCE_LEDGER
        
    def _log_resonance(self, event_type: str, content: str, target: AITarget):
        """공명 장부에 이벤트 기록"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "dialogue_event",
                "layer": "external_bridge",
                "event": event_type,
                "target": target.value,
                "content_summary": content[:100] + "..." if len(content) > 100 else content,
                "length": len(content)
            }
            
            self.resonance_ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.resonance_ledger_path, 'a', encoding='utf-8') as f:
                import json
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                
        except Exception as e:
            logger.warning(f"Failed to log resonance: {e}")

    def _find_window(self, target: AITarget) -> Optional[Any]:
        """대상 AI의 창 찾기"""
        config = TARGET_CONFIGS.get(target)
        if not config:
            return None
            
        try:
            title = config.get("window_title", "")
            windows = gw.getWindowsWithTitle(title)
            
            for win in windows:
                if title.lower() in win.title.lower():
                    logger.info(f"Found existing window: {win.title}")
                    return win
            return None
        except Exception as e:
            logger.warning(f"Window detection failed for {target}: {e}")
            return None
    
    def _activate_window(self, window) -> bool:
        """창 활성화"""
        try:
            if window.isMinimized:
                window.restore()
            window.activate()
            logger.info(f"Activated: {window.title}")
            return True
        except Exception as e:
            logger.warning(f"Activation failed: {e}")
            return False
    
    async def _open_app(self, target: AITarget) -> bool:
        """앱 실행 (Win+S 검색)"""
        config = TARGET_CONFIGS.get(target)
        if not config:
            return False
        
        app_name = config.get("app_name", config.get("window_title", ""))
        
        # Win+S → 검색
        pyautogui.hotkey('win', 's')
        await asyncio.sleep(0.5)
        
        # 앱 이름 입력
        pyperclip.copy(app_name)
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(1)
        
        # Enter → 실행
        pyautogui.press('enter')
        logger.info(f"Launched app: {app_name}")
        await asyncio.sleep(2)
        
        return True
    
    async def _open_browser_url(self, target: AITarget) -> bool:
        """브라우저에서 URL 열기"""
        config = TARGET_CONFIGS.get(target)
        if not config:
            return False
            
        # Comet 브라우저의 경우
        if target == AITarget.COMET:
            browser_name = config.get("browser_name", "Comet")
            return await self._open_app(target)
        
        # URL이 있는 경우 기본 브라우저로 열기
        url = config.get("url")
        if url:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            await asyncio.sleep(3)
            return True
            
        return False
    
    async def find_or_open(self, target: AITarget) -> bool:
        """
        대상 AI 창을 찾거나 열기
        맥락 인식: 이미 열려있으면 활성화, 아니면 새로 열기
        """
        # 1. 이미 열린 창 찾기
        window = self._find_window(target)
        
        if window:
            # 창이 있으면 활성화
            logger.info(f"Reusing existing {target.value} window")
            self.active_sessions[target] = window
            return self._activate_window(window)
        
        # 2. 창이 없으면 새로 열기
        logger.info(f"Opening new {target.value}...")
        config = TARGET_CONFIGS.get(target)
        
        if config.get("is_browser"):
            success = await self._open_browser_url(target)
        else:
            success = await self._open_app(target)
        
        if success:
            # 열린 후 창 다시 찾기
            await asyncio.sleep(2)
            window = self._find_window(target)
            if window:
                self.active_sessions[target] = window
                
        return success
    
    async def _type_message(self, message: str):
        """메시지 입력 (클립보드 사용)"""
        await asyncio.sleep(0.5)
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        logger.info(f"Typed message ({len(message)} chars)")
    
    def _compare_screenshots(self, img1: Image.Image, img2: Image.Image, threshold: float = 0.98) -> bool:
        """스크린샷 비교 (응답 완료 감지용)"""
        try:
            arr1 = np.array(img1.convert('L'))
            arr2 = np.array(img2.convert('L'))
            
            if arr1.shape != arr2.shape:
                return False
            
            diff = np.abs(arr1.astype(float) - arr2.astype(float))
            similarity = 1 - (np.sum(diff) / (arr1.size * 255))
            
            return similarity >= threshold
        except:
            return False
    
    async def _wait_for_response(self, timeout_sec: int = 60) -> None:
        """응답 완료 대기 (스크린샷 비교)"""
        logger.info("Waiting for response...")
        await asyncio.sleep(5)  # 초기 대기
        
        start_time = time.time()
        prev_screenshot = pyautogui.screenshot()
        stable_count = 0
        
        while time.time() - start_time < timeout_sec:
            await asyncio.sleep(2.5)
            curr_screenshot = pyautogui.screenshot()
            
            if self._compare_screenshots(prev_screenshot, curr_screenshot):
                stable_count += 1
                if stable_count >= 2:
                    logger.info("Response complete")
                    return
            else:
                stable_count = 0
            
            prev_screenshot = curr_screenshot
        
        logger.warning(f"Timeout after {timeout_sec}s")
    
    async def _capture_and_extract_response(self) -> Optional[str]:
        """
        🧠 스마트 응답 추출 - AGI가 스스로 방법을 선택
        여러 방법 중 성공하는 것을 찾아 학습합니다.
        """
        try:
            from services.smart_response_extractor import smart_extract_response
            
            logger.info("🧠 스마트 추출기 사용 중...")
            result = smart_extract_response()
            
            if result.success:
                logger.info(f"✅ 추출 성공 (방법: {result.method})")
                return result.content
            else:
                logger.warning(f"❌ 추출 실패: {result.error}")
                return None
                
        except ImportError:
            logger.warning("스마트 추출기 없음 - 기존 방법 사용")
            # 폴백: 기존 Vision 방식
            return await self._fallback_vision_extract()
    
    def _start_aura(self, color: str = AURA_COLOR_ACTIVE):
        """오라 효과 시작"""
        try:
            self._stop_aura()
            script_path = Path(__file__).parent / "agi_aura.py"
            if script_path.exists():
                self.aura_process = subprocess.Popen(
                    [sys.executable, str(script_path), "--color", color],
                    stdout=subprocess.DEVNULL
                )
                logger.info(f"Aura started: {color}")
        except Exception as e:
            logger.warning(f"Aura start failed: {e}")
    
    def _stop_aura(self):
        """오라 효과 중지"""
        if self.aura_process:
            try:
                self.aura_process.terminate()
                logger.info("Aura stopped")
            except:
                pass

    async def _send_to_zhipu(self, message: str, context: Optional[str] = None, identity: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Zhipu AI (BigModel) API를 통한 통신"""
        config = TARGET_CONFIGS.get(AITarget.ZHIPU)
        url = config.get("url")
        model = config.get("model")
        
        # API Key load
        api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("WAVE_API_KEY")
        if not api_key:
            # Try credentials manager
            try:
                from scripts.credentials_manager import CredentialsManager
                cm = CredentialsManager()
                api_key = cm.get_credential("ZHIPU_API_KEY") or cm.get_credential("WAVE_API_KEY")
            except:
                pass
        
        if not api_key:
            logger.error("ZHIPU_API_KEY not found in environment or credentials.")
            return "Error: Zhipu API Key missing. Please check .env_credentials."

        messages = []
        if identity:
            messages.append({"role": "system", "content": identity})
        
        user_content = ""
        if context:
            user_content += f"[Context]\n{context}\n\n"
        user_content += message
        messages.append({"role": "user", "content": user_content})
        
        try:
            import json
            import httpx
            
            logger.info(f"Zhipu API 요청 시작: {model}")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                self._log_resonance("zhipu_response", content, AITarget.ZHIPU)
                return content, model
                
        except Exception as e:
            logger.error(f"Zhipu communication failed: {e}")
            return None, model

    async def _send_to_gemini(self, message: str, context: Optional[str] = None, identity: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Gemini API를 통한 직접 통신"""
        logger.info("Gemini API 요청 시작")
        
        full_prompt = ""
        if identity:
            full_prompt += f"You are: {identity}\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += message
        
        try:
            # ModelSelector (which is already initialized in __init__)
            response, model_used = self.model_selector.try_generate_content(full_prompt)
            if response and hasattr(response, 'text'):
                content = response.text
                self._log_resonance("gemini_response", content, AITarget.GEMINI)
                return content, model_used
            return None, model_used
        except Exception as e:
            logger.error(f"Gemini communication failed: {e}")
            return None, None

    async def _send_to_ollama(self, message: str, context: Optional[str] = None, identity: Optional[str] = None) -> Optional[str]:
        """Ollama API를 통한 직접 통신 (Chat API 사용)"""
        config = TARGET_CONFIGS.get(AITarget.OLLAMA)
        url = config.get("url")
        model = config.get("model")
        
        system_prompt = identity if identity else "당신은 시온(Shion)입니다."
        if context:
            system_prompt += f"\n\n[이전 대화 맥락]\n{context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            import json
            import httpx
            
            logger.info(f"Ollama Chat API 요청 시작: {model}")
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                content = result.get("message", {}).get("content", "")
                self._log_resonance("ollama_response", content, AITarget.OLLAMA)
                return content
                
        except Exception as e:
            logger.error(f"Ollama communication failed: {e}")
            return None
    
    async def send_message(
        self,
        target: AITarget,
        message: str,
        context: Optional[str] = None,
        identity: Optional[str] = None,
        timeout_sec: int = 60
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        외부 AI에게 메시지 보내고 응답 받기
        
        Args:
            target: AI 대상 (ChatGPT, Claude, etc.)
            message: 보낼 메시지
            context: 추가 컨텍스트
            identity: 신분 소개 (선택)
            timeout_sec: 응답 대기 시간
        """
        if target == AITarget.OLLAMA:
            content = await self._send_to_ollama(message, context, identity)
            return content, "ollama/llama3.2"
        if target == AITarget.ZHIPU:
            return await self._send_to_zhipu(message, context, identity)
        if target == AITarget.GEMINI:
            return await self._send_to_gemini(message, context, identity)
            
        logger.info(f"Sending message to {target.value}...")
        self._start_aura(AURA_COLOR_ACTIVE)
        
        try:
            # 1. 창 찾거나 열기
            if not await self.find_or_open(target):
                logger.error(f"Failed to open {target.value}")
                return None
            
            await asyncio.sleep(1)
            
            # 2. 메시지 구성
            full_message = ""
            if identity:
                full_message += identity + "\n\n"
            full_message += message
            if context:
                full_message += f"\n\n[Context]\n{context}"
            
            # 3. 메시지 입력
            await self._type_message(full_message)
            
            # 4. Enter 전송
            pyautogui.press('enter')
            logger.info("Message sent")
            
            self._log_resonance("message_sent", message, target)
            
            # 5. 응답 대기
            await self._wait_for_response(timeout_sec)
            
            # 6. 응답 추출
            response = await self._capture_and_extract_response()
            
            if response:
                self._log_resonance("response_received", response, target)
            
            self.last_used_target = target
            return response
            
        finally:
            self._stop_aura()
    
    def get_active_sessions(self) -> List[AITarget]:
        """현재 열린 AI 세션 목록"""
        active = []
        for target in AITarget:
            if self._find_window(target):
                active.append(target)
        return active


# 편의 함수
async def ask_external_ai(
    target: str,
    message: str,
    **kwargs
) -> Optional[str]:
    """외부 AI에게 질문하는 편의 함수"""
    bridge = ExternalAIBridge()
    
    # 문자열 → Enum 변환
    target_enum = AITarget(target.lower())
    
    return await bridge.send_message(target_enum, message, **kwargs)
