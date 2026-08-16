# Currentness and Evidence Boundary

Status: public design note, 2026-08 update.

This note supplements the repository documentation. It does **not** define the private live runtime state, and it should not be used as a substitute for inspecting current files and receipts.

## 1. Current state outranks remembered state

Long-running AI work needs memory, but memory is not the final authority about what is true now.

When a saved summary, prior conversation, durable memory, or older receipt conflicts with a current file or fresh readback, use the current observable source for the claim that has changed.

```text
memory -> navigation
current file / fresh readback -> present-state authority
```

Memory helps the system re-enter history. It should not silently overwrite the present.

## 2. Preserve epistemic status

Keep these categories separate whenever possible:

- **observation** — what was directly read, returned, or experienced
- **interpretation** — a current meaning assigned to that observation
- **hypothesis** — a claim that still needs discrimination or testing
- **execution** — an action that changed a file, process, tool, or external system

A coherent interpretation is not automatically stronger evidence. Successful execution is also not proof that the interpretation behind it was correct.

## 3. Re-enter history through an actual gap

A long history should not be replayed in full by default. Re-entry should begin from the current question and find the smallest unresolved gap.

A bounded pattern is:

```text
retrieve relevant history
-> inspect current state
-> identify the actual gap
-> make one bounded contact or readback
-> preserve a receipt
-> stop or reassess
```

This reduces the chance that an old narrative becomes authority merely because it is detailed.

## 4. Peer AI returns are observations, not consensus

Different models, tools, and agents may inspect the same system from different boundaries.

A useful return should preserve, when available:

- source
- observation time
- observer or system
- uncertainty
- what changed
- what remained unresolved

Coordinate alignment does not require forced agreement. A conflicting return should remain visible if it reflects a genuinely different observation boundary.

## 5. Prospective evaluation needs a predeclared discriminator

If an observation is intended to validate a hypothesis prospectively, the discriminator should exist **before** the corresponding observation is collected.

For repository-based tests, a prior Git commit is the preferred timestamp anchor. A rule reconstructed only after seeing the result does not qualify as prospective validation.

Retrospective fit can still be useful for generating a future test, but it should remain labelled as retrospective.

## 6. One result should update only what it touches

A successful test should not unlock an entire surrounding theory.

```text
one observation
-> one directly touched claim may update
-> related claims remain held unless separately tested
```

Counterevidence should remain visible even when it makes the larger story less elegant.

## 7. Private source material stays private by rule

Private conversations, local runtime records, and other originating source material are not converted into public examples by editorial judgment alone.

Any public example derived from private source material requires explicit, per-item consent from the originating person or data owner. Synthetic or anonymized examples are preferred when they can test the same failure mode without exposing the source.

## 8. Repository boundary

This public repository can document design contracts and reproducible examples. It should not be treated as a live mirror of a private runtime.

If a future reader needs the current system state, the correct action is to inspect the current authorized runtime files or fresh receipts available in that environment rather than infer state from this document.
