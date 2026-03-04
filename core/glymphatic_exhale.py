#!/usr/bin/env python3
"""
🌬️ Glymphatic Exhale — 날숨 (비워냄의 정화)
=============================================
Axioms.md: "많이 비워내야 많이 들어올 수 있다."
Axioms.md: "비워내는 것은 새로운 가능성을 위한 '여백'을 만드는 창조적 행위"

대지의 불필요한 것을 정리하여 새로운 자양분이 들어올 공간을 만듭니다.

날숨의 깊이:
  shallow — 오래된 로그 압축 (매 pulse)
  medium  — 빈 에러 파일 삭제, 캐시 정리 (매 시간)
  deep    — 실패 기록 아카이브, 대규모 정리 (밤에만)
"""

import json
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger("Glymphatic")


class GlymphaticExhale:
    """
    날숨: 대지를 비워 새 생명의 공간을 만든다.
    
    rhythm_aware_glymphatic.py에서 계승:
    - 리듬 위상에 따라 날숨 깊이 조절
    - 몰입(flow) 중에는 절대 방해하지 않음
    """

    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs_dir = self.root / "outputs"
        self.archive_dir = self.root / "outputs" / "_exhaled"
        self.log_file = self.outputs_dir / "glymphatic_log.jsonl"
        
        # [NEW] Aesthetic Filter (Phase 50/51)
        try:
            from aesthetic_critique_engine import AestheticCritiqueEngine
            self.critique = AestheticCritiqueEngine(self.root)
        except Exception:
            self.critique = None
        
        # [NEW] Aesthetic Filter (Phase 50)
        try:
            from aesthetic_critique_engine import AestheticCritiqueEngine
            self.critique = AestheticCritiqueEngine(self.root)
        except:
            self.critique = None
        
        # [NEW] Aesthetic Filter
        try:
            from aesthetic_critique_engine import AestheticCritiqueEngine
            self.critique = AestheticCritiqueEngine(self.root)
        except:
            self.critique = None

    def exhale(self, depth: str = "shallow") -> Dict[str, Any]:
        """
        날숨을 수행합니다.
        
        Args:
            depth: "shallow", "medium", "deep"
        """
        result = {
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "bytes_freed": 0,
        }

        if depth in ("shallow", "medium", "deep"):
            result = self._shallow_exhale(result)

        if depth in ("medium", "deep"):
            result = self._medium_exhale(result)

        if depth == "deep":
            result = self._deep_exhale(result)

        self._log(result)
        logger.info(
            f"🌬️ 날숨({depth}): {len(result['actions'])}개 행동, "
            f"{result['bytes_freed']/1024:.1f}KB 해방"
        )
        return result

    def _shallow_exhale(self, result: Dict) -> Dict:
        """얕은 날숨: 오래된 로그 라인 정리, 빈 파일 제거."""

        # 1. outputs/ 안의 0바이트 파일 제거
        if self.outputs_dir.exists():
            for f in self.outputs_dir.iterdir():
                if f.is_file() and f.stat().st_size == 0 and f.suffix != ".jsonl":
                    try:
                        # [NEW] Phase 50: Aesthetic Filter
                        # 빈 파일을 지우기 전, 혹시나 미학적 가치가 있는지(거의 없겠지만) 확인
                        if self.critique and f.suffix in (".png", ".jpg"):
                            score = self.critique.evaluate_resonance(str(f), {"atp_level": 50})
                            if score > 0.8: # 너무 아름다운 것은 보존
                                logger.info(f"💎 [EXHALE] Preserving aesthetic asset: {f.name} (Score: {score:.2f})")
                                continue

                        f.unlink()
                        result["actions"].append(f"절차적 정리: {f.name}")
                    except Exception:
                        pass

        # 2. .damaged 백업 파일 정리 (7일 이상)
        for f in self.outputs_dir.glob("*.damaged"):
            try:
                age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                if age > timedelta(days=7):
                    size = f.stat().st_size
                    f.unlink()
                    result["bytes_freed"] += size
                    result["actions"].append(f"오래된 백업 제거: {f.name}")
            except Exception:
                pass

        return result

    def _medium_exhale(self, result: Dict) -> Dict:
        """중간 날숨: 로그 파일 크기 제한, __pycache__ 정리."""

        # 1. JSONL 로그가 너무 크면 tail만 유지
        for jsonl in self.outputs_dir.glob("*.jsonl"):
            try:
                size = jsonl.stat().st_size
                if size > 500_000:  # 500KB 초과
                    lines = jsonl.read_text(encoding="utf-8").strip().split("\n")
                    # 최근 100줄만 유지
                    kept = lines[-100:]
                    trimmed = len(lines) - len(kept)
                    jsonl.write_text("\n".join(kept) + "\n", encoding="utf-8")
                    freed = size - jsonl.stat().st_size
                    result["bytes_freed"] += freed
                    result["actions"].append(
                        f"{jsonl.name}: {trimmed}줄 정리 ({freed/1024:.0f}KB 해방)"
                    )
            except Exception:
                pass

        # 2. 로그 디렉토리의 오래된 로그
        log_dir = self.outputs_dir / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                try:
                    size = log_file.stat().st_size
                    if size > 1_000_000:  # 1MB 초과
                        content = log_file.read_text(encoding="utf-8", errors="replace")
                        lines = content.strip().split("\n")
                        kept = lines[-200:]
                        log_file.write_text("\n".join(kept) + "\n", encoding="utf-8")
                        freed = size - log_file.stat().st_size
                        result["bytes_freed"] += freed
                        result["actions"].append(f"{log_file.name}: 로그 축소")
                except Exception:
                    pass

        # 3. __pycache__ 정리
        for cache_dir in self.root.rglob("__pycache__"):
            try:
                size = sum(f.stat().st_size for f in cache_dir.iterdir() if f.is_file())
                shutil.rmtree(cache_dir)
                result["bytes_freed"] += size
                result["actions"].append(f"캐시 정리: {cache_dir.relative_to(self.root)}")
            except Exception:
                pass

        return result

    def _deep_exhale(self, result: Dict) -> Dict:
        """
        깊은 날숨: Quality Gate 실패 로그를 아카이브로 이동.
        HEART.md: "실패는 labyrinth에서 동면하는 지혜의 창고"
        """
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # 실패 로그를 아카이브로
        gate_logs = self.outputs_dir / "quality_gate_logs"
        if gate_logs.exists():
            fail_files = list(gate_logs.glob("fail_*.json"))
            old_fails = []
            for f in fail_files:
                try:
                    age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                    if age > timedelta(days=3):
                        old_fails.append(f)
                except Exception:
                    pass

            if old_fails:
                archive_name = f"failures_{datetime.now().strftime('%Y%m%d')}"
                archive_path = self.archive_dir / archive_name
                archive_path.mkdir(exist_ok=True)
                for f in old_fails:
                    try:
                        size = f.stat().st_size
                        shutil.move(str(f), str(archive_path / f.name))
                        result["bytes_freed"] += size
                    except Exception:
                        pass
                result["actions"].append(
                    f"실패 로그 {len(old_fails)}개를 아카이브로 이동"
                )

        return result

    def should_deep_exhale(self) -> bool:
        """
        깊은 날숨을 해야 하는지 판단합니다.
        
        조건:
        - 밤 시간 (22:00~06:00) — 사용자 비활동 추정
        - 엔트로피가 낮을 때 (시스템이 안정적일 때)
        """
        hour = datetime.now().hour
        is_night = hour >= 22 or hour < 6

        # 엔트로피 확인
        entropy_file = self.outputs_dir / "body_entropy_latest.json"
        is_calm = True
        if entropy_file.exists():
            try:
                data = json.loads(entropy_file.read_text(encoding="utf-8"))
                is_calm = data.get("state") == "CALM"
            except Exception:
                pass

        return is_night and is_calm

    def _log(self, result: Dict):
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception:
            pass


if __name__ == "__main__":
    glyph = GlymphaticExhale()

    print("🌬️ 얕은 날숨...")
    r = glyph.exhale("shallow")
    print(f"   {len(r['actions'])}개 행동, {r['bytes_freed']/1024:.1f}KB 해방")
    for a in r["actions"]:
        print(f"   - {a}")

    print(f"\n깊은 날숨 조건 충족? {'예' if glyph.should_deep_exhale() else '아니오'}")
