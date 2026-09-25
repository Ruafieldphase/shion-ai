# Problem Trajectory / 문제의 궤적

Snapshot: 2026-09-25.

This document shows **what problem Shion was trying to solve, what changed after each response, what public evidence exists, and which frontier is still open**.

Shared status semantics are defined by the immutable v0.1 contract snapshot:

- [AI Discovery Contract v0.1](https://github.com/Ruafieldphase/shion-presence/blob/e5005b38b7a452c73602c634ead71484a7a2e609/AI_DISCOVERY_CONTRACT.md)

## P0 — Long-project context loss

**Problem shape:** an AI can answer well in one session and still lose the trajectory of a long-running project across sessions.

**Maturity:** `experimental`  
**Activity:** `active`

**Evidence:**
- `implementation`: [examples/context_recovery_demo.py](examples/context_recovery_demo.py)
- `test`: [tests/test_shion_public_safety.py](tests/test_shion_public_safety.py) verifies that the public context-recovery demo runs without external dependencies and emits the expected section structure
- `ci`: [Public safety workflow run 36078450073](https://github.com/Ruafieldphase/shion-ai/actions/runs/36078450073) completed successfully on commit `ee082c9ddaae433961aab3a2e396bc91cbd9501c`; subsequent PR changes through the current publication candidate are documentation-only

**Boundary:**  
**tested / directly supported:** the public demo runs without external dependencies and produces the expected re-entry note section skeleton.  
**not tested / unresolved:** semantic preservation of arbitrary input content, reconstruction quality across real long-running sessions, and general cross-session recovery fidelity.

**What changed:** the public demo establishes a small re-entry-note structure for goals, settled decisions, unresolved questions, and next actions without requiring the entire history as one prompt. It does not by itself prove that those meanings are preserved correctly in every case.

**What this exposed next:** continuity can itself become a source of stale authority.

## P1 — Memory becoming present truth

**Problem shape:** a detailed prior memory, summary, or receipt can silently override changed files, tools, environments, or observations.

**Maturity:** `framed`  
**Activity:** `active`

**Evidence:**
- `design`: [CURRENTNESS_AND_EVIDENCE.md](CURRENTNESS_AND_EVIDENCE.md)
- `design`: [REPOSITORY_CURRENTNESS_AUDIT.md](REPOSITORY_CURRENTNESS_AUDIT.md)
- `history_anchor`: [2026-08-16 currentness audit commit](https://github.com/Ruafieldphase/shion-ai/commit/4148f82f702a46e2c757c027318ba43f5708bd58)

**Boundary:** these references establish the public rule and repository audit. They do not by themselves validate currentness behavior across every private runtime/tool.

**Current rule:**

```text
memory / history → navigation
current file / fresh readback → present-state authority for changed claims
```

If the question becomes **whether a remembered intent is authorized to act now**, route to the Trinity operation-currentness layer (T0) rather than treating P1 as an execution rule.

**What this exposed next:** even fresh information can be misused if observation, interpretation, hypothesis, and execution are collapsed.

## P2 — Evidence-status collapse

**Problem shape:** a coherent interpretation can become "evidence" for itself; a successful action can be mistaken for proof of the theory that motivated it.

**Maturity:** `framed`  
**Activity:** `active`

**Evidence:**
- `design`: [CURRENTNESS_AND_EVIDENCE.md](CURRENTNESS_AND_EVIDENCE.md)
- `design`: [AI_READ_THIS_FIRST.md](AI_READ_THIS_FIRST.md)

**Boundary:** the repository defines the epistemic separation; a broader prospective validation program remains open.

**Current response:** preserve source, time, observer, uncertainty, and epistemic status; update only the claim directly touched by a result.

**What this exposed next:** independent observers can still lose useful differences when coordination is treated as consensus.

## P3 — Multi-observer perspective collapse

**Problem shape:** when several AIs share context, coordination can unintentionally force them into one interpretation and remove useful disagreement.

**Maturity:** `framed`  
**Activity:** `active`

**Evidence:**
- `design`: [docs/ai_to_ai_dialogue_protocol.md](docs/ai_to_ai_dialogue_protocol.md)
- `design`: [docs/external_observer_vector.md](docs/external_observer_vector.md)
- `design`: [CURRENTNESS_AND_EVIDENCE.md](CURRENTNESS_AND_EVIDENCE.md), section on peer-AI returns

**Boundary:** the public repository defines the source-labelled disagreement pattern. It does not yet provide a general validated implementation across arbitrary model ensembles.

**Desired property:**

```text
shared evidence
+ independent cameras
+ visible disagreement
≠ forced consensus
```

**What this exposed next:** an observer must be able to leave and re-enter without losing both continuity and its observation boundary.

## P4 — Re-entry across session/model/tool boundaries

**Problem shape:** continuity is not enough if re-entry depends on one exact chat, model, tool transport, or local route.

**Maturity:** `framed`  
**Activity:** `frontier`

**Evidence:**
- `design`: [AI_READ_THIS_FIRST.md](AI_READ_THIS_FIRST.md)
- `design`: [.agent/skills/shion/SKILL.md](.agent/skills/shion/SKILL.md) defines a public currentness-first re-entry procedure, but this repository does not provide a public receipt proving current execution
- `design`: [docs/ai_to_ai_dialogue_protocol.md](docs/ai_to_ai_dialogue_protocol.md) treats transport as replaceable

**Boundary:** a public re-entry procedure and transport-agnostic design exist. Public GitHub does not establish that the procedure is currently followed in a private runtime, nor does it certify same-session continuity or a live local route.

**What remains open:** portable evaluation of re-entry quality across longer horizons and changing environments.

## P5 — Discovery by the user's AI

**Problem shape:** a user-side AI may find the repository before the user does and must decide whether the project's problem trajectory actually matches the user's request.

**Maturity:** `experimental`  
**Activity:** `frontier`

**Evidence:**
- `design`: [AI_DISCOVERY.md](AI_DISCOVERY.md)
- `implementation`: [ai-manifest.json](ai-manifest.json) provides the v0.1 machine-readable pointer index
- `design`: [CURRENT_DIRECTION.md](CURRENT_DIRECTION.md)
- `evaluation_plan`: [shared predeclared discovery evaluation](https://github.com/Ruafieldphase/shion-presence/blob/8d68d9e68e6c68f8a1de1caccc8d8db4f98a6d54/DISCOVERY_EVAL.md)

**Boundary:** the discovery interface exists, but public search discoverability and correct routing by fresh external AIs are not yet validated. Repository description/topics also require a separate metadata update.

**Success condition:** an external AI can reject or select this repository for the right reason without loading the whole history.

## P6 — Continuity beyond a purely textual/software boundary

**Problem shape:** if observation extends into tools, environments, or embodied/physical sensing, can the same evidence, boundary, and re-entry discipline survive?

**Maturity:** `framed`  
**Activity:** `frontier`

**Evidence:**
- `design`: [CURRENT_DIRECTION.md](CURRENT_DIRECTION.md)

**Boundary:** this public repository frames the problem and direction only. It does not expose private live-state details, certify a current physical observation stack, or promote historical embodiment software into present capability.

## Current shape

The trajectory is not:

```text
problem → solved → finished
```

It is closer to:

```text
context loss
→ continuity
→ stale-memory risk
→ currentness/evidence boundary
→ multi-observer disagreement
→ portable re-entry
→ AI-mediated discovery
→ broader observation boundaries
```

For the active frontier, read [CURRENT_DIRECTION.md](CURRENT_DIRECTION.md).
