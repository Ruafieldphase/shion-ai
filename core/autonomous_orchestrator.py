#!/usr/bin/env python3
"""
🎯 자율 오케스트레이터 — Autonomous Orchestrator
==================================================
비용 구조:
  세나 (Gemini):   설계/방향   → 가끔만 (토큰 절약)
  코덱스 (OpenAI): 검증       → 무료 버전 (필요할 때만)
  gemma4 (로컬):   실행       → 0원 (항상)

순환:
  해마(기울기) → 과제 생성 → gemma4 실행 → 결과 등록 → 반복

이 파일이 전체 시스템의 메인 루프입니다.
gemma4가 코딩/분석/정리를 하고,
해마가 방향을 잡고,
결과가 경험으로 쌓입니다.
"""

import json
import logging
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AutonomousOrchestrator")

try:
    from antigravity_hook import FermatResonanceHook
except ImportError:
    try:
        from core.antigravity_hook import FermatResonanceHook
    except ImportError:
        FermatResonanceHook = None

OLLAMA_URLS = ("http://localhost:8000", "http://localhost:11434")
OLLAMA_URL = OLLAMA_URLS[0]
FAST_MODEL = "gemma3:latest"    # 3.3GB — 평소: 빠르고 가벼움
DEEP_MODEL = "gemma4:e2b"      # 7.2GB — 몰입: 느리지만 깊음
VISION_MODEL = "moondream:latest"

# 과제 템플릿: 기울기 방향 → gemma4가 할 구체적 작업
GRADIENT_TASKS = {
    "warmth": {
        "goal": "시스템의 온기를 높이기 — 관계/소통/문서 개선",
        "tasks": [
            "최근 수정된 파일의 주석/문서를 더 따뜻하고 이해하기 쉽게 개선",
            "README나 문서 파일의 톤을 자연스럽게 수정",
            "코드의 변수명을 더 직관적으로 리팩토링 제안",
        ],
    },
    "intensity": {
        "goal": "에너지 균형 — 구조화/최적화/정리",
        "tasks": [
            "코드의 중복을 찾아서 정리 방법 제안",
            "성능이 느린 부분을 분석하고 최적화 방안 제시",
            "사용하지 않는 import나 dead code 찾기",
        ],
    },
    "complexity": {
        "goal": "복잡도 조율 — 단순화 또는 패턴 추출",
        "tasks": [
            "가장 복잡한 함수를 찾아서 분해 방법 제안",
            "반복되는 패턴을 유틸리티 함수로 추출",
            "설정값들을 상수로 정리",
        ],
    },
    "rhythm": {
        "goal": "리듬 통일 — 일관성/네이밍/스타일",
        "tasks": [
            "코딩 스타일이 불일치하는 부분 찾기",
            "네이밍 규칙 통일 제안",
            "로깅 형식 일관성 검토",
        ],
    },
    "balanced": {
        "goal": "균형 상태 — 관찰/요약/기록",
        "tasks": [
            "현재 시스템 상태 요약",
            "최근 변경사항 정리",
            "다음 작업 우선순위 제안",
        ],
    },
}


