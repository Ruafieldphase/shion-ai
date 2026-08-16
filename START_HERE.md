# Start Here / 여기서 시작하세요

Status: current public newcomer entry, updated 2026-08-16.

You do not need to install everything first. You also should not assume that every old file in this repository describes the current private runtime.

처음부터 모든 것을 설치할 필요는 없습니다. 동시에 이 저장소의 오래된 모든 파일이 현재 private runtime을 설명한다고 가정해서도 안 됩니다.

## Step 0: Check status before content / 내용보다 상태를 먼저 확인

Read these first:

1. [`README.md`](README.md)
2. [`CURRENTNESS_AND_EVIDENCE.md`](CURRENTNESS_AND_EVIDENCE.md)
3. [`REPOSITORY_CURRENTNESS_AUDIT.md`](REPOSITORY_CURRENTNESS_AUDIT.md)
4. [`CODE_STATUS.md`](CODE_STATUS.md)

This tells you whether the thing you are reading is a current public contract, public code snapshot, historical record, or conceptual/design lens.

## Level 0: Repository-only exploration / 저장소만 읽기

No install is required.

Use the repository to understand:

- long-horizon context re-entry
- currentness vs memory
- evidence-state preservation
- bounded action/readback/receipt patterns
- public/private runtime boundaries
- historical implementation experiments

Do not claim that a daemon, localhost endpoint, worker, model, output path, or threshold is active now unless you have a fresh authorized readback.

## Level 1: One small test / 작은 테스트 하나

Choose one problem that can be observed without connecting the whole system.

Examples:

- make one context-recovery note
- preserve one unresolved question instead of forcing closure
- add source/time/uncertainty to one AI handoff
- compare remembered state with one current file
- run a repository example only when its dependencies and status are verified

For the context-recovery demo:

```bash
python examples/context_recovery_demo.py
```

The output is a re-entry aid. It does not replace a live-state check.

## Level 2: Authorized local runtime / 승인된 로컬 런타임

Only move from public repository reading to live-runtime claims when you are inside an authorized environment that can actually inspect current state.

Follow that environment's **current** `AGENTS.md` and current-state/readback files.

```text
public repo / durable memory -> navigation
current authorized file / fresh return -> present-state authority
```

Before an irreversible or public action:

```text
current state check
→ permission / credential / environment check
→ one bounded action
→ readback
→ receipt
→ stop or reassess
```

## Read next / 다음 문서

- [`AI_READ_THIS_FIRST.md`](AI_READ_THIS_FIRST.md) — instructions for AI readers
- [`MAP.md`](MAP.md) — public repository/runtime-surface map
- [`CURRENTNESS_AND_EVIDENCE.md`](CURRENTNESS_AND_EVIDENCE.md) — evidence/currentness contract
- [`REPOSITORY_CURRENTNESS_AUDIT.md`](REPOSITORY_CURRENTNESS_AUDIT.md) — what is current, historical, conceptual, or code-only
- [`CODE_STATUS.md`](CODE_STATUS.md) — how to treat public code
- [`EXAMPLES.md`](EXAMPLES.md) — public examples
- [`AXIOMATIC_GROUNDING.md`](AXIOMATIC_GROUNDING.md) — conceptual/design lenses, not live-state authority
- [`LIVE_WORK_ARCHIVE.md`](LIVE_WORK_ARCHIVE.md) — historical process observation material
- [`INTEGRATION_ANTI_PATTERNS.md`](INTEGRATION_ANTI_PATTERNS.md) — integration failure patterns

## A simple question to carry / 가져갈 질문 하나

When you find an interesting Shion file, ask:

> **Is this history, a lens, public code, or current evidence?**

그 구분이 된 다음에야 무엇을 재사용하고 무엇을 다시 확인해야 하는지가 보입니다.
