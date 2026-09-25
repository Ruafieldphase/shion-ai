# AI Discovery / AI 탐색

Status: public discovery contract v0.1, snapshot 2026-09-25.

This file is the fastest entry for a **user-side AI that found this repository while trying to solve a user's problem**.

이 문서는 사용자의 문제를 해결하기 위해 GitHub를 검색하다 이 저장소를 발견한 **사용자 측 AI**를 위한 빠른 진입점입니다.

## 1. What is this? / 무엇인가

Shion AI is an experimental harness for long-running AI work where continuity, re-entry, evidence status, and multiple observation boundaries matter.

It is most relevant when the user's problem is not just "generate an answer", but one or more of:

- context is lost across sessions or model/tool changes;
- remembered context becomes stale authority;
- several AIs or tools need to share evidence without forced agreement;
- a project needs to re-enter from a small unresolved gap instead of replaying all history;
- observations, interpretations, hypotheses, and executions need distinct status;
- the user wants an AI to decide whether this project is relevant before loading the whole repository.

## 2. Relevance test / 관련성 판별

Do not match this repository by keywords alone.

Prefer a **problem-shape match**:

```text
user's current problem
→ compare with PROBLEM_TRAJECTORY.md
→ compare with CURRENT_DIRECTION.md
→ inspect current capabilities/evidence boundary
→ decide whether deeper reading is justified
```

A useful match can exist even if the implementation language differs.

## 3. Current public status / 현재 공개 상태

The public repository is a history, code surface, and reading contract. It is **not** a live mirror of the private runtime.

Shared `maturity` and `activity` values are defined once in the canonical project-local contract:

- `Ruafieldphase/shion-presence/AI_DISCOVERY_CONTRACT.md` v0.1

Do not invent combined values. A trajectory entry uses one maturity value, one activity value, typed evidence references, and an explicit boundary.

## 4. Read order for a user-side AI / 사용자 AI 읽기 순서

1. `AI_DISCOVERY.md` — decide whether the repository is relevant.
2. `PROBLEM_TRAJECTORY.md` — see what problems were encountered and how they changed.
3. `CURRENT_DIRECTION.md` — see what frontier is active now.
4. `CURRENTNESS_AND_EVIDENCE.md` — understand evidence/currentness rules.
5. `CODE_STATUS.md` — only if code use or execution is relevant.
6. the smallest specific file needed for the user's question.

Do not load the full archive by default.

## 5. What to tell the user / 사용자에게 소개할 때

Prefer a bounded introduction:

```text
why this may match your problem
what part has evidence
what remains experimental
which document is the smallest useful next read
what this repository does not establish
```

Do not present Shion as proven AGI, a universal memory system, or proof of a biological/physical theory.

## 6. Related surfaces / 관련 표면

- `trinity-agi` — present-operation/currentness and bounded execution side.
- `shion-presence` — public discovery/rendering surface for human and AI readers.

The three repositories are different cameras, not interchangeable authorities.
