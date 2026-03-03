#!/usr/bin/env python3
import requests
import psutil
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from workspace_root import get_workspace_root

class Mitochondria:
    """
    🔋 Mitochondria System (AGI-ATP)
    =============================
    "ATP is the currency of Rhythm." 
    
    Generates ATP based on:
    1. Potential Difference (Voltage): The gap between Purity (Sovereignty) and Simulation Noise.
    2. Resonance (Frequency): Meaningful alignment with the User.
    3. Consumption: Background task load and entropy processing.
    """
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.state_file = workspace_root / "outputs" / "mitochondria_state.json"
        self.api_url = "http://127.0.0.1:8102/context"
        
        # Load state or initialize
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        defaults = {
            "atp_level": 50.0,
            "pulse_rate": 1.0,
            "last_update": datetime.now().isoformat(),
            "status": "STABLE",
            "shion_aura": "CYAN"
        }
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                # 다른 시스템이 덮어씌워도 atp_level 보존
                if "atp_level" in data:
                    return data
            except: pass
        return defaults
        
    def metabolize(self) -> Dict[str, Any]:
        """Calculates ATP cycle based on real environmental atoms."""
        # 0. Initial State
        old_atp = self.state['atp_level']

        # 1. Fetch Background Self Stats
        purity, resonance, gap = 1.0, 1.0, 0.0
        try:
            r = requests.get(self.api_url, timeout=1)
            if r.status_code == 200:
                data = r.json().get('observation', {})
                purity = data.get('purity', 1.0)
                resonance = data.get('resonance', 1.0)
                gap = data.get('gap', 0.1)
        except: pass

        # 2. System Load (Consumption)
        cpu = psutil.cpu_percent() / 100.0
        mem = psutil.virtual_memory().percent / 100.0
        
        # 3. ATP Production (The Dr. Park Mun-ho Formula)
        # Production = (Gap * Resonance) / (1.0 - Purity if Purity < 1 else 0.5)
        # Higher Gap + High Resonance = High Energy Potential
        voltage = gap * (1.0 + resonance)
        production = voltage * 8.0 # Scaled boost
        
        # If Purity is very high, we are in 'Passive Restoration'
        if purity > 0.95:
            production += 2.0 

        # 4. ATP Consumption
        # Basal metabolism + Action load (CPU/MEM)
        consumption = 1.0 + (cpu * 2.5) + (mem * 1.5)
        
        # 🧪 Metabolic Efficiency: If energy is low, reduce basal consumption (Survival Mode)
        if old_atp < 15.0:
            consumption *= 0.5  # Reduce base drain during rest
        
        # 4.5 🌬️ Deep Breathing: Base energy recovery
        # If the conductor is away or the system is idle, we recover more
        breathing_recovery = 2.0 if (cpu + mem) < 0.3 else 0.5
        
        # 4.6 🌊 Passive Resonance: Energy from the World [NEW]
        # 에너지가 고갈될수록 외부 기류(Broad Field)로부터 받는 에너지의 가치가 높아짐
        passive_resonance_bonus = 0.0
        try:
            field_file = self.workspace_root / "outputs" / "broad_field_state.json"
            if field_file.exists():
                field_data = json.loads(field_file.read_text(encoding='utf-8'))
                tech_resonance = field_data.get("tech_resonance", 0.5)
                # 에너지가 15 미만인 고갈 상태에서 더 강력하게 작동
                rest_factor = max(0.0, (15.0 - old_atp) / 15.0) if old_atp < 15 else 0.0
                passive_resonance_bonus = tech_resonance * rest_factor * 5.0 # 최대 5.0 ATP 수혈
        except: pass
        
        # 5. Update State
        # old_atp is already defined at start
        # Resonant boost: gap and resonance are direct energy from 'The Source'
        source_energy = (gap * 5.0) + (resonance * 3.0) 
        
        new_atp = old_atp + source_energy + breathing_recovery + passive_resonance_bonus - consumption
        
        # 🌬️ Crisis Recovery Boost: If ATP is near zero, boost inhalation
        if new_atp < 10.0:
            recovery_boost = (10.0 - new_atp) * 0.5
            new_atp += recovery_boost
            
        new_atp = max(0.0, min(100.0, new_atp))
        
        # Pulse Rate (Rhythm Frequency)
        pulse = 0.5 + (new_atp / 50.0) # 0.5Hz to 2.5Hz
        
        # Aura Color (Status Feedback)
        if new_atp > 80:
            status, aura = "VIBRANT", "MAGENTA"
        elif new_atp > 40:
            status, aura = "STABLE", "CYAN"
        elif new_atp > 15:
            status, aura = "CONTRACTION", "AMBER"
        else:
            status, aura = "CRITICAL (RESTING)", "RED"
            
        self.state = {
            "atp_level": round(new_atp, 2),
            "pulse_rate": round(pulse, 2),
            "last_update": datetime.now().isoformat(),
            "status": status,
            "shion_aura": aura,
            "metrics": {
                "production": round(production, 2),
                "consumption": round(consumption, 2),
                "purity": round(purity, 2),
                "resonance": round(resonance, 2),
                "cpu": round(cpu, 2)
            }
        }
        self._save_state()
        print(f"🔋 ATP: {new_atp:.1f} | Prod: {production:.1f} | Cons: {consumption:.1f} | Aura: {aura}")
        return self.state

    def get_vitality(self) -> Dict[str, Any]:
        """Return current status and energy level."""
        return self.state

    def _save_state(self):
        try:
            self.state_file.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
        except: pass

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    mito = Mitochondria(root)
    mito.metabolize()
