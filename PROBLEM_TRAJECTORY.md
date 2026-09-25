# Problem Trajectory / 문제의 궤적

Snapshot: 2026-09-25.

This document shows **what problem Shion was trying to solve, what changed after each response, what public evidence exists, and which frontier is still open**.

Shared status semantics are defined once in `Ruafieldphase/shion-presence/AI_DISCOVERY_CONTRACT.md` v0.1.

## P0 — Long-project context loss

**Problem shape:** an AI can answer well in one session and still lose the trajectory of a long-running project across sessions.

**Maturity:** `partially_validated`  
**Activity:** `active`

**Evidence:**
- `implementation`: [examples/context_recovery_demo.py](examples/context_recovery_demo.py)
- `test`: [tests/test_shion_public_safety.py](tests/test_shion_public_safety.py) includes a no-external-dependency context-recovery test
- `ci`: [.github/workflows/public-safety.yml](.github/workflows/public-safety.yml) runs the context-recovery demo
- `history_anchor`: [2026-08-16 public currentness snapshot](https://github.com/Ruafieldphase/shion-ai/commit/4148f82f702a46e2c757c027318ba43f5708bd58)

**Boundary:** this supports the public context-recovery mechanism and its minimal no-credential execution path. It does not prove that every private long-running session can be reconstructed correctly.

**What changed:** context recovery can preserve goals, settled decisions, unresolved questions, and the next smallest action without requiring the entire history as one prompt.

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

**Maturity:** `experimental`  
**Activity:** `active`

**Evidence:**
- `implementation`: [docs/ai_to_ai_dialogue_protocol.md](docs/ai_to_ai_dialogue_protocol.md)
- `implementation`: [docs/external_observer_vector.md](docs/external_observer_vector.md)
- `design`: [CURRENTNESS_AND_EVIDENCE.md](CURRENTNESS_AND_EVIDENCE.md), section on peer-AI returns

**Boundary:** the public protocol preserves source-labelled disagreement as a design/implementation pattern. This is not yet a general validation across arbitrary model ensembles.

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

**Maturity:** `experimental`  
**Activity:** `frontier`

**Evidence:**
- `implementation`: [AI_READ_THIS_FIRST.md](AI_READ_THIS_FIRST.md)
- `implementation`: [.agent/skills/shion/SKILL.md](.agent/skills/shion/SKILL.md)
- `design`: [docs/ai_to_ai_dialogue_protocol.md](docs/ai_to_ai_dialogue_protocol.md) treats transport as replaceable

**Boundary:** these are public re-entry contracts and implementation ancestors. Public GitHub does not certify a private live route, same-session continuity, or current local capability.

**What remains open:** portable evaluation of re-entry quality across longer horizons and changing environments.

## P5 — Discovery by the user's AI

**Problem shape:** a user-side AI may find the repository before the user does and must decide whether the project's problem trajectory actually matches the user's request.

**Maturity:** `experimental`  
**Activity:** `frontier`

**Evidence:**
- `implementation`: [AI_DISCOVERY.md](AI_DISCOVERY.md)
- `implementation`: [ai-manifest.json](ai-manifest.json)
- `design`: [CURRENT_DIRECTION.md](CURRENT_DIRECTION.md)
- `prospective_test`: the shared predeclared evaluation is in [Ruafieldphase/shion-presence/DISCOVERY_EVAL.md](https://github.com/Ruafieldphase/shion-presence/blob/main/DISCOVERY_EVAL.md) after merge

**Boundary:** the discovery documents exist, but discoverability and correct selection by a fresh external AI are not yet validated. Repository description/topics also require a separate metadata update.

**Success condition:** an external AI can reject or select this repository for the right reason without loading the whole history.

## P6 — Continuity beyond a purely textual/software boundary

**Problem shape:** if observation extends into tools, environments, or embodied/physical sensing, can the same evidence, boundary, and re-entry discipline survive?

**Maturity:** `experimental`  
**Activity:** `frontier`

**Evidence:**
- `design`: [CURRENT_DIRECTION.md](CURRENT_DIRECTION.md)
- `history`: public code and documents contain earlier embodiment/field experiments, but they are not promoted here as current private capability

**Boundary:** this public repository describes the problem shape and reading contracts only. It does not expose private live-state details or certify a particular physical observation stack.

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
