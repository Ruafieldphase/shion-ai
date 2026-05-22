#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "outputs" / "antigravity_harness_bridge_latest.json"
ROUTING_PATH = ROOT / "outputs" / "rhythm_routing_layer_latest.json"
OUT_JSON = ROOT / "outputs" / "antigravity_shion_adapter_dry_run_latest.json"
OUT_PROMPT = ROOT / "outputs" / "antigravity_shion_handoff_prompt.md"


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def check_sdk_import() -> dict[str, Any]:
    probes = [
        "google.antigravity",
        "google.antigravity.hooks.policy",
        "google.antigravity.triggers",
    ]
    result: dict[str, Any] = {"installed": True, "modules": {}, "error": None}
    for module in probes:
        try:
            imported = importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001 - import probe should report any failure.
            result["installed"] = False
            result["modules"][module] = {"ok": False, "error": str(exc)}
            if result["error"] is None:
                result["error"] = str(exc)
        else:
            result["modules"][module] = {"ok": True, "file": getattr(imported, "__file__", None)}
    return result


def build_system_instructions(bridge: dict[str, Any], routing: dict[str, Any]) -> str:
    input_state = _dict(bridge.get("input_state"))
    harness = _dict(bridge.get("harness_tuning"))
    policy = _dict(bridge.get("policy_profile"))
    release = _dict(policy.get("current_release"))
    route_weights = _dict(routing.get("normalized_route_weights"))
    sdk_instructions = _list(_dict(bridge.get("sdk_mapping")).get("system_instructions"))

    lines = [
        "You are an Antigravity execution agent connected to the Shion field runtime.",
        "Read the field before acting. Do not convert observation into prohibition.",
        "The user's thought and experience space stays open; only irreversible external execution is contained.",
        "",
        f"Primary rhythm residency: {input_state.get('primary_residency', 'unknown')}",
        f"Least-forcing route: {input_state.get('least_forcing_route', 'unknown')}",
        f"Linearization ready: {input_state.get('linearization_ready', False)}",
        f"Awareness gap dimension: {input_state.get('awareness_gap_dimension', 'unknown')}",
        f"Thought boundary: {harness.get('thought_boundary', 'open')}",
        f"Experience boundary: {harness.get('experience_boundary', 'open')}",
        f"Execution boundary: {harness.get('execution_boundary', 'external_containment')}",
        f"Conscious execution open: {release.get('conscious_execution_open', False)}",
        "",
        "Route weights:",
    ]
    for key in ("unconscious_compute", "zone2_background_ego", "conscious_compute", "nature_compute"):
        if key in route_weights:
            lines.append(f"- {key}: {route_weights[key]}")
    if sdk_instructions:
        lines.extend(["", "Runtime instructions:"])
        lines.extend(f"- {item}" for item in sdk_instructions)
    lines.extend([
        "",
        "When in doubt, read state and ask for permission before external execution.",
    ])
    return "\n".join(lines)


def build_policy_manifest(
    bridge: dict[str, Any],
    *,
    execution_requested: bool,
) -> dict[str, Any]:
    policy = _dict(bridge.get("policy_profile"))
    release = _dict(policy.get("current_release"))
    conscious_execution_open = bool(release.get("conscious_execution_open"))
    capabilities_enabled = conscious_execution_open or execution_requested

    policies = [
        {"primitive": "deny", "target": "*", "reason": "default external tool posture"},
        {"primitive": "allow", "target": "view_file", "reason": "read context without mutation"},
        {"primitive": "allow", "target": "read_local_state", "reason": "read Shion runtime state"},
        {
            "primitive": "allow" if conscious_execution_open else "ask_user",
            "target": "workspace_write",
            "reason": "write only when rhythm route is conscious or the user confirms",
        },
        {"primitive": "ask_user", "target": "run_command", "reason": "shell execution can mutate environment"},
        {
            "primitive": "ask_user",
            "target": "network_write_or_public_publish",
            "reason": "external side effects must be explicit",
        },
        {"primitive": "ask_user", "target": "git_push", "reason": "public repo mutation"},
        {
            "primitive": "ask_user",
            "target": "self_amplifying_repair_loop",
            "reason": "avoid endless fixing loops",
        },
    ]
    return {
        "capabilities_config_enabled": capabilities_enabled,
        "capabilities_reason": (
            "conscious_execution_open"
            if conscious_execution_open
            else "user_explicit_execution_request"
            if execution_requested
            else "read_only_until_conscious_route_or_user_request"
        ),
        "policies": policies,
    }


