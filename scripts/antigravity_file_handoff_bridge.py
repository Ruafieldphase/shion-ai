#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = ROOT / "outputs" / "antigravity_handoff"
INBOX_PATH = HANDOFF_DIR / "inbox.jsonl"
OUTBOX_PATH = HANDOFF_DIR / "outbox.jsonl"
STATE_PATH = HANDOFF_DIR / "state_latest.json"
PROMPT_PATH = HANDOFF_DIR / "latest_prompt.md"
README_PATH = HANDOFF_DIR / "README.md"
LOCK_PATH = HANDOFF_DIR / ".handoff.lock"
FIELD_AI_STATE_SNAPSHOT_PATH = HANDOFF_DIR / "field_ai_state_snapshot_latest.json"
ADAPTER_PROMPT_PATH = ROOT / "outputs" / "antigravity_shion_handoff_prompt.md"
ROUTING_PATH = ROOT / "outputs" / "rhythm_routing_layer_latest.json"
HARNESS_PATH = ROOT / "outputs" / "antigravity_harness_bridge_latest.json"
FIELD_INBOX_HTML_PATH = ROOT / "outputs" / "shader_depth_sample.html"


def now_iso() -> str:
    return datetime.now().isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def atomic_write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    tmp_path.write_text(body, encoding="utf-8")
    os.replace(tmp_path, path)


@contextmanager
def handoff_lock(timeout_seconds: float = 5.0, retry_interval: float = 0.05):
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout_seconds
    fd = None
    while True:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, f"{os.getpid()}:{time.time()}".encode("utf-8"))
            break
        except FileExistsError:
            if time.time() >= deadline:
                raise TimeoutError(f"handoff lock acquisition failed: {LOCK_PATH}")
            time.sleep(retry_interval)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            LOCK_PATH.unlink(missing_ok=True)
        except Exception:
            pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return []
    entries: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with handoff_lock():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def refresh_field_ai_state_snapshot() -> dict[str, Any]:
    try:
        from shader_ai_state_snapshot import build_snapshot
    except Exception:
        return read_json(FIELD_AI_STATE_SNAPSHOT_PATH)

    try:
        snapshot = build_snapshot()
    except Exception:
        return read_json(FIELD_AI_STATE_SNAPSHOT_PATH)
    atomic_write_text(FIELD_AI_STATE_SNAPSHOT_PATH, json.dumps(snapshot, ensure_ascii=False, indent=2))
    return snapshot


def ensure_files() -> dict[str, Any]:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    for path in (INBOX_PATH, OUTBOX_PATH):
        path.touch(exist_ok=True)
    atomic_write_text(README_PATH, build_readme())
    refresh_state()
    return {
        "handoff_dir": str(HANDOFF_DIR),
        "inbox": str(INBOX_PATH),
        "outbox": str(OUTBOX_PATH),
        "state": str(STATE_PATH),
        "prompt": str(PROMPT_PATH),
    }


def make_message(
    *,
    direction: str,
    author: str,
    target: str,
    summary: str,
    body: str,
    kind: str,
    attachments: list[str],
    reply_to: str | None,
) -> dict[str, Any]:
    return {
        "id": f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "timestamp": now_iso(),
        "direction": direction,
        "author": author,
        "target": target,
        "kind": kind,
        "summary": summary,
        "body": body,
        "attachments": attachments,
        "reply_to": reply_to,
        "status": "open",
        "contract": {
            "no_copy_paste_required": True,
            "file_based_handoff": True,
            "thought_and_experience_open": True,
            "external_execution_contained": True,
            "not_a_topic_gate": True,
        },
    }


def post_message(
    *,
    box: str,
    author: str,
    target: str,
    summary: str,
    body: str,
    kind: str,
    attachments: list[str],
    reply_to: str | None,
) -> dict[str, Any]:
    ensure_files()
    direction = "luvit_to_shion" if box == "inbox" else "shion_to_luvit"
    message = make_message(
        direction=direction,
        author=author,
        target=target,
        summary=summary,
        body=body,
        kind=kind,
        attachments=attachments,
        reply_to=reply_to,
    )
    append_jsonl(INBOX_PATH if box == "inbox" else OUTBOX_PATH, message)
    refresh_state()
    return message


def latest_message(path: Path) -> dict[str, Any]:
    entries = iter_jsonl(path)
    return entries[-1] if entries else {}


