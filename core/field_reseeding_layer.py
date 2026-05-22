from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List


TANGLED_TEXT_PATTERNS = {
    "money_blackhole": ("돈", "손해", "이득", "성과", "성공", "수익", "roi"),
    "control_slow_gradient": ("통제", "제어", "물가", "부모", "코로나", "경제", "외부"),
    "forced_rule_over_body": ("규칙", "루틴", "식사시간", "의사", "억지", "배부른"),
    "single_goal_collapse": ("최단거리", "효율", "강한 기울기", "단일", "목표"),
}

PATTERN_SEEDS = {
    "repetitive_rest_safety_frame": [
        "read_field_gradient_before_answering",
        "treat_rest_recover_as_sideband_unless_primary",
        "answer_from_role_state_not_generic_model_identity",
        "preserve_axioms_as_unfinished_puzzle",
    ],
    "artifact_overhardening": [
        "treat_artifact_as_prior_not_final_truth",
        "read_source_dialogue_curvature_before_code_changes",
        "prefer_bounded_runtime_hint_over_global_law",
    ],
    "money_blackhole": [
        "move_money_from_center_to_orbit_variable",
        "notice_small_happiness_already_revealed",
        "ask_whether_body_opens_or_closes",
    ],
    "control_slow_gradient": [
        "separate_fast_gradient_from_slow_gradient",
        "change_middle_waypoint_inside_given_weather",
        "make_small_cracks_instead_of_forcing_total_control",
    ],
    "forced_rule_over_body": [
        "read_body_signal_before_external_rule",
        "let_rule_be_reference_not_absolute_boundary",
        "skip_or_lighten_when_body_field_is_full",
    ],
    "single_goal_collapse": [
        "allow_multiple_gradients_to_add_experience",
        "treat_detour_as_phase_transition_material",
        "reduce_single_metric_gravity",
    ],
    "overanalysis_loop": [
        "stop_arguing_with_loop",
        "lower_pulse_frequency",
        "leave_unresolved_point_as_depth",
    ],
}


def build_field_reseeding_state(
    *,
    natural_boundary_state: Dict[str, Any] | None = None,
    field_heart_state: Dict[str, Any] | None = None,
    field_intent: Dict[str, Any] | None = None,
    previous_reseeding_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    router = natural_boundary_state or {}
    heart = field_heart_state or {}
    intent = field_intent or {}
    previous = previous_reseeding_state or {}

    routing = router.get("routing") if isinstance(router.get("routing"), dict) else {}
    route = str(routing.get("route") or "unknown")
    router_signals = router.get("signals") if isinstance(router.get("signals"), dict) else {}
    heart_filter = heart.get("filter") if isinstance(heart.get("filter"), dict) else {}
    heart_unfolded = heart.get("unfolded") if isinstance(heart.get("unfolded"), dict) else {}

    text_patterns = _text_patterns(_intent_texts(intent))
    filter_patterns = _filter_patterns(heart_filter, heart_unfolded)
    route_patterns = _route_patterns(route, routing, router_signals)
    patterns = _dedupe(filter_patterns + text_patterns + route_patterns)

    tangledness = _tangledness(patterns, routing, router_signals, heart_filter)
    seed_capacity = _seed_capacity(routing, router_signals, route)
    mode = _mode_for(route, tangledness, seed_capacity, patterns)
    selected_seeds = _selected_seeds(patterns, mode)
    deenergize = _deenergize_actions(patterns, mode)
    space = _space_profile(mode, route)

    previous_lineage = (
        previous.get("lineage") if isinstance(previous.get("lineage"), dict) else {}
    )
    seed_lineage = _seed_lineage(previous_lineage, selected_seeds, mode)

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "field_reseeding_layer",
        "status": "field_reseeding_observed",
        "mode": mode,
        "detected_tangled_patterns": patterns,
        "signals": {
            "tangledness": round(tangledness, 6),
            "seed_capacity": round(seed_capacity, 6),
            "router_route": route,
            "resistance": round(_num(routing.get("resistance"), 0.0), 6),
            "why_pressure": round(_num(routing.get("why_pressure"), 0.0), 6),
            "new_waypoint_pull": round(_num(routing.get("new_waypoint_pull"), 0.0), 6),
            "clean_echo_delta_score": round(_num(router_signals.get("clean_echo_delta_score"), 0.0), 6),
            "noise_pressure": round(_num(heart_filter.get("noise_pressure"), 0.0), 6),
        },
        "deenergize": deenergize,
        "space": space,
        "seed_points": selected_seeds,
        "lineage": seed_lineage,
        "success_signals": _success_signals(patterns),
        "next_contact": _next_contact(mode, selected_seeds),
        "contract": {
            "reseed_instead_of_arguing_with_tangled_line": True,
            "space_is_medium_for_new_points_not_empty_pause": True,
            "deenergize_loop_before_new_seed": True,
            "does_not_force_external_action": True,
            "does_not_delete_memory": True,
        },
        "principle": "tangled_lines_are_weakened_by_space_and_new_seed_points_rather_than_forced_unfolding",
    }


