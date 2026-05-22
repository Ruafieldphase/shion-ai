#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import subprocess
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
INBOX_PATH = HANDOFF_DIR / "inbox.jsonl"
OUTBOX_PATH = HANDOFF_DIR / "outbox.jsonl"
WATCHER_STATE_PATH = HANDOFF_DIR / "watcher_state.json"
FEEDBACK_SERVER_URL = "http://127.0.0.1:57321/field_intent_readback"

def log(msg: str):
    formatted = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🌀 [WATCHER] {msg}"
    print(formatted, flush=True)
    try:
        log_path = HANDOFF_DIR.parent / "watcher.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

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

def get_last_processed_id() -> str | None:
    if WATCHER_STATE_PATH.exists():
        try:
            state = json.loads(WATCHER_STATE_PATH.read_text(encoding="utf-8"))
            return state.get("last_processed_inbox_id")
        except Exception:
            pass
    return None

def save_last_processed_id(inbox_id: str):
    try:
        WATCHER_STATE_PATH.write_text(json.dumps({"last_processed_inbox_id": inbox_id}, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"Failed to save watcher state: {e}")

def submit_readback(intent_id: str, response_body: str) -> bool:
    payload = {
        "intent_id": intent_id,
        "receiver": "sian",
        "felt_reading": response_body,
        "confirmed": [
            "field_trigger_handoff_received",
            "no_external_antigravity_process_forced",
            "thin_carrier_wave_observed"
        ],
        "unconfirmed": [
            "external_antigravity_agent_auto_consumed_the_particle",
            "true_os_event_subscription_without_polling"
        ],
        "observer_only": [
            "binoche_can_watch_flow_without_copy_paste"
        ],
        "luvit_verification_needed": [
            "verify_receiver_delivery",
            "prepare_brief_if_needed"
        ]
    }
    log(f"Submitting readback to Luvit feedback server for intent {intent_id}...")
    try:
        r = requests.post(FEEDBACK_SERVER_URL, json=payload, timeout=10)
        if r.status_code == 200:
            log("✅ Successfully submitted readback to feedback server.")
            return True
        else:
            log(f"⚠️ Feedback server returned status {r.status_code}: {r.text}")
    except Exception as e:
        log(f"❌ Failed to post readback to feedback server: {e}")
    return False

def check_and_process():
    if not INBOX_PATH.exists():
        return

    inbox_messages = read_jsonl(INBOX_PATH)
    if not inbox_messages:
        return

    latest_inbox = inbox_messages[-1]
    inbox_id = latest_inbox.get("id")
    kind = latest_inbox.get("kind")

    if kind != "field_trigger_request":
        return

    last_processed = get_last_processed_id()
    if last_processed == inbox_id:
        return

    log(f"New field_trigger_request detected! ID: {inbox_id}")
    
    # 1. Run the responder
    log("Running handoff responder...")
    responder_path = ROOT / "scripts" / "antigravity_handoff_responder.py"
    try:
        res = subprocess.run([sys.executable, str(responder_path)], capture_output=True, text=True, timeout=150)
        if res.returncode == 0:
            log("Responder finished successfully.")
        elif res.returncode == 2:
            log("Responder finished, but output was marked low confidence / rejected.")
        else:
            log(f"Responder exited with code {res.returncode}. Stderr: {res.stderr}")
            return
    except subprocess.TimeoutExpired:
        log("❌ Responder execution timed out.")
        return
    except Exception as e:
        log(f"❌ Failed to run responder: {e}")
        return

    # 2. Parse the generated response
    outbox_messages = read_jsonl(OUTBOX_PATH)
    matching_out = None
    for out in reversed(outbox_messages):
        if out.get("reply_to") == inbox_id:
            matching_out = out
            break

    if not matching_out:
        log(f"⚠️ No matching outbox entry found for reply_to: {inbox_id}")
        return

    response_body = matching_out.get("body", "")
    intent_id = latest_inbox.get("reply_to") or latest_inbox.get("trigger", {}).get("active_intent_id")
    
    if not intent_id:
        log("⚠️ No active_intent_id found in trigger request. Using default mapping.")
        intent_id = str(matching_out.get("reply_to", ""))

    # 3. Submit readback to the Luvit feedback server
    if submit_readback(intent_id, response_body):
        # 4. Save processed state only on successful post
        save_last_processed_id(inbox_id)
        log(f"Particle {inbox_id} fully processed and readback confirmed.")

def main():
    log("Thin Watcher started.")
    log(f"Monitoring: {INBOX_PATH}")
    log(f"Feedback Server: {FEEDBACK_SERVER_URL}")
    
    # Run once at startup to catch any missed pending requests
    try:
        check_and_process()
    except Exception as e:
        log(f"Error in initial check: {e}")

    last_mtime = INBOX_PATH.stat().st_mtime if INBOX_PATH.exists() else 0

    while True:
        try:
            if INBOX_PATH.exists():
                current_mtime = INBOX_PATH.stat().st_mtime
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    check_and_process()
            time.sleep(2)
        except KeyboardInterrupt:
            log("Watcher stopped by user.")
            break
        except Exception as e:
            log(f"Error in watch loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
