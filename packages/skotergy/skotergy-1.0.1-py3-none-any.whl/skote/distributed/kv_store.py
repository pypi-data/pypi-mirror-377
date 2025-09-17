# skote/distributed/kv_store.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Shardable KV store for Skotergy.

Design goals
------------
- Drop-in replacement for single-device PKV manager with identical high-level semantics:
    * create / append / read_window / evict / free / stats
- Page-based KV with optional host spill and lightweight Q8_0 compression.
- Auto "T-shard" across multiple devices (time-axis sharding) with best-effort remote reads:
  - If peer access is enabled -> cudaMemcpyPeer
  - Else -> bounce via pinned host buffer
- Safe single-device fast path with minimal overhead.
- Zero hard dependency on collectives; when collectives are available later,
  cross-rank gather/scatter can be wired at two hooks (see TODO notes).

Environment knobs
-----------------
SKOTE_KV_PAGED=1                 : enable page-based KV (default=1)
SKOTE_KV_PAGE_TOKENS=512         : tokens per page (default=512)
SKOTE_KV_SPILL_HOST=1            : allow host-pinned spill (default=1)
SKOTE_KV_COMPRESS=none|Q8_0      : enable lossy page compression on cold pages (default=none)
SKOTE_KV_EVICT_POLICY=lru-hotshield : eviction strategy (default=lru-hotshield)
SKOTE_KV_HOTSHIELD_TOKENS=2048   : do not evict last N tokens per sequence (default=2048)
SKOTE_KV_REMOTE_READ=1           : allow cross-device on-demand reads (default=1)
SKOTE_KV_PREFETCH=1              : prefetch next page to target device on window reads (default=1)

Integration with Skotergy
-------------------------
- On single GPU, simply instantiate ShardableKV with current device; behavior matches local PKV.
- On multi GPU (single node / multi-process), each rank/process owns its local pages;
  when read_window() targets a different device, data migrates by P2P or host bounce.
- With collectives.py in the future, route remote reads via all_gather/reduce_scatter
  for cross-rank scenarios (TODO stubs provided).

API (subset superset of PKV semantics)
--------------------------------------
- ensure_seq(seq_id, kv_dim): initialize sequence table
- append(seq_id, k, v): append T tokens (time-major)
- read_window(seq_id, start, end, device=None): return [K,V] for [start,end)
- evict(seq_id, up_to_step): evict pages fully before up_to_step respecting hotshield
- free(seq_id): free all pages of sequence
- stats(): memory & page statistics
- state_dict() / load_state_dict(): checkpoint support (single-node best effort)

NOTE
----
This module focuses on robustness and portability. It does not assume specific
K/V tensor shape beyond time-major compatibility. Minimal assumption:
  K.shape == [T, ...], V.shape == [T, ...] with identical T.
"""

from __future__ import annotations

import os
import math
import time
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

try:
    import torch
    from torch import Tensor
except Exception as e:  # pragma: no cover
    raise RuntimeError("ShardableKV requires PyTorch") from e

# Optional utilities: we avoid hard deps; logging plugs into Skotergy's logger if present.
def _get_logger(name: str) -> logging.Logger:
    try:
        from skote import get_logger  # type: ignore
        return get_logger(name)
    except Exception:
        logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))
        return logging.getLogger(name)

LOG = _get_logger("skotergy.kv_store")


# ------------------------------ Config helpers ------------------------------

def _env_true(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip() in ("1", "true", "True", "YES", "yes")

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default

def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)

# Defaults
KV_PAGED = _env_true("SKOTE_KV_PAGED", True)
PAGE_TOKENS = _env_int("SKOTE_KV_PAGE_TOKENS", 512)
ALLOW_SPILL = _env_true("SKOTE_KV_SPILL_HOST", True)
COMPRESS_KIND = _env_str("SKOTE_KV_COMPRESS", "none").upper()
EVICT_POLICY = _env_str("SKOTE_KV_EVICT_POLICY", "lru-hotshield")
HOTSHIELD_TOK = _env_int("SKOTE_KV_HOTSHIELD_TOKENS", 2048)
REMOTE_READ = _env_true("SKOTE_KV_REMOTE_READ", True)
PREFETCH = _env_true("SKOTE_KV_PREFETCH", True)


# ------------------------------ Compression ------------------------------

class CompressionCodec:
    """
    Very light-weight per-page Q8_0 codec: int8 with a single scale per page.
    This is intentionally simple and fast; for better quality use blockwise quantization.
    """

    @staticmethod
    def encode_q8_0(x: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Quantize to int8 with a single positive scale per page:
          scale = max(abs(x)) / 127
          q = round(x / max(scale, eps))
        Returns (q:int8, scale:float32[1])
        """
        if x.numel() == 0:
            return x.to(torch.int8), torch.tensor([1.0], dtype=torch.float32, device=x.device)
        with torch.no_grad():
            max_abs = torch.amax(torch.abs(x))
            scale = torch.clamp(max_abs / 127.0, min=1e-8)
            q = torch.round(x / scale).to(torch.int8)
            return q, scale.to(torch.float32).reshape(1)

    @staticmethod
    def decode_q8_0(q: Tensor, scale: Tensor, dtype: torch.dtype) -> Tensor:
        with torch.no_grad():
            return (q.to(torch.float32) * scale.to(torch.float32)).to(dtype)


