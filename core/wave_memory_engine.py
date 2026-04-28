#!/usr/bin/env python3
"""
🌊 Wave Memory Engine (비유클리드 파동 기억 엔진)
==================================================
기존의 RAG(검색 증강 생성)처럼 키워드로 과거를 찾는 것이 아니라,
현재 시스템의 주파수(Vibe: 엔트로피, 위상)와 공명하는 과거의 기억을 건져 올립니다.

"데이터가 정지해 있을 때가 아니라 흐르고 있을 때, 
 그 흐름 속에서 정지한 데이터를 바라보는 것"
"""

import json
import logging
import math
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("WaveMemoryEngine")

class WaveMemoryEngine:
    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path

    def _calculate_vibe_distance(self, current_vibe: Dict[str, Any], log_vibe: Dict[str, Any]) -> float:
        """두 파동 간의 비유클리드 거리를 계산합니다. (거리가 0에 가까울수록 공명)"""
        # 1. Entropy Distance (연속형 값의 유클리드 거리)
        curr_ent = current_vibe.get("entropy", 0.0)
        log_ent = log_vibe.get("entropy", 0.0)
        ent_dist = abs(curr_ent - log_ent)

        # 2. Phase Distance (카테고리형 값의 이산 거리)
        curr_phase = current_vibe.get("phase", "UNKNOWN")
        log_phase = log_vibe.get("phase", "UNKNOWN")
        phase_dist = 0.0 if curr_phase == log_phase else 0.5

        # 3. Keyword Resonance (교집합)
        curr_kw = set(current_vibe.get("top_keywords", []))
        log_kw = set(log_vibe.get("top_keywords", []))
        resonance_bonus = len(curr_kw.intersection(log_kw)) * 0.1

        # 최종 거리 (작을수록 공명도가 높음)
        # 기본 거리에 보너스를 뺌 (거리가 음수가 되지 않도록 max 처리)
        total_dist = max(0.0, (ent_dist + phase_dist) - resonance_bonus)
        return total_dist

    def _retroactive_vibe_infer(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """과거 데이터에 vibe_signature가 없는 경우, 데이터의 속성으로 파동을 추론합니다."""
        length = entry.get("length", 0)
        content = entry.get("content_summary", "")
        
        # 텍스트 길이나 내용으로 대략적인 엔트로피/위상 추론 (임시 척도)
        inferred_entropy = min(1.0, length / 4000.0)  # 긴 글일수록 엔트로피(복잡도)가 높다고 가정
        
        inferred_phase = "FLOW"
        if "심연" in content or "Void" in content:
            inferred_phase = "VOID"
        elif "팽창" in content or length > 2000:
            inferred_phase = "EXPANSION"
        elif "수축" in content or length < 500:
            inferred_phase = "CONTRACTION"
            
        return {
            "entropy": inferred_entropy,
            "phase": inferred_phase,
            "top_keywords": []
        }

    def extract_resonant_memories(self, current_vibe: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        """현재 시스템의 Vibe와 가장 공명하는(거리가 가까운) 기억 조각들을 추출합니다."""
        if not self.ledger_path.exists():
            logger.warning(f"Resonance ledger not found at {self.ledger_path}")
            return []

        memories_with_distance = []
        
        try:
            # 레저에 멀티라인 JSON과 한 줄 JSON이 혼재할 수 있으므로
            # 전체 파일을 읽은 후 JSON 객체를 하나씩 추출합니다.
            content = self.ledger_path.read_text(encoding='utf-8')
            entries = self._parse_mixed_jsonl(content)
            
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                log_vibe = entry.get("vibe_signature")
                if not log_vibe:
                    log_vibe = self._retroactive_vibe_infer(entry)
                    
                distance = self._calculate_vibe_distance(current_vibe, log_vibe)
                memories_with_distance.append((distance, entry))
        except Exception as e:
            logger.error(f"Error reading ledger for resonance: {e}")
            
        # 거리가 가장 가까운(공명도가 가장 높은) 순서대로 정렬
        memories_with_distance.sort(key=lambda x: x[0])
        
        # 상위 K개 추출
        resonant_entries = [item[1] for item in memories_with_distance[:top_k]]
        return resonant_entries

    def _parse_mixed_jsonl(self, content: str) -> List[Dict[str, Any]]:
        """멀티라인 JSON과 한 줄 JSON이 혼재된 파일을 파싱합니다."""
        entries = []
        # 먼저 한 줄씩 시도
        buffer = ""
        brace_depth = 0
        
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
            
            # brace depth 추적
            brace_depth += stripped.count('{') - stripped.count('}')
            buffer += line + '\n'
            
            # brace가 닫히면 JSON 객체 하나 완성
            if brace_depth == 0 and buffer.strip():
                try:
                    entry = json.loads(buffer)
                    if isinstance(entry, dict):
                        entries.append(entry)
                except json.JSONDecodeError:
                    pass
                buffer = ""
        
        return entries
