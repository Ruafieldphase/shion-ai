#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
sys.path.insert(0, str(CORE))

from visual_axiom_field import build_ai_handoff_markdown, build_visual_axiom_field


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "visual_axiom_field_latest.json"
OUT_JSONL = OUT_DIR / "visual_axiom_field.jsonl"
OUT_MD = OUT_DIR / "visual_axiom_field_latest.md"
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
HANDOFF_PATH = HANDOFF_DIR / "visual_axiom_field.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-context", default="")
    args = parser.parse_args()

    state = build_visual_axiom_field(current_context=args.current_context)
    markdown = build_ai_handoff_markdown(state)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(state, ensure_ascii=False, separators=(",", ":")) + "\n")
    OUT_MD.write_text(markdown, encoding="utf-8")

    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    HANDOFF_PATH.write_text(markdown, encoding="utf-8")

    print(json.dumps(state, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

