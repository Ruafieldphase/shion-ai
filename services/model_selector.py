import logging
import os
import time
from pathlib import Path
import warnings
from typing import Any, Dict, List, Optional, Tuple

# Try importing both SDKs (Vertex AI and AI Studio)
try:
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel as VertexModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

try:
    # google.generativeai는 deprecated 되어 import 시 FutureWarning을 발생시킬 수 있다.
    # "접속 실패"로 오해되는 로그 노이즈를 줄이기 위해 import 구간에서만 경고를 숨긴다.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


RATE_LIMIT_MARKERS = ("429", "rate limit", "quota", "exhausted", "exceeded")


def _load_dotenv_value(name: str) -> str | None:
    """
    Process env에 키가 없더라도, 워크스페이스의 .env에서 값을 읽어올 수 있게 한다.
    - 값을 출력/로그하지 않는다.
    - 기존 env가 있으면 덮어쓰지 않는다.
    """
    try:
        root = Path(__file__).resolve().parents[1]  # C:\workspace\agi
        for env_path in (root / ".env_credentials", root / ".env"):
            if not env_path.exists():
                continue
            text = env_path.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in text:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                if k.strip() != name:
                    continue
                val = v.strip().strip('"').strip("'")
                return val or None
    except Exception:
        return None
    return None