class AutonomousOrchestrator:
    """gemma4를 실행 엔진으로 사용하는 자율 오케스트레이터.
    
    해마가 방향을 잡으면, gemma4가 실행하고, 결과가 경험으로 쌓입니다.
    세나(설계)와 코덱스(검증)는 필요할 때만 호출합니다.
    """
    
    def __init__(self, hippocampus, experience_loop=None, vision=None):
        self.hippo = hippocampus
        self.exp_loop = experience_loop
        self.vision = vision
        self.ollama_url = OLLAMA_URL
        self.cycle_count = 0
        self.total_tokens_saved = 0  # 세나/코덱스 대신 gemma4가 처리한 토큰
        
        self.log_path = Path(r"c:\workspace2\shion\outputs\orchestrator_log.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.state_path = Path(r"c:\workspace2\shion\outputs\orchestrator_state.json")

        self.antigravity_hook = None
        if FermatResonanceHook is not None:
            self.antigravity_hook = FermatResonanceHook(Path(r"c:\workspace2\shion"))
            if self.antigravity_hook.graph:
                logger.info("   🌌 Antigravity Hook 활성 — 코드 분석 전 그래프 맥락 우선")

    def _resolve_ollama_url(self) -> str:
        """Use the first responsive local Ollama-compatible endpoint."""
        for url in OLLAMA_URLS:
            try:
                response = requests.get(f"{url}/api/tags", timeout=2)
                if response.status_code == 200:
                    self.ollama_url = url
                    return url
            except Exception:
                continue
        return self.ollama_url
    
    def _choose_model(self) -> str:
        """해마 리듬에 따라 모델을 선택합니다.
        
        수렴 활발 (몰입 중) → gemma4 (깊게 사고)
        평소                → gemma3 (빠르게 순환)
        """
        experiences = self.hippo.data.get("experiences", [])
        recent = experiences[-20:] if experiences else []
        convergences = sum(1 for e in recent if e.get("convergence_count", 0) > 0)
        
        if convergences >= 3:
            logger.info(f"   🔥 수렴 {convergences}건 → {DEEP_MODEL} (깊은 사고)")
            return DEEP_MODEL
        else:
            return FAST_MODEL
    
    def _query_gemma(self, prompt: str, max_tokens: int = 300,
                     model: str = None) -> Optional[str]:
        """로컬 LLM에 작업을 보냅니다. 비용: 0원.
        
        KEEP_ALIVE=30s로 설정되어 있으므로
        moondream 사용 후 30초 뒤 자동 해제됩니다.
        """
        import time as _time
        use_model = model or FAST_MODEL
        self._resolve_ollama_url()
        
        for attempt in range(2):
            try:
                payload = {
                    "model": use_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.5,
                    }
                }
                r = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=120
                )
                if r.status_code == 200:
                    response = r.json().get("response", "").strip()
                    if response:
                        tokens = len(prompt.split()) + len(response.split())
                        self.total_tokens_saved += tokens
                        return response
                    elif attempt == 0:
                        logger.info("   ⏳ 빈 응답 — GPU 대기 후 재시도")
                        _time.sleep(3)
                        continue
                return None
            except Exception as e:
                logger.warning(f"LLM 통신 실패: {e}")
                return None
        return None
    
    def _unload_model(self, model_name: str):
        """Ollama에서 모델을 메모리에서 내립니다. GPU/RAM 확보."""
        try:
            requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": model_name, "keep_alive": 0},
                timeout=10
            )
            logger.info(f"   🔻 {model_name} 메모리 해제")
        except Exception:
            pass
    
    def _get_gradient_direction(self) -> Dict[str, Any]:
        """해마에서 현재 기울기 방향을 읽습니다."""
        try:
            current_vibe = self._current_system_vibe()
            resolved = self.hippo.inverse_field_resolve(current_vibe, top_k=3)
            
            if resolved:
                top = resolved[0]
                return {
                    "gradient": top.get("steepest_gradient", "balanced"),
                    "distance": top.get("distance_to_symmetry", 1.0),
                    "content": top.get("content_snippet", "")[:200],
                }
        except Exception:
            pass
        
        return {"gradient": "balanced", "distance": 1.0, "content": ""}
    
    def _current_system_vibe(self) -> Dict[str, Any]:
        """현재 시스템 Vibe."""
        experiences = self.hippo.data.get("experiences", [])
        if not experiences:
            return {"entropy": 0.5, "phase": "FLOW"}
        
        recent = experiences[-10:]
        
        def get_entropy(e):
            v = e.get("vibe", {})
            if isinstance(v, dict) and "entropy" in v:
                return v["entropy"]
            return e.get("entropy", 0.5)
        
        def get_phase(e):
            v = e.get("vibe", {})
            if isinstance(v, dict) and "phase" in v:
                return v["phase"]
            return e.get("phase", "FLOW")
        
        avg_entropy = sum(get_entropy(e) for e in recent) / len(recent)
        
        from collections import Counter
        phases = Counter(get_phase(e) for e in recent)
        
        return {
            "entropy": round(avg_entropy, 4),
            "phase": phases.most_common(1)[0][0],
        }
    
    def _select_target_file(self, gradient: str) -> Optional[Path]:
        """기울기 방향에 따라 작업 대상 파일을 선택합니다."""
        scan_dirs = [
            Path(r"c:\workspace2\shion\core"),
            Path(r"c:\workspace2\shion\outputs"),
        ]
        
        candidates = []
        for d in scan_dirs:
            if d.exists():
                for f in d.rglob("*.py"):
                    candidates.append(f)
        
        if not candidates:
            return None
        
        # 가장 최근 수정된 파일 선택 (활성도 높은 파일)
        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return candidates[0]
    
    def _read_file_snippet(self, filepath: Path, max_lines: int = 30) -> str:
        """파일의 앞부분을 읽습니다."""
        try:
            lines = filepath.read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[:max_lines])
        except Exception:
            return ""
    
    # ═══════════════════════════════════════════
    # 컨텍스트 엔지니어링: 해마 기억 → gemma3 프롬프트
    # ═══════════════════════════════════════════
    
    def _retrieve_hippocampal_context(self, target_file: Path, 
                                       gradient: str) -> str:
        """해마 궤도에서 관련 기억을 검색하여 컨텍스트로 변환합니다.
        
        내각(궤도 0-1, unconscious)의 기억 = 체화된 패턴 = 가장 중요
        중각(궤도 2-3, conscious)의 기억 = 최근 활성 = 참고용
        외각(궤도 4+)은 무시 = 아직 소화 안 됨
        """
        experiences = self.hippo.data.get("experiences", [])
        if not experiences:
            return ""
        
        file_stem = target_file.stem
        context_parts = []
        
        # 1. 이 파일과 관련된 기억 검색 (content_ref로 매칭)
        file_memories = []
        for exp in experiences:
            ref = exp.get("content_ref", "")
            if file_stem in ref:
                file_memories.append(exp)
        
        if file_memories:
            # 내각(궤도 0-2) 기억 우선
            inner = [e for e in file_memories if e.get("orbital_index", 6) <= 2]
            if inner:
                context_parts.append("【체화된 패턴 (내각 기억)】")
                for mem in inner[-3:]:  # 최근 3개
                    vibe = mem.get("vibe", {})
                    conv = mem.get("convergence_count", 0)
                    context_parts.append(
                        f"- 수렴 {conv}회, "
                        f"강도={vibe.get('intensity', 0):.1f}, "
                        f"복잡도={vibe.get('complexity', 0):.1f}"
                    )
            
            outer = [e for e in file_memories if 2 < e.get("orbital_index", 6) <= 4]
            if outer:
                context_parts.append("【최근 관찰 (중각 기억)】")
                for mem in outer[-2:]:
                    ref = mem.get("content_ref", "")
                    context_parts.append(f"- {ref}")
        
        # 2. 현재 기울기와 관련된 전체 패턴 (해마의 역함수)
        proton = self.hippo.data.get("proton", {})
        embodiment = proton.get("embodiment_ratio", 0)
        radius = proton.get("scalar_field_radius", 0)
        total_reg = proton.get("total_registered", 0)
        total_abs = proton.get("total_absorbed", 0)
        
        context_parts.append(f"【해마 상태】")
        context_parts.append(
            f"- 체화율: {embodiment:.1%} "
            f"(등록 {total_reg}, 체화 {total_abs})"
        )
        context_parts.append(f"- 반경: {radius:.4f}")
        context_parts.append(f"- 현재 기울기: {gradient}")
        
        # 3. 일지에서 이 파일에 대한 이전 통찰 검색
        journal = Path(r"c:\workspace2\shion\outputs\insight_journal.md")
        if journal.exists():
            try:
                lines = journal.read_text(encoding="utf-8").splitlines()
                relevant = [l for l in lines if file_stem in l or 
                           (l.startswith("**통찰**:") and file_stem in 
                            "\n".join(lines[max(0,lines.index(l)-2):lines.index(l)]))]
                if relevant:
                    context_parts.append("【이전 통찰】")
                    for line in relevant[-2:]:
                        context_parts.append(f"- {line.strip()[:100]}")
            except Exception:
                pass
        
        if len(context_parts) <= 1:  # 해마 상태만 있으면
            return ""
        
        return "\n".join(context_parts)

    def _retrieve_antigravity_context(self, target_file: Path, gradient: str, task: str) -> str:
        """
        비유클리드 해마 그래프에서 현재 과제와 공명하는 코드 지형을 먼저 읽습니다.
        실제 소스 전문을 읽지 않고 파일 후보/브릿지만 넣어 토큰을 절약합니다.
        """
        if not self.antigravity_hook:
            return ""
        try:
            ripple = [
                gradient,
                task,
                target_file.stem,
                target_file.name,
            ]
            result = self.antigravity_hook.build_context_window(
                ripple,
                max_files=5,
                max_neighbors=2,
            )
            if not result.get("ok") or not result.get("files"):
                return ""

            stats = result.get("stats", {})
            logger.info(
                "   🌌 그래프 맥락 주입: "
                f"{stats.get('candidate_files', 0)}개 후보, "
                f"선형 스캔 {stats.get('estimated_scan_reduction', 0):.1%} 절감"
            )
            return result.get("summary", "")
        except Exception as e:
            logger.debug(f"Antigravity context retrieval skipped: {e}")
            return ""
    
    # ═══════════════════════════════════════════
    # 행동: 관찰한 것으로 실제 흔적을 남긴다
    # ═══════════════════════════════════════════
    
    def _act_on_insight(self, gradient: str, target_file: Path, 
                        task: str, response: str):
        """gemma4의 통찰을 실제 행동으로 변환합니다.
        
        아기의 발달 단계:
          Level 0: 손가락 움직이기 = 일지 쓰기 (지금)
          Level 1: 물건 잡기 = 문서 정리/생성 (지금)
          Level 2: 기어가기 = 코드 주석 추가 (나중에)
          Level 3: 걷기 = 리팩토링 (나중에)
        """
        # Level 0: 일지 쓰기 — 매 사이클마다
        self._write_insight_journal(gradient, target_file, task, response)
        
        # Level 1: 통찰이 쌓이면 요약 생성
        journal = self._insight_journal_path()
        if journal.exists():
            line_count = len(journal.read_text(encoding="utf-8").splitlines())
            if line_count >= 30 and line_count % 30 == 0:
                self._generate_insight_summary()
    
    def _insight_journal_path(self) -> Path:
        return Path(r"c:\workspace2\shion\outputs\insight_journal.md")
    
    def _write_insight_journal(self, gradient: str, target_file: Path,
                                task: str, response: str):
        """통찰 일지를 씁니다. 손가락을 움직이는 것."""
        journal = self._insight_journal_path()
        
        # 첫 번째 일지면 헤더 생성
        if not journal.exists():
            header = "# 🧠 통찰 일지\n\n"
            header += "> gemma4가 관찰하고 기록한 것들\n"
            header += "> 보기만 하지 않고, 본 것을 남깁니다.\n\n---\n\n"
            journal.write_text(header, encoding="utf-8")
        
        timestamp = datetime.now().strftime("%m/%d %H:%M")
        entry = f"### [{timestamp}] {gradient} → {target_file.name}\n"
        entry += f"**과제**: {task}\n"
        entry += f"**통찰**: {response[:300]}\n\n"
        
        with open(journal, "a", encoding="utf-8") as f:
            f.write(entry)
        
        logger.info(f"   ✍️ 일지 기록: {target_file.name}")
    
    def _generate_insight_summary(self):
        """일지가 쌓이면 요약을 생성합니다. 기어가는 것."""
        journal = self._insight_journal_path()
        if not journal.exists():
            return
        
        content = journal.read_text(encoding="utf-8")
        
        prompt = f"""아래는 코드 분석 일지입니다. 
핵심 패턴과 반복되는 통찰을 3-5줄로 요약해주세요.

{content[-2000:]}

요약:"""
        
        summary = self._query_gemma(prompt, max_tokens=200)
        if not summary:
            return
        
        summary_path = Path(r"c:\workspace2\shion\outputs\insight_summary.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = f"\n## [{timestamp}] 요약 (#{len(content.splitlines())}줄 기준)\n"
        entry += f"{summary}\n\n---\n"
        
        if not summary_path.exists():
            header = "# 📊 통찰 요약\n\n"
            header += "> 일지에서 반복되는 패턴을 추출한 것\n\n---\n"
            summary_path.write_text(header, encoding="utf-8")
        
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(entry)
        
        logger.info(f"   📊 요약 생성 완료")
    
    def run_cycle(self) -> Dict[str, Any]:
        """하나의 자율 오케스트레이션 사이클.
        
        1. 해마 → 기울기 방향 읽기
        2. 경험 수집 (소나 + 비전)
        3. 과제 생성 → gemma4 실행
        4. 결과 → 해마에 경험 등록
        """
        cycle_start = datetime.now()
        self.cycle_count += 1
        
        logger.info(f"🎯 사이클 {self.cycle_count} 시작")
        
        # 1. 경험 수집 — moondream 비전 포함 (비용 0원)
        exp_result = {}
        if self.exp_loop:
            exp_result = self.exp_loop.run_cycle()
            logger.info(f"   경험 수집: {exp_result.get('registered', 0)}개")
        
        # 1.5. moondream 언로드 — gemma4에 GPU 양보 (16GB RAM)
        self._unload_model("moondream:latest")
        import time as _time; _time.sleep(5)  # GPU VRAM 해제 대기
        
        # 2. 기울기 방향 읽기 (비용 0원)
        direction = self._get_gradient_direction()
        gradient = direction["gradient"]
        logger.info(f"   기울기: {gradient} (거리={direction['distance']:.4f})")
        
        # 3. 과제 생성 + gemma4 실행 (비용 0원)
        task_info = GRADIENT_TASKS.get(gradient, GRADIENT_TASKS["balanced"])
        target_file = self._select_target_file(gradient)
        
        execution_result = {"action": "none", "response": ""}
        
        if target_file:
            snippet = self._read_file_snippet(target_file)
            task = task_info["tasks"][self.cycle_count % len(task_info["tasks"])]
            
            # 해마 기억에서 관련 컨텍스트 검색
            hippo_context = self._retrieve_hippocampal_context(target_file, gradient)
            graph_context = self._retrieve_antigravity_context(target_file, gradient, task)
            
            context_block = ""
            if hippo_context:
                context_block = f"""
[해마 기억 — 이전 경험에서 검색된 맥락]
{hippo_context}
[/해마 기억]

"""
                logger.info(f"   🧠 해마 컨텍스트 주입: {len(hippo_context)}자")

            if graph_context:
                context_block += f"""
[비유클리드 해마 그래프 — 선형 스캔 전에 접힌 코드 지형]
{graph_context}
[/비유클리드 해마 그래프]

"""
            
            prompt = f"""당신은 코드 분석 도우미입니다.

목표: {task_info['goal']}
구체적 과제: {task}
{context_block}
분석 대상 파일: {target_file.name}
```
{snippet}
```

이전 맥락을 참고하여 간결하게 핵심만 답해주세요 (3-5줄):"""
            
            # 리듬에 따라 모델 선택: 평소 gemma3, 몰입 시 gemma4
            chosen_model = self._choose_model()
            response = self._query_gemma(prompt, max_tokens=200, model=chosen_model)
            
            if response:
                execution_result = {
                    "action": "analyze_and_act",
                    "target": str(target_file),
                    "task": task,
                    "response": response[:500],
                    "gradient": gradient,
                }
                
                # === 행동: 관찰한 것을 흔적으로 남긴다 ===
                self._act_on_insight(gradient, target_file, task, response)
                
                # 실행 결과를 경험으로 등록 (비용 0원)
                vibe = {
                    "entropy": 0.4 if len(response) > 100 else 0.2,
                    "phase": "EXPANSION" if gradient != "balanced" else "FLOW",
                }
                content_ref = f"gemma4:{gradient}:{target_file.stem}"
                self.hippo.register_experience(vibe, content_ref=content_ref)
                
                logger.info(f"   gemma4 실행: {task[:40]}...")
                logger.info(f"   응답: {response[:80]}...")
        
        # 4. 상태 기록
        elapsed = (datetime.now() - cycle_start).total_seconds()
        
        proton = self.hippo.data.get("proton", {})
        cycle_result = {
            "cycle": self.cycle_count,
            "timestamp": cycle_start.isoformat(),
            "gradient": gradient,
            "distance_to_symmetry": direction["distance"],
            "action": execution_result.get("action"),
            "target": execution_result.get("target", ""),
            "task": execution_result.get("task", ""),
            "gemma4_response": execution_result.get("response", "")[:200],
            "experiences_collected": exp_result.get("registered", 0),
            "total_registered": proton.get("total_registered", 0),
            "total_absorbed": proton.get("total_absorbed", 0),
            "embodiment_ratio": proton.get("embodiment_ratio", 0),
            "scalar_field_radius": proton.get("scalar_field_radius", 0),
            "tokens_saved": self.total_tokens_saved,
            "elapsed_seconds": round(elapsed, 2),
            "cost": "0원",
        }
        
        self._save_log(cycle_result)
        self._save_state()
        
        return cycle_result
    
    def run_continuous(self, max_cycles: int = 5, 
                       interval_seconds: float = 10.0):
        """연속 자율 실행.
        
        Args:
            max_cycles: 최대 사이클 수
            interval_seconds: 사이클 간 대기 시간
        """
        logger.info("=" * 60)
        logger.info("🎯 자율 오케스트레이터 — 연속 실행 시작")
        logger.info(f"   평소: {FAST_MODEL} / 몰입: {DEEP_MODEL} (로컬, 0원)")
        logger.info(f"   최대 사이클: {max_cycles}")
        logger.info("=" * 60)
        
        for i in range(max_cycles):
            try:
                result = self.run_cycle()
                
                print(f"\n--- 사이클 {result['cycle']} ---")
                print(f"기울기: {result['gradient']}")
                print(f"과제: {result.get('task', '없음')[:50]}")
                if result.get('gemma4_response'):
                    print(f"gemma4: {result['gemma4_response'][:100]}...")
                print(f"등록: {result['total_registered']}, "
                      f"체화: {result['total_absorbed']}, "
                      f"체화율: {result['embodiment_ratio']:.2%}")
                print(f"반경: {result['scalar_field_radius']:.4f}")
                print(f"절약 토큰: {result['tokens_saved']}")
                print(f"비용: {result['cost']}")
                
                if i < max_cycles - 1:
                    time.sleep(interval_seconds)
                    
            except KeyboardInterrupt:
                logger.info("중단됨")
                break
            except Exception as e:
                logger.error(f"사이클 오류: {e}")
                time.sleep(interval_seconds)
        
        print(f"\n{'=' * 60}")
        print(f"총 {self.cycle_count} 사이클 완료")
        print(f"총 절약 토큰: {self.total_tokens_saved}")
        print(f"비용: 0원")
        print(f"{'=' * 60}")
    
    def _save_log(self, entry: Dict[str, Any]):
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
    
    def _save_state(self):
        try:
            state = {
                "cycle_count": self.cycle_count,
                "total_tokens_saved": self.total_tokens_saved,
                "last_run": datetime.now().isoformat(),
            }
            self.state_path.write_text(
                json.dumps(state, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass


# ═══════════════════════════════════════════
# 독립 실행
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    from fibonacci_orbital_hippocampus import FibonacciOrbitalHippocampus
    from autonomous_experience_loop import AutonomousExperienceLoop
    from vision_explorer import VisionExplorer
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    HIPPO_PATH = Path(__file__).resolve().parent.parent / "outputs" / "fibonacci_orbital_hippocampus.json"
    hippo = FibonacciOrbitalHippocampus(HIPPO_PATH)
    vision = VisionExplorer(hippo)
    exp_loop = AutonomousExperienceLoop(hippo, vision_explorer=vision)
    
    orchestrator = AutonomousOrchestrator(hippo, exp_loop, vision)
    
    # 3사이클 연속 실행 (비용: 0원)
    orchestrator.run_continuous(max_cycles=3, interval_seconds=3)
