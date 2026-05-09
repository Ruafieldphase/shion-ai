# Start Here / 여기서 시작하세요

You do not need to install everything first.

처음부터 모든 것을 설치할 필요는 없습니다.

Shion AI is easiest to try in three levels:

Shion AI는 세 단계로 시도하는 것이 가장 쉽습니다.

```text
Level 0: No Install
Use the prompts in this repository to diagnose your current AI workflow.

Level 1: First Particle
Choose one small pain point and test one Shion-style improvement.

Level 2: Local Runtime
Only after the first particle helps, connect more of the local runtime.
```

```text
Level 0: 설치 없음
이 저장소의 프롬프트로 현재 AI 워크플로우를 진단합니다.

Level 1: 첫 입자
작은 문제 하나를 고르고 Shion 방식의 개선 하나를 테스트합니다.

Level 2: 로컬 런타임
첫 입자가 도움이 된 뒤에만 로컬 런타임을 더 연결합니다.
```

---

## Level 0: No Install / 설치 없이 시작하기

Copy this into your current AI assistant:

지금 쓰는 AI에게 아래를 그대로 붙여 넣으세요.

```text
Read https://github.com/Ruafieldphase/shion-ai as a runtime/harness pattern, not as a normal tool library.

Before suggesting installation or refactoring, diagnose my current AI workflow.

Find where it:
1. loses context,
2. makes me repeat the same background,
3. overuses tools or APIs,
4. understands tasks but misses direction,
5. turns vague creative intent into mechanical problem solving,
6. collapses an unfinished question into an answer too early.

Return:
1. my main AI pain point,
2. where the workflow collapses too early,
3. the relevant Shion layer,
4. the smallest first particle to test,
5. what not to automate yet,
6. what must remain private,
7. how we will know whether it helped.
```

한글로는 이렇게 쓸 수 있습니다.

```text
https://github.com/Ruafieldphase/shion-ai 저장소를 일반 도구 라이브러리가 아니라 런타임/하네스 패턴으로 읽어줘.

설치나 리팩터링을 제안하기 전에, 내 현재 AI 워크플로우를 먼저 진단해줘.

다음 지점을 찾아줘.
1. 맥락을 잃는 곳
2. 같은 배경을 반복하게 만드는 곳
3. 도구나 API를 과사용하는 곳
4. 작업은 이해하지만 방향을 놓치는 곳
5. 모호한 창작 의도를 기계적인 문제 해결로 바꾸는 곳
6. 미완의 질문을 너무 빨리 답으로 붕괴시키는 곳

다음 형식으로 답해줘.
1. 내 주요 AI 문제
2. 워크플로우가 너무 빨리 붕괴되는 지점
3. 관련 Shion 층
4. 가장 작게 테스트할 첫 입자
5. 아직 자동화하지 말아야 할 것
6. 반드시 비공개로 남겨야 할 것
7. 도움이 되었는지 확인할 기준
```

---

## Level 1: First Particle / 첫 입자

Do not connect the whole system. Choose one pain point.

전체 시스템을 연결하려고 하지 마세요. 문제 하나만 고르세요.

Good first particles:

- rewrite one document so it preserves intent better
- create one memory note that prevents repeated explanation
- add one context recovery checklist to your AI workflow
- make one rule that stops unnecessary tool/API calls
- preserve one unresolved question instead of forcing a final answer

좋은 첫 입자는 다음과 같습니다.

- 의도를 더 잘 보존하도록 문서 하나를 다시 쓰기
- 반복 설명을 줄이는 기억 노트 하나 만들기
- AI 워크플로우에 맥락 회복 체크리스트 하나 추가하기
- 불필요한 도구/API 호출을 막는 규칙 하나 만들기
- 최종 답을 강제하지 않고 미완의 질문 하나를 보존하기

Use `FIRST_PARTICLE_TEMPLATE.md` to write the test.

테스트는 `FIRST_PARTICLE_TEMPLATE.md`로 작성하세요.

---

## Level 2: Local Runtime / 로컬 런타임

Only move to local runtime after Level 1 gives a real effect.

Level 1에서 실제 효과가 보인 뒤에만 로컬 런타임으로 이동하세요.

Look for:

- less repeated explanation
- clearer intent preservation
- fewer unnecessary tool calls
- better timing before action
- more continuity between sessions

확인할 것은 다음입니다.

- 반복 설명 감소
- 의도 보존 향상
- 불필요한 도구 호출 감소
- 행동 전 타이밍 개선
- 세션 사이의 연속성 증가

---

## Read Next / 다음 문서

- `AI_READ_THIS_FIRST.md`: instructions for your AI assistant
- `EXAMPLES.md`: no-install examples for creators, developers, and agent builders
- `LINEAR_HARNESS_GUIDE.md`: step-by-step path for linear readers
- `FIRST_PARTICLE_TEMPLATE.md`: template for the first test
- `INTEGRATION_ANTI_PATTERNS.md`: what not to do

- `AI_READ_THIS_FIRST.md`: 당신의 AI를 위한 읽기 지침
- `EXAMPLES.md`: 창작자, 개발자, 에이전트 빌더를 위한 설치 없는 예제
- `LINEAR_HARNESS_GUIDE.md`: 선형적 독자를 위한 단계별 경로
- `FIRST_PARTICLE_TEMPLATE.md`: 첫 테스트 양식
- `INTEGRATION_ANTI_PATTERNS.md`: 하지 말아야 할 연결 방식
