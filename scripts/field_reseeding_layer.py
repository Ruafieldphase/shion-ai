#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from field_reseeding_layer import build_field_reseeding_state


OUTPUTS = ROOT / "outputs"
OUT_JSON = OUTPUTS / "field_reseeding_latest.json"
OUT_JSONL = OUTPUTS / "field_reseeding.jsonl"

SOURCES = {
    "natural_boundary": OUTPUTS / "natural_boundary_router_latest.json",
    "field_heart": OUTPUTS / "field_heart_state_latest.json",
    "field_intent": OUTPUTS / "field_intent_latest.json",
    "previous_reseeding": OUT_JSON,
}


def read_json(path: Path) -> Dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def source_summary() -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for name, path in SOURCES.items():
        summary[name] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            summary[name]["bytes"] = path.stat().st_size
    return summary


def build_payload() -> Dict[str, Any]:
    state = build_field_reseeding_state(
        natural_boundary_state=read_json(SOURCES["natural_boundary"]),
        field_heart_state=read_json(SOURCES["field_heart"]),
        field_intent=read_json(SOURCES["field_intent"]),
        previous_reseeding_state=read_json(SOURCES["previous_reseeding"]),
    )
    state["source_files"] = source_summary()
    return state


def main() -> int:
    payload = build_payload()
    write_json_atomic(OUT_JSON, payload)
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps({"mode": payload["mode"], "patterns": payload["detected_tangled_patterns"], "next_contact": payload["next_contact"]}, ensure_ascii=False, indent=2))
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
