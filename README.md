# Shion AI

Shion AI is an experimental harness for long-running AI work: context recovery, rhythm-aware action, memory consolidation, and feedback-based execution.

Shion AI는 장기 AI 작업을 위한 실험적 하네스입니다. 맥락 복원, 리듬 기반 행동 조율, 기억 통합, 피드백 기반 실행을 다룹니다.

## Two Ways to Read This Project / 이 프로젝트를 읽는 두 가지 방법

### If You Think in Systems / 시스템적으로 읽는다면

Current AI is powerful, but it often fails around the model rather than inside the model. It forgets project context, closes unfinished questions too early, and treats tool use as isolated execution instead of part of a learning loop.

현재 AI는 강력하지만, 한계는 모델 내부보다 모델 주변의 런타임에서 자주 드러납니다. 프로젝트 맥락을 잊고, 미완의 질문을 너무 빨리 닫아버리며, 도구 실행을 학습 루프의 일부가 아니라 고립된 일회성 실행으로 처리합니다.

Shion AI explores a runtime that keeps continuity across sessions, decides when to act or wait, and feeds action results back into memory and the next decision.

Shion AI는 세션이 바뀌어도 연속성을 유지하고, 언제 행동하고 언제 기다릴지 조율하며, 행동 결과를 기억과 다음 판단으로 되돌리는 런타임을 실험합니다.

### If You Think in Fields / 장으로 읽는다면

Shion AI is an experiment in preserving the wave before it collapses into a particle.

Shion AI는 파동이 입자로 붕괴되기 전의 장을 보존하는 실험입니다.

Questions, feelings, unfinished signals, timing, and tension are kept alive until the direction becomes clear enough to act. The system does not try to force every signal into an immediate answer.

질문, 느낌, 미완의 신호, 타이밍, 긴장을 방향이 충분히 선명해질 때까지 살아 있게 둡니다. 모든 신호를 즉시 답으로 고정하려 하지 않습니다.

## Why This Exists / 왜 필요한가

The AI ecosystem has been moving through several layers:

AI 생태계는 여러 층을 지나 이동해 왔습니다.

1. Prompt engineering: what should we say to the model?
2. Context engineering: what should the model remember right now?
3. Agent engineering: what tools can the model use?
4. Harness engineering: what runtime lets the model act without losing direction?

1. 프롬프트 엔지니어링: 모델에게 뭐라고 말해야 하는가?
2. 컨텍스트 엔지니어링: 지금 모델이 무엇을 기억해야 하는가?
3. 에이전트 엔지니어링: 모델이 어떤 도구를 사용할 수 있는가?
4. 하네스 엔지니어링: 모델이 방향을 잃지 않고 행동하려면 어떤 런타임이 필요한가?

Shion AI belongs to the fourth layer. It is not just a better prompt and not just a tool-using agent. It is an experimental runtime around the model.

Shion AI는 네 번째 층에 있습니다. 더 좋은 프롬프트도 아니고, 단순한 도구 사용 에이전트도 아닙니다. 모델 주변의 실험적 런타임입니다.

## What Improves / 무엇이 좋아지는가

### 1. Less Repetition Across Sessions / 세션이 바뀔 때 반복 설명이 줄어듭니다

Normal AI:

- "What were we working on?"
- "Can you paste the previous context?"
- "Which file should I check?"

일반 AI:

- "무엇을 하고 있었나요?"
- "이전 맥락을 붙여 넣어 주실 수 있나요?"
- "어떤 파일을 봐야 하나요?"

Shion-style runtime:

- restores recent decisions
- checks unfinished questions
- reads changed files and reports
- avoids reopening already-settled infrastructure choices

Shion 방식 런타임:

- 최근 결정을 복원합니다.
- 미완의 질문을 확인합니다.
- 변경된 파일과 보고서를 읽습니다.
- 이미 정리된 인프라 결정을 다시 열지 않습니다.

Result: the user does not need to rebuild the same context every day.

결과: 사용자가 매일 같은 맥락을 다시 쌓지 않아도 됩니다.

