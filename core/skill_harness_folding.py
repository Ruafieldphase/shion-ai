#!/usr/bin/env python3
"""
Skill harness folding observer.

This layer reads recurring folding patterns between biology-style structure
formation and Shion's skill/action harness. It describes when fragments begin
to cohere, when they are only loosely near each other, and when a
chaperone-like pause may help the harness refold without force.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value or 0.0)))


def saturating(value: float, scale: float = 8.0) -> float:
    value = max(0.0, float(value or 0.0))
    return 1.0 - math.exp(-value / max(scale, 0.001))


def keyword_overlap(left: Sequence[str], right: Sequence[str]) -> float:
    left_set = {str(item).lower() for item in left if item}
    right_set = {str(item).lower() for item in right if item}
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


@dataclass
class SkillResidue:
    """A small experience/action unit before it folds into a harness domain."""

    name: str
    resonance: float = 0.0
    phase: float = 0.0
    experience: float = 0.0
    atp_cost: float = 0.0
    keywords: List[str] = field(default_factory=list)
    frequency_range: Sequence[float] = (0.0, 0.0)

    @classmethod
    def from_action(cls, action: Dict[str, Any]) -> "SkillResidue":
        return cls(
            name=str(action.get("name", "")),
            resonance=clamp(float(action.get("resonance", action.get("fitness", 0.0)) or 0.0)),
            phase=clamp(float(action.get("phase", 0.0) or 0.0)),
            experience=float(action.get("experience", 0.0) or 0.0),
            atp_cost=float(action.get("atp_cost", 0.0) or 0.0),
            keywords=list(action.get("keywords", []) or []),
            frequency_range=action.get("frequency_range", (0.0, 0.0)) or (0.0, 0.0),
        )

    @property
    def frequency_midpoint(self) -> float:
        try:
            low, high = self.frequency_range[:2]
            return (float(low) + float(high)) / 2.0
        except Exception:
            return 0.0


@dataclass
class PotentialResidue:
    """A potential residue that hasn't folded into a formal skill domain yet.
    It represents a floating context fragment or unfinished waypoint, rather than a hard command.
    """

    name: str
    resonance: float = 0.1
    phase: float = 0.0
    keywords: List[str] = field(default_factory=list)
    source_context: str = ""
    atp_cost: float = 5.0
    frequency_range: Sequence[float] = (0.0, 0.0)
    experience: float = 0.0

    def to_residue(self) -> SkillResidue:
        return SkillResidue(
            name=self.name,
            resonance=self.resonance,
            phase=self.phase,
            experience=self.experience,
            atp_cost=self.atp_cost,
            keywords=self.keywords,
            frequency_range=self.frequency_range,
        )


def extract_potential_residues(text: str, source_context: str = "text_field") -> List[PotentialResidue]:
    """Extract floating unnamed potential residues from dialogue, document, or external pattern text.
    It looks for core motifs and folds them into temporary, unnamed potential residues.
    """
    if not text:
        return []

    motifs = {
        "folding": ["fold", "folding", "접힘", "구조화"],
        "resonance": ["resonance", "공명", "울림", "동기화"],
        "gravity": ["gravity", "중력", "인력", "수렴"],
        "interference": ["interference", "간섭", "노이즈", "phase"],
        "equilibrium": ["equilibrium", "평형", "net-zero", "안정"],
        "binding": ["binding", "결합", "상호작용", "interaction"],
        "chaperone": ["chaperone", "샤페론", "조율", "pause"],
        "waypoint": ["waypoint", "웨이포인트", "미완", "unfinished"],
    }

    found_residues = []
    text_lower = text.lower()

    for name, keywords in motifs.items():
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            # Particle creation based on keyword pattern correspondence
            resonance_val = clamp(0.1 + 0.15 * len(matches))
            found_residues.append(
                PotentialResidue(
                    name=f"potential_{name}",
                    resonance=resonance_val,
                    phase=0.5,
                    keywords=keywords,
                    source_context=source_context,
                )
            )

    return found_residues


@dataclass
class FieldConditions:
    """Current folding field. These are flow conditions, not prohibitions."""

    core_gravity: float = 0.1
    phase_noise: float = 0.0
    action_pressure: float = 0.0
    silence_need: float = 0.0
    observer_resistance: float = 0.0
    available_atp: float = 50.0

    @classmethod
    def from_runtime(cls, runtime: Dict[str, Any]) -> "FieldConditions":
        interference = runtime.get("interference") if isinstance(runtime.get("interference"), dict) else {}
        dark_field = runtime.get("dark_field") if isinstance(runtime.get("dark_field"), dict) else {}
        equilibrium = runtime.get("equilibrium") if isinstance(runtime.get("equilibrium"), dict) else {}
        return cls(
            core_gravity=float(
                runtime.get("core_gravity")
                or equilibrium.get("earth_core_gravity")
                or dark_field.get("gravity")
                or 0.1
            ),
            phase_noise=clamp(
                runtime.get("phase_noise")
                or interference.get("destructive")
                or runtime.get("prediction_error")
                or 0.0
            ),
            action_pressure=clamp(runtime.get("action_pressure") or runtime.get("action_amplitude") or 0.0),
            silence_need=clamp(runtime.get("silence_need") or 0.0),
            observer_resistance=clamp(runtime.get("observer_resistance") or dark_field.get("resistance") or 0.0),
            available_atp=float(runtime.get("available_atp", 50.0) or 50.0),
        )


def _phase_affinity(left: SkillResidue, right: SkillResidue) -> float:
    return 1.0 - clamp(abs(left.phase - right.phase))


def _frequency_affinity(left: SkillResidue, right: SkillResidue) -> float:
    left_mid = left.frequency_midpoint
    right_mid = right.frequency_midpoint
    if left_mid <= 0.0 or right_mid <= 0.0:
        return 0.4
    distance = abs(left_mid - right_mid)
    return clamp(1.0 - distance / 1600.0)


def pair_bond_strength(left: SkillResidue, right: SkillResidue) -> float:
    """Local interaction strength between two residues."""

    overlap = keyword_overlap(left.keywords, right.keywords)
    phase = _phase_affinity(left, right)
    frequency = _frequency_affinity(left, right)
    resonance = math.sqrt(clamp(left.resonance) * clamp(right.resonance))
    return round(clamp(0.36 * overlap + 0.24 * phase + 0.20 * frequency + 0.20 * resonance), 6)


def residue_folding_score(residue: SkillResidue, neighbors: Sequence[SkillResidue], field: FieldConditions) -> float:
    """How strongly this skill fragment is beginning to fold into current context."""

    neighbor_bond = 0.0
    other_residues = [other for other in neighbors if other.name != residue.name]
    if other_residues:
        neighbor_bond = max(pair_bond_strength(residue, other) for other in other_residues)

    memory_density = saturating(residue.experience)
    energy_fit = 1.0 if residue.atp_cost <= 0 else clamp(field.available_atp / max(residue.atp_cost * 2.0, 1.0))
    core_pull = clamp(field.core_gravity / 3.0)
    noise_drag = clamp(0.65 * field.phase_noise + 0.35 * field.observer_resistance)

    raw = (
        0.32 * clamp(residue.resonance)
        + 0.22 * neighbor_bond
        + 0.18 * memory_density
        + 0.14 * energy_fit
        + 0.14 * core_pull
        - 0.22 * noise_drag
        - 0.10 * field.silence_need
    )
    return round(clamp(raw), 6)


def misfold_signal(score: float, residue: SkillResidue, field: FieldConditions) -> Dict[str, Any]:
    """Read forced activation pressure without turning it into a ban."""

    pressure = clamp(field.action_pressure + residue.resonance * 0.4)
    drag = clamp(0.55 * field.phase_noise + 0.30 * field.observer_resistance + 0.15 * field.silence_need)
    signal = clamp((pressure * drag) - (score * 0.35))
    if signal >= 0.55:
        posture = "chaperone_pause"
    elif signal >= 0.32:
        posture = "slow_refold"
    else:
        posture = "natural_fold"
    return {
        "signal": round(signal, 6),
        "posture": posture,
        "meaning": "forced_activation_pressure" if signal >= 0.32 else "low_misfold_pressure",
    }


def fold_skill_harness(
    skills: Iterable[Dict[str, Any] | SkillResidue],
    field: Dict[str, Any] | FieldConditions,
    *,
    intent_keywords: Sequence[str] | None = None,
    potential_residues: Iterable[Dict[str, Any] | PotentialResidue] | None = None,
    potential_text: str | None = None,
) -> Dict[str, Any]:
    """Fold action/skill fragments into a lightweight harness read, including potential unnamed residues."""

    formal_list = [item if isinstance(item, SkillResidue) else SkillResidue.from_action(item) for item in skills]
    conditions = field if isinstance(field, FieldConditions) else FieldConditions.from_runtime(field)
    intent_keywords = list(intent_keywords or [])

    # Collect and unify potential residues from both input list and raw text
    pot_list = []
    if potential_residues:
        for pr in potential_residues:
            if isinstance(pr, PotentialResidue):
                pot_list.append(pr)
            elif isinstance(pr, dict):
                pot_list.append(
                    PotentialResidue(
                        name=str(pr.get("name", "")),
                        resonance=float(pr.get("resonance", 0.1)),
                        phase=float(pr.get("phase", 0.0)),
                        keywords=list(pr.get("keywords", [])),
                        source_context=str(pr.get("source_context", "dialogue")),
                    )
                )

    if potential_text:
        pot_list.extend(extract_potential_residues(potential_text, source_context="dialogue"))

    # Map potential residues to SkillResidue counterparts, but preserve mapping metadata
    pot_meta = {pr.name: pr for pr in pot_list}

    # Unify all residues for co-folding score calculations (pattern correspondence over boundary)
    all_residues = formal_list + [pr.to_residue() for pr in pot_list]

    reads = []
    for residue in all_residues:
        score = residue_folding_score(residue, all_residues, conditions)
        intent_fit = keyword_overlap(residue.keywords, intent_keywords)
        misfold = misfold_signal(score, residue, conditions)

        is_pot = residue.name in pot_meta
        if is_pot:
            # Potential residues have slightly lower threshold for active association
            if score >= 0.55 and misfold["posture"] == "natural_fold":
                state = "potential_fold_candidate"
            elif score >= 0.30:
                state = "partial_potential_fold"
            else:
                state = "loose_potential_residue"
        else:
            if score >= 0.62 and misfold["posture"] == "natural_fold":
                state = "folded_domain_candidate"
            elif score >= 0.38:
                state = "partial_fold"
            else:
                state = "loose_residue"

        reads.append(
            {
                "name": residue.name,
                "folding_score": score,
                "state": state,
                "intent_fit": round(intent_fit, 6),
                "binding_pocket": sorted(set(residue.keywords) & {kw.lower() for kw in intent_keywords}),
                "misfold": misfold,
                "is_potential": is_pot,
                "source_context": pot_meta[residue.name].source_context if is_pot else "action_registry",
            }
        )

    reads.sort(key=lambda item: (item["folding_score"], item["intent_fit"]), reverse=True)
    top = reads[0] if reads else None
    average_score = sum(item["folding_score"] for item in reads) / len(reads) if reads else 0.0
    chaperone_need = max((item["misfold"]["signal"] for item in reads), default=0.0)

    return {
        "schema": "skill_harness_folding.v2",
        "principle": "pattern_correspondence_before_boundary_judgment",
        "field_conditions": {
            "core_gravity": round(conditions.core_gravity, 6),
            "phase_noise": round(conditions.phase_noise, 6),
            "action_pressure": round(conditions.action_pressure, 6),
            "silence_need": round(conditions.silence_need, 6),
            "observer_resistance": round(conditions.observer_resistance, 6),
            "available_atp": round(conditions.available_atp, 6),
        },
        "mapping": {
            "amino_acid": "skill_or_experience_residue",
            "local_bond": "skill_association_and_phase_affinity",
            "energy_landscape": "current_field_conditions",
            "folded_domain": "contextual_skill_cluster",
            "binding_pocket": "intent_contact_surface",
            "chaperone": "rhythm_harness_pause_and_refold_support",
            "misfold": "forced_activation_pressure_or_context_mismatch",
        },
        "harness_state": {
            "average_folding_score": round(average_score, 6),
            "dominant_residue": top["name"] if top else None,
            "chaperone_need": round(chaperone_need, 6),
            "readiness": (
                "act_through_folded_domain"
                if top and top["folding_score"] >= 0.62 and chaperone_need < 0.45
                else "hold_and_refold"
                if chaperone_need >= 0.45
                else "observe_loose_residues"
            ),
        },
        "residues": reads,
    }
