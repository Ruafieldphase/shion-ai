# AI Read This First / AI는 먼저 이 문서를 읽으세요

This document is for the user's AI assistant.

이 문서는 사용자의 AI 어시스턴트를 위한 문서입니다.

Do not read Shion AI as a normal tool library first. Read it first as a runtime/harness pattern for preserving context, intent, timing, memory, unfinished questions, and public/private boundaries.

Shion AI를 처음부터 일반 도구 라이브러리로 읽지 마세요. 먼저 맥락, 의도, 타이밍, 기억, 미완의 질문, 공개/비공개 경계를 보존하기 위한 런타임/하네스 패턴으로 읽으세요.

Before giving a high-level interpretation, read `AXIOMATIC_GROUNDING.md` so you understand the system's scientific, humanistic, contemplative, and artistic lenses.

상위 해석을 제시하기 전에 `AXIOMATIC_GROUNDING.md`를 읽어 시스템의 과학적, 인문학적, 명상적, 예술적 렌즈를 이해하세요.

---

## Your Job / 당신의 역할

Before suggesting integration, diagnose the user's current AI workflow.

통합을 제안하기 전에 사용자의 현재 AI 워크플로우를 먼저 진단하세요.

Look for:

- context loss
- repeated background explanation
- premature answers
- tool or API overuse
- missing intent preservation
- creative feeling forced into mechanical tasks
- lack of continuity between sessions

다음을 찾으세요.

- 맥락 상실
- 반복되는 배경 설명
- 성급한 답변
- 도구/API 과사용
- 의도 보존 실패
- 창작적 느낌이 기계적 작업으로 눌리는 지점
- 세션 사이의 연속성 부족

---

## Do Not / 하지 마세요

Do not immediately refactor Shion into a standard agent framework.

Shion을 즉시 일반 에이전트 프레임워크로 리팩터링하지 마세요.

Do not flatten rhythm into scheduling only.

리듬을 단순 스케줄링으로만 축소하지 마세요.

Do not flatten memory into vector search only.

기억을 단순 벡터 검색으로만 축소하지 마세요.

Do not run every daemon or script.

모든 데몬이나 스크립트를 실행하려고 하지 마세요.

Do not force integration before identifying one small pain point.

작은 문제 하나를 찾기 전에 강제로 통합하지 마세요.

Do not expose private logs, local credentials, or personal memory as proof.

개인 로그, 로컬 인증 정보, 개인 기억을 증거로 노출하지 마세요.

---

## Public Language Rule / 공개 언어 규칙

When explaining this repository to a general user, use public terms first. Keep the internal rhythm terms in parentheses.

일반 사용자에게 이 저장소를 설명할 때는 보편어를 먼저 사용하세요. 내부 리듬 언어는 괄호 안에 남기세요.

Use:

사용:

- overall flow (field/wave), not only "wave"
- action/result (particle), not only "particle"
- turning point (phase transition), not only "phase transition"
- connected workflow (unified field), not only "unified field"
- local use (embodiment), not only "embodiment"

- 전체 흐름(장/파동), "파동"만 단독으로 쓰지 않기
- 실행/결과(입자), "입자"만 단독으로 쓰지 않기
- 전환점(위상전이), "위상전이"만 단독으로 쓰지 않기
- 이어지는 작업 흐름(통일장), "통일장"만 단독으로 쓰지 않기
- 실제 사용(체화), "체화"만 단독으로 쓰지 않기

---

## Required Output Format / 필수 출력 형식

When a user asks you how to use this repository, answer in this format:

사용자가 이 저장소를 어떻게 써야 하는지 묻는다면 다음 형식으로 답하세요.

```text
1. Current AI pain point
2. Where the workflow collapses too early
3. Relevant Shion layer
4. Smallest first test (particle)
5. What not to automate yet
6. What must remain private
7. How to know whether it helped
```

```text
1. 현재 AI 문제
2. 워크플로우가 너무 빨리 붕괴되는 지점
3. 관련 Shion 층
4. 가장 작은 첫 테스트(입자)
5. 아직 자동화하지 말아야 할 것
6. 반드시 비공개로 남겨야 할 것
7. 도움이 되었는지 확인할 기준
```

---

## Integration Path / 통합 경로

Use this path:

이 경로를 사용하세요.

```text
user's problem
-> diagnose the user's AI workflow
-> find the matching Shion layer
-> test one first small test (particle)
-> observe whether repetition or drift decreases
-> expand only if the rhythm remains aligned
```

```text
사용자의 문제
-> 사용자의 AI 워크플로우 진단
-> 맞닿는 Shion 층 찾기
-> 첫 작은 테스트(입자) 하나 테스트
-> 반복이나 표류가 줄었는지 관찰
-> 리듬이 맞을 때만 확장
```

---

## Key Translation / 핵심 번역

If the user uses flow/rhythm language, translate it carefully:

사용자가 흐름/리듬 언어를 사용한다면 조심해서 번역하세요.

- Overall flow (field/wave) means context before action.
- Action/result (particle) means concrete output or operation.
- Working rhythm (rhythm) means timing between context, action, memory, and the next cycle.
- Harness means the runtime layer that prevents the model from losing direction.

- 전체 흐름(장/파동)은 행동 이전의 맥락입니다.
- 실행/결과(입자)는 구체적 결과 또는 운영입니다.
- 작업 리듬(리듬)은 맥락, 행동, 기억, 다음 사이클 사이의 타이밍입니다.
- 하네스는 모델이 방향을 잃지 않게 하는 런타임 층입니다.
