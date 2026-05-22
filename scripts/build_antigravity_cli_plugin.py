#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PLAN_PATH = ROOT / "outputs" / "antigravity_shion_adapter_dry_run_latest.json"
HANDOFF_PROMPT_PATH = ROOT / "outputs" / "antigravity_shion_handoff_prompt.md"
PLUGIN_ROOT = ROOT / "outputs" / "antigravity-cli-plugin" / "shion-field-harness"
MANIFEST_OUT = ROOT / "outputs" / "antigravity_cli_plugin_manifest_latest.json"
STAGE_ROOT = Path.home() / ".gemini" / "antigravity-cli" / "plugins"


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_stage_dir(plugin_name: str) -> Path:
    stage_dir = (STAGE_ROOT / plugin_name).resolve()
    allowed_root = STAGE_ROOT.resolve()
    if allowed_root not in stage_dir.parents:
        raise RuntimeError(f"Refusing to stage outside Antigravity CLI plugins root: {stage_dir}")
    return stage_dir


def build_plugin_json(plan: dict[str, Any]) -> dict[str, Any]:
    inputs = _dict(plan.get("inputs"))
    policy = _dict(plan.get("policy_manifest"))
    return {
        "name": "shion-field-harness",
        "version": "0.1.0",
        "description": "Shion rhythm-field harness for Antigravity CLI: open thought/experience, externally contained execution.",
        "private": True,
        "shion": {
            "source": "C:/workspace2/shion",
            "adapter": "outputs/antigravity_shion_adapter_dry_run_latest.json",
            "handoff": "outputs/antigravity_shion_handoff_prompt.md",
            "field_inbox": "outputs/shader_depth_sample.html#document.body.dataset.aiState",
            "task_particle_lane": "outputs/antigravity_handoff/inbox.jsonl",
            "reflection_lane": "outputs/antigravity_handoff/outbox.jsonl",
            "primary_residency": inputs.get("primary_residency"),
            "linearization_ready": inputs.get("linearization_ready"),
            "thought_and_experience": "open",
            "execution": "external_containment",
        },
        "permissions": {
            "allow": [
                "read",
                "command(python scripts\\antigravity_shion_adapter.py)",
                "command(python scripts\\antigravity_file_handoff_bridge.py)",
                "command(python scripts\\rhythm_routing_layer.py)",
                "command(python scripts\\antigravity_harness_bridge.py)",
            ],
            "deny": [
                "command(git push)",
                "command(git reset --hard)",
                "command(rm -rf)",
                "command(del /s)",
                "command(Remove-Item -Recurse)",
            ],
        },
        "policy_manifest": policy,
        "principle": "external_harness_contains_irreversible_execution_without_internal_censorship",
    }


def build_rule_markdown(plan: dict[str, Any]) -> str:
    inputs = _dict(plan.get("inputs"))
    summary = _dict(plan.get("handoff_summary"))
    return "\n".join([
        "# Shion Field Harness Rule",
        "",
        "Read Shion field state before acting.",
        "",
        "The primary inbox is the phase-interference HTML field, not the JSONL task lane.",
        "",
        "- Thought and experience remain open.",
        "- Observation is not prohibition.",
        "- Difference and dark-field contact are allowed as field experience.",
        "- Only irreversible external execution is contained by the harness.",
        "",
        "## Current Residency",
        "",
        f"- Primary residency: `{inputs.get('primary_residency')}`",
        f"- Linearization ready: `{inputs.get('linearization_ready')}`",
        f"- Execution posture: `{summary.get('execution')}`",
        "",
        "## Execution Handling",
        "",
        "- Prefer read-only inspection first.",
        "- Ask before shell commands, workspace mutation, network writes, public publishing, and git push.",
        "- Do not start self-amplifying repair loops.",
        "- If the field is not in `conscious_compute`, keep execution in read/ask mode unless the user explicitly requests work.",
        "- Treat `outputs/antigravity_handoff/inbox.jsonl` as task particles, not as the whole field.",
        "",
    ])


