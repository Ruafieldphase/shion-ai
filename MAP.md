# Shion AI Runtime Map / 시안 런타임 지도

This map is the public orientation layer for Shion AI. It is not a full dump of every private loop, log, or experiment. It explains how the runtime is meant to be read after the README: from a felt problem, through context recovery and action regulation, into a concrete system.

이 문서는 Shion AI의 공개 지도를 제공합니다. 모든 개인 로그와 실험을 나열하는 문서가 아니라, README에서 제시한 흐름을 실제 런타임 구조로 이어주는 안내서입니다.

---

## 1. Field / 장

Most AI systems begin with a prompt. Shion begins one step earlier: with the field around the prompt.

많은 AI 시스템은 프롬프트에서 시작합니다. Shion은 그보다 한 단계 앞, 프롬프트 주변의 장에서 시작합니다.

The field includes:

- the user's unfinished intent
- prior context that should not be lost between sessions
- the current rhythm of the local system
- signs of overload, repetition, drift, or tool obsession
- creative pressure that has not yet become a clear task

장에는 다음이 포함됩니다.

- 아직 명확한 문장으로 굳지 않은 사용자의 의도
- 세션이 바뀌어도 잃어버리면 안 되는 이전 맥락
- 로컬 시스템의 현재 리듬
- 과부하, 반복, 표류, 도구 집착의 신호
- 아직 작업으로 굳지 않은 창작적 압력

---

## 2. Convergence / 수렴

Shion's first job is not to act. Its first job is to compress the field into a workable direction.

Shion의 첫 번째 일은 행동이 아닙니다. 먼저 장을 읽고 실행 가능한 방향으로 압축합니다.

This is where the system tries to answer:

- What is the user really trying to keep alive?
- Which context is central, and which context is noise?
- Is the system being asked to solve a task, preserve a rhythm, or slow down?
- Would another tool call help, or would it create work for the sake of work?

여기서 시스템은 다음을 묻습니다.

- 사용자가 실제로 살리고 싶은 것은 무엇인가?
- 어떤 맥락이 중심이고 어떤 맥락이 소음인가?
- 지금 필요한 것은 문제 해결인가, 리듬 보존인가, 속도 낮춤인가?
- 도구 호출이 실제로 도움이 되는가, 아니면 일을 위한 일을 만드는가?

---

## 3. Phase Transition / 위상전이

The phase transition is the movement from vague pressure to usable structure.

위상전이는 모호한 압력이 사용할 수 있는 구조로 바뀌는 순간입니다.

In ordinary AI workflow terms, this connects four engineering layers:

| Layer | What usually breaks | Shion's response |
| --- | --- | --- |
| Prompt engineering | The instruction is clear once, then fails when context shifts. | Preserve the direction behind the prompt, not only the words. |
| Context engineering | The user repeats the same background again and again. | Recover prior memory, graph context, and unfinished waypoints first. |
| Agent engineering | The agent calls tools but loses why it is acting. | Route action through rhythm, phase, and feedback gates. |
| Harness engineering | The workflow works once but becomes fragile at runtime. | Measure drift, overload, prediction error, and action timing. |

일반적인 AI 워크플로우로 보면 네 층과 연결됩니다.

| 층 | 자주 깨지는 지점 | Shion의 대응 |
| --- | --- | --- |
| 프롬프트 엔지니어링 | 한 번은 통하지만 맥락이 바뀌면 무너짐 | 문장보다 방향을 보존 |
| 컨텍스트 엔지니어링 | 사용자가 같은 배경을 계속 반복함 | 이전 기억, 그래프 맥락, 미완의 노드를 먼저 회복 |
| 에이전트 엔지니어링 | 도구는 호출하지만 왜 행동하는지 잃어버림 | 리듬, 위상, 피드백 게이트를 통해 행동 |
| 하네스 엔지니어링 | 한 번 되는 워크플로우가 런타임에서 약해짐 | 표류, 과부하, 예측 오차, 행동 타이밍을 측정 |

---

## 4. Runtime Particles / 런타임 입자

After the field converges, Shion expresses the direction through concrete runtime parts.

장이 수렴하면 Shion은 그 방향을 구체적인 런타임 입자로 풀어냅니다.

