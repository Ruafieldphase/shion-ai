# Problem Trajectory / 문제의 궤적

Snapshot: 2026-09-25.

This document shows **what problem Shion was trying to solve, what changed after each partial solution, and which frontier is still open**.

이 문서는 Shion이 어떤 문제를 풀고 있었는지, 부분 해결 뒤 어떤 새 문제가 드러났는지, 현재 어디까지 와 있는지를 보여줍니다.

## Status vocabulary

`observed → framed → experimental → partially_validated → validated_within_boundary → expanded / superseded`

"Validated within boundary" never means the whole surrounding theory is proven.

## P0 — Long-project context loss

**Problem shape:** an AI can answer well in one session and still lose the trajectory of a long-running project across sessions.

**Status:** `partially_validated`

**What changed:** context recovery and re-entry notes can preserve goals, settled decisions, unresolved questions, and the next smallest action without replaying the entire history.

**Boundary:** a recovery note is navigation, not proof that remembered state is still current.

**What this exposed next:** memory continuity can itself become a source of stale authority.

## P1 — Memory becoming present truth

**Problem shape:** a detailed prior memory, summary, or receipt can silently override changed files, tools, environments, or observations.

**Status:** `validated_within_boundary` as a public reading/currentness contract.

**Current rule:**

```text
memory / history → navigation
current file / fresh readback → present-state authority for changed claims
```

**What this exposed next:** even fresh information can be misused if observation, interpretation, hypothesis, and execution are collapsed.

## P2 — Evidence-status collapse

**Problem shape:** a coherent interpretation can become "evidence" for itself; a successful action can be mistaken for proof of the theory that motivated it.

**Status:** `partially_validated`

**Current response:** preserve source, time, observer, uncertainty, and epistemic status; update only the claim directly touched by a result.

**What remains open:** making this discipline portable across heterogeneous tools and long-lived agent workflows.

## P3 — Multi-observer perspective collapse

**Problem shape:** when several AIs share context, coordination can unintentionally force them into one interpretation and remove useful disagreement.

**Status:** `experimental / partially_validated`

**Current response:** share a common source/evidence layer while allowing observers to keep distinct interpretations, provenance, and uncertainty.

**Desired property:**

```text
shared evidence
+ independent cameras
+ visible disagreement
≠ forced consensus
```

**What this exposed next:** an agent must be able to leave and re-enter the work without losing both continuity and its observation boundary.

## P4 — Re-entry across session/model/tool boundaries

**Problem shape:** continuity is not enough if re-entry depends on one exact chat, model, tool transport, or local route.

**Status:** `experimental / partially_validated`

**Current response:** use compact re-entry packets, current-state checks, source-labelled returns, and bounded receipts rather than assuming one permanent transport.

**Boundary:** public GitHub documents cannot certify a private live route or current local capability.

**What remains open:** stronger portable evaluation of re-entry quality across longer horizons and changing environments.

## P5 — Discovery by the user's AI

**Problem shape:** as user-side AIs search repositories on behalf of people, they need to decide not only "what does this repo contain?" but also:

- what problem was it solving?
- which part is actually supported?
- what is still open?
- where is it heading?
- is its problem trajectory similar to my user's request?

**Status:** `framed / active frontier`

**Current response:** add explicit AI discovery metadata, problem trajectory, current direction, currentness labels, and smallest-next-read routes.

**Success condition:** an external AI can reject or select this repository for the right reason without loading the whole history.

## P6 — Continuity beyond a purely textual/software boundary

**Problem shape:** if observation extends into tools, environments, or embodied/physical sensing, can the same evidence, boundary, and re-entry discipline survive?

**Status:** `experimental frontier`

**Public boundary:** this repository may describe the problem shape and contracts, but it does not expose private live-state details or claim that a particular physical observation stack is current.

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

For the active frontier, read `CURRENT_DIRECTION.md`.
