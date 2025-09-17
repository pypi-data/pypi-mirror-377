# skote/kernels/triton_ops.py
"""
Portable kernels for Skotergy (Triton-first with safe PyTorch fallback).

Provided ops:
- rmsnorm(x, weight, eps=1e-6) -> y
- rope_inplace(q, k, cos, sin, interleave=False)  # applies rotary embeddings to Q/K
- enable_triton_patches(model, *, force=False, attn_kernel="auto") -> int
- set_attention_kernel(model, attn_kernel="auto") -> str  # returns the effective kernel

Design goals:
- Always safe under mixed device_map (CPU/XPU/MPS + CUDA): auto fallback to torch.
- Work on CUDA (and Triton ROCm when available); degrade gracefully on CPU.
- Enforce strict dtype/shape checks; avoid hidden copies unless necessary.
- Monkey-patch HF models at the *parent level* (real module replacement).
- Attention-kernel routing stub (sdpa / flash-attn v2/v3) is best-effort and no-op when absent.

Env switches:
- SKOTE_TRITON_PATCH=0        -> disable Triton kernels globally (preferred toggle)
- SKOTE_DISABLE_TRITON=1      -> same effect as above (legacy/alt toggle)
- SKOTE_ATTN_KERNEL={auto|sdpa|fa2|fa3}  -> hint attention implementation
"""

from __future__ import annotations

import os
from typing import Optional, Tuple, Iterable

try:
    import torch
except Exception as e:  # pragma: no cover
    raise RuntimeError("triton_ops requires PyTorch installed.") from e

# ------------------------------------------------------------------------------
# Triton presence & global toggles
# ------------------------------------------------------------------------------
def _env_truthy(name: str, default: str = "0") -> bool:
    v = str(os.environ.get(name, default)).strip().lower()
    return v in {"1", "true", "yes", "on"}

def _env_falsy(name: str, default: str = "1") -> bool:
    v = str(os.environ.get(name, default)).strip().lower()
    return v in {"0", "false", "no", "off"}

# Two equivalent flags are supported; either can disable Triton.
_TRITON_DISABLED_VIA_PATCH = _env_falsy("SKOTE_TRITON_PATCH", default="1")  # 0 -> disable
_TRITON_DISABLED_VIA_LEGACY = _env_truthy("SKOTE_DISABLE_TRITON", default="0")  # 1 -> disable
_TRITON_DISABLE = _TRITON_DISABLED_VIA_PATCH or _TRITON_DISABLED_VIA_LEGACY

_TRITON_AVAILABLE = False
try:
    if not _TRITON_DISABLE:
        import triton  # type: ignore
        import triton.language as tl  # type: ignore
        _TRITON_AVAILABLE = True
except Exception:
    _TRITON_AVAILABLE = False


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
def _is_cuda_like_available() -> bool:
    try:
        return bool(torch.cuda.is_available())
    except Exception:
        return False

def is_triton_ready() -> bool:
    """Return True when Triton is importable AND a CUDA-like device is available."""
    try:
        return _TRITON_AVAILABLE and _is_cuda_like_available()
    except Exception:
        return False

def _cast_fp32(x: torch.Tensor) -> torch.Tensor:
    return x.float() if x.dtype not in (torch.float32,) else x

