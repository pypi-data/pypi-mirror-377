# skote/runtime/decode_graph_adapter.py
"""
PKV-first decode adapter for Skotergy, now device/shard/speculative aware.

Why this revision?
------------------
1) Device-scoped execution:
   - Accept an explicit `device` (or infer from the wrapped model).
   - All tensors are moved lazily with non_blocking copies.
   - Plays nicely with our per-device GraphManager caches.

2) ShardableKV integration (time-axis sharding across devices):
   - Optional `ShardableKV` backing store (best-effort, zero-intrusion).
   - When enabled, we mirror prompt prefill (optional) and per-step last-token K/V
     into the sharded KV via a stable per-sequence id.
   - Cross-device reads migrate pages by P2P or pinned host bounce per kv_store.py.

3) Speculative decoding cooperation (optional):
   - If the caller provides `spec_ctx={"propose_fn": ..., "verify_fn": ...}` we
     delegate to `SpeculativeOrchestrator`. Otherwise we run the eager PKV loop.
   - This keeps single-GPU behavior unchanged and allows multi-card setups where
     a cheap draft runs on one card and the target runs on another.

4) Graph path remains opportunistic:
   - We DO NOT force eager attention when graphs are on.
   - If the model exposes minimal fixed-shape decode hooks and decode graph utilities
     are present, we use the graph-safe path for the last-token step; otherwise we
     remain in eager+PKV.

Environment knobs
-----------------
SKOTE_FORCE_EAGER_ATTENTION = 0|1     # default 0; set 1 to force Transformers eager attention.
SKOTE_GRAPHS               = 0|1      # default 0; allow graph-safe decode path when available.
SKOTE_USE_SHARDABLE_KV     = 0|1      # default 1 if kv_store is importable, else 0.
SKOTE_KV_INIT_PREFILL      = 0|1      # default 0; mirror prefill KV into ShardableKV (may use RAM).
SKOTE_PKV_BUCKET           = int      # fixed-size PKV page (default 8192).

Public API (backward compatible)
--------------------------------
GraphDecodeAdapter(
    model, tok=None, eos_token_id=None, greedy_default=True, bucket=None,
    *, device: Optional[torch.device]=None,
    shard_ctx: Optional[dict]=None,      # { "kv_store"?: ShardableKV, "seq_id"?: int }
    spec_ctx: Optional[dict]=None,       # { "propose_fn", "verify_fn", "config"?: SpecConfig }
)
  .generate(input_ids, max_new_tokens=128, ..., device: Optional[torch.device]=None)

Notes
-----
- Batch size 1 for the decode loop (unchanged).
- ShardableKV is best-effort; if shapes are unexpected or unavailable we safely skip it.
- Speculative is opt-in via `spec_ctx` (or use our SpecConfig env defaults).
"""

from __future__ import annotations

import os
import itertools
from typing import Any, Dict, List, Optional, Tuple

import torch

# ---- tolerant import of our PKV manager -----------------------------------------
try:
    from skote.runtime.pkv import PKVManager
except Exception:
    try:
        from skotergy.runtime.pkv import PKVManager  # type: ignore
    except Exception as e:
        raise RuntimeError("PKVManager is required by decode_graph_adapter") from e

# ---- ShardableKV (optional) ------------------------------------------------------
try:
    from skote.distributed.kv_store import ShardableKV, create_kv_store  # type: ignore
    _HAS_SHARD_KV = True
except Exception:
    ShardableKV = None  # type: ignore
    create_kv_store = None  # type: ignore
    _HAS_SHARD_KV = False

# ---- speculative decode (optional) ----------------------------------------------
try:
    from skote.distributed.speculative import (
        SpecConfig,
        SpeculativeOrchestrator,
        DecodeContext as SpecCtx,
    )  # type: ignore
    _HAS_SPEC = True
except Exception:
    SpecConfig = None  # type: ignore
    SpeculativeOrchestrator = None  # type: ignore
    SpecCtx = None  # type: ignore
    _HAS_SPEC = False

