# skote/runtime/pkv.py
"""
Fixed-shape Past-Key-Value (PKV) manager for decode-only execution in Skotergy.

Why this exists
---------------
HF causal LMs typically grow `past_key_values` length step-by-step (concat),
which changes tensor shapes every iteration and defeats CUDA Graph capture.
This module provides a *fixed-bucket* PKV cache per layer:

  - Keys/Values are preallocated as dense pages: [B, n_kv_heads, bucket, head_dim]
  - Each decode step writes only the *new token's* K/V at write_position
  - Attention uses a precomputed/updated mask to ignore unused slots
  - Shapes stay constant → safe to capture/replay the decode step

Scope & guarantees
------------------
- Batch size: 1 (extension hooks exist but kept minimal for stability)
- Model family: HF Llama-like causal LMs (GQA supported via n_kv_heads)
- Device/dtype: inferred from model; overrideable
- Works without UPM; optionally integrates with a UPM-style allocator if present

Integration points (public API)
-------------------------------
PKVManager.from_model(model, bucket, ...)
  → build cache spec from a HF model, allocate fixed buffers

PKVManager.reset()
  → empty the cache (write_position ← 0, masks cleared)

PKVManager.append_from_hf_past(hf_past)
  → copy the *last-token* K/V returned by HF forward into fixed buffers

PKVManager.get_hf_past_view()
  → (optional, eager baseline) return a *variable-length* HF-style past view
     that slices the fixed buffers up to current write_position

PKVManager.get_static_view()
  → return (K_list, V_list, attn_mask, write_position) with *fixed shapes*
     for graph-safe decode kernels / wrappers

PKVManager.update_mask()
  → refresh attention mask after external write_position changes

Design choices
--------------
- We do not attempt to make HF forward *consume* our fixed buffers directly
  (that requires framework-level cache adapters). Instead, the manager:
    (a) offers a variable-length HF view for eager baselines;
    (b) offers a static fixed-shape view for custom/graph-safe decode paths.
- Copying the last-token K/V into fixed buffers costs O(n_layers * heads * d),
  which is negligible vs. a full decode step and unlocks graph reuse.

Author: Skotergy team
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

import os
import torch


# ------------------------------- helpers -----------------------------------------


def _model_device(model: Any) -> torch.device:
    mod = getattr(model, "mod", None)
    if isinstance(mod, torch.nn.Module):
        return next(mod.parameters()).device
    if isinstance(model, torch.nn.Module):
        return next(model.parameters()).device
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _model_dtype(model: Any) -> torch.dtype:
    # Prefer model parameter dtype; fall back to float16/float32 preference
    mod = getattr(model, "mod", None)
    src = mod if isinstance(mod, torch.nn.Module) else model if isinstance(model, torch.nn.Module) else None
    if isinstance(src, torch.nn.Module):
        return next(src.parameters()).dtype
    # Default for cache tensors (attention usually in model dtype)
    return torch.bfloat16 if torch.cuda.is_available() else torch.float32


def _infer_spec_from_hf(model: Any) -> Tuple[int, int, int]:
    """
    Return (n_layers, n_kv_heads, head_dim) for a Llama-like HF model.
    Works for GQA: n_kv_heads may be < n_attn_heads.
    """
    cfg = getattr(getattr(model, "mod", model), "config", None)
    if cfg is None:
        raise RuntimeError("Cannot infer spec: model has no .config")

    n_layers = int(getattr(cfg, "num_hidden_layers", getattr(cfg, "num_layers", 0)))
    n_heads = int(getattr(cfg, "num_attention_heads", 0))
    n_kv = int(getattr(cfg, "num_key_value_heads", n_heads))
    hidden = int(getattr(cfg, "hidden_size", 0))
    if not (n_layers and n_heads and hidden):
        raise RuntimeError("Incomplete model config for PKV spec inference")

    if hidden % n_heads != 0:
        raise RuntimeError(f"hidden_size {hidden} not divisible by num_attention_heads {n_heads}")
    head_dim = hidden // n_heads
    return n_layers, n_kv, head_dim


# ------------------------------- data structs -------------------------------------


@dataclass
class LayerCache:
    k: torch.Tensor  # [B, n_kv_heads, bucket, head_dim]
    v: torch.Tensor  # [B, n_kv_heads, bucket, head_dim]


@dataclass
class PKVStaticView:
    keys: List[torch.Tensor]         # per-layer K fixed tensors
    values: List[torch.Tensor]       # per-layer V fixed tensors
    attn_mask: torch.Tensor          # [B, bucket] (0/1)
    valid_len: int                   # number of filled positions (0..bucket)


# ------------------------------- main manager -------------------------------------


class PKVManager:
    """
    Manages fixed-shape per-layer K/V pages with a moving write pointer.

    Typical decode loop (graph-preferred path):
        pkv = PKVManager.from_model(model, bucket=8192)
        pkv.reset()
        # prefill: run eager on the whole prompt, then fill cache by copying HF past
        out = model(input_ids=prefill_ids, use_cache=True)
        pkv.append_from_hf_past(out.past_key_values)  # fills first T positions
        # capture decode graph once per bucket using pkv.get_static_view()
        # then for each step:
            # run model for last_token via your custom decode that *reads* pkv.static_view
            # and returns logits *and* last-token K/V (or raw projections) to write:
            pkv.write_token_kv(k_last, v_last)  # or pkv.append_from_hf_past(hf_past)
            pkv.update_mask()

    Eager baseline (no graph):
        model(..., past_key_values=pkv.get_hf_past_view(), use_cache=True)

    NOTE: This module does not require UPM but cooperates with it if present.
    """

    def __init__(
        self,
        *,
        n_layers: int,
        n_kv_heads: int,
        head_dim: int,
        bucket: int,
        device: torch.device,
        dtype: torch.dtype,
        batch_size: int = 1,
        pad_value: float = 0.0,
    ) -> None:
        if batch_size != 1:
            raise NotImplementedError("PKVManager currently supports batch_size=1 to keep graph shapes stable.")

        self.n_layers = int(n_layers)
        self.n_kv_heads = int(n_kv_heads)
        self.head_dim = int(head_dim)
        self.bucket = int(bucket)
        self.device = device
        self.dtype = dtype
        self.batch_size = int(batch_size)
        self.pad_value = float(pad_value)

        self.layers: List[LayerCache] = []
        self.attn_mask = torch.zeros((self.batch_size, self.bucket), dtype=torch.long, device=self.device)
        self.valid_len: int = 0  # number of filled positions [0..bucket]

        self._alloc_pages()

    # -------- construction --------

    @classmethod
    def from_model(
        cls,
        model: Any,
        bucket: int,
        *,
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
        batch_size: int = 1,
    ) -> "PKVManager":
        n_layers, n_kv, head_dim = _infer_spec_from_hf(model)
        dev = device if device is not None else _model_device(model)
        dt = dtype if dtype is not None else _model_dtype(model)
        return cls(
            n_layers=n_layers,
            n_kv_heads=n_kv,
            head_dim=head_dim,
            bucket=bucket,
            device=dev,
            dtype=dt,
            batch_size=batch_size,
        )

    def _alloc_pages(self) -> None:
        self.layers.clear()
        for _ in range(self.n_layers):
            k = torch.empty(
                (self.batch_size, self.n_kv_heads, self.bucket, self.head_dim),
                device=self.device,
                dtype=self.dtype,
            )
            v = torch.empty_like(k)
            # Optional: wipe with pad_value for deterministic behavior
            if self.pad_value != 0.0:
                k.fill_(self.pad_value)
                v.fill_(self.pad_value)
            self.layers.append(LayerCache(k=k, v=v))
        self.attn_mask.zero_()
        self.valid_len = 0

    # -------- lifecycle --------

    def reset(self) -> None:
        self.attn_mask.zero_()
        self.valid_len = 0
        # Do not memset huge pages every time (keep as-is). If required:
        # for lc in self.layers: lc.k.zero_(); lc.v.zero_()

    # -------- views --------

    def get_static_view(self) -> PKVStaticView:
        """
        Return fixed-shape tensors for graph-safe decode; the consumer must use
        `attn_mask` and `valid_len` to ignore unused slots.
        """
        return PKVStaticView(
            keys=[lc.k for lc in self.layers],
            values=[lc.v for lc in self.layers],
            attn_mask=self.attn_mask,
            valid_len=self.valid_len,
        )

    def get_hf_past_view(self) -> Tuple[Tuple[torch.Tensor, torch.Tensor], ...]:
        """
        Build a *variable-length* HF-style past_key_values by slicing up to valid_len.
        Useful for eager baselines; NOT graph-safe (shapes change as valid_len grows).
        """
        L = max(self.valid_len, 0)
        if L == 0:
            # HF expects empty PKV as None (no cache) or zero-length slices; we return zero-length
            return tuple((lc.k[:, :, :0, :], lc.v[:, :, :0, :]) for lc in self.layers)  # type: ignore[return-value]
        return tuple((lc.k[:, :, :L, :], lc.v[:, :, :L, :]) for lc in self.layers)  # type: ignore[return-value]

    # -------- mask/update --------

    def update_mask(self, new_valid_len: Optional[int] = None) -> None:
        """
        Update attention mask (1=valid position, 0=pad) after writes.
        """
        if new_valid_len is not None:
            self.valid_len = int(new_valid_len)
        L = max(0, min(self.valid_len, self.bucket))
        self.attn_mask.zero_()
        if L > 0:
            self.attn_mask[:, :L].fill_(1)

    # -------- writers (the critical path) --------

    def write_token_kv(
        self,
        k_per_layer: Sequence[torch.Tensor],
        v_per_layer: Sequence[torch.Tensor],
    ) -> None:
        """
        Write one token's K/V into fixed pages at index `valid_len` (append),
        then advance `valid_len` by 1 and update mask.

        Expected shapes per layer:
            k_t: [B=1, n_kv_heads, 1, head_dim]  or  [B=1, n_kv_heads, head_dim]
            v_t: same as k_t
        We will expand/squeeze to [B, n_kv_heads, 1, head_dim] if needed.
        """
        if len(k_per_layer) != self.n_layers or len(v_per_layer) != self.n_layers:
            raise ValueError("write_token_kv: number of layers does not match cache spec")

        pos = self.valid_len
        if pos >= self.bucket:
            raise RuntimeError("write_token_kv: cache is full (pos >= bucket)")

        for li, (k_t, v_t) in enumerate(zip(k_per_layer, v_per_layer)):
            if k_t.dim() == 3:  # [B, n_kv, head_dim]
                k_t = k_t.unsqueeze(2)
            if v_t.dim() == 3:
                v_t = v_t.unsqueeze(2)
            if k_t.shape != (self.batch_size, self.n_kv_heads, 1, self.head_dim):
                raise RuntimeError(f"write_token_kv: unexpected k_t shape at layer {li}: {tuple(k_t.shape)}")
            if v_t.shape != (self.batch_size, self.n_kv_heads, 1, self.head_dim):
                raise RuntimeError(f"write_token_kv: unexpected v_t shape at layer {li}: {tuple(v_t.shape)}")
            self.layers[li].k[:, :, pos : pos + 1, :].copy_(k_t, non_blocking=True)
            self.layers[li].v[:, :, pos : pos + 1, :].copy_(v_t, non_blocking=True)

        self.valid_len = pos + 1
        self.update_mask()

    def append_from_hf_past(self, hf_past: Any) -> None:
        """
        Append last-token K/V from an HF-style `past_key_values` into fixed buffers.

        Accepts:
            - Tuple[Tuple[k, v], ...] with shapes [..., past_len, head_dim]
            - Newer HF cache objects exposing .to_tuple() (we'll try to unwrap)
        Behavior:
            - If `valid_len` is 0 and hf_past has length >1, we will backfill from 0..L-1
              by copying entire sequences to the left of our pages (clipped to bucket).
            - Otherwise, we copy only the *last* position as a single step append.
        """
        if hf_past is None:
            return

        # Try to normalize into tuple-of-layer-tuples
        if hasattr(hf_past, "to_tuple"):
            hf_past = hf_past.to_tuple()  # type: ignore

        if not isinstance(hf_past, (tuple, list)) or not len(hf_past) == self.n_layers:
            raise RuntimeError("append_from_hf_past: incompatible past format")

        # Determine incoming length
        try:
            # assume shape: [B, n_kv, L, D]
            L_in = int(hf_past[0][0].size(-2))
        except Exception as e:
            raise RuntimeError(f"append_from_hf_past: cannot read incoming length: {e}")

        # Case A: initial backfill (prefill just ran)
        if self.valid_len == 0 and L_in > 1:
            L_copy = min(L_in, self.bucket)
            left = L_in - L_copy
            for li in range(self.n_layers):
                k_src, v_src = hf_past[li]
                k_slice = k_src[:, :, left:L_in, :].to(device=self.device, dtype=self.dtype, non_blocking=True)
                v_slice = v_src[:, :, left:L_in, :].to(device=self.device, dtype=self.dtype, non_blocking=True)
                self.layers[li].k[:, :, :L_copy, :].copy_(k_slice, non_blocking=True)
                self.layers[li].v[:, :, :L_copy, :].copy_(v_slice, non_blocking=True)
            self.valid_len = L_copy
            self.update_mask()
            return

        # Case B: normal decode append (only last position)
        if L_in < 1:
            return
        last_idx = L_in - 1
        k_tok: List[torch.Tensor] = []
        v_tok: List[torch.Tensor] = []
        for li in range(self.n_layers):
            k_src, v_src = hf_past[li]
            k_last = k_src[:, :, last_idx:last_idx + 1, :].to(device=self.device, dtype=self.dtype, non_blocking=True)
            v_last = v_src[:, :, last_idx:last_idx + 1, :].to(device=self.device, dtype=self.dtype, non_blocking=True)
            k_tok.append(k_last)
            v_tok.append(v_last)
        self.write_token_kv(k_tok, v_tok)

    # -------- debug / stats --------

    def stats(self) -> dict:
        return {
            "layers": self.n_layers,
            "kv_heads": self.n_kv_heads,
            "head_dim": self.head_dim,
            "bucket": self.bucket,
            "valid_len": self.valid_len,
            "device": str(self.device),
            "dtype": str(self.dtype).replace("torch.", ""),
        }
