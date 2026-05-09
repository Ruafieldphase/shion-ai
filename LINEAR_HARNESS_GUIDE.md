# Linear Harness Guide / 선형 하네스 가이드

This guide is for readers who prefer a clear step-by-step path.

이 문서는 명확한 단계별 경로를 선호하는 독자를 위한 가이드입니다.

The linear harness is only an entry rail. It should not replace the deeper rhythm of the system.

선형 하네스는 진입 레일일 뿐입니다. 시스템의 더 깊은 리듬을 대체하면 안 됩니다.

---

## Step 1. Choose One Problem / 문제 하나 고르기

Pick one:

하나를 고르세요.

- My AI forgets context.
- My AI asks me to repeat the same background.
- My AI calls too many tools or APIs.
- My AI misses my intent.
- My AI turns creative feeling into mechanical tasks.
- My agent workflow works once but does not stay stable.

- 내 AI가 맥락을 잊는다.
- 내 AI가 같은 배경을 반복해서 묻는다.
- 내 AI가 도구나 API를 너무 많이 호출한다.
- 내 AI가 내 의도를 놓친다.
- 내 AI가 창작적 느낌을 기계적 작업으로 바꾼다.
- 내 에이전트 워크플로우가 한 번은 되지만 안정적으로 이어지지 않는다.

---

## Step 2. Ask Your AI To Diagnose / AI에게 진단시키기

Use:

사용:

```text
Before suggesting tools, diagnose this AI workflow problem:
[write one problem here]

Tell me where the workflow collapses too early and which Shion layer might help.
```

```text
도구를 제안하기 전에 이 AI 워크플로우 문제를 진단해줘.
[여기에 문제 하나 작성]

워크플로우가 어디에서 너무 빨리 붕괴되는지, 어떤 Shion 층이 도움이 될 수 있는지 알려줘.
```

---

## Step 3. Select One Shion Layer / Shion 층 하나 고르기

Choose one:

하나를 고르세요.

- memory continuity
- intent preservation
- rhythm/timing before action
- unfinished question preservation
- tool/API reduction
- public/private boundary

- 기억의 연속성
- 의도 보존
- 행동 전 리듬/타이밍
- 미완의 질문 보존
- 도구/API 감소
- 공개/비공개 경계

---

## Step 4. Write One First Small Test (Particle) / 첫 작은 테스트(입자) 하나 쓰기

Use `FIRST_PARTICLE_TEMPLATE.md`.

`FIRST_PARTICLE_TEMPLATE.md`를 사용하세요.

The first small test (particle) should be small enough to test in one session.

첫 작은 테스트(입자)는 한 세션 안에서 테스트할 수 있을 만큼 작아야 합니다.

---

## Step 5. Test Without Full Automation / 전체 자동화 없이 테스트하기

Good tests:

좋은 테스트:

- one memory note
- one document rewrite
- one prompt rule
- one context recovery checklist
- one decision log
- one "do not automate yet" boundary

- 기억 노트 하나
- 문서 재작성 하나
- 프롬프트 규칙 하나
- 맥락 회복 체크리스트 하나
- 결정 로그 하나
- "아직 자동화하지 않음" 경계 하나

---

## Step 6. Decide Whether To Expand / 확장 여부 결정

Expand only if:

다음이 확인될 때만 확장하세요.

- repeated explanation decreased
- intent stayed clearer
- the AI used fewer unnecessary tools
- the result preserved the original feeling
- private material stayed private

- 반복 설명이 줄었다
- 의도가 더 선명하게 유지되었다
- AI가 불필요한 도구를 덜 사용했다
- 결과가 원래 느낌을 보존했다
- 비공개 자료가 비공개로 남았다