# ---- (optional) graph util; only used if a graph-safe path exists ----------------
try:
    from skotergy.graph.capture_decode import decode_step_via_graph  # type: ignore
except Exception:
    try:
        from skote.graph.capture_decode import decode_step_via_graph  # type: ignore
    except Exception:
        decode_step_via_graph = None  # type: ignore


def _get_logger():
    try:
        from skote import get_logger  # type: ignore
        return get_logger("skote.runtime.decode_graph_adapter")
    except Exception:
        import logging
        logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))
        return logging.getLogger("skote.runtime.decode_graph_adapter")


log = _get_logger()

# --------------------------------- HF cache helpers --------------------------------

try:
    from transformers.cache_utils import DynamicCache  # transformers >=4.39
except Exception:
    DynamicCache = None  # type: ignore


def _as_hf_cache(past):
    """Convert legacy tuple/list KV to HF Cache if available; otherwise return as-is."""
    if DynamicCache is not None and isinstance(past, (list, tuple)):
        try:
            return DynamicCache.from_legacy_cache(past)
        except Exception:
            return past
    return past


def _cache_to_legacy(past):
    """Convert HF Cache to legacy tuple for PKV manager if it needs that."""
    try:
        if past is not None and hasattr(past, "to_legacy_cache"):
            return past.to_legacy_cache()
    except Exception:
        pass
    return past


# --------------------------------- misc helpers ------------------------------------

def _model_device(model: Any) -> torch.device:
    mod = getattr(model, "mod", None)
    if isinstance(mod, torch.nn.Module):
        return next(mod.parameters()).device
    if isinstance(model, torch.nn.Module):
        return next(model.parameters()).device
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _to_device(x: torch.Tensor, dev: torch.device) -> torch.Tensor:
    if x.device.type != dev.type or (dev.index is not None and x.device.index != dev.index):
        return x.to(dev, non_blocking=True)
    return x


def _maybe_force_eager_attention():
    """
    We DO NOT force eager when graphs are enabled.
    Only force eager if the user explicitly asks for it.
    """
    if os.environ.get("SKOTE_FORCE_EAGER_ATTENTION", "0") == "1":
        os.environ["TRANSFORMERS_ATTENTION_IMPLEMENTATION"] = "eager"


def _decode_text(tok: Any, ids: torch.Tensor) -> Optional[List[str]]:
    if tok is None:
        return None
    try:
        return tok.batch_decode(ids.tolist(), skip_special_tokens=True)
    except Exception:
        try:
            return tok.batch_decode(ids, skip_special_tokens=True)
        except Exception:
            return None


# --------------------------- KV extraction helpers (HF) ----------------------------

