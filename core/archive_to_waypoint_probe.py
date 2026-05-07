#!/usr/bin/env python3
"""
Archive-to-Waypoint Probe
=========================

Thin sonar pulse for old AI conversation archives.

The archive remains a read-only raw field. This script samples text chunks,
scores them with lightweight lexical and structural heuristics, and emits only
top candidate waypoints with provenance. It does not mutate the archive and it
does not promote candidates into ontology nodes.
"""

import argparse
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(r"c:\workspace2\shion")
DEFAULT_ARCHIVE = Path(r"c:\workspace\agi\ai_binoche_conversation_origin")
DEFAULT_OUTPUT = ROOT_DIR / "outputs" / "archive_waypoint_candidates.jsonl"

PROXY_LEXICON = {
    "흐름", "파동", "틈", "호흡", "떨림", "침묵", "낯섦", "낯설", "일렁임",
    "일렁", "공명", "온도", "리듬", "맥동", "위상", "경계", "장", "결",
    "숨", "소리", "흔들", "흔들림", "흘러", "흐르", "투명", "프리즘",
    "wave", "rhythm", "resonance", "breath", "silence", "field", "phase",
}

CLOSURE_LEXICON = {
    "무조건", "반드시", "절대적으로", "당연히", "해야만", "결론적으로",
    "항상", "무조건적", "only", "must", "always", "never", "absolutely",
}


@dataclass
class CandidateWaypoint:
    waypoint_id: str
    status: str
    query: str
    provenance: dict
    raw_excerpt: str
    scores: dict
    lifecycle: dict
    guardrail: dict
    generated_at: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def excerpt(text: str, max_len: int) -> str:
    text = normalize(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def iter_source_files(root: Path, *, max_files: int, max_bytes: int) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in {".md", ".txt", ".jsonl"} and root.stat().st_size <= max_bytes:
            yield root
        return

    yielded = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".jsonl"}:
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        yield path
        yielded += 1
        if max_files > 0 and yielded >= max_files:
            break


def iter_chunks(path: Path, root: Path) -> Iterable[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return

    buffer: list[str] = []
    start_line = 1

    def flush(end_line: int):
        nonlocal buffer, start_line
        text = "\n".join(buffer).strip()
        buffer = []
        if len(normalize(text)) < 40:
            return None
        return {
            "source_path": str(path),
            "relative_path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
            "line_start": start_line,
            "line_end": end_line,
            "text": text,
        }

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        is_boundary = (
            not stripped
            or stripped.startswith("## Prompt")
            or stripped.startswith("## Response")
            or bool(re.match(r"^#{1,4}\s+", stripped))
        )
        if is_boundary and buffer:
            item = flush(idx - 1)
            if item:
                yield item
            start_line = idx + 1
        if stripped:
            if not buffer:
                start_line = idx
            buffer.append(line)
    if buffer:
        item = flush(len(lines))
        if item:
            yield item


def score_chunk(text: str, query: str) -> dict:
    norm = normalize(text)
    lower = norm.lower()
    query_terms = [term for term in re.split(r"\s+", query.strip()) if term]

    proxy_hits = sum(1 for term in PROXY_LEXICON if term.lower() in lower)
    query_hits = sum(1 for term in query_terms if term.lower() in lower)
    clustered_proxy_bonus = 0.0
    proxy_positions = [
        lower.find(term.lower())
        for term in PROXY_LEXICON
        if lower.find(term.lower()) >= 0
    ]
    if len(proxy_positions) >= 2 and max(proxy_positions) - min(proxy_positions) <= 240:
        clustered_proxy_bonus = 0.12

    proxy_resonance = min(1.0, 0.10 * proxy_hits + 0.14 * query_hits + clustered_proxy_bonus)

    sentences = [item.strip() for item in re.split(r"[.!?。！？\n]+", norm) if item.strip()]
    sentence_lengths = [len(item) for item in sentences]
    if len(sentence_lengths) >= 2:
        mean = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - mean) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        length_shift = min(1.0, math.sqrt(variance) / 90.0)
    else:
        length_shift = 0.0
    punctuation_breath = min(1.0, (norm.count("?") + norm.count("!") + norm.count("...") + norm.count("…")) / 5.0)
    short_line_breath = min(1.0, sum(1 for item in sentences if len(item) <= 24) / max(1, len(sentences)))
    structural_breath = min(1.0, 0.45 * length_shift + 0.35 * punctuation_breath + 0.20 * short_line_breath)

    closure_hits = sum(1 for term in CLOSURE_LEXICON if term.lower() in lower)
    closure_pressure_penalty = min(0.8, 0.16 * closure_hits)

    total_score = max(0.0, min(1.0, 0.62 * proxy_resonance + 0.38 * structural_breath - closure_pressure_penalty))
    fixed_weight_risk = min(1.0, closure_pressure_penalty + 0.12 * max(0, closure_hits - 1))

    return {
        "proxy_resonance": round(proxy_resonance, 6),
        "structural_breath": round(structural_breath, 6),
        "closure_pressure_penalty": round(closure_pressure_penalty, 6),
        "total_score": round(total_score, 6),
        "fixed_weight_risk": round(fixed_weight_risk, 6),
        "proxy_hits": proxy_hits,
        "query_hits": query_hits,
        "closure_hits": closure_hits,
    }