class ModelSelector:
    """
    Centralized Gemini model selector.
    Supports both Vertex AI (GCP) and Google AI Studio (API Key).
    """

    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger("ModelSelector")
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        # Priority: 1. Local file (.env_credentials), 2. Process Environment
        self.api_key = (
            _load_dotenv_value("GOOGLE_API_KEY")
            or _load_dotenv_value("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        # Model preferences (Gemini 2.5/3.0 as default for future-proof intelligence)
        self.fast_model = os.getenv("GEMINI_FAST_MODEL", "gemini-2.5-flash")
        self.balanced_model = os.getenv("GEMINI_BALANCED_MODEL", "gemini-2.5-flash")
        self.vision_model = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")
        self.top_model = (
            os.getenv("GEMINI_TOP_TIER_MODEL")
            or "gemini-2.5-pro"
            or "gemini-3-pro-preview"
        )

        self.backend = "none" # 'vertex', 'genai', or 'shion'
        self.shion_url = os.getenv("SHION_MODEL_URL", "http://127.0.0.1:8000/v1")
        self._cache: Dict[str, Any] = {}
        # Feature flags / soft memory (avoid repeated 404 calls).
        # NOTE: do not call network from __init__ (human summaries should be network-free).
        self.supports_gemini_25_flash = "gemini-2.5-flash" in (self.fast_model + " " + self.balanced_model)
        self._model_blacklist_until: Dict[str, float] = {}
        self._last_error: Dict[str, Any] = {}
        self._init_backend()

    def _init_backend(self) -> None:
        """Initialize connection to either GenAI or Vertex AI."""
        # 0. Try Local Shion (Sovereign Core) first
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.shion_url.replace('/v1', '')}/health")
                if res.status_code == 200:
                    self.backend = "shion"
                    self.logger.info(f"Sovereign Shion Core Detected at {self.shion_url}")
                    return
        except Exception:
            pass

        # 1. Try GenAI (API Key) first if available
        if GENAI_AVAILABLE and self.api_key:
            try:
                # Prevent Vertex/GoogleAuth from picking up the Service Account credentials
                # which we know are failing/404ing for this project.
                # Only trust the API Key.
                if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                
                genai.configure(api_key=self.api_key)
                self.backend = "genai"
                # Keep init network-free: model availability is inferred by trial + failure cache.
                self.logger.info("Initialized Google AI Studio (GenAI) backend.")
                return
            except Exception as e:
                self._last_error = {"backend": "genai", "error_type": e.__class__.__name__, "message": str(e)[:400]}
                self.logger.warning(f"GenAI init failed: {e}")

        # 2. Fallback to Vertex AI (If not explicitly disabled)
        disable_vertex = os.getenv("DISABLE_VERTEX_AI", "false").lower() == "true"
        if VERTEX_AVAILABLE and self.project and not disable_vertex:
            try:
                vertexai.init(project=self.project, location=self.location)
                self.backend = "vertex"
                self.logger.info(f"Initialized Vertex AI backend ({self.project}/{self.location}).")
                return
            except Exception as e:
                self._last_error = {"backend": "vertex", "error_type": e.__class__.__name__, "message": str(e)[:400]}
                self.logger.error(f"Vertex init failed: {e}")

        self._last_error = {"backend": "none", "error_type": "NoBackend", "message": "No valid AI backend available"}
        self.logger.error("No valid AI backend available (check GOOGLE_API_KEY or Vertex credentials).")

    @property
    def available(self) -> bool:
        return self.backend != "none"

    def get_status_snapshot(self) -> Dict[str, Any]:
        """
        Network-free status snapshot for human_ops_summary / diagnostics.
        """
        return {
            "available": self.available,
            "backend": self.backend,
            "api_key_present": bool(self.api_key),
            "vertex_project_set": bool(self.project),
            "vertex_location": self.location,
            "blacklisted_models": len(self._model_blacklist_until),
            "last_error": self._last_error or {},
        }

    def _dedup(self, models: List[str]) -> List[str]:
        seen = set()
        ordered = []
        for m in models:
            if not m:
                continue
            if m in seen:
                continue
            seen.add(m)
            ordered.append(m)
        return ordered

    def select_candidates(
        self,
        *,
        intent: str = "",
        text_length: int = 0,
        urgency: bool = False,
        high_precision: bool = False,
        vision: bool = False,
    ) -> List[str]:
        """Return ordered model candidates for this request."""
        candidates: List[str] = []

        # Vision prefers higher fidelity, then balanced.
        if vision:
            if high_precision and self.top_model:
                candidates.append(self.top_model)
            candidates.append(self.vision_model)

        # Complex or long tasks prefer top/balanced.
        if high_precision or text_length > 800 or intent in ["CREATE", "MODIFY", "VERIFY"]:
            if self.top_model:
                candidates.append(self.top_model)
            candidates.append(self.balanced_model)

        # Default path.
        if not candidates:
            if urgency or text_length > 300:
                candidates.append(self.balanced_model)
            else:
                candidates.append(self.fast_model)

        # Fallbacks always available.
        for fallback in (self.balanced_model, self.fast_model):
            if fallback not in candidates:
                candidates.append(fallback)

        ordered = self._dedup(candidates)
        
        # Add version variants for robustness
        extras = []
        for m in ordered:
            if "flash" in m and "002" not in m:
                extras.append(m + "-002") # Try latest 002
                extras.append(m + "-001") # Try older 001
            elif "pro" in m and "002" not in m:
                extras.append(m + "-002")
                extras.append(m + "-001")
        
        # If local shion is available, prioritize it at the very top
        if self.backend == "shion":
            full_list = ["shion-v1"] + [m for m in full_list if m != "shion-v1"]
        
        return self._dedup(full_list)

    def _get_model(self, model_name: str) -> Any:
        if model_name in self._cache:
            return self._cache[model_name]

        model = None
        if self.backend == "genai":
            # AI Studio
            model = genai.GenerativeModel(model_name)
        elif self.backend == "shion":
            # [INTERNAL] Wrap the URL/Request for shion server
            class ShionWrapper:
                def __init__(self, url, logger):
                    self.url = url
                    self.logger = logger
                def generate_content(self, content, **kwargs):
                    import httpx
                    import json
                    # Construct OpenAI-like Chat Completion payload
                    prompt = content if isinstance(content, str) else str(content)
                    payload = {
                        "model": "shion-v1",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": kwargs.get("generation_config", {}).get("temperature", 0.7),
                        "max_tokens": 4096
                    }
                    try:
                        with httpx.Client(timeout=60.0) as client:
                            resp = client.post(f"{self.url}/chat/completions", json=payload)
                            resp.raise_for_status()
                            data = resp.json()
                            text = data["choices"][0]["message"]["content"]
                            
                            # Compatibility layer: mimics google.generativeai.types.GenerateContentResponse
                            class ShionResponse:
                                def __init__(self, t):
                                    self.text = t
                                    self._candidates = []
                                @property
                                def candidates(self): return self._candidates
                                
                            return ShionResponse(text)
                    except Exception as e:
                        self.logger.error(f"Shion Hub Connection Failed: {e}")
                        raise e
            model = ShionWrapper(self.shion_url, self.logger)
        
        if model:
            self._cache[model_name] = model
            return model
        raise RuntimeError(f"Cannot get model {model_name}: No backend initialized")

    def generate_content(
        self,
        content: Any,
        *,
        intent: str = "",
        text_length: int = 0,
        urgency: bool = False,
        high_precision: bool = False,
        vision: bool = False,
        generation_config: Optional[dict] = None,
        **kwargs,
    ) -> Tuple[Any, str]:
        """
        Try generation with prioritized models; falls back on quota/rate errors.
        Returns (response, model_used) or raises on total failure.
        """
        if self.backend == "none":
            raise RuntimeError("AI backend not configured")

        candidates = self.select_candidates(
            intent=intent,
            text_length=text_length,
            urgency=urgency,
            high_precision=high_precision,
            vision=vision,
        )

        errors = []
        # stdout print는 운영 로그/대시보드에 노이즈를 만들 수 있어 debug 로깅으로만 남긴다.
        self.logger.debug(f"Candidates: {candidates}")
        for model_name in candidates:
            # Skip temporarily blacklisted models (e.g., repeated 404).
            try:
                until = float(self._model_blacklist_until.get(model_name) or 0.0)
                if until and time.time() < until:
                    continue
            except Exception:
                pass
            try:
                model = self._get_model(model_name)
                # Ensure generation_config is compatible (GenAI sometimes strict)
                config = generation_config or {"temperature": 0.35}
                
                response = model.generate_content(
                    content,
                    generation_config=config,
                    **kwargs,
                )
                return response, model_name
            except Exception as e:
                msg = str(e)
                errors.append(f"{model_name}: {msg}")
                self._last_error = {"backend": self.backend, "model": model_name, "error_type": e.__class__.__name__, "message": msg[:800]}
                lower = msg.lower()
                # Rate limit handling
                if any(marker in lower for marker in RATE_LIMIT_MARKERS):
                    time.sleep(1.2)
                # 404 handling (try next model)
                if "404" in msg or "not found" in lower:
                    try:
                        # Avoid spamming the same unavailable model for a while.
                        self._model_blacklist_until[model_name] = time.time() + (6 * 60 * 60)
                    except Exception:
                        pass
                    continue
                continue

        raise RuntimeError(f"All Gemini candidates failed. Backends: {self.backend}. Last errors: {' | '.join(errors[-3:])}")

    def try_generate_content(self, *args, **kwargs) -> Tuple[Optional[Any], Optional[str]]:
        """Safe wrapper that returns (None, None) on failure."""
        try:
            return self.generate_content(*args, **kwargs)
        except Exception as e:
            self.logger.warning(f"Model selection failed: {e}")
            return None, None
