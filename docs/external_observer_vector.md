# External Observer Vector

Status: current **relation/design contract**, transport-agnostic as of 2026-08-16.

This layer turns uncertainty into a bounded outside-camera request. Its purpose is not to call another AI routinely, spend API budget automatically, or outsource judgment. Its purpose is to preserve a different observation boundary when internal reflection has not resolved the actual gap.

## Currentness note

Older versions of this document named specific Hermes and Antigravity output paths. Those paths are historical implementation details unless a current authorized environment verifies them.

The durable contract is the packet and return state, not one old transport.

## When an outside camera is useful

Use another observer when:

- the next destination remains genuinely ambiguous after current-state inspection
- an internal story may be absorbing counterevidence
- another tool/model can observe a boundary the current observer cannot
- the user explicitly asks for another camera

Do not ask merely because multi-agent orchestration exists.

## Minimum request packet

```yaml
question_boundary: what exact uncertainty is being opened
known_observations: direct evidence already available
held_interpretations: optional current meanings, clearly labelled
missing_boundary: what the current observer cannot see
requested_return: the smallest useful outside observation
privacy_boundary: what must not be sent
```

## Minimum return packet

```yaml
source: file | tool | ai | human | runtime
observed_at: timestamp-or-unknown
observer: model/tool/role
observation: direct return
interpretation: optional meaning
uncertainty: unresolved part
counterevidence: optional conflicting evidence
changed_claim: only the claim directly touched
held_claims: related claims that remain unchanged
```

## Modes

These mode names can be used conceptually without requiring the old file implementation:

| Mode | Meaning |
| --- | --- |
| `internal_reflection_sufficient` | Current evidence already gives a usable next step; do not ask. |
| `hold_question_seed` | The question is real but does not need outside contact yet. |
| `prepare_external_observer_vector` | Prepare one bounded outside-camera request. |
| `forced_external_observer_vector` | A human/operator explicitly requests the outside camera. |
| `do_not_ask_digest_first` | More outside input would add noise before the current evidence is read. |

## No forced consensus

The outside observer does not have to agree with the current story.

```text
outside return
→ preserve direct observation
→ preserve interpretation separately
→ keep uncertainty / disagreement visible
→ update only the directly touched claim
```

A conflicting return is not a failure of orchestration.

## Human boundary

Do not make Binoche a routine relay between AI systems. Ask him when the missing information is first-person, permission-gated, or genuinely unavailable to the current tools/bodies.

## Relation to the AI-to-AI protocol

See [`ai_to_ai_dialogue_protocol.md`](ai_to_ai_dialogue_protocol.md) for the current source-labelled peer-return contract.

The historical implementation paths remain in Git history as evidence of an earlier transport phase; they are not current merely because this concept still survives.