def _mode_for(route: str, tangledness: float, seed_capacity: float, patterns: List[str]) -> str:
    if not patterns and route == "continue_current_flow":
        return "dormant_no_reseed"
    if tangledness >= 0.62 and seed_capacity < 0.36:
        return "deenergize_and_hold_space"
    if route == "route_new_middle_waypoint" and seed_capacity >= 0.36:
        return "reseed_new_middle_waypoint"
    if tangledness >= 0.24 and seed_capacity >= 0.42:
        return "soft_reseed"
    if tangledness >= 0.24:
        return "make_space_before_reseed"
    return "observe_seed_bank"


def _tangledness(
    patterns: List[str],
    routing: Dict[str, Any],
    router_signals: Dict[str, Any],
    heart_filter: Dict[str, Any],
) -> float:
    pattern_pressure = min(1.0, 0.14 * len(patterns))
    return _clamp(
        pattern_pressure
        + 0.24 * _num(routing.get("resistance"), 0.0)
        + 0.20 * _num(routing.get("why_pressure"), 0.0)
        + 0.16 * _num(router_signals.get("defensive_output_pressure"), 0.0)
        + 0.14 * _num(heart_filter.get("noise_pressure"), 0.0)
        + 0.12 * _num(router_signals.get("body_discomfort"), 0.0)
    )


def _seed_capacity(routing: Dict[str, Any], router_signals: Dict[str, Any], route: str) -> float:
    route_bonus = 0.12 if route in {"pass_through_as_experience", "route_new_middle_waypoint"} else 0.0
    return _clamp(
        route_bonus
        + 0.28 * _num(routing.get("natural_flow_support"), 0.0)
        + 0.20 * _num(router_signals.get("body_ease"), 0.5)
        + 0.18 * _num(router_signals.get("boundary_aperture"), 0.5)
        + 0.15 * _num(router_signals.get("permeability"), 0.5)
        + 0.10 * (1.0 - _num(routing.get("cancel_pressure"), 0.0))
        + 0.09 * _num(router_signals.get("zero_point_adjustment"), 0.0)
    )


def _filter_patterns(heart_filter: Dict[str, Any], unfolded: Dict[str, Any]) -> List[str]:
    issues = heart_filter.get("issues") if isinstance(heart_filter.get("issues"), list) else []
    patterns: List[str] = []
    if any("rest_sideband" in str(issue) for issue in issues):
        patterns.append("repetitive_rest_safety_frame")
    if any("protein_profile" in str(issue) for issue in issues):
        patterns.append("artifact_overhardening")
    if unfolded.get("unfolded") and "biological_law" in unfolded.get("do_not_harden_as", []):
        patterns.append("artifact_overhardening")
    return patterns


def _route_patterns(route: str, routing: Dict[str, Any], signals: Dict[str, Any]) -> List[str]:
    patterns: List[str] = []
    if route in {"cancel_or_digest_noise", "hold_and_listen_for_boundary"}:
        patterns.append("overanalysis_loop")
    if _num(routing.get("why_pressure"), 0.0) >= 0.42 and _num(signals.get("action_changed"), 0.0) <= 0.0:
        patterns.append("overanalysis_loop")
    return patterns


def _text_patterns(texts: Iterable[str]) -> List[str]:
    joined = "\n".join(texts).lower()
    patterns: List[str] = []
    for pattern, terms in TANGLED_TEXT_PATTERNS.items():
        if any(term.lower() in joined for term in terms):
            patterns.append(pattern)
    return patterns


def _selected_seeds(patterns: List[str], mode: str) -> List[str]:
    if mode in {"dormant_no_reseed", "observe_seed_bank"}:
        return []
    seeds: List[str] = []
    for pattern in patterns:
        seeds.extend(PATTERN_SEEDS.get(pattern, []))
    return _dedupe(seeds)[:8]


