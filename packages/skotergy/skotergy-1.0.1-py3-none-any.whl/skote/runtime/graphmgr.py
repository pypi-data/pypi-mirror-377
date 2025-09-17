# skote/runtime/graphmgr.py
"""
Graph Manager for Skotergy (device-scoped, per-device GraphCache)

Why this revision?
------------------
Your runtime is now multi-device aware (see devicemgr / launcher / scheduler).
CUDA Graphs (or any future backend graphs) are **device-local artifacts**:
a graph captured on device 0 cannot be replayed on device 1. The old manager
kept a single global cache keyed only by (model_id, backend, dtype, bucket,...),
which risks cross-device pollution and replay failures.

This revision:
- Maintains an **independent GraphCache per device** (device_index -> LRU).
- All capture/replay decisions are **scoped by device**.
- Capture & warmup discover devices through `DeviceManager` (zero-config).
- Works in single-GPU exactly as before (same API, same behavior).
- Backward compatible with callers that already compute `graph_id` (compact key):
  we keep the same compact id string; internally we pair it with the device id.

Key resilience/perf design (kept & improved):
- Capture only on "stable" buckets (env whitelist) and eager-bypass for small buckets.
- Single-flight capture per (device, key) to avoid thundering herd.
- Blacklist a (device, key) after capture failure for a TTL to prevent retry storms.
- Robust static I/O build & copy-into for replay (fixes previous partial-copy bug).
- Degrades to routing-only mode when no graph backend is available on that device.

Environment knobs (unchanged unless noted):
- SKOTE_GRAPH_CACHE_ITEMS       : per-device LRU size (default 64)
- SKOTE_GRAPH_CACHE_TTL         : TTL seconds (default 3600)
- SKOTE_GRAPH_BUCKETS_CAPTURE   : whitelist, e.g. "1024,2048,4096" (default derived)
- SKOTE_MIN_BUCKET_CAPTURE      : minimal bucket eligible for capture (default 8192)
- SKOTE_EAGER_SMALL_BUCKETS     : "1" => bypass capture for small buckets (default "1")
- SKOTE_GRAPH_BLACKLIST_TTL     : per-(device,key) blacklist seconds after failure (default 900)
- SKOTE_GRAPH_CAPTURE_LOG       : "1" => verbose capture/replay logging (default "0")
"""

from __future__ import annotations

import os
import time
import hashlib
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple, Protocol, runtime_checkable

try:
    import torch  # optional; handled gracefully
except Exception:  # pragma: no cover
    torch = None  # type: ignore

# Pull config/logger from top-level skote
from skote import get_config, get_logger, SkoteConfig

# Device plan (enumeration and backend info)
try:
    from skote.distributed.devicemgr import DeviceManager, BackendKind
except Exception:
    DeviceManager = None  # type: ignore
    class BackendKind:  # minimal fallback
        CUDA = "cuda"
        ROCM = "rocm"
        XPU  = "xpu"
        CPU  = "cpu"

log = get_logger("skotergy.graphmgr")


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def _now() -> float:
    return time.time()


def _stable_hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()  # stable, short


def _as_list_str(prompts: Iterable[str] | str) -> List[str]:
    if isinstance(prompts, str):
        return [prompts]
    return list(prompts)


def _parse_int_list(env_value: str) -> List[int]:
    out: List[int] = []
    for x in env_value.replace(";", ",").split(","):
        x = x.strip()
        if not x:
            continue
        try:
            out.append(int(x))
        except Exception:
            pass
    return sorted(set(out))


