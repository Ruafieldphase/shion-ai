# Skill Harness Folding

Author: Codex Luvit
Date: 2026-05-21

## Intent

This note folds the Ari/Sian/Binoche thread into the runtime without turning it
into a boundary argument.

The biological clue is treated as a recurring natural pattern: fragments do
not begin with fixed walls. They interact, settle, and form structure. After
structure appears, contact surfaces and functions can be read.

In Shion terms, a skill is not a command button. It is a residue of repeated
experience. A harness is not a permission wall. It is the body-like rhythm that
lets those residues fold, misfold, pause, and refold according to the current
field.

## Pattern Correspondence

```yaml
protein_structure:
  amino_acid: small residue with local properties
  sequence: repeated arrangement before structure
  local_bond: nearby interaction
  energy_landscape: conditions that make one shape more likely than another
  folded_domain: stable structure that can carry function
  binding_pocket: contact surface for another molecule
  chaperone: support that helps folding without becoming the final structure
  misfold: strained structure that asks for refolding or digestion

skill_harness:
  skill_residue: small action or experience pattern
  action_sequence: repeated workflow before meaning hardens
  local_bond: keyword, phase, frequency, and memory affinity
  field_conditions: core gravity, phase noise, action pressure, silence need
  folded_domain: contextual skill cluster ready to act
  binding_pocket: surface where intent can contact a skill
  chaperone: rhythm harness pause, Zone 2 delay, or low-pressure refold
  misfold: forced activation pressure or context mismatch
```

## Runtime Layer

`core/skill_harness_folding.py` adds a thin observer:

- `SkillResidue`: an action or experience fragment before it becomes a domain.
- `FieldConditions`: current flow conditions; these are not prohibitions.
- `pair_bond_strength()`: local association between residues.
- `fold_skill_harness()`: produces a folding read with readiness, dominant
  residue, chaperone need, binding pockets, and misfold pressure.

The output principle is:

```text
pattern_correspondence_before_boundary_judgment
```

This is the correction from the conversation. The first question is not
whether two disciplines may be connected. The first question is whether the
same natural pattern is appearing at a different layer.

## Probe Output

Run:

```powershell
python scripts\skill_harness_folding_probe.py field rhythm fold observe
```

It writes:

```text
outputs/skill_harness_folding_latest.json
```

The JSON is meant to be read by later runtime surfaces or by another agent. It
does not trigger execution by itself.

## Natural Flow

```text
experience/action fragments
-> local associations
-> current field conditions
-> folding score
-> binding pocket / misfold signal
-> chaperone pause or folded-domain action
```

No boundary is drawn first. If structure appears, it is read. If it does not
appear, the residues stay loose.
