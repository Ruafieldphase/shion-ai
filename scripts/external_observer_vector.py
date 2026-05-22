#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
sys.path.insert(0, str(CORE))

from external_observer_vector import build_external_observer_vector_state


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "external_observer_vector_latest.json"
OUT_JSONL = OUT_DIR / "external_observer_vector.jsonl"
OUT_MD = OUT_DIR / "external_observer_vector_latest.md"
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
HANDOFF_LATEST = HANDOFF_DIR / "latest.md"

SOURCES = {
    "context_gradient": OUT_DIR / "contextual_execution_gradient_latest.json",
    "dark_field_threshold": OUT_DIR / "dark_field_threshold_latest.json",
    "limb_field": ROOT / "outputs" / "embodied_limb_field_latest.json",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def write_markdown(payload: dict[str, Any]) -> None:
    request = payload.get("observer_request") if isinstance(payload.get("observer_request"), dict) else {}
    next_contact = payload.get("next_contact") if isinstance(payload.get("next_contact"), dict) else {}
    signals = payload.get("signals") if isinstance(payload.get("signals"), dict) else {}
    lines = [
        "# External Observer Vector",
        "",
        f"- mode: `{payload.get('mode')}`",
        f"- need_external_observer: `{payload.get('need_external_observer')}`",
        f"- next action: `{next_contact.get('action')}`",
        f"- question_pressure: `{signals.get('question_pressure')}`",
        f"- ambiguity: `{signals.get('ambiguity')}`",
        f"- destination_absence: `{signals.get('destination_absence')}`",
        f"- internal_reflection_stall: `{signals.get('internal_reflection_stall')}`",
        "",
        next_contact.get("meaning", ""),
    ]
    prompt = request.get("prompt")
    if prompt:
        lines.extend(["", "## Handoff Prompt", "", "```text", str(prompt), "```"])
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_handoff(payload: dict[str, Any]) -> None:
    request = payload.get("observer_request") if isinstance(payload.get("observer_request"), dict) else {}
    prompt = str(request.get("prompt") or "").strip()
    if not prompt:
        return

    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    HANDOFF_LATEST.write_text(
        "# Antigravity Handoff\n\n"
        "Copy this to Shion/Antigravity only if the current work still feels blocked or over-linearized.\n\n"
        "```text\n"
        f"{prompt}\n"
        "```\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-context", default="")
    parser.add_argument("--uncertainty", type=float, default=0.0)
    parser.add_argument("--blockage", type=float, default=0.0)
    parser.add_argument("--force-request", action="store_true")
    args = parser.parse_args()

    payload = build_external_observer_vector_state(
        context_gradient=read_json(SOURCES["context_gradient"]),
        dark_field_threshold=read_json(SOURCES["dark_field_threshold"]),
        limb_field=read_json(SOURCES["limb_field"]),
        issue_context=args.issue_context,
        uncertainty=args.uncertainty,
        blockage=args.blockage,
        force_request=args.force_request,
    )
    payload["source_files"] = {
        key: {"path": str(path), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}
        for key, path in SOURCES.items()
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_markdown(payload)
    write_handoff(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

