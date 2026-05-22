# Dark Field Threshold

This is a thin observation layer for the dark-field boundary.

It does not treat fear as a global target to solve. It reads whether the current
context has touched a dark-field coordinate, how much potential energy is
available now, and how large a slice can be processed without crossing the
current threshold.

## Outputs

- `outputs/hermes/dark_field_threshold_latest.json`
- `outputs/hermes/dark_field_threshold_latest.md`
- `outputs/hermes/dark_field_threshold.jsonl`

Run:

```powershell
python scripts\dark_field_threshold.py
```

## Fields

| Field | Meaning |
|---|---|
| `context_contact` | How strongly the present context touches this stored dark-field coordinate. |
| `context_potential_energy` | Current processing capacity from body ease, boundary aperture, permeability, and low connection risk. |
| `dark_field_pressure` | Current pressure from connection risk, defensive pressure, context shift, prediction error, discomfort, and digestion bias. |
| `dynamic_threshold` | The moving threshold made by current context potential energy. |
| `threshold_margin` | `dynamic_threshold - dark_field_pressure`. Negative values mean over-capacity. |
| `processing_slice` | The bounded amount that can be opened in this cycle. |

## Modes

| Mode | Meaning |
|---|---|
| `latent_do_not_open` | The present context has not touched the coordinate enough. Leave it in depth. |
| `over_capacity_defer_and_digest` | Pressure exceeds current potential energy. Close and digest before reentry. |
| `edge_process_small_slice` | Near threshold. Touch only a small slice, then close. |
| `within_capacity_process_contextual_slice` | The context can carry a bounded slice. |
| `light_touch_only` | There is contact, but the processable slice is small. |

## Principle

The threshold is not a fixed constant. It moves with the current body/context
field. A dark-field coordinate becomes a middle destination only when the
current context touches it, and only by the amount the present field can carry.