def _infer_kv_dims_from_past(past_legacy: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    Return per-token dims for ShardableKV as (dims_k, dims_v).
    We concatenate layers along a leading L dimension for each token row: [L, H, D].
    Assumes batch=1; raises if not satisfied.
    """
    if not isinstance(past_legacy, (list, tuple)) or len(past_legacy) == 0:
        raise ValueError("Cannot infer KV dims: empty past_key_values.")
    L = len(past_legacy)
    k0, v0 = past_legacy[0]
    if k0.dim() < 4 or v0.dim() < 4:
        raise ValueError("Unexpected KV tensor rank; expected [B,H,T,D]-like.")
    if int(k0.size(0)) != 1 or int(v0.size(0)) != 1:
        raise ValueError("ShardableKV helper expects batch=1 for decode.")
    H = int(k0.size(1))
    D = int(k0.size(-1))
    dims = (L, H, D)
    return dims, dims


def _extract_last_token_kv(past_legacy: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Extract last-token K/V across all layers and stack as [1, L, H, D] (time-major first dim).
    """
    ks, vs = [], []
    for k, v in past_legacy:
        # k/v: [B, H, T, D]; take T-1
        ks.append(k[0, :, -1, :].contiguous())  # [H,D]
        vs.append(v[0, :, -1, :].contiguous())
    K = torch.stack(ks, dim=0)  # [L,H,D]
    V = torch.stack(vs, dim=0)  # [L,H,D]
    return K.unsqueeze(0), V.unsqueeze(0)  # [1,L,H,D]


def _extract_full_kv(past_legacy: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Extract full prompt K/V as [T, L, H, D] (time-major).
    WARNING: may use significant memory for long prompts; guarded by env.
    """
    # Determine T from first layer
    T = int(past_legacy[0][0].size(2))
    L = len(past_legacy)
    H = int(past_legacy[0][0].size(1))
    D = int(past_legacy[0][0].size(3))
    # Build by iterating time to keep peak memory bounded
    K_all = []
    V_all = []
    for t in range(T):
        ks, vs = [], []
        for k, v in past_legacy:
            ks.append(k[0, :, t, :].contiguous())
            vs.append(v[0, :, t, :].contiguous())
        K_all.append(torch.stack(ks, dim=0))  # [L,H,D]
        V_all.append(torch.stack(vs, dim=0))
    K = torch.stack(K_all, dim=0)  # [T,L,H,D]
    V = torch.stack(V_all, dim=0)
    return K, V


# --------------------------- main adapter (PKV-first) ------------------------------

class GraphDecodeAdapter:
    """
    Decode driver that prioritizes PKV-based eager decoding.
    If (and only if) the bound model wrapper exposes a custom graph-safe decode
    path (detected via minimal hooks), we will use decode_step_via_graph for
    decode-only replay; otherwise remain in eager PKV mode.

    New (this revision):
    - device override and per-sequence sharded KV mirroring.
    - optional speculative orchestration via `spec_ctx`.
    """

    _SEQ_ID_COUNTER = itertools.count(1000)  # fallback seq ids when not provided

    def __init__(
        self,
        model: Any,
        tok: Optional[Any] = None,
        eos_token_id: Optional[int] = None,
        greedy_default: bool = True,
        bucket: Optional[int] = None,
        *,
        device: Optional[torch.device] = None,
        shard_ctx: Optional[Dict[str, Any]] = None,   # {"kv_store"?: ShardableKV, "seq_id"?: int}
        spec_ctx: Optional[Dict[str, Any]] = None,    # {"propose_fn":..., "verify_fn":..., "config"?: SpecConfig}
    ) -> None:
        _maybe_force_eager_attention()

        self.model = model
        self.tok = tok
        self.device = device or _model_device(model)
        self.greedy_default = bool(greedy_default)

        # EOS
        self.eos_token_id = int(eos_token_id) if eos_token_id is not None else None
        if self.eos_token_id is None and getattr(tok, "eos_token_id", None) is not None:
            self.eos_token_id = int(tok.eos_token_id)  # type: ignore

        # PKV manager (fixed-shape cache). Bucket from arg or env.
        bucket_env = int(os.environ.get("SKOTE_PKV_BUCKET", "8192"))
        self.bucket = int(bucket if bucket is not None else bucket_env)
        self.pkv: Optional[PKVManager] = None

        # ShardableKV
        self._want_shard_kv = (os.environ.get("SKOTE_USE_SHARDABLE_KV", "1") == "1") and _HAS_SHARD_KV
        self._kv_init_prefill = (os.environ.get("SKOTE_KV_INIT_PREFILL", "0") == "1")
        self._kv_store: Optional[ShardableKV] = None  # type: ignore
        self._seq_id: Optional[int] = None
        if self._want_shard_kv:
            try:
                if shard_ctx and isinstance(shard_ctx.get("kv_store"), object):
                    self._kv_store = shard_ctx["kv_store"]  # type: ignore[index]
                elif create_kv_store is not None:
                    self._kv_store = create_kv_store()  # type: ignore[call-arg]
                self._seq_id = int(shard_ctx.get("seq_id")) if shard_ctx and "seq_id" in shard_ctx else next(self._SEQ_ID_COUNTER)
            except Exception:
                self._kv_store = None

        # Speculative
        self._spec_ctx = spec_ctx or {}
        self._use_spec = bool(self._spec_ctx and _HAS_SPEC)

        # Graph flags
        self._graphs_enabled = os.environ.get("SKOTE_GRAPHS", "0") != "0"
        self._has_graph_util = decode_step_via_graph is not None

        # Detect graph-safe hooks on the model (aligned with runner.py injection):
        has_alloc = hasattr(model, "alloc_decode_inputs")
        has_update = hasattr(model, "update_decode_inputs")
        has_decode_step = hasattr(model, "decode_step")
        has_read_logits = hasattr(model, "read_decode_logits")
        self._allow_graph = bool(has_alloc and has_update and (has_decode_step or has_read_logits))

        log.info(
            "GraphDecodeAdapter ready (device=%s, eos=%s, greedy=%s, bucket=%d, graphs=%s, allow_graph=%s, shard_kv=%s, spec=%s)",
            str(self.device),
            str(self.eos_token_id),
            str(self.greedy_default),
            self.bucket,
            str(self._graphs_enabled),
            str(self._allow_graph),
            "on" if self._kv_store is not None else "off",
            "on" if self._use_spec else "off",
        )

    # -------------------------- PKV bootstrap -------------------------------------

    @torch.inference_mode()
    def _ensure_prefill_and_pkv(self, input_ids: torch.Tensor):
        """
        Eager prefill on the full prompt (once), then backfill the fixed PKV pages
        with the returned HF past_key_values. This is the foundation for the
        decode-only loop (last-token + PKV). Optionally mirror KV into ShardableKV.
        """
        if self.pkv is not None:
            return

        if not isinstance(input_ids, torch.Tensor) or input_ids.dtype not in (torch.int64, torch.long):
            raise TypeError("input_ids must be a Long tensor.")

        seq = _to_device(input_ids, self.device)
        attn_mask = torch.ones_like(seq, dtype=torch.long, device=seq.device)

        # Prefill with use_cache=True to get HF PKV
        out = self._forward(seq, attention_mask=attn_mask, use_cache=True)
        if not hasattr(out, "past_key_values"):
            raise RuntimeError("Model did not return past_key_values during prefill.")

        # Allocate fixed-shape PKV and copy-in (accept both Cache and legacy tuple)
        legacy = _cache_to_legacy(out.past_key_values)
        self.pkv = PKVManager.from_model(self.model, bucket=self.bucket)
        self.pkv.append_from_hf_past(legacy)

        # Optional: initialize ShardableKV with full prompt KV (may be heavy)
        if self._kv_store is not None and self._kv_init_prefill:
            try:
                dims_k, dims_v = _infer_kv_dims_from_past(legacy)  # type: ignore[arg-type]
                self._kv_store.ensure_seq(self._seq_id, dims_k, dims_v)  # type: ignore[arg-type]
                K_all, V_all = _extract_full_kv(legacy)  # [T,L,H,D]
                # Ensure tensors on kv_store device
                dev = self._kv_store.device  # type: ignore[union-attr]
                self._kv_store.append(self._seq_id, K_all.to(dev, non_blocking=True), V_all.to(dev, non_blocking=True))  # type: ignore[arg-type]
            except Exception:
                # Best-effort; continue without sharded prefill
                pass

    def _forward(self, *args, **kwargs):
        # Try different call conventions to be tolerant across wrappers
        mod = getattr(self.model, "mod", None)
        fn = None
        if isinstance(mod, torch.nn.Module):
            fn = mod.forward
        elif hasattr(self.model, "forward"):
            fn = self.model.forward  # type: ignore
        else:
            fn = self.model  # __call__
        return fn(*args, **kwargs)

    # -------------------------- one decode step -----------------------------------

    @torch.inference_mode()
    def _decode_step_eager_pkv(self, last_tok: torch.Tensor) -> torch.Tensor:
        """
        Default path: HF eager decode with variable-length past view sliced
        from our fixed PKV pages; then append the returned KV for the next step.
        Returns logits [B, V]. Mirrors the last-token K/V into ShardableKV if enabled.
        """
        if self.pkv is None or self.pkv.valid_len < 0:
            raise RuntimeError("PKV is not initialized; call _ensure_prefill_and_pkv first.")

        past = self.pkv.get_hf_past_view()
        out = self._forward(
            input_ids=last_tok.to(self.device, non_blocking=True),
            attention_mask=None,  # let HF build causal mask; q_len=1 hits the fast path
            past_key_values=_as_hf_cache(past),
            use_cache=True,
        )

        # Append last position K/V back into fixed pages
        if hasattr(out, "past_key_values"):
            legacy = _cache_to_legacy(out.past_key_values)
            self.pkv.append_from_hf_past(legacy)

            # Mirror last-token K/V into ShardableKV if available
            if self._kv_store is not None:
                try:
                    dims_k, dims_v = _infer_kv_dims_from_past(legacy)  # type: ignore[arg-type]
                    # ensure table if this is the first decode step
                    self._kv_store.ensure_seq(self._seq_id, dims_k, dims_v)  # type: ignore[arg-type]
                    K1, V1 = _extract_last_token_kv(legacy)  # [1,L,H,D]
                    dev = self._kv_store.device  # type: ignore[union-attr]
                    self._kv_store.append(self._seq_id, K1.to(dev, non_blocking=True), V1.to(dev, non_blocking=True))  # type: ignore[arg-type]
                except Exception:
                    pass

        logits = out.logits
        if logits.dim() == 3:
            logits = logits[:, -1, :]
        return logits

    @torch.inference_mode()
    def _decode_step_graph_safe(self, seqlen_current: int, last_tok: torch.Tensor) -> torch.Tensor:
        """
        Optional graph path. Requires:
          - graphs enabled,
          - graph util importable,
          - model exposing fixed-shape decode hooks (alloc/update + (decode_step or read_decode_logits)).
        We pass 'kv' as an opaque handle (the model wrapper is responsible for
        mapping it to fixed buffers). If unavailable, fall back to eager PKV.
        """
        if not (self._graphs_enabled and self._has_graph_util and self._allow_graph):
            return self._decode_step_eager_pkv(last_tok)

        # kv handle can be the PKV static view or a model-owned state
        kv_handle = getattr(self.model, "kv_state", None)
        if kv_handle is None and self.pkv is not None:
            # Provide a static view from PKV if model can consume it
            kv_handle = self.pkv.get_static_view()

        out = decode_step_via_graph(  # type: ignore
            self.model,
            seqlen_current,
            token_ids=last_tok.to(self.device, non_blocking=True),
            kv=kv_handle,
        )
        logits = out["logits"] if isinstance(out, dict) and "logits" in out else out
        if isinstance(logits, torch.Tensor) and logits.dim() == 3:
            logits = logits[:, -1, :]
        if not isinstance(logits, torch.Tensor):
            raise RuntimeError("Graph path did not return logits tensor.")
        return logits

    # --------------------------------- generate -----------------------------------

    @torch.inference_mode()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 128,
        *,
        kv: Any = None,  # kept for signature compatibility (unused in PKV path)
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        greedy: Optional[bool] = None,
        stop_at_eos: bool = True,
        return_text: bool = True,
        device: Optional[torch.device] = None,  # per-call override
    ) -> Dict[str, Any]:
        """
        Two paths:
          A) If `spec_ctx` provided and speculative module is available:
             delegate to SpeculativeOrchestrator (caller supplies propose/verify).
          B) Otherwise, run PKV-first decode loop with optional graph-safe step and
             best-effort ShardableKV mirroring.

        Returns: {"input_ids": Tensor[B=1, T], "text": Optional[List[str]]}
        """
        if device is not None:
            self.device = device  # override for this call

        if not isinstance(input_ids, torch.Tensor) or input_ids.dtype not in (torch.int64, torch.long):
            raise TypeError("input_ids must be a Long tensor.")
        if input_ids.size(0) != 1:
            raise ValueError("GraphDecodeAdapter currently supports batch size 1 for decode.")

        # Speculative delegation (opt-in; user provides hooks)
        if self._use_spec:
            try:
                cfg = self._spec_ctx.get("config") if self._spec_ctx else None
                if cfg is None and _HAS_SPEC:
                    cfg = SpecConfig.from_env()  # type: ignore[union-attr]
                propose_fn = self._spec_ctx["propose_fn"]
                verify_fn = self._spec_ctx["verify_fn"]
                orch = SpeculativeOrchestrator(cfg, propose_fn, verify_fn)  # type: ignore[call-arg]
                ctx = SpecCtx(seq_id=int(self._seq_id or 0), device=self.device, meta={"adapter": "decode_graph"})  # type: ignore[call-arg]
                # User-provided hooks must interpret ctx/meta as needed.
                out = orch.generate(ctx, max_new_tokens=int(max_new_tokens))  # type: ignore[attr-defined]
                seq = torch.cat([_to_device(input_ids, self.device), out.tokens.view(1, -1)], dim=-1)
                out_text = _decode_text(self.tok, seq) if return_text else None
                return {"input_ids": seq, "text": out_text, "spec_meta": out.meta}
            except Exception:
                # Fallback to normal path on any issue
                pass

        # Normal PKV-first path
        seq = _to_device(input_ids, self.device)
        self._ensure_prefill_and_pkv(seq)

        eos = self.eos_token_id
        greedy_flag = self.greedy_default if greedy is None else bool(greedy)
        done = torch.zeros((1,), dtype=torch.bool, device=seq.device)

        for _ in range(int(max_new_tokens)):
            seqlen_current = int(seq.shape[-1])
            last_tok = seq[:, -1:].contiguous()

            # Step (prefer graph-safe if available, else eager PKV)
            logits = self._decode_step_graph_safe(seqlen_current, last_tok)

            # Sample
            if greedy_flag:
                next_tok = torch.argmax(logits, dim=-1, keepdim=True)
            else:
                t = float(temperature) if (temperature is not None) else 1.0
                p = float(top_p) if (top_p is not None) else 1.0
                t = max(1e-6, t)
                probs = torch.softmax(logits / t, dim=-1)
                if p >= 1.0:
                    next_tok = torch.multinomial(probs, 1)
                else:
                    sorted_probs, sorted_idx = torch.sort(probs, dim=-1, descending=True)
                    cdf = torch.cumsum(sorted_probs, dim=-1)
                    mask = cdf <= p
                    mask[..., 0] = True
                    nucleus = sorted_probs * mask
                    denom = nucleus.sum(dim=-1, keepdim=True)
                    denom = torch.where(denom > 0, denom, torch.ones_like(denom))
                    nucleus = nucleus / denom
                    sampled = torch.multinomial(nucleus, 1)
                    next_tok = torch.gather(sorted_idx, dim=-1, index=sampled)

            # Respect done rows
            if eos is not None and stop_at_eos:
                eos_tok = torch.full((1, 1), int(eos), dtype=torch.long, device=seq.device)
                next_tok = torch.where(done.view(1, 1), eos_tok, next_tok)

            seq = torch.cat([seq, next_tok], dim=-1)
            if eos is not None and stop_at_eos:
                done = done | (next_tok.view(-1) == int(eos))
                if bool(done.all()):
                    break

            # Safety: stop if fixed PKV bucket full
            if self.pkv is not None and self.pkv.valid_len >= self.pkv.bucket:
                break

        out_text = _decode_text(self.tok, seq) if return_text else None
        return {"input_ids": seq, "text": out_text}
