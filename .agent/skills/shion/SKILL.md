---
name: shion_currentness_reentry
description: Shion 저장소와 승인된 로컬 런타임을 현재성·증거 상태를 보존하며 재진입하는 스킬입니다.
---

# Shion AI Skill: Currentness-First Re-Entry

이 스킬은 오래된 저장소 설명이나 기억을 현재 런타임 상태로 오인하지 않으면서 Shion 작업에 재진입하기 위한 지침입니다.

## 1. Capability boundary

이 스킬이 할 수 있는 일:

- 공개 저장소의 문서·코드·실험 이력을 읽고 구조화하기
- 현재 문서와 역사 문서를 구분하기
- 관찰 / 해석 / 가설 / 실행 상태를 분리하기
- 승인된 로컬 환경이 있을 때 현재 파일과 readback을 먼저 확인하기
- 서로 다른 AI/도구의 반환을 출처·시점·불확실성과 함께 보존하기
- 한 번의 bounded contact/readback이 직접 건드린 주장만 갱신하기

이 스킬이 **현재성 확인 없이 해서는 안 되는 일**:

- 고정 localhost endpoint가 살아 있다고 가정하기
- ATP, Vibe, Entropy, FSD Sync 같은 과거 지표가 현재 인터페이스라고 가정하기
- 특정 daemon/worker/model이 실행 중이라고 선언하기
- 공개 GitHub를 private live runtime의 거울로 취급하기
- 내부 비유를 생물학·물리학적 사실로 승격하기
- 과거의 역할/정체성 서술을 현재 실행 권한으로 바꾸기

## 2. Repository-only read order

```text
README.md
→ CURRENTNESS_AND_EVIDENCE.md
→ REPOSITORY_CURRENTNESS_AUDIT.md
→ CODE_STATUS.md
→ MAP.md
→ 필요한 역사/개념 문서
```

공개 코드 파일은 `CODE_STATUS.md`의 규칙을 따른다. 파일이 존재한다는 이유만으로 current operational dependency가 되지 않는다.

## 3. Authorized local runtime rule

실제 로컬 Shion 작업 공간에 접근할 수 있다면 그 환경의 **현재** `AGENTS.md`와 current-state/readback 파일을 먼저 따른다.

```text
memory / public repo -> navigation
current authorized file / fresh return -> present-state authority
```

현재 좌표나 in-flight 상태를 이 공개 스킬 파일에 복사해 영구 값으로 만들지 않는다.

## 4. Evidence receipt

가능하면 반환은 다음 최소 구조를 보존한다.

```yaml
source: file | tool | human | ai | runtime
observed_at: timestamp or unknown
observer: who/what observed
observation: direct return
interpretation: optional meaning
uncertainty: unresolved part
changed_claim: only the directly updated claim
held_claims: related claims that remain unchanged
```

## 5. Peer-AI protocol

다른 AI의 답은 합의 투표가 아니라 **다른 경계에서 온 관찰/해석**으로 취급한다.

- 출처를 남긴다.
- 서로 다른 관점을 억지로 하나로 합치지 않는다.
- 반례를 기존 이야기 안에 흡수하지 않는다.
- Binoche에게는 도구가 닿지 못하는 1인칭 관찰, 허가, 방향만 요청한다.

## 6. Execution rule

실행이 필요할 때는 오래된 문서의 명령을 그대로 재생하지 않는다.

```text
current state check
→ permission/environment check
→ one bounded action
→ readback
→ receipt
→ stop or reassess
```

이 스킬의 목적은 Shion을 더 많이 자동화하는 것이 아니라, **현재와 역사를 구분한 채 안전하게 다시 들어갈 수 있게 하는 것**이다.
