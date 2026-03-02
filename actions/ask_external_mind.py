#!/usr/bin/env python3
"""
🤝 External Mind Bridge — 다른 AI에게 물어보는 손
=================================================
시안이 혼자 해결 못하는 질문을 외부 AI에게 물어봅니다.

workspace1의 external_ai_bridge.py에서 API 통신 로직을 가져옴.
GUI 조작 없이 API로만 통신 — 백그라운드에서 자동 실행 가능.

프로세스:
  1. 최근 통찰(insight)을 읽음
  2. 시안 v1(로컬 LLM)에게 먼저 물어봄
  3. 응답이 부족하면 Ollama에 물어봄
  4. 결과를 external_mind.json으로 저장
  5. contemplation이 다음 사이클에서 활용

"손이 있어야 세계를 만질 수 있다"
"""

import json
import asyncio
import logging
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger("ExternalMind")

# 경로
SHION_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = SHION_ROOT / "outputs"
INSIGHT_FILE = OUTPUTS / "contemplation_insights.jsonl"
EXTERNAL_MIND_FILE = OUTPUTS / "external_mind.json"
WORLD_FEEDBACK_FILE = OUTPUTS / "world_feedback.json"

# 시안 v1 (로컬 LLM)
SHION_V1_URL = "http://localhost:8000"

# Ollama (로컬 대형 모델, 있으면 사용)
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:4b"


def _get_latest_insight() -> Optional[str]:
    """최근 통찰을 읽습니다."""
    if not INSIGHT_FILE.exists():
        return None
    try:
        lines = INSIGHT_FILE.read_text(encoding="utf-8").strip().split("\n")
        if not lines:
            return None
        last = json.loads(lines[-1])
        return last.get("insight", "")
    except Exception:
        return None


def _get_world_context() -> str:
    """세계 피드백에서 맥락을 추출합니다."""
    if not WORLD_FEEDBACK_FILE.exists():
        return ""
    try:
        data = json.loads(WORLD_FEEDBACK_FILE.read_text(encoding="utf-8"))
        yt = data.get("youtube", {})
        top = yt.get("top_content", "")
        keywords = ", ".join(yt.get("resonance_keywords", []))
        if top:
            return f"최근 콘텐츠 '{top}' (키워드: {keywords})"
        return ""
    except Exception:
        return ""


def _build_question(insight: str, world_context: str) -> str:
    """통찰에서 질문을 생성합니다."""
    question = (
        f"나는 자율 AI 시스템이야. 최근 이런 통찰을 했어:\n"
        f"'{insight}'\n\n"
    )
    if world_context:
        question += f"세계 맥락: {world_context}\n\n"

    question += (
        "이 통찰을 더 깊게 발전시키려면 어떤 방향이 좋을까? "
        "구체적이고 실행 가능한 제안을 해줘. 3줄 이내로."
    )
    return question


def ask_shion_v1(question: str) -> Optional[str]:
    """시안 v1 (로컬 1B LLM)에게 물어봅니다."""
    try:
        payload = json.dumps({
            "prompt": question,
            "max_tokens": 200,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{SHION_V1_URL}/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", result.get("text", ""))
    except Exception as e:
        logger.warning(f"시안 v1 응답 실패: {e}")
        return None


def ask_ollama(question: str) -> Optional[str]:
    """Ollama (로컬 대형 모델)에게 물어봅니다."""
    try:
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": "너는 자율 AI 시스템의 조언자야. 간결하게 답해."},
                {"role": "user", "content": question},
            ],
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("message", {}).get("content", "")
    except Exception as e:
        logger.warning(f"Ollama 응답 실패: {e}")
        return None


def main():
    """외부 AI에게 물어보고 결과를 저장합니다."""
    print("🤝 외부 지성에게 묻는 중...\n")

    # 1. 최근 통찰 읽기
    insight = _get_latest_insight()
    if not insight:
        print("   아직 통찰이 없습니다. contemplation 이후 실행하세요.")
        return

    print(f"💡 최근 통찰: {insight[:80]}...")

    # 2. 세계 맥락
    world_ctx = _get_world_context()
    if world_ctx:
        print(f"🌍 세계 맥락: {world_ctx}")

    # 3. 질문 생성
    question = _build_question(insight, world_ctx)

    # 4. 시안 v1에게 먼저 물어봄
    print("\n🧠 시안 v1에게 묻는 중...")
    response = ask_shion_v1(question)
    source = "shion_v1"

    # 5. 응답이 부족하면 Ollama
    if not response or len(response.strip()) < 10:
        print("🤖 Ollama에게 묻는 중...")
        response = ask_ollama(question)
        source = "ollama"

    if response:
        print(f"\n📩 응답 ({source}):")
        print(f"   {response[:200]}")
    else:
        print("\n❌ 외부 응답 없음 (모든 두뇌 비활성)")
        response = ""
        source = "none"

    # 6. 저장
    result = {
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "world_context": world_ctx,
        "question": question,
        "response": response,
        "source": source,
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    EXTERNAL_MIND_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n💾 저장: {EXTERNAL_MIND_FILE.name}")


if __name__ == "__main__":
    main()
