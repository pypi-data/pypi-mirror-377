# skote/compat/backends.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Unified backend compatibility layer for Skotergy.

Why this file?
--------------
Skotergy runs on heterogeneous devices (CUDA, ROCm, Intel XPU, CPU). This module
hides backend-specific details behind stable utilities:

- Backend detection: cuda | rocm | xpu | cpu
- Streams & events: safe wrappers (no-op on unsupported backends)
- AMP/autocast: cuda.autocast / xpu.amp.autocast / cpu.autocast (fallback to no-op)
- Precision policy: choose preferred dtype (bf16/fp16/fp32/fp8*) with capability checks
- Memory info: free/total where available (cuda/rocm)
- P2P checks: can_access_peer when appropriate
- Triton patches: enable optimized kernels when possible, with safe fallback

Design principles
-----------------
- "Do no harm": single-GPU CPU-only setups must behave identically to upstream PyTorch.
- Be explicit but forgiving: prefer feature probes over platform assumptions.
- Zero hard dependency on optional libs (triton/ipex/pynvml): lazy import & graceful degrade.

Public surface (stable)
-----------------------
get_active_backend() -> str                      # "cuda"|"rocm"|"xpu"|"cpu"
prefer_dtype() -> torch.dtype                    # from env + capability checks
dtype_priority() -> List[torch.dtype]            # ordered candidates for loaders/weights
amp_autocast(dtype=None) -> context manager      # unified autocast (no-op when unavailable)
create_stream(device=None) -> StreamHandle       # unified stream wrapper
create_event(enable_timing=False) -> EventHandle # unified event wrapper
mem_get_info(device_index=None) -> (free,total)  # bytes or (None,None)
can_access_peer(src,dst) -> bool
maybe_enable_triton_patches(model, *, force=False, attn_kernel="auto") -> int
set_matmul_precision(level="high"|"medium"|"low") -> None

Environment knobs
-----------------
SKOTE_BACKEND_HINT=cuda|rocm|xpu|cpu
SKOTE_PREF_PRECISION=bf16|fp16|fp32|fp8   (default bf16)
SKOTE_FORCE_DISABLE_TRITON=0|1            (default 0)
SKOTE_LOG_LEVEL=INFO|DEBUG

