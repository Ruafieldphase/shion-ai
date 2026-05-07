import json
import logging
from pathlib import Path
import networkx as nx
from community import community_louvain

logger = logging.getLogger("WaveClustering")

class ResonanceWaveClusterer:
    """[Phase 3] Wave Interference Clustering (Community Detection)"""
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        self.report_file = root_dir / "outputs" / "GRAPH_REPORT.md"
        
    def cluster_and_report(self):
        if not self.graph_file.exists():
            logger.error("Resonance graph not found. Run builder first.")
            return
            
        with open(self.graph_file, "r") as f:
            data = json.load(f)
            
        # 1. Build NetworkX Graph
        G = nx.Graph()  # Undirected for community detection
        
        for edge in data.get("edges", []):
            u = edge["source"]
            v = edge["target"]
            w = edge.get("weight", 1.0)
            
            if G.has_edge(u, v):
                G[u][v]['weight'] += w
            else:
                G.add_edge(u, v, weight=w)
                
        if len(G.nodes) == 0:
            logger.warning("Graph is empty. No communities to form.")
            return
            
        # 2. Wave Interference Clustering (Louvain)
        # This groups nodes by finding subsets with high internal connectivity (constructive interference)
        partition = community_louvain.best_partition(G, weight='weight')
        
        communities = {}
        for node, comm_id in partition.items():
            if comm_id not in communities:
                communities[comm_id] = []
            communities[comm_id].append(node)
            
        # 3. Identify God Nodes (Centrality)
        # Calculate PageRank or Betweenness Centrality to find nodes with highest "Gravity"
        gravity = nx.pagerank(G, weight='weight')
        god_nodes = sorted(gravity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 4. Generate GRAPH_REPORT.md
        self._generate_report(communities, god_nodes, data["nodes"])
        return self.report_file
        
    def _generate_report(self, communities, god_nodes, node_data):
        lines = [
            "# 🌌 Shion Resonance Graph (Non-Euclidean Space)",
            "This report maps the physical codebase into semantic wave communities. Read this to orient yourself.",
            "",
            "## 🌍 God Nodes (High Gravity Centers)",
            "These are the most deeply connected components in the system:"
        ]
        
        for node, grav in god_nodes:
            lines.append(f"- **{node}** (Gravity: {grav:.4f})")
            
        # [NEW] Extract sensory memories explicitly
        sensory_nodes = [n for n in node_data.keys() if str(n).startswith("sensory:")]
        if sensory_nodes:
            lines.append("\n## 👁️ Sensory Memories (Open System Disruptions)")
            lines.append("These are external perceptions currently warping the codebase gravity:")
            for sn in sorted(sensory_nodes, reverse=True)[:5]: # Show latest 5
                desc = node_data[sn].get("ast", {}).get("description", "Unknown sensation")
                lines.append(f"- **{sn}**: {desc}")
            
        lines.append("\n## 🌊 Resonance Zones (Constructive Interference Communities)")
        
        for comm_id, nodes in communities.items():
            lines.append(f"### Zone {comm_id} (Size: {len(nodes)})")
            
            # Try to summarize the concepts of this zone
            zone_concepts = {}
            for n in nodes:
                sem = node_data.get(n, {}).get("semantics", {})
                for c in sem.get("concepts", []):
                    zone_concepts[c] = zone_concepts.get(c, 0) + 1
                    
            top_concepts = sorted(zone_concepts.items(), key=lambda x: x[1], reverse=True)[:3]
            concept_str = ", ".join([f"{c}({cnt})" for c, cnt in top_concepts]) if top_concepts else "Unknown"
            
            lines.append(f"**Dominant Frequencies (Concepts):** {concept_str}")
            lines.append("**Particles (Files):**")
            for n in sorted(nodes):
                lines.append(f"- `{n}`")
            lines.append("")
            
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        logger.info(f"Generated Resonance Graph Report at {self.report_file}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    clusterer = ResonanceWaveClusterer(Path(r"c:\workspace2\shion"))
    clusterer.cluster_and_report()
