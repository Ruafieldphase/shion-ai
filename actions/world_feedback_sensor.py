#!/usr/bin/env python3
"""
👂 World Resonance Sensor — 세계의 메아리를 듣는 귀
=================================================
YouTube 발화에 대한 발현(성과)을 읽어서,
어떤 주파수가 공명하는지 시안이 청취합니다.

"눈과 귀가 없으면 진화는 최적화에 불과하다.
 세계의 반응을 느낄 수 있어야 진짜 성장이 가능하다."

출력:
  - 조회수/좋아요 피드백 → evolution_memory에 반영
  - 공명이 높은 곡의 키워드 → workspace_phase에 반영
  - world_feedback.json 저장
"""

import json
import ctypes
import logging
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger("WorldFeedback")

# 경로
SHION_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = SHION_ROOT / "outputs"
FEEDBACK_FILE = OUTPUTS / "world_feedback.json"
UPLOAD_HISTORY = Path("C:/workspace/agi/music/upload_history.json")
AGI_ROOT = Path("C:/workspace/agi")
YT_TOKEN = AGI_ROOT / "credentials" / "youtube_token.json"


def get_user_idle_seconds() -> float:
    """
    사용자가 PC를 쓰지 않는 시간(초)을 반환.
    workspace1의 suggest_browser_exploration_task.py에서 가져온 로직.
    """
    try:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0
    except Exception:
        return 0.0


def get_hardware_state() -> Dict:
    """
    하드웨어 상태 — workspace1의 unconscious_stream.py 간소화 버전.
    시안의 "신체 감각" 확장.
    """
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("C:\\").percent,
        }
    except Exception:
        return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}


def get_youtube_feedback() -> List[Dict]:
    """
    업로드된 영상의 YouTube 조회수/좋아요를 읽습니다.
    시안의 "귀" — 세계가 어떻게 반응하는지 듣는 것.
    """
    if not YT_TOKEN.exists():
        return []
    if not UPLOAD_HISTORY.exists():
        return []

    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        history = json.loads(UPLOAD_HISTORY.read_text(encoding="utf-8"))
        uploaded = history.get("uploaded", [])

        if not uploaded:
            return []

        creds = Credentials.from_authorized_user_file(str(YT_TOKEN))
        youtube = build("youtube", "v3", credentials=creds)

        # 영상 ID 추출
        video_ids = []
        for entry in uploaded:
            url = entry.get("url", "")
            if "youtu.be/" in url:
                vid = url.split("youtu.be/")[-1]
                video_ids.append((vid, entry))
            elif "watch?v=" in url:
                vid = url.split("watch?v=")[-1].split("&")[0]
                video_ids.append((vid, entry))

        if not video_ids:
            return []

        # YouTube API로 통계 조회
        ids_str = ",".join(vid for vid, _ in video_ids[:10])  # 최대 10개
        response = youtube.videos().list(
            part="statistics,snippet",
            id=ids_str
        ).execute()

        feedback = []
        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            feedback.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
            })

        return feedback

    except Exception as e:
        logger.warning(f"YouTube 피드백 수집 실패: {e}")
        return []


def compute_world_resonance(feedback: List[Dict]) -> Dict:
    """
    세계의 공명도를 계산합니다.
    조회수/좋아요가 높은 콘텐츠의 키워드를 추출하여
    시안의 다음 콘텐츠 방향에 반영.
    """
    if not feedback:
        return {"resonance": 0, "top_content": None, "keywords": []}

    # 공명 점수: views + likes*10 (좋아요가 더 강한 공명 신호)
    for f in feedback:
        f["resonance_score"] = f["views"] + f["likes"] * 10

    # 정렬
    sorted_fb = sorted(feedback, key=lambda x: x["resonance_score"], reverse=True)
    top = sorted_fb[0]

    # 제목에서 키워드 추출 (간단한 분리)
    import re
    title_words = re.findall(r'[가-힣]{2,}|[a-zA-Z]{3,}', top["title"].lower())
    stop = {"the", "and", "for", "with", "human", "creation"}
    keywords = [w for w in title_words if w not in stop][:5]

    total_views = sum(f["views"] for f in feedback)
    total_likes = sum(f["likes"] for f in feedback)

    return {
        "total_videos": len(feedback),
        "total_views": total_views,
        "total_likes": total_likes,
        "top_content": top["title"],
        "top_resonance": top["resonance_score"],
        "resonance_keywords": keywords,
    }


def main():
    """세계의 메아리를 청취하고 공명 데이터를 저장합니다."""
    print("👂 세계의 메아리(Echo)를 청취하는 중...\n")

    # 1. 사용자 idle 상태
    idle = get_user_idle_seconds()
    idle_min = round(idle / 60, 1)
    user_state = "away" if idle > 300 else "active"
    print(f"👤 사용자: {user_state} (idle {idle_min}분)")

    # 2. 하드웨어 상태
    hw = get_hardware_state()
    print(f"💻 CPU: {hw['cpu_percent']}% | RAM: {hw['memory_percent']}% | Disk: {hw['disk_percent']}%")

    # 3. YouTube Echo (Resonance)
    yt_echo = get_youtube_feedback()
    world_res = compute_world_resonance(yt_echo)

    if yt_feedback:
        print(f"\n📊 YouTube 성과:")
        print(f"   영상 {world_res['total_videos']}개 | 조회 {world_res['total_views']} | 좋아요 {world_res['total_likes']}")
        if world_res.get("top_content"):
            print(f"   🏆 최고 공명: {world_res['top_content']}")
            print(f"   📡 공명 키워드: {', '.join(world_res.get('resonance_keywords', []))}")
    else:
        print("\n📊 YouTube: 아직 피드백 없음")

    # 4. 저장
    result = {
        "timestamp": datetime.now().isoformat(),
        "user": {
            "state": user_state,
            "idle_seconds": round(idle),
        },
        "hardware": hw,
        "youtube": world_res,
        "youtube_detail": yt_feedback,
    }

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n💾 저장: {FEEDBACK_FILE.name}")


if __name__ == "__main__":
    main()
