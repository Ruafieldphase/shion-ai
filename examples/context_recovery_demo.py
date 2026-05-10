from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


SAMPLE_TEXT = """
We keep repeating the same project background in every AI session.
The current goal is to make the public repository easier to enter.
Settled decisions: start small, do not run every daemon, preserve intent.
Files to inspect first: README.md, START_HERE.md, AI_READ_THIS_FIRST.md.
Unresolved question: which code path should become the first safe demo?
Risk: the assistant may jump into installation before reading context.
Next action should be one small context recovery note, not a full migration.
"""

STOPWORDS = {
    "the",
    "and",
    "to",
    "of",
    "a",
    "in",
    "is",
    "it",
    "for",
    "that",
    "this",
    "with",
    "as",
    "be",
    "or",
    "not",
    "every",
    "should",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text)
        if token.lower() not in STOPWORDS
    ]


def collect_repeated_lines(lines: list[str]) -> list[str]:
    normalized = [line.strip() for line in lines if line.strip()]
    counts = Counter(normalized)
    return [line for line, count in counts.items() if count > 1]


def collect_marked_lines(lines: list[str], markers: tuple[str, ...]) -> list[str]:
    selected = []
    for line in lines:
        lower = line.lower()
        if any(marker in lower for marker in markers):
            selected.append(line.strip())
    return selected


def build_context_recovery_note(text: str) -> str:
    lines = text.splitlines()
    keywords = [word for word, _ in Counter(tokenize(text)).most_common(8)]
    repeated_lines = collect_repeated_lines(lines)
    current_goal = collect_marked_lines(lines, ("current goal", "goal:"))
    settled = collect_marked_lines(lines, ("settled", "decision", "decided"))
    inspect_first = collect_marked_lines(lines, ("inspect first", "read first", "files to inspect", "context to inspect"))
    unresolved = collect_marked_lines(lines, ("unresolved", "question", "todo", "risk"))
    action_hints = collect_marked_lines(lines, ("next", "action", "test", "demo"))

    def section(title: str, items: list[str], fallback: str) -> list[str]:
        body = [f"## {title}"]
        if items:
            body.extend(f"- {item}" for item in items)
        else:
            body.append(f"- {fallback}")
        return body

    output = ["# Context Recovery Note", ""]
    output.extend(section("Current Goal", current_goal or ([", ".join(keywords)] if keywords else []), "No explicit goal found. Ask for the current direction before editing."))
    output.append("")
    output.extend(section("Settled Decisions", settled, "No explicit settled decisions found. Ask before reopening assumptions."))
    output.append("")
    output.extend(section("Files Or Context To Inspect First", inspect_first, "No inspect-first context found. Read the smallest available project anchor first."))
    output.append("")
    output.extend(section("Unresolved Questions", unresolved, "No unresolved questions marked. Preserve ambiguity instead of forcing closure."))
    output.append("")
    output.extend(section("What Not To Reopen Unless Evidence Changes", repeated_lines, "Do not reopen settled decisions or expand automation unless new evidence changes the direction."))
    output.append("")
    output.extend(section("Next Smallest Action", action_hints[:3], "Write one first-particle test before installing or automating."))
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a small context recovery note without models, APIs, or credentials.")
    parser.add_argument("input", nargs="?", help="Optional text file to analyze. Uses an embedded sample when omitted.")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = SAMPLE_TEXT

    print(build_context_recovery_note(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