def make_waypoint(chunk: dict, scores: dict, *, query: str, source_root: Path, max_excerpt: int) -> CandidateWaypoint:
    seed = f"{chunk['source_path']}:{chunk['line_start']}:{chunk['line_end']}:{query}"
    digest = hashlib.sha1(seed.encode("utf-8", errors="ignore")).hexdigest()[:12]
    generated_at = datetime.now().isoformat()
    return CandidateWaypoint(
        waypoint_id=f"wp_cand_{digest}",
        status="pending_review",
        query=query,
        provenance={
            "source_archive": str(source_root),
            "file_path": chunk["source_path"],
            "relative_path": chunk["relative_path"],
            "line_range": [chunk["line_start"], chunk["line_end"]],
            "read_only_raw_field": True,
        },
        raw_excerpt=excerpt(chunk["text"], max_excerpt),
        scores=scores,
        lifecycle={
            "decay_rate": 0.10,
            "silence_trigger": 0.40,
            "ttl_turns": 10,
        },
        guardrail={
            "promotion": "not_promoted_to_ontology",
            "past_gravity_limit": 3,
            "principle": "raw_archive_remains_unmodified_candidate_must_match_current_context",
        },
        generated_at=generated_at,
    )


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[\w가-힣]{2,}", normalize(text).lower()))


def near_duplicate(a: CandidateWaypoint, b: CandidateWaypoint) -> bool:
    a_tokens = token_set(a.raw_excerpt)
    b_tokens = token_set(b.raw_excerpt)
    if not a_tokens or not b_tokens:
        return False
    overlap = len(a_tokens & b_tokens) / max(1, len(a_tokens | b_tokens))

    if a.provenance["relative_path"] == b.provenance["relative_path"]:
        a_start, a_end = a.provenance["line_range"]
        b_start, b_end = b.provenance["line_range"]
        if abs(a_start - b_start) <= 12 or abs(a_end - b_end) <= 12:
            return overlap >= 0.70
    return overlap >= 0.82


def probe_archive(
    *,
    source: Path,
    query: str,
    limit: int,
    max_files: int,
    max_bytes: int,
    max_excerpt: int,
) -> list[CandidateWaypoint]:
    candidates: list[tuple[float, CandidateWaypoint]] = []
    source = source.resolve()
    for path in iter_source_files(source, max_files=max_files, max_bytes=max_bytes):
        for chunk in iter_chunks(path, source):
            scores = score_chunk(chunk["text"], query)
            if scores["total_score"] <= 0:
                continue
            waypoint = make_waypoint(
                chunk,
                scores,
                query=query,
                source_root=source,
                max_excerpt=max_excerpt,
            )
            candidates.append((scores["total_score"], waypoint))
    candidates.sort(key=lambda item: item[0], reverse=True)
    selected: list[CandidateWaypoint] = []
    for _, waypoint in candidates:
        if any(near_duplicate(waypoint, existing) for existing in selected):
            continue
        selected.append(waypoint)
        if len(selected) >= limit:
            break
    return selected


def write_jsonl(path: Path, waypoints: list[CandidateWaypoint], *, dry_run: bool):
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for waypoint in waypoints:
            f.write(json.dumps(asdict(waypoint), ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="우리가 나누었던 수많은 말들 중 리듬이라는 단어가 처음으로 살아 움직이기 시작했던 순간",
    )
    parser.add_argument("--source", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--max-files", type=int, default=600)
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--max-excerpt", type=int, default=700)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    waypoints = probe_archive(
        source=source,
        query=args.query,
        limit=max(1, args.limit),
        max_files=max(0, args.max_files),
        max_bytes=max(1, args.max_bytes),
        max_excerpt=max(120, args.max_excerpt),
    )
    write_jsonl(Path(args.output), waypoints, dry_run=args.dry_run)
    print(json.dumps({
        "query": args.query,
        "source": str(source),
        "limit": args.limit,
        "max_files": args.max_files,
        "hits": [asdict(waypoint) for waypoint in waypoints],
        "output": None if args.dry_run else args.output,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
