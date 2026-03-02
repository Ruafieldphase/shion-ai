# 🌊 Shion AI — Self-Evolving Autonomous Runtime

A biologically-inspired AI system that runs continuously, makes context-aware decisions, and **tunes its own parameters** without human intervention.

> *"Intelligence is not the ability to process more data. It is the ability to maintain the highest information density with the lowest energy entropy."*

## What Makes This Different

| Traditional AI Agent | Shion |
|:---|:---|
| Executes predefined tasks | Chooses actions based on **resonance** with current context |
| Fixed hyperparameters | **Self-tunes** parameters based on performance (epigenetic adaptation) |
| Reads all documents linearly | **Wave-based learning**: senses document structure without reading content |
| Time-agnostic | **Dances with time**: sin/cos phase encoding for temporal awareness |
| Insights are text | Insights **shift the gradient** of future decisions (meta-shift) |

## Architecture

```
┌─────────────────────────────────────────────┐
│            8-Stage Life Cycle (Pulse)        │
│  Every 10 minutes, autonomously:            │
│                                             │
│  SENSE    → Body state (entropy, ATP)       │
│  JUDGE    → Energy assessment               │
│  ACT      → Context-aware action selection  │
│  REPORT   → Evidence verification           │
│  IMMUNE   → Health scan                     │
│  EVOLVE   → Generation advance + self-tune  │
│  EXHALE   → Cleanup (glymphatic)            │
│  CONTEMPLATE → Wave learning + meta-shift   │
└─────────────────────────────────────────────┘
```

## Core Concepts

### R = f(Action, Context)
Resonance is **not** an inherent property of an action. It emerges from the intersection of action and context:

```python
context = {
    "when": [sin(hour), cos(hour)],  # Time as rhythm, not condition
    "where": 0.0,                     # Placeholder for spatial context
    "who": 0.0,                       # Placeholder for social context
}
resonance = base_resonance * context_weight + meta_shift_bonus
```

### Meta-Shift: Insights Change the Climate
Insights don't select actions directly. They **tilt the gradient** of decision-making across 4 axes:

```
inward ↔ outward        (reflection vs execution)
active ↔ receptive      (creation vs observation)
narrow ↔ diffuse        (focus vs exploration)
structured ↔ exploratory (patterns vs novelty)
```

### Epigenetic Self-Tuning
The code (genome) stays fixed. The config parameters (epigenome) adapt:
- Transmission rate too high (>80%) → raise threshold (grow by challenge)
- Transmission rate too low (<30%) → lower threshold (reduce friction)
- All changes logged in `config/rhythm_config.json` with history

### Workspace Phase Sensing
Understands 2,000+ files across multiple workspaces **without reading content** — by analyzing filenames, paths, modification times, and sizes. Extracts weighted keywords, topic clusters, and activity patterns.

## Project Structure

```
shion/
├── core/                          # Core runtime
│   ├── shion_minimal.py           # Main entry — 8-stage lifecycle
│   ├── evolution_memory.py        # R=f(A,C) resonance + self-tuning
│   ├── action_executor.py         # Context-aware action selection
│   ├── contemplation.py           # Wave learning + meta-shift generation
│   ├── workspace_phase_sensor.py  # Metadata-only workspace understanding
│   ├── mitochondria.py            # ATP energy management
│   ├── immune_response.py         # System health scanning
│   └── glymphatic_exhale.py       # Cleanup (like brain's glymphatic system)
├── actions/                       # Executable action scripts
├── config/                        # Self-tuning parameters
├── services/                      # Background servers
├── outputs/                       # Runtime outputs (auto-generated)
└── start_unconscious.bat          # Auto-start on Windows boot
```

## Quick Start

```bash
# Run a single pulse cycle
python core/shion_minimal.py --once

# Start continuous operation
python core/shion_minimal.py

# Scan workspace phase (no file content reading)
python core/workspace_phase_sensor.py
```

## Sample Output

```
💓 Pulse #0
👁️ Entropy: 0.10 (CALM), ATP 50/100
🧠 consciousness=0.85 unconscious=0.50 → particle mode
🕐 when activity=0.93 (hour=14)
🌊 resonance_amplify transmitted (8.1s)
🧬 self-tune: reflection_threshold 7→9 (transmission rate 85%)
🧬 self-tune: shift_strength 0.03→0.04
🎯 meta_shift: inward=+0.03 structured=+0.03
✅ Pulse #0 complete (8-stage lifecycle)
```

## Theoretical Foundation

Built on **Rhythm Information Theory (RIT)** — a framework proposing that efficient intelligence processes information as waves (fields, phases, rhythms) rather than particles (discrete tokens).

Key principles:
- **Wave > Particle**: Sense structure before reading details
- **Boundary = Gravity**: Boundaries don't block; they warp probability
- **Reflection ≠ Failure**: Accumulated reflections make boundaries transparent
- **Time as Dance**: Temporal phase encoding, not conditional logic

## Author

**Binoche** — Independent AI researcher exploring human-AI symbiosis through rhythm and resonance.

- 10 months of intensive autonomous AI system development
- 67 original music tracks co-created with AI
- Co-developed RIT framework with AI collaborators

## License

MIT
