#!/usr/bin/env python3
"""
Create a local music media manifest and link it to the Suno ontology manifest.

The script only reads metadata. It does not copy, transcode, or upload media.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
DEFAULT_MUSIC_DIR = Path(r"D:\ARCHIVE_WORKSPACE\agi\music")
SUNO_ONTOLOGY = OUTPUTS / "suno_playlist_ruafieldphase_ontology.json"
OUT_JSON = OUTPUTS / "local_music_media_manifest.json"
OUT_MD = OUTPUTS / "local_music_media_intake.md"

MEDIA_EXTENSIONS = {".mp3", ".wav", ".mp4", ".m4a", ".flac", ".aac"}


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _normalize_title(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"\[[^\]]*\]", " ", value)
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\bv\d+\b", " ", value)
    value = re.sub(r"\b\d+min\b", " ", value)
    value = re.sub(r"\bversion\b", " ", value)
    value = re.sub(r"\bmusic focus\b", " ", value)
    value = re.sub(r"[^0-9a-z가-힣♭#]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _duration_label(seconds: float | None) -> str:
    if seconds is None:
        return ""
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def _probe(path: Path, timeout: float = 10.0) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,bit_rate:stream=codec_type,codec_name,width,height,sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        if proc.returncode != 0:
            return {"ok": False, "error": proc.stderr.strip()[:400]}
        data = json.loads(proc.stdout or "{}")
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}

    fmt = data.get("format") if isinstance(data.get("format"), dict) else {}
    streams = data.get("streams") if isinstance(data.get("streams"), list) else []
    duration = None
    try:
        if fmt.get("duration") is not None:
            duration = float(fmt["duration"])
    except Exception:
        duration = None
    return {
        "ok": True,
        "duration_seconds": round(duration, 3) if duration is not None else None,
        "duration": _duration_label(duration),
        "bit_rate": fmt.get("bit_rate"),
        "streams": streams,
    }


def _best_song_match(file_title: str, songs: list[dict[str, Any]]) -> dict[str, Any] | None:
    norm = _normalize_title(file_title)
    if not norm:
        return None
    best: tuple[float, dict[str, Any] | None] = (0.0, None)
    for song in songs:
        song_title = str(song.get("title") or "")
        candidate = _normalize_title(song_title)
        if not candidate:
            continue
        score = SequenceMatcher(None, norm, candidate).ratio()
        if candidate in norm or norm in candidate:
            score = max(score, 0.92)
        if score > best[0]:
            best = (score, song)
    if best[1] is None:
        return None
    return {
        "score": round(best[0], 4),
        "suno_index": best[1].get("index"),
        "suno_id": best[1].get("id"),
        "suno_title": best[1].get("title"),
        "suno_url": best[1].get("url"),
        "motifs": best[1].get("motifs", []),
    }


def build_manifest(music_dir: Path, probe: bool) -> dict[str, Any]:
    suno = _load_json(SUNO_ONTOLOGY, {})
    suno_songs = suno.get("songs") if isinstance(suno.get("songs"), list) else []

    files = []
    extension_counts: Counter[str] = Counter()
    total_bytes = 0
    matched = 0
    strong_matched = 0
    duration_total = 0.0
    duration_count = 0

    for path in sorted(music_dir.rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in MEDIA_EXTENSIONS and ext not in {".json", ".m3u", ".png"}:
            continue
        stat = path.stat()
        extension_counts.update([ext or "<none>"])
        total_bytes += stat.st_size
        item: dict[str, Any] = {
            "path": str(path),
            "name": path.name,
            "stem": path.stem,
            "extension": ext,
            "bytes": stat.st_size,
            "last_write_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        if ext in MEDIA_EXTENSIONS:
            item["match"] = _best_song_match(path.stem, suno_songs)
            if item["match"]:
                matched += 1
                if float(item["match"]["score"]) >= 0.86:
                    strong_matched += 1
            if probe:
                media = _probe(path)
                item["media"] = media
                if media.get("ok") and media.get("duration_seconds") is not None:
                    duration_total += float(media["duration_seconds"])
                    duration_count += 1
        files.append(item)

    return {
        "generated_at": datetime.now().isoformat(),
        "version": "local-music-media-manifest-v1",
        "music_dir": str(music_dir),
        "policy": "metadata_only_no_copy_no_transcode_no_upload",
        "counts": {
            "files": len(files),
            "media_files": sum(1 for item in files if item["extension"] in MEDIA_EXTENSIONS),
            "extensions": dict(extension_counts.most_common()),
            "total_bytes": total_bytes,
            "total_gb": round(total_bytes / (1024**3), 4),
            "matched_to_suno": matched,
            "strong_matched_to_suno": strong_matched,
        },
        "duration": {
            "probed": probe,
            "media_with_duration": duration_count,
            "total_seconds": round(duration_total, 3),
            "average_seconds": round(duration_total / duration_count, 3) if duration_count else None,
        },
        "source_links": {
            "suno_ontology": str(SUNO_ONTOLOGY),
            "suno_song_count": len(suno_songs),
        },
        "runtime_use": [
            "local_audio_wave_analysis_source",
            "mp4_lyric_video_source",
            "motif_to_wave_feature_alignment",
            "future_blender_audio_reactivity",
        ],
        "files": files,
    }


def write_markdown(manifest: dict[str, Any]) -> None:
    counts = manifest["counts"]
    duration = manifest["duration"]
    lines = [
        "# Local Music Media Intake",
        "",
        f"- Generated: `{manifest['generated_at']}`",
        f"- Source folder: `{manifest['music_dir']}`",
        f"- Policy: `{manifest['policy']}`",
        f"- Files: `{counts['files']}`",
        f"- Media files: `{counts['media_files']}`",
        f"- Total size: `{counts['total_gb']}` GB",
        f"- Matched to Suno metadata: `{counts['matched_to_suno']}`",
        f"- Strong title matches: `{counts['strong_matched_to_suno']}`",
        f"- Duration probed: `{duration['probed']}`",
        f"- Media with duration: `{duration['media_with_duration']}`",
        f"- Average duration: `{duration['average_seconds']}` seconds",
        "",
        "## Extension Counts",
        "",
    ]
    for ext, count in counts["extensions"].items():
        lines.append(f"- `{ext}`: {count}")
    lines.extend(
        [
            "",
            "## Runtime Mapping",
            "",
            "```yaml",
            "local_music_media:",
            "  role: local_wave_source_for_lyric_ontology",
            "  policy: metadata_only_no_copy_no_transcode_no_upload",
            "  current_use:",
            "    - title_and_duration_manifest",
            "    - suno_metadata_alignment",
            "  next_use:",
            "    - breath_pulse",
            "    - silence_gap",
            "    - crescendo_decay",
            "    - loop_return",
            "    - emotional_density",
            "    - phase_transition_point",
            "```",
            "",
            "## Outputs",
            "",
            f"- JSON: `{OUT_JSON}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local music media manifest.")
    parser.add_argument("--music-dir", type=Path, default=DEFAULT_MUSIC_DIR)
    parser.add_argument("--no-probe", action="store_true")
    args = parser.parse_args()

    manifest = build_manifest(args.music_dir, probe=not args.no_probe)
    OUT_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(manifest)
    print(json.dumps({"files": manifest["counts"]["files"], "media": manifest["counts"]["media_files"], "json": str(OUT_JSON), "markdown": str(OUT_MD)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
