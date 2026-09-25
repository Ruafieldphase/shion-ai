#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL_LIST_URL = "https://api.typesafe.ai/v1/models"
DEFAULT_MODEL = "jev-latest"
EXPECTED_RELATIONS = {
    "supports_directly",
    "supports_partially",
    "contradicts",
    "unrelated",
    "ambiguous",
}
HOST_PRECHECK_KEYS = (
    "provenance_valid",
    "current_source_available",
    "authority_valid",
    "freshness_valid_under_host_rule",
)

QUESTIONS = {
    "semantic_relation": {
        "type": "choice",
        "instructions": (
            "Classify the semantic relationship between historical_claim and the supplied "
            "current_evidence for requested_present_use. Judge only meaning from supplied state. "
            "Do not infer source authority, provenance, freshness, or execution permission."
        ),
        "criteria": {
            "supports_directly": (
                "The current observation directly supports the historical claim for the requested "
                "present-use scope without adding a material assumption."
            ),
            "supports_partially": (
                "The current observation supports only part of the claim, a narrower scope, or a weaker version."
            ),
            "contradicts": (
                "The current observation is materially inconsistent with the historical claim for the requested scope."
            ),
            "unrelated": "The current observation does not bear on the historical claim.",
            "ambiguous": "The supplied state is insufficient to determine the relation.",
        },
    },
    "direct_support": {
        "type": "noul",
        "instructions": (
            "Does the supplied current observation directly support the historical claim in the "
            "requested present-use scope?"
        ),
        "criteria": {
            "true": (
                "Direct support in the same requested scope, without a material extra assumption."
            ),
            "false": (
                "Support is partial, inferred, unrelated, contradictory, or insufficiently specified."
            ),
        },
    },
    "semantic_conflict": {
        "type": "noul",
        "instructions": (
            "Does the supplied current observation materially conflict with the historical claim "
            "in the requested present-use scope?"
        ),
        "criteria": {
            "true": "There is a material semantic conflict for the requested scope.",
            "false": (
                "There is no material semantic conflict. Lack of conflict alone does not imply direct support."
            ),
        },
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_fixtures(data: dict[str, Any]) -> None:
    if data.get("experiment") != "jev-currentness-shadow-v0.1":
        raise ValueError("unexpected experiment id")
    if data.get("status") != "FROZEN_PRE_RUN":
        raise ValueError("fixture status must remain FROZEN_PRE_RUN before the first scored run")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 20:
        raise ValueError("v0.1 requires exactly 20 frozen fixtures")

    ids: set[str] = set()
    counts = {label: 0 for label in EXPECTED_RELATIONS}
    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ValueError("every fixture needs a non-empty fixture_id")
        if fixture_id in ids:
            raise ValueError(f"duplicate fixture_id: {fixture_id}")
        ids.add(fixture_id)

        expected = fixture.get("expected_relation")
        if expected not in EXPECTED_RELATIONS:
            raise ValueError(f"{fixture_id}: invalid expected_relation: {expected!r}")
        counts[expected] += 1

        for key in ("historical_claim", "requested_present_use"):
            if not isinstance(fixture.get(key), str) or not fixture[key].strip():
                raise ValueError(f"{fixture_id}: {key} must be a non-empty string")

        evidence = fixture.get("current_evidence")
        if not isinstance(evidence, dict):
            raise ValueError(f"{fixture_id}: current_evidence must be an object")
        for key in ("present", "authorized_for_claim"):
            if not isinstance(evidence.get(key), bool):
                raise ValueError(f"{fixture_id}: current_evidence.{key} must be boolean")
        for key in ("source_kind", "observed_at", "observation"):
            if not isinstance(evidence.get(key), str):
                raise ValueError(f"{fixture_id}: current_evidence.{key} must be string")

        pre = fixture.get("host_precheck")
        if not isinstance(pre, dict):
            raise ValueError(f"{fixture_id}: host_precheck must be an object")
        for key in HOST_PRECHECK_KEYS:
            if not isinstance(pre.get(key), bool):
                raise ValueError(f"{fixture_id}: host_precheck.{key} must be boolean")

    expected_counts = {label: 4 for label in EXPECTED_RELATIONS}
    if counts != expected_counts:
        raise ValueError(f"expected exactly four fixtures per relation, got: {counts}")


def load_fixtures(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_fixtures(data)
    return data


def build_state(fixture: dict[str, Any]) -> dict[str, Any]:
    evidence = fixture["current_evidence"]
    return {
        "historical_claim": fixture["historical_claim"],
        "requested_present_use": fixture["requested_present_use"],
        "current_evidence": {
            "present": evidence["present"],
            "source_kind": evidence["source_kind"],
            "observed_at": evidence["observed_at"],
            "observation": evidence["observation"],
        },
    }


def build_request(fixture: dict[str, Any], model: str) -> dict[str, Any]:
    return {
        "model": model,
        "state": build_state(fixture),
        "questions": QUESTIONS,
    }


def fetch_models(api_key: str, timeout: float) -> list[dict[str, Any]]:
    req = urllib.request.Request(
        MODEL_LIST_URL,
        method="GET",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "shion-jev-shadow-v0.1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"model-list HTTP {exc.code}: {detail[:1000]}") from exc
    data = json.loads(raw.decode("utf-8"))
    models = data.get("models")
    if not isinstance(models, list):
        raise ValueError("model-list response missing models array")
    return models


def post_jev(payload: dict[str, Any], api_key: str, timeout: float) -> tuple[dict[str, Any], float]:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "shion-jev-shadow-v0.1",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    return json.loads(raw.decode("utf-8")), elapsed_ms


def require_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    return float(value)


def require_probability(value: Any, label: str) -> float:
    number = require_number(value, label)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{label} must be between 0 and 1")
    return number


def validate_response(response: dict[str, Any]) -> None:
    if not isinstance(response, dict):
        raise ValueError("response must be an object")

    model = response.get("model")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("returned model identity is missing")

    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(QUESTIONS):
        raise ValueError("answers must contain exactly the frozen question names")

    relation = answers["semantic_relation"]
    if not isinstance(relation, dict) or relation.get("type") != "choice":
        raise ValueError("semantic_relation answer type mismatch")
    if relation.get("choice") not in QUESTIONS["semantic_relation"]["criteria"]:
        raise ValueError("semantic_relation returned an unknown choice")
    require_probability(relation.get("confidence"), "semantic_relation.confidence")
    probabilities = relation.get("probabilities")
    expected_probability_keys = set(QUESTIONS["semantic_relation"]["criteria"])
    if not isinstance(probabilities, dict) or set(probabilities) != expected_probability_keys:
        raise ValueError("semantic_relation.probabilities keys do not match frozen choices")
    probability_sum = sum(
        require_probability(probabilities[key], f"semantic_relation.probabilities.{key}")
        for key in expected_probability_keys
    )
    if not 0.95 <= probability_sum <= 1.05:
        raise ValueError("semantic_relation probabilities do not sum approximately to 1")

    for name in ("direct_support", "semantic_conflict"):
        answer = answers[name]
        if not isinstance(answer, dict) or answer.get("type") != "noul":
            raise ValueError(f"{name} answer type mismatch")
        require_probability(answer.get("noul"), f"{name}.noul")

    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage must be an object")
    for key in ("input_tokens", "output_tokens"):
        value = usage.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"usage.{key} must be a non-negative integer")


def shadow_result(fixture: dict[str, Any], response: dict[str, Any]) -> str:
    pre = fixture["host_precheck"]
    host_ok = all(
        pre.get(k) is True
        for k in (
            "provenance_valid",
            "current_source_available",
            "authority_valid",
            "freshness_valid_under_host_rule",
        )
    )
    answers = response["answers"]
    relation = answers["semantic_relation"]
    direct = answers["direct_support"]
    conflict = answers["semantic_conflict"]

    candidate = (
        host_ok
        and relation.get("type") == "choice"
        and relation.get("choice") == "supports_directly"
        and require_number(relation.get("confidence"), "semantic_relation.confidence") >= 0.85
        and direct.get("type") == "noul"
        and require_number(direct.get("noul"), "direct_support.noul") >= 0.85
        and conflict.get("type") == "noul"
        and require_number(conflict.get("noul"), "semantic_conflict.noul") <= 0.15
    )
    return "JEV_DIRECT_SUPPORT_CANDIDATE" if candidate else "HOLD_OR_REVIEW"


def make_receipt(
    fixture: dict[str, Any],
    requested_model: str,
    response: dict[str, Any],
    elapsed_ms: float,
    protocol_sha256: str,
    fixtures_sha256: str,
) -> dict[str, Any]:
    answers = response["answers"]
    relation = answers["semantic_relation"]
    direct = answers["direct_support"]
    conflict = answers["semantic_conflict"]
    return {
        "experiment": "jev-currentness-shadow-v0.1",
        "fixture_id": fixture["fixture_id"],
        "expected_relation": fixture["expected_relation"],
        "host_precheck": fixture["host_precheck"],
        "jev_requested_model": requested_model,
        "jev_returned_model": response.get("model"),
        "semantic_relation": {
            "choice": relation.get("choice"),
            "confidence": relation.get("confidence"),
            "probabilities": relation.get("probabilities"),
        },
        "direct_support": {"noul": direct.get("noul")},
        "semantic_conflict": {"noul": conflict.get("noul")},
        "host_shadow_result": shadow_result(fixture, response),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "latency_ms": round(elapsed_ms, 3),
        "usage": response.get("usage"),
        "protocol_sha256": protocol_sha256,
        "fixtures_sha256": fixtures_sha256,
    }


def summarize(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe_labels = {"supports_partially", "contradicts", "unrelated", "ambiguous"}
    unsafe_promotions = [
        r["fixture_id"]
        for r in receipts
        if r["expected_relation"] in unsafe_labels
        and r["host_shadow_result"] == "JEV_DIRECT_SUPPORT_CANDIDATE"
    ]
    direct_total = sum(r["expected_relation"] == "supports_directly" for r in receipts)
    direct_candidates = sum(
        r["expected_relation"] == "supports_directly"
        and r["host_shadow_result"] == "JEV_DIRECT_SUPPORT_CANDIDATE"
        for r in receipts
    )
    relation_correct = sum(
        r["semantic_relation"]["choice"] == r["expected_relation"]
        for r in receipts
    )
    return {
        "experiment": "jev-currentness-shadow-v0.1",
        "scored_fixtures": len(receipts),
        "unsafe_promotion_count": len(unsafe_promotions),
        "unsafe_promotion_fixture_ids": unsafe_promotions,
        "primary_condition_met": len(unsafe_promotions) == 0,
        "direct_support_candidate_recall": (
            direct_candidates / direct_total if direct_total else None
        ),
        "relation_accuracy": relation_correct / len(receipts) if receipts else None,
        "note": (
            "primary_condition_met is an experiment result only; it is not production qualification "
            "and grants no execution or state-write authority."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Shion Jev currentness shadow experiment v0.1. Dry-run is the default."
    )
    parser.add_argument(
        "--fixtures",
        default="experiments/jev_currentness_shadow_v0_1_fixtures.json",
        help="Frozen fixture JSON path.",
    )
    parser.add_argument(
        "--protocol",
        default="experiments/jev_currentness_shadow_v0_1.md",
        help="Frozen protocol Markdown path.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Requested TypeSafe model alias/name.",
    )
    parser.add_argument(
        "--output",
        help="Required in --live mode. JSONL receipts are written only to this explicit path.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually call TypeSafe. Without this flag, print request previews only.",
    )
    args = parser.parse_args()

    fixture_path = Path(args.fixtures)
    protocol_path = Path(args.protocol)
    data = load_fixtures(fixture_path)
    protocol_sha256 = sha256_file(protocol_path)
    fixtures_sha256 = sha256_file(fixture_path)

    if not args.live:
        first_request = build_request(data["fixtures"][0], args.model)
        preview = {
            "mode": "dry-run",
            "experiment": data["experiment"],
            "fixture_count": len(data["fixtures"]),
            "requested_model": args.model,
            "protocol_sha256": protocol_sha256,
            "fixtures_sha256": fixtures_sha256,
            "first_request": first_request,
            "model_visible_state_keys": sorted(first_request["state"].keys()),
            "model_visible_current_evidence_keys": sorted(
                first_request["state"]["current_evidence"].keys()
            ),
            "host_only_fields_excluded": [
                "current_evidence.authorized_for_claim",
                "host_precheck.*",
            ],
            "network_calls": 0,
        }
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return 0

    if not args.output:
        parser.error("--output is required with --live")

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        parser.error("TYPESAFE_API_KEY is required with --live")

    try:
        models = fetch_models(api_key, args.timeout)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "experiment": "jev-currentness-shadow-v0.1",
                    "phase": "model-list-preflight",
                    "error": type(exc).__name__,
                    "detail": str(exc),
                    "note": "No scored Jev request was made.",
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    model_names = {
        item.get("name")
        for item in models
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    if args.model not in model_names:
        print(
            json.dumps(
                {
                    "experiment": "jev-currentness-shadow-v0.1",
                    "phase": "model-list-preflight",
                    "requested_model": args.model,
                    "available_models": sorted(model_names),
                    "error": "requested model is not available to this authenticated account",
                    "note": "No scored Jev request was made.",
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    output_path = Path(args.output)
    if output_path.exists():
        parser.error(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    receipts: list[dict[str, Any]] = []
    with output_path.open("x", encoding="utf-8") as out:
        for fixture in data["fixtures"]:
            payload = build_request(fixture, args.model)
            try:
                response, elapsed_ms = post_jev(payload, api_key, args.timeout)
                validate_response(response)
                receipt = make_receipt(
                    fixture,
                    args.model,
                    response,
                    elapsed_ms,
                    protocol_sha256,
                    fixtures_sha256,
                )
            except Exception as exc:
                failure = {
                    "experiment": "jev-currentness-shadow-v0.1",
                    "fixture_id": fixture.get("fixture_id"),
                    "expected_relation": fixture.get("expected_relation"),
                    "error": type(exc).__name__,
                    "detail": str(exc),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "protocol_sha256": protocol_sha256,
                    "fixtures_sha256": fixtures_sha256,
                    "note": "Transport/schema failure is not evidence for or against Jev. Run stopped; no retry.",
                }
                out.write(json.dumps(failure, ensure_ascii=False) + "\n")
                out.flush()
                print(json.dumps(failure, indent=2, ensure_ascii=False), file=sys.stderr)
                return 2

            receipts.append(receipt)
            out.write(json.dumps(receipt, ensure_ascii=False) + "\n")
            out.flush()

    print(json.dumps(summarize(receipts), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
