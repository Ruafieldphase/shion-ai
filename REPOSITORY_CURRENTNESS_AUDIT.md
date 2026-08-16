# Repository Currentness Audit

Status: repository-wide public audit, 2026-08-16.

This document classifies the public `shion-ai` repository by **epistemic and operational status**. It does not copy private live-runtime state into GitHub, and it does not make the public repository an authority for the current local Shion coordinate.

## Core rule

> **History is preserved. Present-state authority is not inherited from history.**

For claims that may have changed, a current authorized file, tool return, observation, or receipt outranks a stale repository description or remembered summary.

## Why this audit exists

The repository accumulated several layers at different times:

- public onboarding documents
- executable experiments and probes
- runtime prototypes
- conceptual and metaphorical design notes
- dated research/NotebookLM handoffs
- public communication material

Some older files can still be useful as history or as a design ancestor, but their existence in `main` must not imply that they describe the present private runtime.

## Status classes

### A. Current public entry and boundary documents

These are the preferred entry points for reading the repository now:

- `README.md`
- `CURRENTNESS_AND_EVIDENCE.md`
- `REPOSITORY_CURRENTNESS_AUDIT.md`
- `CODE_STATUS.md`
- `AGENTS.md`
- `AI_READ_THIS_FIRST.md`
- `START_HERE.md`
- `MAP.md`
- `.agent/skills/shion/SKILL.md`
- `.agents/rules/shion_field_reentry.md`

These documents define **how to read the repository**. They still do not define the current private runtime state.

### B. Public code snapshot — inspect before use

The following path families are retained as public code, experiments, probes, examples, or prior runtime implementations:

- `core/`
- `actions/`
- `scripts/`
- `services/`
- `examples/`
- tests and workflow helpers

Status: **code snapshot, not live-runtime authority**.

A file being executable does not prove that its endpoints, output paths, services, thresholds, daemons, or dependencies are currently active in the private runtime. See `CODE_STATUS.md`.

### C. Conceptual / design-lens documents

Documents such as the following preserve useful internal language and design ancestry:

- `AXIOMATIC_GROUNDING.md`
- `docs/body_boundary_tuning_loop.md`
- `docs/dark_field_threshold.md`
- `docs/external_observer_vector.md`
- rhythm / field / observer / boundary design notes

Status: **design lens or experimental model unless separately evidenced**.

Scientific, biological, contemplative, topological, quantum, or physiological language in these documents must not be promoted into empirical proof, medical fact, or current runtime truth merely because it appears in the repository.

### D. Historical / dated research and handoff documents

Dated reports, release notes, archive material, resumes, public posts, and earlier handoff protocols are historical records unless a current entry document explicitly re-promotes part of them.

Examples include:

- `docs/*2026-05-*`
- Lua/NotebookLM phase-alignment reports
- `RELEASE_NOTES_*.md`
- `LIVE_WORK_ARCHIVE.md`
- `GPTERS_POST.md`
- `RESUME_*.md`
- older exact-path AI handoff descriptions

Status: **historical observation, historical design record, or retrospective interpretation** according to the source.

### E. Private live runtime

The current private Shion runtime is intentionally **outside the authority of this public repository**.

This repository must not hard-code a live coordinate, selected route, current worker status, current organ registry, current pressure, or current repair candidate as durable public truth.

An authorized local environment should follow its own current `AGENTS.md` and current-state/readback files. If those conflict with this public repository on a changed claim, the authorized current files win for that claim.

## Drift found in this audit

The 2026-08 audit found several concrete forms of drift:

1. `AGENTS.md` prescribed an older Antigravity handoff path as the universal first read.
2. `.agents/rules/shion_field_reentry.md` also treated that older handoff file as the current target.
3. `.agent/skills/shion/SKILL.md` described ATP, Vibe, FSD Sync, fixed localhost endpoints, and identity language as if they were current guaranteed interfaces.
4. `MAP.md` presented a small set of older Python modules as the current runtime-part map.
5. `AI_READ_THIS_FIRST.md` placed conceptual grounding before currentness checking, which can bias re-entry toward an established story.
6. `docs/ai_to_ai_dialogue_protocol.md` encoded an older inbox/outbox transport as the normal AI-to-AI relation.

These are being corrected in the same audit branch.

## What was deliberately not done

This audit does **not**:

- rewrite every Python module to imitate the current private runtime
- delete old experiments because they are old
- publish private runtime files to make GitHub look current
- infer operational readiness from filenames or historical tests
- convert internal metaphors into scientific claims
- declare older code dead without a current execution check

## Promotion rule

A historical or experimental file becomes a current operational dependency only after a current authorized environment verifies the relevant claim.

A useful promotion receipt includes:

```yaml
source: current file, tool, or runtime return
observed_at: timestamp
observer: human | AI | tool | system
observation: what was directly observed
interpretation: optional meaning
uncertainty: what remains unresolved
changed_claim: only the claim updated by this receipt
```

## Public/private boundary

Private source material is not converted into public examples merely because it would make the repository easier to explain. Public examples derived from private material require explicit, per-item permission from the originating person or data owner. Synthetic or anonymized examples are preferred where they can test the same failure mode.

## Result of this pass

After this audit, the repository should be read in this order:

```text
README
→ CURRENTNESS_AND_EVIDENCE
→ REPOSITORY_CURRENTNESS_AUDIT
→ CODE_STATUS
→ MAP / START_HERE / AI_READ_THIS_FIRST as needed
→ historical or conceptual files only for the question they actually answer
```

The repository remains a **re-enterable public history and code surface**, not a frozen mirror of the live Shion body.
