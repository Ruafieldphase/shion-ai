import ast
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any
import urllib.request
import urllib.error
import re
import math

logger = logging.getLogger("ResonanceGraphBuilder")


def _rhythm_tokens(value: Any) -> set:
    """Convert concepts and symbols into local wave bands without scanning the graph."""
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = [str(v) for v in value]
    else:
        items = []

    bands = set()
    for item in items:
        text = item.lower()
        parts = re.findall(r"[a-z0-9]+|[가-힣]+", text)
        if not parts and text:
            parts = [text]
        for part in parts:
            if len(part) < 3:
                continue
            bands.add(part)
            for n in range(3, min(7, len(part)) + 1):
                bands.add(part[:n])
    return bands


def _phase_energy(node: Dict[str, Any]) -> float:
    ast_data = node.get("ast", {})
    sem_data = node.get("semantics", {})
    concept_count = len(sem_data.get("concepts", []))
    symbol_count = sum(
        len(ast_data.get(key, []))
        for key in ("functions", "classes", "imports", "calls")
        if isinstance(ast_data.get(key, []), list)
    )
    status_gain = {
        "EXTRACTED": 1.25,
        "SENSORY_INJECTED": 1.15,
        "INFERRED": 0.9,
        "AMBIGUOUS": 0.65,
    }.get(sem_data.get("status"), 0.8)
    return math.log1p(concept_count + symbol_count) * status_gain


def calculate_resonance(node_a, node_b, graph_data):
    """
    Calculate Gravity & Resonance between two nodes in local phase space.

    node_a/node_b may be node ids or node dictionaries. graph_data may include
    an optional `_phase_index` keyed by node id; no graph-wide scan is required.
    """
    nodes = graph_data.get("nodes", {}) if isinstance(graph_data, dict) else {}
    phase_index = graph_data.get("_phase_index", {}) if isinstance(graph_data, dict) else {}

    key_a = node_a if isinstance(node_a, str) else None
    key_b = node_b if isinstance(node_b, str) else None
    data_a = nodes.get(key_a, {}) if key_a else node_a
    data_b = nodes.get(key_b, {}) if key_b else node_b
    if not isinstance(data_a, dict) or not isinstance(data_b, dict):
        return 0.0

    bands_a = set(phase_index.get(key_a, ())) if key_a in phase_index else _node_bands(data_a)
    bands_b = set(phase_index.get(key_b, ())) if key_b in phase_index else _node_bands(data_b)
    if not bands_a or not bands_b:
        return 0.0

    overlap = bands_a & bands_b
    interference = sum((len(band) / 6.0) ** 2 for band in overlap)
    normalization = math.sqrt(len(bands_a) * len(bands_b))
    constructive_interference = interference / normalization if normalization else 0.0

    gravity = math.sqrt(_phase_energy(data_a) * _phase_energy(data_b))
    curvature = 1.0 - math.exp(-(constructive_interference * gravity))
    resonance = round(curvature * 4.0, 4)

    # Non-Euclidean least action: stronger constructive interference bends phase space so the geodesic cost decreases without a global scan.
    return resonance


def _node_bands(node: Dict[str, Any]) -> set:
    ast_data = node.get("ast", {})
    sem_data = node.get("semantics", {})
    bands = set()
    bands |= _rhythm_tokens(sem_data.get("concepts", []))
    for key in ("functions", "classes", "imports", "calls"):
        bands |= _rhythm_tokens(ast_data.get(key, []))
    if "description" in ast_data:
        bands |= _rhythm_tokens(ast_data.get("description", ""))
    return bands

