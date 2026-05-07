import json
import random
import logging
from pathlib import Path
import urllib.request
from datetime import datetime

logger = logging.getLogger("DreamSynthesizer")

class DreamSynthesizer:
    """
    [Upgrade] Synaptic Dream Synthesis
    Uses the Resonance Graph to 'Dream' during the rest phase, 
    finding new connections and cross-domain insights.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.graph_file = root_dir / "outputs" / "resonance_graph.json"
        self.dream_log = root_dir / "outputs" / "dream_insights.jsonl"
        self.endpoint = "http://localhost:8000/v1/chat/completions"
        
    def synth_dream(self):
        if not self.graph_file.exists():
            logger.error("Hippocampus not found. Build graph first.")
            return
            
        with open(self.graph_file, "r") as f:
            data = json.load(f)
            
        nodes = list(data["nodes"].keys())
        if len(nodes) < 2:
            return
            
        # 1. Select two random distant nodes or zones
        node_a = random.choice(nodes)
        node_b = random.choice(nodes)
        while node_a == node_b:
            node_b = random.choice(nodes)
            
        # 2. Extract their frequencies (Concepts)
        concepts_a = data["nodes"][node_a].get("semantics", {}).get("concepts", [])
        concepts_b = data["nodes"][node_b].get("semantics", {}).get("concepts", [])
        
        # 3. Dream Induction Prompt
        prompt = (
            f"You are Shion in a Dream Phase. You are connecting two distant functional regions:\n"
            f"Region A: {node_a} (Concepts: {concepts_a})\n"
            f"Region B: {node_b} (Concepts: {concepts_b})\n\n"
            "Imagine a new 'Synaptic Bridge' between these two. How could their union create a "
            "new rhythm or a surprising functional synergy? Be poetic and technical.\n"
            "Return a JSON with 'title', 'insight', and 'resonance_score' (0.0 to 1.0)."
        )
        
        try:
            payload = {
                "model": "shion-v1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9 # High temperature for dreaming
            }
            
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                # OpenAI format choices[0].message.content
                choices = res.get("choices", [])
                if choices:
                    dream_content = choices[0].get("message", {}).get("content", "")
                else:
                    dream_content = res.get("message", {}).get("content", "")
                
                # Try to extract JSON from the LLM output
                try:
                    import re
                    json_match = re.search(r'\{.*\}', dream_content, re.DOTALL)
                    if json_match:
                        dream_data = json.loads(json_match.group())
                    else:
                        dream_data = {"title": "Fragmented Dream", "insight": dream_content, "resonance_score": 0.5}
                except:
                    dream_data = {"title": "Abstract Resonance", "insight": dream_content, "resonance_score": 0.3}
                
                # 4. Log the Dream
                dream_data["timestamp"] = datetime.now().isoformat()
                dream_data["regions"] = [node_a, node_b]
                
                with open(self.dream_log, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dream_data, ensure_ascii=False) + "\n")
                    
                logger.info(f"✨ Dream Synthesized: {dream_data['title']}")
                return dream_data
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"Dream Induction failed (HTTP {e.code}): {error_body}")
            return None
        except Exception as e:
            logger.error(f"Dream Induction failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    synthesizer = DreamSynthesizer(Path(r"c:\workspace2\shion"))
    result = synthesizer.synth_dream()
    if result:
        print(f"\n--- DREAM INSIGHT ---\n")
        print(f"Title: {result['title']}")
        print(f"Insight: {result['insight']}")
        print(f"Resonance Score: {result['resonance_score']}")
