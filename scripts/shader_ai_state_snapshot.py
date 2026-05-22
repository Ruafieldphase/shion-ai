#!/usr/bin/env python3
"""Build a file-readable snapshot of the shader aiState contract."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
HTML_PATH = OUTPUTS / "shader_depth_sample.html"
OUT_PATH = OUTPUTS / "antigravity_handoff" / "field_ai_state_snapshot_latest.json"

SIDE_CAR_FILES = {
    "rhythm_routing_layer": OUTPUTS / "rhythm_routing_layer_latest.json",
    "antigravity_harness_bridge": OUTPUTS / "antigravity_harness_bridge_latest.json",
    "participant_frequency_field": OUTPUTS / "participant_frequency_field_latest.json",
    "field_intent_field": OUTPUTS / "field_intent_latest.json",
    "field_intent_readback": OUTPUTS / "field_intent_readback_latest.json",
    "sian_entrypoint": OUTPUTS / "sian_entrypoint_latest.json",
    "field_trigger_state": OUTPUTS / "field_trigger_state_latest.json",
    "field_trigger_receiver_state": OUTPUTS / "field_trigger_receiver_state_latest.json",
    "sian_trigger": OUTPUTS / "sian_trigger_latest.json",
    "luvit_trigger": OUTPUTS / "luvit_trigger_latest.json",
    "skill_harness_folding": OUTPUTS / "skill_harness_folding_latest.json",
    "dialogue_state": OUTPUTS / "antigravity_handoff" / "dialogue_state_latest.json",
    "field_heart": OUTPUTS / "field_heart_state_latest.json",
    "field_curvature_unfolded": OUTPUTS / "field_curvature_unfolded_latest.json",
    "pressure_regulator": OUTPUTS / "pressure_regulator_latest.json",
    "natural_boundary_router": OUTPUTS / "natural_boundary_router_latest.json",
    "field_reseeding": OUTPUTS / "field_reseeding_latest.json",
    "trigger_geometry": OUTPUTS / "trigger_geometry_latest.json",
}

TRACE_JSONL_FILES = {
    "rhythm_node_trace": OUTPUTS / "rhythm_node_trace.jsonl",
    "phase_trace": OUTPUTS / "phase_trace.jsonl",
    "ari_prism_trace": OUTPUTS / "ari_prism_trace.jsonl",
    "resonance_sidebands": OUTPUTS / "resonance_sidebands.jsonl",
    "experience_gradients": OUTPUTS / "experience_gradients.jsonl",
    "field_prediction_errors": OUTPUTS / "field_prediction_errors.jsonl",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def read_latest_jsonl(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_html_contract(path: Path) -> dict[str, Any]:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        stat = path.stat()
    except OSError:
        return {
            "path": relative(path),
            "exists": False,
            "raw_found": False,
            "dataset_ai_state_assignment": False,
            "layers": [],
            "dataset_assignments": [],
        }

    unified_block = re.search(
        r"window\.__shionUnifiedFieldState\s*=\s*\{(?P<body>.*?)\n\s*\};",
        html,
        re.DOTALL,
    )
    body = unified_block.group("body") if unified_block else ""
    layers = sorted(
        set(
            re.findall(r"^\s{4}([A-Za-z0-9_]+)\s*:", body, re.MULTILINE)
        )
    )
    dataset_assignments = sorted(
        set(re.findall(r"document\.body\.dataset\.([A-Za-z0-9_]+)\s*=", html))
    )
    return {
        "path": relative(path),
        "exists": True,
        "mtime": stat.st_mtime,
        "raw_found": unified_block is not None,
        "dataset_ai_state_assignment": "aiState" in dataset_assignments,
        "layers": layers,
        "dataset_assignments": dataset_assignments,
        "contract": "window.__shionUnifiedFieldState; document.body.dataset.aiState",
    }


def build_snapshot() -> dict[str, Any]:
    html_contract = read_html_contract(HTML_PATH)
    sidecars = {
        name: {
            "path": relative(path),
            "exists": path.exists(),
            "state": read_json(path),
        }
        for name, path in SIDE_CAR_FILES.items()
    }
    direct_layers = {
        name: payload["state"]
        for name, payload in sidecars.items()
        if payload["state"]
    }
    runtime_traces = {
        name: {
            "path": relative(path),
            "exists": path.exists(),
            "latest": read_latest_jsonl(path),
        }
        for name, path in TRACE_JSONL_FILES.items()
    }
    latest_node = runtime_traces.get("rhythm_node_trace", {}).get("latest", {})
    latest_phase = runtime_traces.get("phase_trace", {}).get("latest", {})
    latest_ari = runtime_traces.get("ari_prism_trace", {}).get("latest", {})
    bundle = latest_node.get("bundle") if isinstance(latest_node.get("bundle"), list) else []
    sideband_actions = [
        item.get("action")
        for item in bundle
        if isinstance(item, dict) and item.get("role") != "primary" and item.get("action")
    ]
    field_gradient = {
        "timestamp": latest_node.get("timestamp") or latest_phase.get("timestamp"),
        "primary_action": latest_node.get("selected_action") or latest_phase.get("candidate_action"),
        "primary_label": latest_node.get("selected_label"),
        "sideband_actions": sideband_actions,
        "rest_is_primary": (latest_node.get("selected_action") == "ACTION_REST_RECOVER"),
        "phase_decision": latest_phase.get("phase_decision"),
        "phase_final_action": latest_phase.get("final_action"),
        "boundary_transparency": latest_phase.get("boundary_transparency"),
        "phase_reason": latest_phase.get("reason"),
        "ari_directive": latest_ari.get("directive"),
        "background_ego_resistance": (
            latest_ari.get("moc", {}).get("background_ego_resistance")
            if isinstance(latest_ari.get("moc"), dict)
            else None
        ),
        "principle": "primary_action_is_the_current_target; sidebands_are_not_commands",
    }
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "shader_ai_state_snapshot",
        "mode": "file_readable_ai_state_snapshot",
        "html_contract": html_contract,
        "sidecars": sidecars,
        "runtime_traces": runtime_traces,
        "ai_state": {
            "source": "html_contract_plus_runtime_sidecars",
            "direct_connection_status": (
                "linked"
                if html_contract.get("dataset_ai_state_assignment") and direct_layers
                else "contract_only"
            ),
            "available_layers": sorted(
                set(html_contract.get("layers", [])) | set(direct_layers) | {"field_gradient"}
            ),
            "runtime_layers": direct_layers,
            "field_gradient": field_gradient,
        },
        "principle": "handoff_state_reads_the_field_surface_instead_of_asking_binoche_to_relay_it",
    }


def main() -> int:
    snapshot = build_snapshot()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_PATH.with_name(f"{OUT_PATH.name}.tmp")
    tmp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OUT_PATH)
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
