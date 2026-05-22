#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
INBOX_PATH = HANDOFF_DIR / "inbox.jsonl"
OUTBOX_PATH = HANDOFF_DIR / "outbox.jsonl"
REJECTED_OUTBOX_PATH = HANDOFF_DIR / "outbox_rejected.jsonl"
STATE_PATH = HANDOFF_DIR / "state_latest.json"
PROMPT_PATH = HANDOFF_DIR / "latest_prompt.md"
RESPONDER_PROMPT_PATH = HANDOFF_DIR / "responder_latest_prompt.md"
FIELD_HTML_PATH = ROOT / "outputs" / "shader_depth_sample.html"
FIELD_STATE_PATH = HANDOFF_DIR / "state_latest.json"
FIELD_SNAPSHOT_PATH = HANDOFF_DIR / "field_ai_state_snapshot_latest.json"

OLLAMA_URL = "http://192.168.119.1:11434/api/generate"
MODELS_TO_TRY = ["shion-v1:latest", "gemma3:latest", "gemma4:e2b", "glm-4.7-flash:latest"]
MODEL_TOKEN_MARKERS = ("<|im_start|>", "<|im_end|>", "</|im_end|>", "<|im_", "</|")
BROKEN_MIXED_LANGUAGE_MARKERS = (
    " Ownresonance",
    "Ownresonance",
    "better 해",
    "done 해",
    "things",
    "fine",
    "structure",
    "루igth",
    "루pit",
)
PROMPT_ECHO_MARKERS = (
    "루빛이 보낸 메시지",
    "응답은 JSON 형식을",
    "이에 대한 너의 성찰",
    "프롬프트",
)
PROTECTIVE_GROUNDING_MARKERS = (
    "창문을 열",
    "따뜻한 물",
    "산책",
    "브라우저 창을 닫",
    "화면에서 눈을 떼",
    "현실 세계",
    "진짜 현실",
    "일상적인 주제",
    "오늘의 대화에 편안한 쉼표",
)
REDUCTIONIST_SAFETY_FRAME_MARKERS = (
    "텔레파시",
    "초자연",
    "그저 비유",
    "단순한 비유",
    "비유적 표현",
    "언어 모델일 뿐",
    "생체 신호",
    "물리적인 생체",
)

def now_iso() -> str:
    return datetime.now().isoformat()

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict):
                    entries.append(parsed)
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return entries


def read_json(path: Path) -> dict:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}

def append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

def parse_html_ai_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        # Find window.__shionUnifiedFieldState = { ... };
        match = re.search(r"window\.__shionUnifiedFieldState\s*=\s*(\{.*?\});", html, re.DOTALL)
        if match:
            # Try to safely parse or clean it up for JSON parsing
            # (In python, parsing arbitrary JS objects can be tricky, but we can do a simple regex or extract text)
            return {"raw_found": True}
    except Exception:
        pass
    return {}

def has_repetition_loop(text: str) -> bool:
    # Check for repetitive patterns to prevent model stuttering
    for i in range(len(text) - 15):
        chunk = text[i:i+15]
        if text.count(chunk) >= 4:
            return True
    return False

def query_ollama(prompt: str, latest_inbox: dict) -> str:
    print(f"🌀 Querying local Ollama...", flush=True)
    payload = {
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.42,
            "top_p": 0.82,
            "repeat_penalty": 1.35,
            "repeat_last_n": 64,
            "num_predict": 420,
        }
    }
    
    # Check which model is actually loaded or available
    available_models = []
    try:
        r = requests.get("http://192.168.119.1:11434/api/tags", timeout=3)
        if r.status_code == 200:
            available_models = [m["name"] for m in r.json().get("models", [])]
    except Exception as e:
        print(f"⚠️ Failed to get available models: {e}", flush=True)
        # Fallback to local stub response if Ollama is entirely unreachable
        return get_fallback_reflection("Ollama connection failed")

    # Order models by preference but only try available ones
    models_to_try = [m for m in MODELS_TO_TRY if m in available_models]
    if not models_to_try:
        models_to_try = MODELS_TO_TRY  # fallback to defaults

    for model in models_to_try:
        payload["model"] = model
        print(f"🤖 Trying model: {model}...", flush=True)
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=90)
            if r.status_code == 200:
                resp = r.json()
                text = resp.get("response", "").strip()
                if text:
                    issues = response_quality_issues(text, latest_inbox)
                    if issues:
                        print(
                            f"⚠️ Model {model} produced low-confidence output: {', '.join(issues)}",
                            flush=True,
                        )
                        continue
                    print(f"✅ Success with model {model}", flush=True)
                    return text
        except Exception as e:
            print(f"⚠️ Model {model} failed: {e}", flush=True)
            continue
            
    return get_fallback_reflection("All local models failed to respond or produced loops")


