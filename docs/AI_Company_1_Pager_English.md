# Shion AI Research One-Pager

## Position

Shion AI is a local AI runtime for continuity, rhythm-aware context, and action regulation. It is not presented as another chatbot wrapper. It is a harness around AI work: a way to preserve intent, recover context, decide when to act, and prevent agent loops from turning into wasteful automation.

## The Problem

Current AI workflows often fail after the first successful prompt:

- The model understands a sentence but loses the user's actual direction.
- The user must repeat prior context across tools and sessions.
- Agents call APIs and tools without preserving why the work matters.
- Creative intent is compressed too quickly into linear problem solving.
- Automation expands until it creates more management work than it removes.

This is why the field has moved from prompt engineering toward context engineering, agent engineering, and harness engineering. The problem is no longer only "how do we phrase the prompt?" It is "how do we preserve the direction, memory, timing, and feedback loop around the prompt?"

## The Approach

Shion is organized as a phase-transition runtime:

1. **Field**: Read the user's pressure, unfinished intent, local state, and prior context.
2. **Convergence**: Compress that field into a workable direction.
3. **Phase Transition**: Decide whether the next step should be action, waiting, digestion, or redirection.
4. **Particle**: Express the direction as a concrete file change, test, document, command, or artifact.
5. **Unified Field**: Feed the result back into continuity so the next session does not start from zero.

## What Improves

For creators:

- Vague creative pressure can become an outline, script, README, design direction, or workflow without losing its original feeling.
- The user does not need to become more mechanical just to work with a logical AI.

For developers:

- Prior architecture and intent can be recovered before code changes.
- Agents can be guided by runtime context instead of tool availability alone.
- Repetition, drift, and unnecessary API use can be reduced.

For public projects:

- The repository can show an accessible entry point for linear readers.
- The deeper rhythm philosophy can remain present without blocking practical understanding.
- Private memory and generated logs can stay out of the public proof surface.

## Technical Surface

Representative public components include:

- `core/orchestrator_daemon.py` for rhythm-level runtime coordination
- `core/ari_prism.py` for boundary and rhythm adjustment
- `core/phase_governor.py` for wait/act/redirect decisions
- `core/fibonacci_orbital_hippocampus.py` for continuity and memory geometry
- `core/unfinished_waypoint_graph.py` for preserving unresolved questions
- `core/korean_context_harness.py` for keeping Korean user framing intact

## Public Status

This repository is a public research and runtime codebase. Generated logs, private memory, local credentials, and personal outputs are intentionally excluded. The public proof surface should be source code, tests, reproducible behavior, and clear documentation.

## Final Question

If your current AI workflow can answer one prompt but cannot preserve the direction behind it, what runtime layer is missing?
