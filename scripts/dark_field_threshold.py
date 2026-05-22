#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from dark_field_threshold import build_dark_field_threshold_state


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "dark_field_threshold_latest.json"
OUT_JSONL = OUT_DIR / "dark_field_threshold.jsonl"
OUT_MD = OUT_DIR / "dark_field_threshold_latest.md"

SOURCES = {
    "felt_state": ROOT / "outputs" / "felt_body_state.json",
    "prediction_trace": ROOT / "outputs" / "field_prediction_errors.jsonl",
    "boundary_state": OUT_DIR / "boundary_aperture_latest.json",
    "execution_gradient": OUT_DIR / "contextual_execution_gradient_latest.json",
}


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _read_jsonl_tail(path: Path, limit: int = 1) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[-limit:]:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _source_summary() -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for name, path in SOURCES.items():
        summary[name] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            summary[name]["bytes"] = path.stat().st_size
    return summary


def _write_markdown(payload: Dict[str, Any]) -> None:
    threshold = payload["threshold"]
    lines = [
        "# Dark Field Threshold",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Next action: `{payload['next_contact']['action']}`",
        f"- Tail limit: `{payload['next_contact']['tail_limit_chars']}`",
        f"- Middle destination active: `{payload['middle_destination']['active']}`",
        "",
        "## Threshold",
        "",
        "| Signal | Value |",
        "|---|---:|",
    ]
    for key in (
        "context_contact",
        "context_potential_energy",
        "dark_field_pressure",
        "dynamic_threshold",
        "threshold_margin",
        "processing_slice",
    ):
        lines.append(f"| `{key}` | `{threshold[key]}` |")
    lines.extend(
        [
            "",
            "## Meaning",
            "",
            payload["next_contact"]["meaning"],
            "",
            "This is not a fixed constant, not a therapy protocol, and not a hard rule. It opens a dark-field coordinate only when the present context touches it, and only by the currently processable slice.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload() -> Dict[str, Any]:
    prediction_tail = _read_jsonl_tail(SOURCES["prediction_trace"], limit=1)
    state = build_dark_field_threshold_state(
        felt_state=_read_json(SOURCES["felt_state"]),
        prediction_trace=prediction_tail[-1] if prediction_tail else {},
        boundary_state=_read_json(SOURCES["boundary_state"]),
        execution_gradient=_read_json(SOURCES["execution_gradient"]),
    )
    state["source_files"] = _source_summary()
    return state


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    _write_markdown(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "mode": payload["mode"],
                "threshold": payload["threshold"],
                "next_contact": payload["next_contact"],
            },
            ensure_ascii=False,
        )
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
