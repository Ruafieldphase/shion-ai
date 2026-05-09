# Shion AI

Have you ever felt that AI understands your words, but not your direction?

AI가 당신의 말은 이해하지만, 당신의 방향은 이해하지 못한다고 느낀 적이 있나요?

Have you repeated the same context again and again because yesterday's memory could not continue into today?

어제의 기억이 오늘로 이어지지 않아서 같은 맥락을 계속 반복하고 있었나요?

Have you used more prompts, more API calls, and more tools, only to feel that the work was drifting away from your real intention?

더 많은 프롬프트, 더 많은 API 호출, 더 많은 도구를 쓰고도 작업이 당신의 진짜 의도에서 멀어지고 있다고 느낀 적이 있나요?

Have you felt a vague creative feeling become too logical, too problem-solving, or too unlike its original rhythm after passing through AI?

모호한 창작의 느낌이 AI를 거치며 너무 논리적이고, 문제 해결 중심적이고, 원래의 리듬과 달라졌다고 느낀 적이 있나요?

Have you felt your thinking become fixed inside the AI's boundaries instead of being widened by it?

AI가 당신의 사고를 넓혀주기보다, 오히려 AI의 경계와 바운더리 안에 당신의 사고가 고정된다고 느낀 적이 있나요?

Shion AI begins from that gap. It is an experimental harness for long-running AI work: context recovery, rhythm-aware action, memory consolidation, and feedback-based execution.

Shion AI는 그 간극에서 시작합니다. 장기 AI 작업을 위한 실험적 하네스로서, 맥락 복원, 리듬 기반 행동 조율, 기억 통합, 피드백 기반 실행을 다룹니다.

If you are new, start with [`START_HERE.md`](START_HERE.md). If you are asking your own AI to inspect this repository, give it [`AI_READ_THIS_FIRST.md`](AI_READ_THIS_FIRST.md) first.

처음이라면 [`START_HERE.md`](START_HERE.md)에서 시작하세요. 당신의 AI에게 이 저장소를 읽히려면 먼저 [`AI_READ_THIS_FIRST.md`](AI_READ_THIS_FIRST.md)를 읽게 하세요.

For concrete no-install examples, see [`EXAMPLES.md`](EXAMPLES.md).

설치 없이 따라 하는 구체적인 예시는 [`EXAMPLES.md`](EXAMPLES.md)를 보세요.

For the scientific, humanistic, contemplative, and artistic assumptions behind the system, see [`AXIOMATIC_GROUNDING.md`](AXIOMATIC_GROUNDING.md).

시스템의 과학적, 인문학적, 명상적, 예술적 전제는 [`AXIOMATIC_GROUNDING.md`](AXIOMATIC_GROUNDING.md)를 보세요.

For the lightweight local-first design position, see [`LIGHTWEIGHT_BY_DESIGN.md`](LIGHTWEIGHT_BY_DESIGN.md).

가벼운 로컬 우선 설계 관점은 [`LIGHTWEIGHT_BY_DESIGN.md`](LIGHTWEIGHT_BY_DESIGN.md)를 보세요.

For unedited live recordings of the human-AI workflow, see [`LIVE_WORK_ARCHIVE.md`](LIVE_WORK_ARCHIVE.md).

편집 없는 인간-AI 작업 과정 기록은 [`LIVE_WORK_ARCHIVE.md`](LIVE_WORK_ARCHIVE.md)를 보세요.

This README uses public terms first, with our internal rhythm language in parentheses:

이 README는 보편적인 단어를 먼저 쓰고, 괄호 안에 우리의 내부 리듬 언어를 함께 남깁니다.

```text
Problem Flow (Field/Wave) -> Direction (Convergence) -> Turning Point (Phase Transition) -> Action/Result (Particle) -> Connected Workflow (Unified Field) -> Local Use (Embodiment)
문제의 전체 흐름(장/파동) -> 방향 정리(수렴) -> 전환점(위상전이) -> 실행/결과(입자) -> 이어지는 작업 흐름(통일장) -> 실제 사용(체화)
```