def _infer_device_index_from_args(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Optional[int]:
    """
    Best-effort extraction of a CUDA device index from example tensors.
    """
    def _scan(obj) -> Optional[int]:
        if torch is not None and torch.is_tensor(obj):
            if obj.device.type == "cuda" and obj.device.index is not None:
                return int(obj.device.index)
        if isinstance(obj, (list, tuple)):
            for e in obj:
                r = _scan(e)
                if r is not None:
                    return r
        if isinstance(obj, dict):
            for v in obj.values():
                r = _scan(v)
                if r is not None:
                    return r
        return None

    r = None
    for a in args:
        r = _scan(a)
        if r is not None:
            return r
    return _scan(kwargs)


# ---------------------------------------------------------------------
# Bucketing policy
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class BucketPolicy:
    """
    Length bucketing policy.
    - buckets: ascending list of target sequence lengths.
    - overflow: if True, anything > last bucket goes to an 'overflow' bucket.
    """
    buckets: List[int]
    overflow: bool = True

    def choose(self, length: int) -> Tuple[int, bool]:
        """
        Return (bucket_value, is_overflow).
        Pick the smallest bucket >= length; if none and overflow=True, return last bucket and mark overflow.
        """
        for b in self.buckets:
            if length <= b:
                return b, False
        # overflow
        if not self.overflow:
            return self.buckets[-1], True
        return self.buckets[-1], True


# ---------------------------------------------------------------------
# Graph cache records
# ---------------------------------------------------------------------

@dataclass
class GraphKey:
    """
    Canonical key for a compiled/captured graph.

    NOTE: To keep backward compatibility with existing callers that already
    compute a compact id, we DO NOT inject device_id into the compact string.
    Instead, device scoping is handled by **per-device caches** internally.
    """
    model_id: str
    backend: str
    dtype: str
    bucket: int
    attn_kernel: str = "auto"
    extra: str = ""  # reserved (e.g., kv_layout, tokenizer_id, etc.)

    def to_string(self) -> str:
        parts = [
            f"m={self.model_id}",
            f"be={self.backend}",
            f"dtype={self.dtype}",
            f"bkt={self.bucket}",
            f"attn={self.attn_kernel}",
            f"x={self.extra}",
        ]
        return "|".join(parts)

    def to_compact(self) -> str:
        return _stable_hash(self.to_string())[:16]


@dataclass
class GraphRecord:
    key: GraphKey
    handle: Any = None             # {'g': CUDAGraph, 'static_args': ..., 'static_kwargs': ...}
    created_at: float = field(default_factory=_now)
    last_used_at: float = field(default_factory=_now)
    hits: int = 0
    cold_misses: int = 0
    warm: bool = False             # True when usable
    aot: bool = False              # whether created via warmup/AOT
    size_hint_bytes: int = 0       # optional, for memory-based eviction
    # persistent static I/O used by CUDA Graphs (for introspection)
    static_args: Optional[Tuple[Any, ...]] = None
    static_kwargs: Optional[Dict[str, Any]] = None
    # failure/health fields
    fail_reason: Optional[str] = None
    partial: bool = False          # reserved for "partial capture" bookkeeping


class LRUCache:
    """
    Simple thread-safe LRU with TTL and max items.
    """

    def __init__(self, max_items: int = 64, ttl_sec: int = 3600) -> None:
        self.max_items = max_items
        self.ttl_sec = ttl_sec
        self._items: Dict[str, GraphRecord] = {}
        self._lock = threading.Lock()

    def get(self, k: str) -> Optional[GraphRecord]:
        now = _now()
        with self._lock:
            rec = self._items.get(k)
            if not rec:
                return None
            if now - rec.created_at > self.ttl_sec:
                # expired
                self._items.pop(k, None)
                return None
            rec.last_used_at = now
            return rec

    def put(self, k: str, v: GraphRecord) -> None:
        with self._lock:
            if k in self._items:
                self._items[k] = v
            else:
                if len(self._items) >= self.max_items:
                    # evict least-recently-used
                    ev_k = sorted(self._items.items(), key=lambda kv: kv[1].last_used_at)[0][0]
                    self._items.pop(ev_k, None)
                self._items[k] = v

    def touch(self, k: str) -> None:
        with self._lock:
            rec = self._items.get(k)
            if rec:
                rec.last_used_at = _now()

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._items),
                "keys": list(self._items.keys())[:8],  # trim
                "ttl_sec": self.ttl_sec,
                "max_items": self.max_items,
            }


# ---------------------------------------------------------------------
# Graph executor interface & CUDA impl
# ---------------------------------------------------------------------

@runtime_checkable
class GraphExecutor(Protocol):
    """
    Minimal interface for a backend graph executor.
    """

    @property
    def available(self) -> bool:
        ...

    def capture(self, fn, example_args: Tuple[Any, ...], example_kwargs: Dict[str, Any]) -> Any:
        """Capture/compile a graph for the function 'fn' with example inputs."""
        ...

    def replay(self, handle: Any, *args, **kwargs) -> Any:
        """Replay the compiled graph."""
        ...


