import logging
from pathlib import Path
from resonance_graph_builder import ResonanceGraphBuilder
from wave_clustering import ResonanceWaveClusterer

def test_sensory_injection():
    logging.basicConfig(level=logging.INFO)
    root = Path(r"c:\workspace2\shion")
    
    # 1. Inject Sensory Memory
    builder = ResonanceGraphBuilder(root)
    desc = "The screen shows a Python code editor with Antigravity agent logs. There is a blue background."
    
    print("🌊 [Test] Injecting visual memory...")
    node_id = builder.imprint_sensory_wave(
        sensory_type="vision",
        description=desc,
        content_ref="dummy_screen.png"
    )
    
    # 2. Re-cluster and Report
    print("🌊 [Test] Re-clustering Wave Space...")
    clusterer = ResonanceWaveClusterer(root)
    clusterer.cluster_and_report()
    
    # 3. Read Report
    report = (root / "outputs" / "GRAPH_REPORT.md").read_text(encoding="utf-8")
    
    print("\n--- NEW GRAPH REPORT PREVIEW ---")
    for line in report.split("\n")[:25]:
        print(line)

if __name__ == "__main__":
    test_sensory_injection()
