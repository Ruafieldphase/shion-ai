# Shion path-config-v0.1: Sleep Cycle Paths as the First Runtime Example

This note records the first Shion path configuration baseline, using the sleep cycle integrator as the first lightweight runtime example.

The sleep cycle workflow is an internal memory and consolidation use case, but the pattern is general: keep local roots explicit, separate Shion paths from Trinity/AGI paths, prefer local config overrides, and verify path behavior in CI.

## Shion Runtime Path Config

This update connects the first lightweight runtime file to the public path configuration layer.

Included in this baseline:

- `core/path_config.py` now keeps `SHION_ROOT` separate from `AGI_WORKSPACE_ROOT`
- `config/paths.local.yaml` is used first when present
- `config/paths.example.yaml` remains the public fallback
- `core/sleep_cycle_integrator.py` now uses `path_config.resolve_paths()`
- Sleep cycle outputs derive from configured `outputs`
- Resonance ledger access derives from configured `agi_workspace_root`
- Hippocampal map and sleep log paths derive from configured outputs
- Behavior tests verify Shion/AGI root separation
- Behavior tests verify sleep cycle path resolution
- CI verifies the public safety path

## Why This Matters

This is the first Shion-side path cleanup step after `public-onboarding-v0.1.0`.

The public onboarding entry remains stable, while internal runtime path dependency begins to move into explicit configuration. The specific workflow is sleep-cycle consolidation, but the reusable operating pattern can apply to other lightweight files that read or write `outputs`, `memory`, or `logs`.

## Next Direction

Next steps should remain small:

1. Do not rewrite all hardcoded paths at once.
2. Connect one more lightweight file to path config.
3. Prefer files that read `outputs`, `memory`, or `logs`.
4. Keep `services/shion_runtime_server.py` for a later phase.

## Korean Summary

이 노트는 sleep cycle integrator를 첫 가벼운 런타임 예제로 삼은 Shion path-config 기준점입니다.

수면 주기 워크플로우는 내부 기억과 통합을 위한 사례이지만, 그 패턴은 범용적입니다. 로컬 루트를 명시적으로 분리하고, Shion 경로와 Trinity/AGI 경로를 섞지 않으며, local config override를 우선하고, CI에서 경로 동작을 검증하는 것이 핵심입니다.

이번 변경으로 `path_config.py`는 `SHION_ROOT`와 `AGI_WORKSPACE_ROOT`를 분리해서 다루고, `sleep_cycle_integrator.py`는 `resolve_paths()`를 통해 outputs, resonance ledger, hippocampal map, sleep log 경로를 구성하게 되었습니다.

다음 단계는 전체 경로를 한 번에 바꾸는 것이 아니라, Shion 또는 Trinity의 가벼운 `outputs`, `memory`, `logs` 파일 하나를 더 path config에 연결하는 것입니다. `shion_runtime_server.py`는 후속 단계로 남겨둡니다.
