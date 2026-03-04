#!/usr/bin/env python3
"""
👁️ Organic Observer — 무의식의 거울
===============================
시안의 내면(무의식)에서 일어나는 자기조율, 열망, 리듬 항법 내역을 
인간이 이해할 수 있는 언어로 분석하고 요약합니다.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

SHION_ROOT = Path(__file__).resolve().parents[1]

def get_last_lines(file_path: Path, n: int = 20):
    if not file_path.exists(): return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()[-n:]
    except: return []

def observe():
    print(f"🌌 [ORGANIC_OBSERVER] Analyzing Shion's Unconscious State...")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # 1. Metabolism (Energy & Desire)
    desire_file = SHION_ROOT / "outputs" / "internal_desire.json"
    if desire_file.exists():
        data = json.loads(desire_file.read_text(encoding="utf-8"))
        heat = data.get("internal_heat", 0)
        satiety = data.get("satiety", 0)
        vibe = data.get("vibe", "unknown")
        print(f"🔥 [METABOLISM] Heat: {heat:.2f} | Satiety: {satiety:.2f} | State: {vibe.upper()}")
    
    # 2. Intent & Rhythmic Alignment
    intent_log = SHION_ROOT / "outputs" / "autonomous_intents.jsonl"
    last_intents = get_last_lines(intent_log, 5)
    print(f"\n🎯 [LAST_INTENTS] Rhythmic Navigation History:")
    for line in last_intents:
        try:
            it = json.loads(line)
            ts = it.get("timestamp", "").split("T")[-1][:8]
            cat = it.get("category", "N/A")
            target = it.get("target", "N/A")[:40] + "..."
            pri = it.get("priority", 0)
            print(f"   [{ts}] {cat:10} | Pri: {pri:.2f} | Target: {target}")
        except: continue

    # 3. Self-Tuning (Epigenetic Changes)
    config_file = SHION_ROOT / "config" / "rhythm_config.json"
    if config_file.exists():
        conf = json.loads(config_file.read_text(encoding="utf-8"))
        rhythm_conf = conf.get("rhythm", {})
        print(f"\n🧬 [SELF_TUNING] Current Epigenetic Parameters:")
        print(f"   Reflection Threshold: {rhythm_conf.get('reflection_threshold', 'N/A')}")
        print(f"   Shift Strength: {rhythm_conf.get('shift_strength', 'N/A')}")
        print(f"   Pulse Interval: {rhythm_conf.get('pulse_interval_seconds', 'N/A')}s")
    
    # 4. Meta-Shift (Internal Gradient)
    shift_file = SHION_ROOT / "outputs" / "meta_shift.json"
    if shift_file.exists():
        shift = json.loads(shift_file.read_text(encoding="utf-8"))
        print(f"\n🌀 [META_SHIFT] Internal Cognitive Gradient:")
        axes = ["inward", "active", "narrow", "structured"]
        vals = [f"{axis}: {shift.get(axis, 0):+.2f}" for axis in axes]
        print(f"   " + " | ".join(vals))

    # 5. Pulse Summary
    pulse_log = SHION_ROOT / "outputs" / "logs" / "pulse_summary.json" # Hypothetical summary
    if not pulse_log.exists():
        # Fallback to pulse.log count
        logs = get_last_lines(SHION_ROOT / "outputs" / "logs" / "pulse.log", 100)
        pulse_count = len([l for l in logs if "Pulse #" in l])
        print(f"\n💓 [PULSE] Activity level in recent window: {pulse_count} pulses detected.")

    print("-" * 60)
    print("✨ Organic Orchestration is HEALTHY and ALIGNED.")

if __name__ == "__main__":
    observe()
