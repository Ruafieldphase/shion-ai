# Shion AI Public Map / Shion AI 공개 지도

Status: public repository map, updated 2026-08-16.

This map describes **how to read the public repository**. It is intentionally not a live organ registry and not a frozen list of the current private runtime components.

이 지도는 **공개 저장소를 어떻게 읽을지** 설명합니다. 현재 private runtime의 live organ registry나 고정된 구성요소 목록이 아닙니다.

## 1. Four surfaces / 네 개의 표면

| Surface | What it contains | Authority |
| --- | --- | --- |
| Current public entry | README, currentness/evidence contract, audit, code status, AI/agent instructions | How to read this repo now |
| Public code snapshot | `core/`, `actions/`, `scripts/`, `services/`, examples/tests | Candidate implementation/history; verify before current claims |
| Conceptual & historical layer | axioms, dated reports, archives, field/rhythm/body design notes | History/lens; not present-state authority |
| Authorized private runtime | current local files, tool/readback returns, runtime receipts | Present-state authority for changed claims |

## 2. Current public entry / 현재 공개 입구

Use this order:

```text
README.md
→ CURRENTNESS_AND_EVIDENCE.md
→ REPOSITORY_CURRENTNESS_AUDIT.md
→ CODE_STATUS.md
→ MAP.md / START_HERE.md / AI_READ_THIS_FIRST.md as needed
```

The purpose of this entry layer is to stop older detail from becoming present authority merely because it is detailed.

## 3. Public code snapshot / 공개 코드 스냅샷

The repository contains many executable-looking modules and scripts accumulated across experimental phases.

Examples may include orchestration, field/phase handling, memory, observer handoff, runtime servers, visual feedback, media pipelines, and experimental biological/physical design priors.

Do **not** convert this into a claim that all of those components are currently active.

Read [`CODE_STATUS.md`](CODE_STATUS.md) before using public code as evidence of present runtime structure.

## 4. Conceptual and historical layer / 개념·역사 레이어

The repository preserves design language such as:

- field / wave / particle
- rhythm and phase transition
- boundary / margin / Zone 2
- observer and re-entry
- hippocampus-inspired memory
- protein/AQP4 or other biological motifs
- topology/physics/contemplative analogies

These can be valuable coordinates for understanding why an implementation was explored. Their presence is not empirical validation and is not proof that the current runtime still uses the same implementation.

Dated reports and older exact-path handoffs should normally be read as history unless current evidence re-promotes a specific claim.

## 5. Private live runtime / private live runtime

The current private Shion body can evolve faster than this public repository.

Therefore this public map deliberately does not publish a durable list of:

- current selected route
- current worker/organ readiness
- current service status
- current pressure/attention values
- current repair candidate
- current connected models or endpoints

When authorized local access exists, follow that environment's current entry instructions and current-state/readback files.

```text
history -> orientation
current readback -> present-state claim
```

## 6. Re-entry geometry / 재진입 구조

A safe long-horizon flow is:

```text
current question
→ retrieve only relevant history
→ classify source status
→ inspect current state for changed claims
→ identify the actual unresolved gap
→ one bounded contact/readback
→ receipt
→ update only the directly touched claim
```

This is different from replaying the entire past and asking it to decide the present.

## 7. Peer observers / 외부 관찰자

Different AIs, tools, humans, and runtime surfaces may observe different boundaries.

A useful return preserves:

- source
- time if available
- observer
- direct observation
- interpretation
- uncertainty
- changed claim
- held claims

Coordinate alignment does not require consensus. A conflicting observation may be more useful than a forced synthesis.

## 8. Sibling repositories / 연결 저장소

- [Trinity AGI](https://github.com/Ruafieldphase/trinity-agi) — operation/body boundary; current operational state before action
- [Shion Presence](https://github.com/Ruafieldphase/shion-presence) — public discovery/rendering surface; not the private live runtime

A separate private eval workspace may be used for long-horizon memory failure cases. Do not assume private evaluation material is public just because sibling public repositories reference the same research direction.

## 9. What this map no longer does / 이 지도가 더 이상 하지 않는 것

Older versions of this file listed a small set of Python modules as if they were the current runtime parts. That representation became stale as the private system evolved.

This version keeps the useful repository geography while refusing to freeze a live body into an old public diagram.