class CudaGraphsExecutor:
    """
    Thin wrapper around torch.cuda.CUDAGraph (optional).
    If CUDA or torch not present, available=False.

    Notes:
    - We deep-clone example inputs to device to build static buffers.
    - Replay copies user inputs into those static buffers (shape/dtype enforced).
    """

    def __init__(self) -> None:
        self._ok = bool(
            torch is not None
            and hasattr(torch, "cuda")
            and getattr(torch.cuda, "is_available", lambda: False)()
            and hasattr(torch.cuda, "CUDAGraph")
        )
        # Future: pool-per-graph could be stored here.
        self._pools: Dict[str, Any] = {}

    @property
    def available(self) -> bool:
        return self._ok

    def _clone_static(self, x):
        """Deep-clone to device, preserving structure; detach and requires_grad=False."""
        if torch.is_tensor(x):
            # Move to CUDA and make non-differentiable.
            t = x.detach().to("cuda", non_blocking=True).clone()
            t.requires_grad_(False)
            return t
        if isinstance(x, (list, tuple)):
            typ = type(x)
            return typ(self._clone_static(e) for e in x)
        if isinstance(x, dict):
            return {k: self._clone_static(v) for k, v in x.items()}
        return x  # non-tensor

    def capture(self, fn, example_args: Tuple[Any, ...], example_kwargs: Dict[str, Any]) -> Any:
        if not self._ok:
            raise RuntimeError("CUDA Graphs not available")

        # build static inputs (same structure as example_args/kwargs)
        static_args = self._clone_static(example_args)
        static_kwargs = self._clone_static(example_kwargs)

        # capture using a private stream
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        g = torch.cuda.CUDAGraph()
        torch.cuda.set_stream(stream)
        stream.synchronize()
        with torch.cuda.graph(g):
            _ = fn(*static_args, **static_kwargs)
        torch.cuda.current_stream().wait_stream(stream)

        # return a handle that carries graph + static buffers
        return {"g": g, "static_args": static_args, "static_kwargs": static_kwargs}

    def replay(self, handle: Any, *args, **kwargs) -> Any:
        if not self._ok:
            raise RuntimeError("CUDA Graphs not available")
        h = handle if isinstance(handle, dict) else {"g": handle, "static_args": (), "static_kwargs": {}}

        def _copy_into(dst, src):
            # Robust deep copy with exact shape/dtype enforcement; supports nested containers.
            if torch.is_tensor(dst) and torch.is_tensor(src):
                if dst.shape != src.shape or dst.dtype != src.dtype:
                    raise RuntimeError(
                        f"replay input mismatch: expected {tuple(dst.shape)}/{dst.dtype}, got {tuple(src.shape)}/{src.dtype}"
                    )
                # Ensure same device; copy with non_blocking where possible.
                if src.device != dst.device:
                    src = src.to(dst.device, non_blocking=True)
                dst.copy_(src, non_blocking=True)
                return
            if isinstance(dst, (list, tuple)) and isinstance(src, (list, tuple)):
                if len(dst) != len(src):
                    raise RuntimeError(f"replay input list/tuple length mismatch: {len(dst)} vs {len(src)}")
                for d, s in zip(dst, src):
                    _copy_into(d, s)
                return
            if isinstance(dst, dict) and isinstance(src, dict):
                # Only copy keys that exist in dst; ignore extra keys in src.
                for k in dst.keys():
                    if k not in src:
                        raise RuntimeError(f"replay input dict missing key: {k}")
                    _copy_into(dst[k], src[k])
                return
            # Non-tensor leaves: allow equality or pass-through for None/identical cases.

        if args:
            _copy_into(h.get("static_args", ()), args)
        if kwargs:
            _copy_into(h.get("static_kwargs", {}), kwargs)

        h["g"].replay()
        return None


class NoopExecutor:
    """
    Safe executor when graphs are not supported on the current backend.
    """
    @property
    def available(self) -> bool:
        return False

    def capture(self, fn, example_args: Tuple[Any, ...], example_kwargs: Dict[str, Any]) -> Any:
        raise RuntimeError("Graph capture not supported on this backend")

    def replay(self, handle: Any, *args, **kwargs) -> Any:
        raise RuntimeError("Graph replay not supported on this backend")


