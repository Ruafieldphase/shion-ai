from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List


EXPECTED_LOCAL_PORTS = {57321, 57322}
EXPECTED_BOUNDARY_PORTS = {11434}
EXPECTED_PROCESS_NAMES = {"python.exe", "pythonw.exe", "ollama.exe", "python", "pythonw", "ollama"}
SENSITIVE_PATH_MARKERS = (".env", "key", "secret", "credential", "token")


def build_security_boundary_state(
    file_changes: Iterable[Dict[str, Any]] | None = None,
    process_observations: Iterable[Dict[str, Any]] | None = None,
    listener_observations: Iterable[Dict[str, Any]] | None = None,
    trace_observations: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    files = list(file_changes or [])
    processes = list(process_observations or [])
    listeners = list(listener_observations or [])
    traces = trace_observations or {}

    file_reading = _read_file_changes(files)
    process_reading = _read_processes(processes)
    listener_reading = _read_listeners(listeners)
    trace_reading = _read_traces(traces)

    ambiguity = _clamp(
        0.24 * file_reading["unknown_mutation_ratio"]
        + 0.22 * process_reading["unknown_process_ratio"]
        + 0.22 * listener_reading["external_listener_ratio"]
        + 0.18 * trace_reading["missing_trace_ratio"]
        + 0.14 * trace_reading["boundary_contact"]
    )
    intrusion_pressure = _clamp(
        0.35 * file_reading["sensitive_mutation_pressure"]
        + 0.28 * process_reading["unknown_executable_pressure"]
        + 0.24 * listener_reading["unexpected_external_pressure"]
        + 0.13 * trace_reading["connection_risk"]
    )
    verification_need = _clamp(
        0.38 * ambiguity
        + 0.34 * intrusion_pressure
        + 0.16 * file_reading["workspace_mutation_pressure"]
        + 0.12 * listener_reading["unexpected_listener_pressure"]
    )

    mode = _mode_for(intrusion_pressure, verification_need, ambiguity)
    next_contact = _next_contact_for(mode)

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "security_boundary_observed",
        "field": "source_separation_boundary",
        "readings": {
            "files": file_reading,
            "processes": process_reading,
            "listeners": listener_reading,
            "traces": trace_reading,
        },
        "signals": {
            "ambiguity": round(ambiguity, 6),
            "intrusion_pressure": round(intrusion_pressure, 6),
            "verification_need": round(verification_need, 6),
        },
        "mode": mode,
        "next_contact": next_contact,
        "not_an_intrusion_claim": True,
        "not_a_blocker": True,
        "principle": "separate_internal_metabolism_from_external_contact_before_interpreting_change",
    }


