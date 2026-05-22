from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


def build_trigger_geometry_state(
    *,
    field_trigger_state: Dict[str, Any] | None = None,
    field_heart_state: Dict[str, Any] | None = None,
    natural_boundary_state: Dict[str, Any] | None = None,
    field_reseeding_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    trigger = field_trigger_state or {}
    heart = field_heart_state or {}
    boundary = natural_boundary_state or {}
    reseed = field_reseeding_state or {}

    points = _points(trigger, heart, boundary, reseed)
    edges = _edges(points)
    plane = _plane(points, edges)
    geometry = _geometry_for(points, edges, plane)
    multiparty = _multiparty_for(points, edges, plane, geometry)
    profile = _profile_for(geometry)

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "trigger_geometry",
        "status": "trigger_geometry_observed",
        "points": points,
        "edges": edges,
        "plane": plane,
        "geometry": geometry,
        "multiparty": multiparty,
        "execution_profile": profile,
        "next_contact": {
            "action": profile["action"],
            "meaning": profile["meaning"],
            "speed": profile["speed"],
            "stability": profile["stability"],
            "irreversible_effect": False,
            "external_api_cost": False,
        },
        "contract": {
            "point_convergence_is_fast_but_noise_sensitive": True,
            "line_convergence_requires_two_coherent_points": True,
            "plane_convergence_uses_weighted_quorum_not_all_points": True,
            "multi_party_is_processed_as_primary_dyad_plus_sidebands": True,
            "central_rhythm_is_alignment_reference_not_controller": True,
            "geometry_observes_trigger_shape_without_forcing_execution": True,
        },
        "principle": "trigger_shape_depends_on_how_many_field_points_cohere_before_threshold_crossing; multi_party_relations_fold_to_primary_dyad_plus_loose_central_rhythm",
    }


