#!/usr/bin/env python3
"""
🔊 Vibe Sonar — 소나 시스템
============================
워크스페이스를 파동적으로 스캔하여 궤도 해마에 Vibe 지문을 등록합니다.

workspace_phase_sensor(소나) → fibonacci_orbital_hippocampus(해마)

파일 내용을 읽지 않습니다.
메타데이터(이름, 크기, 수정시간, 경로)만으로 Vibe를 추출합니다.
결과: 각 파일/폴더의 Vibe 좌표 + 파일 경로가 궤도에 등록됩니다.

이후 의식적 트리거(외각 공명)가 발동하면, 
content_ref에 저장된 파일 경로를 통해 실제 내용을 읽습니다.
"""

import sys
import math
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent))

from workspace_phase_sensor import WorkspacePhaseSensor, SCAN_EXTENSIONS, IGNORE_DIRS
from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus

logger = logging.getLogger("VibeSonar")

# 키워드 → 위상(phase) 매핑
# 키워드의 느낌으로 위상을 추정합니다
PHASE_KEYWORDS = {
    "FLOW": {
        "config", "setup", "init", "core", "main", "base", "common",
        "utils", "helper", "routine", "daily", "pulse", "breath",
        "rhythm", "sync", "heartbeat", "minimal",
    },
    "EXPANSION": {
        "new", "experiment", "research", "explore", "discovery",
        "integration", "bridge", "connect", "expand", "growth",
        "evolution", "upgrade", "vision", "dream", "creative",
    },
    "CONTRACTION": {
        "fix", "repair", "debug", "error", "test", "verify",
        "validate", "check", "review", "refactor", "optimize",
        "clean", "prune", "secure", "defense",
    },
    "VOID": {
        "archive", "old", "legacy", "deprecated", "backup",
        "void", "sleep", "rest", "silence", "memory", "history",
        "past", "origin", "heritage",
    },
}


def estimate_phase(name: str, relpath: str) -> str:
    """파일명과 경로에서 위상을 추정합니다."""
    text = (name + " " + relpath).lower()
    scores = {}
    for phase, keywords in PHASE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[phase] = score
    
    max_phase = max(scores, key=scores.get)
    if scores[max_phase] == 0:
        return "FLOW"  # 기본값
    return max_phase


def estimate_entropy(size: int, mtime: datetime, now: datetime) -> float:
    """파일 메타데이터에서 엔트로피를 추정합니다.
    
    - 크고 오래된 파일 → 낮은 엔트로피 (안정적, 내각)
    - 작고 최근 파일 → 높은 엔트로피 (실험적, 외각)
    - 중간 크기 + 중간 시간 → 중간 엔트로피
    """
    # 크기 요소: 큰 파일 = 축적된 리듬 = 낮은 엔트로피
    size_factor = 1.0 - min(1.0, math.log1p(size / 1000) / 12)
    
    # 시간 요소: 오래된 파일 = 안정적 = 낮은 엔트로피
    days_ago = (now - mtime).total_seconds() / 86400
    time_factor = 1.0 - min(1.0, days_ago / 90)  # 90일 이상이면 최소
    
    # 결합: 두 요소의 가중 평균
    entropy = (size_factor * 0.4) + (time_factor * 0.6)
    return max(0.01, min(0.99, entropy))


def run_sonar(
    workspace_roots: List[Path],
    hippocampus_path: Path,
    max_files: int = 500,
) -> Dict[str, Any]:
    """소나 실행: 워크스페이스 스캔 → Vibe 추출 → 궤도 등록
    
    Returns:
        소나 결과 요약
    """
    hippo = FibonacciOrbitalHippocampus(hippocampus_path)
    now = datetime.now()
    
    registered = 0
    skipped = 0
    phase_counts = {"FLOW": 0, "EXPANSION": 0, "CONTRACTION": 0, "VOID": 0}
    
    for root in workspace_roots:
        if not root.exists():
            continue
        
        count = 0
        for ext in SCAN_EXTENSIONS:
            for path in root.rglob(f"*{ext}"):
                # 무시 디렉토리
                try:
                    parts = path.relative_to(root).parts
                except ValueError:
                    continue
                if any(p in IGNORE_DIRS for p in parts):
                    continue
                
                try:
                    stat = path.stat()
                except (PermissionError, OSError):
                    continue
                
                # Vibe 추출 (내용 읽지 않음)
                name = path.stem
                relpath = str(path.relative_to(root))
                phase = estimate_phase(name, relpath)
                entropy = estimate_entropy(stat.st_size, 
                                           datetime.fromtimestamp(stat.st_mtime), now)
                
                vibe = {
                    "entropy": entropy,
                    "phase": phase,
                    "top_keywords": [name.lower()],
                }
                
                # 궤도에 등록 (파일 경로를 content_ref로)
                hippo.register_experience(vibe, content_ref=str(path))
                registered += 1
                phase_counts[phase] += 1
                
                count += 1
                if count >= max_files:
                    break
            if count >= max_files:
                break
    
    summary = hippo.get_summary()
    
    return {
        "registered": registered,
        "skipped": skipped,
        "phase_distribution": phase_counts,
        "hippocampus_summary": summary,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    print("🔊 Vibe Sonar — 소나 시스템")
    print("=" * 50)
    print("파일 내용을 읽지 않습니다 — 메타데이터만으로 Vibe를 느낍니다")
    print()
    
    # 대지 설정
    ws1 = Path("C:/workspace")
    ws2 = Path("C:/workspace2")
    roots = [r for r in [ws2, ws1] if r.exists()]
    
    print(f"🌍 대지: {', '.join(str(r) for r in roots)}")
    
    # 해마 경로
    hippo_path = ws2 / "shion" / "outputs" / "fibonacci_orbital_hippocampus.json"
    
    print(f"🧠 해마: {hippo_path}")
    print()
    
    # 소나 실행
    result = run_sonar(roots, hippo_path, max_files=300)
    
    print(f"\n{'=' * 50}")
    print(f"📊 소나 결과:")
    print(f"   등록: {result['registered']}개 Vibe 지문")
    print(f"   위상 분포:")
    for phase, count in result['phase_distribution'].items():
        bar = "█" * (count // 5)
        print(f"     {phase:15s} {count:4d}개 {bar}")
    print(f"   해마 상태: {result['hippocampus_summary']}")
