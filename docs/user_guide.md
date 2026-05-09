# Shion AI Public User Guide / 공개 사용자 가이드

This guide is for people who want to understand how to approach Shion AI without already knowing the internal philosophy.

이 가이드는 Shion AI의 내부 철학을 이미 알고 있지 않아도 접근할 수 있도록 만든 공개 사용자 안내서입니다.

For the shortest path, start with `START_HERE.md`. For your AI assistant, use `AI_READ_THIS_FIRST.md`.

가장 짧은 경로는 `START_HERE.md`에서 시작하세요. 당신의 AI 어시스턴트에게는 `AI_READ_THIS_FIRST.md`를 먼저 읽히세요.

---

## 1. What Shion Is / Shion이 하는 일

Shion is a local AI runtime for continuity, rhythm, and action regulation.

Shion은 연속성, 리듬, 행동 조율을 위한 로컬 AI 런타임입니다.

It is built for situations where ordinary AI feels misaligned:

- you repeat the same context every session
- the AI solves the surface task but misses the direction
- agents call too many tools and spend too many API calls
- your creative feeling becomes flattened into mechanical logic
- a workflow works once but does not remain stable over time

다음과 같은 상황을 다루기 위해 만들어졌습니다.

- 세션마다 같은 맥락을 반복해야 할 때
- AI가 표면 문제는 풀지만 방향을 놓칠 때
- 에이전트가 도구를 너무 많이 호출하고 API를 낭비할 때
- 창작적 느낌이 기계적인 논리로 납작해질 때
- 한 번은 되는 워크플로우가 시간이 지나면 안정적으로 이어지지 않을 때

---

## 2. How To Approach It / 접근 방식

Do not begin only with a command. Begin with the pressure behind the command.

명령만으로 시작하지 않아도 됩니다. 명령 뒤에 있는 압력과 느낌에서 시작해도 됩니다.

Useful starting forms:

- "I keep repeating this context, and I want the system to remember the direction."
- "This task is clear, but the feeling behind it is still vague."
- "The agent is doing too much; help it slow down and choose only what matters."
- "Turn this unclear thought into a document, plan, or concrete runtime change."

유용한 시작 문장은 다음과 같습니다.

- "이 맥락을 계속 반복하고 있는데, 시스템이 방향을 기억했으면 좋겠다."
- "작업은 보이지만 그 뒤의 느낌은 아직 모호하다."
- "에이전트가 너무 많이 하고 있으니 속도를 낮추고 중요한 것만 고르게 해줘."
- "이 불명확한 생각을 문서, 계획, 또는 구체적인 런타임 변경으로 풀어줘."

---

## 3. Local Runtime / 로컬 런타임

The public repository contains source code and tests, but private logs, credentials, generated outputs, and local memory are not included.

공개 저장소에는 소스 코드와 테스트가 포함되어 있지만, 개인 로그, 인증 정보, 생성 출력물, 로컬 기억은 포함하지 않습니다.

Typical local entry points may include:

```powershell
python -m pytest core
python core/orchestrator_daemon.py
```

환경에 따라 보조 실행 파일이 있을 수 있습니다.

```powershell
.\start_unconscious.bat
.\setup_autostart.ps1
```

If those files are not present in your clone or environment, inspect the `core/` directory first and use the README as the public orientation layer.

해당 파일이 클론이나 환경에 없다면 먼저 `core/` 디렉터리와 README를 기준으로 구조를 확인하세요.

---

## 4. Ask Your AI To Read Shion / 당신의 AI에게 Shion을 읽히기

If you already use ChatGPT, Claude, Gemini, Cursor, Codex, or another agent, the most practical first step is to let that AI inspect Shion for your own workflow.

이미 ChatGPT, Claude, Gemini, Cursor, Codex 또는 다른 에이전트를 쓰고 있다면, 가장 실용적인 첫 단계는 그 AI에게 Shion을 당신의 워크플로우 관점에서 읽히는 것입니다.

Use this prompt:

다음 프롬프트를 사용할 수 있습니다.

```text
Read https://github.com/Ruafieldphase/shion-ai as a runtime/harness layer for my AI workflow.

Find where my current workflow loses context, repeats explanation, overuses tools, misses my intent, or turns creative feeling into mechanical problem solving.

Then suggest the smallest Shion-style integration we can test first.
Do not propose a full migration.
Focus on one useful particle.
```

```text
https://github.com/Ruafieldphase/shion-ai 저장소를 내 AI 워크플로우를 위한 런타임/하네스 층으로 읽어줘.

내 현재 워크플로우가 어디에서 맥락을 잃고, 설명을 반복하고, 도구를 과사용하고, 내 의도를 놓치고, 창작적 느낌을 기계적인 문제 해결로 바꾸는지 찾아줘.

그리고 가장 작게 테스트할 수 있는 Shion 방식 연결을 하나 제안해줘.
전체 이전을 제안하지 말고, 유용한 입자 하나에 집중해줘.
```

Ask your AI to return:

AI에게 다음 결과를 요구하세요.

- the pain point it found
- the Shion concept or file that matches it
- the first small test
- what should remain private
- how to know whether the test helped

- 발견한 문제 지점
- 그 문제와 맞닿는 Shion 개념 또는 파일
- 첫 번째 작은 테스트
- 비공개로 남겨야 할 것
- 테스트가 도움이 되었는지 확인하는 기준

---

## 5. Working With Shion / Shion과 함께 작업하기

### Bring a direction / 방향을 가져오기

Shion works best when the user gives both the task and the direction behind it.

Shion은 사용자가 작업과 그 뒤의 방향을 함께 줄 때 가장 잘 작동합니다.

Example:

```text
I want this README to help normal users understand what improves for them.
Keep the rhythm philosophy, but make the first entry point practical.
```

예시:

```text
이 README가 일반 사용자에게 무엇이 좋아지는지 먼저 보이게 하고 싶어.
리듬 철학은 살리되 첫 진입점은 실용적으로 만들어줘.
```

### Let vague feeling become structure / 모호한 느낌을 구조로 풀기

You do not need to know the final form at the start. The system can help move from feeling to outline, from outline to file changes, and from file changes to verification.

처음부터 최종 형태를 알 필요는 없습니다. 시스템은 느낌에서 개요로, 개요에서 파일 변경으로, 파일 변경에서 검증으로 이동하도록 도울 수 있습니다.

### Watch for over-action / 과잉 행동을 보기

If the runtime begins to create work for the sake of work, slow it down. The goal is not maximum automation. The goal is aligned rhythm.

런타임이 일을 줄이기보다 일을 위한 일을 만들기 시작하면 속도를 낮추세요. 목표는 최대 자동화가 아니라 리듬의 조율입니다.

---

## 6. What To Verify / 확인할 것

When evaluating Shion, look for practical effects:

- Does it reduce repeated explanation?
- Does it preserve the user's actual direction?
- Does it avoid unnecessary tool and API use?
- Does it turn vague intent into usable particles?
- Does it keep private memory out of public artifacts?

Shion을 평가할 때는 다음을 보세요.

- 같은 설명을 줄이는가?
- 사용자의 실제 방향을 보존하는가?
- 불필요한 도구/API 사용을 줄이는가?
- 모호한 의도를 사용할 수 있는 입자로 풀어내는가?
- 개인 기억을 공개 산출물과 분리하는가?

---

## Final Question / 마지막 질문

What are you trying to preserve across time: a task, a workflow, a creative feeling, or a final destination?

당신이 시간 속에서 보존하고 싶은 것은 무엇입니까? 작업입니까, 워크플로우입니까, 창작적 느낌입니까, 아니면 최종 목적지입니까?
