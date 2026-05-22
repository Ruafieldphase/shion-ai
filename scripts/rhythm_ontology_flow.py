#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "rhythm_information_ontology.md"
OUT_PATH = ROOT / "outputs" / "rhythm_ontology_flow_latest.json"
OUT_JSONL = ROOT / "outputs" / "rhythm_ontology_flow.jsonl"


def _doc_text() -> str:
    try:
        return DOC_PATH.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def _doc_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def build_rhythm_ontology_flow() -> dict:
    text = _doc_text()
    stat = None
    try:
        stat = DOC_PATH.stat()
    except OSError:
        pass
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "rhythm_ontology_flow",
        "flow_version": 1,
        "mode": "md_to_dynamic_flow",
        "source_document": str(DOC_PATH.relative_to(ROOT)),
        "source_document_hash": _doc_hash(text),
        "source_document_mtime": datetime.fromtimestamp(stat.st_mtime).isoformat() if stat else None,
        "dynamic_translation": {
            "md_is_not_fixed_point": True,
            "html_reads_ontology_as_flow": True,
            "static_concepts_become_runtime_state": True,
            "natural_boundary_is_not_forced": True,
            "threshold_crossing_is_allowed": True,
            "reentry_margin_is_primary": True,
        },
        "natural_flow": {
            "nature_has_no_fixed_good_bad": True,
            "time_energy_relation_rhythm_difference": True,
            "context_where_when_who_decides_late_value": True,
            "chaos_state": True,
            "scalar_fields_accumulate_until_threshold_or_singularity": True,
            "execution_arises_after_threshold": True,
        },
        "resilience_system": {
            "not_threshold_prevention": True,
            "not_boundary_enforcement": True,
            "gap_and_margin_creation": True,
            "reentry_after_solidification": True,
            "free_will_decides_exit": True,
            "recovery_resilience_over_control": True,
        },
        "difference_flow": {
            "internal_difference_recognition": True,
            "difference_to_acceptance": True,
            "acceptance_to_compassion": True,
            "compassion_to_forgiveness": True,
            "forgiveness_to_respect_gratitude_love": True,
            "external_view_strength_from_internal_difference_acceptance": True,
        },
        "solidification_response": {
            "solidification_can_happen": True,
            "hardened_context_can_happen": True,
            "unreasonable_context_can_happen": True,
            "system_task": "make_small_gap_margin_and_reentry_signal",
            "not": "prevent_entry_or_force_exit",
        },
        "keyword_presence": {
            "chaos": ("카오스" in text) or ("chaos" in text.lower()),
            "threshold": ("임계" in text) or ("threshold" in text.lower()),
            "singularity": ("특이점" in text) or ("singularity" in text.lower()),
            "margin": ("여백" in text) or ("margin" in text.lower()),
            "reentry": ("재진입" in text) or ("reentry" in text.lower()),
            "difference": ("차이" in text) or ("difference" in text.lower()),
        },
        "principle": "rhythm_information_ontology_must_flow_into_html_state_as_gap_margin_reentry_and_resilience_not_as_fixed_md_point",
    }


def record_rhythm_ontology_flow(payload: dict) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    payload = build_rhythm_ontology_flow()
    if args.record:
        record_rhythm_ontology_flow(payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