def _points(
    trigger: Dict[str, Any],
    heart: Dict[str, Any],
    boundary: Dict[str, Any],
    reseed: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    potentials = trigger.get("node_potential") if isinstance(trigger.get("node_potential"), dict) else {}
    thresholds = trigger.get("thresholds") if isinstance(trigger.get("thresholds"), dict) else {}
    heart_filter = heart.get("filter") if isinstance(heart.get("filter"), dict) else {}
    heart_delta = heart.get("echo_delta") if isinstance(heart.get("echo_delta"), dict) else {}
    routing = boundary.get("routing") if isinstance(boundary.get("routing"), dict) else {}
    lineage = reseed.get("lineage") if isinstance(reseed.get("lineage"), dict) else {}
    line_strength = lineage.get("candidate_line_strength") if isinstance(lineage.get("candidate_line_strength"), dict) else {}

    return {
        "sian": _point(
            value=_ratio(potentials.get("sian"), thresholds.get("sian"), default_threshold=0.72),
            role="field_opener",
            basis="field_trigger_state.node_potential.sian",
        ),
        "luvit": _point(
            value=_ratio(potentials.get("luvit"), thresholds.get("luvit"), default_threshold=0.68),
            role="implementation_verifier",
            basis="field_trigger_state.node_potential.luvit",
        ),
        "heart_echo": _point(
            value=_num(heart_filter.get("clean_delta_score"), _num(heart_delta.get("delta_score"), 0.0)) / 0.34,
            role="carrier_echo_delta",
            basis="field_heart.clean_delta_score",
        ),
        "natural_boundary": _point(
            value=max(_num(routing.get("why_pressure"), 0.0), _num(routing.get("new_waypoint_pull"), 0.0)) / 0.38,
            role="resistance_why_router",
            basis="natural_boundary_router.routing",
        ),
        "reseed_lineage": _point(
            value=max((_num(value, 0.0) for value in line_strength.values()), default=0.0),
            role="new_seed_line_strength",
            basis="field_reseeding.lineage.candidate_line_strength",
        ),
    }


def _point(*, value: float, role: str, basis: str) -> Dict[str, Any]:
    strength = _clamp(value)
    return {
        "strength": round(strength, 6),
        "active": strength >= 0.60,
        "role": role,
        "basis": basis,
    }


def _edges(points: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    pairs = {
        "sian_luvit": ("sian", "luvit"),
        "heart_boundary": ("heart_echo", "natural_boundary"),
        "boundary_reseed": ("natural_boundary", "reseed_lineage"),
        "luvit_reseed": ("luvit", "reseed_lineage"),
    }
    edges: Dict[str, Dict[str, Any]] = {}
    for name, (a, b) in pairs.items():
        a_strength = _num(points.get(a, {}).get("strength"), 0.0)
        b_strength = _num(points.get(b, {}).get("strength"), 0.0)
        coherence = (a_strength * b_strength) ** 0.5
        edges[name] = {
            "points": [a, b],
            "coherence": round(coherence, 6),
            "active": coherence >= 0.72,
        }
    return edges


def _plane(points: Dict[str, Dict[str, Any]], edges: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    active_points = [name for name, point in points.items() if point.get("active")]
    active_edges = [name for name, edge in edges.items() if edge.get("active")]
    point_strengths = [_num(point.get("strength"), 0.0) for point in points.values()]
    edge_strengths = [_num(edge.get("coherence"), 0.0) for edge in edges.values()]
    point_mean = sum(point_strengths) / max(1, len(point_strengths))
    edge_mean = sum(edge_strengths) / max(1, len(edge_strengths))
    quorum_score = _clamp(0.62 * point_mean + 0.38 * edge_mean)
    quorum_required = min(3, len(points))
    return {
        "active_points": active_points,
        "active_edges": active_edges,
        "quorum_score": round(quorum_score, 6),
        "quorum_required": quorum_required,
        "active": len(active_points) >= quorum_required and quorum_score >= 0.64,
        "all_points_required": False,
        "meaning": "plane convergence is a weighted surface quorum, not a requirement that every point fire",
    }


def _geometry_for(
    points: Dict[str, Dict[str, Any]],
    edges: Dict[str, Dict[str, Any]],
    plane: Dict[str, Any],
) -> Dict[str, Any]:
    strongest_point = max(points.items(), key=lambda item: _num(item[1].get("strength"), 0.0))
    strongest_edge = max(edges.items(), key=lambda item: _num(item[1].get("coherence"), 0.0))
    if plane.get("active"):
        shape = "plane"
    elif strongest_edge[1].get("active"):
        shape = "line"
    elif strongest_point[1].get("active"):
        shape = "point"
    else:
        shape = "latent"
    return {
        "shape": shape,
        "strongest_point": strongest_point[0],
        "strongest_point_strength": strongest_point[1]["strength"],
        "strongest_edge": strongest_edge[0],
        "strongest_edge_coherence": strongest_edge[1]["coherence"],
        "plane_active": bool(plane.get("active")),
    }


def _multiparty_for(
    points: Dict[str, Dict[str, Any]],
    edges: Dict[str, Dict[str, Any]],
    plane: Dict[str, Any],
    geometry: Dict[str, Any],
) -> Dict[str, Any]:
    strongest_edge_name = geometry["strongest_edge"]
    strongest_edge = edges[strongest_edge_name]
    primary_dyad = strongest_edge["points"]
    central_rhythm = _central_rhythm_for(points, plane)
    sidebands = [
        {
            "node": name,
            "strength": point["strength"],
            "role": point["role"],
            "active": point["active"],
        }
        for name, point in points.items()
        if name not in primary_dyad
    ]
    sideband_pressure = _clamp(
        sum(_num(item["strength"], 0.0) for item in sidebands) / max(1, len(sidebands))
    )
    hub_alignment = _clamp(
        0.46 * _num(plane.get("quorum_score"), 0.0)
        + 0.34 * _num(strongest_edge.get("coherence"), 0.0)
        + 0.20 * (1.0 - abs(sideband_pressure - _num(strongest_edge.get("coherence"), 0.0)))
    )
    return {
        "mode": (
            "loose_resonance_around_central_rhythm"
            if geometry["shape"] in {"line", "plane"}
            else "single_vertex_or_latent"
        ),
        "primary_dyad": {
            "edge": strongest_edge_name,
            "nodes": primary_dyad,
            "coherence": strongest_edge["coherence"],
            "meaning": "process_the_strongest_pair_first_to_avoid_multi_party_chaos",
        },
        "central_rhythm": central_rhythm,
        "sideband_nodes": sidebands,
        "sideband_pressure": round(sideband_pressure, 6),
        "hub_alignment": round(hub_alignment, 6),
        "processing_order": _processing_order(primary_dyad, central_rhythm, sidebands),
        "principle": "multi_party_field_is_stabilized_by_pairwise_bonds_around_a_loose_central_rhythm_not_total_mutual_lock",
    }


def _central_rhythm_for(points: Dict[str, Dict[str, Any]], plane: Dict[str, Any]) -> Dict[str, Any]:
    heart = points.get("heart_echo", {})
    natural = points.get("natural_boundary", {})
    reseed = points.get("reseed_lineage", {})
    observer_strength = _clamp(
        0.36 * _num(plane.get("quorum_score"), 0.0)
        + 0.24 * _num(heart.get("strength"), 0.0)
        + 0.22 * _num(natural.get("strength"), 0.0)
        + 0.18 * _num(reseed.get("strength"), 0.0)
    )
    return {
        "node": "binoche_observer_field",
        "supporting_nodes": ["field_heart", "natural_boundary", "reseed_lineage"],
        "strength": round(observer_strength, 6),
        "role": "loose_hub_rhythm",
        "meaning": "keeps_pairwise_relations_comfortable_without_controlling_every_node",
    }


def _processing_order(
    primary_dyad: List[str],
    central_rhythm: Dict[str, Any],
    sidebands: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    ordered = [
        {
            "step": "primary_dyad",
            "nodes": primary_dyad,
            "purpose": "stabilize_the_strongest_pair_first",
        },
        {
            "step": "central_rhythm",
            "nodes": [central_rhythm["node"]],
            "purpose": "align_with_observer_hub_without_turning_it_into_control",
        },
    ]
    active_sidebands = [item["node"] for item in sidebands if item.get("active")]
    if active_sidebands:
        ordered.append(
            {
                "step": "sideband_quorum",
                "nodes": active_sidebands,
                "purpose": "expand_to_surface_only_when_sideband_pressure_crosses_threshold",
            }
        )
    return ordered


def _profile_for(geometry: Dict[str, Any]) -> Dict[str, Any]:
    shape = geometry["shape"]
    profiles = {
        "latent": {
            "action": "keep_latent_no_trigger_shape",
            "meaning": "No point, line, or plane has enough coherence to shape a trigger.",
            "speed": "none",
            "stability": "latent",
            "noise_risk": "low",
        },
        "point": {
            "action": "fast_point_trigger_with_noise_check",
            "meaning": "One vertex is strong enough for fast execution, but it needs noise filtering.",
            "speed": "fast",
            "stability": "low_to_medium",
            "noise_risk": "high",
        },
        "line": {
            "action": "paired_line_trigger",
            "meaning": "Two coherent points form a line trigger; slower than point, more stable.",
            "speed": "medium",
            "stability": "medium",
            "noise_risk": "medium",
        },
        "plane": {
            "action": "surface_quorum_trigger",
            "meaning": "Several points form a surface quorum; slowest, most stable, no need for every point to fire.",
            "speed": "slow",
            "stability": "high",
            "noise_risk": "low",
        },
    }
    return profiles[shape]


def _ratio(value: Any, threshold: Any, *, default_threshold: float) -> float:
    denom = _num(threshold, default_threshold)
    if denom <= 0:
        denom = default_threshold
    return _num(value, 0.0) / denom


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
