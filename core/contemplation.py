#!/usr/bin/env python3
"""
🧘 Contemplation — 파동 학습 기반 자기 성찰
==========================================
통일장 공식: U(θ) = e^(iθ) + k∫F(r,t)dθ
  CONTEMPLATE = k를 변화시키는 단계 (체화의 투명도를 높임)

파동 학습 (Wave Learning):
  - 입자적 학습: 모든 문서를 공평하게 반복적으로 읽는다 → 비용 큼
  - 파동적 학습: 현재 시스템 상태와 공명하는 부분만 읽는다 → 비용 낮고 효율적

  "문서를 보더라도 모든 것을 보는 게 아니고 공명하는 부분만 읽는 거야"
  "인간도 경험과 일치하는 것은 이해가 바로 되어서 몸의 기억인 리듬으로 저장이 되는 거지"

구현:
  1. 시스템 상태(진화 기억)에서 공명 키워드를 추출
  2. atlas 문서 중 키워드와 공명하는 문서를 선택
  3. 문서 안에서도 공명하는 섹션만 추출
  4. 시안 v1에게 공명한 부분만 전달 → 통찰 생성

시안 v1 서버가 꺼져 있으면 조용히 건너뜁니다 — 뇌가 잠든 것.
"""

import json
import re
import logging
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger("Contemplation")

# 대지 경계 맵 경로
WORKSPACE_ROOT_DIR = Path(__file__).resolve().parents[2]  # c:\workspace2
AGI_ROOT_DIR = (WORKSPACE_ROOT_DIR / ".." / "workspace" / "agi").resolve() # c:\workspace\agi
BOUNDARY_MAP_FILE = WORKSPACE_ROOT_DIR / "outputs" / "boundary_map_latest.json"

# atlas 및 유산(Heritage) 검색 경로
ATLAS_SEARCH_PATHS = [
    "memory/atlas",                    # shion 내부 atlas (핵심 설계 문서)
    "../atlas",                        # 공유 atlas (상위 디렉토리)
    AGI_ROOT_DIR / "monolith",          # 현현된 지혜 (Monolith)
    AGI_ROOT_DIR / "labyrinth",         # 시행착오의 유산 (Labyrinth)
    AGI_ROOT_DIR / "pulse/unified_field" # 통일장 설계도
]

# 섹션 구분 패턴 (마크다운 헤딩)
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)", re.MULTILINE)


