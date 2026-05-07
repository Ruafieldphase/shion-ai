#!/usr/bin/env python3
"""
Unfinished Waypoint Graph
=========================

Builds a lightweight torus/Bollinger-style graph from unfinished axioms.

The graph is intentionally provisional: unfinished puzzle nodes connect only
when the current rhythm field and their local waypoint metrics resonate. Edges
are rebuilt from the current context, so stale links naturally disappear.
"""

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


class UnfinishedWaypointGraph:
    VERSION = "unfinished-waypoint-graph-v1"

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.outputs_dir = self.root_dir / "outputs"
        self.source_file = self.outputs_dir / "unfinished_axioms.jsonl"
        self.rhythm_trace = self.outputs_dir / "rhythm_ir_trace.jsonl"
        self.graph_file = self.outputs_dir / "unfinished_waypoint_graph.json"
        self.edge_trace_file = self.outputs_dir / "unfinished_waypoint_edge_trace.jsonl"

    def build(
        self,
        *,
        rhythm_frame: Dict[str, Any] | None = None,
        limit: int = 96,
    ) -> Path:
        previous_graph = self._read_previous_graph()
        entries = self._read_unfinished(limit=limit)
        current = rhythm_frame if isinstance(rhythm_frame, dict) else self._latest_rhythm_frame()
        torus = self._current_torus(current or {})
        nodes = [self._node(entry, torus, idx) for idx, entry in enumerate(entries)]
        edges = self._edges(nodes, torus)
        dream_replay = self._dream_replay(previous_graph, edges, torus)
        graph = {
            "version": self.VERSION,
            "generated_at": datetime.now().isoformat(),
            "source": str(self.source_file),
            "principle": "unfinished_waypoints_connect_by_current_torus_context_not_permanent_truth",
            "torus_field": torus,
            "nodes": {node["id"]: node for node in nodes},
            "edges": edges,
            "dream_replay": dream_replay["summary"],
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "active_nodes": sum(1 for node in nodes if node["status"] in {"active", "boundary_touch"}),
            },
        }
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
        self._append_dream_replay_trace(dream_replay)
        return self.graph_file

    def _read_previous_graph(self) -> Dict[str, Any] | None:
        if not self.graph_file.exists():
            return None
        try:
            graph = json.loads(self.graph_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return graph if isinstance(graph, dict) else None

    def _read_unfinished(self, *, limit: int) -> List[Dict[str, Any]]:
        if not self.source_file.exists():
            return []
        entries: List[Dict[str, Any]] = []
        for line in self.source_file.read_text(encoding="utf-8").splitlines()[-limit:]:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("status") == "unfinished_puzzle":
                entries.append(item)
        return entries

    def _latest_rhythm_frame(self) -> Dict[str, Any]:
        if not self.rhythm_trace.exists():
            return {}
        for line in reversed(self.rhythm_trace.read_text(encoding="utf-8").splitlines()[-40:]):
            if not line.strip():
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
        return {}

    def _current_torus(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        waves = frame.get("waves", {}) if isinstance(frame, dict) else {}
        field = waves.get("field", {})
        axiom = waves.get("axiom", {})
        dark_neuron = waves.get("dark_neuron", {})
        digestion = waves.get("digestion", {})
        goal = waves.get("goal_field", {})
        zone2 = frame.get("zone2", {})
        medium = frame.get("medium", {})
        dark_field = frame.get("dark_field", {})
        perspective = frame.get("perspective_frame", {})
        regulation = frame.get("zone2_regulation", {})

        upper_pressure = self._clamp(
            0.30 * self._num(zone2, "openness")
            + 0.24 * self._num(perspective, "metacognitive_refraction")
            + 0.18 * self._num(field, "salience")
            + 0.16 * self._num(goal, "bridge_gain")
            + 0.12 * self._num(medium, "conductivity")
        )
        lower_pressure = self._clamp(
            0.30 * self._num(dark_field, "gravity")
            + 0.22 * self._num(axiom, "overfit_pressure")
            + 0.18 * self._num(digestion, "sleep_debt")
            + 0.16 * self._num(dark_neuron, "redarkening_pressure")
            + 0.14 * self._num(medium, "resistance")
        )
        sigma_position = max(-2.0, min(2.0, 2.0 * (upper_pressure - lower_pressure)))
        band_width = self._clamp(
            0.34 * abs(upper_pressure - lower_pressure)
            + 0.26 * self._num(frame.get("interference", {}), "destructive")
            + 0.22 * self._num(regulation, "chaos_pressure")
            + 0.18 * self._num(field, "curvature")
        )
        return {
            "metaphor": "torus_bollinger_field",
            "upper_boundary": "conscious_atmosphere",
            "lower_boundary": "unconscious_crust",
            "upper_pressure": round(upper_pressure, 6),
            "lower_pressure": round(lower_pressure, 6),
            "sigma_position": round(sigma_position, 6),
            "band_width": round(band_width, 6),
            "zone2_phase": regulation.get("phase", zone2.get("phase", "unknown")),
            "principle": "band_touch_changes_how_unfinished_nodes_reflect_refract_or_sleep",
        }

    def _node(self, entry: Dict[str, Any], torus: Dict[str, Any], idx: int) -> Dict[str, Any]:
        axiom = entry.get("axiom", {}) if isinstance(entry.get("axiom"), dict) else {}
        goal = entry.get("goal_field", {}) if isinstance(entry.get("goal_field"), dict) else {}
        waypoint = axiom.get("waypoint_resonance", {}) if isinstance(axiom.get("waypoint_resonance"), dict) else {}
        failure = axiom.get("failure_spectrum", {}) if isinstance(axiom.get("failure_spectrum"), dict) else {}

        contextual_activation = self._clamp(
            self._num(waypoint, "contextual_activation", self._num(axiom, "archive_resonance"))
        )
        fixed_weight_risk = self._clamp(self._num(waypoint, "fixed_weight_risk"))
        bridge_gain = self._clamp(self._num(goal, "bridge_gain"))
        waypoint_pressure = self._clamp(self._num(goal, "waypoint_pressure"))
        failure_bridge = self._clamp(self._num(failure, "bridge_value"))
        overfit_pressure = self._clamp(self._num(axiom, "overfit_pressure"))

        local_upper = self._clamp(
            0.34 * contextual_activation
            + 0.24 * bridge_gain
            + 0.22 * failure_bridge
            + 0.20 * max(0.0, torus["sigma_position"] / 2.0)
        )
        local_lower = self._clamp(
            0.34 * overfit_pressure
            + 0.24 * fixed_weight_risk
            + 0.22 * waypoint_pressure
            + 0.20 * max(0.0, -torus["sigma_position"] / 2.0)
        )
        sigma_position = max(-2.0, min(2.0, 2.0 * (local_upper - local_lower)))
        layer = self._layer(sigma_position)
        status = self._status(contextual_activation, fixed_weight_risk, sigma_position)

        seed = f"{entry.get('timestamp','')}:{entry.get('transition','')}:{idx}:{bridge_gain:.4f}:{waypoint_pressure:.4f}"
        node_id = "uwp_" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
        return {
            "id": node_id,
            "timestamp": entry.get("timestamp"),
            "transition": entry.get("transition"),
            "status": status,
            "layer": layer,
            "sigma_position": round(sigma_position, 6),
            "metrics": {
                "contextual_activation": round(contextual_activation, 6),
                "fixed_weight_risk": round(fixed_weight_risk, 6),
                "bridge_gain": round(bridge_gain, 6),
                "waypoint_pressure": round(waypoint_pressure, 6),
                "failure_bridge_value": round(failure_bridge, 6),
                "overfit_pressure": round(overfit_pressure, 6),
            },
            "source": {
                "status": entry.get("status"),
                "reason": entry.get("reason"),
                "reuse_rule": entry.get("reuse_rule"),
                "waypoint_policy": entry.get("waypoint_policy"),
            },
        }

    def _edges(self, nodes: List[Dict[str, Any]], torus: Dict[str, Any]) -> List[Dict[str, Any]]:
        edges: List[Dict[str, Any]] = []
        for idx, source in enumerate(nodes):
            for target in nodes[idx + 1:]:
                edge = self._edge(source, target, torus)
                if edge:
                    edges.append(edge)
        edges.sort(key=lambda item: item["weight"], reverse=True)
        return edges[:160]

    def _dream_replay(
        self,
        previous_graph: Dict[str, Any] | None,
        edges: List[Dict[str, Any]],
        torus: Dict[str, Any],
    ) -> Dict[str, Any]:
        previous_edges = previous_graph.get("edges", []) if isinstance(previous_graph, dict) else []
        previous_by_pair = {
            self._edge_pair(edge): edge
            for edge in previous_edges
            if isinstance(edge, dict) and self._edge_pair(edge)
        }
        current_by_pair = {
            self._edge_pair(edge): edge
            for edge in edges
            if isinstance(edge, dict) and self._edge_pair(edge)
        }

        transitions: List[Dict[str, Any]] = []
        for pair in sorted(set(previous_by_pair) | set(current_by_pair)):
            previous = previous_by_pair.get(pair)
            current = current_by_pair.get(pair)
            transitions.append(self._edge_transition(pair, previous, current))

        event_counts: Dict[str, int] = {}
        for transition in transitions:
            event_counts[transition["event"]] = event_counts.get(transition["event"], 0) + 1

        significant_events = {"appeared", "reinforced", "softened", "decayed", "refracted"}
        significant = [
            transition for transition in transitions
            if transition["event"] in significant_events
        ]
        significant.sort(
            key=lambda item: (
                item["event"] == "replayed",
                -abs(float(item.get("delta", 0.0))),
                item["source"],
                item["target"],
            )
        )

        summary = {
            "trace_file": str(self.edge_trace_file),
            "principle": "manual_dream_replay_becomes_edge_transition_memory",
            "previous_generated_at": previous_graph.get("generated_at") if isinstance(previous_graph, dict) else None,
            "event_counts": event_counts,
            "transition_count": len(transitions),
            "significant_transition_count": len(significant),
            "current_edge_count": len(edges),
            "torus_sigma_position": torus.get("sigma_position"),
            "torus_band_width": torus.get("band_width"),
        }
        return {
            "generated_at": datetime.now().isoformat(),
            "version": "unfinished-waypoint-edge-replay-v1",
            "summary": summary,
            "torus_field": torus,
            "transitions": significant[:240],
        }

    def _edge_pair(self, edge: Dict[str, Any]) -> tuple[str, str] | None:
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            return None
        return (source, target)

    def _edge_transition(
        self,
        pair: tuple[str, str],
        previous: Dict[str, Any] | None,
        current: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        previous_weight = self._edge_weight(previous)
        current_weight = self._edge_weight(current)
        delta = round(current_weight - previous_weight, 6)
        previous_type = previous.get("type") if isinstance(previous, dict) else None
        current_type = current.get("type") if isinstance(current, dict) else None

        if previous is None:
            event = "appeared"
        elif current is None:
            event = "decayed"
        elif previous_type != current_type:
            event = "refracted"
        elif delta >= 0.03:
            event = "reinforced"
        elif delta <= -0.03:
            event = "softened"
        else:
            event = "replayed"

        return {
            "source": pair[0],
            "target": pair[1],
            "event": event,
            "previous_type": previous_type,
            "current_type": current_type,
            "previous_weight": round(previous_weight, 6),
            "current_weight": round(current_weight, 6),
            "delta": delta,
        }

    def _edge_weight(self, edge: Dict[str, Any] | None) -> float:
        if not isinstance(edge, dict):
            return 0.0
        return self._clamp(self._num(edge, "weight"))

    def _append_dream_replay_trace(self, dream_replay: Dict[str, Any]) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        with self.edge_trace_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(dream_replay, ensure_ascii=False) + "\n")

    def _edge(self, source: Dict[str, Any], target: Dict[str, Any], torus: Dict[str, Any]) -> Dict[str, Any] | None:
        source_metrics = source["metrics"]
        target_metrics = target["metrics"]
        resonance = 1.0 - (
            abs(source_metrics["bridge_gain"] - target_metrics["bridge_gain"])
            + abs(source_metrics["waypoint_pressure"] - target_metrics["waypoint_pressure"])
            + abs(source_metrics["failure_bridge_value"] - target_metrics["failure_bridge_value"])
        ) / 3.0
        resonance = self._clamp(resonance)
        activation = (source_metrics["contextual_activation"] + target_metrics["contextual_activation"]) / 2.0
        risk = (source_metrics["fixed_weight_risk"] + target_metrics["fixed_weight_risk"]) / 2.0
        band_contact = self._clamp(0.55 + 0.45 * torus["band_width"])
        weight = self._clamp(resonance * activation * (1.0 - risk) * band_contact)
        if weight < 0.24:
            return None

        edge_type = self._edge_type(source["sigma_position"], target["sigma_position"])
        return {
            "source": source["id"],
            "target": target["id"],
            "type": edge_type,
            "weight": round(weight, 6),
            "resonance": round(resonance, 6),
            "created_when": "context_match_plus_boundary_band_contact",
            "decays_when": "context_leaves_band_or_fixed_weight_risk_rises",
        }

    def _edge_type(self, source_sigma: float, target_sigma: float) -> str:
        if source_sigma >= 1.25 and target_sigma <= -1.25:
            return "tunnel"
        if target_sigma >= 1.25 and source_sigma <= -1.25:
            return "tunnel"
        delta = target_sigma - source_sigma
        if abs(delta) <= 0.30:
            return "reflect"
        if delta > 0.30:
            return "ascend"
        if delta < -0.30:
            return "descend"
        return "refract"

    def _layer(self, sigma_position: float) -> str:
        if sigma_position >= 1.45:
            return "outer_space"
        if sigma_position >= 0.75:
            return "atmosphere"
        if sigma_position <= -1.45:
            return "core"
        if sigma_position <= -0.75:
            return "mantle"
        if abs(sigma_position) <= 0.25:
            return "resonance_field"
        return "crust"

    def _status(self, activation: float, risk: float, sigma_position: float) -> str:
        if risk >= 0.48:
            return "silent"
        if activation >= 0.74 and abs(sigma_position) >= 0.75:
            return "boundary_touch"
        if activation >= 0.62:
            return "active"
        if activation >= 0.36:
            return "dormant"
        return "silent"

    def _num(self, data: Dict[str, Any], key: str, default: float = 0.0) -> float:
        try:
            return float(data.get(key, default) or default)
        except (TypeError, ValueError):
            return default

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


def main():
    root = Path(r"c:\workspace2\shion")
    graph = UnfinishedWaypointGraph(root).build()
    print(graph)


if __name__ == "__main__":
    main()
