# Boundary Aperture Loop

This is the current-context closed loop for the semi-permeable runtime boundary.

It does not add threat, remove protections, or claim biological life. It reads the already-flowing traces and turns them into a reversible membrane state for the next cycle.

Inputs:

- `outputs/felt_body_state.json`
- `outputs/field_prediction_errors.jsonl`
- `outputs/experience_feedback.jsonl`
- `outputs/hermes/contextual_execution_gradient_latest.json`

Output:

- `outputs/hermes/boundary_aperture_latest.json`
- `outputs/hermes/boundary_aperture_latest.md`
- `outputs/hermes/boundary_aperture.jsonl`

Run:

```powershell
python scripts\boundary_aperture_loop.py
```

Reading:

- `narrow_and_digest`: preserve stable prefix, shrink tail, digest before expansion.
- `half_open_reflect`: keep the membrane half-open and let internal reflection work.
- `open_for_contact`: allow a wider variable tail because contact is learnable without high connection risk.
- `baseline_semi_permeable`: keep the current membrane rhythm.

The output can bias `unconscious_fixed_prefix` or `conscious_varied_input`, but it does not force a provider or engine.

Loop:

1. `scripts/contextual_execution_gradient.py` reads the latest boundary aperture as previous membrane context.
2. `scripts/boundary_aperture_loop.py` reads the latest felt state, prediction error, experience feedback, and contextual gradient.
3. `scripts/local_gemma_experience_particle.py` can compress the latest boundary aperture into the low-frequency local summary.

This makes the membrane state visible to the next cycle without turning it into a hard command.