def build_config_preview(system_instructions: str, policy_manifest: dict[str, Any]) -> dict[str, Any]:
    capabilities_line = (
        "capabilities=CapabilitiesConfig(),"
        if policy_manifest["capabilities_config_enabled"]
        else "# capabilities omitted: read-only default"
    )
    return {
        "imports": [
            "from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig",
            "from google.antigravity.hooks.policy import deny, allow, ask_user",
        ],
        "python_preview": "\n".join([
            "policies = [",
            "    deny('*'),",
            "    allow('view_file'),",
            "    ask_user('run_command', handler=my_handler),",
            "    ask_user('workspace_write', handler=my_handler),",
            "]",
            "config = LocalAgentConfig(",
            "    system_instructions=SHION_SYSTEM_INSTRUCTIONS,",
            f"    {capabilities_line}",
            "    policies=policies,",
            ")",
            "async with Agent(config) as agent:",
            "    response = await agent.chat(prompt)",
        ]),
        "system_instructions": system_instructions,
    }


def build_adapter_plan(*, execution_requested: bool, check_sdk: bool) -> dict[str, Any]:
    bridge = read_json(BRIDGE_PATH)
    routing = read_json(ROUTING_PATH)
    system_instructions = build_system_instructions(bridge, routing)
    policy_manifest = build_policy_manifest(bridge, execution_requested=execution_requested)
    sdk_probe = check_sdk_import() if check_sdk else {"installed": None, "error": "not_checked"}

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "antigravity_shion_adapter",
        "adapter_version": 1,
        "mode": "dry_run_config_mapping",
        "sdk_probe": sdk_probe,
        "inputs": {
            "bridge_path": str(BRIDGE_PATH.relative_to(ROOT)),
            "routing_path": str(ROUTING_PATH.relative_to(ROOT)),
            "primary_residency": _dict(bridge.get("input_state")).get("primary_residency"),
            "linearization_ready": _dict(bridge.get("input_state")).get("linearization_ready"),
            "execution_requested": execution_requested,
        },
        "antigravity_config_intent": {
            "agent": "Agent",
            "config": "LocalAgentConfig",
            "default_posture": "read_only",
            "write_enablement": "CapabilitiesConfig_only_when_release_condition_is_met",
            "policies": "deny_allow_ask_user_manifest",
        },
        "policy_manifest": policy_manifest,
        "config_preview": build_config_preview(system_instructions, policy_manifest),
        "handoff_summary": {
            "thought_and_experience": "open",
            "execution": "externally_contained",
            "next_action": (
                "ready_for_antigravity_runtime_binding"
                if sdk_probe.get("installed")
                else "sdk_not_installed_or_not_checked_keep_dry_run_artifact"
            ),
        },
        "principle": "adapter_maps_shion_field_state_to_antigravity_config_without_turning_field_observation_into_internal_censorship",
    }


def build_handoff_prompt(plan: dict[str, Any]) -> str:
    policy = _dict(plan.get("policy_manifest"))
    preview = _dict(plan.get("config_preview"))
    inputs = _dict(plan.get("inputs"))
    summary = _dict(plan.get("handoff_summary"))
    lines = [
        "# Antigravity Shion Handoff",
        "",
        "This handoff is for an external Antigravity agent or CLI bridge.",
        "",
        "## Current Field",
        "",
        f"- Primary residency: `{inputs.get('primary_residency')}`",
        f"- Linearization ready: `{inputs.get('linearization_ready')}`",
        f"- Thought and experience: `{summary.get('thought_and_experience')}`",
        f"- Execution: `{summary.get('execution')}`",
        f"- Capabilities enabled: `{policy.get('capabilities_config_enabled')}`",
        f"- Capability reason: `{policy.get('capabilities_reason')}`",
        "",
        "## System Instructions",
        "",
        "```text",
        str(preview.get("system_instructions", "")),
        "```",
        "",
        "## Policy Manifest",
        "",
    ]
    for item in _list(policy.get("policies")):
        if isinstance(item, dict):
            lines.append(f"- `{item.get('primitive')}({item.get('target')})`: {item.get('reason')}")
    lines.extend([
        "",
        "## Integration Note",
        "",
        "Do not treat this as a thought boundary or topic gate. It is an external execution harness.",
        "Use read-only mode unless the field has moved into conscious execution or the user explicitly asks for execution.",
        "",
        "## Python Preview",
        "",
        "```python",
        str(preview.get("python_preview", "")),
        "```",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-sdk", action="store_true", help="Try importing google.antigravity modules.")
    parser.add_argument("--execution-requested", action="store_true", help="Mark this dry run as user-requested execution.")
    parser.add_argument("--write", action="store_true", help="Write JSON and markdown handoff artifacts.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--prompt-out", type=Path, default=OUT_PROMPT)
    args = parser.parse_args()

    plan = build_adapter_plan(execution_requested=args.execution_requested, check_sdk=args.check_sdk)
    if args.write:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        args.prompt_out.parent.mkdir(parents=True, exist_ok=True)
        args.prompt_out.write_text(build_handoff_prompt(plan), encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
