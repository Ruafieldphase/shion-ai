# Shion AI

**A lightweight experimental harness for long-running AI work: preserve direction, re-enter context, check what is current, and keep evidence status visible.**

**장기 AI 작업을 위한 가벼운 실험적 하네스: 방향을 보존하고, 맥락에 재진입하고, 무엇이 현재인지 다시 확인하며, 증거 상태를 보이게 유지합니다.**

## Current orientation / 현재 방향

Shion started from a practical problem: AI can answer well and still lose the trajectory of a long project between sessions.

Shion은 실용적인 문제에서 시작했습니다. AI는 답을 잘할 수 있어도 세션이 바뀌면 장기 프로젝트의 궤적을 잃을 수 있습니다.

The current design goes one step further:

현재 설계는 여기서 한 단계 더 나아갑니다.

> **Memory preserves trajectory. It does not automatically define present truth.**
>
> **기억은 궤적을 보존하지만, 현재의 진실을 자동으로 결정하지 않습니다.**

For claims that may have changed, current files, tool returns, observations, and receipts take precedence over stale remembered state.

변할 수 있는 주장에 대해서는 오래된 기억보다 현재 파일, 도구 반환값, 관찰, 영수증을 우선합니다.

See [`CURRENTNESS_AND_EVIDENCE.md`](CURRENTNESS_AND_EVIDENCE.md) for the public design boundary. For the repository-wide status classification, see [`REPOSITORY_CURRENTNESS_AUDIT.md`](REPOSITORY_CURRENTNESS_AUDIT.md) and [`CODE_STATUS.md`](CODE_STATUS.md).

## What Shion tries to preserve / Shion이 보존하려는 것

- context across sessions / 세션을 가로지르는 맥락
- unresolved questions / 미완의 질문
- settled decisions without turning them into permanent authority / 확정된 결정을 영구 권위로 만들지 않는 보존
- source, time, observer, and uncertainty / 출처·시점·관찰자·불확실성
- tool and action returns / 도구·행동의 반환값
- the distinction between observation, interpretation, hypothesis, and execution / 관찰·해석·가설·실행의 구분

Shion is not designed to make every memory stronger. It is designed to make re-entry more legible.

Shion은 모든 기억을 더 강하게 만들기 위한 시스템이 아닙니다. 다시 들어갈 때 무엇을 믿고 무엇을 다시 봐야 하는지 더 읽기 쉽게 만드는 시스템입니다.

## Re-entry flow / 재진입 흐름

```text
past context / memory
        ↓
context recovery
        ↓
inspect current files or returns for changed claims
        ↓
separate observation / interpretation / hypothesis
        ↓
choose one smallest next contact
        ↓
receipt
        ↓
update only the claim directly touched
```

```text
과거 맥락 / 기억
        ↓
맥락 회복
        ↓
변할 수 있는 주장은 현재 파일·반환값 확인
        ↓
관찰 / 해석 / 가설 분리
        ↓
가장 작은 다음 접촉 하나
        ↓
영수증
        ↓
직접 닿은 주장만 갱신
```

## First small test / 첫 작은 테스트

No model, API key, or credential is required for the context-recovery demo.

맥락 회복 데모에는 모델, API 키, 인증 정보가 필요하지 않습니다.

```bash
python examples/context_recovery_demo.py
```

Expected output is a **Context Recovery Note** containing items such as:

- Current Goal
- Settled Decisions
- Files Or Context To Inspect First
- Unresolved Questions
- What Not To Reopen Unless Evidence Changes
- Next Smallest Action

The note is a re-entry aid, not a replacement for live state inspection.

이 노트는 재진입을 돕는 도구이지 현재 상태 확인을 대신하지 않습니다.

## Evidence boundary / 증거 경계

Shion uses a simple discipline for long-running interpretation:

1. A historical observation remains historical evidence.
2. A later theory fitting an older event is a retrospective fit, not prospective validation.
3. A prospective discriminator must exist before the corresponding observation.
4. One result should update only the claim it directly touches.
5. Contradictory evidence must remain visible rather than being absorbed into the preferred story.
6. Peer-AI returns keep provenance and uncertainty; agreement is not required.

