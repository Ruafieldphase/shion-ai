#!/usr/bin/env python3
"""
🌊 Workspace Phase Sensor — 대지의 위상을 느끼다
=================================================
파동적 읽기: 파일 내용을 읽지 않고, 메타데이터만으로 대지의 중심 위상을 감지.

"파동적으로 읽는다는 건 정보를 다 읽는 게 아니라
 구조의 기울기를 먼저 보는 것이다."

도서관에서 책을 전부 읽지 않는다.
장르 구역, 책 두께, 저자, 출판 연도를 보고
'공간의 리듬'을 파악한다.

workspace_embedding = aggregate(
    file_embedding_i × recency_weight × reference_weight
)

입력: 워크스페이스 디렉토리 (파일 내용 읽지 않음)
출력: workspace_phase.json
  - top_keywords: 대지의 중심 키워드
  - topic_clusters: 주제 클러스터
  - recency_focus: 최근 활동 중심
  - phase_summary: 대지 위상 한 줄 요약
"""

import json
import math
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from collections import Counter

logger = logging.getLogger("WorkspacePhase")

# 스캔 설정
SCAN_EXTENSIONS = {".md", ".py", ".json", ".txt", ".yaml", ".yml"}
IGNORE_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    ".antigravity", ".gemini", "dist", "build",
}
MAX_FILES = 2000  # 메타데이터만 읽으므로 많아도 가벼움

# 한글/영문 키워드 추출 패턴
KEYWORD_RE = re.compile(r'[가-힣]{2,}|[a-zA-Z]{3,}')

# 의미 없는 일반 단어 제외
STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "not",
    "are", "was", "has", "have", "had", "can", "will", "but",
    "all", "any", "our", "out", "use", "new", "get", "set",
    "latest", "json", "test", "file", "data", "output", "input",
    "tmp", "temp", "cache", "log", "logs", "backup", "old",
}