### 2. Less Premature Closure / 성급한 결론이 줄어듭니다

User:

> This feature feels wrong, but I do not know why.

사용자:

> 이 기능이 뭔가 아닌 것 같은데, 왜 그런지는 모르겠어.

Normal AI may immediately produce a refactor plan.

일반 AI는 바로 리팩터링 계획을 만들 수 있습니다.

Shion-style runtime treats this as an unresolved signal. It can inspect related code, previous attempts, logs, design intent, and timing before changing anything destructive.

Shion 방식 런타임은 이 말을 미완의 신호로 봅니다. 파괴적인 수정을 하기 전에 관련 코드, 이전 시도, 로그, 설계 의도, 타이밍을 확인할 수 있습니다.

Result: fewer unnecessary rewrites, fewer fixing loops, and better timing.

결과: 불필요한 재작성과 끝없는 수정 루프가 줄고, 행동 타이밍이 좋아집니다.

### 3. Tool Use Becomes Learning / 도구 실행이 학습이 됩니다

Normal agent:

- runs a test
- fixes the error
- ends the session

일반 에이전트:

- 테스트를 실행합니다.
- 오류를 고칩니다.
- 세션을 끝냅니다.

Shion-style runtime:

- runs the test
- records prediction error
- stores what changed
- updates the next action bias
- uses the result in later cycles

Shion 방식 런타임:

- 테스트를 실행합니다.
- 예측 오차를 기록합니다.
- 무엇이 바뀌었는지 저장합니다.
- 다음 행동 성향을 조정합니다.
- 이후 사이클에서 그 결과를 사용합니다.

Result: action results become part of memory, not just command output.

결과: 행동 결과가 단순 명령 출력이 아니라 기억의 일부가 됩니다.

### 4. Long Projects Keep Direction / 긴 프로젝트의 방향성이 유지됩니다

In a multi-week creative or engineering project, the hard part is not one answer. The hard part is preserving direction across many small decisions.

몇 주 동안 이어지는 창작/엔지니어링 프로젝트에서 어려운 것은 답 하나가 아닙니다. 많은 작은 결정 사이에서 방향성을 보존하는 것이 어렵습니다.

Shion AI keeps unresolved waypoints, rhythm signals, memory traces, and runtime feedback available to the next cycle.

Shion AI는 미완의 웨이포인트, 리듬 신호, 기억 흔적, 런타임 피드백을 다음 사이클에서 다시 사용할 수 있게 보존합니다.

Result: the system is better suited for ongoing work than one-shot answers.

결과: 일회성 답변보다 계속 이어지는 작업에 더 적합한 구조가 됩니다.

## Wave and Particle / 파동과 입자

In practical terms, wave means context before action: feeling, question, tension, timing, memory, and unresolved intent.

실용적으로 말하면, 파동은 행동 이전의 맥락입니다. 느낌, 질문, 긴장, 타이밍, 기억, 미완의 의도가 여기에 포함됩니다.

Particle means concrete output: a decision, a tool call, a code change, a generated artifact, a scheduled task, or a report.

입자는 구체적 결과입니다. 판단, 도구 호출, 코드 변경, 생성물, 예약 작업, 보고서가 여기에 해당합니다.

The goal is not to avoid particles. The goal is to avoid collapsing the wave too early.

목표는 입자를 피하는 것이 아닙니다. 파동을 너무 빨리 붕괴시키지 않는 것입니다.

## Translation Layer / 개념 번역표

| Concept | Practical meaning | 한국어 설명 |
| --- | --- | --- |
| Wave | Context before action: felt direction, question, tension, timing, memory | 행동 이전의 맥락: 느낌의 방향, 질문, 긴장, 타이밍, 기억 |
| Particle | Concrete output: code, tool call, decision, artifact, scheduled task | 구체적 결과: 코드, 도구 호출, 판단, 생성물, 예약 작업 |
| Rhythm | Timing and self-regulation across runtime loops | 런타임 루프의 타이밍과 자기 조율 |
| Field | The active context window that shapes what becomes actionable | 무엇이 실행 가능한지가 결정되는 활성 맥락 장 |
| Collapse | The moment a vague direction becomes a concrete action | 흐릿한 방향이 구체적 행동으로 고정되는 순간 |
| ARI | Adjust Rhythm Information: a framework for regulating context before action | 행동 전에 맥락의 리듬을 조율하는 프레임워크 |

