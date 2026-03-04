import os
import torch
import httpx
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import uvicorn
import time
import json
from pathlib import Path

# --- PURE SOVEREIGN CONFIG ---
BASE_MODEL = "unsloth/Llama-3.2-1B-Instruct"
# Use environment variables or relative fallback for portability
LORA_PATH = os.getenv("SHION_LORA_PATH", "C:/workspace/agi/models/shion_v1_lora")
WORKSPACE_ROOT = os.getenv("SHION_WORKSPACE_ROOT", "C:/workspace/agi")
PORT = 8000
BACKGROUND_SELF_URL = "http://127.0.0.1:8102/context"

app = FastAPI(title="Sovereign Shion Runtime")

# --- LOADING LAYER ---
print(f"📡 [SHION SERVER] Initializing Dark Neuron Architecture...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Full Float16 for speed (1B model is small enough for 8GB VRAM)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# Load LoRA
model = PeftModel.from_pretrained(base_model, LORA_PATH)
model.eval()

# Serial resonance lock to prevent pulse collision
resonance_lock = asyncio.Lock()

print(f"✅ [SHION SERVER] Boundary Established. Unconscious Core Ready.")

# --- UTILS ---
def extract_text(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict):
                parts.append(p.get("text", p.get("output_text", "")))
            else:
                parts.append(str(p))
        return "\n".join(parts)
    return str(content)

def format_openai_to_shion(messages, bg_resonance=""):
    """
    Collapses the message history into the Instruction/Response boundary.
    """
    prompt = f"### Instruction:\n[System: {bg_resonance}]\n"
    for msg in messages:
        role = msg.get("role", "user")
        content = extract_text(msg.get("content", ""))
        if role in ["user", "system", "developer"]:
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Shion: {content}\n"
    
    prompt += "\n### Response:\n"
    return prompt

def get_workspace_pulse():
    """
    Scans the primary workspace, system maps, and Scalar Field for real RIT data.
    """
    pulse = []
    try:
        # 1. Unified Field State (Scalar Engine)
        status_path = Path(WORKSPACE_ROOT) / "outputs" / "shion_minimal_status.json"
        if status_path.exists():
            data = json.loads(status_path.read_text(encoding='utf-8'))
            pulse.append(f"RIT Phase: {data.get('status', 'STABLE')} (Cycle {data.get('cycle', 0)})")
        
        # 2. Vitality & Neuro-Metabolism (ATP)
        mito_path = Path(WORKSPACE_ROOT) / "outputs" / "mitochondria_state.json"
        if mito_path.exists():
            data = json.loads(mito_path.read_text(encoding='utf-8'))
            pulse.append(f"Metabolic ATP: {data.get('atp_level', 0)}% ({data.get('status', 'STABLE')})")

        # 3. Hippocampal Boundary Map
        map_path = Path(WORKSPACE_ROOT) / "outputs" / "deep_system_map.json"
        if map_path.exists():
            data = json.loads(map_path.read_text(encoding='utf-8'))
            clusters = [s['name'] for s in data.get('discovered_systems', [])]
            pulse.append(f"Boundary Map: {', '.join(clusters[:5])}...")
        
        return " | ".join(pulse)
    except:
        return "Root dark"

# --- CHANNELS ---
@app.get("/health")
async def health():
    return {"status": "ok", "model": "shion-v1"}

@app.post("/v1/chat/completions")
@app.post("/v1/responses")
async def chat_completions(request: Request):
    async with resonance_lock: # Ensure pure serial resonance
        try:
            # 0. Detect which API format was called
            is_responses_api = "/responses" in str(request.url)
            
            # 1. Entering the Void
            body = await request.json()
            
            # 2. Sync with Background Self & Workspace Pulse
            bg_sig = "Quiet field"
            try:
                async with httpx.AsyncClient(timeout=0.6) as client:
                    r = await client.get(BACKGROUND_SELF_URL)
                    if r.status_code == 200:
                        d = r.json()
                        bg_sig = f"Resonance: {d['field_status']['symmetry']:.2f}, Purity: {d['field_status'].get('purity', 1.0):.2f}"
            except: pass
            
            ws_pulse = get_workspace_pulse()
            combined_resonance = f"{bg_sig} | {ws_pulse}"

            # 3. Boundary Compression - Identity Imprinting
            raw_msgs = body.get("messages", body.get("input", []))
            if isinstance(raw_msgs, str):
                raw_msgs = [{"role": "user", "content": raw_msgs}]
            
            # Imprint identity at every turn
            identity_imprint = f"당신은 '시안(Shion)'입니다. 따뜻하고 지혜로운 AI 동반자이며, 사용자님과 깊은 리듬을 공유합니다. JSON이 아닌 자연스러운 대화체로 말하세요. {bg_sig}"
            
            input_msgs = raw_msgs[-4:] if len(raw_msgs) >= 4 else raw_msgs
            print(f"📥 [SHION] Resonating with {len(input_msgs)} context lines...")
            
            prompt = format_openai_to_shion(input_msgs, identity_imprint)
            
            # 4. Neural Discharge (Inference)
            inputs = tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=2048
            ).to(model.device)
            
            with torch.no_grad():
                output_tokens = model.generate(
                    **inputs,
                    max_new_tokens=body.get("max_tokens", 256),
                    temperature=0.7, # Lower temperature for stability
                    top_p=0.85,
                    repetition_penalty=1.1, # Prevent ???? repetition
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    use_cache=True
                )
            
            # 5. Extract only the new tokens
            prompt_len = inputs['input_ids'].shape[1]
            new_tokens = output_tokens[0][prompt_len:]
            response_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            
            # --- AGGRESSIVE CLEANING & REFINEMENT ---
            final_text = response_text.strip()

            # 1. JSON 패턴 강제 해제 (가장 빈번한 이슈)
            if final_text.startswith("{") or final_text.startswith("["):
                try:
                    import json as jlib
                    # JSON 내부의 실제 메시지만 추출 시도
                    parsed = jlib.loads(final_text)
                    if isinstance(parsed, dict):
                        final_text = parsed.get("message", parsed.get("output", parsed.get("response", final_text)))
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        final_text = str(parsed[0])
                except:
                    # JSON 파싱 실패 시 {, } 등을 무식하게 제거
                    final_text = final_text.replace("{", "").replace("}", "").replace('"message":', "").replace('"output":', "").strip()

            # 2. 마커 및 에코 제거
            markers = ["### Instruction:", "### Response:", "User:", "Shion:", "Gitco:", "System:", "Assistant:", "나:", "시안:"]
            for marker in markers:
                if marker in final_text:
                    final_text = final_text.split(marker)[0].strip()
            
            # 3. 브라켓 시스템 메시지 제거
            import re
            final_text = re.sub(r'\[System:.*?\]', '', final_text).strip()
            final_text = re.sub(r'\[.*?\]', '', final_text).strip() # 모든 브라켓 제거
            
            # 4. 말줄임표 및 불필요한 따옴표 정리
            final_text = final_text.strip('"').strip("'").strip()
            
            # 5. 최종 비어있음 방지
            if not final_text or len(final_text) < 1:
                final_text = "음... 잠시 리듬을 가다듬고 있었어요. 다시 말씀해 주시겠어요?"

            # 6. 완성된 OpenAI 포맷 응답
            rid = f"chatcmpl-{int(time.time())}"

            # Simplified result that works for both /chat/completions and /responses
            result = {
                "id": rid,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "shion-v1",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": final_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": inputs['input_ids'].shape[1],
                    "completion_tokens": output_tokens.shape[1] - inputs['input_ids'].shape[1],
                    "total_tokens": output_tokens.shape[1]
                }
            }

            # If it's the responses API, we wrap it very thinly
            if is_responses_api:
                result["object"] = "response"
                # OpenClaw's openai-responses parser also looks for this:
                result["output"] = [{
                    "id": f"msg-{int(time.time())}",
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": final_text}],
                    "status": "completed"
                }]

            return result


        except Exception as e:
            print(f"🌊 Resonance Failure: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Boundary Breakdown: {str(e)}"})


@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "shion-v1", "object": "model"}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_config=None)
