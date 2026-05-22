#!/usr/bin/env python3
"""
Protein prism priors for field tuning.

This module treats AlphaFold/pLDDT distributions as a design prior, not as a
biological law. The numbers can suggest bounded runtime margins, but they
should not overwrite the current field state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


@dataclass(frozen=True)
class ProteinPrismPrior:
    protein: str
    accession: str
    total_residues: int
    mean_confidence: float
    solidified_core: float
    active_void: float
    flexible_boundary: float
    transitional_membrane: float
    source_path: str = ""

    @classmethod
    def from_profile_json(cls, path: Path) -> "ProteinPrismPrior":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        summary = data.get("topology_summary") or {}
        residues = data.get("residues") or []
        total = int(summary.get("total_residues") or len(residues) or 0)
        if total <= 0:
            raise ValueError(f"protein prism profile has no residues: {path}")

        counts = {
            "solidified": int(summary.get("solidified_membrane_core_count") or 0),
            "active_void": int(summary.get("active_void_disorder_count") or 0),
            "flexible": int(summary.get("flexible_resonance_boundary_count") or 0),
            "transitional": int(summary.get("transitional_membrane_count") or 0),
        }

        if not any(counts.values()) and residues:
            for residue in residues:
                state = str(residue.get("structural_state") or "").lower()
                if "solidified" in state or "high order" in state:
                    counts["solidified"] += 1
                elif "void" in state or "disorder" in state:
                    counts["active_void"] += 1
                elif "flexible" in state or "medium order" in state:
                    counts["flexible"] += 1
                elif "transitional" in state or "low order" in state:
                    counts["transitional"] += 1

        return cls(
            protein=str(data.get("protein") or "unknown protein"),
            accession=str(data.get("uniprot_accession") or ""),
            total_residues=total,
            mean_confidence=clamp(float(data.get("mean_plddt") or 0.0) / 100.0),
            solidified_core=clamp(counts["solidified"] / total),
            active_void=clamp(counts["active_void"] / total),
            flexible_boundary=clamp(counts["flexible"] / total),
            transitional_membrane=clamp(counts["transitional"] / total),
            source_path=str(Path(path)),
        )

    def as_runtime_tuning(self) -> Dict[str, Any]:
        """
        Convert the profile into small, bounded runtime margins.

        The default resonance field damping gain was 0.3. AQP4-like profiles
        should only breathe around that baseline, not replace the live field.
        """
        damping_gain = 0.24 + (self.solidified_core * 0.12)
        damping_gain += self.flexible_boundary * 0.03
        damping_gain -= self.active_void * 0.04
        hover_margin = (self.flexible_boundary * 0.8) + (self.active_void * 0.2)

        return {
            "protein": self.protein,
            "accession": self.accession,
            "source_path": self.source_path,
            "mean_confidence": round(self.mean_confidence, 6),
            "solidified_core": round(self.solidified_core, 6),
            "active_void": round(self.active_void, 6),
            "flexible_boundary": round(self.flexible_boundary, 6),
            "transitional_membrane": round(self.transitional_membrane, 6),
            "damping_gain": round(clamp(damping_gain, 0.18, 0.42), 6),
            "void_tolerance": round(self.active_void, 6),
            "band_breathing_margin": round(self.flexible_boundary, 6),
            "hover_margin": round(clamp(hover_margin, 0.0, 0.25), 6),
            "epistemic_status": "alphafold_plddt_distribution_as_design_prior_not_biological_law",
        }


def load_first_available(paths: Iterable[Path]) -> Optional[ProteinPrismPrior]:
    for path in paths:
        if not path or not Path(path).exists():
            continue
        try:
            return ProteinPrismPrior.from_profile_json(Path(path))
        except Exception:
            continue
    return None
