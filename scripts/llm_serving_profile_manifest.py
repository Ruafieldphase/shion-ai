#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))

from llm_serving_profiles import build_profile_manifest


OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "llm_serving_profiles_latest.json"
OUT_JSONL = OUT_DIR / "llm_serving_profiles.jsonl"
OUT_MD = OUT_DIR / "llm_serving_profiles_latest.md"


def _write_markdown(payload: dict) -> None:
    lines = [
        "# LLM Serving Profiles",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Status: `{payload['status']}`",
        f"- Principle: `{payload['principle']}`",
        "",
        "## Profiles",
        "",
        "| Name | Role | Provider fit | Stable prefix fingerprint | Prefix chars | Tail examples |",
        "|---|---|---|---|---:|---:|",
    ]
    for name, profile in payload["profiles"].items():
        lines.append(
            "| {name} | {role} | {fit} | `{fp}` | {chars} | {tails} |".format(
                name=name,
                role=profile["role"],
                fit=profile["provider_fit"],
                fp=profile["stable_prefix_fingerprint"][:16],
                chars=profile["stable_prefix_chars"],
                tails=profile["tail_examples"],
            )
        )
    lines.extend(
        [
            "",
            "## Routing",
            "",
            f"- Unconscious: {payload['routing']['unconscious']}",
            f"- Conscious: {payload['routing']['conscious']}",
            f"- Provider boundary: {payload['routing']['provider_boundary']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_profile_manifest()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    _write_markdown(payload)
    print(json.dumps({"status": payload["status"], "profiles": list(payload["profiles"].keys())}, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