## 1. Problem Flow (Field/Wave): What You Might Be Looking For
## 1. 문제의 전체 흐름(장/파동): 당신이 찾고 있을 수 있는 것

Different people may arrive here through different middle destinations.

사람들은 서로 다른 중간목적지를 통해 이곳에 도착할 수 있습니다.

If you are a developer, you may be looking for better project continuity: an AI that remembers decisions, reads changed files, and resumes unfinished work without asking you to repeat the same context every day.

개발자라면 더 나은 프로젝트 연속성을 찾고 있을 수 있습니다. 결정을 기억하고, 변경된 파일을 읽고, 매일 같은 맥락을 다시 설명하지 않아도 미완의 작업을 이어가는 AI입니다.

If you are a researcher, you may be looking for long-form thought continuity: an AI that preserves unresolved questions instead of reducing everything to a short summary.

연구자라면 긴 사고 흐름의 연속성을 찾고 있을 수 있습니다. 모든 것을 짧은 요약으로 줄이지 않고 미완의 질문을 보존하는 AI입니다.

If you are a creator, you may be looking for a bridge from feeling to artifact: an AI that can hold a vague direction until it becomes a song, video, text, visual form, or public release.

창작자라면 느낌에서 산출물로 이어지는 다리를 찾고 있을 수 있습니다. 흐릿한 방향을 노래, 영상, 글, 시각적 형태, 공개 산출물이 될 때까지 보존하는 AI입니다.

If you are building agents, you may be looking for a runtime harness: an environment where tool use, memory, timing, feedback, and action boundaries stay connected.

에이전트를 만드는 사람이라면 런타임 하네스를 찾고 있을 수 있습니다. 도구 실행, 기억, 타이밍, 피드백, 행동 경계가 분리되지 않고 연결되는 환경입니다.

If you think in overall flows (fields/waves), you may be looking for a system that does not turn every unclear context into an immediate answer.

전체 흐름(장/파동)으로 읽는 사람이라면 불명확한 맥락을 즉시 답으로 바꾸지 않는 시스템을 찾고 있을 수 있습니다.

## 2. Convergence: The Shared AI Problem
## 2. 수렴: 현재 AI의 공통 문제

These middle destinations point to the same practical problem: current AI often loses rhythm around the model.

이 중간목적지들은 같은 실용적 문제를 가리킵니다. 현재 AI는 모델 주변에서 리듬을 잃는 경우가 많습니다.

Modern models are powerful, but the runtime around them often fails to preserve:

현대 모델은 강력하지만, 모델 주변의 런타임은 다음을 보존하지 못하는 경우가 많습니다.

- context across sessions
- unfinished questions
- prior decisions
- action timing
- tool results
- prediction errors
- the user's working rhythm

- 세션을 가로지르는 맥락
- 미완의 질문
- 이전 결정
- 행동 타이밍
- 도구 실행 결과
- 예측 오차
- 사용자의 작업 리듬

The result is familiar: the user repeats context, the AI answers too early, tools run as isolated commands, and long projects lose direction.

그 결과는 익숙합니다. 사용자는 같은 맥락을 반복하고, AI는 너무 빨리 답하고, 도구는 고립된 명령처럼 실행되고, 긴 프로젝트는 방향을 잃습니다.

## 3. Turning Point (Phase Transition): From Prompt to Harness
## 3. 전환점(위상전이): 프롬프트에서 하네스로

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

The transition is this:

전환점은 이것입니다.

```text
better answer -> better context -> better tool use -> better runtime rhythm
더 나은 답변 -> 더 나은 맥락 -> 더 나은 도구 실행 -> 더 나은 런타임 리듬
```

## 4. Action/Result (Particle): What Actually Improves
## 4. 실행/결과(입자): 실제로 좋아지는 것