Notes
-----
- FP8 support is signaled only as a *preference*; enable actual FP8 ops where upstream supports.
- ROCm reports as torch.cuda; we rely on torch.version.hip to distinguish.
"""

from __future__ import annotations

import os
import logging
import contextlib
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List

# --- Torch (optional submodules are guarded) ---
try:
    import torch
except Exception as e:  # pragma: no cover
    raise RuntimeError("backends.py requires PyTorch") from e

# Optional: Intel IPEX (for XPU autocast/streams)
try:
    import intel_extension_for_pytorch as ipex  # type: ignore
    _HAS_IPEX = True
except Exception:
    _HAS_IPEX = False

# Optional: Triton patches from Skotergy kernels (graceful fallback)
try:
    from skote.kernels.triton_ops import enable_triton_patches as _enable_triton_patches  # type: ignore
    from skote.kernels.triton_ops import set_attention_kernel as _set_attention_kernel    # type: ignore
    _HAS_SKOTE_TRITON = True
except Exception:
    _HAS_SKOTE_TRITON = False

# Optional: DeviceManager backend enums (avoid hard dep at import-time)
try:
    from skote.distributed.devicemgr import BackendKind  # type: ignore
except Exception:
    class BackendKind:
        CUDA = "cuda"
        ROCM = "rocm"
        XPU  = "xpu"
        CPU  = "cpu"

# Logging
def _get_logger(name: str) -> logging.Logger:
    try:
        from skote import get_logger  # type: ignore
        return get_logger(name)
    except Exception:
        logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))
        return logging.getLogger(name)

LOG = _get_logger("skotergy.backends")


# ----------------------------- Backend detection -----------------------------

def _detect_backend_hint() -> Optional[str]:
    v = os.environ.get("SKOTE_BACKEND_HINT")
    if not v:
        return None
    v = v.strip().lower()
    if v in (BackendKind.CUDA, BackendKind.ROCM, BackendKind.XPU, BackendKind.CPU):
        return v
    return None


def get_active_backend() -> str:
    """
    Return "cuda" | "rocm" | "xpu" | "cpu".
    """
    hint = _detect_backend_hint()
    if hint:
        return hint

    if torch.cuda.is_available():
        # Distinguish ROCm vs CUDA
        try:
            if getattr(torch.version, "hip", None):
                return BackendKind.ROCM
        except Exception:
            pass
        return BackendKind.CUDA

    # Intel XPU
    try:
        has_xpu = hasattr(torch, "xpu") and torch.xpu.is_available()  # type: ignore[attr-defined]
    except Exception:
        has_xpu = False
    if has_xpu:
        return BackendKind.XPU

    return BackendKind.CPU


# ----------------------------- Precision policy ------------------------------

def _norm_precision_env() -> str:
    return (os.environ.get("SKOTE_PREF_PRECISION", "bf16") or "bf16").strip().lower()


def _supports_bf16(backend: str) -> bool:
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        # Ampere+ or ROCm gfx90a+ generally have bf16; probe dtype support instead of arch.
        try:
            x = torch.tensor([0.0], dtype=torch.bfloat16, device="cuda")
            return x.dtype == torch.bfloat16
        except Exception:
            return False
    if backend == BackendKind.XPU:
        # IPEX supports bf16 broadly; still probe.
        try:
            x = torch.tensor([0.0], dtype=torch.bfloat16, device="xpu")  # type: ignore
            return x.dtype == torch.bfloat16
        except Exception:
            return False
    # CPU bf16 is widely available in recent PyTorch; probe
    try:
        torch.tensor([0.0], dtype=torch.bfloat16)
        return True
    except Exception:
        return False


def _supports_fp16(backend: str) -> bool:
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            x = torch.tensor([0.0], dtype=torch.float16, device="cuda")
            return x.dtype == torch.float16
        except Exception:
            return False
    if backend == BackendKind.XPU:
        try:
            x = torch.tensor([0.0], dtype=torch.float16, device="xpu")  # type: ignore
            return x.dtype == torch.float16
        except Exception:
            return False
    # CPU half is usually not efficient; treat as unsupported preference.
    return False


def _supports_fp8(backend: str) -> bool:
    """
    FP8 is *not* universally supported in PyTorch stable; treat as hint only.
    """
    # Conservative: expose as False by default; override when user opts-in and libs exist.
    return False


def prefer_dtype() -> torch.dtype:
    """
    Decide the preferred compute dtype given env and capabilities.
    Priority (when supported): env -> bf16 -> fp16 -> fp32.
    """
    back = get_active_backend()
    pref = _norm_precision_env()

    if pref in ("fp8", "e4m3", "e5m2") and _supports_fp8(back):
        # Placeholder; map to float16 until fp8 kernels are explicit.
        return torch.float16

    if pref in ("bf16", "bfloat16") and _supports_bf16(back):
        return torch.bfloat16
    if pref in ("fp16", "half") and _supports_fp16(back):
        return torch.float16
    if pref in ("fp32", "float32"):
        return torch.float32

    # Fallback preference
    if _supports_bf16(back):
        return torch.bfloat16
    if _supports_fp16(back):
        return torch.float16
    return torch.float32


def dtype_priority() -> List[torch.dtype]:
    """
    Ordered list of candidate dtypes for loading weights / cast decisions.
    """
    d = prefer_dtype()
    order = [d]
    if d != torch.bfloat16 and _supports_bf16(get_active_backend()):
        order.append(torch.bfloat16)
    if d != torch.float16 and _supports_fp16(get_active_backend()):
        order.append(torch.float16)
    if torch.float32 not in order:
        order.append(torch.float32)
    return order


# ----------------------------- AMP / autocast ------------------------------

@contextlib.contextmanager
def amp_autocast(dtype: Optional[torch.dtype] = None, enabled: bool = True):
    """
    Unified autocast context manager (torch.amp API with safe fallbacks).

    - CUDA/ROCm: torch.amp.autocast("cuda", dtype=...)
      (fallback to torch.cuda.amp.autocast if needed)
    - XPU: torch.xpu.amp.autocast via IPEX when available, else try torch.amp.autocast("xpu")
    - CPU: ONLY enable when dtype in {bfloat16, float16}; otherwise no-op
           (prevents warnings on fp32 and avoids deprecated API).
    """
    if not enabled:
        yield
        return

    backend = get_active_backend()
    target_dtype = dtype or prefer_dtype()

    # --- CUDA / ROCm ---
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            from torch import amp as _amp
            with _amp.autocast("cuda", dtype=target_dtype):
                yield
                return
        except Exception:
            pass
        # Fallback to legacy API if torch.amp path is unavailable
        try:
            with torch.cuda.amp.autocast(dtype=target_dtype):
                yield
                return
        except Exception:
            pass

    # --- XPU ---
    if backend == BackendKind.XPU:
        if _HAS_IPEX and hasattr(torch, "xpu"):
            try:
                with torch.xpu.amp.autocast(dtype=target_dtype):  # type: ignore[attr-defined]
                    yield
                    return
            except Exception:
                pass
        try:
            from torch import amp as _amp
            with _amp.autocast("xpu", dtype=target_dtype):  # may not exist on all builds
                yield
                return
        except Exception:
            pass

    # --- CPU ---
    if target_dtype in (torch.bfloat16, torch.float16):
        # Use new torch.amp API first, then optional legacy fallback
        try:
            from torch import amp as _amp
            with _amp.autocast("cpu", dtype=target_dtype):
                yield
                return
        except Exception:
            pass
        try:
            with torch.cpu.amp.autocast(dtype=target_dtype):
                yield
                return
        except Exception:
            pass

    # Default: no autocast (avoids fp32-on-CPU warnings and deprecation warnings)
    yield


# ----------------------------- Streams & events ------------------------------

@dataclass
class StreamHandle:
    backend: str
    raw: Any  # torch Stream or None (no-op)

    def __enter__(self):
        if self.backend in (BackendKind.CUDA, BackendKind.ROCM) and self.raw is not None:
            return self.raw.__enter__()
        if self.backend == BackendKind.XPU and self.raw is not None:
            return self.raw.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.backend in (BackendKind.CUDA, BackendKind.ROCM) and self.raw is not None:
            return self.raw.__exit__(exc_type, exc, tb)
        if self.backend == BackendKind.XPU and self.raw is not None:
            return self.raw.__exit__(exc_type, exc, tb)
        return False

    def synchronize(self) -> None:
        if self.raw is None:
            return
        try:
            self.raw.synchronize()
        except Exception:
            pass


@dataclass
class EventHandle:
    backend: str
    raw: Any  # torch Event or None (no-op)

    def record(self, stream: Optional[StreamHandle] = None) -> None:
        if self.raw is None:
            return
        try:
            if stream is not None and stream.raw is not None:
                self.raw.record(stream.raw)
            else:
                self.raw.record()
        except Exception:
            pass

    def wait(self, stream: Optional[StreamHandle] = None) -> None:
        if self.raw is None:
            return
        try:
            if stream is not None and stream.raw is not None:
                stream.raw.wait_event(self.raw)
            else:
                self.raw.synchronize()
        except Exception:
            pass


def create_stream(device: Optional[torch.device] = None) -> StreamHandle:
    backend = get_active_backend()
    if device is None:
        if backend in (BackendKind.CUDA, BackendKind.ROCM):
            device = torch.device("cuda", torch.cuda.current_device())
        elif backend == BackendKind.XPU and hasattr(torch, "xpu"):
            device = torch.device("xpu", 0)  # type: ignore
        else:
            return StreamHandle(backend=backend, raw=None)

    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            s = torch.cuda.Stream(device=device)
            return StreamHandle(backend=backend, raw=s)
        except Exception:
            return StreamHandle(backend=backend, raw=None)

    if backend == BackendKind.XPU and hasattr(torch, "xpu"):
        try:
            # IPEX exposes torch.xpu.Stream in recent releases
            s = torch.xpu.Stream(device=device)  # type: ignore[attr-defined]
            return StreamHandle(backend=backend, raw=s)
        except Exception:
            return StreamHandle(backend=backend, raw=None)

    return StreamHandle(backend=backend, raw=None)


def create_event(enable_timing: bool = False) -> EventHandle:
    backend = get_active_backend()
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            e = torch.cuda.Event(enable_timing=enable_timing)
            return EventHandle(backend=backend, raw=e)
        except Exception:
            return EventHandle(backend=backend, raw=None)
    if backend == BackendKind.XPU and hasattr(torch, "xpu"):
        # No stable Event API across all versions; provide a no-op placeholder
        return EventHandle(backend=backend, raw=None)
    return EventHandle(backend=backend, raw=None)


# ----------------------------- Memory & P2P ------------------------------

def mem_get_info(device_index: Optional[int] = None) -> Tuple[Optional[int], Optional[int]]:
    """
    Return (free_bytes, total_bytes) for CUDA/ROCm; (None,None) otherwise.
    """
    backend = get_active_backend()
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            dev = device_index if device_index is not None else torch.cuda.current_device()
            with torch.cuda.device(dev):
                free_b, total_b = torch.cuda.mem_get_info()
            return int(free_b), int(total_b)
        except Exception:
            return None, None
    return None, None


def can_access_peer(src_index: int, dst_index: int) -> bool:
    backend = get_active_backend()
    if backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            return bool(torch.cuda.device_can_access_peer(dst_index, src_index))
        except Exception:
            return False
    # XPU: not universally exposed; return False conservatively
    return False


# ----------------------------- Triton kernels ------------------------------

def maybe_enable_triton_patches(model: Any, *, force: bool = False, attn_kernel: str = "auto") -> int:
    """
    Attempt to enable Skotergy Triton patches (rmsnorm, rope, attention routing).
    Returns number of modules patched. Safe no-op when Triton or backend is not supported.
    """
    if os.environ.get("SKOTE_FORCE_DISABLE_TRITON", "0") in ("1", "true", "True"):
        LOG.info("Triton patches disabled via SKOTE_FORCE_DISABLE_TRITON=1")
        return 0

    if not _HAS_SKOTE_TRITON:
        LOG.info("Skotergy triton_ops not available; skipping patches.")
        return 0

    backend = get_active_backend()
    if backend == BackendKind.CPU:
        LOG.info("CPU backend: Triton kernels disabled.")
        return 0

    try:
        patched = _enable_triton_patches(model, force=force, attn_kernel=attn_kernel)
        LOG.info("Enabled Triton patches: %d modules (attn=%s)", patched, attn_kernel)
        return int(patched)
    except Exception as e:
        LOG.warning("Failed to enable Triton patches: %s", e)
        return 0


def set_attention_kernel(model: Any, attn_kernel: str = "auto") -> str:
    """
    Route attention implementation (sdpa/flash*), when triton_ops provides the hook.
    """
    if not _HAS_SKOTE_TRITON:
        return "auto"
    try:
        return _set_attention_kernel(model, attn_kernel=attn_kernel)
    except Exception:
        return "auto"


# ----------------------------- Matmul precision ------------------------------

def set_matmul_precision(level: str = "high") -> None:
    """
    Forward to torch.set_float32_matmul_precision when available.

    - "high"   : prefer TF32/fast paths (default)
    - "medium" : allow more approximate kernels on some backends
    - "low"    : most permissive
    """
    try:
        torch.set_float32_matmul_precision(level)  # type: ignore[attr-defined]
    except Exception:
        pass


# ----------------------------- Convenience ------------------------------

def current_device() -> torch.device:
    """
    Return the current torch.device aligned with the active backend.
    """
    back = get_active_backend()
    if back in (BackendKind.CUDA, BackendKind.ROCM) and torch.cuda.is_available():
        return torch.device("cuda", torch.cuda.current_device())
    if back == BackendKind.XPU and hasattr(torch, "xpu") and torch.xpu.is_available():  # type: ignore[attr-defined]
        try:
            return torch.device("xpu", torch.xpu.current_device())  # type: ignore[attr-defined]
        except Exception:
            return torch.device("xpu", 0)
    return torch.device("cpu")


def to_device(t: torch.Tensor, device: Optional[torch.device] = None, non_blocking: bool = True) -> torch.Tensor:
    """
    Safe tensor move with sensible defaults.
    """
    device = device or current_device()
    if str(t.device) == str(device):
        return t
    return t.to(device, non_blocking=non_blocking)


# ----------------------------- Debug / CLI ------------------------------

if __name__ == "__main__":
    """
    Quick probe:
      $ python -m skote.compat.backends
    """
    b = get_active_backend()
    print("[backends] active:", b)
    print(" prefer dtype:", str(prefer_dtype()))
    print(" dtype priority:", [str(d) for d in dtype_priority()])
    d = current_device()
    print(" current device:", d)
    s = create_stream(d)
    e = create_event(enable_timing=True)
    with amp_autocast():
        x = torch.randn(1024, 1024, device=d, dtype=prefer_dtype())
        y = x @ x.t()
    e.record(s)
    s.synchronize()
    free, total = mem_get_info()
    print(" mem:", free, total)