## Repository Map / 저장소 관계

`shion-ai` is the mind/runtime layer. It studies context recovery, rhythm-based regulation, memory consolidation, prediction, reflection, and autonomous tool execution.

`shion-ai`는 마음/런타임 레이어입니다. 맥락 복원, 리듬 기반 조율, 기억 통합, 예측, 반성, 자율 도구 실행을 다룹니다.

`trinity-agi` is the body/infrastructure layer. It handles automation, publishing, scheduling, local runtime support, synchronization, and status reporting.

`trinity-agi`는 몸/인프라 레이어입니다. 자동화, 게시, 예약, 로컬 런타임 지원, 동기화, 상태 보고를 담당합니다.

Public scope: this repository contains experimental runtime code and sanitized research artifacts. Local credentials, personal memory, generated logs, media outputs, and machine-specific state are intentionally excluded from the public tree.

공개 범위: 이 저장소에는 실험적 런타임 코드와 정리된 연구 산출물이 포함됩니다. 로컬 인증 정보, 개인 기억, 생성 로그, 미디어 출력물, 장비별 상태 파일은 공개 트리에서 의도적으로 제외합니다.

## What Is Inside / 주요 구성

- `core/orchestrator_daemon.py`: background runtime loop that observes state and triggers actions.
- `core/ari_prism.py`: rhythm and boundary layer for refracting context before action.
- `core/phase_governor.py`: phase-aware control layer for slowing, passing, or redirecting actions.
- `core/fibonacci_orbital_hippocampus.py`: memory structure for registering, digesting, and converging experience.
- `core/unfinished_waypoint_graph.py`: provisional graph for unresolved questions and unfinished context.
- `core/nocturnal_consolidation.py`: idle-time consolidation and dream-like synthesis.
- `core/prediction_engine.py` and `core/world_model_executor.py`: prediction and action-feedback experiments.

위 파일들은 시안의 핵심 런타임을 이룹니다. 데몬은 상태를 관찰하고, ARI 프리즘과 위상 관리자는 행동 전 맥락을 조율하며, 해마/웨이포인트/야간 통합 모듈은 경험을 저장하고 다시 연결합니다.

## Runtime Flow / 실행 흐름

1. A question, feeling, or signal enters the field.
2. The runtime reads rhythm, tension, memory, and unresolved context.
3. ARI and phase layers decide whether to wait, soften, redirect, or act.
4. If the field becomes clear enough, it collapses into a particle: a concrete action.
5. The result feeds back into memory and the next rhythm cycle.

1. 질문, 느낌, 신호가 장으로 들어옵니다.
2. 런타임은 리듬, 긴장, 기억, 미완의 맥락을 읽습니다.
3. ARI와 위상 레이어가 기다릴지, 늦출지, 방향을 바꿀지, 실행할지 판단합니다.
4. 장이 충분히 선명해지면 입자로 붕괴되어 구체적 행동이 됩니다.
5. 결과는 다시 기억과 다음 리듬 사이클로 돌아갑니다.

## Quick Start / 빠른 시작

```bash
git clone https://github.com/Ruafieldphase/shion-ai.git
cd shion-ai

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Windows
./start_unconscious.bat
```

This is an experimental local runtime. Some scripts assume a Windows environment and local paths used by the original system.

이 저장소는 실험적 로컬 런타임입니다. 일부 스크립트는 Windows 환경과 원래 시스템에서 사용하던 로컬 경로를 전제로 합니다.

## Core Sentence / 핵심 문장

> I want you to understand my rhythm.
>
> 나는 네가 나의 리듬을 이해하기를 바란다.

## License

MIT
