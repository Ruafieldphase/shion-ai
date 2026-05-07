#!/usr/bin/env python3
"""
Intake a public Suno playlist as lyric/rhythm ontology metadata.

This script does not generate music and does not require a private Suno API key.
It reads public playlist metadata, extracts song metadata, and compresses style
prompts into motif signals for Rhythm Information Theory.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

DEFAULT_URL = "https://suno.com/playlist/722c3707-8992-4a1c-aaa6-6633627c5238"
RAW_HTML = OUTPUTS / "suno_playlist_ruafieldphase_raw.html"
RAW_API = OUTPUTS / "suno_playlist_ruafieldphase_api_pages.json"
OUT_JSON = OUTPUTS / "suno_playlist_ruafieldphase_ontology.json"
OUT_MD = OUTPUTS / "suno_playlist_ruafieldphase_intake.md"


MOTIF_RULES: dict[str, list[str]] = {
    "breath": ["breath", "breathing", "breathe", "숨", "호흡"],
    "light_lumen": ["light", "lumen", "luminous", "빛", "루멘"],
    "water_memory": ["water", "liquid", "underwater", "memory", "remembrance", "기억", "물"],
    "recursion_loop": ["recursion", "recursive", "loop", "circular", "cycle", "continuum", "순환", "환류", "무한"],
    "phase_transition": ["phase", "transition", "threshold", "awakening", "expansion", "return", "각성", "확장", "귀환"],
    "resonance": ["resonance", "resonant", "432hz", "frequency", "공명", "주파수"],
    "comfort_acceptance": ["comfort", "comforting", "self-acceptance", "safe", "peaceful", "healing", "괜찮아", "위로"],
    "silence_stillness": ["silence", "stillness", "quiet", "ambient", "meditative", "고요", "침묵"],
    "space_cosmic": ["space", "cosmic", "celestial", "stars", "galaxy", "우주", "별"],
    "body_pulse": ["pulse", "heartbeat", "sub-bass", "bass", "body", "맥박", "심장"],
    "bilingual_voice": ["korean-english", "bilingual", "korean", "english", "female vocals", "보컬"],
}


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ShionOntologyIntake/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def _fetch_json(url: str) -> dict[str, Any]:
    return json.loads(_fetch(url))


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _duration_to_seconds(duration: str) -> int | None:
    match = re.match(r"^(\d+):(\d{2})$", duration or "")
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2))


def _safe_duration(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return ""
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def _find_song_card(anchor: Any) -> Any:
    node = anchor
    for _ in range(10):
        if node is None:
            return None
        text = _clean_text(node.get_text(" ", strip=True))
        if re.match(r"^\d+:\d{2}\s+", text) and "Remix" in text:
            return node
        node = node.parent
    return None


def _extract_style_tags(card: Any, title: str) -> list[str]:
    tags: list[str] = []
    title_norm = _clean_text(title)
    for span in card.find_all("span"):
        value = span.get("title")
        if not value:
            continue
        value = _clean_text(value)
        if not value or value == title_norm:
            continue
        if value.lower().startswith("style:"):
            pieces = [p.strip() for p in re.split(r",|\n", value) if p.strip()]
            tags.extend(pieces)
        else:
            tags.append(value)
    seen = set()
    out = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            out.append(tag)
    return out


def _extract_songs(html: str, url: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    soup = BeautifulSoup(html, "html.parser")
    text_lines = [line.strip() for line in soup.get_text("\n", strip=True).splitlines() if line.strip()]

    playlist_title = soup.title.string.replace(" | Suno", "").strip() if soup.title and soup.title.string else "Suno Playlist"
    visible_title = text_lines[1] if len(text_lines) > 1 else playlist_title
    description = ""
    for line in text_lines:
        if "정보이론" in line or "노이즈 캔슬링" in line:
            description = line
            break

    songs = []
    seen_hrefs = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        if not href.startswith("/song/") or "?" in href or href in seen_hrefs:
            continue
        title = _clean_text(anchor.get_text(" ", strip=True))
        if not title:
            continue
        card = _find_song_card(anchor)
        if card is None:
            continue
        seen_hrefs.add(href)
        card_text = _clean_text(card.get_text(" ", strip=True))
        duration_match = re.match(r"^(\d+:\d{2})\s+", card_text)
        duration = duration_match.group(1) if duration_match else ""
        version_match = re.search(r"\b(v\d(?:\.\d\+?)?)\b", card_text)
        version = version_match.group(1) if version_match else ""
        style_tags = _extract_style_tags(card, title)
        songs.append(
            {
                "index": len(songs) + 1,
                "title": title,
                "url": "https://suno.com" + href,
                "duration": duration,
                "duration_seconds": _duration_to_seconds(duration),
                "version": version,
                "style_tags": style_tags,
                "style_text": ", ".join(style_tags),
            }
        )

    playlist = {
        "title": visible_title,
        "page_title": playlist_title,
        "url": url,
        "description": description,
        "visible_song_count": len(songs),
    }
    return playlist, songs


def _api_url(url: str, page: int) -> str:
    playlist_id = url.rstrip("/").split("/")[-1]
    return f"https://studio-api.prod.suno.com/api/playlist/{playlist_id}?page={page}"


def _fetch_api_pages(url: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    page = 1
    while True:
        data = _fetch_json(_api_url(url, page))
        pages.append(data)
        clips = data.get("playlist_clips") if isinstance(data.get("playlist_clips"), list) else []
        if not clips or not data.get("next_cursor"):
            break
        page += 1
        if page > 20:
            break
    return pages


def _extract_from_api_pages(pages: list[dict[str, Any]], url: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    first = pages[0] if pages else {}
    playlist = {
        "title": str(first.get("name") or "Suno Playlist"),
        "page_title": f"{first.get('name') or 'Suno Playlist'} by @{first.get('user_handle') or ''}".strip(),
        "url": url,
        "description": str(first.get("description") or ""),
        "visible_song_count": int(first.get("num_total_results") or 0),
        "api_pages": len(pages),
        "source_endpoint": "studio-api.prod.suno.com/api/playlist",
    }

    songs: list[dict[str, Any]] = []
    seen = set()
    for page in pages:
        clips = page.get("playlist_clips") if isinstance(page.get("playlist_clips"), list) else []
        for item in clips:
            clip = item.get("clip") if isinstance(item, dict) and isinstance(item.get("clip"), dict) else {}
            song_id = str(clip.get("id") or "")
            if not song_id or song_id in seen:
                continue
            seen.add(song_id)
            metadata = clip.get("metadata") if isinstance(clip.get("metadata"), dict) else {}
            tags = str(metadata.get("tags") or "")
            style_tags = [part.strip() for part in tags.split(",") if part.strip()]
            duration_seconds = _safe_duration(metadata.get("duration"))
            songs.append(
                {
                    "index": len(songs) + 1,
                    "relative_index": item.get("relative_index"),
                    "id": song_id,
                    "title": str(clip.get("title") or ""),
                    "url": f"https://suno.com/song/{song_id}",
                    "audio_url": clip.get("audio_url"),
                    "video_url": clip.get("video_url"),
                    "image_url": clip.get("image_url"),
                    "duration": _format_duration(duration_seconds),
                    "duration_seconds": duration_seconds,
                    "version": str(clip.get("major_model_version") or metadata.get("model_name") or ""),
                    "model_name": str(clip.get("model_name") or metadata.get("model_name") or ""),
                    "style_tags": style_tags,
                    "style_text": ", ".join(style_tags),
                    "prompt": str(metadata.get("prompt") or ""),
                    "play_count": int(clip.get("play_count") or 0),
                    "created_at": clip.get("created_at"),
                }
            )
    return playlist, songs


def _motifs_for(song: dict[str, Any]) -> list[str]:
    haystack = f"{song.get('title', '')} {song.get('style_text', '')}".lower()
    motifs = []
    for motif, needles in MOTIF_RULES.items():
        if any(needle.lower() in haystack for needle in needles):
            motifs.append(motif)
    return motifs


def _summarize(playlist: dict[str, Any], songs: list[dict[str, Any]]) -> dict[str, Any]:
    motif_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    version_counts: Counter[str] = Counter()
    duration_total = 0.0
    duration_count = 0
    by_motif: dict[str, list[str]] = defaultdict(list)

    for song in songs:
        motifs = _motifs_for(song)
        song["motifs"] = motifs
        motif_counts.update(motifs)
        for motif in motifs:
            if len(by_motif[motif]) < 8:
                by_motif[motif].append(song["title"])
        tag_counts.update(tag.lower() for tag in song.get("style_tags", []))
        if song.get("version"):
            version_counts.update([song["version"]])
        if song.get("duration_seconds") is not None:
            duration_total += float(song["duration_seconds"])
            duration_count += 1

    avg_duration = round(duration_total / duration_count, 2) if duration_count else None
    top_motifs = [{"motif": k, "count": v, "coverage": round(v / max(1, len(songs)), 4)} for k, v in motif_counts.most_common()]

    phase_chain = [
        "silence_stillness",
        "breath",
        "light_lumen",
        "phase_transition",
        "water_memory",
        "recursion_loop",
        "comfort_acceptance",
    ]
    observed_chain = [motif for motif in phase_chain if motif_counts.get(motif, 0) > 0]

    return {
        "generated_at": datetime.now().isoformat(),
        "version": "suno-playlist-ontology-intake-v1",
        "source": playlist,
        "song_count": len(songs),
        "duration": {
            "total_seconds": round(duration_total, 2),
            "average_seconds": avg_duration,
        },
        "versions": dict(version_counts.most_common()),
        "motifs": {
            "top": top_motifs,
            "examples": dict(by_motif),
            "phase_chain": observed_chain,
        },
        "style_tags_top": [{"tag": k, "count": v} for k, v in tag_counts.most_common(40)],
        "ontology_compression": {
            "interpretation": "playlist_as_lyric_ontology_corpus",
            "function": "compresses personal and AGI context into repeatable rhythm motifs",
            "runtime_use": [
                "motif_seed_for_curiosity_gravity",
                "dream_replay_language_palette",
                "blender_field_label_palette",
                "future_audio_wave_analysis_manifest",
            ],
            "guardrail": "metadata_first_audio_later_no_generation_api_required",
        },
        "audio_manifest": {
            "available_audio_urls": sum(1 for song in songs if song.get("audio_url")),
            "download_policy": "manifest_only_no_audio_download_performed",
            "future_wave_features": [
                "breath_pulse",
                "silence_gap",
                "crescendo_decay",
                "loop_return",
                "emotional_density",
                "phase_transition_point",
            ],
        },
        "songs": songs,
    }


def _write_markdown(summary: dict[str, Any], path: Path) -> None:
    source = summary["source"]
    top = summary["motifs"]["top"][:12]
    tags = summary["style_tags_top"][:16]
    lines = [
        "# Suno Playlist Ontology Intake - RuaFieldPhase",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Source: [{source['title']}]({source['url']})",
        f"- Songs parsed: `{summary['song_count']}`",
        f"- Source pages: `{source.get('api_pages', 'html_snapshot')}`",
        f"- Average duration: `{summary['duration']['average_seconds']}` seconds",
        "",
        "## Role",
        "",
        "This playlist is treated as a lyric/rhythm ontology corpus, not as a music-generation API.",
        "Its metadata compresses recurring lived motifs into repeatable rhythm coordinates.",
        "",
        "## Dominant Motifs",
        "",
    ]
    for item in top:
        lines.append(f"- `{item['motif']}`: {item['count']} songs, coverage `{item['coverage']}`")

    lines.extend(["", "## Phase Chain", ""])
    lines.append(" -> ".join(f"`{m}`" for m in summary["motifs"]["phase_chain"]))

    lines.extend(["", "## Frequent Style Tags", ""])
    for item in tags:
        lines.append(f"- `{item['tag']}`: {item['count']}")

    lines.extend(
        [
            "",
            "## Runtime Mapping",
            "",
            "```yaml",
            "suno_playlist_intake:",
            "  source: rua_field_phase_playlist",
            "  role: lyric_ontology_compression_corpus",
            "  primary_use:",
            "    - motif_seed_for_curiosity_gravity",
            "    - dream_replay_language_palette",
            "    - blender_field_label_palette",
            "    - future_audio_wave_analysis_manifest",
            "  guardrail: metadata_first_audio_later_no_generation_api_required",
            "```",
            "",
            "## Audio Manifest",
            "",
            f"- Available audio URLs: `{summary['audio_manifest']['available_audio_urls']}`",
            "- Download performed: `false`",
            "- Future wave features: `breath_pulse`, `silence_gap`, `crescendo_decay`, `loop_return`, `emotional_density`, `phase_transition_point`",
            "",
            "## Outputs",
            "",
            f"- JSON: `{OUT_JSON}`",
            f"- Raw HTML snapshot: `{RAW_HTML}`",
            f"- API snapshot: `{RAW_API}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract ontology motifs from a public Suno playlist.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--html", type=Path, default=RAW_HTML)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    if not args.html_only:
        pages = _fetch_api_pages(args.url)
        RAW_API.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
        playlist, songs = _extract_from_api_pages(pages, args.url)
    else:
        if args.refresh or not args.html.exists():
            html = _fetch(args.url)
            args.html.write_text(html, encoding="utf-8")
        else:
            html = args.html.read_text(encoding="utf-8", errors="replace")
        playlist, songs = _extract_songs(html, args.url)

    summary = _summarize(playlist, songs)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(summary, OUT_MD)
    print(json.dumps({"songs": len(songs), "json": str(OUT_JSON), "markdown": str(OUT_MD)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
