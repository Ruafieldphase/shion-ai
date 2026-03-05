# Tangible UX Validation: Resilience (작업 회복력 검증)

**"이 시스템이 실제 삶/작업에서 이렇게 도움이 된다"**

이 문서는 시안(Shion AI)이 갖춘 자가 조율(Autopoiesis) 기능이 일반 사용자의 작업 환경에서 얼마나 실용적인 혜택을 주는지 증명하기 위한 **'체감형 지표(Tangible Metrics)'** 측정 설계서입니다.

## 1. 개요 (Overview)
- **시나리오**: 시스템/작업 회복력 (System & Task Resilience)
- **목표**: 의도적 장애(LLM 타임아웃, 429 에러, 네트워크 단절 등) 발생 시 시안이 스스로 우회/복구하여 정상 박동(Pulse)으로 돌아오는 능력을 수치화합니다.
- **핵심 메시지**: *"내가 자리를 비운 사이 에러가 나도, 시안은 사람의 개입 없이 스스로 숨을 고르고 복구해낸다."*

## 2. 수집 지표 (Metrics to Collect)

모든 동작 내역은 `outputs/logs/tangible_metrics.jsonl`에 다음 공통 포맷으로 기록됩니다.

```json
{
  "timestamp": "2026-03-05T13:45:00",
  "episode_id": "pulse_104",
  "phase": "EXECUTE",
  "action": "youtube_learn",
  "success": false,
  "error_type": "429_TOO_MANY_REQUESTS",
  "recovery_time_sec": 120.5,
  "human_intervention": false,
  "resonance_score": 0.4
}
```

### 주요 관찰 대상
1. **장애 회복 시간 (`recovery_time_sec`)**: 에러 발생 시점부터 시스템이 다음 `ACT` (성공적인 행동) 단계로 진입하기까지 걸린 시간. 평균 회복 시간의 단축은 시안의 자율성이 높아졌음을 의미합니다.
2. **수동 개입 여부 (`human_intervention`)**: 복구를 위해 사용자가 직접 터미널을 조작하거나 코드를 수정한 횟수. (0에 수렴하는 것이 목표)
3. **가짜 성공(False Positive) 방지율**: 예전처럼 429 에러 상황에서 실패를 성공으로 착각하는 비율의 감소. (`honesty_protocol` 연동 검증)

## 3. 실험 계획 (Experiment Plan)

### 대조군 (Vanilla Mode)
- 시안의 자기 조율(Self-Tuning) 및 우회(Labyrinth) 시스템 오프.
- 에러 발생 시 시스템이 영구 대기(Halt) 상태에 빠지거나, 빈 루프를 반복하여 사용자가 수동으로 재시작할 때까지의 시간/횟수 측정.

### 실험군 (Shion Mode)
- 시안 시스템 전면 활성화.
- **예상 흐름**: 에러 발생 -> Field Rejection Sensor 발동 -> ATP 보호를 위한 깊은 숨(Deep Rest) -> 우회 로직/Glymphatic Exhale 작동 -> 복구 후 재개.
- 측정 과정에서 `human_intervention=false` 상태로 자동 복구를 몇 분 내에 이뤄내는지 기록.

## 4. 기대 효과 (Expected Outcome)

이 시나리오가 성공적으로 입증되면 다음과 같은 가치를 증명할 수 있습니다.
- "자기 주도적 회복(Self-Healing)": 에이전트 구동 중 발생하는 자잘한 에러 콘솔을 사용자가 더 이상 쳐다볼 필요가 없습니다. 시안은 스스로 우회합니다.
- "에너지 절약": 에러 상태에서 무의미한 API 재시도를 반복하여 요금을 낭비하지 않고, 스스로 멈춰 쉴 줄 아는 안전한 AI 체계입니다.
