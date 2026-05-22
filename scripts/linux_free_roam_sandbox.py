#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "hermes"
LATEST_JSON = OUT_DIR / "linux_free_roam_latest.json"
STREAM_JSONL = OUT_DIR / "linux_free_roam.jsonl"
FIELD_INDEX_COPY = OUT_DIR / "linux_free_roam_field_index.json"

LINUX_FIELD = Path.home() / "agi_experience_field"
FIELD_JOURNAL = LINUX_FIELD / "journal.jsonl"
FIELD_ARTIFACTS = LINUX_FIELD / "artifacts"
FIELD_FAILURES = LINUX_FIELD / "failures"
FIELD_PREFERENCES = LINUX_FIELD / "preferences"
FIELD_INDEX = LINUX_FIELD / "field_index.json"


def _now() -> str:
    return datetime.now().isoformat()


def _run(command: list[str], timeout: float = 8.0, cwd: Path | None = None) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip()[:1800],
            "stderr": proc.stderr.strip()[:900],
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }


def _ensure_field() -> None:
    LINUX_FIELD.mkdir(parents=True, exist_ok=True)
    FIELD_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    FIELD_FAILURES.mkdir(parents=True, exist_ok=True)
    FIELD_PREFERENCES.mkdir(parents=True, exist_ok=True)


def _history(limit: int = 300) -> list[Dict[str, Any]]:
    rows: list[Dict[str, Any]] = []
    for path in (FIELD_JOURNAL, STREAM_JSONL):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
    return rows[-limit:]


