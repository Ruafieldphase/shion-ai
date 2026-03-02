from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _resolve_from_env() -> Optional[Path]:
    env_root = os.getenv("SHION_ROOT") or os.getenv("AGI_WORKSPACE_ROOT")
    if not env_root:
        return None
    try:
        candidate = Path(env_root).expanduser().resolve()
    except Exception:
        return None
    if candidate.exists():
        return candidate
    return None


def _resolve_from_file() -> Path:
    # This file lives in {shion_root}/core/, so parent is shion root.
    return Path(__file__).resolve().parents[1]


def get_workspace_root() -> Path:
    env_root = _resolve_from_env()
    if env_root:
        return env_root
    return _resolve_from_file()


WORKSPACE_ROOT = get_workspace_root()
