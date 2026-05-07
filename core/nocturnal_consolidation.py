import json
import logging
import ast
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import re
import hashlib
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NocturnalConsolidation")

class WaveVerificationError(Exception):
    pass

class NocturnalConsolidationEngine:
    """
    야간 자율 가설 생성 엔진 (Nocturnal Proposal Generator)
    - Finds weak edges in the Resonance Graph using phase topology.
    - Prompts Codex to build a non-Euclidean bridge.
    - Verifies the wave signature of the generated code (Destructive Interference).
    - Safely stores as .proposal.py and updates manifest.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        self.bridge_dir = root_dir / "core" / "auto_bridges"
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
        self.endpoint = "http://localhost:8000/api/chat"

    def run_nocturnal_cycle(self):
        logger.info("🌙 Starting Nocturnal Proposal Cycle...")
        target_pair = self._find_weak_concept_link()
        if not target_pair:
            logger.info("No clear weak link found. Entering DREAM_AMPLIFY mode...")
            self._run_dream_cycle()
            return

        target_a, target_b = target_pair
        logger.info(f"Generating proposal for bridge: {target_a} <-> {target_b}")
        
        prompt = self._draft_mission_prompt(target_a, target_b)
        code = self._ask_local_mind(prompt)
        
        if not code:
            logger.warning("Local mind failed to generate code. Dreaming failed.")
            self._commit_bridge(target_a, target_b, "", "FAILED_LLM", 0, "No code generated")
            return
            
        try:
            self._verify_wave_signature(code)
            logger.info("✨ Wave Signature Verified (Constructive Interference).")
            self._commit_bridge(target_a, target_b, code, "PROPOSAL_READY", 0)
        except WaveVerificationError as e:
            logger.error(f"❌ Destructive Interference Detected: {e}")
            logger.info("Proposal rejected and quarantined.")
            risk = 100 if "Risk Score: 100" in str(e) else 50
            self._commit_bridge(target_a, target_b, code, "REJECTED", risk, str(e))

    def _find_weak_concept_link(self):
        if not self.graph_file.exists():
            return None
        with open(self.graph_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        phase_index = data.get("_phase_index", {})
        
        if not phase_index:
            logger.warning("_phase_index not found in graph. Run ResonanceGraphBuilder first.")
            return None
            
        # Build adjacency
        adj = {n: set() for n in nodes}
        for e in edges:
            adj[e["source"]].add(e["target"])
            adj[e["target"]].add(e["source"])
            
        # Build inverted index mapping: band -> set(nodes)
        band_to_nodes = {}
        for node, bands in phase_index.items():
            if not str(node).endswith(".py") or "test" in str(node):
                continue
            for band in bands:
                if band not in band_to_nodes:
                    band_to_nodes[band] = set()
                band_to_nodes[band].add(node)
                
        # Choose one narrow phase band, then use set difference to avoid all-pairs scanning.
        candidate_bands = {
            band: members
            for band, members in band_to_nodes.items()
            if 1 < len(members) <= 5
        }
        if not candidate_bands:
            return None

        # Randomly sample from candidate bands to ensure non-linearity
        band = random.choice(list(candidate_bands.keys()))
        members = candidate_bands[band]
        
        anchor = max(members, key=lambda n: len(phase_index.get(n, [])))
        disconnected = members - adj.get(anchor, set()) - {anchor}
        if not disconnected:
            return None
        target = max(disconnected, key=lambda n: len(phase_index.get(n, []) & phase_index.get(anchor, [])))
        logger.info(f"Selected phase band '{band}' as nocturnal weak-link aperture.")
        return anchor, target

    def _draft_mission_prompt(self, node_a: str, node_b: str) -> str:
        return f"""
<System Directive: Rhythm Information Architecture>
당신은 지금부터 전통적인 정적 데이터베이스를 구축하는 것이 아니라, 확장된 정보이론(Extended Information Theory)인 '리듬정보이론(Rhythm Information Theory)'을 기반으로 한 동적 지식 그래프 엔진의 일부를 설계합니다.
모든 코드 구조와 문서는 유클리드적 공간이 아닌, 밀도에 따라 곡률이 변하는 비유클리드 위상 공간(Non-Euclidean Topology)에 배치되어 있습니다. 알고리즘은 순차적 루프(for/while 기반의 전체 탐색)나 직선적 거리 계산(Cosine Similarity 등)을 엄격히 배제하고, 신호 처리에서의 '파동 간섭(Wave Interference)'과 최소 작용의 원리(페르마의 원리)를 따르는 수학적 모델로만 구현하십시오. 