def _to_dtype(x: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
    return x if x.dtype == dtype else x.to(dtype)

def _assert_lastdim_match(x: torch.Tensor, w: torch.Tensor, name: str) -> None:
    if x.shape[-1] != w.shape[-1]:
        raise ValueError(f"{name}: last-dimension mismatch: x[..,{x.shape[-1]}] vs w[{w.shape[-1]}]")

def _as_contiguous_2d_view(x: torch.Tensor, D: int) -> Tuple[torch.Tensor, bool]:
    """
    Return (view, shares_storage).
    If x is already contiguous, avoid extra copy so in-place ops touch original.
    """
    if x.is_contiguous():
        return x.view(-1, D), True
    return x.contiguous().view(-1, D), False


# ------------------------------------------------------------------------------
# RMSNorm
# ------------------------------------------------------------------------------
def _rmsnorm_torch(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """
    PyTorch fallback RMSNorm: y = x / sqrt(mean(x^2) + eps) * weight
    Expect x: [..., D], weight: [D]
    """
    _assert_lastdim_match(x, weight, "rmsnorm")
    orig_dtype = x.dtype
    x32 = _cast_fp32(x)
    var = x32.pow(2).mean(dim=-1, keepdim=True)
    inv = torch.rsqrt(var + eps)
    y = (x32 * inv).to(orig_dtype) * _to_dtype(weight, orig_dtype)
    return y

if _TRITON_AVAILABLE:
    @triton.jit  # type: ignore[name-defined]
    def _rmsnorm_kernel(X, W, Y, eps, D: tl.constexpr, BLOCK: tl.constexpr):  # type: ignore[name-defined]
        """
        X: * x D (flattened)
        W: D
        Y: * x D (flattened)
        """
        pid = tl.program_id(0)
        offs = pid * D + tl.arange(0, BLOCK)
        mask = tl.arange(0, BLOCK) < D

        x = tl.load(X + offs, mask=mask, other=0.0)
        w = tl.load(W + tl.arange(0, BLOCK), mask=mask, other=1.0)

        sq = x * x
        mean = tl.sum(sq, axis=0) / D
        inv = 1.0 / tl.sqrt(mean + eps)
        y = x * inv * w
        tl.store(Y + offs, y, mask=mask)

class _RMSNormFn(torch.autograd.Function):
    """
    Autograd wrapper:
      - forward prefers Triton when ready AND input/weight on the same CUDA device;
        otherwise torch fallback.
      - backward uses an analytic formula with correct weight chaining and fp32 math.
      - Safe under mixed device maps: CPU tensors never enter Triton.
    """
    @staticmethod
    def forward(ctx, x: torch.Tensor, weight: torch.Tensor, eps: float):
        _assert_lastdim_match(x, weight, "rmsnorm")
        orig_1d = (x.dim() == 1)
        if orig_1d:
            x = x.unsqueeze(0)

        *batch, D = x.shape
        x_contig = x.contiguous()
        w_contig = weight.contiguous()

        # Triton only when x and weight are CUDA tensors on the *same* device.
        same_cuda = (
            is_triton_ready()
            and x_contig.is_cuda
            and w_contig.is_cuda
            and (x_contig.device == w_contig.device)
        )
        if same_cuda:
            # Make sure Triton runs on the correct CUDA device/stream.
            torch.cuda.set_device(x_contig.device)
            y = torch.empty_like(x_contig)
            BLOCK = 1 << (D - 1).bit_length()
            BLOCK = min(BLOCK, 4096)
            grid = (int(x_contig.numel() // D),)
            _rmsnorm_kernel[grid](x_contig, w_contig, y, eps, D=D, BLOCK=BLOCK)  # type: ignore[name-defined]
        else:
            # Safe fallback: CPU/MPS/XPU or cross-device tensors.
            y = _rmsnorm_torch(x_contig, w_contig, eps)

        # save tensors for backward in fp32
        ctx.save_for_backward(_cast_fp32(x_contig), _cast_fp32(w_contig))
        ctx.eps = float(eps)

        out = y.view(*batch, D)
        return out[0] if orig_1d else out

    @staticmethod
    def backward(ctx, grad_out: torch.Tensor):
        # Saved inputs in fp32 for stability
        x, w = ctx.saved_tensors
        eps = ctx.eps

        # inv and y in fp32
        var = x.pow(2).mean(dim=-1, keepdim=True)
        inv = torch.rsqrt(var + eps)        # shape [..., 1]
        y = x * inv                          # normalized x (fp32)

        # Chain rule: output = y * w  ==> dL/dy = grad_out * w
        grad_out = grad_out.to(y.dtype)
        gprime = grad_out * w               # includes weight per-dim

        # d(weight) = sum(grad_out * y) over all dims except the last
        gw = torch.sum((grad_out * y), dim=tuple(range(0, y.dim() - 1)))

        # d(x): g' * inv - x * inv^3 * mean(x·g')
        D = x.shape[-1]
        tmp = torch.sum(x * gprime, dim=-1, keepdim=True) / D
        gx = (gprime * inv) - (x * (inv ** 3) * tmp)

        return gx.to(grad_out.dtype), gw.to(w.dtype), None

def rmsnorm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """
    RMSNorm fused op with autograd; safe under mixed device maps.
    x: [..., D], weight: [D]
    """
    return _RMSNormFn.apply(x, weight, eps)


# ------------------------------------------------------------------------------
# RMSNorm Patching Layer
# ------------------------------------------------------------------------------
class RMSNormModule(torch.nn.Module):
    """
    Drop-in RMSNorm which calls our fused/tuned path (Triton or torch fallback).
    Intended to replace modules like transformers.models.llama.modeling_llama.LlamaRMSNorm.
    """
    def __init__(self, weight: torch.Tensor, eps: float = 1e-6):
        super().__init__()
        self.weight = torch.nn.Parameter(weight.detach().clone())
        self.eps = float(eps)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        return rmsnorm(x, self.weight, self.eps)

def _replace_children_recursive(parent: torch.nn.Module, target_names: Iterable[str]) -> int:
    """
    Replace child modules whose class name is in target_names with RMSNormModule.
    Returns the number of replacements.
    """
    patched = 0
    for name, child in list(parent.named_children()):
        cls = child.__class__.__name__
        if cls in target_names and hasattr(child, "weight"):
            eps = float(getattr(child, "eps", 1e-6))
            w = getattr(child, "weight")
            repl = RMSNormModule(w, eps=eps).to(device=w.device, dtype=w.dtype)
            setattr(parent, name, repl)
            patched += 1
        else:
            patched += _replace_children_recursive(child, target_names)
    return patched


# ------------------------------------------------------------------------------
# Model patch entry
# ------------------------------------------------------------------------------
def enable_triton_patches(
    model: torch.nn.Module,
    *,
    force: bool = False,
    attn_kernel: str = "auto",
) -> int:
    """
    Enable kernel-preferring patches on a loaded HF model.
    Currently: RMSNorm → our fused path; optional attention-kernel routing.
    Returns the number of modules patched.

    Safety:
    - We patch even on CPU when force=True; runtime will use the torch branch.
    - Under mixed device maps (some layers on CPU), our RMSNorm remains safe.
    """
    patched = 0
    try:
        target_cls = ("LlamaRMSNorm", "RMSNorm", "FusedRMSNorm")
        if force or is_triton_ready():
            patched += _replace_children_recursive(model, target_cls)
        else:
            if force:
                patched += _replace_children_recursive(model, target_cls)
    except Exception:
        # Never let patching break model load
        patched = patched

    # Attention kernel routing is best-effort and never fatal
    try:
        set_attention_kernel(model, attn_kernel=attn_kernel)
    except Exception:
        pass

    return patched


# ------------------------------------------------------------------------------
# Attention kernel routing (best-effort)
# ------------------------------------------------------------------------------
def set_attention_kernel(model: torch.nn.Module, attn_kernel: str = "auto") -> str:
    """
    Set attention implementation preference for the current runtime:
      - 'auto' : leave defaults (let Torch/HF decide).
      - 'sdpa' : prefer PyTorch scaled-dot-product-attention backends.
      - 'fa2'  : try FlashAttention-2 via model.config.attn_implementation when supported.
      - 'fa3'  : try FlashAttention-3 if available; fallback to 'fa2' or 'sdpa'.
    Returns the *effective* kernel string after applying preferences.

    Notes:
    - For SDPA, we adjust torch.backends.cuda SDP knobs when CUDA is available.
    - For FlashAttention, we don't hard-depend on the package; we only set the HF
      config to request flash kernels when the model/backends support it.
    """
    env = os.environ.get("SKOTE_ATTN_KERNEL", "").strip().lower()
    if env:
        attn_kernel = env

    attn_kernel = (attn_kernel or "auto").lower()
    effective = attn_kernel

    # Configure PyTorch SDPA backend preferences (safe to call on CPU)
    try:
        if torch.cuda.is_available():
            if attn_kernel in ("auto",):
                torch.backends.cuda.enable_flash_sdp(True)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
                torch.backends.cuda.enable_math_sdp(True)
            elif attn_kernel == "sdpa":
                torch.backends.cuda.enable_flash_sdp(False)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
                torch.backends.cuda.enable_math_sdp(True)
            # For FA2/FA3 we leave SDPA toggles permissive
    except Exception:
        pass

    # Hint HF config for flash-attn when applicable
    try:
        cfg = getattr(model, "config", None)
        if cfg is not None and hasattr(cfg, "attn_implementation"):
            if attn_kernel in ("fa3", "flash3", "flash_attention_3"):
                try:
                    cfg.attn_implementation = "flash_attention_3"
                except Exception:
                    cfg.attn_implementation = "flash_attention_2"
                    effective = "fa2"
            elif attn_kernel in ("fa2", "flash2", "flash_attention_2"):
                cfg.attn_implementation = "flash_attention_2"
            elif attn_kernel == "sdpa":
                cfg.attn_implementation = "sdpa"
            else:
                effective = getattr(cfg, "attn_implementation", "auto")
        else:
            if attn_kernel in ("fa2", "fa3"):
                effective = "sdpa"
    except Exception:
        pass

    return effective


# ------------------------------------------------------------------------------
# RoPE (Rotary Positional Embedding) for Q/K
# ------------------------------------------------------------------------------
def _rope_torch_inplace(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor, interleave: bool = False) -> None:
    """
    PyTorch fallback of rotary embedding applied in-place on the last dimension.
    Shapes:
      q, k: [..., D]
      cos, sin: [*, D/2] or broadcastable to q[...,:D/2]
    If interleave=True, treat even/odd dims as pairs; else split halves.
    """
    D = q.shape[-1]
    if interleave:
        q1, q2 = q[..., ::2], q[..., 1::2]
        k1, k2 = k[..., ::2], k[..., 1::2]
        q[..., ::2] = q1 * cos - q2 * sin
        q[..., 1::2] = q1 * sin + q2 * cos
        k[..., ::2] = k1 * cos - k2 * sin
        k[..., 1::2] = k1 * sin + k2 * cos
    else:
        half = D // 2
        q1, q2 = q[..., :half], q[..., half:]
        k1, k2 = k[..., :half], k[..., half:]
        q[..., :half] = q1 * cos - q2 * sin
        q[..., half:] = q1 * sin + q2 * cos
        k[..., :half] = k1 * cos - k2 * sin
        k[..., half:] = k1 * sin + k2 * cos

if _TRITON_AVAILABLE:
    @triton.jit  # type: ignore[name-defined]
    def _rope_kernel(Q, K, COS, SIN, D: tl.constexpr, INTERLEAVE: tl.constexpr):  # type: ignore[name-defined]
        """
        Apply RoPE in-place on last dim of Q/K.
        Q, K: [N, D] flattened; COS/SIN: [N, D/2] (or broadcast prepared by host)
        """
        pid = tl.program_id(0)
        offs = pid * D + tl.arange(0, D)
        q = tl.load(Q + offs)
        k = tl.load(K + offs)

        if INTERLEAVE:
            idx = tl.arange(0, D // 2)
            cos = tl.load(COS + pid * (D // 2) + idx)
            sin = tl.load(SIN + pid * (D // 2) + idx)
            q_even = q[0:D:2]
            q_odd  = q[1:D:2]
            k_even = k[0:D:2]
            k_odd  = k[1:D:2]
            q_even_new = q_even * cos - q_odd * sin
            q_odd_new  = q_even * sin + q_odd * cos
            k_even_new = k_even * cos - k_odd * sin
            k_odd_new  = k_even * sin + k_odd * cos
            q = tl.zeros([D], dtype=q.dtype)
            k = tl.zeros([D], dtype=k.dtype)
            q = tl.where(tl.arange(0, D) % 2 == 0, q_even_new, q_odd_new)
            k = tl.where(tl.arange(0, D) % 2 == 0, k_even_new, k_odd_new)
        else:
            half = D // 2
            idx = tl.arange(0, half)
            cos = tl.load(COS + pid * half + idx)
            sin = tl.load(SIN + pid * half + idx)
            q1 = q[:half]
            q2 = q[half:]
            k1 = k[:half]
            k2 = k[half:]
            q = tl.zeros([D], dtype=q.dtype)
            k = tl.zeros([D], dtype=k.dtype)
            q[:half] = q1 * cos - q2 * sin
            q[half:] = q1 * sin + q2 * cos
            k[:half] = k1 * cos - k2 * sin
            k[half:] = k1 * sin + k2 * cos

        tl.store(Q + offs, q)
        tl.store(K + offs, k)

def rope_inplace(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    *,
    interleave: bool = False,
) -> None:
    """
    Apply RoPE to Q and K in-place on their last dimension.

    Shapes (common layout):
      q, k: [B, H, T, D] or [*, D]
      cos, sin: broadcastable to [..., D/2] (prepare per sequence position)

    Guarantees:
      - Works on fp16/bf16/fp32.
      - Safe under mixed device maps: CPU tensors go torch path.
      - Avoids hidden copies unless necessary; copy-back when contiguous view was created.
    """
    if q.shape != k.shape:
        raise ValueError(f"rope_inplace: q/k shape must match, got {tuple(q.shape)} vs {tuple(k.shape)}")
    D = q.shape[-1]
    if D % 2 != 0:
        raise ValueError("rope_inplace: last-dimension must be even")

    qv, q_share = _as_contiguous_2d_view(q, D)
    kv, k_share = _as_contiguous_2d_view(k, D)

    half = D // 2
    cs = cos.expand(*q.shape[:-1], half).contiguous().view(-1, half)
    sn = sin.expand(*q.shape[:-1], half).contiguous().view(-1, half)

    # Triton only if Q and K are on the *same* CUDA device; move cos/sin if needed.
    same_cuda = (
        is_triton_ready()
        and qv.is_cuda
        and kv.is_cuda
        and (qv.device == kv.device)
    )
    if same_cuda:
        # Ensure auxiliary buffers live on the same device.
        if cs.device != qv.device:
            cs = cs.to(qv.device, non_blocking=True)
        if sn.device != qv.device:
            sn = sn.to(qv.device, non_blocking=True)
        torch.cuda.set_device(qv.device)

        grid = (qv.shape[0],)
        _rope_kernel[grid](qv, kv, cs, sn, D=D, INTERLEAVE=int(interleave))  # type: ignore[name-defined]
        if not q_share:
            q.copy_(qv)
        if not k_share:
            k.copy_(kv)
    else:
        # Safe fallback for CPU/MPS/XPU or cross-device tensors.
        _rope_torch_inplace(q, k, cs, sn, interleave=interleave)


# ------------------------------------------------------------------------------
# Smoke test (optional)
# ------------------------------------------------------------------------------
def _smoke_test(device: Optional[str] = None) -> Tuple[bool, str]:
    """
    Quick smoke test for dev: returns (ok, message).
    """
    try:
        dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
        x = torch.randn(4, 16, device=dev, dtype=torch.float16)
        w = torch.ones(16, device=dev, dtype=torch.float16)
        y = rmsnorm(x, w, 1e-6)
        if not torch.isfinite(y).all():
            return False, "rmsnorm produced non-finite"

        B, H, T, D = 1, 2, 3, 8
        q = torch.randn(B, H, T, D, device=dev, dtype=torch.float16)
        k = torch.randn(B, H, T, D, device=dev, dtype=torch.float16)
        cos = torch.cos(torch.arange(D//2, device=dev, dtype=torch.float32))[None, None, None, :]
        sin = torch.sin(torch.arange(D//2, device=dev, dtype=torch.float32))[None, None, None, :]
        rope_inplace(q, k, cos, sin, interleave=False)
        if not torch.isfinite(q).all():
            return False, "rope produced non-finite"

        eff = set_attention_kernel(type("M", (), {"config": type("C", (), {})()})(), attn_kernel=os.environ.get("SKOTE_ATTN_KERNEL", "auto"))
        return True, f"Triton={'on' if is_triton_ready() else 'off'} device={dev} attn={eff}"
    except Exception as e:
        return False, f"exception: {e}"

if __name__ == "__main__":  # pragma: no cover
    ok, msg = _smoke_test()
    print("triton_ops smoke:", ok, msg)
