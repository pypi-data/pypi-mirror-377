# skote/__init__.py
"""
Skotergy public API and bootstrap.

Design goals:
- Stable top-level API: run(), configure(), session() — minimal friction to adopt.
- Hardware portability: backend registry (CUDA/ROCm/Level-Zero/Vulkan/CPU) with probing & preference.
- Feature flags: graph bucketing, unified paging memory (UPM), scheduler (continuous batching + QoS),
  speculative decoding, and attention kernel selection (auto/FA-3/SDPA/FA-2).
- Metrics and plugins: single place to wire telemetry and load optional extensions.
"""

from __future__ import annotations

import os
import json
import logging
import importlib
import contextlib
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Tuple

__all__ = [
    "VERSION",
    "SkoteConfig",
    "configure",
    "get_config",
    "enable",
    "disable",
    "register_backend",
    "list_backends",
    "select_best_backend",
    "SkoteSession",
    "session",
    "run",
    "get_logger",
]

# --------------------------- Version & Logger ---------------------------

VERSION: str = "0.1.0-dev"

# Keep a shared handler but return per-name loggers; avoids earlier "one global logger" pitfall.
_BASE_LOGGER: Optional[logging.Logger] = None
_LOGGERS: Dict[str, logging.Logger] = {}


def _install_base_logger(level_name: str) -> logging.Logger:
    global _BASE_LOGGER
    if _BASE_LOGGER is not None:
        return _BASE_LOGGER
    logger = logging.getLogger("skotergy")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    if not logger.handlers:
        h = logging.StreamHandler()
        fmt = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
        h.setFormatter(logging.Formatter(fmt))
        logger.addHandler(h)
    logger.propagate = False
    _BASE_LOGGER = logger
    return logger


def get_logger(name: str = "skotergy") -> logging.Logger:
    """Return a namespaced logger that shares the base handler/level."""
    level = os.environ.get("SKOTE_LOG_LEVEL", "INFO")
    base = _install_base_logger(level)
    if name in _LOGGERS:
        return _LOGGERS[name]
    lg = logging.getLogger(name)
    lg.setLevel(base.level)
    # Avoid duplicate handlers if user re-imports
    if not lg.handlers:
        for h in base.handlers:
            lg.addHandler(h)
    lg.propagate = False
    _LOGGERS[name] = lg
    return lg


log = get_logger("skotergy")


# --------------------------- Utilities ---------------------------

