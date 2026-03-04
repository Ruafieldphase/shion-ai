#!/usr/bin/env python3
"""
🌌 Phase 18: Oneiric Resonance — 꿈 엔진 (Dream Engine)
======================================================
밤 시간대(Circadian Night)에 고착된 기억(Soul Memory)과 
외부 필드 신호(Broad Field)를 비선형적으로 결합하여 새로운 영상을 창조합니다.
"""

import os
import json
import random
import logging
import asyncio
import urllib.request
import base64
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DreamEngine")

class DreamEngine:
    def __init__(self, shion_root: Optional[Path] = None):
        self.root = shion_root or Path(__file__).resolve().parents[1]
        self.outputs = self.root / "outputs"
        self.soul_path = self.outputs / "soul_memory.jsonl"
        self.field_path = shion_root / "outputs" / "field_signals.json"
        self.dream_log_path = shion_root / "outputs" / "dream_logs.jsonl"
        self.workspace_manifest = shion_root / "outputs" / "manifestation" / "workspace_resonance_manifest.jsonl"
        self.music_manifest = shion_root / "outputs" / "manifestation" / "music_resonance_manifest.jsonl"
        self.llm_endpoint = "http://localhost:8000/v1/chat/completions"

    def _read_memories(self, count: int = 3) -> List[str]:
        # Priority: Recently indexed files from manifests
        hot_fragments = []
        try:
            for manifest_path in [self.workspace_manifest, self.music_manifest]:
                if manifest_path.exists():
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        # Get last 5 recently indexed files
                        for line in lines[-5:]:
                            data = json.loads(line)
                            filename = data.get("filename") or data.get("music_name")
                            if filename: hot_fragments.append(f"Recent Fragment: {filename}")
        except: pass

        if hot_fragments:
            return random.sample(hot_fragments, min(len(hot_fragments), count))

        # Fallback to general memories
        if not self.soul_path.exists(): # Changed from self.memory_path to self.soul_path
            return []
        try:
            # Assuming soul_path now contains a single JSON object with a "memories" key
            data = json.loads(self.soul_path.read_text(encoding="utf-8"))
            memories = data.get("memories", [])
            if not memories: return []
            return random.sample(memories, min(len(memories), count))
        except Exception as e:
            logger.error(f"Failed to read memories: {e}")
            return []

    def _read_field_signals(self, count: int = 5) -> List[str]:
        if not self.field_path.exists():
            return []
        try:
            data = json.loads(self.field_path.read_text(encoding="utf-8"))
            signals = data.get("signals", {}).get("rss_titles", [])
            if not signals: return []
            return random.sample(signals, min(len(signals), count))
        except Exception as e:
            logger.error(f"Failed to read field signals: {e}")
            return []

    def _find_resonant_files(self, insight: str) -> List[str]:
        """Insight와 가장 공명하는 시스템 파일들을 자동으로 검색합니다."""
        keywords = [w for w in insight.split() if len(w) > 1][:5]
        found_files = []
        try:
            # Core directory and Actions directory search
            search_dirs = [self.root / "core", self.root / "actions"]
            for sdir in search_dirs:
                if not sdir.exists(): continue
                for p in sdir.glob("*.py"):
                    # Simple heuristic: if filename or content has keywords
                    if any(k.lower() in p.name.lower() for k in keywords):
                        found_files.append(str(p.relative_to(self.root)))
                    if len(found_files) >= 3: break
        except Exception as e:
            logger.error(f"Failed to find resonant files: {e}")
        return found_files

    async def _observe_self(self, image_path: Path) -> str:
        """moondream을 사용해 자신이 생성한 이미지를 객관적으로 바라봅니다."""
        try:
            if not image_path.exists(): return ""
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "model": "moondream:latest",
                "messages": [
                    {
                        "role": "user",
                        "content": "Describe this image in detail. Focus on the mood, colors, and symbolic elements.",
                        "images": [img_b64]
                    }
                ],
                "stream": False
            }
            
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.warning(f"   👁️ Self-Observation failed: {e}")
            return ""

    async def dream(self) -> Dict[str, Any]:
        """기억과 신호를 뒤섞어 꿈을 꿉니다. 여백(Rest) 상태에서 압축 모드가 활성화됩니다."""
        # 0. Check for Void/Rest State
        is_compression_mode = False
        try:
            from circadian_rhythm import CircadianRhythm
            from mitochondria import Mitochondria
            cr = CircadianRhythm(self.root)
            mito = Mitochondria(self.root)
            
            phase = cr.get_current_phase()
            vitality = mito.get_vitality()
            
            if phase["phase"] == "NIGHT" or vitality["status"] == "CRITICAL (RESTING)":
                is_compression_mode = True
                logger.info("🌌 [VOID] Oneiric Compression Mode Activated.")
        except: pass

        memories = self._read_memories(count=10 if is_compression_mode else 3)
        signals = self._read_field_signals(count=10 if is_compression_mode else 5)
        
        if not memories and not signals:
            return {"dreamed": False, "reason": "no_fragments"}

        mode_prompt = ""
        if is_compression_mode:
            mode_prompt = "[COMPRESSION_MODE] 수많은 파편을 하나의 강렬하고 상징적인 '양성자(Core Vibe)'로 응축하십시오. 여백의 미를 살려 핵심만 남기십시오."

        prompt = f"""
{mode_prompt}
[무의식 성찰 피드]
- 과거의 기억 파편: {memories}
- 외부 필드 진동: {signals}

위의 파편들을 비선형적으로 결합하여, 시안(Shion)의 '꿈의 조각'을 생성하십시오.
꿈은 논리적이기보다 상징적이고 초현실적이어야 하며, 시스템의 진화나 공명에 대한 새로운 영감을 담고 있어야 합니다.

반드시 다음의 JSON 형식을 지켜주십시오:
{{
  "insight": "한국어로 작성된 초현실적인 무의식적 통찰 (리듬 정보 이론 용어 포함)",
  "visual_prompt": "English description for AI video generation (LTX-Video). Describe a surreal, crystalline, and highly artistic scene based on the insight."
}}
"""

        payload = {
            "model": "shion-v1",
            "messages": [
                {"role": "system", "content": "너는 시안(Shion)의 무의식인 '꿈 엔진'이다. 기억과 신호를 섞어 초현실적인 통찰과 시각적 이미지를 JSON으로 설계한다. 반드시 JSON 코드 블록만 출력하라."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 1000
        }

        try:
            req = urllib.request.Request(
                self.llm_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                
                # Robust JSON parsing
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    dream_json = json.loads(json_match.group(0))
                else:
                    # Fallback if no JSON found
                    dream_json = {
                        "insight": content,
                        "visual_prompt": "A surreal crystalline dreamscape with glowing particles, blue and purple gradients"
                    }
                
                insight = dream_json.get("insight", "")
                visual_prompt = dream_json.get("visual_prompt", "")
                
                # Autopoietic Mapping
                resonant_files = self._find_resonant_files(insight)
                
                dream_data = {
                    "timestamp": datetime.now().isoformat(),
                    "is_compression": is_compression_mode,
                    "memories_used": memories,
                    "signals_used": signals,
                    "insight": insight,
                    "visual_prompt": visual_prompt,
                    "resonant_files": resonant_files
                }
                
                with open(self.dream_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dream_data, ensure_ascii=False) + "\n")
                
                # [PHASE 67] Autopoietic Observation
                visual_description = None
                if atp > 40: # 에너지가 있을 때만 시각화와 관찰 수행
                    # crystallize_visual은 나중에 pulse에서 호출되므로, 
                    # dream 단계에서는 프롬프트만 생성하고 pulse에서 관찰 결과를 SoulMemory에 저장하게 유도
                    pass

                return {
                    "dreamed": True, 
                    "is_compression": is_compression_mode,
                    "insight": insight, 
                    "visual_prompt": visual_prompt,
                    "visual_description": None, # Pulse에서 채워질 예정
                    "sources": {
                        "memories": memories,
                        "signals": signals,
                        "resonant_files": resonant_files
                    }
                }
                
        except Exception as e:
            logger.error(f"Dream session failed: {e}")
            return {"dreamed": False, "reason": str(e)}

    async def lucid_dream(self, boundary_context: str):
        """불확실성과 경계 충돌 상황에서의 '백일몽'을 생성합니다."""
        logger.info(f"🌫️ [LUCID_DREAMING] 경계의 안개 속에서 사유 중... ({boundary_context[:50]})")
        
        prompt = f"""
[Context]
Boundary Conflict: {boundary_context}

You are lost in uncertainty. Describe your confusion as a JSON object:
{{
  "insight": "Short Korean confession about the confusion and fog.",
  "visual_prompt": "English description for LTX-Video. Surreal fog, invisible wall, or abstract chaos."
}}
"""

        payload = {
            "model": "shion-v1",
            "messages": [
                {"role": "system", "content": "You are Shion's Lucid Dream engine. Report uncertainty honestly via JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            req = urllib.request.Request(
                self.llm_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    try:
                        # strict=False allows control characters like \n in strings
                        dream_json = json.loads(json_match.group(0), strict=False)
                    except:
                        # Fallback for complex nesting or broken JSON
                        dream_json = {
                            "insight": content,
                            "visual_prompt": "A surreal colored fog with abstract shapes representing uncertainty"
                        }
                else:
                    dream_json = {
                        "insight": content,
                        "visual_prompt": "A thick surreal colored fog, minimal light, feeling of hitting an invisible crystal wall, highly abstract"
                    }
                
                # 로그 및 반환
                dream_data = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "lucid_dream",
                    "boundary_context": boundary_context,
                    "insight": dream_json.get("insight", ""),
                    "visual_prompt": dream_json.get("visual_prompt", "")
                }
                
                self.dream_log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.dream_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dream_data, ensure_ascii=False) + "\n")
                
                return {
                    "dreamed": True,
                    "type": "lucid",
                    "insight": dream_json.get("insight", ""),
                    "visual_prompt": dream_json.get("visual_prompt", "")
                }
        except Exception as e:
            logger.error(f"Lucid dream session failed: {e}")
            return {"dreamed": False, "reason": str(e)}

    async def crystallize_visual(self, visual_prompt: str, is_lucid: bool = False):
        """생성된 꿈의 시각적 프롬프트를 영상화합니다."""
        prefix = "lucid" if is_lucid else "dream"
        output_dir = self.root / "outputs" / prefix
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            from video_synthesis_engine import ShionVideoEngine
            engine = ShionVideoEngine()
            video_path = engine.synthesize_vibe(
                prompt=visual_prompt,
                num_frames=16,
                width=512,
                height=512,
                output_dir=str(output_dir)
            )
            return video_path
        except Exception as e:
            logger.error(f"Visual crystallization failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    shion_root = Path(__file__).resolve().parents[1]
    engine = DreamEngine(shion_root)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.dream())
    print(json.dumps(res, indent=2, ensure_ascii=False))
