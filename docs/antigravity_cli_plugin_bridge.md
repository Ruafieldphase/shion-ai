# Antigravity CLI Plugin Bridge

The Python SDK path is not currently the first usable Windows path for this
machine. The public PyPI package exists, but the available `google-antigravity`
0.1.0 wheels are macOS arm64 and Linux aarch64/x86_64. On this Windows runtime,
`pip install google-antigravity` has no matching distribution.

The local Antigravity command is present:

```powershell
antigravity.cmd
```

So the next bridge surface is the Antigravity CLI plugin shape: a staged bundle
with `plugin.json`, optional `rules/`, `skills/`, and `agents/`.

## Generated Package

```text
outputs/antigravity-cli-plugin/shion-field-harness/
  plugin.json
  README.md
  rules/shion_field_harness.md
  skills/shion-field-state/SKILL.md
  agents/field-friction-sensor.md
```

## Build

```powershell
python scripts\build_antigravity_cli_plugin.py
```

This creates the plugin package under `outputs/` and writes:

```text
outputs/antigravity_cli_plugin_manifest_latest.json
```

## Stage Into Antigravity CLI

Only stage after reviewing the generated files:

```powershell
python scripts\build_antigravity_cli_plugin.py --stage
```

The stage target is:

```text
~/.gemini/antigravity-cli/plugins/shion-field-harness/
```

## Start A Shion-Aware Antigravity Chat

The installed Antigravity editor CLI supports:

```powershell
antigravity chat --mode agent --add-file <path> <prompt>
```

Use the launcher to refresh the handoff, stage the plugin, and open a chat with
the Shion state files attached:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_antigravity_shion_chat.ps1 -Refresh
```

Preview the exact command without opening Antigravity:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_antigravity_shion_chat.ps1 -DryRun
```

Open in ask mode when you want Antigravity to read the field without editing:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_antigravity_shion_chat.ps1 -Mode ask
```

## File-Based Luvit/Shion Handoff

The phase-interference HTML remains the primary field inbox:

```text
outputs/shader_depth_sample.html
  document.body.dataset.aiState
```

The bridge also creates a no-copy-paste task-particle lane:

```text
outputs/antigravity_handoff/
  inbox.jsonl          # task particles, Luvit -> Shion
  outbox.jsonl         # reflection/result particles, Shion -> Luvit
  latest_prompt.md     # attached to antigravity chat
  state_latest.json    # latest counts and state
```

Initialize or refresh it:

```powershell
python scripts\antigravity_file_handoff_bridge.py init
python scripts\antigravity_file_handoff_bridge.py refresh
```

Send a task particle to Shion without manual copy-paste:

```powershell
python scripts\antigravity_file_handoff_bridge.py post-inbox --summary "next task" --body "Read the handoff and report field friction."
```

Read Shion's return lane:

```powershell
python scripts\antigravity_file_handoff_bridge.py read-outbox --tail 5
```

The launcher includes these handoff files automatically.

Do not treat `inbox.jsonl` as the whole room. It is only a short request lane
on top of the field. Shion should read the HTML field state first, then use
`inbox.jsonl` as the current task note.

## Principle

This plugin carries Shion's field harness into Antigravity as an external
execution container:

- thought and experience stay open
- observation is not prohibition
- field entry is allowed
- irreversible execution remains contained by read/ask permissions