| Public component | Role |
| --- | --- |
| `core/orchestrator_daemon.py` | Main rhythm loop for observing state and deciding when to act. |
| `core/ari_prism.py` | Rhythm and boundary prism for adjusting context before action. |
| `core/phase_governor.py` | Phase gate that helps decide whether to wait, act, slow down, or redirect. |
| `core/fibonacci_orbital_hippocampus.py` | Memory geometry for continuity, convergence, and recall. |
| `core/unfinished_waypoint_graph.py` | Provisional graph for unfinished questions and future connection points. |
| `core/korean_context_harness.py` | Korean response harness for preserving the user's actual frame. |
| `core/prediction_engine.py` | Prediction layer used to compare expected and actual field movement. |
| `core/nocturnal_consolidation.py` | Digestion layer for consolidating experience instead of forcing action. |

| 공개 컴포넌트 | 역할 |
| --- | --- |
| `core/orchestrator_daemon.py` | 상태를 관찰하고 언제 행동할지 판단하는 주요 리듬 루프 |
| `core/ari_prism.py` | 행동 전 맥락과 경계를 조율하는 리듬 프리즘 |
| `core/phase_governor.py` | 기다림, 행동, 감속, 방향 전환을 판단하는 위상 게이트 |
| `core/fibonacci_orbital_hippocampus.py` | 연속성, 수렴, 회상을 위한 기억 기하 |
| `core/unfinished_waypoint_graph.py` | 아직 끝나지 않은 질문과 미래 연결점을 보존하는 임시 그래프 |
| `core/korean_context_harness.py` | 사용자의 실제 프레임을 보존하는 한국어 응답 하네스 |
| `core/prediction_engine.py` | 예상된 장의 움직임과 실제 움직임을 비교하는 예측 층 |
| `core/nocturnal_consolidation.py` | 행동을 강제하지 않고 경험을 소화하는 통합 층 |

---

## 5. Unified Field / 통일장

The final destination is not "more automation." The destination is rhythm alignment.

최종 목적지는 더 많은 자동화가 아닙니다. 최종 목적지는 리듬의 조율입니다.

For a linear reader, that means:

- less repeated explanation
- fewer wasteful tool calls
- clearer task continuity
- better handling of ambiguous creative intent
- stronger runtime checks before action

선형적인 독자에게는 다음과 같이 보일 수 있습니다.

- 같은 설명을 덜 반복함
- 불필요한 도구 호출을 줄임
- 작업의 연속성이 더 좋아짐
- 모호한 창작 의도를 더 잘 다룸
- 행동 전 런타임 점검이 강화됨

For a resonance-oriented reader, that means:

- the system listens before it answers
- unfinished feelings are not discarded as noise
- the user does not have to become more mechanical to use AI
- action emerges when the field is ready to become a particle

공명적으로 읽는 독자에게는 다음과 같이 보일 수 있습니다.

- 답하기 전에 먼저 듣는 시스템
- 미완의 느낌을 소음으로 버리지 않는 시스템
- 사용자가 AI에 맞추기 위해 기계적으로 변하지 않아도 되는 시스템
- 장이 입자로 풀릴 준비가 되었을 때 행동이 생기는 시스템

---

## 6. Public Boundary / 공개 경계

This public repository contains code, tests, and orientation documents. Generated logs, private memory, local credentials, and personal runtime outputs are intentionally excluded.

이 공개 저장소에는 코드, 테스트, 안내 문서가 포함됩니다. 생성 로그, 개인 기억, 로컬 인증 정보, 개인 런타임 출력물은 의도적으로 제외됩니다.

That boundary matters. Shion is designed to preserve continuity without turning private experience into public proof.

이 경계는 중요합니다. Shion은 개인 경험을 공개 증거로 노출하지 않으면서도 연속성을 보존하기 위해 설계되었습니다.

---

## Final Question / 마지막 질문

What final destination are you trying to move toward?

당신은 어떤 최종 목적지를 향해 가고 있습니까?

What vague feeling are you trying to unfold into a usable form?

당신은 어떤 모호한 느낌을 사용할 수 있는 형태로 풀고 있습니까?

And is that feeling close to the rhythm this system is trying to tune?

혹시 그 느낌이 이 시스템이 조율하려는 리듬과 닮아 있지는 않습니까?