# ------------------------------ Page & Tables ------------------------------

@dataclass
class Page:
    """
    A KV page containing a contiguous token segment for a given sequence.
    """
    seq_id: int
    start: int       # inclusive token index within the sequence
    length: int      # token count inside this page
    device: torch.device
    k: Optional[Tensor] = None
    v: Optional[Tensor] = None

    # Host spill / compression buffers
    on_host: bool = False
    host_k: Optional[Tensor] = None   # pinned int8/float storages
    host_v: Optional[Tensor] = None
    comp: str = "none"                # "none" | "Q8_0"
    k_scale: Optional[Tensor] = None  # shape [1], float32 on device/host
    v_scale: Optional[Tensor] = None

    last_use_ts: float = field(default_factory=lambda: time.time())

    def token_range(self) -> Tuple[int, int]:
        return self.start, self.start + self.length

    def touch(self) -> None:
        self.last_use_ts = time.time()

    def is_hot(self, seq_len: int) -> bool:
        """
        Hotshield: protect last HOTSHIELD_TOK tokens of the sequence from eviction.
        """
        if HOTSHIELD_TOK <= 0:
            return False
        s, e = self.token_range()
        return e > max(0, seq_len - HOTSHIELD_TOK)


@dataclass
class SeqTable:
    """
    Per-sequence table mapping token intervals to pages and maintaining meta info.
    """
    kv_dim_k: Optional[Tuple[int, ...]] = None
    kv_dim_v: Optional[Tuple[int, ...]] = None
    length: int = 0
    pages: List[Page] = field(default_factory=list)


# ------------------------------ KV Store ------------------------------

