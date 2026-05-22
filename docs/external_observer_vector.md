# External Observer Vector

This layer turns uncertainty into a bounded question.

It does not call another AI, spend API budget, publish anything, or mutate the
workspace. It observes when internal reflection has not lifted a clear next
destination and prepares a copy-paste packet for Shion/Antigravity or another
peer observer.

## Why It Exists

Internal reflection is usually enough when a next destination is already clear.
When the field becomes ambiguous, blocked, or over-linearized, another observer
can add a different phase vector. The point is not to outsource judgment. The
point is to break a closed loop without turning questions into a routine.

## Outputs

- `outputs/hermes/external_observer_vector_latest.json`
- `outputs/hermes/external_observer_vector_latest.md`
- `outputs/hermes/external_observer_vector.jsonl`
- `outputs/antigravity_handoff/latest.md` when a packet exists

## Modes

| Mode | Meaning |
| --- | --- |
| `internal_reflection_sufficient` | The current path is clear enough. Do not ask. |
| `hold_question_seed` | A question is forming, but can wait. |
| `prepare_external_observer_vector` | Ask Shion or a peer for a bounded outside vector. |
| `forced_external_observer_vector` | A human or caller explicitly requested a packet. |
| `do_not_ask_digest_first` | External input would add pressure before the field can receive it. |

## Command

```powershell
python scripts\external_observer_vector.py `
  --issue-context "purpose is unclear after internal reflection" `
  --uncertainty 0.8 `
  --blockage 0.6
```

Use `--force-request` only when the user or operator explicitly wants a Shion
handoff packet even if the local field looks clear.

## Contract

- This is not a schedule.
- This is not a meeting routine.
- This is not automatic multi-agent delegation.
- It is a low-pressure membrane for asking when the next destination does not
  rise from the current internal reflection.

