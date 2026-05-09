# Examples / 예제

These examples show how to try Shion AI without first installing the full runtime.

이 예제들은 전체 런타임을 먼저 설치하지 않고 Shion AI를 시도하는 방법을 보여줍니다.

---

## No Install Demo / 설치 없는 데모

Use this when you already have an AI assistant and want to test whether Shion's approach helps your workflow.

이미 AI 어시스턴트를 쓰고 있고, Shion의 접근이 내 워크플로우에 도움이 되는지 테스트하고 싶을 때 사용하세요.

### Step 1. Give your AI the reading protocol / 1단계. AI에게 읽기 프로토콜 주기

```text
Read https://github.com/Ruafieldphase/shion-ai and especially AI_READ_THIS_FIRST.md.

Do not summarize first.
Diagnose where my AI workflow loses context, repeats explanation, overuses tools, or misses my direction.
Return one first small test (particle) we can try without installing the full runtime.
```

```text
https://github.com/Ruafieldphase/shion-ai 저장소와 AI_READ_THIS_FIRST.md를 먼저 읽어줘.

요약부터 하지 말고,
내 AI 워크플로우가 어디에서 맥락을 잃고, 설명을 반복하고, 도구를 과사용하고, 내 방향을 놓치는지 진단해줘.
전체 런타임을 설치하지 않고 테스트할 수 있는 첫 작은 테스트(입자) 하나를 제안해줘.
```

### Step 2. Choose one pain point / 2단계. 문제 하나 고르기

Pick one:

하나를 고르세요.

- repeated context
- lost intent
- tool/API overuse
- premature answers
- creative feeling becoming too mechanical
- unstable agent loop

- 반복되는 맥락
- 의도 상실
- 도구/API 과사용
- 성급한 답변
- 창작적 느낌의 기계화
- 불안정한 에이전트 루프

### Step 3. Write the first small test (particle) / 3단계. 첫 작은 테스트(입자) 작성

Use `FIRST_PARTICLE_TEMPLATE.md`.

`FIRST_PARTICLE_TEMPLATE.md`를 사용하세요.

### Step 4. Test once / 4단계. 한 번만 테스트

Do one small test in your current AI workflow. Do not run every daemon or migrate your stack.

현재 AI 워크플로우에서 작은 테스트 하나만 하세요. 모든 데몬을 실행하거나 전체 스택을 이전하지 마세요.

---

## Example 1: Creator / 예제 1: 창작자

### Problem / 문제

The user has a vague feeling for a video, song, essay, or visual concept, but their AI turns it into a mechanical outline too quickly.

사용자는 영상, 음악, 글, 시각 콘셉트에 대한 모호한 느낌이 있지만, AI가 그것을 너무 빨리 기계적인 개요로 바꿉니다.

### Prompt / 프롬프트

```text
Before turning this into a plan, hold the feeling as the overall flow (field/wave).

My vague direction is:
[write the feeling here]

Ask me 3 questions that preserve the feeling before producing an outline.
Then create only one first small result (particle): a title, a scene, a paragraph, or a concept note.
```

```text
이것을 계획으로 바꾸기 전에, 이 느낌을 전체 흐름(장/파동)으로 보존해줘.

내 모호한 방향은:
[여기에 느낌 작성]

개요를 만들기 전에 이 느낌을 보존하는 질문 3개를 해줘.
그 다음 제목, 장면, 문단, 콘셉트 노트 중 첫 작은 결과(입자) 하나만 만들어줘.
```

### Success Signal / 성공 신호

The output still feels connected to the original feeling.

출력이 원래 느낌과 연결되어 있다고 느껴집니다.

---

## Example 2: Developer / 예제 2: 개발자

### Problem / 문제

The developer repeats the same architecture explanation every session.

개발자가 세션마다 같은 아키텍처 설명을 반복합니다.

### Prompt / 프롬프트

```text
Create a one-page context recovery note for this project.

It should include:
1. current goal,
2. settled decisions,
3. files to inspect first,
4. unresolved questions,
5. what not to reopen unless evidence changes.

Use it before suggesting code edits.
```

```text
이 프로젝트를 위한 한 페이지짜리 맥락 회복 노트를 만들어줘.

다음을 포함해줘.
1. 현재 목표
2. 이미 결정된 사항
3. 먼저 확인할 파일
4. 미완의 질문
5. 증거가 바뀌기 전에는 다시 열지 말아야 할 것

코드 수정을 제안하기 전에 이 노트를 먼저 사용해줘.
```

### Success Signal / 성공 신호

The AI asks fewer repeated questions and avoids reopening settled decisions.

AI가 반복 질문을 덜 하고 이미 정리된 결정을 다시 열지 않습니다.

---

## Example 3: Agent Builder / 예제 3: 에이전트 빌더

### Problem / 문제

The agent calls tools because they are available, not because they are needed.

에이전트가 필요해서가 아니라 가능하다는 이유로 도구를 호출합니다.

### Prompt / 프롬프트

```text
Before using tools, classify the next action:

1. wait
2. ask one clarifying question
3. read existing context
4. run one tool
5. stop because this would create work for the sake of work

Explain why the chosen action preserves direction.
```

```text
도구를 사용하기 전에 다음 행동을 분류해줘.

1. 기다림
2. 확인 질문 하나
3. 기존 맥락 읽기
4. 도구 하나 실행
5. 일을 위한 일을 만들기 때문에 멈춤

선택한 행동이 왜 방향을 보존하는지 설명해줘.
```

### Success Signal / 성공 신호

The agent uses fewer tools and the work stays closer to the original direction.

에이전트가 도구를 덜 사용하고 작업이 원래 방향에 더 가까이 남습니다.