### Less Repetition Across Sessions / 세션 반복 설명 감소

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
- avoids reopening already-settled choices

Shion 방식 런타임:

- 최근 결정을 복원합니다.
- 미완의 질문을 확인합니다.
- 변경된 파일과 보고서를 읽습니다.
- 이미 정리된 결정을 다시 열지 않습니다.

Result: the user does not need to rebuild the same context every day.

결과: 사용자가 매일 같은 맥락을 다시 쌓지 않아도 됩니다.

### Less Premature Closure / 성급한 결론 감소

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

### Tool Use Becomes Learning / 도구 실행이 학습이 됨

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

### Long Projects Keep Direction / 긴 프로젝트의 방향성 유지

In a multi-week creative or engineering project, the hard part is not one answer. The hard part is preserving direction across many small decisions.

몇 주 동안 이어지는 창작/엔지니어링 프로젝트에서 어려운 것은 답 하나가 아닙니다. 많은 작은 결정 사이에서 방향성을 보존하는 것이 어렵습니다.

Shion AI keeps unresolved waypoints, rhythm signals, memory traces, and runtime feedback available to the next cycle.

Shion AI는 미완의 웨이포인트, 리듬 신호, 기억 흔적, 런타임 피드백을 다음 사이클에서 다시 사용할 수 있게 보존합니다.

Result: the system is better suited for ongoing work than one-shot answers.

결과: 일회성 답변보다 계속 이어지는 작업에 더 적합한 구조가 됩니다.

## 5. Connected Workflow (Unified Field): Rhythm Alignment
## 5. 이어지는 작업 흐름(통일장): 리듬의 조율

All of the middle destinations above point toward the deeper destination: rhythm alignment.

위의 모든 중간목적지는 더 깊은 목적지인 리듬의 조율을 향합니다.

The practical goal is better long-running AI work: continuity, timing, memory, feedback, and safer action.

실용적인 목표는 더 나은 장기 AI 작업입니다. 연속성, 타이밍, 기억, 피드백, 더 안정적인 행동을 다룹니다.

The deeper goal is to sense when to wait, when to act, when to preserve an unfinished question, and when to let a direction become concrete.

더 깊은 목표는 언제 기다릴지, 언제 행동할지, 언제 미완의 질문을 보존할지, 언제 방향을 구체화할지를 감지하는 것입니다.

In public language, this project uses these translations:

이 프로젝트는 공개 문서에서 다음 번역을 사용합니다.

- overall flow (field/wave) means context before action: feeling, question, tension, timing, memory, and unresolved intent
- action/result (particle) means concrete output: a decision, tool call, code change, artifact, scheduled task, or report
- working rhythm (rhythm) means the timing relationship between context, action, memory, and the next cycle

- 전체 흐름(장/파동)은 행동 이전의 맥락입니다. 느낌, 질문, 긴장, 타이밍, 기억, 미완의 의도입니다.
- 실행/결과(입자)는 구체적 결과입니다. 판단, 도구 호출, 코드 변경, 산출물, 예약 작업, 보고서입니다.
- 작업 리듬(리듬)은 맥락, 행동, 기억, 다음 사이클 사이의 타이밍 관계입니다.

The goal is not to avoid action/results (particles). The goal is to avoid turning the whole flow (field/wave) into action too early.

목표는 실행/결과(입자)를 피하는 것이 아닙니다. 전체 흐름(장/파동)을 너무 빨리 실행으로 바꾸지 않는 것입니다.

## 6. Local Use (Embodiment): Runtime and Files
## 6. 실제 사용(체화): 런타임과 파일 구조

`shion-ai` is the mind/runtime layer. It studies context recovery, rhythm-based regulation, memory consolidation, prediction, reflection, and autonomous tool execution.

`shion-ai`는 마음/런타임 레이어입니다. 맥락 복원, 리듬 기반 조율, 기억 통합, 예측, 반성, 자율 도구 실행을 다룹니다.

