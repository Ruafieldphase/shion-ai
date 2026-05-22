#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "core"))

from llm_serving_profiles import ServingProfile, build_profile_manifest, profile_cases_for_benchmark

OUT_DIR = ROOT / "outputs" / "hermes"
OUT_JSON = OUT_DIR / "llm_serving_benchmark_latest.json"
OUT_JSONL = OUT_DIR / "llm_serving_benchmark.jsonl"
OUT_MD = OUT_DIR / "llm_serving_benchmark_latest.md"

DEFAULT_OLLAMA_BASE_URL = os.environ.get("SHION_WINDOWS_OLLAMA_BASE_URL", "http://192.168.119.1:11434")
DEFAULT_OLLAMA_MODEL = os.environ.get("SHION_WINDOWS_OLLAMA_MODEL", "gemma3:latest")
DEFAULT_VLLM_BASE_URL = os.environ.get("SHION_VLLM_BASE_URL")
DEFAULT_VLLM_MODEL = os.environ.get("SHION_VLLM_MODEL")
DEFAULT_SGLANG_BASE_URL = os.environ.get("SHION_SGLANG_BASE_URL")
DEFAULT_SGLANG_MODEL = os.environ.get("SHION_SGLANG_MODEL")


@dataclass(frozen=True)
class Provider:
    name: str
    api: str
    base_url: str
    model: str


PROMPT_CASES = profile_cases_for_benchmark()


def _request_json(
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
    method: Optional[str] = None,
) -> Dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method or ("POST" if payload is not None else "GET"),
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
        elapsed = time.perf_counter() - started
        return {
            "ok": True,
            "elapsed_seconds": round(elapsed, 4),
            "data": json.loads(raw) if raw else {},
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1200]
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "http_status": exc.code,
            "error": body,
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "error": str(exc),
        }


def _nvidia_smi() -> Dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"ok": False, "skipped": "nvidia_smi_checked_on_windows_host_only"}
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _parse_provider(raw: str) -> Provider:
    parts = [part.strip() for part in raw.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("provider must be name,api,base_url,model")
    name, api, base_url, model = parts
    if api not in {"ollama", "openai"}:
        raise argparse.ArgumentTypeError("provider api must be ollama or openai")
    return Provider(name=name, api=api, base_url=base_url.rstrip("/"), model=model)


def _default_providers() -> List[Provider]:
    providers = [Provider("windows_ollama", "ollama", DEFAULT_OLLAMA_BASE_URL.rstrip("/"), DEFAULT_OLLAMA_MODEL)]
    if DEFAULT_VLLM_BASE_URL and DEFAULT_VLLM_MODEL:
        providers.append(Provider("vllm", "openai", DEFAULT_VLLM_BASE_URL.rstrip("/"), DEFAULT_VLLM_MODEL))
    if DEFAULT_SGLANG_BASE_URL and DEFAULT_SGLANG_MODEL:
        providers.append(Provider("sglang", "openai", DEFAULT_SGLANG_BASE_URL.rstrip("/"), DEFAULT_SGLANG_MODEL))
    return providers


def _probe_provider(provider: Provider, timeout: float) -> Dict[str, Any]:
    if provider.api == "ollama":
        result = _request_json(f"{provider.base_url}/api/tags", timeout=timeout)
        models: List[str] = []
        if result.get("ok"):
            models = [
                item.get("name")
                for item in result.get("data", {}).get("models", [])
                if isinstance(item, dict) and item.get("name")
            ]
        return {
            "ok": bool(result.get("ok")) and provider.model in models,
            "endpoint_ok": bool(result.get("ok")),
            "models": models[:24],
            "error": result.get("error"),
            "http_status": result.get("http_status"),
        }
    result = _request_json(f"{provider.base_url}/v1/models", timeout=timeout)
    models = []
    if result.get("ok"):
        models = [
            item.get("id")
            for item in result.get("data", {}).get("data", [])
            if isinstance(item, dict) and item.get("id")
        ]
    return {
        "ok": bool(result.get("ok")) and (not models or provider.model in models),
        "endpoint_ok": bool(result.get("ok")),
        "models": models[:24],
        "error": result.get("error"),
        "http_status": result.get("http_status"),
    }


def _make_prompt(case: ServingProfile, variable: str) -> str:
    return case.build_prompt(variable)


def _call_ollama(provider: Provider, prompt: str, max_tokens: int, timeout: float) -> Dict[str, Any]:
    payload = {
        "model": provider.model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "temperature": 0,
            "num_predict": max_tokens,
            "num_ctx": 4096,
        },
    }
    result = _request_json(f"{provider.base_url}/api/generate", payload, timeout=timeout)
    if not result.get("ok") or not isinstance(result.get("data"), dict):
        return result
    data = result["data"]
    result["reading"] = {
        "response": str(data.get("response", "")).strip()[:240],
        "done": data.get("done"),
        "done_reason": data.get("done_reason"),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
        "prompt_eval_duration_ms": _ns_to_ms(data.get("prompt_eval_duration")),
        "eval_duration_ms": _ns_to_ms(data.get("eval_duration")),
    }
    result.pop("data", None)
    return result


