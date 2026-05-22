# Security Boundary Probe

This is a source-separation layer, not a firewall.

It answers one question before interpretation:

> Is this change likely internal metabolism, workspace work, runtime surface, or external contact?

It does not claim intrusion, block traffic, delete files, quarantine processes, or replace normal security tooling. It writes an observation trace that can be read beside `boundary_aperture_latest.json`.

Inputs:

- `git status --porcelain=v1`
- selected file hashes for changed workspace files
- Python/Ollama process observations
- TCP listening sockets
- latest boundary aperture, contextual gradient, prediction error, and experience feedback traces

Outputs:

- `outputs/hermes/security_boundary_latest.json`
- `outputs/hermes/security_boundary_latest.md`
- `outputs/hermes/security_boundary.jsonl`

Run:

```powershell
python scripts\security_boundary_probe.py
```

Modes:

- `baseline_observe`: no strong intrusion claim; keep a trace.
- `verify_boundary_contact`: ambiguity is present; separate sources before interpreting the change as metabolism.
- `narrow_and_verify`: potential external contact is high enough to slow interpretation and preserve evidence before action.

Principle:

Internal traces, workspace edits, runtime listeners, and external contact must remain separate until the field has enough evidence to interpret the change.