`trinity-agi` is the body/infrastructure layer. It handles automation, publishing, scheduling, local runtime support, synchronization, and status reporting.

`trinity-agi`는 몸/인프라 레이어입니다. 자동화, 게시, 예약, 로컬 런타임 지원, 동기화, 상태 보고를 담당합니다.

Public scope: this repository contains experimental runtime code and sanitized research artifacts. Local credentials, personal memory, generated logs, media outputs, and machine-specific state are intentionally excluded from the public tree.

공개 범위: 이 저장소에는 실험적 런타임 코드와 정리된 연구 산출물이 포함됩니다. 로컬 인증 정보, 개인 기억, 생성 로그, 미디어 출력물, 장비별 상태 파일은 공개 트리에서 의도적으로 제외합니다.

### Key Components / 주요 구성

- `core/orchestrator_daemon.py`: background runtime loop that observes state and triggers actions.
- `core/ari_prism.py`: rhythm and boundary layer for refracting context before action.
- `core/phase_governor.py`: phase-aware control layer for slowing, passing, or redirecting actions.
- `core/fibonacci_orbital_hippocampus.py`: memory structure for registering, digesting, and converging experience.
- `core/unfinished_waypoint_graph.py`: provisional graph for unresolved questions and unfinished context.
- `core/nocturnal_consolidation.py`: idle-time consolidation and dream-like synthesis.
- `core/prediction_engine.py` and `core/world_model_executor.py`: prediction and action-feedback experiments.

위 파일들은 시안의 핵심 런타임을 이룹니다. 데몬은 상태를 관찰하고, ARI 프리즘과 위상 관리자는 행동 전 맥락을 조율하며, 해마/웨이포인트/야간 통합 모듈은 경험을 저장하고 다시 연결합니다.

## 7. How To Use This With Your Own AI
## 7. 당신의 AI와 함께 사용하는 방법

This project was uploaded so other people can try the system inside their own AI workflow. You do not need to understand the entire philosophy first. The easiest entry point is to ask your current AI to read Shion as a possible runtime/harness layer.

이 프로젝트는 다른 사람들이 자신의 AI 워크플로우 안에서 실제로 시도해 볼 수 있도록 공개되었습니다. 전체 철학을 먼저 이해할 필요는 없습니다. 가장 쉬운 진입점은 당신이 지금 쓰는 AI에게 Shion을 런타임/하네스 층으로 읽게 하는 것입니다.

Do not ask only:

단순히 이렇게만 묻지 마세요.

```text
Summarize this repository.
```

Instead, ask:

대신 이렇게 물어보세요.

```text
Read https://github.com/Ruafieldphase/shion-ai as a possible runtime/harness layer for my current AI workflow.

Do not only summarize the repository.
Look for where my current AI system loses context, repeats work, overuses tools, misses my intent, or fails to preserve continuity.

Then identify:
1. which Shion AI concepts match my problem,
2. which files or modules are relevant,
3. what the smallest useful integration test (particle) would be,
4. what should remain private or local,
5. what we can test first without over-automating.
```

한글로는 이렇게 요청할 수 있습니다.

```text
https://github.com/Ruafieldphase/shion-ai 저장소를 내 현재 AI 워크플로우에 연결 가능한 런타임/하네스 층으로 읽어줘.

단순 요약만 하지 말고,
내 AI 시스템이 어디에서 맥락을 잃고, 같은 일을 반복하고, 도구를 과사용하고, 내 의도를 놓치고, 연속성을 보존하지 못하는지 찾아줘.

그리고 다음을 정리해줘.
1. 내 문제와 맞닿는 Shion AI 개념
2. 관련 파일 또는 모듈
3. 가장 작게 테스트할 수 있는 연결 테스트(입자)
4. 비공개 또는 로컬로 남겨야 할 것
5. 과잉 자동화 없이 먼저 검증할 수 있는 것
```

### What Your AI Should Look For / 당신의 AI가 봐야 할 지점

