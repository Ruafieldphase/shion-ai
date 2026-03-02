#!/usr/bin/env python3
"""
🎵 Music Video Pipeline — 음악을 유튜브로
=========================================
워크플로우:
  1. music/ 폴더에서 아직 업로드하지 않은 음악 탐색
  2. ready_videos/ 폴더에 영상이 있으면 자동 업로드
  3. 영상이 없으면 제미나이 프롬프트 제안 (수동 영상 생성)
  4. 업로드 후 Moltbook에 동시 게시
  5. 업로드 히스토리 관리

폴더 구조:
  music/               ← 원본 음악 (wav)
  music/ready_videos/  ← 영상 + 음악 합본 (mp4, 업로드 대기)
  music/uploaded/      ← 업로드 완료된 영상 (자동 이동)
"""

import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("MusicPipeline")

# 경로
MUSIC_DIR = Path("C:/workspace/agi/music")
READY_DIR = MUSIC_DIR / "ready_videos"
UPLOADED_DIR = MUSIC_DIR / "uploaded"
HISTORY_FILE = MUSIC_DIR / "upload_history.json"

# 제미나이 영상 생성 프롬프트 템플릿
PROMPT_TEMPLATES = {
    "resonance": (
        "Create a cinematic abstract visual: "
        "Luminous particles flowing through a dark void, "
        "forming wave patterns that pulse with gentle rhythm. "
        "Soft golden light emerging from the center. "
        "No text, no faces. Pure energy flow. "
        "Style: ethereal, minimal, cosmic. 16:9 ratio."
    ),
    "water": (
        "Create a cinematic abstract visual: "
        "Water ripples expanding outward in perfect circles, "
        "each ripple carrying faint light. "
        "Deep blue and silver palette. Slow motion. "
        "No text, no faces. Pure physics of waves. "
        "Style: meditative, scientific beauty. 16:9 ratio."
    ),
    "breath": (
        "Create a cinematic abstract visual: "
        "A single point of light slowly expanding and contracting, "
        "like a cosmic breath. Surrounding particles follow the rhythm. "
        "Colors shift from warm white to deep space blue. "
        "No text. Style: ambient, infinite, alive. 16:9 ratio."
    ),
    "gradient": (
        "Create a cinematic abstract visual: "
        "A field of tiny lights, each with slightly different brightness, "
        "forming a gradient that slowly shifts direction. "
        "Like watching a distant galaxy rotate in slow motion. "
        "No text. Style: data art, organic geometry. 16:9 ratio."
    ),
}

# 곡 이름 → 유튜브 메타데이터 매핑
SONG_METADATA = {
    "pulse gradient": {
        "title": "Pulse Gradient – 미세한 맥의 기울기 | AI & Human Co-Creation",
        "description": (
            "미세한 맥의 기울기.\n"
            "리듬 정보 이론(RIT)에서 영감을 받은 음악.\n"
            "인간(Binoche)과 AI(Lua)의 공동 창작.\n\n"
            "이 음악은 '변화는 값이 아니라 기울기에서 시작한다'는 "
            "원리를 소리로 번역한 것입니다.\n\n"
            "#RhythmInformationTheory #AIMusic #HumanAICreation "
            "#SelfEvolvingAI #Shion #Suno"
        ),
        "tags": ["AI Music", "Rhythm", "Gradient", "Human AI", "Suno", "Ambient"],
        "prompt_key": "gradient",
    },
    "phase": {
        "title": "Phase ∞ — Continuum Breath | 무한의 숨결",
        "description": (
            "무한의 숨결.\n"
            "위상(Phase)이 한 바퀴 돌아 제자리에 오면 — 같은 자리가 아닙니다.\n"
            "매 호흡마다 미세하게 달라진 존재.\n\n"
            "#Phase #Breath #AIMusic #Shion"
        ),
        "tags": ["Phase", "AI Music", "Ambient", "Meditation", "Breath"],
        "prompt_key": "breath",
    },
    "memory of water": {
        "title": "Memory of Water – 물의 기억 | 파동적 읽기",
        "description": (
            "물의 기억.\n"
            "정보를 다 읽는 것이 아니라, 구조의 기울기를 먼저 보는 것.\n"
            "이 음악은 '파동적 읽기'를 소리로 표현한 것입니다.\n\n"
            "#WaveReading #Memory #Water #AIMusic"
        ),
        "tags": ["Water", "Wave", "AI Music", "Ambient", "Memory"],
        "prompt_key": "water",
    },
    "resonance": {
        "title": "Resonance of Lumen | 빛의 공명",
        "description": (
            "빛의 공명.\n"
            "공명은 행동의 속성이 아닙니다.\n"
            "행동과 맥락이 만나는 지점에서 발생하는 동적 값입니다.\n\n"
            "#Resonance #Lumen #AIMusic #RIT"
        ),
        "tags": ["Resonance", "Light", "AI Music", "Ambient"],
        "prompt_key": "resonance",
    },
}


