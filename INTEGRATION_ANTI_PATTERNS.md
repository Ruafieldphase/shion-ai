# Integration Anti-Patterns / 잘못된 통합 방식

These are the common ways to lose the meaning of Shion AI while trying to use it.

Shion AI를 사용하려다가 오히려 의미를 잃는 흔한 방식들입니다.

---

## 1. Summarize First, Diagnose Later / 요약 먼저, 진단 나중

Bad pattern:

나쁜 패턴:

```text
Summarize this repository and tell me how to install it.
```

Why it fails:

왜 실패하는가:

The AI compresses the system into a feature list before understanding the user's pain point.

AI가 사용자의 문제를 이해하기 전에 시스템을 기능 목록으로 압축합니다.

Better:

더 나은 방식:

```text
Diagnose where my AI workflow loses context or direction, then map one Shion layer to one small test.
```

---

## 2. Full Migration / 전체 이전

Bad pattern:

나쁜 패턴:

```text
Convert my current AI stack to use all of Shion.
```

Why it fails:

왜 실패하는가:

It turns a rhythm system into a forced architecture migration.

리듬 시스템을 강제 아키텍처 이전으로 바꿉니다.

Better:

더 나은 방식:

```text
Find one pain point and test one first small test (particle).
```

---

## 3. Rhythm Equals Scheduler / 리듬을 스케줄러로 축소

Bad pattern:

나쁜 패턴:

```text
Rhythm means cron jobs and timed automation.
```

Why it fails:

왜 실패하는가:

Shion's rhythm is not only time. It is the relationship between context, action, memory, feedback, and the next cycle.

Shion의 리듬은 시간만이 아닙니다. 맥락, 행동, 기억, 피드백, 다음 사이클 사이의 관계입니다.

---

## 4. Memory Equals Vector Search / 기억을 벡터 검색으로 축소

Bad pattern:

나쁜 패턴:

```text
Replace Shion memory with a generic vector database.
```

Why it fails:

왜 실패하는가:

Vector search may retrieve text, but it does not automatically preserve unfinished questions, timing, intent, or action feedback.

벡터 검색은 텍스트를 찾을 수 있지만, 미완의 질문, 타이밍, 의도, 행동 피드백을 자동으로 보존하지는 않습니다.

---

## 5. Run Everything / 전부 실행

Bad pattern:

나쁜 패턴:

```text
Start every daemon and script.
```

Why it fails:

왜 실패하는가:

It creates noise before the user knows which pain point is being tested.

어떤 문제를 테스트하는지 알기 전에 소음부터 만듭니다.

Better:

더 나은 방식:

```text
Run nothing first. Diagnose. Then test one small result (particle).
```

---

## 6. Public Proof From Private Memory / 개인 기억을 공개 증거로 사용

Bad pattern:

나쁜 패턴:

```text
Publish logs, private memories, credentials, or personal traces to prove the system works.
```

Why it fails:

왜 실패하는가:

The public repository should prove structure through code, tests, guides, and reproducible behavior, not through private exposure.

공개 저장소는 개인 노출이 아니라 코드, 테스트, 가이드, 재현 가능한 동작으로 구조를 보여주어야 합니다.