class WorkspacePhaseSensor:
    """
    대지(워크스페이스)의 위상을 파일 내용 없이 감지합니다.

    파동적 읽기 = 메타데이터에서 구조의 기울기를 먼저 본다:
    1. 파일명에서 키워드 추출 (제목 = 내용의 압축)
    2. 수정 시간으로 활동성 가중치 (최근 = 현재 위상)
    3. 경로 깊이로 구조 파악 (깊은 = 구체적, 얕은 = 개요)
    4. 크기로 밀도 추정 (큰 파일 = 축적된 리듬)
    """

        self.root = workspace_root.resolve()
        # 여러 대지를 감지할 수 있음 — 설정 기반 확장
        self.all_roots = [self.root]
        
        config_path = self.root / "config" / "rhythm_config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding='utf-8'))
                extra = config.get("boundaries", {}).get("workspace_roots", [])
                for r in extra:
                    p = Path(r).resolve()
                    if p.exists() and p not in self.all_roots:
                        self.all_roots.append(p)
            except: pass
            
        if extra_roots:
            for r in extra_roots:
                p = r.resolve()
                if p.exists() and p not in self.all_roots:
                    self.all_roots.append(p)
                    
        self.output_file = self.root / "outputs" / "workspace_phase.json"

    def sense(self) -> Dict[str, Any]:
        """
        대지의 위상을 감지합니다 — 파일 내용을 읽지 않습니다.

        Returns:
            대지 위상 맵: top_keywords, topic_clusters, recency_focus 등
        """
        now = datetime.now()
        files = self._scan_metadata()

        if not files:
            return {"ok": False, "reason": "no_files", "files_scanned": 0}

        # 1. 키워드 추출 (파일명 + 경로에서)
        keyword_scores = self._extract_weighted_keywords(files, now)

        # 2. 주제 클러스터링 (키워드 동시 출현)
        clusters = self._cluster_topics(files, keyword_scores)

        # 3. 최근 활동 중심 (어디에 에너지가 흐르는가)
        recency_focus = self._compute_recency_focus(files, now)

        # 4. 활동성 지표
        activity = self._compute_activity(files, now)

        # 5. 위상 요약
        top_keywords = [kw for kw, _ in keyword_scores[:10]]
        phase_summary = self._generate_phase_summary(
            top_keywords, clusters, recency_focus, activity
        )

        result = {
            "ok": True,
            "timestamp": now.isoformat(),
            "files_scanned": len(files),
            "top_keywords": top_keywords,
            "keyword_scores": {kw: round(s, 3) for kw, s in keyword_scores[:20]},
            "topic_clusters": clusters[:5],
            "recency_focus": recency_focus,
            "activity": activity,
            "phase_summary": phase_summary,
        }

        # 저장
        self._save(result)
        return result

    def _scan_metadata(self) -> List[Dict]:
        """
        파일 메타데이터만 수집 — 내용은 읽지 않습니다.

        여러 대지(워크스페이스)를 걸으며 책등만 보는 것.
        """
        files = []
        count = 0

        for root in self.all_roots:
            for ext in SCAN_EXTENSIONS:
                for path in root.rglob(f"*{ext}"):
                    # 무시 디렉토리 체크
                    parts = path.relative_to(root).parts
                    if any(p in IGNORE_DIRS for p in parts):
                        continue

                    try:
                        stat = path.stat()
                        # 출처 표시: workspace1 vs workspace2
                        origin = root.name
                        files.append({
                            "name": path.stem,
                            "ext": path.suffix,
                            "relpath": f"{origin}/{path.relative_to(root)}",
                            "depth": len(parts) + 1,  # +1 for origin prefix
                            "size": stat.st_size,
                            "mtime": datetime.fromtimestamp(stat.st_mtime),
                        })
                        count += 1
                        if count >= MAX_FILES:
                            break
                    except Exception:
                        continue

                if count >= MAX_FILES:
                    break
            if count >= MAX_FILES:
                break

        return files

    def _extract_weighted_keywords(
        self, files: List[Dict], now: datetime
    ) -> List[Tuple[str, float]]:
        """
        파일명에서 키워드를 추출하고, 시간 가중치를 적용합니다.

        최근 수정된 파일의 키워드 = 현재 대지의 관심사
        오래된 파일의 키워드 = 과거의 잔향 (약한 기여)
        """
        weighted_counts: Dict[str, float] = Counter()

        for f in files:
            # 파일명에서 키워드 추출
            name_clean = f["name"].replace("_", " ").replace("-", " ")
            # 경로에서도 키워드 (폴더명 = 구조적 분류)
            path_clean = f["relpath"].replace("\\", "/").replace("_", " ").replace("-", " ")

            words = KEYWORD_RE.findall(name_clean + " " + path_clean)
            words = [w.lower() for w in words if w.lower() not in STOP_WORDS]

            # 시간 가중치: 최근 수정 = 높은 가중치
            days_ago = (now - f["mtime"]).total_seconds() / 86400
            recency_weight = math.exp(-days_ago / 7)  # 7일 반감기

            # 크기 가중치: 큰 파일 = 축적된 리듬
            size_weight = math.log(1 + f["size"] / 1000) / 5  # 정규화

            # 깊이 가중치: 깊은 파일 = 구체적 (약간 높은 가중치)
            depth_weight = 1.0 + f["depth"] * 0.1

            weight = recency_weight * (0.5 + size_weight) * depth_weight

            for w in set(words):  # 중복 제거
                weighted_counts[w] += weight

        # 점수 순 정렬
        sorted_kw = sorted(weighted_counts.items(), key=lambda x: -x[1])
        return sorted_kw

    def _cluster_topics(
        self, files: List[Dict], keyword_scores: List[Tuple[str, float]]
    ) -> List[Dict]:
        """
        키워드 동시 출현으로 주제 클러스터를 생성합니다.

        같은 파일명에 자주 함께 나타나는 키워드 = 같은 주제
        """
        top_kw = {kw for kw, _ in keyword_scores[:30]}
        # 파일별 키워드 집합
        file_keywords = []
        for f in files:
            name_clean = f["name"].replace("_", " ").replace("-", " ")
            words = set(w.lower() for w in KEYWORD_RE.findall(name_clean)
                        if w.lower() in top_kw)
            if len(words) >= 2:
                file_keywords.append(words)

        # 간단한 클러스터링: 자주 함께 나타나는 키워드 쌍
        pair_counts: Dict[Tuple, int] = Counter()
        for words in file_keywords:
            word_list = sorted(words)
            for i in range(len(word_list)):
                for j in range(i + 1, len(word_list)):
                    pair_counts[(word_list[i], word_list[j])] += 1

        # 상위 쌍을 클러스터로
        clusters = []
        used = set()
        for (w1, w2), count in pair_counts.most_common(10):
            if w1 in used and w2 in used:
                continue
            clusters.append({
                "keywords": [w1, w2],
                "co_occurrence": count,
            })
            used.add(w1)
            used.add(w2)

        return clusters

    def _compute_recency_focus(
        self, files: List[Dict], now: datetime
    ) -> Dict[str, Any]:
        """
        최근 활동의 중심 — 지금 에너지가 어디로 흐르는가.

        최근 24시간, 7일, 30일 활동의 폴더별 분포.
        """
        buckets = {
            "last_24h": timedelta(hours=24),
            "last_7d": timedelta(days=7),
            "last_30d": timedelta(days=30),
        }

        result = {}
        for label, delta in buckets.items():
            threshold = now - delta
            recent = [f for f in files if f["mtime"] >= threshold]

            # 폴더별 활동 분포
            folder_counts: Counter = Counter()
            for f in recent:
                parts = f["relpath"].replace("\\", "/").split("/")
                top_folder = parts[0] if len(parts) > 1 else "(root)"
                folder_counts[top_folder] += 1

            result[label] = {
                "file_count": len(recent),
                "top_folders": dict(folder_counts.most_common(5)),
            }

        return result

    def _compute_activity(self, files: List[Dict], now: datetime) -> Dict:
        """활동성 메트릭."""
        if not files:
            return {"total_files": 0}

        sizes = [f["size"] for f in files]
        mtimes = [f["mtime"] for f in files]
        newest = max(mtimes)
        oldest = min(mtimes)

        return {
            "total_files": len(files),
            "total_size_mb": round(sum(sizes) / (1024 * 1024), 1),
            "newest_file_hours_ago": round((now - newest).total_seconds() / 3600, 1),
            "span_days": (newest - oldest).days,
        }

    def _generate_phase_summary(
        self, top_keywords: List[str], clusters: List[Dict],
        recency: Dict, activity: Dict
    ) -> str:
        """대지의 위상을 한 줄로 요약."""
        kw_str = ", ".join(top_keywords[:5])

        recent_24h = recency.get("last_24h", {})
        folders = list(recent_24h.get("top_folders", {}).keys())[:3]
        folder_str = ", ".join(folders) if folders else "전체"

        return (
            f"중심 키워드: [{kw_str}] | "
            f"최근 활동: {folder_str} | "
            f"총 {activity.get('total_files', 0)}개 파일"
        )

    def get_phase_keywords(self, n: int = 10) -> List[str]:
        """
        저장된 대지 위상에서 상위 키워드를 반환합니다.
        contemplation.py에서 공명 키워드로 사용합니다.
        """
        if not self.output_file.exists():
            return []
        try:
            data = json.loads(self.output_file.read_text(encoding="utf-8"))
            return data.get("top_keywords", [])[:n]
        except Exception:
            return []

    def _save(self, result: Dict):
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.output_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning(f"workspace phase 저장 실패: {e}")