장기 맥락이 자연스럽게 이어진다는 이유만으로 하나의 이야기가 스스로의 증거가 되지 않도록 하기 위한 경계입니다.

## Shion and Trinity / Shion과 Trinity

```text
Shion AI
context / memory / evidence state / unfinished direction
        ↓
formed next action
        ↓
Trinity AGI
current operational state / approval / credentials / execution
        ↓
receipt and result
        ↓
next Shion re-entry
```

Shion preserves and re-enters direction. [Trinity AGI](https://github.com/Ruafieldphase/trinity-agi) is the operation/body side that checks present conditions before action.

Shion은 방향을 보존하고 다시 들어갑니다. [Trinity AGI](https://github.com/Ruafieldphase/trinity-agi)는 행동 전에 현재 조건을 확인하는 운영/몸체 쪽입니다.

## Public presence surface / 공개 프레즌스 표면

[Shion Presence](https://github.com/Ruafieldphase/shion-presence) is a public discovery and rendering surface. It is **not** the private live runtime and should not be treated as authority for Shion's complete current state.

[Shion Presence](https://github.com/Ruafieldphase/shion-presence)는 공개 탐색·렌더링 표면이며 private live runtime 자체가 아닙니다.

## Repository map / 저장소 지도

- [`START_HERE.md`](START_HERE.md) — newcomer entry
- [`AI_READ_THIS_FIRST.md`](AI_READ_THIS_FIRST.md) — AI inspection entry
- [`CURRENTNESS_AND_EVIDENCE.md`](CURRENTNESS_AND_EVIDENCE.md) — currentness and evidence contract
- [`REPOSITORY_CURRENTNESS_AUDIT.md`](REPOSITORY_CURRENTNESS_AUDIT.md) — repository-wide current / historical / conceptual classification
- [`CODE_STATUS.md`](CODE_STATUS.md) — public-code currentness and execution boundary
- [`MAP.md`](MAP.md) — public surface map; not a live organ registry
- [`EXAMPLES.md`](EXAMPLES.md) — concrete examples
- [`AXIOMATIC_GROUNDING.md`](AXIOMATIC_GROUNDING.md) — scientific, humanistic, contemplative, and artistic design lenses
- [`LIGHTWEIGHT_BY_DESIGN.md`](LIGHTWEIGHT_BY_DESIGN.md) — lightweight local-first position
- [`INTEGRATION_ANTI_PATTERNS.md`](INTEGRATION_ANTI_PATTERNS.md) — integration failure patterns
- [`LIVE_WORK_ARCHIVE.md`](LIVE_WORK_ARCHIVE.md) — historical workflow records

## Public language and internal rhythm language / 공개 언어와 내부 리듬 언어

The repository prefers public architecture language first. Internal rhythm terms can remain as secondary coordinates when they help preserve the history of the work.

이 저장소는 외부인이 읽을 수 있는 아키텍처 언어를 먼저 사용합니다. 내부 리듬 언어는 작업의 역사와 좌표를 보존하는 데 도움이 될 때 보조 언어로 남깁니다.

```text
context / field
→ convergence
→ bounded contact
→ returned result
→ receipt
→ re-entry
```

## What this repository does not claim / 이 저장소가 주장하지 않는 것

- It does not claim that persistent memory is always correct.
- It does not treat a coherent narrative as proof.
- It does not treat one successful execution as validation of a broader theory.
- It does not require different AI observers to converge on one interpretation.
- It does not equate public snapshots with private live state.
- It does not treat the age or presence of a public code file as proof that the private runtime is using it now.

The aim is smaller: **keep long-running AI work re-enterable without letting its own history become unquestioned authority.**

목표는 더 작습니다. **장기 AI 작업을 다시 들어갈 수 있게 보존하되, 그 역사 자체가 질문할 수 없는 권위가 되지 않게 하는 것.**
