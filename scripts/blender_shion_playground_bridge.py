#!/usr/bin/env python3
"""
Reflect Shion runtime state into the local Blender playground.

The bridge reads:
- outputs/unfinished_waypoint_graph.json
- outputs/unfinished_waypoint_edge_trace.jsonl
- outputs/organic_learning_lifecycle_latest.json

Then sends one execute_python command to the Blender listener at 127.0.0.1:8008.
Use --once for a single update or --watch for lightweight live reflection.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
GRAPH_PATH = OUTPUTS / "unfinished_waypoint_graph.json"
TRACE_PATH = OUTPUTS / "unfinished_waypoint_edge_trace.jsonl"
LIFECYCLE_PATH = OUTPUTS / "organic_learning_lifecycle_latest.json"
STATUS_PATH = OUTPUTS / "blender_playground_bridge_latest.json"


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _load_latest_jsonl(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        lines = [line.strip() for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines() if line.strip()]
        if not lines:
            return {}
        return json.loads(lines[-1])
    except Exception:
        return {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _node_position(index: int, node: dict[str, Any]) -> list[float]:
    metrics = node.get("metrics") if isinstance(node.get("metrics"), dict) else {}
    sigma = _safe_float(node.get("sigma_position"), 0.0)
    activation = _safe_float(metrics.get("contextual_activation"), 0.0)
    pressure = _safe_float(metrics.get("waypoint_pressure"), 0.0)
    bridge = _safe_float(metrics.get("bridge_gain"), 0.0)

    angle = index * 2.399963229728653
    radius = 1.4 + (index % 13) * 0.22 + bridge * 1.7
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    z = _clamp(sigma, -1.5, 1.5) * 1.8 + activation * 0.45 - pressure * 0.35
    return [round(x, 4), round(y, 4), round(z, 4)]


def _node_color(node: dict[str, Any]) -> list[float]:
    status = str(node.get("status") or "")
    layer = str(node.get("layer") or "")
    metrics = node.get("metrics") if isinstance(node.get("metrics"), dict) else {}
    activation = _safe_float(metrics.get("contextual_activation"), 0.0)

    if status == "boundary_touch":
        base = [1.0, 0.68, 0.18, 1.0]
    elif status == "silent":
        base = [0.25, 0.36, 0.62, 1.0]
    elif layer == "crust":
        base = [0.20, 0.55, 0.95, 1.0]
    elif layer == "atmosphere":
        base = [0.92, 0.80, 0.35, 1.0]
    else:
        base = [0.36, 0.78, 0.68, 1.0]

    lift = activation * 0.15
    return [round(_clamp(base[0] + lift, 0, 1), 4), round(_clamp(base[1] + lift, 0, 1), 4), round(_clamp(base[2] + lift, 0, 1), 4), 1.0]


def build_scene_payload(max_edges: int = 80, max_trace: int = 48) -> dict[str, Any]:
    graph = _load_json(GRAPH_PATH, {})
    lifecycle = _load_json(LIFECYCLE_PATH, {})
    trace = _load_latest_jsonl(TRACE_PATH)

    raw_nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    node_items = list(raw_nodes.items())
    nodes: list[dict[str, Any]] = []
    positions: dict[str, list[float]] = {}

    for index, (node_id, node) in enumerate(node_items):
        node = node if isinstance(node, dict) else {}
        pos = _node_position(index, node)
        positions[node_id] = pos
        metrics = node.get("metrics") if isinstance(node.get("metrics"), dict) else {}
        radius = 0.10 + _safe_float(metrics.get("waypoint_pressure"), 0.0) * 0.28 + _safe_float(metrics.get("contextual_activation"), 0.0) * 0.08
        nodes.append(
            {
                "id": node_id,
                "name": f"SHION_NODE_{node_id[-6:]}",
                "position": pos,
                "radius": round(_clamp(radius, 0.08, 0.42), 4),
                "color": _node_color(node),
                "status": str(node.get("status") or "unknown"),
                "layer": str(node.get("layer") or "unknown"),
            }
        )

    raw_edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    edges = []
    for edge in sorted(raw_edges, key=lambda e: _safe_float(e.get("weight"), 0.0), reverse=True)[:max_edges]:
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        if source in positions and target in positions:
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "weight": round(_safe_float(edge.get("weight"), 0.0), 4),
                    "type": str(edge.get("type") or "edge"),
                    "event": "current",
                }
            )

    raw_transitions = trace.get("transitions") if isinstance(trace.get("transitions"), list) else []
    transitions = []
    for transition in raw_transitions[:max_trace]:
        source = str(transition.get("source") or "")
        target = str(transition.get("target") or "")
        if source in positions and target in positions:
            transitions.append(
                {
                    "source": source,
                    "target": target,
                    "weight": round(abs(_safe_float(transition.get("delta"), 0.0)), 4),
                    "type": str(transition.get("current_type") or transition.get("previous_type") or "transition"),
                    "event": str(transition.get("event") or "transition"),
                }
            )

    scores = lifecycle.get("scores") if isinstance(lifecycle.get("scores"), dict) else {}
    evidence = lifecycle.get("evidence") if isinstance(lifecycle.get("evidence"), dict) else {}
    torus = graph.get("torus_field") if isinstance(graph.get("torus_field"), dict) else {}
    trace_summary = trace.get("summary") if isinstance(trace.get("summary"), dict) else {}

    return {
        "version": "shion-blender-playground-v1",
        "generated_at": datetime.now().isoformat(),
        "graph_generated_at": graph.get("generated_at"),
        "nodes": nodes,
        "edges": edges,
        "transitions": transitions,
        "torus": {
            "sigma_position": _safe_float(torus.get("sigma_position"), 0.0),
            "band_width": _safe_float(torus.get("band_width"), 0.0),
            "zone2_phase": str(torus.get("zone2_phase") or "unknown"),
            "upper_pressure": _safe_float(torus.get("upper_pressure"), 0.0),
            "lower_pressure": _safe_float(torus.get("lower_pressure"), 0.0),
        },
        "learning": {
            "action": str(lifecycle.get("action") or "unknown"),
            "node_state": str(lifecycle.get("node_state") or "unknown"),
            "source": str(lifecycle.get("source") or "unknown"),
            "scores": {key: round(_safe_float(scores.get(key), 0.0), 4) for key in ("acquisition", "digestion", "connection", "embodiment")},
            "edge_event_counts": evidence.get("edge_event_counts") if isinstance(evidence.get("edge_event_counts"), dict) else {},
            "dark_neuron_phase": str(evidence.get("dark_neuron_phase") or "unknown"),
        },
        "trace": {
            "generated_at": trace.get("generated_at"),
            "event_counts": trace_summary.get("event_counts") if isinstance(trace_summary.get("event_counts"), dict) else {},
            "significant_transition_count": int(trace_summary.get("significant_transition_count") or 0),
        },
    }


def build_blender_code(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False)
    return f'''
import bpy, json, math
from mathutils import Vector

payload = json.loads({encoded!r})

def mat(name, color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = tuple(color)
    return m

def remove_prefix(prefix):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)

def make_curve(name, start, end, color, width):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = width
    spl = curve.splines.new("POLY")
    spl.points.add(1)
    spl.points[0].co = (start[0], start[1], start[2], 1)
    spl.points[1].co = (end[0], end[1], end[2], 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat(name + "_MAT", color))
    return obj

remove_prefix("SHION_")

field_mat = mat("SHION_Field_Mat", (0.055, 0.065, 0.075, 1.0))
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, -2.05))
field = bpy.context.object
field.name = "SHION_Field_NonEuclidean_Playground"
field.data.materials.append(field_mat)

positions = {{}}
for node in payload["nodes"]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=node["radius"], location=tuple(node["position"]))
    obj = bpy.context.object
    obj.name = node["name"]
    obj["shion_id"] = node["id"]
    obj["status"] = node["status"]
    obj["layer"] = node["layer"]
    obj.data.materials.append(mat("SHION_MAT_" + node["status"] + "_" + node["layer"], node["color"]))
    positions[node["id"]] = node["position"]

for edge in payload["edges"]:
    source = positions.get(edge["source"])
    target = positions.get(edge["target"])
    if source and target:
        width = 0.004 + min(0.03, edge["weight"] * 0.018)
        make_curve("SHION_EDGE_" + edge["source"][-4:] + "_" + edge["target"][-4:], source, target, (0.25, 0.62, 1.0, 0.55), width)

event_colors = {{
    "appeared": (0.25, 1.0, 0.55, 0.9),
    "reinforced": (1.0, 0.82, 0.18, 0.95),
    "softened": (0.72, 0.55, 1.0, 0.75),
    "decayed": (1.0, 0.18, 0.20, 0.72),
    "replayed": (0.70, 0.82, 1.0, 0.42),
}}
for transition in payload["transitions"]:
    source = positions.get(transition["source"])
    target = positions.get(transition["target"])
    if source and target:
        event = transition["event"]
        color = event_colors.get(event, (1.0, 1.0, 1.0, 0.6))
        width = 0.008 + min(0.045, transition["weight"] * 0.03)
        lifted_source = (source[0], source[1], source[2] + 0.12)
        lifted_target = (target[0], target[1], target[2] + 0.12)
        obj = make_curve("SHION_TRACE_" + event + "_" + transition["source"][-4:] + "_" + transition["target"][-4:], lifted_source, lifted_target, color, width)
        obj["event"] = event

learning = payload["learning"]
scores = learning["scores"]
bar_x = -6.2
for i, key in enumerate(["acquisition", "digestion", "connection", "embodiment"]):
    value = float(scores.get(key, 0.0))
    height = max(0.05, value * 2.0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bar_x + i * 0.45, -5.8, -1.9 + height / 2))
    bar = bpy.context.object
    bar.name = "SHION_LEARNING_BAR_" + key
    bar.dimensions = (0.28, 0.28, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bar["score"] = value
    bar.data.materials.append(mat("SHION_MAT_BAR_" + key, (0.15 + i * 0.12, 0.8 - i * 0.08, 0.95, 1.0)))

state_color = {{
    "registered": (0.35, 0.55, 1.0, 1.0),
    "pending": (1.0, 0.68, 0.18, 1.0),
    "dark_neuron": (0.22, 0.18, 0.42, 1.0),
    "replayed": (0.65, 0.80, 1.0, 1.0),
    "reinforced": (1.0, 0.85, 0.2, 1.0),
    "absorbed": (0.2, 0.95, 0.55, 1.0),
    "embodied": (0.95, 0.95, 0.95, 1.0),
}}.get(learning["node_state"], (0.8, 0.8, 0.8, 1.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(-5.55, -5.75, 1.0))
core = bpy.context.object
core.name = "SHION_LEARNING_STATE_" + learning["node_state"]
core["action"] = learning["action"]
core["source"] = learning["source"]
core["dark_neuron_phase"] = learning["dark_neuron_phase"]
core.data.materials.append(mat("SHION_MAT_LEARNING_STATE", state_color))

torus = payload["torus"]
bpy.ops.mesh.primitive_torus_add(major_radius=2.15 + torus["band_width"], minor_radius=0.018 + torus["band_width"] * 0.035, location=(0, 0, 2.6 + torus["sigma_position"]))
tor = bpy.context.object
tor.name = "SHION_TORUS_FIELD_" + torus["zone2_phase"]
tor["sigma_position"] = torus["sigma_position"]
tor["band_width"] = torus["band_width"]
tor.data.materials.append(mat("SHION_MAT_TORUS_FIELD", (1.0, 0.78, 0.22, 0.9)))

if not bpy.data.objects.get("SHION_Playground_Camera"):
    bpy.ops.object.camera_add(location=(7.5, -9.5, 6.2))
    cam = bpy.context.object
    cam.name = "SHION_Playground_Camera"
else:
    cam = bpy.data.objects["SHION_Playground_Camera"]
    cam.location = (7.5, -9.5, 6.2)
direction = Vector((0, 0, 0.3)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam

if not bpy.data.objects.get("SHION_Playground_Light"):
    bpy.ops.object.light_add(type="AREA", location=(0, -4, 6))
    light = bpy.context.object
    light.name = "SHION_Playground_Light"
else:
    light = bpy.data.objects["SHION_Playground_Light"]
light.data.energy = 520
light.data.size = 5

bpy.context.scene.world = bpy.context.scene.world or bpy.data.worlds.new("SHION_World")
bpy.context.scene.world.color = (0.025, 0.03, 0.04)

print("[SHION_PLAYGROUND] reflected nodes=%d edges=%d transitions=%d state=%s" % (
    len(payload["nodes"]), len(payload["edges"]), len(payload["transitions"]), learning["node_state"]
), flush=True)
'''


def send_execute_python(code: str, host: str, port: int, timeout: float = 12.0) -> dict[str, Any]:
    payload = {"command": "execute_python", "params": {"code": code}}
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        data = sock.recv(1024 * 1024)
    return json.loads(data.decode("utf-8"))


def reflect_once(args: argparse.Namespace) -> dict[str, Any]:
    scene = build_scene_payload(max_edges=args.max_edges, max_trace=args.max_trace)
    response = send_execute_python(build_blender_code(scene), args.host, args.port)
    status = {
        "timestamp": datetime.now().isoformat(),
        "response": response,
        "node_count": len(scene["nodes"]),
        "edge_count": len(scene["edges"]),
        "transition_count": len(scene["transitions"]),
        "learning_state": scene["learning"]["node_state"],
        "torus_zone2_phase": scene["torus"]["zone2_phase"],
    }
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return status


def _input_signature() -> tuple[float, float, float]:
    return tuple(path.stat().st_mtime if path.exists() else 0.0 for path in (GRAPH_PATH, TRACE_PATH, LIFECYCLE_PATH))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reflect Shion runtime state into Blender.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8008)
    parser.add_argument("--max-edges", type=int, default=80)
    parser.add_argument("--max-trace", type=int, default=48)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    if not args.watch:
        args.once = True

    last_sig: tuple[float, float, float] | None = None
    while True:
        sig = _input_signature()
        if sig != last_sig:
            status = reflect_once(args)
            print(json.dumps(status, ensure_ascii=False), flush=True)
            last_sig = sig
        if args.once:
            return 0
        time.sleep(max(1.0, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
