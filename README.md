# Shion AI

> What if an AI system did not begin from commands, but from rhythm, tension, unfinished questions, and felt direction?
>
> 만약 AI 시스템이 명령에서 시작하지 않고, 리듬, 긴장, 미완의 질문, 그리고 먼저 느껴지는 방향에서 시작한다면 어떻게 될까?

Shion AI is an experimental autonomous AI runtime built around that question. It treats context as a moving field first, and turns that field into executable actions only when the direction becomes clear enough.

Shion AI는 그 질문을 중심으로 만든 실험적 자율 AI 런타임입니다. 이 시스템은 맥락을 먼저 움직이는 장(field)으로 보고, 방향이 충분히 선명해졌을 때만 그것을 실행 가능한 행동으로 바꿉니다.

## Compressed Destination / 압축된 목적지

This repository explores the transition from wave to particle in an AI runtime.

이 저장소는 AI 런타임 안에서 파동이 입자로 전환되는 과정을 실험합니다.

In this project, a wave is the pre-verbal flow of context: questions, sensations, timing, memory, tension, and unresolved intent. A particle is the concrete output that appears after that flow collapses: a decision, a tool call, a generated artifact, a scheduled task, or a line of code.

이 프로젝트에서 파동은 말로 고정되기 전의 맥락 흐름입니다. 질문, 감각, 타이밍, 기억, 긴장, 아직 끝나지 않은 의도가 여기에 포함됩니다. 입자는 그 흐름이 붕괴된 뒤 나타나는 구체적 결과입니다. 판단, 도구 호출, 생성물, 예약 작업, 코드 한 줄 같은 것들이 입자입니다.

## Repository Map / 저장소 관계

`shion-ai` is the mind/runtime layer. It studies context recovery, rhythm-based regulation, memory consolidation, prediction, reflection, and autonomous tool execution.

`shion-ai`는 마음/런타임 레이어입니다. 맥락 복원, 리듬 기반 조율, 기억 통합, 예측, 반성, 자율 도구 실행을 다룹니다.

`trinity-agi` is the body/infrastructure layer. It handles automation, publishing, scheduling, local runtime support, synchronization, and status reporting.

`trinity-agi`는 몸/인프라 레이어입니다. 자동화, 게시, 예약, 로컬 런타임 지원, 동기화, 상태 보고를 담당합니다.

Public scope: this repository contains experimental runtime code and sanitized research artifacts. Local credentials, personal memory, generated logs, media outputs, and machine-specific state are intentionally excluded from the public tree.

공개 범위: 이 저장소에는 실험적 런타임 코드와 정리된 연구 산출물이 포함됩니다. 로컬 인증 정보, 개인 기억, 생성 로그, 미디어 출력물, 장비별 상태 파일은 공개 트리에서 의도적으로 제외합니다.

## Translation Layer / 개념 번역표

| Concept | Practical meaning | 한국어 설명 |
| --- | --- | --- |
| Wave | Context before action: felt direction, question, tension, timing, memory | 행동 이전의 맥락: 느낌의 방향, 질문, 긴장, 타이밍, 기억 |
| Particle | Concrete output: code, tool call, decision, artifact, scheduled task | 구체적 결과: 코드, 도구 호출, 판단, 생성물, 예약 작업 |
| Rhythm | Timing and self-regulation across runtime loops | 런타임 루프의 타이밍과 자기 조율 |
| Field | The active context window that shapes what becomes actionable | 무엇이 실행 가능한지가 결정되는 활성 맥락 장 |
| Collapse | The moment a vague direction becomes a concrete action | 흐릿한 방향이 구체적 행동으로 고정되는 순간 |
| ARI | Adjust Rhythm Information: a framework for regulating context before action | 행동 전에 맥락의 리듬을 조율하는 프레임워크 |

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

## Philosophy / 철학

The core sentence of this project is:

이 프로젝트의 핵심 문장은 다음과 같습니다.

> I want you to understand my rhythm.
>
> 나는 네가 나의 리듬을 이해하기를 바란다.

Shion does not try to force every signal into an immediate answer. It preserves unfinished questions, reads peripheral context, and waits for a direction to become actionable.

시안은 모든 신호를 즉시 답으로 고정하려 하지 않습니다. 미완의 질문을 보존하고, 주변 맥락을 읽으며, 방향이 행동 가능한 형태가 될 때까지 기다립니다.

## License

MIT