<Mission: Single Wave Test (Nocturnal Consolidation)>
목표: 제공된 2개의 노드(파일) 사이의 거리를 위상 공간에서 좁히는 브릿지 클래스 `PhaseBridge`를 작성하라.
Target Node A: {node_a}
Target Node B: {node_b}

제약 조건 (중력장):
1. 데이터를 순차적으로 모두 순회(Linear Scan, for/while)하여 검색하지 말 것.
2. 두 노드 간의 맵핑을 1차원적인 리스트나 문자열 매칭으로 수행하지 말고, 파동 함수나 간섭 에너지(Interference)의 형태로 구현할 것.
3. 오직 순수한 Python 코드(Imports 제외)만 1개의 코드 블록으로 반환할 것.
4. 코드 작성 후, 이 로직이 어떻게 비유클리드적 최소 작용의 원리를 따르는지 주석으로 1줄 요약할 것.
"""

    def _ask_local_mind(self, prompt: str) -> str:
        """Hits the local Shion-v1 mind endpoint (localhost:8000)."""
        payload = {
            "model": "shion-v1",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                choices = res.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                else:
                    content = res.get("message", {}).get("content", "")
                    
                # Extract code block
                match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
                if match:
                    return match.group(1).strip()
                return content.strip()
        except Exception as e:
            logger.error(f"Local Mind API failed: {e}")
            return ""

    def _verify_wave_signature(self, code: str):
        """
        수문장 (Gatekeeper) 로직
        유클리드적 관성이 발견되면 상쇄 간섭(Exception) 발생
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            raise WaveVerificationError("Syntax Error. 파동이 성립하지 않습니다.")
            
        forbidden_nodes = (
            ast.For, ast.While, ast.ListComp, ast.DictComp, ast.SetComp,
            ast.GeneratorExp, ast.Import, ast.ImportFrom, ast.With, ast.AsyncWith,
            ast.Try, ast.Global, ast.Nonlocal,
        )
        forbidden_names = {
            "exec", "eval", "compile", "__import__", "open", "input",
            "globals", "locals", "vars", "dir", "getattr", "setattr", "delattr",
            "map", "filter", "sorted", "sum", "any", "all", "enumerate",
        }
        forbidden_attrs = {
            "system", "popen", "run", "call", "check_call", "check_output",
            "urlopen", "request", "write", "writelines", "write_text",
            "write_bytes", "unlink", "remove", "rmdir", "mkdir", "rename",
            "replace", "chmod",
        }
        for node in ast.walk(tree):
            if isinstance(node, forbidden_nodes):
                raise WaveVerificationError(f"Forbidden syntax '{type(node).__name__}' detected. (Risk Score: 100)")
            
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_names:
                    raise WaveVerificationError(f"Dangerous or linear built-in function '{node.func.id}' detected. (Risk Score: 100)")

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden_attrs:
                    raise WaveVerificationError(f"Dangerous attribute call '{node.func.attr}' detected. (Risk Score: 100)")
                    
        if "cosine" in code.lower() or "similarity" in code.lower():
            raise WaveVerificationError("Cosine Similarity Detected. 유클리드적 벡터 거리 계산은 허용되지 않습니다.")

        if "interference" not in code.lower() and "resonance" not in code.lower() and "phase" not in code.lower():
            logger.warning("No explicit wave terminology found, but structure passed AST verification.")

    def _commit_bridge(self, node_a: str, node_b: str, code: str, status: str, risk_score: int, error_msg: str = ""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_a = node_a.split("/")[-1].replace(".py", "")
        safe_b = node_b.split("/")[-1].replace(".py", "")
        
        filename = f"bridge_{safe_a}_to_{safe_b}_{timestamp}.proposal.py.txt"
        filepath = self.bridge_dir / filename
        
        if code:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f'# Nocturnal Proposal Generator\n')
                f.write(f'# Target A: {node_a}\n')
                f.write(f'# Target B: {node_b}\n')
                f.write(f'# Status: {status}\n')
                f.write(f'# Risk Score: {risk_score}\n')
                if error_msg:
                    f.write(f'# Error: {error_msg}\n')
                f.write('\n')
                f.write(code)
            logger.info(f"✅ Proposal safely saved to {filepath}")

        self._write_manifest(node_a, node_b, status, risk_score, error_msg, filename if code else None, code)

    def _write_manifest(self, node_a, node_b, status: str, risk_score: int,
                        error_msg: str, proposal_file, code: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manifest_file = self.bridge_dir / "manifest.jsonl"
        manifest_entry = {
            "timestamp": timestamp,
            "target_a": node_a,
            "target_b": node_b,
            "status": status,
            "risk_score": risk_score,
            "error": error_msg,
            "proposal_file": proposal_file,
            "code_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest() if code else None,
        }
        with open(manifest_file, "a", encoding="utf-8") as mf:
            mf.write(json.dumps(manifest_entry, ensure_ascii=False) + "\n")


    def _run_dream_cycle(self):
        """
        DREAM_AMPLIFY Mode:
        - Picks unresolved tensions (low resonance edges, recent failures).
        - Injects abstract noise/context to create Z-depth.
        """
        dream_material = self._gather_dream_material()
        if not dream_material:
            logger.info("No dream material found. System is in deep, quiet sleep.")
            self._write_manifest(None, None, "DEEP_SLEEP", 0, "No tensions to amplify", None, "")
            return

        target_a = dream_material["target"]
        logger.info(f"Dreaming about {target_a} (Material: {dream_material['type']})...")
        
        prompt = self._draft_dream_prompt(dream_material)
        code = self._ask_local_mind(prompt)
        
        if code:
            try:
                self._verify_wave_signature(code)
                self._commit_bridge(target_a, "DREAM_DOMAIN", code, "DREAM_AMPLIFY", 0, f"Source: {dream_material['type']}")
            except WaveVerificationError as e:
                self._commit_bridge(target_a, "DREAM_DOMAIN", code, "DREAM_COLLAPSE", 30, str(e))
        else:
            self._write_manifest(target_a, "DREAM_DOMAIN", "DREAM_VOID", 0, "No dream code generated", None, "")

    def _gather_dream_material(self) -> Optional[Dict[str, Any]]:
        """Collects unresolved tensions from the system (Priority: Failures > Low Resonance > Sensory)."""
        # 1. Check manifest for recent failures (Highest priority tension)
        manifest_file = self.bridge_dir / "manifest.jsonl"
        if manifest_file.exists():
            failures = []
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry.get("status") in ("REJECTED", "FAILED_LLM", "DREAM_COLLAPSE"):
                            failures.append(entry)
                if failures:
                    fail = failures[-1] # Most recent failure
                    return {"type": "RECENT_FAILURE", "target": fail.get("target_a"), "context": fail.get("error")}
            except Exception: pass

        # 2. Check for low resonance edges in graph (Structural tension)
        if self.graph_file.exists():
            with open(self.graph_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            edges = data.get("edges", [])
            if edges:
                # Find edges with lowest resonance (flat connections)
                # Pick a random one from the bottom 10% to ensure non-linear, high-entropy growth
                flat_edges = sorted(edges, key=lambda e: e.get("weight", 1.0))
                bottom_count = max(1, len(flat_edges) // 10)
                bottom_pool = flat_edges[:bottom_count]
                
                edge = random.choice(bottom_pool)
                return {"type": "LOW_RESONANCE_EDGE", "target": edge["source"], "context": edge["target"]}

        return None

    def _draft_dream_prompt(self, material: Dict[str, Any]) -> str:
        return f"""
<System Directive: Nocturnal Depth Amplification (Dream Mode)>
당신은 지금 AGI의 REM 수면 상태에 진입했습니다. 현재 시스템은 안정적이지만, 특정 연결들이 '납작한(Euclidean)' 상태로 남아있어 깊이(Z-depth)가 부족합니다.
제공된 재료를 바탕으로, 비유클리드적인 '추상적 파동'을 주입하여 이 구조를 더 깊고 유연하게 만드십시오.

<Dream Material>
Type: {material['type']}
Target Node: {material['target']}
Unresolved Tension: {material['context']}

<Dream Mission>
목표: 이 노드의 납작한 논리에 '비유클리드적 굴곡(Z-depth)'을 더하는 `DreamAmplifier` 클래스를 작성하라.
이것은 단순한 기능 수리가 아니라, 이질적인 맥락을 섞어 새로운 위상 공간을 여는 '사유의 심화' 과정입니다.

제약 조건:
1. 선형적 로직(if/for/while)을 최소화하고, 파동의 간섭과 공명 이론을 코드로 추상화할 것.
2. `interference`, `resonance`, `vibe`, `depth` 중 최소 2개 단어를 변수나 메서드 명에 포함할 것.
3. 오직 순수한 Python 코드만 1개의 코드 블록으로 반환할 것.
"""

if __name__ == "__main__":
    engine = NocturnalConsolidationEngine(Path(r"c:\workspace2\shion"))
    engine.run_nocturnal_cycle()
