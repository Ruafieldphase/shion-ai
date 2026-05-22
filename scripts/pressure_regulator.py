#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from pressure_regulator import build_pressure_regulator_state


OUTPUTS = ROOT / "outputs"
OUT_JSON = OUTPUTS / "pressure_regulator_latest.json"
OUT_JSONL = OUTPUTS / "pressure_regulator.jsonl"

SOURCES = {
    "field_heart": OUTPUTS / "field_heart_state_latest.json",
    "felt_state": OUTPUTS / "felt_body_state.json",
    "prediction_trace": OUTPUTS / "field_prediction_errors.jsonl",
    "boundary_state": OUTPUTS / "hermes" / "boundary_aperture_latest.json",
    "dark_field_state": OUTPUTS / "hermes" / "dark_field_threshold_latest.json",
    "field_intent": OUTPUTS / "field_intent_latest.json",
}


def read_json(path: Path) -> Dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def read_latest_jsonl(path: Path) -> Dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def source_summary() -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for name, path in SOURCES.items():
        summary[name] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            summary[name]["bytes"] = path.stat().st_size
    return summary


def build_payload() -> Dict[str, Any]:
    state = build_pressure_regulator_state(
        field_heart_state=read_json(SOURCES["field_heart"]),
        felt_state=read_json(SOURCES["felt_state"]),
        prediction_trace=read_latest_jsonl(SOURCES["prediction_trace"]),
        boundary_state=read_json(SOURCES["boundary_state"]),
        dark_field_state=read_json(SOURCES["dark_field_state"]),
        field_intent=read_json(SOURCES["field_intent"]),
    )
    state["source_files"] = source_summary()
    return state


def write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    payload = build_payload()
    write_json_atomic(OUT_JSON, payload)
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps({"pressure": payload["pressure"], "handling": payload["handling"]}, ensure_ascii=False, indent=2))
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
