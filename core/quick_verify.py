import logging
from pathlib import Path
from resonance_graph_builder import ResonanceGraphBuilder
from wave_clustering import ResonanceWaveClusterer
from antigravity_hook import FermatResonanceHook

def quick_verify():
    logging.basicConfig(level=logging.INFO)
    root = Path(r"c:\workspace2\shion")
    
    # Override root dir logic in builder to just scan the `config` or a very specific dir
    # Actually, we can just instantiate the builder and patch the file list
    builder = ResonanceGraphBuilder(root)
    
    # We will manually pass a small list of files
    test_files = [
        root / "core" / "metrics_engine.py",
        root / "core" / "mitochondria.py",
        root / "core" / "body_entropy_sensor.py"
    ]
    
    print("🌊 [Quick Verify] Extracting base frequencies and semantics...")
    for f in test_files:
        if f.exists():
            rel_path = str(f.relative_to(root)).replace("\\", "/")
            builder.parser.parse_file(f)
            sem = builder.semantic.extract_semantics(f)
            builder.graph_data["nodes"][rel_path] = {
                "ast": builder.parser.nodes.get(rel_path, {}),
                "semantics": sem
            }
            
    # Build edges
    builder._build_edges()
    
    # Save temp graph
    temp_graph = root / "outputs" / "temp_graph.json"
    import json
    with open(temp_graph, "w") as f:
        json.dump(builder.graph_data, f, indent=2)
        
    print("\n🌊 [Quick Verify] Clustering Waves...")
    clusterer = ResonanceWaveClusterer(root)
    clusterer.graph_file = temp_graph
    clusterer.report_file = root / "outputs" / "QUICK_GRAPH_REPORT.md"
    report_file = clusterer.cluster_and_report()
    
    print("\n--- QUICK GRAPH REPORT PREVIEW ---")
    if report_file and report_file.exists():
        report = report_file.read_text(encoding="utf-8")
        lines = report.split("\n")
        for line in lines[:20]:
            print(line)
        print("...")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    quick_verify()