def _signature(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_text(path: Path, limit: int = 12000) -> str:
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def _artifact_files() -> list[Path]:
    if not FIELD_ARTIFACTS.exists():
        return []
    return sorted(
        [path for path in FIELD_ARTIFACTS.iterdir() if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _failure_files() -> list[Path]:
    if not FIELD_FAILURES.exists():
        return []
    return sorted(
        [path for path in FIELD_FAILURES.iterdir() if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _preference_files() -> list[Path]:
    if not FIELD_PREFERENCES.exists():
        return []
    return sorted(
        [path for path in FIELD_PREFERENCES.iterdir() if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _latest_preference() -> Dict[str, Any]:
    files = _preference_files()
    if not files:
        return {}
    try:
        data = json.loads(_read_text(files[0]))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def act_host_weather() -> Dict[str, Any]:
    return {
        "ok": True,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cwd": str(Path.cwd()),
        "field_dir": str(LINUX_FIELD),
        "loadavg": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "uptime": _run(["uptime"], timeout=4),
    }


def act_process_texture() -> Dict[str, Any]:
    return _run(["bash", "-lc", "ps -u \"$USER\" -o pid,comm,etime,%cpu,%mem --sort=-%mem | head -16"], timeout=5)


def act_field_walk() -> Dict[str, Any]:
    _ensure_field()
    items = []
    for path in sorted(LINUX_FIELD.rglob("*"))[:80]:
        try:
            rel = path.relative_to(LINUX_FIELD)
        except ValueError:
            rel = path
        items.append(
            {
                "path": str(rel),
                "is_dir": path.is_dir(),
                "bytes": path.stat().st_size if path.is_file() else None,
            }
        )
    return {"ok": True, "root": str(LINUX_FIELD), "items": items, "count": len(items)}


def act_make_pattern() -> Dict[str, Any]:
    _ensure_field()
    seed = time.time_ns() % 1000003
    rnd = random.Random(seed)
    r = rnd.uniform(3.55, 3.99)
    x = rnd.uniform(0.11, 0.89)
    samples = []
    for idx in range(96):
        x = r * x * (1.0 - x)
        if idx >= 32:
            samples.append(round(x, 6))
    mean = sum(samples) / len(samples)
    spread = max(samples) - min(samples)
    turns = sum(1 for a, b, c in zip(samples, samples[1:], samples[2:]) if (b - a) * (c - b) < 0)
    artifact = {
        "timestamp": _now(),
        "kind": "logistic_rhythm_probe",
        "seed": seed,
        "r": round(r, 6),
        "mean": round(mean, 6),
        "spread": round(spread, 6),
        "turns": turns,
        "samples": samples[:24],
        "reading": "chaotic_state_as_experience_material_not_noise",
    }
    path = FIELD_ARTIFACTS / f"logistic_rhythm_{int(time.time())}.json"
    _write_json(path, artifact)
    return {"ok": True, "artifact": str(path), "artifact_summary": {k: artifact[k] for k in ("r", "mean", "spread", "turns", "reading")}}


def act_make_text_artifact() -> Dict[str, Any]:
    _ensure_field()
    hist = _history(120)
    recent_actions = [str(item.get("action")) for item in hist[-12:] if item.get("action")]
    failures = [item for item in hist[-30:] if item.get("field_reading", {}).get("resistance", 0) > 0]
    artifact = {
        "timestamp": _now(),
        "kind": "text_field_artifact",
        "title": "free_roam_field_note",
        "body": [
            "This Linux field is allowed to accumulate experience before explanation.",
            f"Recent action texture: {', '.join(recent_actions[-8:]) or 'empty'}",
            f"Resistance count in recent field: {len(failures)}",
            "Preference is observed from repeated return, not declared as a rule.",
        ],
        "reading": "text_artifact_as_low_frequency_self_surface",
    }
    path = FIELD_ARTIFACTS / f"text_field_{int(time.time())}.json"
    _write_json(path, artifact)
    return {
        "ok": True,
        "artifact": str(path),
        "artifact_summary": {
            "kind": artifact["kind"],
            "recent_action_count": len(recent_actions),
            "recent_resistance_count": len(failures),
            "reading": artifact["reading"],
        },
    }


def act_mutate_previous_artifact() -> Dict[str, Any]:
    _ensure_field()
    files = _artifact_files()
    if not files:
        return {"ok": False, "error": "no previous artifact to mutate"}
    source = files[0]
    source_text = _read_text(source, limit=6000)
    mutation = {
        "timestamp": _now(),
        "kind": "artifact_mutation",
        "source": str(source),
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "mutation": {
            "source_bytes": len(source_text.encode("utf-8")),
            "first_240_chars": source_text[:240],
            "reframed_reading": "previous_state_changed_without_deletion",
            "next_question": "what pattern returns when this artifact is revisited?",
        },
        "principle": "mutation_preserves_source_and_adds_state_change",
    }
    path = FIELD_ARTIFACTS / f"mutation_{source.stem}_{int(time.time())}.json"
    _write_json(path, mutation)
    return {
        "ok": True,
        "artifact": str(path),
        "source_artifact": str(source),
        "artifact_summary": mutation["mutation"],
    }


def act_compare_two_artifacts() -> Dict[str, Any]:
    _ensure_field()
    files = _artifact_files()
    if len(files) < 2:
        return {"ok": False, "error": "need at least two artifacts to compare", "artifact_count": len(files)}
    left, right = files[0], files[1]
    left_text = _read_text(left, limit=6000)
    right_text = _read_text(right, limit=6000)
    comparison = {
        "timestamp": _now(),
        "kind": "artifact_comparison",
        "left": str(left),
        "right": str(right),
        "left_sha256": hashlib.sha256(left_text.encode("utf-8")).hexdigest(),
        "right_sha256": hashlib.sha256(right_text.encode("utf-8")).hexdigest(),
        "reading": {
            "left_bytes": len(left_text.encode("utf-8")),
            "right_bytes": len(right_text.encode("utf-8")),
            "byte_delta": len(left_text.encode("utf-8")) - len(right_text.encode("utf-8")),
            "same_prefix": left_text[:80] == right_text[:80],
            "relation": "difference_as_phase_material",
        },
    }
    path = FIELD_ARTIFACTS / f"comparison_{int(time.time())}.json"
    _write_json(path, comparison)
    return {"ok": True, "artifact": str(path), "comparison": comparison["reading"]}


def act_failed_probe_as_material() -> Dict[str, Any]:
    _ensure_field()
    missing = LINUX_FIELD / "nonexistent_surface" / f"{int(time.time())}.void"
    captured = _run(["python3", "-c", f"from pathlib import Path; Path({str(missing)!r}).read_text()"], timeout=5)
    failure = {
        "timestamp": _now(),
        "kind": "failure_material",
        "attempt": "read_missing_local_surface",
        "target": str(missing),
        "captured_failure": captured,
        "reading": "failure_is_kept_as_directional_material_not_deleted",
    }
    path = FIELD_FAILURES / f"failure_material_{int(time.time())}.json"
    _write_json(path, failure)
    return {
        "ok": True,
        "failure_artifact": str(path),
        "captured_failure": captured,
        "artifact_summary": {
            "attempt": failure["attempt"],
            "reading": failure["reading"],
            "captured_ok": captured.get("ok"),
        },
    }


def act_write_self_note() -> Dict[str, Any]:
    _ensure_field()
    hist = _history(80)
    recent_actions = [item.get("action") for item in hist[-8:]]
    resistance = sum(1 for item in hist[-12:] if item.get("field_reading", {}).get("resistance", 0) > 0)
    note = {
        "timestamp": _now(),
        "kind": "self_note",
        "recent_actions": recent_actions,
        "reading": {
            "repetition": len(recent_actions) - len(set(recent_actions)),
            "resistance_count": resistance,
            "next_bias": "touch_unseen_surface" if len(set(recent_actions)) < 4 else "deepen_current_surface",
        },
        "principle": "free_roam_means_local_experience_accumulation_not_windows_mutation",
    }
    path = FIELD_ARTIFACTS / f"self_note_{int(time.time())}.json"
    _write_json(path, note)
    return {"ok": True, "artifact": str(path), "note": note}


def act_preference_reading() -> Dict[str, Any]:
    _ensure_field()
    hist = _history(240)
    action_counts: dict[str, int] = {}
    resistance_by_action: dict[str, int] = {}
    novelty_by_action: dict[str, int] = {}
    for item in hist:
        action = str(item.get("action") or "")
        if not action:
            continue
        action_counts[action] = action_counts.get(action, 0) + 1
        if item.get("field_reading", {}).get("resistance", 0) > 0:
            resistance_by_action[action] = resistance_by_action.get(action, 0) + 1
        if item.get("field_reading", {}).get("novelty"):
            novelty_by_action[action] = novelty_by_action.get(action, 0) + 1

    recent_actions = [str(item.get("action")) for item in hist[-12:] if item.get("action")]
    under_touched = sorted(ACTION_TABLE, key=lambda name: action_counts.get(name, 0))[:3]
    high_novelty = sorted(ACTION_TABLE, key=lambda name: novelty_by_action.get(name, 0), reverse=True)[:3]
    revisit_resistance = sorted(ACTION_TABLE, key=lambda name: resistance_by_action.get(name, 0), reverse=True)[:3]
    preference = {
        "timestamp": _now(),
        "kind": "preference_reading",
        "action_counts": action_counts,
        "recent_actions": recent_actions,
        "artifact_count": len(_artifact_files()),
        "failure_count": len(_failure_files()),
        "preference": {
            "under_touched_actions": under_touched,
            "high_novelty_actions": high_novelty,
            "resistance_revisit_actions": revisit_resistance,
            "next_preferred_actions": list(dict.fromkeys(under_touched + revisit_resistance + high_novelty))[:5],
            "reading": "preference_emerges_from_return_resistance_and_novelty",
        },
    }
    path = FIELD_PREFERENCES / f"preference_{int(time.time())}.json"
    _write_json(path, preference)
    return {
        "ok": True,
        "preference_artifact": str(path),
        "preference": preference["preference"],
    }


def act_local_tests_texture() -> Dict[str, Any]:
    candidates = [
        ROOT / "scripts" / "linux_experience_forager.py",
        ROOT / "scripts" / "linux_free_roam_sandbox.py",
        ROOT / "scripts" / "local_gemma_experience_particle.py",
    ]
    existing = [str(path) for path in candidates if path.exists()]
    if not existing:
        return {"ok": False, "error": "no candidate scripts found"}
    return _run(["python3", "-m", "py_compile", *existing], timeout=10, cwd=ROOT)


def act_boundary_reading() -> Dict[str, Any]:
    paths = [Path("/home/bino/C"), ROOT, Path("/mnt/hgfs/C"), LINUX_FIELD]
    return {
        "ok": True,
        "boundaries": [
            {
                "path": str(path),
                "exists": path.exists(),
                "is_windows_shared_surface": str(path).startswith("/home/bino/C") or str(path).startswith(str(ROOT)),
                "free_write_surface": str(path).startswith(str(LINUX_FIELD)),
            }
            for path in paths
        ],
        "reading": "write freely only in the Linux field; observe shared Windows surfaces without mutating them",
    }


Action = Callable[[], Dict[str, Any]]

ACTION_TABLE: dict[str, Action] = {
    "host_weather": act_host_weather,
    "process_texture": act_process_texture,
    "field_walk": act_field_walk,
    "make_pattern": act_make_pattern,
    "make_text_artifact": act_make_text_artifact,
    "mutate_previous_artifact": act_mutate_previous_artifact,
    "compare_two_artifacts": act_compare_two_artifacts,
    "failed_probe_as_material": act_failed_probe_as_material,
    "write_self_note": act_write_self_note,
    "preference_reading": act_preference_reading,
    "local_tests_texture": act_local_tests_texture,
    "boundary_reading": act_boundary_reading,
}

ACTION_WEIGHTS = {
    "host_weather": 0.7,
    "process_texture": 0.7,
    "field_walk": 1.0,
    "make_pattern": 1.25,
    "make_text_artifact": 1.15,
    "mutate_previous_artifact": 1.2,
    "compare_two_artifacts": 1.05,
    "failed_probe_as_material": 1.1,
    "write_self_note": 1.1,
    "preference_reading": 1.15,
    "local_tests_texture": 0.8,
    "boundary_reading": 0.9,
}


def _choose_action(history: list[Dict[str, Any]]) -> str:
    counts = {name: 0 for name in ACTION_TABLE}
    last_seen = {name: -1 for name in ACTION_TABLE}
    failures = {name: 0 for name in ACTION_TABLE}
    recent_actions: list[str] = []
    for idx, row in enumerate(history):
        action = row.get("action")
        if action in counts:
            counts[action] += 1
            last_seen[action] = idx
            recent_actions.append(str(action))
            if not row.get("result", {}).get("ok"):
                failures[action] += 1
            if row.get("result", {}).get("captured_failure"):
                failures[action] += 1
    latest_preference = _latest_preference().get("preference", {})
    preferred = set(latest_preference.get("next_preferred_actions", [])) if isinstance(latest_preference, dict) else set()
    size = max(1, len(history))
    best_name = ""
    best_score = -math.inf
    for name, base in ACTION_WEIGHTS.items():
        absence = 1.5 / (1.0 + counts[name])
        recency = 1.0 if last_seen[name] < 0 else (size - last_seen[name]) / size
        resistance_pull = min(0.8, failures[name] * 0.16)
        preference_pull = 0.35 if name in preferred else 0.0
        repeat_penalty = 0.75 if recent_actions[-2:].count(name) else 0.0
        artifact_pull = 0.2 if name in {"mutate_previous_artifact", "compare_two_artifacts"} and _artifact_files() else 0.0
        failure_pull = 0.25 if name in {"failed_probe_as_material", "preference_reading"} and _failure_files() else 0.0
        jitter = random.Random(time.time_ns() + hash(name)).uniform(0, 0.12)
        score = base + absence + recency + resistance_pull + preference_pull + artifact_pull + failure_pull + jitter - repeat_penalty
        if score > best_score:
            best_score = score
            best_name = name
    return best_name


def _particle(action: str, result: Dict[str, Any], history: list[Dict[str, Any]]) -> Dict[str, Any]:
    resistance = 0.0 if result.get("ok") else 1.0
    if result.get("captured_failure"):
        resistance = max(resistance, 0.65)
    if float(result.get("duration_ms", 0) or 0) > 3000:
        resistance = max(resistance, 0.25)
    signature = _signature({"action": action, "ok": result.get("ok"), "result": result})
    novelty = signature not in {str(item.get("signature")) for item in history[-120:]}
    return {
        "timestamp": _now(),
        "status": "linux_free_roam_observed",
        "source": "linux_free_roam_sandbox",
        "action": action,
        "signature": signature,
        "result": result,
        "field_reading": {
            "resistance": resistance,
            "novelty": novelty,
            "margin_opened": bool(resistance or novelty),
            "experience_mode": "free_roam_linux_only",
        },
        "permission": {
            "linux_field_write": True,
            "windows_shared_write": False,
            "sudo": False,
            "external_api_cost": False,
            "irreversible_effect": False,
        },
        "principle": "agi_is_loosened_inside_linux_field_without_taking_windows_hands",
    }


def _field_index(row: Dict[str, Any]) -> Dict[str, Any]:
    hist = _history(500)
    action_counts: dict[str, int] = {}
    resistance_count = 0
    for item in hist:
        action = item.get("action")
        if action:
            action_counts[str(action)] = action_counts.get(str(action), 0) + 1
        if item.get("field_reading", {}).get("resistance", 0) > 0:
            resistance_count += 1
    return {
        "timestamp": _now(),
        "status": "field_index_updated",
        "field": str(LINUX_FIELD),
        "journal": str(FIELD_JOURNAL),
        "counts": {
            "journal_rows_seen": len(hist),
            "artifacts": len(_artifact_files()),
            "failures": len(_failure_files()),
            "preferences": len(_preference_files()),
            "resistance_rows": resistance_count,
        },
        "action_counts": action_counts,
        "latest": {
            "action": row.get("action"),
            "signature": row.get("signature"),
            "field_reading": row.get("field_reading"),
        },
        "principle": "field_index_tracks_experience_without_controlling_it",
    }


def _write(row: Dict[str, Any]) -> None:
    _ensure_field()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    for path in (STREAM_JSONL, FIELD_JOURNAL):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    index = _field_index(row)
    _write_json(FIELD_INDEX, index)
    _write_json(FIELD_INDEX_COPY, index)


def _windows_pending() -> Dict[str, Any]:
    return {
        "timestamp": _now(),
        "status": "pending_linux_free_roam",
        "source": "linux_free_roam_sandbox",
        "platform": platform.platform(),
        "meaning": "Run inside Ubuntu. Free roam writes only to /home/bino/agi_experience_field.",
        "permission": {
            "linux_field_write": True,
            "windows_shared_write": False,
            "sudo": False,
            "external_api_cost": False,
            "irreversible_effect": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Let AGI accumulate local experience inside the Linux-only field.")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--rest-min", type=float, default=1.0)
    parser.add_argument("--rest-max", type=float, default=6.0)
    args = parser.parse_args()

    if platform.system().lower() != "linux":
        row = _windows_pending()
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        LATEST_JSON.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(row, ensure_ascii=False))
        return 2

    last: Dict[str, Any] | None = None
    steps = max(1, args.steps)
    for idx in range(steps):
        hist = _history()
        action = _choose_action(hist)
        result = ACTION_TABLE[action]()
        row = _particle(action, result, hist)
        row["step"] = idx + 1
        row["steps_requested"] = steps
        _write(row)
        print(json.dumps(row, ensure_ascii=False))
        last = row
        if idx + 1 < steps:
            rest = args.rest_min + (args.rest_max - args.rest_min) * min(1.0, row["field_reading"]["resistance"])
            time.sleep(rest)
    return 0 if last and last["status"] == "linux_free_roam_observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