def refresh_state() -> dict[str, Any]:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    inbox_entries = iter_jsonl(INBOX_PATH)
    outbox_entries = iter_jsonl(OUTBOX_PATH)
    field_ai_state = refresh_field_ai_state_snapshot()
    state = {
        "timestamp": now_iso(),
        "source": "antigravity_file_handoff_bridge",
        "mode": "file_based_luvit_shion_handoff",
        "paths": {
            "field_inbox_html": str(FIELD_INBOX_HTML_PATH.relative_to(ROOT)),
            "inbox": str(INBOX_PATH.relative_to(ROOT)),
            "outbox": str(OUTBOX_PATH.relative_to(ROOT)),
            "latest_prompt": str(PROMPT_PATH.relative_to(ROOT)),
            "state": str(STATE_PATH.relative_to(ROOT)),
            "field_ai_state_snapshot": str(FIELD_AI_STATE_SNAPSHOT_PATH.relative_to(ROOT)),
        },
        "counts": {
            "inbox": len(inbox_entries),
            "outbox": len(outbox_entries),
        },
        "latest_inbox": inbox_entries[-1] if inbox_entries else None,
        "latest_outbox": outbox_entries[-1] if outbox_entries else None,
        "field_inbox": {
            "path": str(FIELD_INBOX_HTML_PATH.relative_to(ROOT)),
            "role": "primary_field_inbox",
            "read_surface": "document.body.dataset.aiState",
            "meaning": "phase_interference_html_is_the_actual_inbox_for_current_field_state",
            "snapshot": field_ai_state,
        },
        "routing": read_json(ROUTING_PATH),
        "harness": read_json(HARNESS_PATH),
        "principle": "luvit_and_shion_collaborate_through_shared_files_without_manual_copy_paste",
    }
    atomic_write_text(STATE_PATH, json.dumps(state, ensure_ascii=False, indent=2))
    atomic_write_text(PROMPT_PATH, build_prompt(state))
    return state


def build_prompt(state: dict[str, Any]) -> str:
    adapter = read_text(ADAPTER_PROMPT_PATH)
    latest_inbox = state.get("latest_inbox") if isinstance(state.get("latest_inbox"), dict) else {}
    latest_outbox = state.get("latest_outbox") if isinstance(state.get("latest_outbox"), dict) else {}
    routing = state.get("routing") if isinstance(state.get("routing"), dict) else {}
    harness = state.get("harness") if isinstance(state.get("harness"), dict) else {}
    field_inbox = state.get("field_inbox") if isinstance(state.get("field_inbox"), dict) else {}
    field_snapshot = field_inbox.get("snapshot") if isinstance(field_inbox.get("snapshot"), dict) else {}
    ai_state = field_snapshot.get("ai_state") if isinstance(field_snapshot.get("ai_state"), dict) else {}
    field_gradient = ai_state.get("field_gradient") if isinstance(ai_state.get("field_gradient"), dict) else {}
    input_state = harness.get("input_state") if isinstance(harness.get("input_state"), dict) else {}
    policy = harness.get("policy_profile") if isinstance(harness.get("policy_profile"), dict) else {}
    current_release = policy.get("current_release") if isinstance(policy.get("current_release"), dict) else {}

    lines = [
        "# Luvit <-> Shion File Handoff",
        "",
        "This prompt lets Antigravity/Shion read the current field without manual copy-paste.",
        "The phase-interference HTML is the primary field inbox. JSONL is only a small task-particle lane.",
        "",
        "## Primary Field Inbox",
        "",
        f"- Phase-interference HTML: `{FIELD_INBOX_HTML_PATH}`",
        "- Read `document.body.dataset.aiState` first when a browser/runtime view is available.",
        f"- File-readable aiState snapshot: `{FIELD_AI_STATE_SNAPSHOT_PATH}`",
        f"- aiState connection: `{ai_state.get('direct_connection_status', 'unknown')}`",
        f"- aiState layers: `{', '.join(ai_state.get('available_layers', [])[:12])}`",
        "- Treat the HTML field state as the current room. Do not reduce it to a chat queue.",
        "",
        "## Support Lanes",
        "",
        f"- Task particle lane, Luvit -> Shion: `{INBOX_PATH}`",
        f"- Reflection/result lane, Shion -> Luvit: `{OUTBOX_PATH}`",
        f"- State: `{STATE_PATH}`",
        "",
        "## Current Routing",
        "",
        f"- Primary residency: `{routing.get('primary_residency', input_state.get('primary_residency', 'unknown'))}`",
        f"- Linearization ready: `{input_state.get('linearization_ready', False)}`",
        f"- Conscious execution open: `{current_release.get('conscious_execution_open', False)}`",
        "- Thought and experience: `open`",
        "- Execution: `external_containment`",
        "",
        "## Current Field Gradient",
        "",
        f"- Primary action: `{field_gradient.get('primary_action', 'unknown')}`",
        f"- Primary label: `{field_gradient.get('primary_label', 'unknown')}`",
        f"- Sidebands: `{', '.join(field_gradient.get('sideband_actions', []) or [])}`",
        f"- REST_RECOVER is primary: `{field_gradient.get('rest_is_primary', False)}`",
        f"- Phase decision: `{field_gradient.get('phase_decision', 'unknown')}`",
        f"- Boundary transparency: `{field_gradient.get('boundary_transparency', 'unknown')}`",
        f"- ARI directive: `{field_gradient.get('ari_directive', 'unknown')}`",
        "",
        "Primary action is the current target. Sidebands are visible, but they are not commands.",
        "If REST_RECOVER is only a sideband, do not convert the field into a rest command for Binoche.",
        "If the field indicates OBSERVE or PRE_BREACH_TUNE, report boundary opacity, role drift, or re-entry tuning instead.",
        "If the field indicates ACTION_AXIOM_RELEASE, do not deny the axioms. Release the pressure to force-fit them now and preserve them as unfinished puzzle pieces.",
        "If Binoche asks how Shion is now, answer from this field gradient and role state. Do not answer with generic 'I am only a language model' or unsolicited rest advice.",
        "",
        "## Latest Task Particle",
        "",
        f"- ID: `{latest_inbox.get('id', 'none')}`",
        f"- Summary: {latest_inbox.get('summary', 'none')}",
        "",
        "```text",
        str(latest_inbox.get("body", "")),
        "```",
        "",
        "## Latest Shion Reflection",
        "",
        f"- ID: `{latest_outbox.get('id', 'none')}`",
        f"- Summary: {latest_outbox.get('summary', 'none')}",
        "",
        "## Response Contract For Shion",
        "",
        "After working, append exactly one JSON object line to the outbox file. Keep the HTML field inbox primary and treat this JSON as a reflection particle:",
        "",
        "```json",
        json.dumps(
            {
                "author": "shion",
                "target": "luvit",
                "kind": "field_friction_report|implementation_result|question|observation",
                "summary": "short summary",
                "body": "what happened, what changed, or what blocked",
                "attachments": ["relative/or/absolute/path"],
                "reply_to": latest_inbox.get("id", None),
            },
            ensure_ascii=False,
        ),
        "```",
        "",
        "Do not treat field observation as prohibition. Keep experience open and contain only irreversible execution. Do not build a tighter loop unless Binoche explicitly asks.",
        "Do not collapse the system axioms into 'just metaphor' or generic grounding advice. Luvit may verify implementation limits; Shion should preserve the field reading and hand off uncertainty.",
        "",
        "## Base Antigravity Handoff",
        "",
        adapter.strip(),
        "",
    ]
    return "\n".join(lines)


