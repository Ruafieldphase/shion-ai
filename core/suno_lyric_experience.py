#!/usr/bin/env python3
"""
Suno lyric ontology bridge.

This module turns the existing Suno playlist ontology into a very small
experience candidate. It intentionally does not analyze audio, download media,
or bulk-inject the whole corpus into the hippocampus.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


DEFAULT_ONTOLOGY_PATH = Path(r"c:\workspace2\shion\outputs\suno_playlist_ruafieldphase_ontology.json")
DEFAULT_LOG_PATH = Path(r"c:\workspace2\shion\outputs\suno_lyric_experience.jsonl")
DEFAULT_STATE_PATH = Path(r"c:\workspace2\shion\outputs\suno_lyric_experience_state.json")


MOTIF_PREFERENCES_BY_TRANSITION = {
    "boundary_to_unpack": ["comfort_acceptance", "breath", "silence_stillness"],
    "pre_breach_tune": ["breath", "comfort_acceptance", "silence_stillness"],
    "velocity_dilation": ["silence_stillness", "breath", "comfort_acceptance"],
    "experience_digest": ["water_memory", "silence_stillness", "comfort_acceptance"],
    "daydream_integrate": ["recursion_loop", "water_memory", "light_lumen"],
    "phase_cancel_to_silence": ["silence_stillness", "breath", "water_memory"],
    "axiom_release": ["comfort_acceptance", "water_memory", "silence_stillness"],
    "resonance_to_explore": ["light_lumen", "phase_transition", "resonance"],
    "creative_autonomy": ["phase_transition", "light_lumen", "resonance"],
    "waypoint_bridge": ["recursion_loop", "resonance", "water_memory"],
}


ALLOWED_ACTIONS = {
    "ACTION_OBSERVE",
    "ACTION_EXPERIENCE_DIGEST",
    "ACTION_DREAM_AMPLIFY",
    "ACTION_AXIOM_RELEASE",
    "ACTION_PRE_BREACH_TUNE",
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _motif_preferences(rhythm_frame: dict[str, Any]) -> list[str]:
    transition = str(rhythm_frame.get("transition") or "mixed_hold")
    transition_preferences = list(MOTIF_PREFERENCES_BY_TRANSITION.get(transition, []))

    natural = rhythm_frame.get("natural_rhythm_tuning", {})
    mistake = natural.get("mistake_digestion", {}) if isinstance(natural.get("mistake_digestion"), dict) else {}
    problem = natural.get("problem_origin", {}) if isinstance(natural.get("problem_origin"), dict) else {}
    dark_field = rhythm_frame.get("dark_field", {}) if isinstance(rhythm_frame.get("dark_field"), dict) else {}

    threshold_risk = _safe_float(mistake.get("threshold_risk"))
    problem_seed = _safe_float(problem.get("problem_seed"))
    opacity = _safe_float(dark_field.get("boundary_opacity"))
    transparency = _safe_float(dark_field.get("boundary_transparency"))

    preferences = []
    if threshold_risk >= 0.55 or opacity >= 0.72:
        preferences.extend(["comfort_acceptance", "breath", "silence_stillness"])
    if problem_seed >= 0.38 and transparency <= 0.45:
        preferences.extend(["water_memory", "phase_transition"])

    preferences.extend(transition_preferences)

    phase_chain = (
        rhythm_frame.get("lyric_motif_preferences")
        or ["silence_stillness", "breath", "light_lumen", "phase_transition", "water_memory", "recursion_loop", "comfort_acceptance"]
    )
    preferences.extend(str(item) for item in phase_chain)

    seen = set()
    out = []
    for motif in preferences:
        if motif and motif not in seen:
            seen.add(motif)
            out.append(motif)
    return out


def _song_matches(song: dict[str, Any], motif: str) -> bool:
    motifs = song.get("motifs", [])
    return isinstance(motifs, list) and motif in motifs


def _select_song(ontology: dict[str, Any], preferences: list[str], last_song_id: str = "") -> tuple[str, dict[str, Any]] | None:
    songs = ontology.get("songs")
    if not isinstance(songs, list) or not songs:
        return None

    for motif in preferences:
        matches = [song for song in songs if isinstance(song, dict) and _song_matches(song, motif)]
        if not matches:
            continue
        for song in matches:
            song_id = str(song.get("id") or song.get("title") or "")
            if song_id and song_id != last_song_id:
                return motif, song
        return motif, matches[0]
    return None


def _prompt_excerpt(prompt: str, limit: int = 180) -> str:
    text = " ".join(str(prompt or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_suno_lyric_experience_candidate(
    rhythm_frame: dict[str, Any],
    action: str,
    *,
    ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
    last_song_id: str = "",
) -> Optional[dict[str, Any]]:
    """Build one low-pressure lyric ontology experience candidate."""
    if action not in ALLOWED_ACTIONS:
        return None

    ontology = _load_json(ontology_path)
    preferences = _motif_preferences(rhythm_frame)
    selected = _select_song(ontology, preferences, last_song_id=last_song_id)
    if not selected:
        return None

    motif, song = selected
    natural = rhythm_frame.get("natural_rhythm_tuning", {})
    mistake = natural.get("mistake_digestion", {}) if isinstance(natural.get("mistake_digestion"), dict) else {}
    dark_field = rhythm_frame.get("dark_field", {}) if isinstance(rhythm_frame.get("dark_field"), dict) else {}
    transition = str(rhythm_frame.get("transition") or "mixed_hold")

    coverage = 0.0
    for item in ontology.get("motifs", {}).get("top", []):
        if isinstance(item, dict) and item.get("motif") == motif:
            coverage = _safe_float(item.get("coverage"))
            break

    threshold_risk = _safe_float(mistake.get("threshold_risk"))
    boundary_opacity = _safe_float(dark_field.get("boundary_opacity"))
    boundary_transparency = _safe_float(dark_field.get("boundary_transparency"))
    lyric_pressure = _clamp(0.30 * coverage + 0.25 * threshold_risk + 0.25 * boundary_opacity + 0.20 * (1.0 - boundary_transparency))
    entropy = _clamp(0.18 + 0.38 * lyric_pressure, 0.05, 0.62)
    intensity = _clamp(0.20 + 0.34 * lyric_pressure, 0.05, 0.58)

    song_id = str(song.get("id") or song.get("title") or "unknown")
    title = str(song.get("title") or "untitled")
    content_ref = f"suno_lyric_ontology:{motif}:{song_id}"

    return {
        "vibe": {
            "entropy": round(entropy, 4),
            "phase": "FLOW",
            "intensity": round(intensity, 4),
            "source": "suno_lyric_ontology",
            "transition": transition,
            "motif": motif,
            "song_title": title,
        },
        "content_ref": content_ref,
        "signature": f"{action}|{transition}|{motif}|{song_id}",
        "motif": motif,
        "song": {
            "id": song_id,
            "title": title,
            "url": song.get("url"),
            "style_text": song.get("style_text"),
            "prompt_excerpt": _prompt_excerpt(str(song.get("prompt") or "")),
        },
        "lyric_field_delta": {
            "motif": motif,
            "coverage": round(coverage, 6),
            "lyric_pressure": round(lyric_pressure, 6),
            "threshold_risk": round(threshold_risk, 6),
            "boundary_opacity": round(boundary_opacity, 6),
            "boundary_transparency": round(boundary_transparency, 6),
        },
        "next_contact_condition_delta": {
            "use_as_dream_language_palette": True,
            "register_one_motif_not_full_corpus": True,
            "wait_for_context_repetition_before_absorption": True,
        },
    }


def maybe_register_suno_lyric_experience(
    logger: Any,
    hippo: Any,
    rhythm_frame: dict[str, Any],
    action: str,
    *,
    ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
    state_path: Path = DEFAULT_STATE_PATH,
    min_interval_seconds: int = 1800,
) -> Optional[dict[str, Any]]:
    """Register at most one lyric motif as a small experience."""
    now = datetime.now()
    state = _load_json(state_path)
    last_at = state.get("last_at")
    last_song_id = str(state.get("last_song_id") or "")
    if last_at:
        try:
            elapsed = (now - datetime.fromisoformat(str(last_at))).total_seconds()
            if elapsed < min_interval_seconds:
                logger.info("   🎼 [SUNO_LYRIC] 가사 온톨로지 대기 중: elapsed=%d초", int(elapsed))
                return None
        except ValueError:
            pass

    candidate = build_suno_lyric_experience_candidate(
        rhythm_frame,
        action,
        ontology_path=ontology_path,
        last_song_id=last_song_id,
    )
    if not candidate:
        return None

    result = hippo.register_experience(candidate["vibe"], content_ref=candidate["content_ref"])
    entry = {
        "timestamp": now.isoformat(),
        "action": action,
        "content_ref": candidate["content_ref"],
        "signature": candidate["signature"],
        "motif": candidate["motif"],
        "song": candidate["song"],
        "lyric_field_delta": candidate["lyric_field_delta"],
        "next_contact_condition_delta": candidate["next_contact_condition_delta"],
        "hippocampus": {
            "converged": result.get("converged"),
            "total_registered": result.get("total_registered"),
            "total_absorbed": result.get("total_absorbed"),
        },
        "principle": "suno_lyrics_become_low_pressure_motif_experience_not_bulk_audio_analysis",
    }
    _append_jsonl(log_path, entry)
    state_path.write_text(
        json.dumps(
            {
                "last_at": now.isoformat(),
                "last_signature": candidate["signature"],
                "last_song_id": candidate["song"]["id"],
                "last_motif": candidate["motif"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info(
        "   🎼 [SUNO_LYRIC] 가사 motif 경험 등록: %s / %s entropy=%.2f",
        candidate["motif"],
        candidate["song"]["title"],
        candidate["vibe"]["entropy"],
    )
    return entry