def _make_executor(backend: str) -> GraphExecutor:
    b = backend.lower()
    if b == "cuda":
        return CudaGraphsExecutor()
    # TODO: future: HIP Graphs / IREE / Level-Zero / Vulkan backends
    return NoopExecutor()


# ---------------------------------------------------------------------
# Graph Manager (device-scoped caches)
# ---------------------------------------------------------------------

@dataclass
class RouteInfo:
    bucket: int
    overflow: bool
    seq_lens: List[int]
    hit: bool
    key_compact: str
    cache_size: int
    backend: str
    device: int


class GraphManager:
    """
    Orchestrates bucketing and per-device graph caches.
    Works in 'routing-only' mode if the per-device executor is unavailable.

    Differences vs previous version
    -------------------------------
    - Maintains `cache_by_dev[device_index]` and related structures.
    - `route()` can accept `device_index`; if omitted we infer from torch or default to 0.
    - `maybe_capture()` / `replay()` accept optional `device_index`; when omitted, we infer
      it from tensors in the provided args/kwargs or use current CUDA device.
    - `warmup_aot()` can warm a single device or **all devices** discovered by DeviceManager.
    """

    def __init__(self, cfg: Optional[SkoteConfig] = None) -> None:
        self.cfg = cfg or get_config()

        # buckets
        buckets = sorted(set(int(x) for x in getattr(self.cfg, "max_context_buckets", []) if int(x) > 0))
        if not buckets:
            buckets = [2048, 4096, 8192, 16384, 32768]
        self.policy = BucketPolicy(buckets=buckets, overflow=True)

        # per-device caches & state
        self._lock = threading.RLock()
        self.cache_by_dev: Dict[int, LRUCache] = {}
        self.exec_by_dev: Dict[int, GraphExecutor] = {}
        self.backend_by_dev: Dict[int, str] = {}
        self._cap_locks_by_dev: Dict[int, Dict[str, threading.Lock]] = {}
        self._blacklist_by_dev: Dict[int, Dict[str, float]] = {}
        self._hits_by_dev: Dict[int, int] = {}
        self._misses_by_dev: Dict[int, int] = {}

        # capture policy knobs
        self.min_bucket_capture = int(os.environ.get("SKOTE_MIN_BUCKET_CAPTURE", "8192"))
        self.eager_small_buckets = (os.environ.get("SKOTE_EAGER_SMALL_BUCKETS", "1").strip() == "1")

        whitelist_env = os.environ.get("SKOTE_GRAPH_BUCKETS_CAPTURE", "").strip()
        self.capture_whitelist = _parse_int_list(whitelist_env) if whitelist_env else [
            b for b in self.policy.buckets if b >= self.min_bucket_capture
        ]

        self.blacklist_ttl = int(os.environ.get("SKOTE_GRAPH_BLACKLIST_TTL", "900"))
        self.verbose = os.environ.get("SKOTE_GRAPH_CAPTURE_LOG", "0") == "1"

        # LRU defaults (per device)
        self._lru_items = int(os.environ.get("SKOTE_GRAPH_CACHE_ITEMS", "64"))
        self._lru_ttl   = int(os.environ.get("SKOTE_GRAPH_CACHE_TTL", "3600"))

        # Discover devices via DeviceManager (falls back to a single "device 0")
        self._init_devices()

        log.info(
            "GraphManager ready (devices=%s, buckets=%s, capture_whitelist=%s, min_bucket=%d, eager_small=%s)",
            sorted(self.cache_by_dev.keys()), self.policy.buckets, self.capture_whitelist,
            self.min_bucket_capture, self.eager_small_buckets
        )

    # --------------------------- Device init ---------------------------

    def _init_devices(self) -> None:
        if DeviceManager is None:
            # Minimal single-device (0) init
            self._ensure_device_structs(0, backend="cuda" if (torch and torch.cuda.is_available()) else "cpu")
            return

        plan = DeviceManager.from_env().get_plan(model_num_params=None, dtype=os.environ.get("SKOTE_PREF_PRECISION", "bf16"))
        if not getattr(plan, "devices", None):
            self._ensure_device_structs(0, backend="cpu")
            return

        for dinfo in plan.devices:
            if getattr(dinfo, "backend", None) in (BackendKind.CUDA, BackendKind.ROCM):
                backend = "cuda"  # CUDA graphs API namespace (HIP treated as cuda, availability probed below)
            elif getattr(dinfo, "backend", None) == BackendKind.XPU:
                backend = "xpu"
            else:
                backend = "cpu"
            self._ensure_device_structs(int(dinfo.index), backend=backend)

    def _ensure_device_structs(self, device_index: int, *, backend: str) -> None:
        with self._lock:
            if device_index not in self.cache_by_dev:
                self.cache_by_dev[device_index] = LRUCache(max_items=self._lru_items, ttl_sec=self._lru_ttl)
            if device_index not in self.exec_by_dev:
                self.exec_by_dev[device_index] = _make_executor(backend)
            self.backend_by_dev[device_index] = backend
            self._cap_locks_by_dev.setdefault(device_index, {})
            self._blacklist_by_dev.setdefault(device_index, {})
            self._hits_by_dev.setdefault(device_index, 0)
            self._misses_by_dev.setdefault(device_index, 0)

    def _resolve_device_index(self, device_index: Optional[int]) -> int:
        if device_index is not None:
            return int(device_index)
        # Prefer current CUDA device if available
        if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
            try:
                return int(torch.cuda.current_device())
            except Exception:
                pass
        # Fallback: smallest known device id
        if self.cache_by_dev:
            return sorted(self.cache_by_dev.keys())[0]
        # Ensure a default
        self._ensure_device_structs(0, backend="cpu")
        return 0

    # --------------------------- Public API ---------------------------

    def route(
        self,
        prompts: Iterable[str] | str,
        *,
        seq_lens: Optional[List[int]] = None,
        model_id: str = "default",
        dtype: str = "auto",
        attn_kernel: str = "auto",
        extra_key: str = "",
        device_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Decide bucket for a batch of prompts and return routing info (device-scoped).
        If seq_lens not provided, we approximate by len(string) (safe heuristic).
        """
        dev = self._resolve_device_index(device_index)

        texts = _as_list_str(prompts)
        if seq_lens is None:
            seq_lens = [len(t) for t in texts]  # heuristic: char length as token surrogate
        max_len = max(seq_lens) if seq_lens else 0
        bucket, overflow = self.policy.choose(max_len)

        gkey = GraphKey(
            model_id=model_id,
            backend=self.backend_by_dev.get(dev, "cpu"),
            dtype=dtype,
            bucket=bucket,
            attn_kernel=attn_kernel,
            extra=extra_key,
        )
        key_str = gkey.to_string()
        key_compact = gkey.to_compact()

        cache = self.cache_by_dev[dev]
        rec = cache.get(key_compact)
        hit = rec is not None and rec.warm

        with self._lock:
            if hit:
                self._hits_by_dev[dev] += 1
            else:
                self._misses_by_dev[dev] += 1

        # Place a cold record placeholder for future warmup (per device)
        if rec is None:
            rec = GraphRecord(key=gkey, warm=False, aot=False)
            cache.put(key_compact, rec)

        return {
            "policy": "len-bucket",
            "bucket": bucket,
            "overflow": overflow,
            "seq_lens": seq_lens,
            "graph_key": key_str,
            "graph_id": key_compact,   # NOTE: compact id string is device-agnostic; cache is device-scoped
            "cached": hit,
            "backend": self.backend_by_dev.get(dev, "cpu"),
            "device": dev,
            "cache_size": cache.stats()["size"],
            "hits": self._hits_by_dev.get(dev, 0),
            "misses": self._misses_by_dev.get(dev, 0),
        }

    # --------------------------- Policy helpers ---------------------------

    def _eligible_for_capture(self, bucket: int) -> bool:
        """Gate capture by whitelist and min-bucket policy."""
        if bucket < self.min_bucket_capture and self.eager_small_buckets:
            if self.verbose:
                log.debug("Capture bypassed: bucket %d < min %d", bucket, self.min_bucket_capture)
            return False
        if self.capture_whitelist and bucket not in self.capture_whitelist:
            if self.verbose:
                log.debug("Capture bypassed: bucket %d not in whitelist %s", bucket, self.capture_whitelist)
            return False
        return True

    def _blacklisted(self, dev: int, key_compact: str) -> bool:
        expiry = self._blacklist_by_dev.get(dev, {}).get(key_compact, 0.0)
        if expiry <= 0:
            return False
        if _now() > expiry:
            # expire
            self._blacklist_by_dev[dev].pop(key_compact, None)
            return False
        return True

    def _get_cap_lock(self, dev: int, key: str) -> threading.Lock:
        # single-flight lock per (device, graph key)
        with self._lock:
            per = self._cap_locks_by_dev.setdefault(dev, {})
            lk = per.get(key)
            if lk is None:
                lk = threading.Lock()
                per[key] = lk
            return lk

    # --------------------------- Capture / Replay ---------------------------

    def maybe_capture(
        self,
        key_compact: str,
        fn,
        example_args: Tuple[Any, ...],
        example_kwargs: Optional[Dict[str, Any]] = None,
        *,
        aot: bool = False,
        device_index: Optional[int] = None,
    ) -> bool:
        """
        Capture/compile the graph for the given key if not warmed yet (device-scoped).
        Returns True if a warm graph is ready after this call.

        Concurrency & robustness:
        - Single-flight per (device,key); if capture failed recently -> blacklist TTL.
        - If executor is unavailable on the device, returns False quickly.
        - If device_index is None, infer from tensors in example_args/kwargs or current device.
        """
        example_kwargs = example_kwargs or {}
        dev = self._resolve_device_index(
            device_index if device_index is not None else _infer_device_index_from_args(example_args, example_kwargs)
        )
        cache = self.cache_by_dev[dev]
        execu = self.exec_by_dev[dev]

        rec = cache.get(key_compact)
        if rec and rec.warm:
            return True
        if not execu.available:
            if self.verbose:
                log.debug("Graph capture skipped: executor unavailable on device %d (backend=%s)", dev, self.backend_by_dev.get(dev))
            return False

        # Create placeholder record if missing (route() should have created one)
        if rec is None:
            # Derive a conservative bucket from provided seq_len (if any)
            seq_len = example_kwargs.get("seq_len", 0)
            rec = GraphRecord(
                key=GraphKey(model_id="default", backend=self.backend_by_dev.get(dev, "cpu"),
                             dtype="auto", bucket=int(seq_len)),
                warm=False, aot=False
            )

        bucket = rec.key.bucket
        if not self._eligible_for_capture(bucket):
            return False

        # Blacklist check (per device)
        if self._blacklisted(dev, key_compact):
            if self.verbose:
                log.debug("Graph capture bypassed: (dev=%d, id=%s) is blacklisted", dev, key_compact)
            return False

        cap_lock = self._get_cap_lock(dev, key_compact)
        if not cap_lock.acquire(blocking=False):
            if self.verbose:
                log.debug("Graph capture in-flight (dev=%d, id=%s); skipping duplicate", dev, key_compact)
            return False

        try:
            # Re-check after acquiring the lock (TOCTOU)
            fresh = cache.get(key_compact)
            if fresh and fresh.warm:
                return True

            t0 = _now()
            # Ensure we capture on the intended device
            if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
                with torch.cuda.device(dev):
                    handle = execu.capture(fn, example_args, example_kwargs)
            else:
                handle = execu.capture(fn, example_args, example_kwargs)
            dt = (_now() - t0) * 1000.0

            rec.handle = handle
            rec.static_args = handle.get("static_args") if isinstance(handle, dict) else None
            rec.static_kwargs = handle.get("static_kwargs") if isinstance(handle, dict) else None
            rec.warm = True
            rec.aot = bool(aot)
            rec.hits = 0
            rec.fail_reason = None
            cache.put(key_compact, rec)
            log.info("Graph captured (dev=%d, id=%s, bucket=%d, aot=%s, %.1f ms)", dev, key_compact, bucket, aot, dt)
            return True
        except Exception as e:  # pragma: no cover
            rec.cold_misses += 1
            rec.fail_reason = str(e)
            cache.put(key_compact, rec)
            # blacklist this (dev,key) to avoid retry storms
            self._blacklist_by_dev[dev][key_compact] = _now() + float(self.blacklist_ttl)
            log.warning("Graph capture failed (dev=%d, id=%s, bucket=%d): %s (blacklisted %ds)",
                        dev, key_compact, bucket, e, self.blacklist_ttl)
            return False
        finally:
            try:
                cap_lock.release()
            except Exception:
                pass

    def replay(self, key_compact: str, *args, device_index: Optional[int] = None, **kwargs) -> bool:
        """
        Replay a previously captured graph on a given device. Returns True on success.
        If device_index is None, infer from tensor args/kwargs or current CUDA device.
        """
        dev = self._resolve_device_index(
            device_index if device_index is not None else _infer_device_index_from_args(args, kwargs)
        )
        cache = self.cache_by_dev[dev]
        execu = self.exec_by_dev[dev]

        rec = cache.get(key_compact)
        if not rec or not rec.warm or not rec.handle:
            if self.verbose:
                log.debug("Graph replay miss (dev=%d, id=%s); warm=%s", dev, key_compact, bool(rec and rec.warm))
            return False

        if not execu.available:
            return False

        try:
            if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
                with torch.cuda.device(dev):
                    execu.replay(rec.handle, *args, **kwargs)
            else:
                execu.replay(rec.handle, *args, **kwargs)
            rec.hits += 1
            cache.put(key_compact, rec)
            return True
        except Exception as e:  # pragma: no cover
            # On replay failures, do not immediately blacklist; log and let caller eager-fallback.
            log.warning("Graph replay failed (dev=%d, id=%s): %s", dev, key_compact, e)
            return False

    # --------------------------- Introspection ---------------------------

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            per_dev = {}
            for dev, cache in self.cache_by_dev.items():
                d = cache.stats()
                d.update({
                    "backend": self.backend_by_dev.get(dev, "cpu"),
                    "hits": self._hits_by_dev.get(dev, 0),
                    "misses": self._misses_by_dev.get(dev, 0),
                    "blacklisted": {
                        k: int(exp - _now()) for k, exp in list(self._blacklist_by_dev.get(dev, {}).items()) if exp > _now()
                    },
                })
                per_dev[dev] = d
            return {
                "devices": per_dev,
                "buckets": self.policy.buckets,
                "capture_whitelist": self.capture_whitelist,
                "min_bucket_capture": self.min_bucket_capture,
                "eager_small_buckets": self.eager_small_buckets,
            }

    # --------------------------- Convenience ---------------------------

    def warmup_aot(
        self,
        model_id: str,
        fn,
        example_inputs: List[Tuple[Tuple[Any, ...], Dict[str, Any]]],
        *,
        dtype: str = "auto",
        attn_kernel: str = "auto",
        extra_key: str = "",
        device: Optional[int | str] = None,   # None=current, int=that device, "all"=all CUDA devices
    ) -> List[Tuple[int, str]]:
        """
        AOT warmup: capture graphs for a set of example shapes.
        Returns list of (device_index, graph_id) warmed.
        Respects capture whitelist and min-bucket policy.

        device: None -> infer current device; "all" -> iterate all discovered devices;
                int -> warm that device only.
        """
        targets: List[int] = []
        if device == "all":
            targets = sorted(self.cache_by_dev.keys())
        elif isinstance(device, int):
            targets = [self._resolve_device_index(device)]
        else:
            targets = [self._resolve_device_index(None)]

        warmed: List[Tuple[int, str]] = []
        for dev in targets:
            backend = self.backend_by_dev.get(dev, "cpu")
            if backend != "cuda" or not self.exec_by_dev[dev].available:
                # Warmup only meaningful where graphs are available
                continue

            for args, kwargs in example_inputs:
                # derive length from kwargs if provided, else from args/text len
                seq_len = kwargs.get("seq_len") if kwargs else None
                if seq_len is None:
                    length_guess = 0
                    if args:
                        a0 = args[0]
                        if isinstance(a0, str):
                            length_guess = len(a0)
                        elif isinstance(a0, (list, tuple)) and a0 and isinstance(a0[0], str):
                            length_guess = max(len(x) for x in a0)  # type: ignore
                    seq_len = int(length_guess)

                bkt, _ = self.policy.choose(int(seq_len))
                # skip if not eligible (keeps warmup tight and stable)
                if not self._eligible_for_capture(bkt):
                    if self.verbose:
                        log.debug("AOT warmup skip: device=%d bucket %d not eligible", dev, bkt)
                    continue

                gkey = GraphKey(
                    model_id=model_id,
                    backend=backend,
                    dtype=dtype,
                    bucket=bkt,
                    attn_kernel=attn_kernel,
                    extra=extra_key,
                )
                kid = gkey.to_compact()
                ok = self.maybe_capture(kid, fn, args, kwargs, aot=True, device_index=dev)
                if ok:
                    warmed.append((dev, kid))
        return warmed
