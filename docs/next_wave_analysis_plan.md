# Next Wave Analysis Plan

Author: 코덱스 루빛
Date: 2026-05-05

## Purpose

This is a memory anchor for the next session. Do not start with the full 423-file
corpus. Start with three representative tracks and test one question:

> Do the lyric ontology motifs appear as measurable wave rhythm features?

## Representative Tracks

```yaml
sample_tracks:
  lumen_declaration:
    role: awakening_and_light_breath
    preferred_file: D:\ARCHIVE_WORKSPACE\agi\music\Lumen Declaration.wav
    duration: 6:13
  memory_of_water:
    role: return_and_liquid_memory
    preferred_file: D:\ARCHIVE_WORKSPACE\agi\music\Memory of Water (물의 기억) (1).wav
    duration: 3:06
  light_learns_to_breathe:
    role: expansion_and_breath_learning
    preferred_file: D:\ARCHIVE_WORKSPACE\agi\music\mp3\The Time When Light Learns to Breathe.mp3
    duration: 4:15
```

## First Features

```yaml
wave_features:
  breath_pulse:
    meaning: slow amplitude pulse that behaves like breathing
  silence_gap:
    meaning: low-energy interval that creates reflective space
  crescendo_decay:
    meaning: energy rise followed by contraction or release
  loop_return:
    meaning: similarity between ending field and opening field
  emotional_density:
    meaning: coarse energy and spectral density proxy, not emotion proof
  phase_transition_point:
    meaning: timestamps where the track changes rhythm state
```

## Guardrail

```yaml
do:
  - analyze three sample tracks first
  - save JSON and Markdown summaries
  - compare extracted features against lyric ontology motifs
  - keep output interpretive, not proof-like

do_not:
  - analyze all 423 media files first
  - download remote Suno audio when local files exist
  - treat waveform metrics as direct emotion labels
  - attach metrics to runtime weights before replay
```

## Suggested Command

```powershell
cd /d C:\workspace2\shion
python scripts\sample_wave_feature_probe.py
```

Expected outputs:

```yaml
outputs:
  json: outputs/sample_wave_feature_probe.json
  markdown: outputs/sample_wave_feature_probe.md
```