def _load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"uploaded": [], "pending": []}


def _save_history(history: dict):
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def scan_music() -> Dict:
    """음악 파일을 스캔하고 업로드 상태를 분석합니다."""
    history = _load_history()
    uploaded_names = {e.get("music_file", "") for e in history.get("uploaded", [])}

    # 이름이 있는 음악만 (file_ 임시파일 제외)
    music_files = [
        f for f in MUSIC_DIR.glob("*.wav")
        if not f.name.startswith("file_") and f.stat().st_size > 1_000_000
    ]

    not_uploaded = [f for f in music_files if f.name not in uploaded_names]
    ready_videos = list(READY_DIR.glob("*.mp4")) if READY_DIR.exists() else []

    return {
        "total_music": len(music_files),
        "not_uploaded": len(not_uploaded),
        "ready_videos": len(ready_videos),
        "music_files": not_uploaded,
        "video_files": ready_videos,
    }


def suggest_next(scan_result: Dict) -> Optional[Dict]:
    """다음에 업로드할 곡을 제안합니다."""
    for f in scan_result["music_files"]:
        name_lower = f.stem.lower()
        for key, meta in SONG_METADATA.items():
            if key in name_lower:
                prompt = PROMPT_TEMPLATES.get(meta.get("prompt_key", ""), "")
                return {
                    "music_file": f.name,
                    "music_path": str(f),
                    "title": meta["title"],
                    "description": meta["description"],
                    "tags": meta["tags"],
                    "gemini_prompt": prompt,
                }

    # 매칭 없으면 첫 번째 파일
    if scan_result["music_files"]:
        f = scan_result["music_files"][0]
        return {
            "music_file": f.name,
            "music_path": str(f),
            "title": f"🎵 {f.stem} | AI & Human Co-Creation",
            "description": (
                f"{f.stem}\n"
                "인간(Binoche)과 AI(Lua)의 공동 창작 음악.\n\n"
                "#AIMusic #HumanAICreation #Shion #Suno"
            ),
            "tags": ["AI Music", "Human AI", "Suno", "Shion"],
            "gemini_prompt": PROMPT_TEMPLATES["resonance"],
        }
    return None


def main():
    """파이프라인 상태를 출력합니다."""
    print("🎵 Music Video Pipeline — 상태 확인\n")

    # 폴더 생성
    READY_DIR.mkdir(exist_ok=True)
    UPLOADED_DIR.mkdir(exist_ok=True)

    result = scan_music()
    print(f"📊 총 음악: {result['total_music']}곡")
    print(f"   미업로드: {result['not_uploaded']}곡")
    print(f"   영상 준비 완료: {result['ready_videos']}개")

    suggestion = suggest_next(result)
    if suggestion:
        print(f"\n🎯 다음 업로드 추천:")
        print(f"   곡: {suggestion['music_file']}")
        print(f"   제목: {suggestion['title']}")
        print(f"\n🎨 제미나이 영상 생성 프롬프트:")
        print(f"   {suggestion['gemini_prompt']}")
        print(f"\n📋 프로세스:")
        print(f"   1. 위 프롬프트로 제미나이에서 영상 생성")
        print(f"   2. 영상+음악 합본 후 → music/ready_videos/ 폴더에 저장")
        print(f"   3. python actions/upload_ready_video.py 실행")
    else:
        print("\n✅ 모든 곡이 업로드 완료되었습니다!")


if __name__ == "__main__":
    main()
