"""
YouTube Bridge - FSD를 위한 외부 지식 검색 인터페이스
=====================================================
(실제 구현: Gemini의 프리트레인 지식을 활용하여 외부 검색을 시뮬레이션)

FSD가 모르는 패턴을 만났을 때, Gemini에게 지식을 물어보고 
그것을 텍스트 지식으로 변환하여 반환합니다.
"""

import logging
from typing import Dict, Optional, Any

# 로거 설정
logger = logging.getLogger("youtube_bridge")
logger.setLevel(logging.INFO)

class YouTubeBridge:
    def __init__(self):
        self.history = []

    async def search_and_learn(self, query: str, model: Any = None) -> Dict[str, str]:
        """
        Gemini에게 지식을 물어봅니다.
        
        Args:
            query: 질문 (예: "OBS 장면 전환 단축키")
            model: Gemini 모델 인스턴스 (FSDController에서 주입)
            
        Returns:
            Dict: {
                "source": "Gemini Knowledge",
                "title": "Generated Solution",
                "content": "솔루션 텍스트..."
            }
        """
        logger.info(f"🕵️ 지식 탐색 시작: {query}")
        
        if not model:
            return await self._simulate_learning(query)
            
        try:
            prompt = f"""
            사용자가 윈도우 PC에서 다음 작업을 하려고 합니다:
            "{query}"
            
            이 작업을 수행하기 위한 구체적인 단계(단축키, 메뉴 클릭, 타이핑 등)를 
            간결한 텍스트로 설명해주세요. 복잡한 설명 대신 실행 가능한 행동 위주로 알려주세요.
            """
            
            response = await model.generate_content_async(prompt)
            content = response.text
            
            return {
                "source": "Gemini Knowledge",
                "title": f"Solution for {query}",
                "content": content
            }
            
        except Exception as e:
            logger.error(f"지식 생성 실패: {e}")
            return await self._simulate_learning(query)

    async def _simulate_learning(self, query: str) -> Dict[str, str]:
        """(폴백) 시뮬레이션 데이터"""
        query_lower = query.lower()
        
        if "obs" in query_lower and "switch" in query_lower:
            return {
                "source": "Simulation",
                "title": "OBS Studio Tutorial",
                "content": "Click on the scene name in the 'Scenes' dock. Or use arrow keys to select."
            }
            
        return {
            "source": "Unknown",
            "title": "Information Not Found",
            "content": f"Sorry, could not find info for '{query}'."
        }

# 싱글톤
_bridge = None

def get_bridge():
    global _bridge
    if _bridge is None:
        _bridge = YouTubeBridge()
    return _bridge
