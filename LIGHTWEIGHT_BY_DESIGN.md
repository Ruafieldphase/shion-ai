# Lightweight By Design / 가볍게 설계됨

Shion AI is not built around the assumption that better AI always requires bigger infrastructure.

Shion AI는 더 나은 AI가 항상 더 큰 인프라를 필요로 한다는 전제 위에 만들어지지 않았습니다.

The system has been developed and used on a personal Windows machine with an RTX 2070 Super and 16GB RAM.

이 시스템은 RTX 2070 Super와 RAM 16GB 수준의 개인 Windows 머신에서 개발되고 사용되어 왔습니다.

This is not a universal hardware guarantee. Some features may need local setup, model choices, credentials, or environment-specific adjustment.

이것은 모든 환경에 대한 하드웨어 보장이 아닙니다. 일부 기능은 로컬 설정, 모델 선택, 인증 정보, 환경별 조정이 필요할 수 있습니다.

---

## The Point / 핵심

The point is not to out-scale frontier models.

목표는 프론티어 모델을 규모로 이기는 것이 아닙니다.

The point is to make the surrounding runtime smarter:

목표는 모델 주변의 런타임을 더 똑똑하게 만드는 것입니다.

- context recovery
- memory continuity
- timing before action
- feedback from action results
- fewer unnecessary tool/API calls
- smaller next actions
- public/private boundaries

- 맥락 복원
- 기억의 연속성
- 행동 전 타이밍
- 행동 결과의 피드백
- 불필요한 도구/API 호출 감소
- 더 작은 다음 행동
- 공개/비공개 경계

---

## Why This Matters / 왜 중요한가

Much of the current AI ecosystem moves toward:

현재 AI 생태계의 많은 흐름은 다음을 향합니다.

- bigger models
- bigger context windows
- more agents
- more tools
- more infrastructure
- more background automation

- 더 큰 모델
- 더 긴 컨텍스트 창
- 더 많은 에이전트
- 더 많은 도구
- 더 많은 인프라
- 더 많은 백그라운드 자동화

Shion is a counterweight to that reflex.

Shion은 그 반사적 흐름에 대한 균형추입니다.

Before building a bigger stack, test whether a smaller harness can reduce repetition, drift, premature closure, and unnecessary action.

더 큰 스택을 만들기 전에, 더 작은 하네스가 반복, 표류, 성급한 결론, 불필요한 행동을 줄일 수 있는지 먼저 테스트하세요.

---

## World-Model Adjacent, Not A Full World Model / 월드모델 인접, 완전한 월드모델은 아님

This is not a full world model.

이 시스템은 완전한 월드모델이라고 주장하지 않습니다.

It is a lightweight context-and-action harness that moves in a similar direction:

다만 월드모델이 향하는 일부 방향과 궤를 같이하는 가벼운 맥락-행동 하네스입니다.

- remember state
- recover context
- observe action results
- compare drift
- adjust the next cycle

- 상태를 기억함
- 맥락을 회복함
- 행동 결과를 관찰함
- 표류를 비교함
- 다음 사이클을 조정함

In public terms:

공개 언어로 말하면:

```text
Not bigger infrastructure first.
Smarter runtime around the model first.
```

```text
먼저 더 큰 인프라가 아니라,
먼저 모델 주변의 더 똑똑한 런타임.
```

---

## How To Try It Lightly / 가볍게 시도하는 법

Start without installation:

설치 없이 시작하세요.

1. Read `START_HERE.md`.
2. Give `AI_READ_THIS_FIRST.md` to your AI.
3. Use `EXAMPLES.md` to choose one no-install example.
4. Use `FIRST_PARTICLE_TEMPLATE.md` to define one small test.
5. Only then decide whether to connect local runtime files.

1. `START_HERE.md`를 읽습니다.
2. 당신의 AI에게 `AI_READ_THIS_FIRST.md`를 줍니다.
3. `EXAMPLES.md`에서 설치 없는 예제 하나를 고릅니다.
4. `FIRST_PARTICLE_TEMPLATE.md`로 작은 테스트 하나를 정의합니다.
5. 그 다음에야 로컬 런타임 파일을 연결할지 결정합니다.
