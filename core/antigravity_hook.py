import json
from pathlib import Path
import networkx as nx
import logging
import re
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime

logger = logging.getLogger("AntigravityHook")

class FermatResonanceHook:
    """[Phase 4] Antigravity Retrieval via Fermat's Principle"""
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        self.context_file = root_dir / "outputs" / "metacognitive_context_latest.json"
        self.metrics_file = root_dir / "outputs" / "token_savings_metrics.jsonl"
        self.manifest_file = root_dir / "core" / "auto_bridges" / "manifest.jsonl"
        self.graph = None
        self.graph_data: Dict[str, Any] = {"nodes": {}, "edges": []}
        self._load_graph()
        
    def _load_graph(self):
        if not self.graph_file.exists():
            return
        
        try:
            with open(self.graph_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "Resonance graph unavailable; continuing without graph context: %s",
                exc,
            )
            self.graph = None
            self.graph_data = {"nodes": {}, "edges": []}
            return
        self.graph_data = data
            
        self.graph = nx.Graph()
        for node in data.get("nodes", {}):
            self.graph.add_node(node)
        for edge in data.get("edges", []):
            # Invert weight for Dijkstra (shortest path = least resistance/strongest resonance)
            # High resonance weight -> low distance
            w = max(0.1, edge.get("weight", 1.0))
            dist = 1.0 / w
            self.graph.add_edge(
                edge["source"],
                edge["target"],
                weight=dist,
                resonance=edge.get("weight", 1.0),
                type=edge.get("type", "unknown"),
            )
            
    def get_resonance_path(self, start_node: str, end_node: str):
        """
        Finds the path of least resistance (strongest resonance) between two concepts/files.
        """
        if not self.graph or start_node not in self.graph or end_node not in self.graph:
            return None
            
        try:
            path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

    def read_graph_report(self) -> str:
        """
        Reads the high-level GRAPH_REPORT.md.
        Agents should call this BEFORE reading actual code files to orient themselves.
        """
        self.check_and_rebuild_freshness()
        report_file = self.root_dir / "outputs" / "GRAPH_REPORT.md"
        if report_file.exists():
            return report_file.read_text(encoding="utf-8")
        return "Graph Report not generated yet. Please run Resonance Graph Builder."

    def check_and_rebuild_freshness(self) -> bool:
        if not self.graph_file.exists():
            return False
            
        graph_mtime = self.graph_file.stat().st_mtime
        stale = False
        
        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in py_file.parts or "outputs" in py_file.parts or ".git" in py_file.parts:
                continue
            if py_file.exists() and py_file.stat().st_mtime > graph_mtime:
                logger.warning(f"[STALE_GRAPH] {py_file.name} modified after resonance graph.")
                stale = True
                break
                
        if stale:
            logger.info("Auto-rebuilding Resonance Graph to ensure metacognitive freshness...")
            try:
                try:
                    from resonance_graph_builder import ResonanceGraphBuilder
                    from wave_clustering import ResonanceWaveClusterer
                except ImportError:
                    from core.resonance_graph_builder import ResonanceGraphBuilder
                    from core.wave_clustering import ResonanceWaveClusterer

                builder = ResonanceGraphBuilder(self.root_dir)
                builder.build()
                ResonanceWaveClusterer(self.root_dir).cluster_and_report()
                self._load_graph()
                logger.info("Graph rebuilt successfully.")
            except Exception as e:
                logger.error(f"Failed to auto-rebuild graph: {e}")
        return not stale

    def build_context_window(
        self,
        ripple: Iterable[str] | str,
        max_files: int = 8,
        max_neighbors: int = 2,
    ) -> Dict[str, Any]:
        """
        Bend the code graph around the current metacognitive ripple.

        This does not read source files. It returns a small orientation window:
        high-resonance file candidates, nearby bridge nodes, and rough token
        savings compared with linear project scanning.
        """
        self.check_and_rebuild_freshness()
        
        if not self.graph or not self.graph_data.get("nodes"):
            return {
                "ok": False,
                "reason": "resonance_graph_missing",
                "files": [],
                "summary": "Resonance graph is not available yet.",
            }

        terms = self._normalize_terms(ripple)
        scored = self._score_nodes(terms)
        selected = scored[:max_files]

        files: List[Dict[str, Any]] = []
        seen = set()
        for node, score, reasons in selected:
            if node.startswith("sensory:"):
                continue
            node_data = self.graph_data.get("nodes", {}).get(node, {})
            neighbors = self._strong_neighbors(node, max_neighbors=max_neighbors)
            concepts = node_data.get("semantics", {}).get("concepts", [])
            item = {
                "path": node,
                "score": round(score, 3),
                "concepts": concepts[:6],
                "reasons": reasons[:5],
                "neighbors": neighbors,
            }
            files.append(item)
            seen.add(node)

        total_py_bytes = 0
        total_py_files = 0
        for n in self.graph_data.get("nodes", {}):
            if str(n).endswith(".py"):
                total_py_files += 1
                try:
                    fpath = self.root_dir / n
                    if fpath.exists():
                        total_py_bytes += fpath.stat().st_size
                except Exception:
                    pass

        selected_bytes = 0
        for item in files:
            try:
                fpath = self.root_dir / item["path"]
                if fpath.exists():
                    selected_bytes += fpath.stat().st_size
            except Exception:
                pass

        avoided_files = max(0, total_py_files - len(files))
        savings_ratio = round(avoided_files / total_py_files, 3) if total_py_files else 0.0
        
        avoided_bytes = max(0, total_py_bytes - selected_bytes)
        byte_savings_ratio = round(avoided_bytes / total_py_bytes, 3) if total_py_bytes else 0.0

        try:
            metric_entry = {
                "timestamp": datetime.now().isoformat(),
                "ripple": terms,
                "total_candidate_bytes": total_py_bytes,
                "selected_full_file_bytes": selected_bytes,
                "byte_savings_ratio": byte_savings_ratio,
                "file_savings_ratio": savings_ratio
            }
            with open(self.metrics_file, "a", encoding="utf-8") as mf:
                mf.write(json.dumps(metric_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug(f"Failed to write metrics: {e}")

        peripheral_files = self._get_peripheral_field(terms, seen, max_files=4)
        tense_files = self._get_excluded_but_tense(seen, max_files=3)
        depth_trigger = self._detect_depth_trigger(terms, files + peripheral_files + tense_files)

        result = {
            "ok": True,
            "ripple": terms,
            "files": files,
            "peripheral_field": peripheral_files,
            "excluded_but_tense": tense_files,
            "depth_trigger": depth_trigger,
            "stats": {
                "graph_nodes": len(self.graph_data.get("nodes", {})),
                "candidate_files": len(files),
                "linear_files_avoided": avoided_files,
                "estimated_scan_reduction": savings_ratio,
                "actual_byte_savings_ratio": byte_savings_ratio,
                "total_candidate_bytes": total_py_bytes,
                "selected_full_file_bytes": selected_bytes
            },
            "summary": self._format_context_summary(terms, files, peripheral_files, tense_files, depth_trigger, savings_ratio, byte_savings_ratio),
        }
        self._save_latest_context(result)
        return result

    def _normalize_terms(self, ripple: Iterable[str] | str) -> List[str]:
        if isinstance(ripple, str):
            raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[가-힣]{2,}", ripple)
        else:
            raw = []
            for item in ripple:
                raw.extend(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[가-힣]{2,}", str(item)))

        stopwords = {
            "the", "and", "for", "with", "from", "this", "that", "context",
            "current", "system", "general", "logic", "파일", "현재", "시스템",
        }
        terms = []
        seen = set()
        for term in raw:
            norm = term.lower().strip("_")
            if len(norm) < 2 or norm in stopwords or norm in seen:
                continue
            terms.append(norm)
            seen.add(norm)
        return terms[:24]

    def _score_nodes(self, terms: List[str]):
        scored = []
        for node, data in self.graph_data.get("nodes", {}).items():
            searchable_parts = [node.lower()]
            ast_data = data.get("ast", {})
            for key in ("functions", "classes", "imports", "calls"):
                value = ast_data.get(key, [])
                if isinstance(value, list):
                    searchable_parts.extend(str(v).lower() for v in value)
            semantics = data.get("semantics", {})
            concepts = semantics.get("concepts", [])
            searchable_parts.extend(str(c).lower() for c in concepts)
            if "description" in ast_data:
                searchable_parts.append(str(ast_data["description"]).lower())

            haystack = " ".join(searchable_parts)
            score = 0.0
            reasons = []
            for term in terms:
                if term in haystack:
                    weight = 1.0
                    if term in node.lower():
                        weight += 1.0
                    if any(term in str(c).lower() for c in concepts):
                        weight += 1.5
                    score += weight
                    reasons.append(term)

            if self.graph and node in self.graph:
                score += min(1.0, self.graph.degree(node) / 20.0)

            if score > 0:
                scored.append((node, score, reasons))

        return sorted(scored, key=lambda item: item[1], reverse=True)

    def _strong_neighbors(self, node: str, max_neighbors: int = 2) -> List[str]:
        if not self.graph or node not in self.graph:
            return []
        edges = []
        for neighbor in self.graph.neighbors(node):
            data = self.graph.get_edge_data(node, neighbor) or {}
            edges.append((neighbor, data.get("resonance", 0.0)))
        edges.sort(key=lambda item: item[1], reverse=True)
        return [neighbor for neighbor, _ in edges[:max_neighbors]]

    def _format_context_summary(
        self,
        terms: List[str],
        files: List[Dict[str, Any]],
        peripheral: List[Dict[str, Any]],
        tense: List[Dict[str, Any]],
        depth_trigger: Dict[str, Any],
        savings_ratio: float,
        byte_savings_ratio: float = 0.0
    ) -> str:
        lines = [
            "[ANTIGRAVITY_CONTEXT]",
            f"Ripple: {', '.join(terms[:10]) if terms else 'none'}",
            f"Estimated scan reduction (Files): {savings_ratio:.1%}",
            f"Actual scan reduction (Bytes): {byte_savings_ratio:.1%}",
            "---",
            "Read these files before broad scanning (DIRECT FOCUS):",
        ]
        for item in files:
            concepts = ", ".join(item.get("concepts", [])[:3]) or "unlabeled"
            reasons = ", ".join(item.get("reasons", [])[:3]) or "graph gravity"
            lines.append(
                f"- {item['path']} | score={item['score']} | concepts={concepts} | reasons={reasons}"
            )

        if peripheral:
            lines.append("\nPERIPHERAL_FIELD (Related contexts for intuition):")
            for item in peripheral:
                lines.append(f"- {item['path']} | type={item.get('type', 'UNKNOWN')} | score={item.get('score', 0)}")

        if tense:
            lines.append("\nEXCLUDED_BUT_TENSE (Low match, but high system pressure/failure):")
            for item in tense:
                lines.append(f"- {item['path']} | tension_score={item.get('tension', 0)}")

        if depth_trigger.get("triggered"):
            lines.append(f"\n[DEPTH_TRIGGER] {depth_trigger['reason']}")
            lines.append(">>> Recommendation: STOP summarizing. Read full source files for the items above.")

        return "\n".join(lines)

    def _get_peripheral_field(self, terms: List[str], seen: set, max_files: int) -> List[Dict[str, Any]]:
        """Finds files based on recent activity and failure status, even if not in ripple focus."""
        peripheral = []
        now = datetime.now().timestamp()
        
        # 1. Check for recently modified files
        for py_file in self.root_dir.rglob("*.py"):
            if any(p in py_file.parts for p in ("venv", "outputs", ".git")):
                continue
            node = str(py_file.relative_to(self.root_dir)).replace("\\", "/")
            if node in seen:
                continue
            
            mtime = py_file.stat().st_mtime
            age_score = max(0, 1.0 - (now - mtime) / (3600 * 24)) # Score decreases over 24h
            if age_score > 0.5:
                peripheral.append({"path": node, "score": age_score, "type": "RECENT_EDIT"})

        # 2. Add Sensory Nodes from graph (if they exist)
        for node in self.graph_data.get("nodes", {}):
            if node.startswith("sensory:") and node not in seen:
                peripheral.append({"path": node, "score": 0.8, "type": "SENSORY_TRACE"})
        
        peripheral.sort(key=lambda x: x["score"], reverse=True)
        return peripheral[:max_files]

    def _get_excluded_but_tense(self, seen: set, max_files: int) -> List[Dict[str, Any]]:
        """Finds high-priority nodes using degree, recent failures, and manifest risk."""
        tense = []
        if not self.graph: return []
        
        # Collect recent failure paths from manifest
        failure_nodes = set()
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-20:]: # Last 20 entries
                        entry = json.loads(line)
                        if entry.get("status") in ("REJECTED", "FAILED_LLM", "DREAM_COLLAPSE"):
                            if entry.get("target_a"): failure_nodes.add(entry["target_a"])
            except Exception: pass

        for node in self.graph.nodes:
            if node in seen or not node.endswith(".py"):
                continue
            
            degree_score = min(1.0, self.graph.degree(node) / 50.0)
            failure_score = 1.0 if node in failure_nodes else 0.0
            
            # Weighted tension: Favor failures and high centrality, but penalize pure test files
            is_test = 0.5 if "test" in node.lower() else 1.0
            tension_score = (degree_score * 0.4 + failure_score * 0.6) * is_test
            
            if tension_score > 0.2:
                tense.append({"path": node, "tension": round(tension_score, 3)})
        
        tense.sort(key=lambda x: x["tension"], reverse=True)
        return tense[:max_files]

    def _detect_depth_trigger(self, terms: List[str], all_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detects if the current situation requires deep reading (Non-Euclidean Z-depth)."""
        trigger = {"triggered": False, "reason": ""}
        
        # Trigger 1: Concept confusion (too many ripple terms with low average score)
        if len(terms) > 6 and len(all_candidates) < 4:
            trigger = {"triggered": True, "reason": "High term ambiguity with low resonance match."}
        
        # Trigger 2: Identity/Role collision (Fixed names: luvit, 루빛, 시안, 아리, 세나, 루아, 비노체)
        collision_terms = {
            "identity", "shion", "luvit", "ari", "binoche", "lua", "role",
            "시안", "루빛", "아리", "비노체", "루아"
        }
        if any(t in terms for t in collision_terms):
             trigger = {"triggered": True, "reason": "Identity or Role collision detected in ripple (Critical Anchor check)."}
        
        # Trigger 3: Explicit failure context
        if any(t in ("fail", "error", "failed", "crash", "bug") for t in terms):
             trigger = {"triggered": True, "reason": "Failure recovery context requires deep source analysis."}

        return trigger

    def _save_latest_context(self, result: Dict[str, Any]) -> None:
        try:
            self.context_file.parent.mkdir(parents=True, exist_ok=True)
            self.context_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.debug(f"Failed to save metacognitive context: {exc}")

if __name__ == "__main__":
    hook = FermatResonanceHook(Path(r"c:\workspace2\shion"))
    print("Hook initialized.")
    print("Graph Report Preview:\n")
    print(hook.read_graph_report()[:500] + "...")
    print("\nContext Window Preview:\n")
    print(hook.build_context_window("metacognition hippocampus token resonance")["summary"])
