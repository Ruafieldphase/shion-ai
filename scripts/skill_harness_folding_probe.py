#!/usr/bin/env python3
"""Write the current skill harness folding read to outputs."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from skill_harness_folding import fold_skill_harness  # noqa: E402


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _registry_skills() -> list[dict]:
    from action_executor import ACTION_REGISTRY

    skills = []
    for name, meta in ACTION_REGISTRY.items():
        skills.append(
            {
                "name": name,
                "resonance": 0.5,
                "phase": 0.0,
                "experience": 0,
                "atp_cost": meta.get("atp_cost", 0),
                "keywords": meta.get("keywords", []),
                "frequency_range": meta.get("frequency_range", (0.0, 0.0)),
            }
        )
    return skills


def main() -> int:
    outputs = ROOT / "outputs"
    outputs.mkdir(exist_ok=True)

    rhythm_trace = outputs / "rhythm_ir_trace.jsonl"
    latest_rhythm = {}
    if rhythm_trace.exists():
        lines = [line for line in rhythm_trace.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            latest_rhythm = json.loads(lines[-1])

    field_energy = _load_json(outputs / "field_energy.json")
    runtime = {
        "core_gravity": field_energy.get("earth_core_gravity"),
        "phase_noise": latest_rhythm.get("interference", {}).get("destructive"),
        "action_pressure": latest_rhythm.get("action_amplitude"),
        "silence_need": latest_rhythm.get("silence_need"),
        "observer_resistance": latest_rhythm.get("dark_field", {}).get("resistance"),
        "available_atp": field_energy.get("atp", 50.0),
        "interference": latest_rhythm.get("interference", {}),
        "dark_field": latest_rhythm.get("dark_field", {}),
    }
    import argparse

    parser = argparse.ArgumentParser(description="Skill harness folding probe.")
    parser.add_argument(
        "--potential-text",
        type=str,
        default=None,
        help="Raw text/dialogue to extract unnamed potential residues from.",
    )
    parser.add_argument(
        "intent_keywords",
        nargs="*",
        default=["field", "rhythm", "fold", "observe"],
        help="Intent keywords for pocket binding.",
    )

    args = parser.parse_args()

    folded = fold_skill_harness(
        _registry_skills(),
        runtime,
        intent_keywords=args.intent_keywords,
        potential_text=args.potential_text,
    )
    folded["timestamp"] = datetime.now().isoformat()
    folded["source"] = "skill_harness_folding_probe"
    folded["intent_keywords"] = args.intent_keywords

    out = outputs / "skill_harness_folding_latest.json"
    out.write_text(json.dumps(folded, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Harness folded: {out}")
    if args.potential_text:
        potentials_extracted = [r["name"] for r in folded["residues"] if r.get("is_potential")]
        print(f"Extracted potential residues: {potentials_extracted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
