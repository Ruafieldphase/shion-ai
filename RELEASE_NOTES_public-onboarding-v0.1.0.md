# public-onboarding-v0.1.0

This release marks the first public onboarding baseline for the Shion-Trinity system.

## Shion AI

Shion AI now presents itself first as a lightweight harness that helps AI preserve direction across sessions by turning repeated context into a Context Recovery Note.

Included in this baseline:

- No-model context recovery demo
- No API key required
- No credentials required
- 3-Minute Start section at the top of README
- Before / After explanation
- Expected output for the demo
- Shion -> Context Recovery Note -> First small particle test -> Trinity flow

## Public Safety

This repository now includes public safety checks intended to make the first public entry safer:

- No-credential context recovery demo
- Minimal default requirements
- CI verification for the demo and public safety assumptions

## Next Direction

The next phase is path and environment cleanup:

- `SHION_ROOT`
- `AGI_WORKSPACE_ROOT`
- `WORKSPACE_ROOT`
- `config/paths.example.yaml` or `local_paths.example.json`
- hardcoded local path reduction

This release freezes the first public onboarding baseline before deeper internal path cleanup begins.

## Korean Summary

이 릴리즈는 Shion-Trinity 시스템의 첫 공개 온보딩 기준점입니다.

Shion은 반복되는 맥락을 Context Recovery Note로 바꾸는 가벼운 하네스로 정리되었습니다.

이번 기준점에는 다음이 포함됩니다.

- Shion no-model context recovery demo
- API 키와 인증 정보가 필요 없는 첫 실행
- public safety CI
- README 최상단 3분 입구
- Before / After
- expected output
- Shion-Trinity 흐름도

다음 단계는 path resolver, config example, hardcoded local path cleanup입니다.
