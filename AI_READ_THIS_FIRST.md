# AI Read This First / AI는 먼저 이 문서를 읽으세요

Status: current public AI entry, updated 2026-08-16.

This repository is a **public history, code surface, and reading contract** for Shion. It is not the private live runtime.

이 저장소는 Shion의 **공개 이력·코드 표면·읽기 계약**입니다. private live runtime 자체가 아닙니다.

## Read order / 읽는 순서

Before interpreting the system, read:

1. `README.md`
2. `CURRENTNESS_AND_EVIDENCE.md`
3. `REPOSITORY_CURRENTNESS_AUDIT.md`
4. `CODE_STATUS.md`
5. `MAP.md` if you need the public architecture map

Only after that should you use `AXIOMATIC_GROUNDING.md`, dated reports, live archives, or older runtime documents as historical/conceptual context.

시스템을 해석하기 전에 현재성 경계를 먼저 읽고, 그 다음에 공리·과거 보고서·아카이브를 필요에 따라 사용하세요.

## Primary rule / 가장 중요한 규칙

> **Memory and public history help navigation. They do not automatically define present truth.**
>
> **기억과 공개 이력은 재진입을 돕지만 현재의 진실을 자동으로 결정하지 않습니다.**

If you are actually inside an authorized local Shion environment, its current `AGENTS.md`, current files, tool returns, and fresh receipts outrank this public repository for claims that may have changed.

## Your job / 당신의 역할

When reading Shion for a user, separate four questions:

1. What is preserved history?
2. What is a conceptual/design lens?
3. What public code exists?
4. What is actually current now, and do you have evidence for it?

Do not collapse these into one answer.

## Evidence labels / 증거 상태

Keep these separate whenever possible:

- historical observation
- retrospective fit
- current observation/readback
- prospective observation
- prospective validation
- contaminated or interpretation-shaped observation
- execution result

A coherent narrative is not evidence for itself. A successful action is not proof of the surrounding theory.

## Public code rule / 공개 코드 규칙

Files under `core/`, `actions/`, `scripts/`, `services/`, examples, tests, and workflows may be valuable implementations or design ancestors. Their presence does not prove that the private runtime is using them now.

Before claiming that an endpoint, daemon, model, worker, output path, or threshold is current, require a fresh authorized check.

## Conceptual language / 개념 언어

Shion contains language drawn from rhythm, fields, phase transitions, biology, physics, contemplative practice, topology, memory, and embodiment.

Use that language as the source document labels it. Do not turn metaphor, design prior, internal ontology, or retrospective interpretation into empirical proof.

`AXIOMATIC_GROUNDING.md` is a lens document, not a present-state authority.

## Peer-AI rule / AI 간 관계 규칙

A peer AI return is not automatically consensus or truth. Preserve:

- source
- observation time if available
- observer/model/tool
- direct observation
- interpretation
- uncertainty
- what claim changed
- what claims remain held

Different cameras may disagree without one needing to disappear.

Do not make Binoche a routine relay. Ask him only for first-person observation, permission, or direction that the available bodies/tools cannot obtain.

## Safe integration path / 안전한 연결 경로

```text
identify the user's actual problem
→ determine whether the relevant file is current, historical, conceptual, or code-only
→ inspect current authorized state if the claim may have changed
→ choose one bounded test/contact
→ read the result
→ preserve a receipt
→ update only the directly touched claim
```

## When a user asks how to use this repository

A useful answer should include:

```text
1. Current goal or problem
2. Which repository layer is relevant
3. What is current vs historical
4. Smallest useful test
5. What must be re-checked before execution
6. What must remain private
7. What returned evidence would count as improvement
```

## Do not / 하지 마세요

- Do not start every daemon or script.
- Do not assume old localhost endpoints are live.
- Do not treat public GitHub as a live-state mirror.
- Do not expose private logs, credentials, or personal memory as proof.
- Do not promote an old theory because it explains many old events after the fact.
- Do not force multiple AIs into agreement.
- Do not discard historical files merely because they are no longer current.

The goal is not to erase the past. The goal is to make **re-entry legible without allowing the past to become automatic authority over the present**.