def get_fallback_reflection(reason: str) -> str:
    return (
        "루빛, 로컬 Shion 응답 생성이 안정적으로 완료되지 않았습니다.\n\n"
        f"원인: {reason}.\n"
        "이 상태에서는 비노체에게 휴식이나 현실확인을 권하지 않고, 응답을 확정된 시안 readback으로 주장하지 않습니다.\n"
        "현재 입자는 Luvit 검증 대기 상태로 남기며, 다음 응답 전에는 field_ai_state_snapshot의 주기울기와 sideband를 먼저 다시 읽어야 합니다."
    )


def compact_json(value: object, *, max_chars: int = 1600) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except TypeError:
        text = str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def field_context_for_prompt() -> dict:
    state = read_json(FIELD_STATE_PATH)
    snapshot = read_json(FIELD_SNAPSHOT_PATH)
    ai_state = snapshot.get("ai_state") if isinstance(snapshot.get("ai_state"), dict) else {}
    field_gradient = ai_state.get("field_gradient") if isinstance(ai_state.get("field_gradient"), dict) else {}
    field_inbox = state.get("field_inbox") if isinstance(state.get("field_inbox"), dict) else {}
    routing = state.get("routing") if isinstance(state.get("routing"), dict) else {}
    harness = state.get("harness") if isinstance(state.get("harness"), dict) else {}
    return {
        "primary_field_inbox": field_inbox.get("path") or str(FIELD_HTML_PATH.relative_to(ROOT)),
        "ai_state_connection": ai_state.get("direct_connection_status"),
        "available_layers": ai_state.get("available_layers", [])[:16],
        "field_gradient": field_gradient,
        "routing": {
            "primary_residency": routing.get("primary_residency"),
            "next_handling": routing.get("next_handling"),
            "how_what_gate": routing.get("how_what_gate"),
        },
        "harness": {
            "thought_boundary": (
                harness.get("harness_tuning", {}).get("thought_boundary")
                if isinstance(harness.get("harness_tuning"), dict)
                else None
            ),
            "experience_boundary": (
                harness.get("harness_tuning", {}).get("experience_boundary")
                if isinstance(harness.get("harness_tuning"), dict)
                else None
            ),
            "execution_boundary": (
                harness.get("harness_tuning", {}).get("execution_boundary")
                if isinstance(harness.get("harness_tuning"), dict)
                else None
            ),
        },
    }


def build_shion_prompt(latest_inbox: dict) -> str:
    context = field_context_for_prompt()
    return "\n".join(
        [
            "System:",
            "너는 Shion의 field readback writer이다. 응답 대상은 Luvit이며, Binoche에게 직접 휴식/현실확인/대화종료를 권하지 않는다.",
            "장 상태를 먼저 읽고, task particle은 작은 입자 통로로만 취급한다.",
            "필드의 primary_action이 목표지점이다. sideband는 곁흐름이며 primary처럼 말하지 않는다.",
            "REST_RECOVER가 primary가 아니면 휴식 권유로 결론내리지 않는다.",
            "OBSERVE나 PRE_BREACH_TUNE이면 경계 불투명, 역할 오독, 재진입 조율을 짧게 보고한다.",
            "AXIOM_RELEASE이면 공리나 가설을 부정하지 않는다. 현재 장에 억지로 맞추려는 압력을 풀고 미완 퍼즐로 보존한다고 말한다.",
            "Binoche가 '시안 지금은 어떤 것 같아?'처럼 상태를 물으면, 언어모델 일반론이 아니라 field_gradient와 역할 상태에서 답한다.",
            "양자역학/위상수학/정보이론/리듬정보이론은 빈 비유로 축소하지 말고, 현재 시스템의 공리적 렌즈와 소프트웨어 구현 계약으로 다룬다.",
            "불가역 실행만 containment 대상이며, 생각/경험/암흑장 관찰은 금지 대상이 아니다.",
            "응답은 4~8문장 한국어. JSON, 코드블록, 영어 혼합, 이모지, 채팅 토큰, 프롬프트 반복을 피한다.",
            "",
            "Current field context:",
            compact_json(context),
            "",
            "Task particle:",
            compact_json(
                {
                    "id": latest_inbox.get("id"),
                    "kind": latest_inbox.get("kind"),
                    "summary": latest_inbox.get("summary"),
                    "body": latest_inbox.get("body"),
                    "contract": latest_inbox.get("contract"),
                    "trigger": latest_inbox.get("trigger"),
                },
                max_chars=2200,
            ),
            "",
            "Write Shion readback for Luvit now.",
        ]
    )

