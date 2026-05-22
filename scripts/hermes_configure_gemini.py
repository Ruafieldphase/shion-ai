#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


MODEL_BLOCK = """model:
  # Configured by Shion Hermes hand-layer setup.
  # Luvit remains the execution conductor; Hermes is the Linux hand layer.
  default: "gemini-flash-latest"
  model: "gemini-flash-latest"
  provider: "gemini"
  base_url: "https://generativelanguage.googleapis.com/v1beta"
"""


def replace_model_block(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.strip() == "model:" and not line.startswith((" ", "\t")):
            start = idx
            break
    if start is None:
        return MODEL_BLOCK.rstrip() + "\n\n" + text

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if line and not line.startswith((" ", "\t", "#")):
            end = idx
            break
    return "\n".join(lines[:start] + MODEL_BLOCK.rstrip().splitlines() + lines[end:]) + "\n"


def main() -> int:
    config_path = Path.home() / ".hermes" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    original = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated = replace_model_block(original)
    config_path.write_text(updated, encoding="utf-8")
    print(f"configured Gemini route in {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