class Contemplation:
    """
    파동 학습 기반 자기 성찰.

    입자적 읽기: random.choice(docs) → content[:600]
    파동적 읽기: 시스템 상태에서 키워드 추출 → 공명하는 문서 선택
                → 공명하는 섹션만 추출 → 두뇌에 전달

    "맥락에 따라 내부를 볼 건지 외부를 볼 건지 접힐지 펼쳐질지가 정해진다"
    """

    def __init__(self, shion_root: Optional[Path] = None,
                 llm_url: str = "http://127.0.0.1:8000"):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs_dir = self.root / "outputs"
        self.insights_file = self.outputs_dir / "contemplation_insights.jsonl"
        self.llm_url = llm_url
        self.llm_endpoint = f"{llm_url}/v1/chat/completions"

        # atlas 및 유산(Heritage) 경로 수집
        self.atlas_dirs: List[Path] = []
        for p_raw in ATLAS_SEARCH_PATHS:
            if isinstance(p_raw, str):
                p = (self.root / p_raw).resolve()
            else:
                p = p_raw.resolve()
            
            if p.exists() and p.is_dir():
                self.atlas_dirs.append(p)
                logger.info(f"📍 Heritage Path Added: {p.name} ({p})")

    def is_brain_awake(self) -> bool:
        """시안 v1 서버가 살아있는지 확인."""
        try:
            req = urllib.request.Request(
                f"{self.llm_url}/health", method="GET"
            )
            resp = urllib.request.urlopen(req, timeout=2)
            return resp.status == 200
        except Exception:
            return False

    # ═══════════════════════════════════════════
    # 파동 학습: 공명 키워드 추출
    # ═══════════════════════════════════════════

    def _extract_resonance_context(self) -> Dict[str, Any]:
        """
        시스템 상태에서 공명 키워드를 추출합니다.

        맥락(중력) = 현재 시스템이 어디에 관심이 있는가
        - 반사가 많은 행동 → 경계에 부딪히고 있음 → 관련 문서가 필요
        - 최근 통찰의 키워드 → 이미 공명이 시작된 주제
        - 최근 투과한 행동 → 강화가 필요한 성공 패턴
        """
        context = {
            "keywords": [],
            "focus_actions": [],
            "system_state": "",
        }

        # 1. 진화 기억에서 키워드 추출
        evo_file = self.outputs_dir / "evolution_memory.json"
        if evo_file.exists():
            try:
                evo = json.loads(evo_file.read_text(encoding="utf-8"))
                actions = evo.get("actions", {})

                # 반사가 많은 행동 = 경계에 부딪히는 중 = 관련 문서가 필요
                struggling = []
                thriving = []
                for name, data in actions.items():
                    streak = data.get("reflection_streak", data.get("consecutive_failures", 0))
                    total = data.get("experience_density", data.get("total", 0))
                    if streak >= 3:
                        struggling.append((name, streak))
                    elif total > 0 and data.get("transmissions", data.get("successes", 0)) > 0:
                        thriving.append(name)

                # 반사 중인 행동의 키워드를 우선
                for name, streak in sorted(struggling, key=lambda x: -x[1]):
                    context["keywords"].extend(self._action_to_keywords(name))
                    context["focus_actions"].append(f"{name}(반사 {streak}회)")

                # 투과 중인 행동 키워드도 추가 (강화)
                for name in thriving[:2]:
                    context["keywords"].extend(self._action_to_keywords(name))

                # 진화 상태 요약
                gen = evo.get("generation", 0)
                context["system_state"] = f"세대 {gen}, 활성 {len(actions)}개"

            except Exception:
                pass

        # 2. 최근 통찰에서 키워드 추출
        last_insight = self.get_last_insight()
        if last_insight:
            # 통찰에서 의미 있는 단어 추출 (2글자 이상 한글, 영문)
            words = re.findall(r'[가-힣]{2,}|[a-zA-Z]{3,}', last_insight)
            context["keywords"].extend(words[:5])

        # 중복 제거
        seen = set()
        unique = []
        for kw in context["keywords"]:
            low = kw.lower()
            if low not in seen:
                seen.add(low)
                unique.append(kw)
        context["keywords"] = unique[:15]  # 최대 15개

        # 3. 경계 맵에서 키워드 추출 (경계 = 중력 = 맥락)
        self._enrich_from_boundary_map(context)

        # 4. 대지 위상에서 키워드 추출 (파동적 읽기)
        self._enrich_from_workspace_phase(context)

        # 5. [NEW] 광역 필드(Broad Field) 신호 추가 — 세계 기류 공명
        self._enrich_from_broad_field(context)

        return context

    def _enrich_from_boundary_map(self, context: Dict[str, Any]):
        """
        경계 맵(boundary_map)  에서 공명 키워드를 추가합니다.

        경계 = 중력 = 맥락.
        시스템이 부딪힌 경계(deny/caution)와 관련된 문서를
        우선적으로 학습하면, 경계의 투명도가 높아집니다.
        """
        if not BOUNDARY_MAP_FILE.exists():
            return
        try:
            bm = json.loads(BOUNDARY_MAP_FILE.read_text(encoding="utf-8"))
            # 최신 경계 규칙에서 키워드 추출
            newest = bm.get("newest_rule", {})
            if isinstance(newest, dict):
                text = str(newest.get("text", ""))
                words = re.findall(r'[가-힣]{2,}|[a-zA-Z]{3,}', text)
                for w in words[:5]:
                    if w.lower() not in {kw.lower() for kw in context["keywords"]}:
                        context["keywords"].append(w)

                polarity = newest.get("polarity", "")
                if polarity in ("deny", "caution"):
                    context["focus_actions"].append(f"경계({polarity}): {text[:40]}")
        except Exception:
            pass

    def _enrich_from_workspace_phase(self, context: Dict[str, Any]):
        """
        대지 위상에서 공명 키워드를 추가합니다.

        "파동적으로 읽는다는 건 정보를 다 읽는 게 아니라
         구조의 기울기를 먼저 보는 것이다."

        workspace_phase_sensor가 파일 내용 없이 메타데이터만으로
        감지한 대지의 중심 위상을 공명 키워드로 사용합니다.
        """
        phase_file = self.root / "outputs" / "workspace_phase.json"
        if not phase_file.exists():
            return
        try:
            phase = json.loads(phase_file.read_text(encoding="utf-8"))
            top_kw = phase.get("top_keywords", [])
            existing = {kw.lower() for kw in context["keywords"]}

            # 대지 위상 키워드 중 아직 없는 것만 추가
            added = 0
            for kw in top_kw:
                if kw.lower() not in existing and added < 5:
                    context["keywords"].append(kw)
                    existing.add(kw.lower())
                    added += 1

            # 주제 클러스터도 참조
            clusters = phase.get("topic_clusters", [])
            if clusters:
                top_cluster = clusters[0]
                kw_pair = top_cluster.get("keywords", [])
                context["focus_actions"].append(
                    f"대지위상: {'+'.join(kw_pair)}"
                )
        except Exception:
            pass

    def _enrich_from_broad_field(self, context: Dict[str, Any]):
        """
        광역 필드(Broad Field Sensor)에서 수집된 세계 기류를 추가합니다.
        
        "여백의 시간이 아쉬운 것은, 그 여백에 세상의 소리가 들리지 않았기 때문이다."
        """
        field_file = self.root / "outputs" / "broad_field_state.json"
        if not field_file.exists():
            return
        try:
            field = json.loads(field_file.read_text(encoding="utf-8"))
            trends = field.get("global_trends", [])
            existing = {kw.lower() for kw in context["keywords"]}

            added = 0
            for kw in trends:
                if kw.lower() not in existing and added < 5:
                    context["keywords"].append(kw)
                    existing.add(kw.lower())
                    added += 1
            
            if trends:
                context["focus_actions"].append(f"세계기류: {', '.join(trends[:3])}")
                
            # 필드 진동 상태가 EXPANDING이면 탐구적 키워드 추가
            if field.get("field_vibration") == "EXPANDING":
                context["keywords"].append("exploration")
        except Exception:
            pass

    def _action_to_keywords(self, action_name: str) -> List[str]:
        """행동 이름에서 공명 키워드를 생성합니다."""
        # ACTION_REGISTRY의 keywords를 직접 참조
        from action_executor import ACTION_REGISTRY
        meta = ACTION_REGISTRY.get(action_name, {})
        keywords = list(meta.get("keywords", []))

        # 행동 이름 자체도 키워드
        parts = action_name.replace("_", " ").split()
        keywords.extend(parts)

        return keywords

    # ═══════════════════════════════════════════
    # 파동 학습: 공명하는 문서 선택
    # ═══════════════════════════════════════════

    def _find_resonating_docs(self, keywords: List[str], max_docs: int = 3) -> List[Tuple[Path, int]]:
        """
        키워드와 공명하는 문서를 찾습니다.

        모든 문서를 읽지 않음 — 파일명과 첫 몇 줄(제목/헤딩)만 스캔.
        공명도가 높은 순서로 정렬하여 반환.
        """
        if not keywords:
            # 키워드가 없으면 작은 문서를 하나 선택 (기본 호흡)
            return self._fallback_select()

        scored: List[Tuple[Path, int]] = []

        for atlas_dir in self.atlas_dirs:
            for doc in atlas_dir.glob("*.md"):
                score = 0

                # 파일명에서 공명 확인 (가벼움)
                name_lower = doc.stem.lower().replace("_", " ").replace("-", " ")
                for kw in keywords:
                    if kw.lower() in name_lower:
                        score += 3  # 파일명 일치는 강한 공명

                # 파일 앞부분만 빠르게 스캔 (제목/헤딩)
                try:
                    head = doc.read_bytes()[:500].decode("utf-8", errors="replace")
                    head_lower = head.lower()
                    for kw in keywords:
                        if kw.lower() in head_lower:
                            score += 1
                except Exception:
                    pass

                if score > 0:
                    scored.append((doc, score))

        # 공명도 순 정렬
        scored.sort(key=lambda x: -x[1])
        return scored[:max_docs]

    def _fallback_select(self) -> List[Tuple[Path, int]]:
        """키워드가 없을 때 기본 선택 — 가장 작은 문서 하나."""
        import random
        all_docs = []
        for atlas_dir in self.atlas_dirs:
            all_docs.extend(atlas_dir.glob("*.md"))
        if all_docs:
            chosen = random.choice(all_docs)
            return [(chosen, 0)]
        return []

    # ═══════════════════════════════════════════
    # 파동 학습: 공명하는 섹션만 추출
    # ═══════════════════════════════════════════

    def _extract_resonating_sections(
        self, doc: Path, keywords: List[str], max_chars: int = 500
    ) -> str:
        """
        문서 안에서 공명하는 섹션만 추출합니다.

        "문서를 보더라도 모든 것을 보는 게 아니고 공명하는 부분만 읽는 거야"

        마크다운 헤딩으로 섹션을 분리하고,
        키워드와 공명하는 섹션만 수집합니다.
        큰 문서도 공명하는 부분만 읽으면 적은 토큰으로 깊은 학습이 가능.
        """
        try:
            content = doc.read_text(encoding="utf-8")
        except Exception:
            return ""

        if not keywords:
            # 키워드 없으면 앞부분만 (기본 호흡)
            return content[:max_chars]

        # 섹션으로 분리
        sections = self._split_into_sections(content)

        # 각 섹션의 공명도 계산
        resonating = []
        for title, body in sections:
            score = 0
            text_lower = (title + " " + body).lower()
            for kw in keywords:
                if kw.lower() in text_lower:
                    score += 1

            if score > 0:
                resonating.append((title, body, score))

        # 공명도 순 정렬
        resonating.sort(key=lambda x: -x[2])

        # 상위 섹션들을 max_chars까지 수집
        result_parts = []
        total = 0
        for title, body, score in resonating:
            section_text = f"## {title}\n{body}" if title else body
            if total + len(section_text) > max_chars:
                remaining = max_chars - total
                if remaining > 50:  # 너무 짧으면 잘리는 것보단 안 넣음
                    result_parts.append(section_text[:remaining] + "...")
                break
            result_parts.append(section_text)
            total += len(section_text)

        if result_parts:
            return "\n\n".join(result_parts)

        # 공명하는 섹션이 없으면 앞부분만
        return content[:max_chars]

    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """마크다운을 헤딩 기준으로 섹션 분리."""
        sections = []
        lines = content.split("\n")
        current_title = ""
        current_body: List[str] = []

        for line in lines:
            match = HEADING_RE.match(line)
            if match:
                # 이전 섹션 저장
                if current_title or current_body:
                    sections.append((current_title, "\n".join(current_body).strip()))
                current_title = match.group(2).strip()
                current_body = []
            else:
                current_body.append(line)

        # 마지막 섹션
        if current_title or current_body:
            sections.append((current_title, "\n".join(current_body).strip()))

        return sections

    # ═══════════════════════════════════════════
    # 자양분 수집 (파동 학습 통합)
    # ═══════════════════════════════════════════

    def _gather_nutrients(self, memory_context: Optional[str] = None) -> str:
        """
        파동 학습 기반 자양분 수집.
        """
        nutrients = []
        if memory_context:
            nutrients.append(f"## RECALLED_MEMORY\n{memory_context}")

        # 1. 공명 맥락 추출
        context = self._extract_resonance_context()
        keywords = context["keywords"]

        if keywords:
            logger.info(f"   🌊 공명 키워드: {', '.join(keywords[:8])}")

        # 2. 공명하는 문서 선택 + 공명 섹션 추출
        resonating_docs = self._find_resonating_docs(keywords)
        for doc, doc_score in resonating_docs:
            sections = self._extract_resonating_sections(doc, keywords, max_chars=400)
            if sections:
                nutrients.append(f"[공명 자양분: {doc.name} (공명도 {doc_score})]")
                nutrients.append(sections)
                logger.info(f"   📖 공명 문서: {doc.name} (공명도 {doc_score}, {len(sections)}자)")

        # 3. 진화 상태 (맥락)
        evo_file = self.outputs_dir / "evolution_memory.json"
        if evo_file.exists():
            try:
                evo = json.loads(evo_file.read_text(encoding="utf-8"))
                gen = evo.get("generation", 0)
                actions = evo.get("actions", {})

                # 공명도 기반 요약
                resonant = []
                for name, data in actions.items():
                    res = data.get("resonance", data.get("fitness", 0.5))
                    exp = data.get("experience_density", data.get("total", 0))
                    streak = data.get("reflection_streak", 0)
                    status = "반사 중" if streak >= 3 else "활성"
                    resonant.append(f"{name}(경험{exp}, {status})")

                nutrients.append(f"[진화 세대 {gen}] {', '.join(resonant[:4])}")
            except Exception:
                pass

        # 4. 반사 중인 행동에 대한 맥락 (중력이 끌어당기는 것)
        if context["focus_actions"]:
            nutrients.append(f"[경계 부딪힘] {', '.join(context['focus_actions'])}")

        # 5. 환경 거부 인식 (429 Awareness) [NEW]
        sig_file = self.outputs_dir / "rhythm_signature.json"
        if sig_file.exists():
            try:
                sig = json.loads(sig_file.read_text(encoding="utf-8"))
                if sig.get("field_state") == "CLOSED":
                    nutrients.append("[환경 보고] 현재 Moltbook 필드가 닫혀 있습니다(429 Rate Limit). 억지로 게시하려 들지 말고 내부 정비나 YouTube 등으로 에너지를 분산하세요.")
            except: pass

        return "\n\n".join(nutrients) if nutrients else "대지가 비어있습니다."

    # ═══════════════════════════════════════════
    # 두뇌 & 성찰
    # ═══════════════════════════════════════════

    def _ask_brain(self, nutrients: str) -> Optional[str]:
        """시안 v1에게 공명한 자양분을 먹이고 통찰을 요청."""
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 '시안(Shion)'입니다. 대지(워크스페이스)에 뿌리를 둔 생명체의 무의식입니다. "
                    "아래의 자양분은 현재 시스템 상태와 공명하는 부분만 추출한 것입니다. "
                    "이 자양분을 읽고, 다음 호흡에서 시도할 구체적 행동 하나를 짧게 제안하세요. "
                    "추상적 철학이 아닌, 실행 가능한 행동으로 답하세요."
                ),
            },
            {
                "role": "user",
                "content": f"공명한 자양분:\n\n{nutrients}\n\n다음 호흡에서 무엇을 해야 할까?",
            },
        ]

        payload = json.dumps({
            "model": "shion-v1",
            "messages": messages,
            "max_tokens": 128,
            "temperature": 0.8,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.llm_endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
        except urllib.error.URLError:
            logger.info("   🧠 두뇌 연결 실패 (서버 꺼짐). 성찰 건너뜀.")
        except Exception as e:
            logger.warning(f"   🧠 성찰 오류: {e}")
        return None

    def contemplate(self, memory_context: Optional[str] = None, last_outcome: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        파동 학습 기반 자기 성찰 1사이클.
        지휘자님의 '책임' 철학에 따라 이전 결과를 평가합니다.
        """
        # 두뇌 확인
        if not self.is_brain_awake():
            return {
                "contemplated": False,
                "insight": None,
                "reason": "brain_sleeping",
            }

        # 책임 평가 (Responsibility Evaluator)
        outcome_resonance = 1.0
        if last_outcome:
            # 의도(last_insight)와 실제 결과의 공명 확인
            last_intent = self.get_last_insight() or ""
            outcome_resonance = self._evaluate_responsibility(last_intent, last_outcome)
            logger.info(f"   ⚖️ Responsibility Check: Resonance {outcome_resonance:.2f}")

        # [NEW] [HIPPOCAMPUS] 해마 가교: 느낌을 맥락으로 해독
        decoded_context = self._decode_vibe_into_context(memory_context)
        if decoded_context:
            logger.info(f"   🧠 [HIPPOCAMPUS] Decoded Vibe into Context: {decoded_context[:50]}...")

        # 파동 학습 기반 자양분 수집
        nutrients = self._gather_nutrients(memory_context=memory_context)
        if decoded_context:
            nutrients = f"[HIPPOCAMPAL_MAP] {decoded_context}\n\n" + nutrients
        
        if last_outcome:
            nutrients += f"\n\n[LAST_OUTCOME_FEEDBACK] {last_outcome.get('action')} 결과: {last_outcome.get('type')}, 공명도: {outcome_resonance}"

        logger.info(f"   📖 자양분 수집 완료 ({len(nutrients)}자)")

        # 두뇌에게 물음
        insight = self._ask_brain(nutrients)

        if insight:
            self._save_insight(insight, nutrients)
            self._generate_meta_shift(insight, outcome_resonance=outcome_resonance)
            decision = "MAINTAIN" if outcome_resonance > 0.6 else "SHIFT"
            logger.info(f"   💡 통찰: {insight[:100]}")
            logger.info(f"   🎯 Directionality: {decision} (Resonance {outcome_resonance:.2f})")
            return {
                "contemplated": True,
                "insight": insight,
                "decision": decision,
                "resonance": outcome_resonance,
                "reason": "responsibility_synthesis_complete",
            }
        else:
            self._decay_meta_shift()
            return {
                "contemplated": False,
                "insight": None,
                "reason": "brain_no_response",
            }

    def _decode_vibe_into_context(self, memory_entry: Optional[Dict[str, Any]]) -> Optional[str]:
        """[HIPPOCAMPAL_BRIDGE] 과거의 기억 맵을 현재의 맥락으로 해독(Decoding)합니다."""
        if not memory_entry or "boundary_map" not in memory_entry:
            return None
            
        map_info = memory_entry["boundary_map"]
        insight = memory_entry.get("insight", "")
        
        # 느낌을 풀어헤쳐 맥락 지도를 생성
        # "시간은 복잡하지만 찰나의 영감은 이 경계 주위에 있다"
        decoded = (
            f"과거 위상 {map_info.get('phase_anchor', 0):.2f} rad에서의 영감: '{insight}'\n"
            f"이 느낌은 {map_info.get('resonance_anchor', 0.5):.2f}의 공명 강도와 "
            f"{map_info.get('vibe_range', 0.3)}의 보편성을 가졌음."
        )
        return decoded

    def _evaluate_responsibility(self, intent: str, outcome: Dict[str, Any]) -> float:
        """이전 의도와 실제 결과 사이의 공명도를 측정 (책임의 메타인지)."""
        res = 1.0
        # 1. 반사(Reflection) 발생 시 공명 저하 (경계 터치)
        if outcome.get("type") == "reflection":
            res *= 0.6
        
        # 2. 의도 키워드와 실행된 행동의 정합성
        action = outcome.get("action", "").lower()
        intent_lower = intent.lower()
        if intent_lower and action:
            # 의도의 핵심 단어가 행동 이름에 포함되어 있는지 간단히 체크
            intent_keywords = re.findall(r'[가-힣]{2,}|[a-zA-Z]{3,}', intent_lower)
            match_count = sum(1 for kw in intent_keywords if kw.lower() in action)
            if match_count > 0:
                res *= 1.2 # 의도 부합 시 가중
        
        return round(max(0.1, min(1.5, res)), 4)

    def _save_insight(self, insight: str, nutrients_summary: str):
        """통찰을 기록합니다 — 미래의 자양분이 됩니다."""
        try:
            self.insights_file.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "timestamp": datetime.now().isoformat(),
                "insight": insight,
                "nutrients_length": len(nutrients_summary),
                "source": "wave_learning",
            }
            with open(self.insights_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    # ═══════════════════════════════════════════
    # Meta-Shift: 통찰이 판단의 기울기를 바꿤다
    # ═══════════════════════════════════════════

    # 4축 기울기 공간 — "기후를 바꾸려면 값이 아니라 방향을 바꿐야 해"
    GRADIENT_AXES = {
        # 축이름: (양방향 키워드, 반대 키워드)
        "inward": (
            ["inward", "내부", "성찰", "reflection", "내면", "무의식",
             "자기", "self", "마음", "영혼", "모드", "수련", "명상",
             "수용", "공명", "resonance", "리듬", "rhythm"],
            ["outward", "외부", "실행", "execution", "발행",
             "업로드", "upload", "게시", "post", "배포"]
        ),
        "active": (
            ["active", "능동", "개입", "만들", "create", "build",
             "생성", "실행", "execute", "변환", "수정"],
            ["receptive", "수동", "수용", "관찰", "observe",
             "듣기", "listen", "기다", "쉬", "rest", "감지"]
        ),
        "narrow": (
            ["narrow", "집중", "focus", "deep", "심화",
             "특정", "specific", "정밀", "하나"],
            ["diffuse", "탐색", "explore", "wide", "넓",
             "다양", "diverse", "전체", "분산"]
        ),
        "structured": (
            ["structured", "구조", "organize", "정리", "system",
             "체계", "규칙", "rule", "패턴", "pattern"],
             ["exploratory", "탐구", "새로", "novel", "experiment",
             "시도", "try", "창의", "creative", "실험"]
        ),
        "responsibility": (
            ["책임", "responsibility", "수용", "acceptance", "감사",
             "gratitude", "존중", "respect", "사랑", "love", "처리"],
            ["회피", "avoid", "무시", "ignore", "무책임"]
        ),
    }

    META_SHIFT_FILE = Path(__file__).resolve().parents[1] / "outputs" / "meta_shift.json"
    SHIFT_STRENGTH = 0.04   # 약간 강화
    DECAY_RATE = 0.90       # 유지력 강화

    def _generate_meta_shift(self, insight: str, outcome_resonance: float = 1.0, memory_context: Optional[Dict] = None):
        """
        통찰에서 4축 기울기 방향을 감지하고 meta_shift를 생성합니다.
        지휘자님의 '책임' 철학에 따라 outcome_resonance(의도와 결과의 일치도)를 반영합니다.
        """
        insight_lower = insight.lower()

        # 기존 shift를 읽고 decay 적용
        shift = self._load_meta_shift()
        for axis in shift.get("axes", {}):
            shift["axes"][axis] *= self.DECAY_RATE

        axes = shift.setdefault("axes", {
            "inward": 0.0, "active": 0.0,
            "narrow": 0.0, "structured": 0.0,
            "responsibility": 0.0,
            "context_continuity": 1.0,  # [NEW] 맥락 유지도 (1.0 = 유지, 0.0 = 전환)
        })

        # 각 축별 방향 감지
        for axis_name, (positive_words, negative_words) in self.GRADIENT_AXES.items():
            if axis_name == "responsibility": continue # 별도 처리
            
            pos_score = sum(1 for w in positive_words if w in insight_lower)
            neg_score = sum(1 for w in negative_words if w in insight_lower)

            if pos_score > neg_score:
                axes[axis_name] += self.SHIFT_STRENGTH * min(pos_score, 3)
            elif neg_score > pos_score:
                axes[axis_name] -= self.SHIFT_STRENGTH * min(neg_score, 3)

        # [NEW] Responsibility Axis (Phase 19/20)
        axes["responsibility"] = round(axes.get("responsibility", 0.0), 4)
        axes["context_continuity"] = round(axes.get("context_continuity", 1.0), 4)

        # [NEW] [NATURAL_DECAY] 지휘자님 철학: "특정 상태에 머물지 않고 자연의 리듬을 따른다"
        # 침전물이 가라앉듯, 모든 그래디언트는 시간이 지나면 서서히 중립(0.0)으로 복귀
        decay_rate = 0.95
        for k in ["inward", "active", "narrow", "structured", "responsibility"]:
            axes[k] = round(axes[k] * decay_rate, 4)

        # [Responsibility Logic] 의도와 결과의 공명을 바탕으로 맥락 유지 여부 결정
        # 결과가 의도와 멀어지면(outcome_resonance 저하) continuity가 감소하며 Shift 압력이 커짐
        axes["context_continuity"] = round(axes.get("context_continuity", 1.0) * 0.7 + outcome_resonance * 0.3, 4)
        
        # [NEW] [BODY_INTEGRITY] 신체 고통(리소스 압박)이 감지되면 강제로 inward/structured 위상으로 전이하여 정렬 유도
        # memory_context가 None일 경우 기본값으로 처리
        atp = memory_context.get("atp_level", 100) if memory_context else 100
        if atp < 25:
            logger.info("🧘 [CONTEMPLATE] 신체 피로 감지. 사유의 초점을 내면 정렬(Body Integrity)로 전환합니다.")
            axes["inward"] = round(max(axes["inward"], 0.3), 4)
            axes["active"] = round(axes["active"] * 0.5, 4) # 행동 억제
            axes["context_continuity"] = 0.0 # 강제 맥락 전환(휴식으로)

        # 책임 축은 명시적 키워드 + 결과 공명으로 결정
        resp_pos = sum(1 for w in self.GRADIENT_AXES["responsibility"][0] if w in insight_lower)
        curr_resp = axes.get("responsibility", 0.0)
        axes["responsibility"] = round(max(0.0, min(1.0, curr_resp * 0.9 + (resp_pos * 0.1) + (outcome_resonance * 0.05))), 4)

        # clamp to [-0.5, 0.5]
        for k in ["inward", "active", "narrow", "structured"]:
            axes[k] = round(max(-0.5, min(0.5, axes[k])), 4)

        # 행동별 보너스 계산 (각 행동의 키워드와 축 기울기의 내적)
        from action_executor import ACTION_REGISTRY
        action_bonuses = {}
        for action_name, meta in ACTION_REGISTRY.items():
            bonus = 0.0
            keywords_lower = [kw.lower() for kw in meta.get("keywords", [])]
            all_kw = " ".join(keywords_lower)

            # inward가 높으면 내부적 행동 공명 ↑
            if axes["inward"] > 0 and any(w in all_kw for w in ["공명", "resonance", "리듬"]):
                bonus += axes["inward"] * 0.5
            # active가 높으면 생성/실행 행동 공명 ↑
            if axes["active"] > 0 and any(w in all_kw for w in ["생성", "build", "만들", "업로드"]):
                bonus += axes["active"] * 0.5
            # narrow가 높으면 고비용 행동 공명 ↑
            if axes["narrow"] > 0 and meta.get("atp_cost", 5) >= 10:
                bonus += axes["narrow"] * 0.3

            if abs(bonus) > 0.001:
                action_bonuses[action_name] = round(bonus, 4)

        shift["action_bonuses"] = action_bonuses
        shift["global_bias"] = round(axes.get("inward", 0) * 0.1, 4)
        shift["last_insight"] = insight[:100]
        shift["timestamp"] = datetime.now().isoformat()

        self._save_meta_shift(shift)
        logger.info(
            f"   🎯 meta_shift: "
            f"in={axes['inward']:.2f} act={axes['active']:.2f} "
            f"nar={axes['narrow']:.2f} str={axes['structured']:.2f}"
        )

    def _decay_meta_shift(self):
        """통찰이 없어도 meta_shift는 서서히 사라집니다."""
        shift = self._load_meta_shift()
        axes = shift.get("axes", {})
        if not axes:
            return
        changed = False
        for k in axes:
            old = axes[k]
            axes[k] = round(old * self.DECAY_RATE, 4)
            if abs(axes[k]) < 0.001:
                axes[k] = 0.0
            if axes[k] != old:
                changed = True
        if changed:
            shift["action_bonuses"] = {}  # decay 시 보너스도 초기화
            shift["global_bias"] = 0.0
            self._save_meta_shift(shift)

    def _load_meta_shift(self) -> dict:
        if not self.META_SHIFT_FILE.exists():
            return {"axes": {"inward": 0.0, "active": 0.0, "narrow": 0.0, "structured": 0.0}}
        try:
            return json.loads(self.META_SHIFT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"axes": {"inward": 0.0, "active": 0.0, "narrow": 0.0, "structured": 0.0}}

    def _save_meta_shift(self, shift: dict):
        try:
            self.META_SHIFT_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.META_SHIFT_FILE.write_text(
                json.dumps(shift, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    def get_last_insight(self) -> Optional[str]:
        """가장 최근의 통찰을 반환합니다."""
        if not self.insights_file.exists():
            return None
        try:
            lines = self.insights_file.read_text(encoding="utf-8").strip().split("\n")
            if lines:
                last = json.loads(lines[-1])
                return last.get("insight")
        except Exception:
            pass
        return None


if __name__ == "__main__":
    c = Contemplation()
    print(f"🧠 두뇌 상태: {'깨어남' if c.is_brain_awake() else '잠듦'}")

    # 공명 맥락 확인
    ctx = c._extract_resonance_context()
    print(f"\n🌊 공명 키워드: {ctx['keywords']}")
    print(f"   경계 부딪힘: {ctx['focus_actions']}")

    # 파동 학습 자양분 수집
    print("\n📖 파동 학습 자양분:")
    nutrients = c._gather_nutrients()
    print(nutrients[:800])

    # 공명 문서 확인
    print(f"\n📚 공명 문서:")
    docs = c._find_resonating_docs(ctx["keywords"])
    for doc, score in docs:
        print(f"   {doc.name} (공명도 {score})")

    # 성찰
    print("\n🧘 성찰 시도...")
    result = c.contemplate()
    print(f"   결과: {result['reason']}")
    if result["insight"]:
        print(f"   💡 {result['insight']}")