def _call_openai(provider: Provider, case: ServingProfile, variable: str, max_tokens: int, timeout: float) -> Dict[str, Any]:
    payload = {
        "model": provider.model,
        "messages": case.build_openai_messages(variable),
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }
    result = _request_json(f"{provider.base_url}/v1/chat/completions", payload, timeout=timeout)
    if not result.get("ok") or not isinstance(result.get("data"), dict):
        return result
    data = result["data"]
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") if isinstance(choice, dict) else {}
    result["reading"] = {
        "response": str((message or {}).get("content", "")).strip()[:240],
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "usage": data.get("usage"),
    }
    result.pop("data", None)
    return result


def _ns_to_ms(value: Any) -> Optional[float]:
    if not isinstance(value, (int, float)):
        return None
    return round(value / 1_000_000, 3)


def _median(values: Iterable[float]) -> Optional[float]:
    items = [value for value in values if math.isfinite(value)]
    if not items:
        return None
    return round(statistics.median(items), 4)


def _mean(values: Iterable[float]) -> Optional[float]:
    items = [value for value in values if math.isfinite(value)]
    if not items:
        return None
    return round(statistics.mean(items), 4)


def _case_summary(samples: List[Dict[str, Any]], warmups: int) -> Dict[str, Any]:
    measured = samples[warmups:]
    latencies = [item["elapsed_seconds"] for item in measured if item.get("ok")]
    prompt_eval_ms = [
        item.get("reading", {}).get("prompt_eval_duration_ms")
        for item in measured
        if isinstance(item.get("reading"), dict) and item.get("reading", {}).get("prompt_eval_duration_ms") is not None
    ]
    first = latencies[0] if latencies else None
    later_median = _median(latencies[1:]) if len(latencies) > 1 else None
    speedup_pct = None
    if first and later_median is not None and first > 0:
        speedup_pct = round((first - later_median) / first * 100, 2)
    return {
        "ok_samples": len(latencies),
        "failed_samples": len(measured) - len(latencies),
        "latency_seconds": {
            "mean": _mean(latencies),
            "median": _median(latencies),
            "first_measured": round(first, 4) if first is not None else None,
            "later_median": later_median,
        },
        "ollama_prompt_eval_duration_ms": {
            "mean": _mean([float(value) for value in prompt_eval_ms if value is not None]),
            "median": _median([float(value) for value in prompt_eval_ms if value is not None]),
        },
        "cache_signal": {
            "type": "latency_warm_reuse_estimate",
            "speedup_pct_after_first_measured_sample": speedup_pct,
            "note": "This is a portable signal, not a provider-native cache-hit counter.",
        },
    }


def _run_case(
    provider: Provider,
    case: ServingProfile,
    iterations: int,
    warmups: int,
    max_tokens: int,
    timeout: float,
) -> Dict[str, Any]:
    samples: List[Dict[str, Any]] = []
    variables = case.tail_examples
    before_gpu = _nvidia_smi()
    for index in range(iterations + warmups):
        variable = variables[index % len(variables)]
        started_at = datetime.now().isoformat()
        if provider.api == "ollama":
            sample = _call_ollama(provider, _make_prompt(case, variable), max_tokens=max_tokens, timeout=timeout)
        else:
            sample = _call_openai(provider, case, variable, max_tokens=max_tokens, timeout=timeout)
        sample.update(
            {
                "started_at": started_at,
                "index": index,
                "phase": "warmup" if index < warmups else "measured",
                "variable_sha256_hint": hashlib.sha256(variable.encode("utf-8")).hexdigest()[:12],
            }
        )
        samples.append(sample)
    after_gpu = _nvidia_smi()
    return {
            "case": {
                "name": case.name,
                "role": case.role,
                "provider_fit": case.provider_fit,
                "stable_prefix_fingerprint": case.stable_prefix_fingerprint,
                "fixed_prefix_chars": len(case.stable_prefix),
                "variables": len(case.tail_examples),
            },
        "summary": _case_summary(samples, warmups=warmups),
        "gpu": {"before": before_gpu, "after": after_gpu},
        "samples": samples,
    }


