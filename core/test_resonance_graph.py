import logging
from pathlib import Path
from resonance_graph_builder import ResonanceGraphBuilder
from wave_clustering import ResonanceWaveClusterer
from antigravity_hook import FermatResonanceHook

def test_hippocampus():
    logging.basicConfig(level=logging.INFO)
    root = Path(r"c:\workspace2\shion")
    
    print("🌊 [Phase 1 & 2] Building Resonance Graph (AST + Semantics)...")
    builder = ResonanceGraphBuilder(root)
    graph_file = builder.build()
    print(f"✅ Graph built at: {graph_file}")
    
    print("\n🌊 [Phase 3] Clustering Waves (Topology Community Detection)...")
    clusterer = ResonanceWaveClusterer(root)
    report_file = clusterer.cluster_and_report()
    print(f"✅ Report generated at: {report_file}")
    
    print("\n🌊 [Phase 4] Testing Fermat's Hook...")
    hook = FermatResonanceHook(root)
    report = hook.read_graph_report()
    
    print("\n--- GRAPH REPORT PREVIEW ---")
    lines = report.split("\n")
    for line in lines[:20]:
        print(line)
    if len(lines) > 20:
        print("...")

if __name__ == "__main__":
    test_hippocampus()
