# skotergy/graph/capture_decode.py
"""
Decode-only CUDA Graph capture & replay for Skotergy (PKV-first).

What this module guarantees
---------------------------
- We ONLY attempt to capture the *decode step* (one token step) whose shapes
  are stable when the runtime uses a fixed-shape KV cache (PKV/paged-KV).
- If the bound model exposes decode helpers, we use them; otherwise we safely
  fall back to eager execution. We never crash the caller for lack of hooks.
- During warmup/capture we temporarily force a capture-safe attention path
  (disable SDPA/FA, prefer math/eager) to avoid known HF Llama issues.

Environment knobs (aligned with Skotergy)
-----------------------------------------
SKOTE_GRAPHS=1                         : enable graph path
SKOTE_GRAPH_BUCKETS_CAPTURE="..."      : candidate buckets (sorted, default: 128..16384)
SKOTE_MIN_BUCKET_CAPTURE=256           : min bucket eligible for capture
SKOTE_EAGER_SMALL_BUCKETS=0/1          : force eager under min bucket
SKOTE_SCHED_LOG=0/1                    : verbose debug logs
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional, Tuple

import torch

# ------------------------------ Env & policy ---------------------------------------

_SKOTE_GRAPHS = os.getenv("SKOTE_GRAPHS", "1").strip() == "1"
_BUCKETS = [
    int(x) for x in os.getenv(
        "SKOTE_GRAPH_BUCKETS_CAPTURE",
        "128,256,512,1024,2048,4096,8192,16384"
    ).split(",") if x.strip()
]
_MIN_BUCKET = int(os.getenv("SKOTE_MIN_BUCKET_CAPTURE", "256"))
_EAGER_SMALL = os.getenv("SKOTE_EAGER_SMALL_BUCKETS", "0").strip() == "1"
_VERBOSE = os.getenv("SKOTE_SCHED_LOG", "0").strip() == "1"

# ------------------------------ Capture state --------------------------------------

class _DecodeGraphRec:
    __slots__ = ("bucket", "g", "xbuf", "kv", "out_ref", "stream")

    def __init__(self, bucket: int, g: torch.cuda.CUDAGraph,
                 xbuf: torch.Tensor, kv: Any, out_ref: Any, stream: torch.cuda.Stream):
        self.bucket = bucket
        self.g = g
        self.xbuf = xbuf          # token buffer on device, typically [B=1, 1]
        self.kv = kv              # model-specific KV/state handle (opaque)
        self.out_ref = out_ref    # captured output object (tensor or structure)
        self.stream = stream      # capture/replay stream

_lock = threading.RLock()
_graphs: Dict[int, _DecodeGraphRec] = {}   # bucket -> record

# ------------------------------ Utilities ------------------------------------------

def _log_debug(msg: str, *a: Any) -> None:
    if _VERBOSE:
        try:
            from skote import get_logger  # optional
            get_logger("skotergy.graph.decode").debug(msg, *a)
        except Exception:
            print("[skote/decode] " + (msg % a if a else msg))

def _choose_bucket(seqlen: int) -> int:
    # Largest bucket <= seqlen; if none, the smallest.
    cand = [b for b in _BUCKETS if b <= seqlen]
    return (max(cand) if cand else min(_BUCKETS))

def _model_device(model: Any) -> torch.device:
    # Try common attributes
    dev = getattr(model, "device", None)
    if isinstance(dev, torch.device):
        return dev
    if isinstance(dev, torch.nn.Module):
        return next(dev.parameters()).device
    # HuggingFace-like wrapper: try .mod
    mod = getattr(model, "mod", None)
    if isinstance(mod, torch.nn.Module):
        return next(mod.parameters()).device
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _alloc_inputs(model: Any, bucket: int) -> Tuple[torch.Tensor, Any]:
    """
    Prefer model-provided allocator; else allocate a generic [1,1] token buffer.
    Returns (xbuf, kv_handle_or_none).
    """
    for name in ("alloc_decode_inputs", "decode_alloc", "allocate_decode_inputs"):
        fn = getattr(model, name, None)
        if callable(fn):
            x, kv = fn(bucket)  # type: ignore
            return x, kv
    dev = _model_device(model)
    x = torch.empty((1, 1), dtype=torch.long, device=dev)
    return x, None

def _write_tokens(model: Any, xbuf: torch.Tensor, token_ids: Optional[torch.Tensor]) -> None:
    """
    Copy latest token_ids into xbuf if provided; prefer model-provided updater.
    """
    if token_ids is None:
        return
    for name in ("update_decode_inputs", "decode_update", "write_decode_tokens"):
        fn = getattr(model, name, None)
        if callable(fn):
            fn(xbuf, token_ids)  # type: ignore
            return
    # Fallback: shape-safe direct copy
    ncols = min(xbuf.shape[-1], token_ids.shape[-1])
    nrows = min(xbuf.shape[0], token_ids.shape[0])
    xbuf[:nrows, :ncols].copy_(token_ids[:nrows, :ncols], non_blocking=True)

def _read_logits(model: Any, out_ref: Any) -> Any:
    """
    Canonicalize output if model offers a helper; otherwise return as-is.
    """
    for name in ("read_decode_logits", "decode_logits", "extract_logits"):
        fn = getattr(model, name, None)
        if callable(fn):
            return fn(out_ref)  # type: ignore
    return out_ref

@contextmanager
def _attn_capture_ctx(model: Any):
    """
    Make attention capture-safe during warmup & capture:
      - force SDPA/FA off, enable math kernels,
      - switch HF attention implementation to 'eager' if possible.
    """
    # Try to tweak HF config on the model (if present)
    cfg = getattr(getattr(model, "mod", model), "config", None)
    old_impl = getattr(cfg, "attn_implementation", None) if cfg is not None else None
    if cfg is not None and hasattr(cfg, "attn_implementation"):
        try:
            cfg.attn_implementation = "eager"
        except Exception:
            pass

    # SDP kernel context (math-only)
    try:
        sdp_ctx = torch.backends.cuda.sdp_kernel(
            enable_flash=False, enable_mem_efficient=False, enable_math=True
        )
    except Exception:
        @contextmanager
        def _null():
            yield
        sdp_ctx = _null()

    # Also hint transformers via env (harmless if already set)
    prev_env = os.environ.get("TRANSFORMERS_ATTENTION_IMPLEMENTATION", None)
    os.environ.setdefault("TRANSFORMERS_ATTENTION_IMPLEMENTATION", "eager")

    try:
        with sdp_ctx:
            yield
    finally:
        if prev_env is None and "TRANSFORMERS_ATTENTION_IMPLEMENTATION" in os.environ:
            # We only added it; remove to restore previous state
            try:
                del os.environ["TRANSFORMERS_ATTENTION_IMPLEMENTATION"]
            except Exception:
                pass
        if cfg is not None and old_impl is not None:
            try:
                cfg.attn_implementation = old_impl
            except Exception:
                pass

# ------------------------------ Capture & replay -----------------------------------

def ensure_decode_graph(model: Any, seqlen: int) -> bool:
    """
    Ensure a one-step decode CUDA Graph exists for the selected bucket.
    Returns True if graph is ready (captured or cached), False otherwise.
    """
    if not torch.cuda.is_available() or not _SKOTE_GRAPHS:
        return False

    bucket = _choose_bucket(seqlen)
    if bucket < _MIN_BUCKET and _EAGER_SMALL:
        _log_debug("Bucket %d < MIN %d; policy chooses eager.", bucket, _MIN_BUCKET)
        return False

    with _lock:
        if bucket in _graphs:
            return True

        # Allocate inputs and capture resources
        xbuf, kv = _alloc_inputs(model, bucket)
        stream = torch.cuda.Stream()
        g = torch.cuda.CUDAGraph()

        # Choose a step function; prefer model.decode_step (PKV-friendly)
        step = getattr(model, "decode_step", None)
        if not callable(step):
            # Generic fallback: treat model as HF-like forward
            def step(x, kv_state=None):
                if hasattr(model, "forward"):
                    return model.forward(input_ids=x)
                return model(x)  # type: ignore

        # Warmup + Capture under capture-safe attention context
        try:
            with _attn_capture_ctx(model):
                with torch.cuda.stream(stream):
                    _ = step(xbuf, kv)  # type: ignore
                torch.cuda.synchronize(stream)
                with torch.cuda.graph(g):
                    out_ref = step(xbuf, kv)  # type: ignore
        except Exception as e:
            _log_debug("Graph capture failed for bucket=%d: %s; falling back to eager.", bucket, str(e))
            return False

        _graphs[bucket] = _DecodeGraphRec(bucket=bucket, g=g, xbuf=xbuf, kv=kv, out_ref=out_ref, stream=stream)
        _log_debug("Captured decode graph for bucket=%d.", bucket)
        return True


@torch.no_grad()
def decode_step_via_graph(
    model: Any,
    seqlen: int,
    token_ids: Optional[torch.Tensor] = None,
    kv: Any = None
) -> Any:
    """
    Execute a one-step decode via graph if eligible; otherwise run eager.

    Parameters
    ----------
    model : Any
        Model wrapper or module. Preferably exposes:
          - alloc_decode_inputs(bucket) -> (xbuf, kv_handle)
          - update_decode_inputs(xbuf, token_ids)
          - update_decode_kv(kv_handle, new_state)    [optional]
          - decode_step(xbuf, kv_handle) -> logits    [preferred path]
    seqlen : int
        Current sequence length used to choose the capture bucket.
    token_ids : Optional[Tensor]
        Latest token ids to copy into the captured input buffer (shape [1,1] typical).
    kv : Any
        Optional KV/cached state to use with the step.

    Returns
    -------
    Any
        Model-specific output (logits tensor or structure).
    """
    if torch.cuda.is_available() and _SKOTE_GRAPHS and ensure_decode_graph(model, seqlen):
        bucket = _choose_bucket(seqlen)
        rec = _graphs.get(bucket)
        if rec is not None:
            # Update input token(s)
            _write_tokens(model, rec.xbuf, token_ids)
            # Optionally update KV/state (opaque to this module)
            if kv is not None:
                for name in ("update_decode_kv", "decode_update_kv", "set_kv_state"):
                    fn = getattr(model, name, None)
                    if callable(fn):
                        try:
                            fn(rec.kv, kv)  # type: ignore
                        except Exception:
                            pass
                        break
            # Replay
            rec.g.replay()
            return _read_logits(model, rec.out_ref)

    # Eager fallback path
    step = getattr(model, "decode_step", None)
    if callable(step):
        x = token_ids
        if x is None:
            dev = _model_device(model)
            x = torch.zeros((1, 1), dtype=torch.long, device=dev)
        return step(x, kv)  # type: ignore

    # Generic forward fallback
    if hasattr(model, "forward"):
        x = token_ids
        if x is None:
            dev = _model_device(model)
            x = torch.zeros((1, 1), dtype=torch.long, device=dev)
        return model.forward(input_ids=x)

    # Last resort: call model directly
    x = token_ids
    if x is None:
        dev = _model_device(model)
        x = torch.zeros((1, 1), dtype=torch.long, device=dev)
    return model(x)  # type: ignore

# ------------------------------ Management -----------------------------------------

def warmup_decode_graphs(model: Any, buckets: Iterable[int]) -> None:
    """
    Proactively capture graphs for the provided buckets (if eligible).
    """
    for b in sorted(set(int(x) for x in buckets)):
        ensure_decode_graph(model, b)

def reset_decode_graphs() -> None:
    """
    Drop all cached decode graphs. Streams and tensors are left to GC.
    """
    with _lock:
        _graphs.clear()