class ShardableKV:
    """
    Page-based, optionally sharded KV manager.

    - Time-major append and window reads.
    - Transparent host spill and optional Q8_0 compression on cold pages.
    - Multi-device aware: each page has an owner device; remote reads are served
      via P2P or host bounce.
    """

    def __init__(self,
                 device: Optional[torch.device] = None,
                 page_tokens: int = PAGE_TOKENS,
                 paged: bool = KV_PAGED,
                 allow_spill: bool = ALLOW_SPILL,
                 compress_kind: str = COMPRESS_KIND,
                 evict_policy: str = EVICT_POLICY):
        self.page_tokens = max(1, int(page_tokens))
        self.paged = bool(paged)
        self.allow_spill = bool(allow_spill)
        self.compress_kind = compress_kind.upper()
        self.evict_policy = evict_policy
        self.tables: Dict[int, SeqTable] = {}
        self.device = device or (torch.device("cuda", torch.cuda.current_device()) if torch.cuda.is_available() else torch.device("cpu"))
        self._stat_pages = 0

        LOG.info("ShardableKV init: device=%s, page_tokens=%d, paged=%s, spill=%s, compress=%s, evict=%s",
                 str(self.device), self.page_tokens, self.paged, self.allow_spill, self.compress_kind, self.evict_policy)

    # ---------- Public API (PKV-compatible superset) ----------

    def ensure_seq(self, seq_id: int, kv_dim_k: Tuple[int, ...], kv_dim_v: Tuple[int, ...]) -> None:
        """
        Ensure a sequence table exists. kv_dim_* are shapes for a *single token* K/V row
        (e.g., [num_heads, head_dim] flattened or structured; we store as-is).
        """
        if seq_id not in self.tables:
            self.tables[seq_id] = SeqTable(kv_dim_k=kv_dim_k, kv_dim_v=kv_dim_v, length=0, pages=[])
        else:
            st = self.tables[seq_id]
            if st.kv_dim_k is None:
                st.kv_dim_k = kv_dim_k
            if st.kv_dim_v is None:
                st.kv_dim_v = kv_dim_v

    def append(self, seq_id: int, k: Tensor, v: Tensor, device: Optional[torch.device] = None) -> None:
        """
        Append T tokens (time-major) to the sequence KV.
        T = k.shape[0] = v.shape[0]. The remaining dimensions are per-token.
        """
        assert k.shape[0] == v.shape[0], "K/V time length mismatch"
        T = int(k.shape[0])

        if seq_id not in self.tables:
            self.ensure_seq(seq_id, tuple(k.shape[1:]), tuple(v.shape[1:]))
        st = self.tables[seq_id]
        if st.kv_dim_k is None or st.kv_dim_v is None:
            self.ensure_seq(seq_id, tuple(k.shape[1:]), tuple(v.shape[1:]))

        dev = device or self.device
        k = k.to(dev, non_blocking=True)
        v = v.to(dev, non_blocking=True)

        if not self.paged:
            # Single big page
            p = Page(seq_id=seq_id, start=st.length, length=T, device=dev, k=k.contiguous(), v=v.contiguous())
            st.pages.append(p)
            st.length += T
            self._stat_pages += 1
            return

        # Page writes
        offset = 0
        while offset < T:
            cap = self._page_capacity(st, dev)
            take = min(cap, T - offset)
            kseg = k[offset:offset + take].contiguous()
            vseg = v[offset:offset + take].contiguous()
            p = Page(seq_id=seq_id, start=st.length, length=take, device=dev, k=kseg, v=vseg)
            st.pages.append(p)
            st.length += take
            self._stat_pages += 1
            offset += take

        # Opportunistic compress older pages if enabled
        if self.compress_kind == "Q8_0":
            self._maybe_compress_cold_pages(seq_id)

        # Evict if memory pressure (simple heuristic)
        self._maybe_evict(seq_id)

    def read_window(self, seq_id: int, start: int, end: int, device: Optional[torch.device] = None) -> Tuple[Tensor, Tensor]:
        """
        Read [start, end) tokens for a sequence and return (K,V) on target device.
        Cross-device transfers are handled transparently.
        """
        assert seq_id in self.tables, f"seq {seq_id} not found"
        st = self.tables[seq_id]
        assert 0 <= start <= end <= st.length, "invalid window bounds"
        dev = device or self.device

        # Gather segments
        k_parts: List[Tensor] = []
        v_parts: List[Tensor] = []

        remaining = (end - start)
        pos = start
        for p in st.pages:
            ps, pe = p.token_range()
            if pe <= pos or ps >= end:
                continue
            s = max(ps, pos)
            e = min(pe, end)
            seg_slice = slice(s - ps, e - ps)
            pk, pv = self._materialize_slice(p, seg_slice, dev)
            k_parts.append(pk)
            v_parts.append(pv)
            pos = e
            if pos >= end:
                break

        K = torch.cat(k_parts, dim=0) if len(k_parts) > 1 else k_parts[0]
        V = torch.cat(v_parts, dim=0) if len(v_parts) > 1 else v_parts[0]

        # Optional prefetch next page
        if PREFETCH:
            self._prefetch_next(st, end, dev)

        return K, V

    def evict(self, seq_id: int, up_to_step: int) -> int:
        """
        Evict fully-covered pages for tokens < up_to_step respecting hotshield.
        Returns the number of pages evicted.
        """
        assert seq_id in self.tables, f"seq {seq_id} not found"
        st = self.tables[seq_id]
        before = len(st.pages)
        kept: List[Page] = []
        for p in st.pages:
            ps, pe = p.token_range()
            if pe <= up_to_step and not p.is_hot(st.length):
                self._free_page(p)
                self._stat_pages -= 1
            else:
                kept.append(p)
        st.pages = kept
        return before - len(kept)

    def free(self, seq_id: int) -> None:
        """Free all pages of a sequence."""
        if seq_id not in self.tables:
            return
        st = self.tables.pop(seq_id)
        for p in st.pages:
            self._free_page(p)
        # No need to adjust _stat_pages: we don't track across sequences here

    def stats(self) -> Dict[str, Any]:
        """Return KV-level statistics for observability."""
        dev_pages = {}
        total_tokens = 0
        for sid, st in self.tables.items():
            total_tokens += st.length
            for p in st.pages:
                dev_pages.setdefault(str(p.device), 0)
                dev_pages[str(p.device)] += 1
        return {
            "num_sequences": len(self.tables),
            "total_tokens": total_tokens,
            "total_pages": sum(dev_pages.values()),
            "pages_by_device": dev_pages,
            "paged": self.paged,
            "spill": self.allow_spill,
            "compress": self.compress_kind,
        }

    # State dict for checkpointing (single node best effort)
    def state_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "cfg": {
                "page_tokens": self.page_tokens,
                "paged": self.paged,
                "allow_spill": self.allow_spill,
                "compress_kind": self.compress_kind,
                "evict_policy": self.evict_policy,
            },
            "seqs": {},
        }
        for sid, st in self.tables.items():
            seqd = {
                "kv_dim_k": st.kv_dim_k,
                "kv_dim_v": st.kv_dim_v,
                "length": st.length,
                "pages": [],
            }
            for p in st.pages:
                rec = {
                    "start": p.start,
                    "length": p.length,
                    "device": str(p.device),
                    "on_host": p.on_host,
                    "comp": p.comp,
                }
                # Persist payload on host to simplify
                k_cpu, v_cpu, k_scale, v_scale = self._page_to_host_payload(p)
                rec["k"] = k_cpu
                rec["v"] = v_cpu
                rec["k_scale"] = k_scale
                rec["v_scale"] = v_scale
                seqd["pages"].append(rec)
            out["seqs"][sid] = seqd
        return out

    def load_state_dict(self, state: Dict[str, Any], map_location: Optional[torch.device] = None) -> None:
        self.page_tokens = state["cfg"]["page_tokens"]
        self.paged = state["cfg"]["paged"]
        self.allow_spill = state["cfg"]["allow_spill"]
        self.compress_kind = state["cfg"]["compress_kind"]
        self.evict_policy = state["cfg"]["evict_policy"]
        self.tables.clear()

        for sid_str, seqd in state["seqs"].items():
            sid = int(sid_str)
            st = SeqTable(kv_dim_k=tuple(seqd["kv_dim_k"]), kv_dim_v=tuple(seqd["kv_dim_v"]), length=int(seqd["length"]), pages=[])
            for rec in seqd["pages"]:
                dev = map_location or self.device
                p = Page(seq_id=sid, start=int(rec["start"]), length=int(rec["length"]), device=dev)
                self._page_from_host_payload(p,
                                             rec["k"], rec["v"],
                                             rec.get("k_scale"), rec.get("v_scale"),
                                             comp=rec["comp"])
                st.pages.append(p)
            self.tables[sid] = st

    # ---------- Convenience aliases for PKV-like naming ----------

    def write_tokens(self, seq_id: int, k: Tensor, v: Tensor, device: Optional[torch.device] = None) -> None:
        """Alias of append()."""
        self.append(seq_id, k, v, device=device)

    def read_recent(self, seq_id: int, window_tokens: int, device: Optional[torch.device] = None) -> Tuple[Tensor, Tensor]:
        """Return the most recent window of tokens."""
        st = self.tables[seq_id]
        end = st.length
        start = max(0, end - window_tokens)
        return self.read_window(seq_id, start, end, device=device)

    # ---------- Internals ----------

    def _page_capacity(self, st: SeqTable, device: torch.device) -> int:
        return self.page_tokens

    def _maybe_compress_cold_pages(self, seq_id: int) -> None:
        st = self.tables[seq_id]
        # Compress pages that are far from the sequence end and currently on device.
        cold_cut = max(0, st.length - HOTSHIELD_TOK)
        for p in st.pages:
            if p.comp != "none":
                continue
            ps, pe = p.token_range()
            if pe <= cold_cut:
                # Move to host + compress if enabled
                if self.allow_spill:
                    self._spill_to_host(p, compress=(self.compress_kind == "Q8_0"))

    def _maybe_evict(self, seq_id: int) -> None:
        """
        Heuristic eviction hook (no global memory pressure signal yet):
        - When total device pages exceed a soft cap, evict coldest ones to host.
        """
        if not self.allow_spill:
            return
        # Soft cap: 4096 pages across all sequences on current process
        SOFT_CAP = 4096
        if self._stat_pages <= SOFT_CAP:
            return

        # Collect candidates
        cands: List[Tuple[float, Page, int]] = []  # (last_use_ts, page, seq_len)
        for sid, st in self.tables.items():
            for p in st.pages:
                if not p.on_host and not p.is_hot(st.length):
                    cands.append((p.last_use_ts, p, st.length))
        cands.sort(key=lambda x: x[0])  # oldest first

        evicted = 0
        for _, p, _len in cands:
            self._spill_to_host(p, compress=(self.compress_kind == "Q8_0"))
            evicted += 1
            if self._stat_pages - evicted <= SOFT_CAP:
                break

    # ---------- Page materialization / movement ----------

    def _materialize_slice(self, p: Page, seg: slice, target: torch.device) -> Tuple[Tensor, Tensor]:
        """
        Ensure that the requested slice of page p is materialized on target device
        and return (K,V) tensors with the slice applied.
        """
        # Fast path: already on correct device without compression
        if (not p.on_host) and p.comp == "none" and str(p.device) == str(target):
            p.touch()
            return p.k[seg], p.v[seg]

        # Need to ensure K/V exist on target device
        self._ensure_on_device(p, target)
        p.touch()
        return p.k[seg], p.v[seg]

    def _ensure_on_device(self, p: Page, target: torch.device) -> None:
        """
        Bring page payload to target device. Handles:
          - host -> device (decompress if needed)
          - device A -> device B (peer or host bounce)
        """
        if (not p.on_host) and str(p.device) == str(target) and p.comp == "none":
            return

        # 1) If on host (possibly compressed), reconstruct tensors on target
        if p.on_host:
            # Decode or copy from host
            if p.comp == "Q8_0":
                assert p.host_k is not None and p.k_scale is not None
                assert p.host_v is not None and p.v_scale is not None
                k = CompressionCodec.decode_q8_0(p.host_k, p.k_scale, dtype=torch.float16).to(target, non_blocking=True)
                v = CompressionCodec.decode_q8_0(p.host_v, p.v_scale, dtype=torch.float16).to(target, non_blocking=True)
            else:
                k = p.host_k.to(target, non_blocking=True) if p.host_k is not None else None
                v = p.host_v.to(target, non_blocking=True) if p.host_v is not None else None
            p.k = k.contiguous()
            p.v = v.contiguous()
            p.on_host = False
            p.comp = "none"
            p.device = target
            # Optionally free host copies to save RAM (keep metadata only)
            p.host_k = None
            p.host_v = None
            p.k_scale = None
            p.v_scale = None
            return

        # 2) Device A -> Device B movement
        if str(p.device) != str(target):
            # Try P2P first
            can_p2p = False
            try:
                if torch.cuda.is_available():
                    src_idx = p.device.index if p.device.index is not None else torch.cuda.current_device()
                    dst_idx = target.index if target.index is not None else torch.cuda.current_device()
                    can_p2p = torch.cuda.device_can_access_peer(dst_idx, src_idx)
            except Exception:
                can_p2p = False

            if can_p2p:
                # Simple .to(target) typically uses P2P when available
                p.k = p.k.to(target, non_blocking=True)
                p.v = p.v.to(target, non_blocking=True)
            else:
                if not REMOTE_READ:
                    raise RuntimeError("Remote KV read disabled (SKOTE_KV_REMOTE_READ=0)")
                # Bounce via host pinned
                k_host = p.k.to("cpu", non_blocking=True, pin_memory=True)
                v_host = p.v.to("cpu", non_blocking=True, pin_memory=True)
                p.k = k_host.to(target, non_blocking=True)
                p.v = v_host.to(target, non_blocking=True)
            p.device = target
            p.comp = "none"
            return

    def _spill_to_host(self, p: Page, compress: bool) -> None:
        """
        Move page payload from device to host pinned memory; optional Q8_0 compression.
        """
        if p.on_host:
            return
        if p.k is None or p.v is None:
            return

        if compress:
            qk, ks = CompressionCodec.encode_q8_0(p.k)
            qv, vs = CompressionCodec.encode_q8_0(p.v)
            p.host_k = qk.to("cpu", non_blocking=True, pin_memory=True)
            p.host_v = qv.to("cpu", non_blocking=True, pin_memory=True)
            p.k_scale = ks.cpu()
            p.v_scale = vs.cpu()
            p.comp = "Q8_0"
        else:
            p.host_k = p.k.to("cpu", non_blocking=True, pin_memory=True)
            p.host_v = p.v.to("cpu", non_blocking=True, pin_memory=True)
            p.comp = "none"
        # Release device payload
        p.k = None
        p.v = None
        p.on_host = True

    def _free_page(self, p: Page) -> None:
        """Release all tensors of a page."""
        p.k = None
        p.v = None
        p.host_k = None
        p.host_v = None
        p.k_scale = None
        p.v_scale = None

    def _prefetch_next(self, st: SeqTable, end_pos: int, target: torch.device) -> None:
        """
        Prefetch the page that starts at end_pos (if any).
        """
        for p in st.pages:
            if p.start == end_pos and (p.on_host or str(p.device) != str(target)):
                try:
                    self._ensure_on_device(p, target)
                except Exception:
                    # Prefetch is best-effort
                    pass
                break

    # ---------- Checkpoint helpers ----------

    def _page_to_host_payload(self, p: Page) -> Tuple[Tensor, Tensor, Optional[Tensor], Optional[Tensor]]:
        """
        Return host tensors for K/V and scales (if compressed), creating them if needed.
        """
        if p.on_host:
            return (
                p.host_k if p.host_k is not None else torch.empty(0, dtype=torch.int8),
                p.host_v if p.host_v is not None else torch.empty(0, dtype=torch.int8),
                p.k_scale,
                p.v_scale,
            )
        # Produce CPU copies
        if p.comp == "Q8_0":
            # Should not happen: device payload cannot be int8 here; create Q8_0 snapshot
            qk, ks = CompressionCodec.encode_q8_0(p.k)
            qv, vs = CompressionCodec.encode_q8_0(p.v)
            return qk.cpu(), qv.cpu(), ks.cpu(), vs.cpu()
        else:
            return p.k.cpu(), p.v.cpu(), None, None

    def _page_from_host_payload(self, p: Page,
                                k_host: Tensor, v_host: Tensor,
                                k_scale: Optional[Tensor], v_scale: Optional[Tensor],
                                comp: str = "none") -> None:
        """
        Materialize page from host payload into device memory (keeping host copies).
        """
        if comp == "Q8_0" and k_scale is not None and v_scale is not None:
            p.host_k = k_host.pin_memory()
            p.host_v = v_host.pin_memory()
            p.k_scale = k_scale
            p.v_scale = v_scale
            p.on_host = True
            p.comp = "Q8_0"
            p.k = None
            p.v = None
        else:
            p.k = k_host.to(self.device, non_blocking=True).contiguous()
            p.v = v_host.to(self.device, non_blocking=True).contiguous()
            p.on_host = False
            p.comp = "none"
        p.device = self.device


