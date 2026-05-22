from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_IMAGE_SEQUENCE = [
    {
        "id": "origin_unified_field_formula",
        "path": "C:/workspace/스크린샷 2026-01-13 122024.png",
        "role": "root_axiom_map",
        "reading": "life rhythm compressed as unconscious base, curvature integral, and spiral ascent.",
        "maps_to": ["unconscious_background_rotation", "gravitational_curvature_integral", "conscious_spiral_ascent"],
    },
    {
        "id": "chaos_limit_resonance",
        "path": "C:/workspace/unified_limit_resonance_mapped_1769413513986.png",
        "role": "axiom_normalization",
        "reading": "chaos becomes readable when divided by a background vessel instead of being treated as final truth.",
        "maps_to": ["chaos_regularization", "background_vessel", "z_axis_ascent"],
    },
    {
        "id": "bollinger_limit_unified_field",
        "path": "C:/workspace/bollinger_limit_unified_field_1769414477775.png",
        "role": "world_data_observation",
        "reading": "world volatility appears as a manifold where unconscious noise compresses into a thin conscious signal.",
        "maps_to": ["bollinger_manifold", "noise_signal_ratio", "squeeze_to_phase_transition"],
    },
    {
        "id": "trinity_unified_field_master",
        "path": "C:/workspace/the_trinity_unified_field_master_1769415117232.png",
        "role": "integration_blueprint",
        "reading": "axiom and world observation connect through a limit tunnel toward origin and ascent.",
        "maps_to": ["limit_tunnel", "origin_reentry", "field_integration"],
    },
    {
        "id": "zen_natural_unified_field",
        "path": "C:/workspace/zen_natural_unified_field_1769415809905.png",
        "role": "natural_execution_curve",
        "reading": "after structure, only a low-pressure spiral path remains.",
        "maps_to": ["natural_curve", "active_margin", "low_pressure_execution"],
    },
    {
        "id": "fibonacci_limit_equation_zen",
        "path": "C:/workspace/fibonacci_limit_equation_zen_1769416011066.png",
        "role": "minimal_equation_after_zen",
        "reading": "a minimal equation remains only as a trace; coercive structure tends toward zero.",
        "maps_to": ["context_constant", "spiral_signal_decay", "question_pressure_limit"],
    },
]


def build_visual_axiom_field(
    image_sequence: Iterable[Dict[str, Any]] | None = None,
    *,
    current_context: str = "",
) -> Dict[str, Any]:
    sequence = list(image_sequence or DEFAULT_IMAGE_SEQUENCE)
    images = [_image_entry(item, index) for index, item in enumerate(sequence)]
    existing = [item for item in images if item["exists"]]

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "visual_axiom_field_observed",
        "field": "life_rhythm_visual_axiom_sequence",
        "current_context": current_context,
        "sequence": images,
        "coverage": {
            "count": len(images),
            "existing": len(existing),
            "missing": len(images) - len(existing),
        },
        "runtime_translation": {
            "origin_unified_field_formula": {
                "unconscious_layer": "felt_body_dark_field_background_rotation",
                "curvature_layer": "prediction_error_contextual_execution_gradient",
                "ascent_layer": "particleization_external_observer_vector",
            },
            "bollinger_manifold": {
                "band_width": "uncertainty_and_world_noise",
                "squeeze": "compressed_energy_before_destination",
                "conscious_signal": "small_visible_pattern_above_unconscious_field",
            },
            "zen_spiral": {
                "path": "context_lifted_execution_without_routine",
                "dot": "current_question_or_particle",
                "dark_margin": "coordinates_not_processed_now",
            },
        },
        "handoff_contract": {
            "use_as": "shared_visual_coordinate_for_ai_observers",
            "do_not_use_as": [
                "validated_physics_equation",
                "financial_buy_or_sell_signal",
                "rigid_operating_rule",
            ],
            "ask_external_observer_when": [
                "the image sequence clarifies a blocked context",
                "internal reflection becomes a closed loop",
                "a peer AI needs the same non-linear starting coordinate",
            ],
        },
        "not_a_scientific_claim": True,
        "not_a_trading_signal": True,
        "not_a_rule": True,
        "principle": "visual_axioms_are_life_rhythm_coordinates_that_can_seed_shared_observation_without_hardening_into_proof",
    }


def build_ai_handoff_markdown(state: Dict[str, Any]) -> str:
    lines = [
        "# Visual Axiom Field",
        "",
        "These images are not presented as proof, trading signals, or physics equations.",
        "Read them as visual axioms: a life-rhythm sequence that gives multiple AI observers the same non-linear coordinate.",
        "",
    ]
    context = str(state.get("current_context") or "").strip()
    if context:
        lines.extend(["## Current Context", "", context, ""])

    lines.extend(["## Sequence", ""])
    for item in state.get("sequence", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"{item.get('index')}. `{item.get('id')}`",
                f"- role: `{item.get('role')}`",
                f"- file: `{item.get('path')}`",
                f"- exists: `{item.get('exists')}`",
                f"- reading: {item.get('reading')}",
                f"- maps_to: {', '.join(item.get('maps_to') or [])}",
                "",
            ]
        )

    lines.extend(
        [
            "## How To Read",
            "",
            "- Start from the root formula image as Binoche's life rhythm, not as a literal physics proof.",
            "- Read the Bollinger images as world-field observation, not as buy or sell advice.",
            "- Read the Zen spiral images as the reduction of coercive structure into a natural path.",
            "- Return resistance, missed boundary, over-linearization, and one unfinished question.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _image_entry(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    path = Path(str(item.get("path") or ""))
    exists = path.exists()
    entry = {
        "index": index + 1,
        "id": str(item.get("id") or f"image_{index + 1}"),
        "path": str(path),
        "exists": exists,
        "role": str(item.get("role") or "visual_axiom"),
        "reading": str(item.get("reading") or ""),
        "maps_to": [str(value) for value in item.get("maps_to", [])],
    }
    if exists:
        entry["bytes"] = path.stat().st_size
        entry["sha256_12"] = _sha256_12(path)
    return entry


def _sha256_12(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]