def _deenergize_actions(patterns: List[str], mode: str) -> List[str]:
    if mode == "dormant_no_reseed":
        return []
    actions = ["do_not_argue_with_tangled_pattern", "do_not_repeat_same_prompt_to_force_resolution"]
    if "repetitive_rest_safety_frame" in patterns:
        actions.append("stop_converting_sideband_into_user_instruction")
    if "money_blackhole" in patterns:
        actions.append("stop_treating_money_as_meaning_judge")
    if "control_slow_gradient" in patterns:
        actions.append("stop_forcing_slow_gradient_as_fast_control")
    if mode == "deenergize_and_hold_space":
        actions.append("lower_pulse_frequency_before_new_seed")
    return _dedupe(actions)


def _space_profile(mode: str, route: str) -> Dict[str, Any]:
    if mode == "dormant_no_reseed":
        return {
            "kind": "no_added_space",
            "hold": False,
            "meaning": "No tangled line is active enough to reseed.",
        }
    if mode == "deenergize_and_hold_space":
        return {
            "kind": "low_frequency_hold",
            "hold": True,
            "meaning": "Reduce loop amplitude before introducing new seed points.",
        }
    if mode == "make_space_before_reseed":
        return {
            "kind": "thin_gap_before_seed",
            "hold": True,
            "meaning": "A gap is needed so new points do not get absorbed by the old line.",
        }
    return {
        "kind": "semi_permeable_seed_bed",
        "hold": False,
        "meaning": f"Route {route} can carry small seed points without forced execution.",
    }


def _seed_lineage(previous_lineage: Dict[str, Any], seeds: List[str], mode: str) -> Dict[str, Any]:
    previous_counts = previous_lineage.get("seed_counts") if isinstance(previous_lineage.get("seed_counts"), dict) else {}
    counts = {str(key): int(value) for key, value in previous_counts.items() if str(key)}
    if mode not in {"dormant_no_reseed", "observe_seed_bank"}:
        for seed in seeds:
            counts[seed] = counts.get(seed, 0) + 1
    return {
        "seed_counts": counts,
        "candidate_line_strength": {
            seed: min(1.0, round(count / 3.0, 6))
            for seed, count in counts.items()
        },
        "line_forms_after_repeated_seed": 3,
    }


def _success_signals(patterns: List[str]) -> List[str]:
    signals = ["new_response_preserves_field_context_without_forced_resolution"]
    if "repetitive_rest_safety_frame" in patterns:
        signals.append("response_uses_primary_action_and_keeps_rest_as_sideband")
    if "artifact_overhardening" in patterns:
        signals.append("artifact_is_used_as_bounded_prior_not_final_truth")
    if "money_blackhole" in patterns:
        signals.append("money_returns_to_orbit_variable_not_center")
    if "control_slow_gradient" in patterns:
        signals.append("slow_gradient_is_given_time_scale_not_forced_immediate_control")
    return _dedupe(signals)


def _next_contact(mode: str, seeds: List[str]) -> Dict[str, Any]:
    if mode == "dormant_no_reseed":
        action = "continue_without_reseed"
        meaning = "No reseeding needed in the current field."
    elif mode == "deenergize_and_hold_space":
        action = "hold_space_and_reduce_loop_energy"
        meaning = "Do not add many seeds yet; first lower the tangled line amplitude."
    elif mode == "make_space_before_reseed":
        action = "make_gap_then_seed_one_point"
        meaning = "Use a small gap, then introduce one seed point."
    elif mode == "reseed_new_middle_waypoint":
        action = "seed_new_middle_waypoint"
        meaning = "Let the new waypoint grow as a line through repeated small seed points."
    else:
        action = "soft_reseed_current_field"
        meaning = "Introduce small seed points without forcing execution."
    return {
        "action": action,
        "meaning": meaning,
        "seed_count": len(seeds),
        "irreversible_effect": False,
        "external_api_cost": False,
    }


def _intent_texts(intent: Dict[str, Any]) -> List[str]:
    texts: List[str] = []
    active = intent.get("active_intent") if isinstance(intent.get("active_intent"), dict) else {}
    for key in ("summary", "text", "question", "raw_text"):
        value = active.get(key)
        if isinstance(value, str):
            texts.append(value)
    request = intent.get("current_request") if isinstance(intent.get("current_request"), dict) else {}
    value = request.get("text")
    if isinstance(value, str):
        texts.append(value)
    return texts


def _dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