def _env_flag(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(key: str, sep: str = ",") -> List[str]:
    val = os.environ.get(key, "")
    return [x.strip() for x in val.split(sep) if x.strip()]


def _safe_import(mod: str) -> Optional[Any]:
    with contextlib.suppress(Exception):
        return importlib.import_module(mod)
    return None


# --------------------------- Config ---------------------------

AttentionKernel = Literal["auto", "fa3", "sdpa", "fa2"]
DType = Literal["auto", "fp8", "bf16", "fp16", "fp32"]
QoSMode = Literal["latency", "throughput", "balanced"]

DEFAULT_BUCKETS: List[int] = [2048, 4096, 8192, 16384, 32768]


@dataclass
class SkoteConfig:
    # Backend & portability
    backend_preference: List[str] = field(
        default_factory=lambda: _env_list("SKOTE_BACKENDS")
        or ["cuda", "rocm", "level_zero", "vulkan", "cpu"]
    )
    device_ids: Optional[List[int]] = None
    allow_fallback: bool = True

    # Feature flags
    # Note: env name kept for backward-compat (typo preserved intentionally).
    enable_graph_bucketing: bool = _env_flag("SKOTE_GRAPH_BUCKETING", True)
    enable_upm: bool = _env_flag("SKOTE_UPM", True)
    enable_scheduler: bool = _env_flag("SKOTE_SCHEDULER", True)
    enable_spec_decode: bool = _env_flag("SKOTE_SPEC_DECODE", False)

    # Performance knobs
    qos_mode: QoSMode = os.environ.get("SKOTE_QOS", "balanced")  # type: ignore
    max_context_buckets: List[int] = field(
        default_factory=lambda: (
            [int(x) for x in _env_list("SKOTE_BUCKETS")] or DEFAULT_BUCKETS
        )
    )
    batch_window_ms: int = int(os.environ.get("SKOTE_BATCH_WINDOW_MS", "16"))
    page_size_kv: int = int(os.environ.get("SKOTE_PAGE_KV", "16384"))
    page_size_apc: int = int(os.environ.get("SKOTE_PAGE_APC", "16384"))
    page_size_lora: int = int(os.environ.get("SKOTE_PAGE_LORA", "16384"))
    # Optional TMP page size; UPM falls back to KV size when absent.
    page_size_tmp: Optional[int] = None

    # Numerics / kernels
    attention_kernel: AttentionKernel = os.environ.get("SKOTE_ATTN", "auto")  # type: ignore
    dtype: DType = os.environ.get("SKOTE_DTYPE", "auto")  # type: ignore
    allow_mixed_precision: bool = _env_flag("SKOTE_MIXED_PREC", True)

    # Threading (honored by callers; not enforced here)
    intra_op_threads: Optional[int] = None
    inter_op_threads: Optional[int] = None

    # Telemetry & misc
    metrics_enabled: bool = _env_flag("SKOTE_METRICS", True)
    log_level: str = os.environ.get("SKOTE_LOG_LEVEL", "INFO")
    seed: Optional[int] = None
    plugin_paths: List[str] = field(default_factory=lambda: _env_list("SKOTE_PLUGINS"))
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


_GLOBAL_CONFIG = SkoteConfig()


def configure(**kwargs: Any) -> SkoteConfig:
    """Update global config (feature flags, backend preference, knobs)."""
    global _GLOBAL_CONFIG
    for k, v in kwargs.items():
        if hasattr(_GLOBAL_CONFIG, k):
            setattr(_GLOBAL_CONFIG, k, v)
        else:
            _GLOBAL_CONFIG.extra[k] = v
            log.debug("Config.extra set: %s=%r", k, v)
    # adjust logger level if provided
    if "log_level" in kwargs:
        for lg in (_BASE_LOGGER, *_LOGGERS.values()):
            if lg:
                lg.setLevel(getattr(logging, str(_GLOBAL_CONFIG.log_level).upper(), logging.INFO))
    return _GLOBAL_CONFIG


def get_config() -> SkoteConfig:
    return _GLOBAL_CONFIG


def enable(name: str) -> None:
    """Enable a feature flag by name."""
    cfg = get_config()
    key = name.strip().lower()
    if key in {"graph", "graph_bucketing", "bucketing"}:
        cfg.enable_graph_bucketing = True
    elif key in {"upm", "paging", "unified_paging"}:
        cfg.enable_upm = True
    elif key in {"sched", "scheduler", "batching"}:
        cfg.enable_scheduler = True
    elif key in {"spec", "spec_decode", "speculative"}:
        cfg.enable_spec_decode = True
    else:
        cfg.extra[key] = True


def disable(name: str) -> None:
    """Disable a feature flag by name."""
    cfg = get_config()
    key = name.strip().lower()
    if key in {"graph", "graph_bucketing", "bucketing"}:
        cfg.enable_graph_bucketing = False
    elif key in {"upm", "paging", "unified_paging"}:
        cfg.enable_upm = False
    elif key in {"sched", "scheduler", "batching"}:
        cfg.enable_scheduler = False
    elif key in {"spec", "spec_decode", "speculative"}:
        cfg.enable_spec_decode = False
    else:
        cfg.extra[key] = False


# --------------------------- Backend Registry ---------------------------

BackendProbe = Callable[[], bool]
BackendCreate = Callable[[SkoteConfig], Any]

_BACKENDS: Dict[str, Tuple[BackendProbe, BackendCreate, int]] = {}


def register_backend(
    name: str,
    probe: BackendProbe,
    create: BackendCreate,
    priority: int = 0,
) -> None:
    """
    Register a backend by name with a probe (availability) and create factory.
    Priority is used when preference list is empty or set to 'auto'.
    """
    key = name.strip().lower()
    _BACKENDS[key] = (probe, create, int(priority))
    log.debug("Registered backend: %s (priority=%d)", key, priority)


def list_backends() -> List[str]:
    return list(_BACKENDS.keys())


def _probe_torch_cuda() -> bool:
    torch = _safe_import("torch")
    if torch is None:
        return False
    with contextlib.suppress(Exception):
        return bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    return False


def _probe_torch_rocm() -> bool:
    torch = _safe_import("torch")
    if torch is None:
        return False
    # crude ROCm probe: hip version attribute
    return bool(getattr(getattr(torch, "version", None), "hip", None))


def _probe_level_zero() -> bool:
    # Prefer a minimal, permissive probe to avoid import cost
    dpctl = _safe_import("dpctl")
    return dpctl is not None


def _probe_vulkan() -> bool:
    # If vulkan sdk or torch._dynamo with vk is present (placeholder)
    return bool(os.environ.get("VK_ICD_FILENAMES") or os.environ.get("SKOTE_ALLOW_VK"))


def _probe_cpu() -> bool:
    return True


def _create_backend_stub(name: str) -> BackendCreate:
    def _factory(cfg: SkoteConfig) -> Dict[str, Any]:
        return {"name": name, "device": name, "info": "stub-backend"}
    return _factory


# Register default backends (real implementations plug in later)
register_backend("cuda", _probe_torch_cuda, _create_backend_stub("cuda"), priority=100)
register_backend("rocm", _probe_torch_rocm, _create_backend_stub("rocm"), priority=90)
register_backend("level_zero", _probe_level_zero, _create_backend_stub("level_zero"), priority=80)
register_backend("vulkan", _probe_vulkan, _create_backend_stub("vulkan"), priority=70)
register_backend("cpu", _probe_cpu, _create_backend_stub("cpu"), priority=10)


def select_best_backend(cfg: Optional[SkoteConfig] = None) -> str:
    """Choose an available backend based on preference list and probe results."""
    cfg = cfg or get_config()
    prefs = cfg.backend_preference or ["cuda", "rocm", "level_zero", "vulkan", "cpu"]
    for name in prefs:
        meta = _BACKENDS.get(name)
        if not meta:
            continue
        probe, _, _ = meta
        if probe():
            return name
    # fallback by priority
    by_prio = sorted(_BACKENDS.items(), key=lambda kv: -kv[1][2])
    for name, (probe, _, _) in by_prio:
        if probe():
            log.warning("Preference unavailable; falling back to backend=%s", name)
            return name
    if not cfg.allow_fallback:
        raise RuntimeError("No available backend found and fallback disabled.")
    return "cpu"


# --------------------------- Session & API ---------------------------

class SkoteSession:
    """
    A lightweight execution context that wires runtime subsystems (graph mgr, UPM, scheduler),
    the chosen backend, and optional metrics. Safe to construct before kernels are implemented.
    """

    def __init__(self, config: Optional[SkoteConfig] = None, backend_name: Optional[str] = None):
        self.config = config or get_config()
        # Keep base logger level in sync with config
        _install_base_logger(self.config.log_level)

        self.backend_name = backend_name or select_best_backend(self.config)
        self.backend = self._create_backend(self.backend_name)
        self.metrics = self._load_metrics()
        self.graphmgr = self._load_graphmgr()
        self.upm = self._load_upm()
        self.scheduler = self._load_scheduler()
        log.info("Skotergy session initialized (backend=%s, features: graph=%s, upm=%s, sched=%s)",
                 self.backend_name,
                 self.config.enable_graph_bucketing,
                 self.config.enable_upm,
                 self.config.enable_scheduler)

    # ---- Lazy loaders (safe if modules not implemented yet) ----

    def _create_backend(self, name: str) -> Any:
        probe, create, _ = _BACKENDS[name]
        if not probe():
            if self.config.allow_fallback:
                fb = select_best_backend(self.config)
                log.warning("Backend '%s' unavailable; using '%s'", name, fb)
                name = fb
            else:
                raise RuntimeError(f"Requested backend '{name}' is not available.")
        return create(self.config)

    def _load_graphmgr(self) -> Any:
        if not self.config.enable_graph_bucketing:
            return None
        mod = _safe_import("skote.runtime.graphmgr")
        if mod and hasattr(mod, "GraphManager"):
            return mod.GraphManager(self.config)
        return None

    def _load_upm(self) -> Any:
        if not self.config.enable_upm:
            return None
        mod = _safe_import("skote.runtime.upm")
        if mod and hasattr(mod, "UnifiedPagingMemory"):
            return mod.UnifiedPagingMemory(self.config)
        return None

    def _load_scheduler(self) -> Any:
        if not self.config.enable_scheduler:
            return None
        mod = _safe_import("skote.runtime.scheduler")
        if not (mod and hasattr(mod, "Scheduler")):
            return None
        try:
            # Preferred: ctor accepts config
            try:
                sched = mod.Scheduler(self.config)
            except TypeError:
                # Fallback: no-arg ctor, then attach config if possible
                sched = mod.Scheduler()
                with contextlib.suppress(Exception):
                    setattr(sched, "cfg", self.config)

            # Attach metrics if available
            if self.metrics and hasattr(sched, "attach_metrics"):
                with contextlib.suppress(Exception):
                    sched.attach_metrics(self.metrics)

            # Attach GraphManager for capture/replay (use method if provided; else set attribute)
            if self.graphmgr:
                if hasattr(sched, "attach_graph_manager"):
                    with contextlib.suppress(Exception):
                        sched.attach_graph_manager(self.graphmgr)
                else:
                    with contextlib.suppress(Exception):
                        setattr(sched, "_graphmgr", self.graphmgr)

            return sched
        except Exception:
            return None

    def _load_metrics(self) -> Any:
        if not self.config.metrics_enabled:
            return None
        mod = _safe_import("skote.runtime.metrics")
        if mod and hasattr(mod, "Metrics"):
            return mod.Metrics(self.config)
        return None

    # ---- Public APIs ----

    def run(
        self,
        model: Any,
        prompts: Iterable[str] | str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Minimal orchestration flow (safe placeholder):
        1) Normalize inputs; 2) (optional) route to bucket/graph; 3) enqueue via scheduler;
        4) collect metrics; 5) return outputs.
        Real kernel execution is plugged in later by runtime modules.
        """
        # normalize
        if isinstance(prompts, str):
            prompts = [prompts]

        # route to bucket (no-op if graphmgr missing)
        bucket_info: Optional[Dict[str, Any]] = None
        if self.graphmgr and hasattr(self.graphmgr, "route"):
            try:
                # pass through hints if present
                seq_lens = kwargs.pop("seq_lens", None)
                model_id = kwargs.get("model_id", "default")
                bucket_info = self.graphmgr.route(list(prompts), seq_lens=seq_lens, model_id=model_id)
                if self.metrics and hasattr(self.metrics, "record_route"):
                    self.metrics.record_route(bucket_info)
            except Exception as e:
                log.debug("graphmgr.route error (ignored in placeholder): %s", e)

        # schedule (no-op fallback)
        outputs: List[Dict[str, Any]] = []
        if self.scheduler and hasattr(self.scheduler, "submit"):
            outputs = self.scheduler.submit(model, list(prompts), bucket_info=bucket_info, **kwargs)
        else:
            # direct model call (user provided callable) as placeholder
            import time as _time
            t0 = _time.time()
            for p in prompts:
                with contextlib.suppress(Exception):
                    if callable(model):
                        outputs.append({"text": model(p), "prompt": p})
                    else:
                        outputs.append({"text": "", "prompt": p})
            t1 = _time.time()
            # metrics
            if self.metrics and hasattr(self.metrics, "record_batch"):
                self.metrics.record_batch(
                    inputs=list(prompts),
                    outputs=outputs,
                    extra={
                        "latency_ms": (t1 - t0) * 1000.0,
                        "lane": self.config.qos_mode,
                        "groups": 1,
                        "backend": self.backend_name,
                        "bucket": (bucket_info or {}).get("bucket", -1),
                    },
                )

        return {"outputs": outputs, "meta": {"backend": self.backend_name, "bucket": bucket_info}}

    # context manager convenience
    def __enter__(self) -> "SkoteSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        # flush metrics or cleanup if needed
        if self.metrics and hasattr(self.metrics, "flush"):
            with contextlib.suppress(Exception):
                self.metrics.flush()
        # stop scheduler thread if it exposes stop()
        if self.scheduler and hasattr(self.scheduler, "stop"):
            with contextlib.suppress(Exception):
                self.scheduler.stop()


# Global session helper (lightweight singleton for simple scripts)
_GLOBAL_SESSION: Optional[SkoteSession] = None


def session() -> SkoteSession:
    global _GLOBAL_SESSION
    if _GLOBAL_SESSION is None:
        _GLOBAL_SESSION = SkoteSession()
    return _GLOBAL_SESSION


def run(model: Any, prompts: Iterable[str] | str, **kwargs: Any) -> Dict[str, Any]:
    """
    Public entry point: skote.run(model, prompts, **kwargs)
    """
    return session().run(model, prompts, **kwargs)


# --------------------------- Plugin Loader ---------------------------

def _load_plugins(cfg: SkoteConfig) -> None:
    for path in cfg.plugin_paths:
        try:
            importlib.import_module(path)
            log.info("Loaded plugin: %s", path)
        except Exception as e:
            log.warning("Failed to load plugin '%s': %s", path, e)


# Auto-load plugins at import time
with contextlib.suppress(Exception):
    _load_plugins(get_config())
