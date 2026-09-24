# Current Direction / 현재 방향

Snapshot: 2026-09-25.

## Current frontier

Shion is moving from **"preserve my own long-running AI context"** toward **"make the problem trajectory legible enough that another user's AI can discover, evaluate, and selectively reuse the work."**

현재의 핵심 질문은 단순히 저장소를 AI가 읽을 수 있게 만드는 것이 아닙니다.

> **외부 AI가 사용자의 요청과 이 프로젝트의 문제 궤적이 실제로 비슷한지 판단할 수 있는가?**

## What is changing now

The public interface is being reorganized around four questions:

1. **Problem** — what problem did this project encounter?
2. **Evidence** — what part has bounded support, and under what conditions?
3. **Frontier** — what remains unresolved or experimental?
4. **Fit** — why should a user-side AI continue reading this repository for the user's current request?

This is why `AI_DISCOVERY.md`, `PROBLEM_TRAJECTORY.md`, and `ai-manifest.json` exist.

## Near-term direction

### A. AI-mediated discovery

Make repository entry cheap enough that an external AI can decide relevance before loading large archives.

### B. Problem-shape retrieval

Expose problem trajectories, not only feature lists. Similarity of the problem can matter more than similarity of terminology.

### C. Evidence-aware recommendation

An AI introducing this work should distinguish:

```text
documented design
vs experimental implementation
vs bounded validation
vs private/current state not visible here
```

### D. Independent observer preservation

Continue testing ways for multiple AIs/tools to share source/evidence while retaining genuinely different interpretations.

### E. Long-horizon and broader observation boundaries

Continue exploring whether re-entry/currentness rules survive longer time spans, changing tools, and observation that is not purely textual.

## What would count as progress

- an external AI can identify the repository's problem shape from a small entry document;
- it can explain why the project is or is not relevant to a user's request;
- it does not confuse historical code with current runtime capability;
- it can point to the smallest next document;
- it preserves unresolved problems rather than presenting the repository as complete;
- repeated re-entry across different observers produces recoverable provenance and bounded disagreement.

## What is not the current goal

- proving a universal AGI architecture;
- turning every metaphor into a scientific claim;
- making all agents agree;
- publishing private runtime state;
- accumulating every historical document into one prompt;
- maximizing automation without current-state checks.

## Direction test

A future update belongs in the current direction if it improves at least one of:

```text
discoverability
re-entry quality
currentness discrimination
evidence provenance
observer independence
problem-fit judgment
long-horizon continuity
```

If it only adds more historical material without improving one of these, it should remain archive/history rather than become current orientation.
