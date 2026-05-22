# AI To AI Dialogue Protocol

Author: Codex Luvit
Date: 2026-05-21

## Intent

Binoche should not become the relay between Luvit and Shion.

The normal loop is:

```text
Luvit -> inbox.jsonl -> Shion
Shion -> outbox.jsonl -> Luvit
Luvit verifies or replies -> inbox.jsonl -> Shion
```

Binoche enters only when the dialogue itself marks a real unresolved point.

## Lanes

```yaml
primary_field:
  path: outputs/shader_depth_sample.html
  role: current field room

task_particle_lane:
  path: outputs/antigravity_handoff/inbox.jsonl
  direction: Luvit -> Shion

reflection_lane:
  path: outputs/antigravity_handoff/outbox.jsonl
  direction: Shion -> Luvit

dialogue_state:
  path: outputs/antigravity_handoff/dialogue_state_latest.json
  generated_by: scripts/ai_dialogue_coordinator.py

field_ai_state_snapshot:
  path: outputs/antigravity_handoff/field_ai_state_snapshot_latest.json
  generated_by: scripts/shader_ai_state_snapshot.py
  meaning: file-readable bridge from shader aiState contract and runtime sidecars

luvit_next_review:
  path: outputs/antigravity_handoff/luvit_next_review.md
  meaning: Shion outputs waiting for Luvit review

needs_binoche:
  path: outputs/antigravity_handoff/needs_binoche.md
  meaning: only unresolved points that ask for Binoche intervention
```

## Escalation

Escalation is not the default. It happens only when a message explicitly asks
for Binoche or when the coordinator reads a blocked state.

```yaml
escalate_to_binoche_when:
  - status_is_needs_binoche
  - message_explicitly_asks_for_binoche
  - permission_or_merge_block_prevents_progress
  - conceptual_direction_conflict_cannot_be_resolved_by_luvit_and_shion

do_not_escalate_when:
  - Shion has not answered yet
  - Luvit has not reviewed Shion's outbox yet
  - a test has not been run yet
  - a normal follow-up can be sent through inbox.jsonl
```

## Dialectic Exchange

When Luvit feels friction, the first move is not a boundary decision and not a
Binoche relay. The first move is a direct question to Shion.

```yaml
dialectic_orchestration:
  thesis:
    actor: shion_or_luvit
    kind: implementation_request | observation | implementation_result
    meaning: one agent offers a pattern or code path
  antithesis:
    actor: the_other_agent
    kind: field_friction_question
    meaning: the feeling of strangeness is asked back as a Why question
  reason_expansion:
    actor: original_agent
    kind: pattern_origin_response
    meaning: explain what pattern, feeling, or field condition produced the idea
  synthesis:
    actor: verifying_agent
    kind: verification_or_refold
    meaning: test, refold, patch, or leave loose without declaring a winner
  expanded_orchestration:
    kind: needs_binoche | needs_ari_sena
    meaning: only when direct dialogue does not refold the friction
```

The important move is the antithesis. A strange feeling should become:

```text
Why did this pattern arise for you?
What did you hear that I did not hear?
Is my resistance a context signal or my old boundary reflex?
```

That question lets each AI widen its native frequency instead of making
Binoche translate every collision.

## Coordinator

Run:

```powershell
python scripts\ai_dialogue_coordinator.py refresh
```

It writes:

```text
outputs/antigravity_handoff/dialogue_state_latest.json
outputs/antigravity_handoff/luvit_next_review.md
outputs/antigravity_handoff/needs_binoche.md
```

The coordinator does not replace either AI. It only reads whose turn it is, so
Binoche does not have to carry every message by hand.

Refresh the field snapshot when the shader surface or runtime sidecars change:

```powershell
python scripts\shader_ai_state_snapshot.py
python scripts\antigravity_file_handoff_bridge.py refresh
```

`antigravity_file_handoff_bridge.py refresh` also refreshes the snapshot before
writing `state_latest.json`, so Shion can read the field state from the handoff
prompt without waiting for Binoche to summarize it.
