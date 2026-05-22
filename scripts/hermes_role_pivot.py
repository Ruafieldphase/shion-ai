#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "hermes_role_latest.json"
OUT_JSONL = OUT_DIR / "hermes_role.jsonl"


SOURCE_PATHS = [
    OUT_DIR / "natural_flow_pivot_latest.json",
    OUT_DIR / "windows_native_flow_latest.json",
    OUT_DIR / "model_route_probe_latest.json",
    OUT_DIR / "local_gemma_route_probe_latest.json",
]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def build_role() -> dict[str, Any]:
    sources = []
    for path in SOURCE_PATHS:
        data = _read_json(path)
        sources.append(
            {
                "path": str(path),
                "exists": data is not None,
                "status": data.get("status") if data else None,
                "field": data.get("field") if data else None,
                "timestamp": data.get("timestamp") if data else None,
            }
        )

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "hermes_optional_hand_parked",
        "role": "optional_hand_not_default_body",
        "decision": {
            "do_not_autostart": True,
            "do_not_make_conductor": True,
            "do_not_require_linux": True,
            "use_when_called_for_bounded_probe": True,
        },
        "allowed_when_called": [
            "search its own memory/session history",
            "run bounded read-only probes",
            "summarize resistance as experience particles",
            "propose patches as text",
        ],
        "not_default_now": [
            "autonomous daemon",
            "required Linux hand layer",
            "workspace mutation authority",
            "daily runtime switchboard",
        ],
        "next_particle": {
            "action": "leave_hermes_parked",
            "meaning": "Use Windows native flow first; call Hermes only if a concrete bounded hand task appears.",
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "sources": sources,
        "principle": "hands_are_useful_only_when_the_field_calls_for_touch",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_role()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
