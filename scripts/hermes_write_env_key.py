#!/usr/bin/env python3
from __future__ import annotations

import base64
import sys
from pathlib import Path


ALLOWED_KEYS = {"GOOGLE_API_KEY", "GEMINI_API_KEY"}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED_KEYS:
        print("usage: hermes_write_env_key.py GOOGLE_API_KEY|GEMINI_API_KEY", file=sys.stderr)
        return 2
    name = sys.argv[1]
    encoded = sys.stdin.read().lstrip("\ufeff").strip()
    if not encoded:
        print(f"{name} not provided", file=sys.stderr)
        return 2
    value = base64.b64decode(encoded.encode("ascii")).decode("utf-8").strip()
    if not value:
        print(f"{name} decoded empty", file=sys.stderr)
        return 2

    env_path = Path.home() / ".hermes" / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []

    out: list[str] = []
    written = False
    for line in lines:
        if line.startswith(f"{name}="):
            out.append(f"{name}={value}")
            written = True
        else:
            out.append(line)
    if not written:
        out.append(f"{name}={value}")

    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{name} written to {env_path} without printing value")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