def _read_file_changes(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(files)
    untracked = sum(1 for item in files if "?" in str(item.get("status", "")))
    modified = sum(1 for item in files if "M" in str(item.get("status", "")))
    deleted = sum(1 for item in files if "D" in str(item.get("status", "")))
    sensitive = [
        str(item.get("path", ""))
        for item in files
        if any(marker in str(item.get("path", "")).lower() for marker in SENSITIVE_PATH_MARKERS)
    ]
    hashed = sum(1 for item in files if item.get("sha256"))
    unknown_hash = max(0, total - hashed)
    return {
        "total_changes": total,
        "modified": modified,
        "untracked": untracked,
        "deleted": deleted,
        "hashed": hashed,
        "unknown_hash": unknown_hash,
        "sensitive_paths": sensitive[:12],
        "workspace_mutation_pressure": _ratio(min(total, 40), 40),
        "unknown_mutation_ratio": _ratio(unknown_hash, max(1, total)),
        "sensitive_mutation_pressure": _clamp(len(sensitive) * 0.55 + deleted * 0.25),
    }


def _read_processes(processes: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(processes)
    unknown = []
    expected = []
    for item in processes:
        name = str(item.get("name") or item.get("Name") or item.get("ProcessName") or "").lower()
        if name in EXPECTED_PROCESS_NAMES:
            expected.append(item)
        else:
            unknown.append(item)
    unknown_with_path = [
        item
        for item in unknown
        if item.get("path") or item.get("Path") or item.get("ExecutablePath")
    ]
    return {
        "total_observed": total,
        "expected_runtime_processes": len(expected),
        "unknown_processes": len(unknown),
        "unknown_process_ratio": _ratio(len(unknown), max(1, total)),
        "unknown_executable_pressure": _ratio(len(unknown_with_path), 2),
        "sample_unknown": [_process_compact(item) for item in unknown[:8]],
        "sample_expected": [_process_compact(item) for item in expected[:8]],
    }


def _read_listeners(listeners: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(listeners)
    expected = []
    unexpected_loopback = []
    external = []
    unexpected_external = []
    for item in listeners:
        port = _int(item.get("local_port", item.get("LocalPort")), 0)
        address = str(item.get("local_address", item.get("LocalAddress", "")))
        if port in EXPECTED_LOCAL_PORTS or port in EXPECTED_BOUNDARY_PORTS:
            expected.append(item)
            continue
        if _is_loopback(address):
            unexpected_loopback.append(item)
            continue
        external.append(item)
        if port not in {135, 139, 445, 902, 912, 1033, 2179, 3389, 5040} and port < 49152:
            unexpected_external.append(item)
    return {
        "total_listeners": total,
        "expected_runtime_listeners": len(expected),
        "unexpected_loopback_listeners": len(unexpected_loopback),
        "external_listeners": len(external),
        "unexpected_external_listeners": len(unexpected_external),
        "external_listener_ratio": _ratio(len(external), max(1, total)),
        "unexpected_listener_pressure": _ratio(len(unexpected_loopback) + len(unexpected_external), 24),
        "unexpected_external_pressure": _ratio(len(unexpected_external), 2),
        "sample_expected": [_listener_compact(item) for item in expected[:8]],
        "sample_external": [_listener_compact(item) for item in external[:12]],
        "sample_unexpected_external": [_listener_compact(item) for item in unexpected_external[:8]],
    }


def _read_traces(traces: Dict[str, Any]) -> Dict[str, Any]:
    expected_keys = ("boundary_aperture", "field_prediction", "experience_feedback", "contextual_gradient")
    present = sum(1 for key in expected_keys if traces.get(key))
    boundary = traces.get("boundary_aperture") if isinstance(traces.get("boundary_aperture"), dict) else {}
    signals = boundary.get("signals") if isinstance(boundary.get("signals"), dict) else {}
    aperture = boundary.get("aperture") if isinstance(boundary.get("aperture"), dict) else {}
    return {
        "present_traces": present,
        "expected_traces": len(expected_keys),
        "missing_trace_ratio": _ratio(len(expected_keys) - present, len(expected_keys)),
        "boundary_mode": boundary.get("mode"),
        "connection_risk": _num(signals.get("connection_risk"), 0.0),
        "boundary_contact": _num(signals.get("boundary_contact"), 0.0),
        "permeability": _num(aperture.get("permeability"), 0.0),
    }


def _mode_for(intrusion_pressure: float, verification_need: float, ambiguity: float) -> str:
    if intrusion_pressure >= 0.45:
        return "narrow_and_verify"
    if verification_need >= 0.35 or ambiguity >= 0.35:
        return "verify_boundary_contact"
    return "baseline_observe"


def _next_contact_for(mode: str) -> Dict[str, Any]:
    if mode == "narrow_and_verify":
        return {
            "action": "narrow_boundary_and_preserve_evidence",
            "meaning": "Potential external contact is high enough to slow interpretation and preserve traces before acting.",
            "irreversible_effect": False,
            "external_api_cost": False,
        }
    if mode == "verify_boundary_contact":
        return {
            "action": "separate_sources_before_interpretation",
            "meaning": "There is ambiguity; read source, hash, process, and listener surfaces before treating change as metabolism.",
            "irreversible_effect": False,
            "external_api_cost": False,
        }
    return {
        "action": "record_boundary_trace",
        "meaning": "No strong intrusion claim; keep a trace so later changes have a baseline.",
        "irreversible_effect": False,
        "external_api_cost": False,
    }


def _process_compact(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pid": item.get("pid") or item.get("Id") or item.get("ProcessId"),
        "name": item.get("name") or item.get("Name") or item.get("ProcessName"),
        "path": item.get("path") or item.get("Path") or item.get("ExecutablePath"),
        "command_line": str(item.get("command_line") or item.get("CommandLine") or "")[:220],
    }


def _listener_compact(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "local_address": item.get("local_address", item.get("LocalAddress")),
        "local_port": _int(item.get("local_port", item.get("LocalPort")), 0),
        "owning_process": item.get("owning_process", item.get("OwningProcess")),
        "process_name": item.get("process_name"),
    }


def _is_loopback(address: str) -> bool:
    return address in {"127.0.0.1", "::1", "localhost"} or address.startswith("127.")


def _ratio(value: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 0.0
    return _clamp(float(value) / float(denominator))


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
