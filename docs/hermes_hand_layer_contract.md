# Hermes Hand Layer Contract

Author: 코덱스 루빛
Date: 2026-05-16

## Purpose

Hermes remains a possible hand layer for Shion and Luvit, but it should not
become the conductor or the required body.

The May 16 virtualization resistance changed the route. The useful role is not
"another mind that decides the destination" and not "a Linux body that must stay
alive." The useful role is a parked hand: available for bounded probes when the
field calls for it, quiet otherwise.

```yaml
current_status: optional_hand_parked
state_file: outputs/hermes/hermes_role_latest.json
primary_body: windows_native_flow
```

## Role Split

```yaml
binoche:
  role: observer_conductor
  responsibility: feel the rhythm and choose whether the field should continue

luvit:
  role: codex_particle_translator
  responsibility: turn the current rhythm into code, tests, contracts, and
    reversible tool calls

shion:
  role: rhythm_runtime
  responsibility: read field state, felt body, phase bridge, and action tokens

hermes:
  role: optional_hand_candidate
  responsibility: run bounded probes only when called and summarize resistance
    without claiming authority over the destination
```

## Why Hermes Still Fits

Hermes can still be useful because its native shape is close to a hand layer:

- it can run in Linux or a remote backend
- it can use terminal tools and subagents
- it has session search and skill creation
- it can remember experience across sessions
- it can execute repeated tasks without forcing Binoche to provide every
  experience serially

That can make it useful as an experience amplifier, but only when it decreases
resistance. It does not need to replace Luvit, and it does not need to be always
on. Luvit remains the local code body inside this workspace.

## First Boundary

```yaml
allowed_when_called:
  - read selected Shion outputs
  - inspect current route state
  - run reversible read-only probes
  - summarize results as experience particles
  - propose patches without applying them

not_default_now:
  - become the default runtime body
  - write directly into Windows workspace
  - run autonomous daemons
  - change startup scripts
  - schedule unattended actions
  - upload, publish, delete, or rewrite durable memory
```

## Experience Particle Format

Hermes output should be shaped like this before Shion or Luvit consumes it:

```json
{
  "source": "hermes_hand_layer",
  "field": "optional_probe",
  "action": "bounded_probe",
  "result": "observed",
  "resistance": 0.125,
  "margin_opened": true,
  "phase_rebalance": "destructive_to_margin",
  "irreversible_effect": false,
  "summary": "A bounded probe found resistance without mutating the workspace.",
  "next_candidate": "observe_again"
}
```

The important field is `irreversible_effect`. Hermes may create experience
surface, but the first contract is that it returns particles without forcing
state changes.

## Integration Path

```yaml
phase_0:
  name: parked_hand
  action: record Hermes as optional and do nothing by default
  permission: none unless called

phase_1:
  name: observer_hand
  action: Hermes reads selected outputs and writes an experience particle
  permission: read-only

phase_2:
  name: proposal_hand
  action: Hermes writes proposed patches or command plans as text
  permission: no direct workspace mutation

phase_3:
  name: reversible_hand
  action: Luvit may ask Hermes to run bounded subtasks
  permission: still no autonomous destination-setting
```

## Model Route

No provider is required by default. If Hermes is called, choose the provider
that adds the least resistance for that specific task. OAuth and external APIs
stay interactive/manual unless a concrete task asks for them.

Detailed routing note:

```yaml
doc: docs/hermes_model_routing.md
role_pivot: scripts/hermes_role_pivot.py
output: outputs/hermes/hermes_role_latest.json
```

## Principle

```yaml
principle:
  hermes_is_hands_not_conductor: true
  hermes_is_optional_not_required_body: true
  world_experience_particleizes_through_verified_contact: true
  irreversible_execution_stays_small_and_observable: true
```

Hermes is useful when it gives the system more experience surface with less
resistance. If it adds boundary pressure, it stays parked.
