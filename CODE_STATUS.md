# Public Code Status

Status: 2026-08 repository currentness contract.

The Python, scripts, services, tests, examples, and workflow files in this repository are a **public code snapshot accumulated across multiple experimental phases**.

They are not, by filename or presence alone, proof of what the private Shion runtime is executing now.

## Reading rule

Treat public code as one of four things until a current runtime check says otherwise:

1. executable example
2. experimental implementation
3. prior runtime implementation
4. reusable design ancestor

Do not silently promote it to `current operational dependency`.

## What must be re-checked before execution claims

For any code path that may have changed, verify in the authorized environment:

- the file itself is current
- expected inputs and output paths still exist
- referenced services/endpoints are available
- credentials/permissions are valid where required
- dependencies are installed
- the process is actually intended to run now
- the returned result matches the current contract

A historical passing test or an old commit message is not enough.

## Modeling language inside code

Some modules intentionally use names drawn from biology, physics, contemplative practice, music, or internal rhythm language. Examples in the repository include protein/AQP4, field, resonance, dark-field, prism, hippocampus, phase, and related terms.

These names may encode a design prior or an experimental mapping. They do **not** establish that the software reproduces the biological/physical system named by the metaphor.

Where modules already state that a biological or physical analogy is only a design prior, preserve that boundary.

## Live-state rule

The public code tree must not be used to infer:

- the current selected route
- current worker/organ readiness
- which daemon is running
- current model availability
- current pressure or attention state
- current repair candidate
- current external connections

Those are present-state questions and require a current authorized readback.

## Safe use pattern

```text
public code candidate
→ inspect current authorized environment
→ run one bounded check if permitted
→ capture returned result
→ record uncertainty
→ update only the directly touched claim
```

## Why code is not mass-rewritten in this audit

A repository-wide documentation audit can detect stale descriptions, but it cannot prove that a different local implementation should replace each historical module. Rewriting working or historically useful code merely to make modification dates look recent would destroy evidence and create false currentness.

Therefore this pass updates the **reading contract and stale agent instructions**, while holding code semantics unless a current execution/readback specifically touches them.
