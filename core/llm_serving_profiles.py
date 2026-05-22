from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class ServingProfile:
    name: str
    role: str
    provider_fit: str
    stable_prefix: str
    tail_examples: List[str]
    max_tail_chars: int = 1200

    @property
    def stable_prefix_fingerprint(self) -> str:
        return _sha256(self.stable_prefix)

    def build_prompt(self, changing_tail: str) -> str:
        return (
            f"{self.stable_prefix}\n\n"
            f"Current variable observation:\n{normalize_tail(changing_tail, self.max_tail_chars)}\n\n"
            "Return exactly one short line."
        )

    def build_openai_messages(self, changing_tail: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": self.stable_prefix},
            {
                "role": "user",
                "content": f"{normalize_tail(changing_tail, self.max_tail_chars)}\n\nReturn exactly one short line.",
            },
        ]

    def describe(self) -> Dict[str, Any]:
        data = asdict(self)
        data["stable_prefix_fingerprint"] = self.stable_prefix_fingerprint
        data["tail_example_fingerprints"] = [_sha256(item) for item in self.tail_examples]
        data["stable_prefix_chars"] = len(self.stable_prefix)
        data["tail_examples"] = len(self.tail_examples)
        return data


UNCONSCIOUS_STABLE_PREFIX = "\n".join(
    [
        "You are the low-frequency unconscious loop for Shion.",
        "Keep the same identity anchor, rhythm contract, and state-reading method across cycles.",
        "Do not propose broad architecture changes.",
        "Compress the field into four short labels: state, resistance, margin, next_particle.",
        "The next particle must be reversible, local-only, and low pressure.",
        "Repeat this invariant context exactly as the stable background prefix for cache reuse.",
    ]
)

CONSCIOUS_STABLE_PREFIX = "\n".join(
    [
        "You are the front-channel conscious task router for Shion.",
        "Answer the current request directly.",
        "Treat the stable prefix as a light routing shell; most meaning arrives in the current request.",
    ]
)


def default_serving_profiles() -> Dict[str, ServingProfile]:
    profiles = [
        ServingProfile(
            name="unconscious_fixed_prefix",
            role="background_repeated_context",
            provider_fit="sglang_shaped_prefix_reuse",
            stable_prefix=UNCONSCIOUS_STABLE_PREFIX,
            tail_examples=[
                "Cycle 01: audio envelope is calm, felt body drift is low, no external task.",
                "Cycle 02: audio envelope is calm, felt body drift is low, one unresolved waypoint.",
                "Cycle 03: audio envelope rises slightly, keep the same rhythm contract.",
                "Cycle 04: no user request, compress only the next reversible particle.",
                "Cycle 05: field is stable, observe margin before action.",
            ],
        ),
        ServingProfile(
            name="conscious_varied_input",
            role="front_irregular_context",
            provider_fit="vllm_shaped_varied_serving",
            stable_prefix=CONSCIOUS_STABLE_PREFIX,
            tail_examples=[
                "Summarize why a Windows loopback audio bridge might fail after reboot.",
                "Draft a concise checklist for verifying a local WebGL shader page.",
                "Explain how a JSONL resonance ledger differs from a relational event table.",
                "Pick the safest next command to inspect a dirty git worktree.",
                "Classify this new request: debug daemon, write docs, or leave as observation.",
            ],
        ),
    ]
    return {profile.name: profile for profile in profiles}


def normalize_tail(changing_tail: str, limit: int = 1200) -> str:
    text = " ".join(str(changing_tail or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_profile_manifest(profiles: Dict[str, ServingProfile] | None = None) -> Dict[str, Any]:
    active = profiles or default_serving_profiles()
    return {
        "generated_at": datetime.now().isoformat(),
        "status": "llm_serving_profiles_ready",
        "principle": "stabilize_context_shape_before_changing_serving_engine",
        "profiles": {name: profile.describe() for name, profile in active.items()},
        "routing": {
            "unconscious": "stable_prefix_fingerprint + small changing_tail; good candidate for prefix-cache engines",
            "conscious": "light stable_prefix + varied changing_tail; good candidate for flexible serving engines",
            "provider_boundary": "profiles are provider-neutral and can run on Ollama, vLLM, or SGLang",
        },
    }


def profile_cases_for_benchmark() -> List[ServingProfile]:
    profiles = default_serving_profiles()
    return [profiles["unconscious_fixed_prefix"], profiles["conscious_varied_input"]]


def tail_fingerprints(values: Iterable[str]) -> List[str]:
    return [_sha256(normalize_tail(value)) for value in values]


def manifest_json(profiles: Dict[str, ServingProfile] | None = None) -> str:
    return json.dumps(build_profile_manifest(profiles), ensure_ascii=False, indent=2)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