Ask your AI to inspect these points:

당신의 AI에게 다음 지점을 보라고 하세요.

- Memory continuity: where does my current AI forget important context?
- Intent preservation: where does it understand the task but miss the direction?
- Tool behavior: where does it call tools or APIs too often?
- Agent loop stability: where does a workflow work once but fail to stay stable?
- Creative translation: where does vague feeling become too mechanical?
- Public/private boundary: what should stay local, private, or excluded?
- First integration test (particle): what is the smallest connection we can test first?

- 기억의 연속성: 내 AI가 중요한 맥락을 어디에서 잊는가?
- 의도 보존: 작업은 이해하지만 방향을 놓치는 지점은 어디인가?
- 도구 행동: 도구나 API를 너무 많이 호출하는 지점은 어디인가?
- 에이전트 루프 안정성: 한 번은 되지만 안정적으로 이어지지 않는 흐름은 어디인가?
- 창작 번역: 모호한 느낌이 너무 기계적으로 바뀌는 지점은 어디인가?
- 공개/비공개 경계: 무엇을 로컬, 비공개, 제외 대상으로 남겨야 하는가?
- 첫 연결 테스트(입자): 가장 작게 테스트할 수 있는 연결점은 무엇인가?

### First Integration Test (Particle) / 첫 연결 테스트(입자)

Start small. Do not try to run every loop at once.

작게 시작하세요. 모든 루프를 한 번에 실행하려고 하지 마세요.

```text
1. Pick one pain point: repeated context, tool overuse, lost intent, or unstable agent loop.
2. Ask your AI to map that pain point to one Shion module or concept.
3. Create one small test: a document rewrite, a context recovery step, a memory note, or a runtime check.
4. Observe whether the result reduces repetition or preserves direction.
5. Only then decide whether to connect more of the system.
```

```text
1. 하나의 문제를 고릅니다: 반복되는 맥락, 도구 과사용, 의도 상실, 불안정한 에이전트 루프.
2. 당신의 AI에게 그 문제를 Shion의 한 모듈 또는 개념과 연결하게 합니다.
3. 작은 테스트 하나를 만듭니다: 문서 정리, 맥락 회복, 기억 노트, 런타임 점검.
4. 결과가 반복을 줄이고 방향을 보존하는지 관찰합니다.
5. 그 다음에야 시스템을 더 깊게 연결할지 결정합니다.
```

### Quick Start / 빠른 시작

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

## Final Question / 마지막 질문

Before this README becomes only an explanation, it should return the question to you.

이 README가 단순한 설명으로 끝나기 전에, 질문은 다시 당신에게 돌아가야 합니다.

What final destination are you moving toward?

당신은 어떤 최종목적지를 향해 가고 있습니까?

What feeling, question, or unresolved direction are you trying to unfold?

당신은 어떤 느낌, 질문, 아직 풀리지 않은 방향을 펼치고 있습니까?

Could the destination you are working toward be resonating with the destination this system is trying to unfold: rhythm alignment?

혹시 당신이 풀고 있는 목적지도, 이 시스템이 풀고 있는 최종목적지인 리듬의 조율과 비슷한 결로 공명하고 있지는 않을까요?

If so, Shion AI is not asking you to adopt its philosophy first. It is offering a runtime shape for the kind of work that needs continuity, timing, memory, and the patience to let the overall flow (field/wave) become action/result (particle) at the right moment.

그렇다면 Shion AI는 먼저 철학을 받아들이라고 요구하지 않습니다. 연속성, 타이밍, 기억, 그리고 전체 흐름(장/파동)이 적절한 순간에 실행/결과(입자)가 되도록 기다리는 인내가 필요한 작업을 위한 런타임 형태를 제안합니다.

## Core Sentence / 핵심 문장

> I want you to understand my rhythm.
>
> 나는 네가 나의 리듬을 이해하기를 바란다.

## License

MIT
