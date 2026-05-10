from __future__ import annotations

import os
from pathlib import Path

try:
    from workspace_root import get_workspace_root
except ImportError:
    def get_workspace_root() -> Path:
        env_root = os.getenv("SHION_ROOT") or os.getenv("AGI_WORKSPACE_ROOT")
        return Path(env_root).expanduser().resolve() if env_root else Path(__file__).resolve().parents[1]


ENV_OVERRIDES = {
    "shion_root": "SHION_ROOT",
    "agi_workspace_root": "AGI_WORKSPACE_ROOT",
    "workspace_root": "WORKSPACE_ROOT",
}


def _strip_inline_comment(value: str) -> str:
    in_quote = False
    quote_char = ""
    for index, char in enumerate(value):
        if char in {"'", '"'}:
            if in_quote and char == quote_char:
                in_quote = False
                quote_char = ""
            elif not in_quote:
                in_quote = True
                quote_char = char
        if char == "#" and not in_quote:
            return value[:index].strip()
    return value.strip()


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_path_config(config_path: Path | None = None) -> dict[str, str]:
    """Load the simple public paths.example.yaml format without third-party YAML."""
    root = get_workspace_root()
    path = config_path or (root / "config" / "paths.example.yaml")
    values: dict[str, str] = {}
    in_paths = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "paths:":
            in_paths = True
            continue
        if not in_paths:
            continue
        if not raw_line.startswith((" ", "\t")):
            break
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = _unquote(_strip_inline_comment(value))

    return values


def resolve_path(value: str, root: Path | None = None) -> Path | None:
    if not value:
        return None
    base = root or get_workspace_root()
    expanded = os.path.expandvars(os.path.expanduser(value))
    candidate = Path(expanded)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


def resolve_paths(config_path: Path | None = None) -> dict[str, Path | None]:
    root = get_workspace_root()
    values = load_path_config(config_path)
    resolved: dict[str, Path | None] = {}

    for key, value in values.items():
        env_name = ENV_OVERRIDES.get(key)
        if env_name and os.getenv(env_name):
            value = os.getenv(env_name, "")
        resolved[key] = resolve_path(value, root=root)

    return resolved