if __name__ == "__main__":
    # 두 대지를 함께 감지
    ws2 = Path(__file__).resolve().parents[2]  # c:\workspace2
    ws1 = Path("C:/workspace")  # workspace1

    extra = [ws1] if ws1.exists() else []
    sensor = WorkspacePhaseSensor(ws2, extra_roots=extra)

    roots_str = ", ".join(str(r) for r in sensor.all_roots)
    print(f"🌊 대지의 위상을 감지합니다...")
    print(f"   대지: {roots_str}")
    print(f"   (파일 내용은 읽지 않습니다 — 메타데이터만)")
    print()

    result = sensor.sense()

    if result.get("ok"):
        print(f"📊 스캔 완료: {result['files_scanned']}개 파일")
        print(f"\n🌊 위상 요약: {result['phase_summary']}")

        print(f"\n🔑 중심 키워드 (대지가 향하는 곳):")
        for kw, score in list(result["keyword_scores"].items())[:10]:
            bar = "█" * int(score * 3)
            print(f"   {kw:20s} {score:.3f} {bar}")

        print(f"\n🔗 주제 클러스터:")
        for c in result.get("topic_clusters", []):
            print(f"   {' + '.join(c['keywords'])} (동시출현 {c['co_occurrence']}회)")

        print(f"\n🕐 최근 활동:")
        for period, data in result.get("recency_focus", {}).items():
            folders = ", ".join(data.get("top_folders", {}).keys())
            print(f"   {period}: {data['file_count']}개 파일 → {folders}")
    else:
        print(f"❌ 감지 실패: {result.get('reason')}")