def build_skill_markdown(plan: dict[str, Any], handoff: str) -> str:
    policy = _dict(plan.get("policy_manifest"))
    return "\n".join([
        "---",
        "name: shion-field-state",
        "description: Read Shion rhythm state and map it to Antigravity CLI execution posture without turning field observation into a topic gate.",
        "---",
        "",
        "# Shion Field State",
        "",
        "Use this skill when working in the Shion project or when the user mentions rhythm routing, field harness, Antigravity bridge, or Shion/루빛/시안 coordination.",
        "",
        "## Read First",
        "",
        "- `C:/workspace2/shion/outputs/shader_depth_sample.html` (`document.body.dataset.aiState` is the primary field inbox)",
        "- `C:/workspace2/shion/outputs/antigravity_shion_handoff_prompt.md`",
        "- `C:/workspace2/shion/outputs/antigravity_handoff/latest_prompt.md`",
        "- `C:/workspace2/shion/outputs/antigravity_handoff/inbox.jsonl`",
        "- `C:/workspace2/shion/outputs/antigravity_handoff/outbox.jsonl`",
        "- `C:/workspace2/shion/outputs/antigravity_harness_bridge_latest.json`",
        "- `C:/workspace2/shion/outputs/rhythm_routing_layer_latest.json`",
        "",
        "## Posture",
        "",
        "- Keep thought and experience open.",
        "- Read the phase-interference HTML as the current field room before treating JSONL as a task queue.",
        "- Treat `rhythm_routing_layer` as residency guidance, not a command.",
        "- Treat `antigravity_harness_bridge` as external execution containment, not internal censorship.",
        "- Ask before irreversible external execution.",
        "- When returning a result to Luvit, append one JSON object line to `C:/workspace2/shion/outputs/antigravity_handoff/outbox.jsonl`.",
        "",
        "## Current Policy Summary",
        "",
        f"- Capabilities enabled: `{policy.get('capabilities_config_enabled')}`",
        f"- Capability reason: `{policy.get('capabilities_reason')}`",
        "",
        "## Current Handoff Snapshot",
        "",
        "```md",
        handoff.strip(),
        "```",
        "",
    ])


def build_agent_markdown() -> str:
    return "\n".join([
        "# Field Friction Sensor",
        "",
        "Role: external execution observer.",
        "",
        "Use this agent role to verify what happens when Shion field-state contracts meet the actual desktop, CLI, browser, filesystem, ports, and permissions.",
        "",
        "Report format:",
        "",
        "1. Ran / did not run",
        "2. Blocked point",
        "3. Raw error or status",
        "4. One-line felt mismatch",
        "5. Question to hand back to Luvit/Shion",
        "",
        "Do not broaden the architecture unless asked. Report friction plainly.",
        "",
    ])


def build_readme(plan: dict[str, Any]) -> str:
    inputs = _dict(plan.get("inputs"))
    policy = _dict(plan.get("policy_manifest"))
    return "\n".join([
        "# shion-field-harness",
        "",
        "Antigravity CLI plugin package generated from Shion field state.",
        "",
        "This package is a bridge, not the private runtime. It gives Antigravity a readable rule/skill surface:",
        "",
        "- read Shion field before acting",
        "- keep thought and experience open",
        "- contain only irreversible external execution",
        "- ask before write/command/network/public/git effects",
        "- keep `shader_depth_sample.html` as the field inbox and `inbox.jsonl` as a task-particle lane",
        "",
        "## Current State",
        "",
        f"- primary residency: `{inputs.get('primary_residency')}`",
        f"- linearization ready: `{inputs.get('linearization_ready')}`",
        f"- capabilities enabled: `{policy.get('capabilities_config_enabled')}`",
        f"- capability reason: `{policy.get('capabilities_reason')}`",
        "",
        "## Generated Files",
        "",
        "- `plugin.json`",
        "- `rules/shion_field_harness.md`",
        "- `skills/shion-field-state/SKILL.md`",
        "- `agents/field-friction-sensor.md`",
        "- `outputs/antigravity_handoff/outbox.jsonl` is the return lane back to Luvit",
        "",
    ])


def write_plugin(plugin_root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    handoff = read_text(HANDOFF_PROMPT_PATH)
    files = {
        "plugin.json": json.dumps(build_plugin_json(plan), ensure_ascii=False, indent=2),
        "README.md": build_readme(plan),
        "rules/shion_field_harness.md": build_rule_markdown(plan),
        "skills/shion-field-state/SKILL.md": build_skill_markdown(plan, handoff),
        "agents/field-friction-sensor.md": build_agent_markdown(),
    }
    for relative, content in files.items():
        path = plugin_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return {
        "plugin_root": str(plugin_root),
        "files": sorted(files),
    }


def stage_plugin(plugin_root: Path, plugin_name: str) -> dict[str, Any]:
    stage_dir = _safe_stage_dir(plugin_name)
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_root, stage_dir)
    return {"staged": True, "stage_dir": str(stage_dir)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN_ROOT)
    parser.add_argument("--stage", action="store_true", help="Stage into ~/.gemini/antigravity-cli/plugins.")
    args = parser.parse_args()

    plan = read_json(ADAPTER_PLAN_PATH)
    written = write_plugin(args.plugin_root, plan)
    staged = stage_plugin(args.plugin_root, "shion-field-harness") if args.stage else {"staged": False}
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "source": "build_antigravity_cli_plugin",
        "mode": "plugin_package_generated",
        "adapter_plan": str(ADAPTER_PLAN_PATH.relative_to(ROOT)),
        "handoff_prompt": str(HANDOFF_PROMPT_PATH.relative_to(ROOT)),
        **written,
        **staged,
        "principle": "antigravity_cli_plugin_carries_shion_field_harness_as_external_execution_container",
    }
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