def _build_recommendation(provider_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    for provider_result in provider_results:
        if provider_result.get("status") != "benchmarked":
            continue
        case_map = {case["case"]["name"]: case["summary"] for case in provider_result.get("cases", [])}
        unconscious = case_map.get("unconscious_fixed_prefix", {})
        conscious = case_map.get("conscious_varied_input", {})
        rows.append(
            {
                "provider": provider_result["provider"]["name"],
                "unconscious_median_seconds": unconscious.get("latency_seconds", {}).get("median"),
                "unconscious_cache_signal_pct": unconscious.get("cache_signal", {}).get(
                    "speedup_pct_after_first_measured_sample"
                ),
                "conscious_median_seconds": conscious.get("latency_seconds", {}).get("median"),
                "conscious_cache_signal_pct": conscious.get("cache_signal", {}).get(
                    "speedup_pct_after_first_measured_sample"
                ),
            }
        )
    return {
        "principle": "observe_context_fit_without_turning_numbers_into_rules",
        "routing_hint": {
            "unconscious": "Observe low fixed-prefix latency and positive reuse signal as low-resistance evidence.",
            "conscious": "Observe stable varied-input latency and fewer failures as low-resistance evidence.",
        },
        "rows": rows,
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# LLM Serving Benchmark",
        "",
        f"- Generated: `{payload['timestamp']}`",
        f"- Iterations: `{payload['config']['iterations']}` measured + `{payload['config']['warmups']}` warmup",
        f"- Output JSON: `{OUT_JSON}`",
        "",
        "## Results",
        "",
        "| Provider | Status | Unconscious median | Unconscious reuse signal | Conscious median | Conscious reuse signal |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    row_map = {row["provider"]: row for row in payload.get("recommendation", {}).get("rows", [])}
    for result in payload.get("providers", []):
        provider_name = result.get("provider", {}).get("name")
        row = row_map.get(provider_name, {})
        lines.append(
            "| {provider} | {status} | {u_med} | {u_sig} | {c_med} | {c_sig} |".format(
                provider=provider_name,
                status=result.get("status"),
                u_med=_fmt(row.get("unconscious_median_seconds")),
                u_sig=_fmt_pct(row.get("unconscious_cache_signal_pct")),
                c_med=_fmt(row.get("conscious_median_seconds")),
                c_sig=_fmt_pct(row.get("conscious_cache_signal_pct")),
            )
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- `unconscious_fixed_prefix` is the SGLang-shaped case: stable background prefix, small variable tail.",
            "- `conscious_varied_input` is the vLLM-shaped case: irregular front-channel prompts.",
            "- The numbers are an observation surface, not the decision maker.",
            "- The reuse signal is latency-based and portable. It is not a native cache-hit counter.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    return "" if value is None else f"{value}s"


def _fmt_pct(value: Any) -> str:
    return "" if value is None else f"{value}%"


def run_benchmark(providers: List[Provider], iterations: int, warmups: int, max_tokens: int, timeout: float) -> Dict[str, Any]:
    provider_results: List[Dict[str, Any]] = []
    for provider in providers:
        probe = _probe_provider(provider, timeout=min(timeout, 20))
        result: Dict[str, Any] = {
            "provider": {
                "name": provider.name,
                "api": provider.api,
                "base_url": provider.base_url,
                "model": provider.model,
            },
            "probe": probe,
        }
        if not probe.get("ok"):
            result["status"] = "skipped_endpoint_or_model_not_ready"
            provider_results.append(result)
            continue
        result["status"] = "benchmarked"
        result["cases"] = [
            _run_case(provider, case, iterations=iterations, warmups=warmups, max_tokens=max_tokens, timeout=timeout)
            for case in PROMPT_CASES
        ]
        provider_results.append(result)
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "llm_serving_benchmark_completed",
        "config": {
            "iterations": iterations,
            "warmups": warmups,
            "max_tokens": max_tokens,
            "timeout_seconds": timeout,
        },
        "providers": provider_results,
        "profile_manifest": build_profile_manifest(),
        "recommendation": _build_recommendation(provider_results),
        "permission": {
            "starts_servers": False,
            "external_api_cost": False,
            "writes_outputs_only": True,
            "irreversible_effect": False,
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    _write_markdown(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark local LLM serving endpoints for fixed-prefix unconscious loops vs varied conscious input."
    )
    parser.add_argument(
        "--provider",
        action="append",
        type=_parse_provider,
        help="Add provider as name,api,base_url,model. api is ollama or openai. May be repeated.",
    )
    parser.add_argument("--iterations", type=int, default=3, help="Measured requests per case.")
    parser.add_argument("--warmups", type=int, default=1, help="Warmup requests per case.")
    parser.add_argument("--max-tokens", type=int, default=32)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()

    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    if args.warmups < 0:
        parser.error("--warmups must be >= 0")

    providers = args.provider or _default_providers()
    payload = run_benchmark(
        providers=providers,
        iterations=args.iterations,
        warmups=args.warmups,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
    )
    print(json.dumps(payload["recommendation"], ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if any(result.get("status") == "benchmarked" for result in payload["providers"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
