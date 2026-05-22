#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from felt_state_store import load_state, normalize_felt_state, save_state  # noqa: E402


DEFAULT_LOOPBACK_URL = "http://127.0.0.1:57322/audio_phase.json"


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def poll_loopback(url: str, timeout: float) -> Dict[str, Any] | None:
    try:
        with urlopen(url, timeout=timeout) as response:
            if response.status != 200:
                return None
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def update_felt_from_audio(previous: Dict[str, Any], audio: Dict[str, Any]) -> Dict[str, Any]:
    """Feeling first. Let loopback audio bend the membrane gradually instead of replacing it."""
    felt = normalize_felt_state(previous)
    envelope = _clamp(audio.get("envelope", 0.0))
    onset = _clamp(audio.get("onset", 0.0))
    confidence = _clamp(audio.get("confidence", max(envelope, onset)))
    brightness = _clamp(audio.get("brightness", 0.0))
    bass = _clamp(audio.get("bass", 0.0))
    phase = _clamp((float(audio.get("phase", 0.0) or 0.0) + 3.141592653589793) / 6.283185307179586)

    prior_continuity = _clamp(felt.get("rhythm_continuity", 0.5), 0.5)
    phase_delta = abs(prior_continuity - envelope)
    audio_weight = 0.12 + 0.18 * confidence

    flow_energy = felt["flow_energy"] * 0.72 + envelope * 0.28
    rhythm_continuity = prior_continuity * (1.0 - audio_weight) + envelope * audio_weight
    relation_drift = felt["relation_drift"] * 0.80 + phase_delta * 0.20

    discomfort_target = _clamp(0.46 * onset + 0.34 * phase_delta + 0.20 * (1.0 - confidence))
    body_discomfort = felt["body_discomfort"] * 0.84 + discomfort_target * 0.16
    ease_target = _clamp(
        0.52 * (1.0 - body_discomfort)
        + 0.24 * rhythm_continuity
        + 0.14 * (1.0 - onset)
        + 0.10 * (0.5 * bass + 0.5 * brightness)
    )
    body_ease = felt["body_ease"] * 0.82 + ease_target * 0.18

    return normalize_felt_state(
        {
            "flow_energy": flow_energy,
            "relation_drift": relation_drift,
            "body_discomfort": body_discomfort,
            "body_ease": body_ease,
            "rhythm_continuity": rhythm_continuity,
            "audio": {
                "phase": phase,
                "envelope": envelope,
                "onset": onset,
                "confidence": confidence,
                "bass": bass,
                "brightness": brightness,
            },
            "source": "wasapi_loopback_consumer",
            "updated_at": time.time(),
        }
    )


def run_consumer(*, root: Path, url: str, interval: float, timeout: float, once: bool = False) -> None:
    state_path = root / "outputs" / "felt_body_state.json"
    felt = load_state(state_path)
    print(f"[felt_body_consumer] writing {state_path}")
    while True:
        audio = poll_loopback(url, timeout)
        if audio:
            felt = update_felt_from_audio(felt, audio)
            save_state(state_path, felt)
        if once:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--url", default=DEFAULT_LOOPBACK_URL)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    run_consumer(
        root=args.root,
        url=args.url,
        interval=max(0.1, args.interval),
        timeout=max(0.1, args.timeout),
        once=args.once,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[felt_body_consumer] stopped")