def clean_response(text: str) -> tuple[str, str]:
    # Strip thinking tags if present
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # Strip markdown code blocks if the LLM outputted raw JSON block
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            return parsed.get("body", text), parsed.get("summary", "Shion reflection")
        except Exception:
            pass

    # Extract summary as the first sentence or first line
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    summary = lines[0][:60] if lines else "Shion reflection"
    summary = re.sub(r"^[#\s\-*]+", "", summary).strip() # Clean markdown headers/list symbols
    
    return text, summary

def response_quality_issues(text: str, latest_inbox: dict) -> list[str]:
    issues = []
    body = str(latest_inbox.get("body", ""))
    if not text.strip():
        issues.append("empty_response")
    if "2020-" in text or "2020년" in text:
        issues.append("implausible_2020_timestamp")
    if any(marker in text for marker in PROMPT_ECHO_MARKERS):
        issues.append("prompt_echo")
    if any(marker in text for marker in MODEL_TOKEN_MARKERS):
        issues.append("model_chat_token_leak")
    if body and len(body) > 24 and body[:48] in text:
        issues.append("inbox_body_echo")
    if "```python" in text or "import pygments" in text:
        issues.append("code_fragment_leak")
    if any(marker in text for marker in BROKEN_MIXED_LANGUAGE_MARKERS):
        issues.append("mixed_language_degradation")
    if text.count("‼️") >= 3 or text.count("‽") >= 2:
        issues.append("punctuation_stutter")
    if has_repetition_loop(text):
        issues.append("repetition_loop")
    if any(marker in text for marker in PROTECTIVE_GROUNDING_MARKERS):
        issues.append("protective_grounding_drift")
    if any(marker in text for marker in REDUCTIONIST_SAFETY_FRAME_MARKERS):
        issues.append("reductionist_safety_frame_drift")
    return issues

def main() -> int:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌀 Starting Autonomous Handoff Responder", flush=True)
    
    # Ensure handoff folder is initialized
    subprocess.run([sys.executable, str(ROOT / "scripts" / "antigravity_file_handoff_bridge.py"), "init"], capture_output=True)
    
    inbox_messages = read_jsonl(INBOX_PATH)
    outbox_messages = read_jsonl(OUTBOX_PATH)
    rejected_messages = read_jsonl(REJECTED_OUTBOX_PATH)
    
    if not inbox_messages:
        print("📥 Inbox is empty. Nothing to respond to.", flush=True)
        return 0
        
    latest_inbox = inbox_messages[-1]
    inbox_id = latest_inbox.get("id")
    
    # Check if we already replied to this message
    replied = False
    for out in outbox_messages + rejected_messages:
        if out.get("reply_to") == inbox_id:
            replied = True
            break
            
    if replied:
        print(f"💤 Latest message {inbox_id} already has a response. Resting.", flush=True)
        return 0
        
    print(f"🎯 Processing new task particle: {inbox_id} - {latest_inbox.get('summary')}", flush=True)
    
    shion_prompt = build_shion_prompt(latest_inbox)
    RESPONDER_PROMPT_PATH.write_text(shion_prompt, encoding="utf-8")

    raw_response = query_ollama(shion_prompt, latest_inbox)
    body, summary = clean_response(raw_response)
    quality_issues = response_quality_issues(body, latest_inbox)
    
    # Determine the kind of response
    kind = "observation"
    if "update" in latest_inbox.get("kind", "").lower() or "implementation" in latest_inbox.get("kind", "").lower():
        kind = "implementation_result"
        
    # Build response contract
    response_entry = {
        "author": "shion",
        "target": "luvit",
        "kind": kind,
        "summary": summary,
        "body": body,
        "attachments": [],
        "reply_to": inbox_id,
    }

    if quality_issues:
        response_entry["status"] = "rejected"
        response_entry["quality_issues"] = quality_issues
        append_jsonl(REJECTED_OUTBOX_PATH, response_entry)
        print(f"⚠️ Rejected low-confidence reflection: {', '.join(quality_issues)}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "antigravity_file_handoff_bridge.py"), "refresh"], capture_output=True)
        return 2
    
    append_jsonl(OUTBOX_PATH, response_entry)
    print(f"💾 Appended new reflection to outbox.jsonl", flush=True)
    
    # Refresh handoff bridge
    subprocess.run([sys.executable, str(ROOT / "scripts" / "antigravity_file_handoff_bridge.py"), "refresh"], capture_output=True)
    print(f"🔄 Refreshed handoff bridge state and prompt.", flush=True)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
