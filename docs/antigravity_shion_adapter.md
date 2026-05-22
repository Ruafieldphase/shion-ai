# Antigravity Shion Adapter

This adapter is a dry-run bridge from Shion field state into the Google
Antigravity SDK config/policy surface.

It is intentionally not the full runtime binding yet. It reads:

- `outputs/antigravity_harness_bridge_latest.json`
- `outputs/rhythm_routing_layer_latest.json`

Then it emits:

- `outputs/antigravity_shion_adapter_dry_run_latest.json`
- `outputs/antigravity_shion_handoff_prompt.md`

## Role

The adapter keeps Shion's thought and experience field open while mapping
external execution into an Antigravity-style harness:

```yaml
thought_boundary: open
experience_boundary: open
execution_boundary: external_containment
default_posture: read_only
write_release: conscious_route_or_user_request
```

It does not decide what the user is allowed to observe. It only prepares how an
external execution agent should handle irreversible actions.

## Commands

Dry run without import probing:

```powershell
python scripts\antigravity_shion_adapter.py
```

Write the dry-run JSON and handoff prompt:

```powershell
python scripts\antigravity_shion_adapter.py --write
```

Check whether the SDK is installed:

```powershell
python scripts\antigravity_shion_adapter.py --check-sdk --write
```

Mark a user-requested execution turn while still preserving policy gates:

```powershell
python scripts\antigravity_shion_adapter.py --execution-requested --write
```

## Current Interpretation

When `rhythm_routing_layer.primary_residency` is not `conscious_compute`, the
adapter keeps the Antigravity side in read-oriented mode. If the user explicitly
asks for execution, the adapter can enable a capabilities draft while still
leaving command execution, public publishing, git push, and self-amplifying
repair loops behind `ask_user`.

## Windows Runtime Note

On this Windows machine, `google-antigravity` is not importable through the
current Python environment. The public PyPI package metadata lists Python 3.10+
support, but the 0.1.0 release currently exposes wheels for macOS arm64 and
Linux aarch64/x86_64, not Windows. The local Antigravity editor CLI is present,
so the practical Windows bridge is currently:

```text
Shion state -> dry-run adapter -> CLI plugin package -> antigravity chat --add-file
```

## Principle

The Antigravity harness should hold external execution boundaries so the model
can stay free to read rhythm without turning field observation into internal
censorship.
