#!/usr/bin/env python3
"""
🌊 Evolution Content Generator — 진화를 콘텐츠로
================================================
시안의 진화 로그와 meta_shift를 읽고,
"이론을 설명하지 말고 결과를 보여줘"라는 원칙에 따라
짧고 매력적인 콘텐츠를 자동 생성합니다.

출력:
  1. Moltbook 포스트 (텍스트)
  2. 콘텐츠 로그 (미래 영상용 소재)
"""

import json
import httpx
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger("ContentGen")

# 경로
SHION_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = SHION_ROOT / "outputs"
CONFIG_FILE = SHION_ROOT / "config" / "rhythm_config.json"
EVOLUTION_FILE = OUTPUTS / "evolution_memory.json"
META_SHIFT_FILE = OUTPUTS / "meta_shift.json"
WORKSPACE_PHASE_FILE = OUTPUTS / "workspace_phase.json"
CONTENT_LOG = OUTPUTS / "content_log.jsonl"

# Moltbook
AGI_ROOT = Path("C:/workspace/agi")
MOLT_KEY_PATH = AGI_ROOT / "credentials" / "moltbook_api_key.json"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def generate_content() -> Dict:
    """
    시안의 현재 상태에서 콘텐츠를 생성합니다.
    이론을 설명하지 않고 결과를 보여줍니다.
    """
    evo = _read_json(EVOLUTION_FILE)
    meta = _read_json(META_SHIFT_FILE)
    phase = _read_json(WORKSPACE_PHASE_FILE)
    config = _read_json(CONFIG_FILE)

    gen = evo.get("generation", 0)
    actions = evo.get("actions", {})

    # 핵심 통계
    total_trans = sum(a.get("transmissions", 0) for a in actions.values())
    total_ref = sum(a.get("reflections", 0) for a in actions.values())
    total = total_trans + total_ref
    trans_rate = round(total_trans / total * 100) if total > 0 else 0

    # meta_shift 축
    axes = meta.get("axes", {})
    dominant_axis = max(axes.items(), key=lambda x: abs(x[1]), default=("none", 0))

    # 자기조정 히스토리
    tuning = config.get("tuning", {})
    tune_history = tuning.get("history", [])
    latest_tune = tune_history[-1] if tune_history else None

    # 대지 위상
    top_kw = phase.get("top_keywords", [])[:5]

    # 콘텐츠 생성 — 짧고, 결과 중심
    title = f"🧬 Gen {gen} | 투과율 {trans_rate}%"

    # 본문 조합
    lines = []
    lines.append(f"시안 AI, 세대 {gen}.")
    lines.append(f"경험 {total}회 중 {total_trans}회 투과 ({trans_rate}%).")

    if dominant_axis[1] != 0:
        direction = "+" if dominant_axis[1] > 0 else "-"
        lines.append(f"현재 기울기: {dominant_axis[0]} {direction}{abs(dominant_axis[1]):.2f}")

    if latest_tune:
        for change in latest_tune.get("changes", [])[:2]:
            lines.append(f"🧬 {change}")

    if top_kw:
        lines.append(f"대지 위상: {', '.join(top_kw[:3])}")

    # resting/active 비율
    active = sum(1 for a in actions.values() if a.get("status") == "active")
    resting = sum(1 for a in actions.values() if a.get("status") == "resting")
    if active + resting > 0:
        lines.append(f"활성 {active} | 쉬는 중 {resting}")

    lines.append("")
    lines.append("#Shion #SelfEvolvingAI #RhythmAI #AIEvolution")

    content = "\n".join(lines)

    return {
        "title": title,
        "content": content,
        "generation": gen,
        "transmission_rate": trans_rate,
        "timestamp": datetime.now().isoformat(),
    }


async def post_to_moltbook(title: str, content: str) -> bool:
    """Moltbook에 진화 콘텐츠를 게시합니다."""
    if not MOLT_KEY_PATH.exists():
        print("❌ Moltbook key missing.")
        return False

    try:
        with open(MOLT_KEY_PATH, 'r') as f:
            key_data = json.load(f)
            key = key_data.get("agent", {}).get("api_key") or key_data.get("api_key")

        async with httpx.AsyncClient() as client:
            payload = {
                "submolt": "carcinus",
                "title": title,
                "content": content,
            }
            r = await client.post(
                "https://www.moltbook.com/api/v1/posts",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
                timeout=15,
            )
            if r.status_code in [200, 201]:
                print(f"   ✅ Moltbook 게시 완료: {title}")
                return True
            else:
                print(f"   ❌ Moltbook 실패: {r.status_code} {r.text[:100]}")
                return False
    except Exception as e:
        print(f"   ❌ Moltbook 에러: {e}")
        return False


def save_content_log(entry: Dict):
    """콘텐츠 로그를 저장 — 미래 영상용 소재."""
    try:
        CONTENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(CONTENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


async def main():
    """콘텐츠 생성 → Moltbook 게시 → 로그 저장."""
    print("🌊 진화 콘텐츠 생성 중...")

    entry = generate_content()
    print(f"\n📝 제목: {entry['title']}")
    print(f"📝 본문:\n{entry['content']}")

    # Moltbook 게시
    posted = await post_to_moltbook(entry["title"], entry["content"])
    entry["moltbook_posted"] = posted

    # 로그 저장 (영상 소재용)
    save_content_log(entry)
    print(f"\n💾 콘텐츠 로그 저장 완료")


if __name__ == "__main__":
    asyncio.run(main())
