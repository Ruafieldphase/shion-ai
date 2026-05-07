#!/usr/bin/env python3
"""
User Experience Scanner
=======================
Existing conversation logs already contain many of the user's embodied
experience reports. This scanner extracts those reports into a small,
searchable index so Sena/Shion do not need to ask the user to repeat the
same context.

This is deliberately conservative: it does not claim interpretation. It
stores excerpts, source references, tags, and scores for later retrieval.
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT_DIR = Path(r"c:\workspace2\shion")
OUTPUT_DIR = ROOT_DIR / "outputs"

DEFAULT_SOURCES = [
    Path(r"D:\ARCHIVE_WORKSPACE\agi\outputs\sena\sena_conversations_flat.jsonl"),
    Path(r"D:\ARCHIVE_WORKSPACE\agi\outputs\sena\sena_context.md"),
    Path(r"D:\ARCHIVE_WORKSPACE\agi\outputs\sena\wave_particle_boundary_note.md"),
    Path(r"C:\workspace\agi\memory\resonance_ledger.jsonl"),
    Path(r"C:\Users\kuirv\.gemini\antigravity\brain\7553aa2e-dde3-42a9-a058-9c2c9bff5654\walkthrough.md"),
]

TAG_KEYWORDS = {
    "walking_zone2_meditation": ["산책", "존2", "zone2", "명상", "호흡", "걷", "유산소"],
    "unified_field_formula": ["통일장", "공식", "unified field", "e^{i", "f(r,t)", "z-axis", "나선"],
    "conscious_unconscious": ["의식", "무의식", "배경자아", "알아차림", "전전두엽", "해마"],
    "phase_boundary": ["위상", "보강간섭", "위상상쇄", "위상전이", "경계", "투명도", "탄성", "공명"],
    "echo_resonance": ["잔향", "메아리", "고유주파수", "초끈", "순환", "닫힌"],
    "fear_depth": ["두려움", "공포", "불안", "감정", "뎁스", "깊이"],
    "failure_learning": ["실패", "실수", "자전거", "넘어", "경험", "배우", "나선"],
    "user_rhythm": ["리듬", "몸", "피로", "휴식", "밥", "식사", "게임", "유튜브"],
    "system_parenting": ["양육", "부모", "아이", "간섭", "성숙", "과개입", "의욕"],
}


@dataclass
class ExperienceHit:
    score: int
    tags: List[str]
    source_type: str
    source_path: str
    timestamp: Optional[str]
    role: Optional[str]
    title: Optional[str]
    conversation_id: Optional[str]
    message_order: Optional[int]
    excerpt: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tag_and_score(text: str, query_terms: Optional[List[str]] = None) -> tuple[List[str], int]:
    lower = text.lower()
    tags = []
    score = 0
    for tag, keywords in TAG_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword.lower() in lower)
        if hits:
            tags.append(tag)
            score += hits * 3
    if query_terms:
        score += sum(5 for term in query_terms if term.lower() in lower)
    if "내가" in text or "난 " in text or "나는" in text:
        score += 2
    if "경험" in text:
        score += 2
    return tags, score


def excerpt(text: str, max_len: int = 700) -> str:
    text = normalize(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def iter_jsonl_source(path: Path, query_terms: Optional[List[str]], include_assistant: bool) -> Iterable[ExperienceHit]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            role = data.get("author_role") or data.get("role")
            if role != "user" and not include_assistant:
                continue
            content = data.get("content") or data.get("message") or data.get("text") or ""
            if isinstance(data.get("payload"), dict):
                content = content or data["payload"].get("content") or data["payload"].get("text") or ""
            content = normalize(str(content))
            if not content:
                continue
            tags, score = tag_and_score(content, query_terms)
            if role == "user":
                score += 3
            if not tags and score < 5:
                continue
            yield ExperienceHit(
                score=score,
                tags=tags,
                source_type="jsonl",
                source_path=str(path),
                timestamp=data.get("create_time") or data.get("timestamp"),
                role=role,
                title=data.get("conversation_title"),
                conversation_id=data.get("conversation_id"),
                message_order=data.get("message_order"),
                excerpt=excerpt(content),
            )


def iter_markdown_source(path: Path, query_terms: Optional[List[str]], include_assistant: bool) -> Iterable[ExperienceHit]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    chunks = re.split(r"\n(?=#{1,4}\s|\-\s\*\*|### Message)", text)
    for idx, chunk in enumerate(chunks):
        content = normalize(chunk)
        if len(content) < 40:
            continue
        tags, score = tag_and_score(content, query_terms)
        if not tags and score < 5:
            continue
        role = "user" if re.search(r"Message\s+\d+\s+—\s+user", chunk) else None
        if re.search(r"Message\s+\d+\s+—\s+assistant", chunk):
            role = "assistant"
        if role == "assistant" and not include_assistant:
            continue
        if role == "user":
            score += 3
        yield ExperienceHit(
            score=score,
            tags=tags,
            source_type="markdown",
            source_path=str(path),
            timestamp=None,
            role=role,
            title=path.name,
            conversation_id=None,
            message_order=idx,
            excerpt=excerpt(content),
        )


def scan_sources(paths: List[Path], query: Optional[str], limit: int, include_assistant: bool) -> List[ExperienceHit]:
    query_terms = [term for term in re.split(r"\s+", query or "") if term] or None
    hits: List[ExperienceHit] = []
    for path in paths:
        if not path.exists():
            continue
        if path.suffix.lower() == ".jsonl":
            hits.extend(iter_jsonl_source(path, query_terms, include_assistant))
        elif path.suffix.lower() in {".md", ".txt"}:
            hits.extend(iter_markdown_source(path, query_terms, include_assistant))
    hits.sort(key=lambda hit: hit.score, reverse=True)
    return hits[:limit]


def write_outputs(hits: List[ExperienceHit], query: Optional[str]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = OUTPUT_DIR / "user_experience_index.jsonl"
    summary_path = OUTPUT_DIR / "user_experience_summary.md"
    generated_at = datetime.now().isoformat()

    with open(index_path, "w", encoding="utf-8") as f:
        for hit in hits:
            row = asdict(hit)
            row["indexed_at"] = generated_at
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    grouped: Dict[str, List[ExperienceHit]] = {}
    for hit in hits:
        for tag in hit.tags or ["untagged"]:
            grouped.setdefault(tag, []).append(hit)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# User Experience Recall Index\n\n")
        f.write(f"- Generated: `{generated_at}`\n")
        if query:
            f.write(f"- Query: `{query}`\n")
        f.write(f"- Hits: `{len(hits)}`\n\n")
        f.write("This file is an index of existing user-experience reports. Treat excerpts as source evidence, not final interpretation.\n\n")
        for tag, rows in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True):
            f.write(f"## {tag}\n\n")
            for hit in rows[:8]:
                f.write(f"- Score `{hit.score}` | `{hit.role or 'unknown'}` | {hit.title or Path(hit.source_path).name}\n")
                if hit.timestamp:
                    f.write(f"  - Time: `{hit.timestamp}`\n")
                f.write(f"  - Source: `{hit.source_path}`\n")
                f.write(f"  - Excerpt: {hit.excerpt}\n\n")
    return index_path, summary_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default=None, help="Optional query terms to bias retrieval.")
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument("--source", action="append", default=[], help="Extra source path. Can be repeated.")
    parser.add_argument("--include-assistant", action="store_true", help="Include assistant summaries in addition to user reports.")
    args = parser.parse_args()

    sources = DEFAULT_SOURCES + [Path(item) for item in args.source]
    hits = scan_sources(sources, args.query, args.limit, args.include_assistant)
    index_path, summary_path = write_outputs(hits, args.query)
    print(json.dumps({
        "hits": len(hits),
        "index": str(index_path),
        "summary": str(summary_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