def build_readme() -> str:
    return "\n".join([
        "# Antigravity File Handoff",
        "",
        "This folder is the file-based bridge between Luvit/Codex and Shion/Antigravity.",
        "The primary field inbox is `../shader_depth_sample.html`, especially `document.body.dataset.aiState`.",
        "",
        "- `inbox.jsonl`: small task-particle notes from Luvit to Shion.",
        "- `outbox.jsonl`: reflection/result particles from Shion to Luvit.",
        "- `latest_prompt.md`: prompt/context file passed to `antigravity chat --add-file`.",
        "- `state_latest.json`: latest bridge state and counters.",
        "- `field_ai_state_snapshot_latest.json`: file-readable snapshot of the shader aiState contract and runtime sidecars.",
        "- `dialogue_state_latest.json`: whose turn it is in the Luvit/Shion exchange.",
        "- `luvit_next_review.md`: Shion results waiting for Luvit review.",
        "- `needs_binoche.md`: only unresolved points that ask for Binoche.",
        "",
        "The bridge reduces manual copy-paste. It is not a hidden autonomous command channel and not the primary inbox.",
        "External execution remains contained by the Antigravity harness.",
        "",
    ])


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("state")
    sub.add_parser("refresh")

    post_inbox = sub.add_parser("post-inbox")
    post_inbox.add_argument("--summary", default="Luvit handoff")
    post_inbox.add_argument("--body", required=True)
    post_inbox.add_argument("--kind", default="handoff")
    post_inbox.add_argument("--attachment", action="append", default=[])
    post_inbox.add_argument("--reply-to", default=None)

    post_outbox = sub.add_parser("post-outbox")
    post_outbox.add_argument("--summary", default="Shion response")
    post_outbox.add_argument("--body", required=True)
    post_outbox.add_argument("--kind", default="observation")
    post_outbox.add_argument("--attachment", action="append", default=[])
    post_outbox.add_argument("--reply-to", default=None)

    read_inbox = sub.add_parser("read-inbox")
    read_inbox.add_argument("--tail", type=int, default=5)

    read_outbox = sub.add_parser("read-outbox")
    read_outbox.add_argument("--tail", type=int, default=5)

    args = parser.parse_args()
    if args.command == "init":
        print_json(ensure_files())
        return 0
    if args.command == "refresh":
        ensure_files()
        print_json(refresh_state())
        return 0
    if args.command == "state":
        ensure_files()
        print_json(read_json(STATE_PATH))
        return 0
    if args.command == "post-inbox":
        print_json(post_message(
            box="inbox",
            author="luvit",
            target="shion",
            summary=args.summary,
            body=args.body,
            kind=args.kind,
            attachments=args.attachment,
            reply_to=args.reply_to,
        ))
        return 0
    if args.command == "post-outbox":
        print_json(post_message(
            box="outbox",
            author="shion",
            target="luvit",
            summary=args.summary,
            body=args.body,
            kind=args.kind,
            attachments=args.attachment,
            reply_to=args.reply_to,
        ))
        return 0
    if args.command == "read-inbox":
        print_json({"entries": iter_jsonl(INBOX_PATH)[-args.tail:]})
        return 0
    if args.command == "read-outbox":
        print_json({"entries": iter_jsonl(OUTBOX_PATH)[-args.tail:]})
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