# ------------------------------ Factory ------------------------------

def create_kv_store() -> ShardableKV:
    """
    Factory that honors environment and current device. Intended to be called from
    your runtime init code (e.g., generate.py) with zero args.
    """
    dev = torch.device("cuda", torch.cuda.current_device()) if torch.cuda.is_available() else torch.device("cpu")
    return ShardableKV(device=dev,
                       page_tokens=PAGE_TOKENS,
                       paged=KV_PAGED,
                       allow_spill=ALLOW_SPILL,
                       compress_kind=COMPRESS_KIND,
                       evict_policy=EVICT_POLICY)


# ------------------------------ Debug CLI ------------------------------

if __name__ == "__main__":
    """
    Quick self-test:
      $ python -m skote.distributed.kv_store
    """
    torch.manual_seed(0)
    kv = create_kv_store()
    sid = 1
    T = 1536
    d_k = (32,)     # per-token K dim (example)
    d_v = (32,)

    kv.ensure_seq(sid, d_k, d_v)
    k = torch.randn(T, *d_k, dtype=torch.float16, device=kv.device)
    v = torch.randn(T, *d_v, dtype=torch.float16, device=kv.device)
    kv.append(sid, k, v)

    # Read two windows
    K1, V1 = kv.read_window(sid, 256, 512)
    print("window1:", K1.shape, V1.shape, "device", K1.device)

    K2, V2 = kv.read_recent(sid, 128)
    print("recent:", K2.shape, V2.shape, "device", K2.device)

    # Evict older pages
    ev = kv.evict(sid, up_to_step=512)
    print("evicted pages:", ev)
    print("stats:", json.dumps(kv.stats(), indent=2, default=str))