class ASTParser:
    """[Phase 1] Base Frequency Extraction (0 Token Cost)"""
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.nodes = {}  # file_path -> {type: "module", functions: [], classes: [], imports: []}
        
    def parse_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Simple heuristic for calls
            calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(node.func.attr)
                        
            rel_path = str(file_path.relative_to(self.root_dir)).replace("\\", "/")
            self.nodes[rel_path] = {
                "functions": funcs,
                "classes": classes,
                "imports": list(set(imports)),
                "calls": list(set(calls))
            }
        except SyntaxError:
            logger.warning(f"Syntax error parsing {file_path}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

class SHA256Cache:
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache = self._load()
        
    def _load(self) -> Dict[str, str]:
        if self.cache_file.exists():
            with open(self.cache_file, "r") as f:
                try: return json.load(f)
                except: return {}
        return {}
        
    def save(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)
            
    def is_changed(self, file_path: Path) -> bool:
        if not file_path.exists():
            return False
        content = file_path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        rel_path = str(file_path)
        
        if self.cache.get(rel_path) != file_hash:
            self.cache[rel_path] = file_hash
            return True
        return False

class SemanticExtractor:
    """[Phase 2] Resonance Network Construction (Tensor Field)"""
    def __init__(self, endpoint="http://localhost:8000/api/chat"):
        self.endpoint = endpoint
        
    def extract_semantics(self, file_path: Path) -> Dict[str, Any]:
        """
        Uses local LLM to extract semantic tags. 
        If the server is down or we want to save time, we provide a fallback.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            # We only read the first 1000 characters to save tokens/time for semantic extraction
            preview = content[:1000]
            
            prompt = (
                "Analyze the following code snippet and extract core concepts or domains it belongs to "
                "(e.g., 'audio', 'ui', 'database', 'resonance', 'agent'). Return a comma separated list.\n\n"
                f"{preview}"
            )
            
            payload = {
                "model": "shion-v1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            # Using short timeout so we don't hang if server is down
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                concepts = res.get("message", {}).get("content", "").split(",")
                return {
                    "concepts": [c.strip().lower() for c in concepts if c.strip()],
                    "status": "EXTRACTED"
                }
        except Exception as e:
            # Fallback to heuristic semantic extraction if LLM fails
            logger.debug(f"Semantic LLM failed for {file_path}, using heuristic: {e}")
            return self._heuristic_extraction(file_path)
            
    def _heuristic_extraction(self, file_path: Path):
        name = file_path.stem.lower()
        concepts = []
        if "audio" in name or "synth" in name: concepts.append("audio_resonance")
        if "agent" in name or "orchestrator" in name: concepts.append("agent_logic")
        if "vision" in name or "screen" in name: concepts.append("visual_perception")
        if "graph" in name or "cluster" in name: concepts.append("hippocampus_memory")
        if not concepts: concepts.append("general_logic")
        
        return {
            "concepts": concepts,
            "status": "INFERRED"
        }

class ResonanceGraphBuilder:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.cache = SHA256Cache(root_dir / "outputs" / "resonance_cache.json")
        self.parser = ASTParser(root_dir)
        self.semantic = SemanticExtractor()
        
        self.graph_data = {
            "nodes": {},  # file -> {ast: {}, semantics: {}}
            "edges": []   # {"source": file, "target": file, "type": "import|call|semantic", "weight": float}
        }
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        
    def _load_previous_graph(self):
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r") as f:
                    self.graph_data = json.load(f)
            except: pass
            
    def build(self):
        self._load_previous_graph()
        py_files = list(self.root_dir.rglob("*.py"))
        
        changed_files = []
        for f in py_files:
            # Skip virtual envs, outputs, tests
            if "venv" in f.parts or "outputs" in f.parts or ".git" in f.parts:
                continue
            if self.cache.is_changed(f):
                changed_files.append(f)
                
        logger.info(f"Found {len(changed_files)} changed files to process out of {len(py_files)} total.")
        
        for f in changed_files:
            rel_path = str(f.relative_to(self.root_dir)).replace("\\", "/")
            self.parser.parse_file(f)
            sem = self.semantic.extract_semantics(f)
            
            self.graph_data["nodes"][rel_path] = {
                "ast": self.parser.nodes.get(rel_path, {}),
                "semantics": sem
            }
            
        # Rebuild edges based on imports and semantics
        self._build_edges()
        self.cache.save()
        
        # Save graph
        with open(self.graph_file, "w") as f:
            json.dump(self.graph_data, f, indent=2)
            
        return self.graph_file

    def imprint_sensory_wave(self, sensory_type: str, description: str, content_ref: str):
        """
        Imprints a sensory wave (e.g., visual memory) onto the Non-Euclidean space.
        Instead of 'forcing' a node, this represents a natural wave leaving a resonance trace.
        """
        from datetime import datetime
        self._load_previous_graph()
        
        node_id = f"sensory:{sensory_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        prompt = (
            "Analyze the following sensory description and extract core concepts or domains it belongs to "
            "(e.g., 'audio', 'ui', 'database', 'resonance', 'agent'). Return a comma separated list.\n\n"
            f"{description}"
        )
        
        concepts = []
        try:
            import urllib.request
            payload = {
                "model": "shion-v1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            req = urllib.request.Request(
                self.semantic.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                choices = res.get("choices", [])
                if choices:
                    concepts_raw = choices[0].get("message", {}).get("content", "")
                else:
                    concepts_raw = res.get("message", {}).get("content", "")
                concepts = [c.strip().lower() for c in concepts_raw.split(",") if c.strip()]
        except Exception:
            concepts = ["visual_perception"]
            if "code" in description.lower() or "python" in description.lower(): concepts.append("general_logic")
            if "audio" in description.lower(): concepts.append("audio_resonance")
            
        self.graph_data["nodes"][node_id] = {
            "ast": {"description": description[:200], "type": "sensory_node"},
            "semantics": {"concepts": concepts, "status": "SENSORY_INJECTED"},
            "content_ref": content_ref
        }
        
        self._build_edges()
        
        with open(self.graph_file, "w") as f:
            json.dump(self.graph_data, f, indent=2)
            
        logger.info(f"👁️ Injected sensory memory into Resonance Graph: {node_id} (Concepts: {concepts})")
        return node_id

    def _build_edges(self):
        self.graph_data["edges"] = []
        nodes = self.graph_data["nodes"]
        
        # Build file name to path mapping for import resolution
        module_to_path = {}
        for path in nodes.keys():
            mod_name = Path(path).stem
            module_to_path[mod_name] = path

        phase_index = {
            path: list(_node_bands(data))
            for path, data in nodes.items()
        }
        self.graph_data["_phase_index"] = phase_index
            
        for source_path, data in nodes.items():
            ast_data = data.get("ast", {})
            
            # 1. Structural Edges (Base Frequency)
            imports = ast_data.get("imports", [])
            for imp in imports:
                # Naive resolution: if import name matches a module file name
                parts = imp.split(".")
                target_mod = parts[-1]
                if target_mod in module_to_path and module_to_path[target_mod] != source_path:
                    target_path = module_to_path[target_mod]
                    self.graph_data["edges"].append({
                        "source": source_path,
                        "target": target_path,
                        "type": "import",
                        "weight": 2.0  # Strong structural connection
                    })
                    
            # 2. Semantic Edges (Tensor Field)
            for target_path, t_data in nodes.items():
                if source_path >= target_path: continue # Undirected semantic similarity
                weight = calculate_resonance(source_path, target_path, self.graph_data)
                if weight > 0:
                    self.graph_data["edges"].append({
                        "source": source_path,
                        "target": target_path,
                        "type": "semantic",
                        "weight": weight
                    })

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = ResonanceGraphBuilder(Path(r"c:\workspace2\shion"))
    out_file = builder.build()
    print(f"Resonance Graph built at {out_file}")
