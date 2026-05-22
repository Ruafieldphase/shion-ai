#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from boundary_aperture_loop import build_boundary_aperture_state


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "boundary_aperture_latest.json"
OUT_JSONL = OUT_DIR / "boundary_aperture.jsonl"
OUT_MD = OUT_DIR / "boundary_aperture_latest.md"

SOURCES = {
    "felt_state": ROOT / "outputs" / "felt_body_state.json",
    "prediction_trace": ROOT / "outputs" / "field_prediction_errors.jsonl",
    "experience_feedback": ROOT / "outputs" / "experience_feedback.jsonl",
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
    aperture = payload["aperture"]
    profile = payload["serving_profile_bias"]
    lines = [
        "# Boundary Aperture Loop",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Next action: `{payload['next_contact']['action']}`",
        f"- Preferred profile: `{profile['preferred_profile']}`",
        f"- Tail limit: `{profile['tail_limit_chars']}`",
        "",
        "## Aperture",
        "",
        "| Signal | Value |",
        "|---|---:|",
    ]
    for key in (
        "opening_pressure",
        "closing_pressure",
        "internal_reflection",
        "boundary_aperture",
        "permeability",
        "digestion_bias",
    ):
        lines.append(f"| `{key}` | `{aperture[key]}` |")
    lines.extend(
        [
            "",
            "## Meaning",
            "",
            profile["meaning"],
            "",
            "This is not a life claim and not a hard rule. It is a small membrane reading from felt state, prediction error, experience feedback, and the current contextual gradient.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload() -> Dict[str, Any]:
    prediction_tail = _read_jsonl_tail(SOURCES["prediction_trace"], limit=1)
    feedback_tail = _read_jsonl_tail(SOURCES["experience_feedback"], limit=1)
    state = build_boundary_aperture_state(
        felt_state=_read_json(SOURCES["felt_state"]),
        prediction_trace=prediction_tail[-1] if prediction_tail else {},
        experience_feedback=feedback_tail[-1] if feedback_tail else {},
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
    print(json.dumps({"status": payload["status"], "mode": payload["mode"], "next_contact": payload["next_contact"]}, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
