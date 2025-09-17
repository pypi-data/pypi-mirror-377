# skote/runtime/upm.py
"""
Unified Paging Memory (UPM) for Skotergy

What this module provides (revamped):
- Device-agnostic page pools with optional CUDA-backed buffers (1 tensor/page).
- Four logical regions: KV, APC(prefix cache), LoRA, and TMP(scratch).
- Borrow/Return API with contiguous page leases for graph-capture stability.
- Pre-warm capacity via env flags to eliminate first-hit allocations.
- Unified or split pools depending on page-size compatibility.
- Rich metrics: free/used/owned pages, payload utilization, fragmentation,
  peak watermarks, borrowed pages and active leases.
- Safe to import and run without CUDA/ROCm (host placeholders).

Why this matters:
- CUDA Graph capture requires stable addresses and zero allocations during
  the capture window. The new contiguous lease mechanism lets GraphManager
  reserve fixed pages up front and replay by copying into those pages,
  removing allocator churn from the hot path (reduces p95 tail).
"""

from __future__ import annotations

import os
import math
import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Literal

from skote import SkoteConfig, get_config, get_logger

log = get_logger("skotergy.upm")

Region = Literal["kv", "apc", "lora", "tmp"]


# --------------------------- Device Arena (pluggable) ---------------------------

class DeviceArena:
    """
    Minimal device arena:
    - device='cuda' → allocate real GPU buffers via torch (1 tensor per page, uint8 of size page_bytes)
    - device='host' → placeholders only (no GPU requirement)
    Exposes .stats() for memory watermarks when CUDA is present.
    """

    def __init__(self, device: str = "host") -> None:
        self.device = device
        self._buffers: List[Any] = []  # keep refs for pages reserved by _ensure_capacity

    def allocate_pages(self, page_bytes: int, n_pages: int) -> Any:
        if self.device == "cuda":
            try:
                import torch  # local import to avoid hard dependency
                for _ in range(int(n_pages)):
                    buf = torch.empty(int(page_bytes), dtype=torch.uint8, device="cuda")
                    self._buffers.append(buf)
                return {"device": "cuda", "page_bytes": int(page_bytes), "n_pages": int(n_pages)}
            except Exception as e:
                log.warning("[UPM] CUDA allocate_pages failed: %s; falling back to host placeholders", e)
        # host or fallback
        return {"device": self.device, "page_bytes": int(page_bytes), "n_pages": int(n_pages)}

    def free_pages(self, handle: Any) -> None:
        # We intentionally retain capacity; pools recycle pages to the free list.
        return

    def stats(self) -> Dict[str, Any]:
        try:
            import torch
            if self.device == "cuda" and torch.cuda.is_available():
                return {
                    "device": "cuda",
                    "memory_allocated": int(torch.cuda.memory_allocated()),
                    "max_memory_allocated": int(torch.cuda.max_memory_allocated()),
                    "memory_reserved": int(torch.cuda.memory_reserved()),
                }
        except Exception:
            pass
        return {"device": self.device}


# --------------------------- Core data structures ---------------------------

@dataclass
class PageSpan:
    start: int
    count: int


@dataclass
class Allocation:
    alloc_id: str
    region: Region
    pages: List[int]
    page_size_elems: int
    payload_elems: int
    created_at: float = field(default_factory=time.time)


@dataclass
class BorrowLease:
    lease_id: str
    region: Region
    pages: List[int]            # contiguous by construction
    page_size_elems: int
    elem_bytes: int
    purpose: str = "graph-capture"
    created_at: float = field(default_factory=time.time)


class PagePool:
    """
    Single page pool with fixed page size (in elements).
    - Bookkeeping only; thread-safe; can grow on demand.
    - Supports regular allocations and contiguous "borrow leases".
    """

    def __init__(
        self,
        name: str,
        page_size_elems: int,
        arena: Optional[DeviceArena] = None,
        soft_limit_pages: int = 1_000_000,
        elem_bytes: Optional[int] = None,
    ) -> None:
        assert page_size_elems > 0
        self.name = name
        self.page_size_elems = int(page_size_elems)
        self._lock = threading.Lock()

        self._free: List[int] = []         # free page ids
        self._owned: int = 0               # total pages ever created/owned
        self._in_use: Dict[int, str] = {}  # page_id -> alloc_id (regular allocations)
        self._allocs: Dict[str, Allocation] = {}
        self._payload_elems: int = 0       # sum of requested elems (for utilization)
        self._peak_in_use_pages: int = 0
        self._soft_limit = int(soft_limit_pages)

        # Borrow/lease tracking
        self._leases: Dict[str, BorrowLease] = {}   # lease_id -> BorrowLease
        self._borrowed_pages: Dict[int, str] = {}   # page_id -> lease_id

        # bytes per element (for backing buffer sizes); env override SKOTE_UPM_ELEM_BYTES
        self._elem_bytes = int(elem_bytes or int(os.environ.get("SKOTE_UPM_ELEM_BYTES", "2")))
        self._arena = arena or DeviceArena("host")

    # --- metrics ---

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            used_pages = len(self._in_use)
            total_pages = self._owned
            free_pages = len(self._free)
            borrowed_pages = len(self._borrowed_pages)
            payload = self._payload_elems
            capacity_elems = used_pages * self.page_size_elems
            util = (payload / capacity_elems) if capacity_elems else 0.0
            frag = 1.0 - util if capacity_elems else 0.0
            dev = self._arena.stats() if hasattr(self._arena, "stats") else {}
            return {
                "pool": self.name,
                "page_size_elems": self.page_size_elems,
                "elem_bytes": self._elem_bytes,
                "owned_pages": total_pages,
                "used_pages": used_pages,
                "free_pages": free_pages,
                "borrowed_pages": borrowed_pages,
                "payload_elems": payload,
                "payload_utilization": util,  # 0..1
                "fragmentation": frag,        # 0..1 (internal, from page rounding)
                "peak_used_pages": self._peak_in_use_pages,
                "device": dev,
                "leases": [{"lease_id": lid, "pages": len(lease.pages), "purpose": lease.purpose} for lid, lease in self._leases.items()],
            }

    # --- capacity / growth ---

    def _ensure_capacity(self, need_pages: int) -> None:
        grow = max(0, need_pages - len(self._free))
        if grow <= 0:
            return
        new_total = self._owned + grow
        if new_total > self._soft_limit:
            raise RuntimeError(f"[UPM] pool '{self.name}' exceeds soft page limit ({self._soft_limit})")
        base = self._owned
        self._owned = new_total
        self._free.extend(range(base, base + grow))
        self._arena.allocate_pages(page_bytes=self.page_size_elems * self._elem_bytes, n_pages=grow)

    def preallocate_pages(self, n_pages: int) -> int:
        """Ensure at least n_pages are available in the free list (idempotent)."""
        if n_pages <= 0:
            return len(self._free)
        with self._lock:
            target_free = max(n_pages, len(self._free))
            self._ensure_capacity(target_free)
            return len(self._free)

    # --- regular allocation ---

    def allocate(self, region: Region, elems: int, alloc_id: Optional[str] = None) -> Allocation:
        if elems <= 0:
            raise ValueError("payload elems must be > 0")
        pages_needed = math.ceil(elems / self.page_size_elems)
        with self._lock:
            self._ensure_capacity(pages_needed)
            pages: List[int] = []
            while len(pages) < pages_needed:
                pid = self._free.pop()
                # Safety: never hand out pages that are borrowed by leases
                if pid in self._borrowed_pages:
                    # Very unlikely if bookkeeping is correct; skip borrowed page
                    continue
                pages.append(pid)
            aid = alloc_id or f"{region}-{pages[0]}-{int(time.time()*1e6)}"
            alloc = Allocation(
                alloc_id=aid,
                region=region,
                pages=pages,
                page_size_elems=self.page_size_elems,
                payload_elems=elems,
            )
            for pid in pages:
                self._in_use[pid] = aid
            self._allocs[aid] = alloc
            self._payload_elems += elems
            self._peak_in_use_pages = max(self._peak_in_use_pages, len(self._in_use))
            return alloc

    def free(self, alloc_id: str) -> bool:
        with self._lock:
            alloc = self._allocs.pop(alloc_id, None)
            if not alloc:
                return False
            for pid in alloc.pages:
                self._in_use.pop(pid, None)
                self._free.append(pid)
            self._payload_elems -= alloc.payload_elems
            return True

    # --- borrow/return contiguous leases (for graph capture) ---

    def _find_contiguous_in_free(self, n_pages: int) -> Optional[List[int]]:
        """Try to find a contiguous span of n_pages within the current free list."""
        if n_pages <= 0:
            return []
        if n_pages == 1 and self._free:
            return [self._free[-1]]
        # sort a copy to scan runs; free list can be unordered due to frees
        f = sorted(self._free)
        run = [f[0]] if f else []
        for prev, cur in zip(f, f[1:]):
            if cur == prev + 1:
                if not run:
                    run = [prev]
                run.append(cur)
                if len(run) >= n_pages:
                    return run[-n_pages:]
            else:
                run = [cur]
        return None

    def borrow_contiguous(self, region: Region, n_pages: int, *, purpose: str = "graph-capture") -> BorrowLease:
        """
        Reserve a contiguous span of pages for a non-owning lease. The pages are
        removed from the free list and marked as borrowed (not visible to regular
        alloc/free). Call return_lease() to release them.
        """
        if n_pages <= 0:
            raise ValueError("n_pages must be > 0")
        with self._lock:
            # First try to locate an existing contiguous run in free pages
            span = self._find_contiguous_in_free(n_pages)
            if span is None:
                # Force growth by exactly n_pages so the newly created ids are contiguous
                need = len(self._free) + n_pages
                self._ensure_capacity(need)
                # Newly appended pages are [self._owned - n_pages, ..., self._owned - 1]
                span = list(range(self._owned - n_pages, self._owned))
            # Remove selected pages from free list
            free_set = set(self._free)
            for pid in span:
                if pid not in free_set:
                    # Should not happen; fallback: rebuild free_set and continue
                    pass
            # Purge span pids from _free (keep order stable)
            span_set = set(span)
            self._free = [pid for pid in self._free if pid not in span_set]

            lease_id = f"lease-{self.name}-{uuid.uuid4().hex[:12]}"
            lease = BorrowLease(
                lease_id=lease_id,
                region=region,
                pages=span,
                page_size_elems=self.page_size_elems,
                elem_bytes=self._elem_bytes,
                purpose=purpose,
            )
            self._leases[lease_id] = lease
            for pid in span:
                self._borrowed_pages[pid] = lease_id
            return lease

    def return_lease(self, lease_id: str) -> bool:
        """Release a previously borrowed contiguous span back to the free list."""
        with self._lock:
            lease = self._leases.pop(lease_id, None)
            if lease is None:
                return False
            for pid in lease.pages:
                self._borrowed_pages.pop(pid, None)
                self._free.append(pid)
            return True

    # --- compaction planning (bookkeeping only) ---

    def plan_compaction(self) -> Dict[str, Any]:
        """
        Return a compaction plan suggestion to reduce internal fragmentation.
        This is a pure accounting plan; execution will be backend-specific.
        """
        with self._lock:
            if not self._allocs:
                return {"moves": [], "expected_frag_after": 0.0}
            allocs = sorted(self._allocs.values(), key=lambda a: -a.payload_elems)
            page_capacity = self.page_size_elems
            pages_needed_exact = sum(a.payload_elems for a in allocs) / page_capacity
            pages_floor = math.ceil(pages_needed_exact)
            ideal_capacity = pages_floor * page_capacity
            payload = sum(a.payload_elems for a in allocs)
            frag_after = 1.0 - (payload / ideal_capacity if ideal_capacity else 1.0)
            cur = 0
            moves: List[Tuple[str, PageSpan]] = []
            for a in allocs:
                need = math.ceil(a.payload_elems / page_capacity)
                moves.append((a.alloc_id, PageSpan(start=cur, count=need)))
                cur += need
            return {"moves": moves, "expected_frag_after": frag_after}

    # --- visibility helpers ---

    def list_allocs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "alloc_id": a.alloc_id,
                    "region": a.region,
                    "pages": list(a.pages),
                    "payload_elems": a.payload_elems,
                }
                for a in self._allocs.values()
            ]

    def list_leases(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {"lease_id": l.lease_id, "region": l.region, "pages": list(l.pages), "purpose": l.purpose}
                for l in self._leases.values()
            ]


# --------------------------- Unified Paging Memory ---------------------------

class UnifiedPagingMemory:
    """
    Front-door for UPM:
    - Prefer one unified pool if page sizes for KV/APC/LoRA/TMP match.
    - Else create subpools per region (still reported as one system).
    - Provide convenience allocators and contiguous borrow/return leases.
    - Optional pre-warm via env to avoid first-use allocations in hot paths.
    """

    def __init__(self, cfg: Optional[SkoteConfig] = None) -> None:
        self.cfg = cfg or get_config()

        ps_kv = int(getattr(self.cfg, "page_size_kv", 16384))
        ps_apc = int(getattr(self.cfg, "page_size_apc", ps_kv))
        ps_lora = int(getattr(self.cfg, "page_size_lora", ps_kv))
        ps_tmp_val = getattr(self.cfg, "page_size_tmp", None)
        ps_tmp = int(ps_tmp_val) if ps_tmp_val is not None else int(ps_kv)

        self.unified = (ps_kv == ps_apc == ps_lora == ps_tmp)
        soft_limit = int(self._env("SKOTE_UPM_SOFT_LIMIT_PAGES", "200000"))
        elem_bytes = int(self._env("SKOTE_UPM_ELEM_BYTES", "2"))

        arena = self._choose_arena()

        if self.unified:
            self._pool = PagePool("unified", page_size_elems=ps_kv, soft_limit_pages=soft_limit, elem_bytes=elem_bytes, arena=arena)
            self._kv = self._pool
            self._apc = self._pool
            self._lora = self._pool
            self._tmp = self._pool
            log.info("UPM initialized: unified pool (page=%d elems, elem_bytes=%d, device=%s)", ps_kv, elem_bytes, arena.device)
        else:
            self._pool = None
            self._kv   = PagePool("kv",   page_size_elems=ps_kv,   soft_limit_pages=soft_limit, elem_bytes=elem_bytes, arena=arena)
            self._apc  = PagePool("apc",  page_size_elems=ps_apc,  soft_limit_pages=soft_limit, elem_bytes=elem_bytes, arena=arena)
            self._lora = PagePool("lora", page_size_elems=ps_lora, soft_limit_pages=soft_limit, elem_bytes=elem_bytes, arena=arena)
            self._tmp  = PagePool("tmp",  page_size_elems=ps_tmp,  soft_limit_pages=soft_limit, elem_bytes=elem_bytes, arena=arena)
            log.info(
                "UPM initialized: split pools (kv=%d, apc=%d, lora=%d, tmp=%d elems/page, elem_bytes=%d, device=%s)",
                ps_kv, ps_apc, ps_lora, ps_tmp, elem_bytes, arena.device
            )

        # Optional pre-warm to remove first-hit allocations during capture
        self._maybe_prewarm()

    # ------------------------ Arena selection ------------------------

    def _choose_arena(self) -> DeviceArena:
        """
        Decide device arena for UPM:
        - SKOTE_UPM_DEVICE=host|cuda|auto (default: auto)
        - auto → cuda if torch.cuda.is_available(), else host
        """
        want = self._env("SKOTE_UPM_DEVICE", "auto").lower()
        if want == "host":
            return DeviceArena("host")
        if want in ("cuda", "auto"):
            try:
                import torch
                if torch.cuda.is_available():
                    return DeviceArena("cuda")
            except Exception:
                pass
        return DeviceArena("host")

    # ------------------------ Pre-warm ------------------------

    def _maybe_prewarm(self) -> None:
        """
        If SKOTE_UPM_PREWARM=1, preallocate pages per region:
        - SKOTE_UPM_PREALLOC_KV_PAGES
        - SKOTE_UPM_PREALLOC_APC_PAGES
        - SKOTE_UPM_PREALLOC_LORA_PAGES
        - SKOTE_UPM_PREALLOC_TMP_PAGES
        """
        if self._env("SKOTE_UPM_PREWARM", "0") != "1":
            return
        try:
            kv = int(self._env("SKOTE_UPM_PREALLOC_KV_PAGES", "0"))
            apc = int(self._env("SKOTE_UPM_PREALLOC_APC_PAGES", "0"))
            lora = int(self._env("SKOTE_UPM_PREALLOC_LORA_PAGES", "0"))
            tmp = int(self._env("SKOTE_UPM_PREALLOC_TMP_PAGES", "0"))

            if kv > 0:
                self._kv.preallocate_pages(kv)
            if apc > 0:
                self._apc.preallocate_pages(apc)
            if lora > 0:
                self._lora.preallocate_pages(lora)
            if tmp > 0:
                self._tmp.preallocate_pages(tmp)

            log.info("UPM prewarmed (kv=%d, apc=%d, lora=%d, tmp=%d pages).", kv, apc, lora, tmp)
        except Exception as e:
            log.warning("UPM prewarm failed: %s", e)

    # ------------------------ Convenience allocators ------------------------

    @staticmethod
    def _elem_size(dtype: str = "fp16") -> int:
        return {
            "fp8": 1,
            "fp16": 2,
            "bf16": 2,
            "fp32": 4,
            "int8": 1,
        }.get(dtype.lower(), 2)

    def allocate_kv(
        self,
        num_heads: int,
        head_dim: int,
        seq_len: int,
        *,
        dtype: str = "fp16",
        factor_kv: int = 2,
        alloc_id: Optional[str] = None,
    ) -> Allocation:
        """
        KV cache: K and V (factor=2 by default)
        elems = num_heads * head_dim * seq_len * factor
        """
        elems = int(num_heads) * int(head_dim) * int(seq_len) * int(factor_kv)
        return self._kv.allocate("kv", elems, alloc_id=alloc_id)

    def allocate_apc(
        self,
        tokens: int,
        hidden_size: int,
        *,
        dtype: str = "fp16",
        alloc_id: Optional[str] = None,
    ) -> Allocation:
        """
        APC (prefix cache) for prefill reuse:
        elems = tokens * hidden_size
        """
        elems = int(tokens) * int(hidden_size)
        return self._apc.allocate("apc", elems, alloc_id=alloc_id)

    def allocate_lora(
        self,
        hidden_size: int,
        rank: int,
        *,
        n_mats: int = 2,
        dtype: str = "fp16",
        alloc_id: Optional[str] = None,
    ) -> Allocation:
        """
        LoRA adapters (A,B) per target module by default (n_mats=2):
        elems = hidden_size * rank * n_mats
        """
        elems = int(hidden_size) * int(rank) * int(n_mats)
        return self._lora.allocate("lora", elems, alloc_id=alloc_id)

    def allocate_tmp(
        self,
        elems: int,
        *,
        dtype: str = "fp16",
        alloc_id: Optional[str] = None,
    ) -> Allocation:
        """
        TMP scratch buffers (generic temporaries)
        elems = arbitrary count of elements required by caller
        """
        return self._tmp.allocate("tmp", int(elems), alloc_id=alloc_id)

    # ------------------------ Borrow/Return (contiguous leases) ------------------------

    def borrow_contiguous(self, region: Region, n_pages: int, *, purpose: str = "graph-capture") -> BorrowLease:
        """
        Reserve a contiguous span of pages for a non-owning lease in the given region.
        The pages are removed from the region's free list and returned via BorrowLease.
        """
        return self._select_pool(region).borrow_contiguous(region, int(n_pages), purpose=purpose)

    def return_lease(self, lease_id: str, region_hint: Optional[Region] = None) -> bool:
        """
        Release a lease back to the appropriate region. If region_hint is not provided,
        we try all pools (safe but a bit slower).
        """
        if region_hint:
            return self._select_pool(region_hint).return_lease(lease_id)
        ok = False
        for pool in self._iter_pools():
            ok = pool.return_lease(lease_id) or ok
        return ok

    # Convenience: compute pages from elements, then borrow a contiguous lease.
    def reserve_kv_pages_for_capture(
        self, num_heads: int, head_dim: int, seq_len: int, *, factor_kv: int = 2
    ) -> BorrowLease:
        elems = int(num_heads) * int(head_dim) * int(seq_len) * int(factor_kv)
        n_pages = math.ceil(elems / self._kv.page_size_elems)
        return self._kv.borrow_contiguous("kv", n_pages, purpose="graph-capture")

    def reserve_tmp_pages_for_capture(self, elems: int) -> BorrowLease:
        n_pages = math.ceil(int(elems) / self._tmp.page_size_elems)
        return self._tmp.borrow_contiguous("tmp", n_pages, purpose="graph-capture")

    # ------------------------ Generic API ------------------------

    def allocate(self, region: Region, elems: int, alloc_id: Optional[str] = None) -> Allocation:
        pool = self._select_pool(region)
        return pool.allocate(region, int(elems), alloc_id=alloc_id)

    def free(self, alloc_id: str, region_hint: Optional[Region] = None) -> bool:
        """
        Free by alloc_id; if region_hint unknown, try all pools.
        """
        if region_hint:
            return self._select_pool(region_hint).free(alloc_id)
        ok = False
        for pool in self._iter_pools():
            ok = pool.free(alloc_id) or ok
        return ok

    # ------------------------ Introspection / Metrics ------------------------

    def stats(self) -> Dict[str, Any]:
        pools = [p.stats() for p in self._iter_pools()]
        owned = sum(p["owned_pages"] for p in pools)
        used = sum(p["used_pages"] for p in pools)
        borrowed = sum(p["borrowed_pages"] for p in pools)
        payload = sum(p["payload_elems"] for p in pools)
        capacity_elems = sum(p["used_pages"] * p["page_size_elems"] for p in pools)
        util = (payload / capacity_elems) if capacity_elems else 0.0
        frag = 1.0 - util if capacity_elems else 0.0
        return {
            "unified": self.unified,
            "pools": pools,
            "global": {
                "owned_pages": owned,
                "used_pages": used,
                "borrowed_pages": borrowed,
                "payload_elems": payload,
                "payload_utilization": util,
                "fragmentation": frag,
            },
        }

    def plan_compaction(self) -> Dict[str, Any]:
        """
        Return a merged compaction plan across pools.
        """
        plan = {"unified": self.unified, "pools": {}, "global_expected_frag_after": None}
        frags_after = []
        for name, pool in self._named_pools():
            p = pool.plan_compaction()
            plan["pools"][name] = p
            frags_after.append(p.get("expected_frag_after", 0.0))
        if frags_after:
            plan["global_expected_frag_after"] = sum(frags_after) / len(frags_after)
        return plan

    def list_allocs(self) -> Dict[str, List[Dict[str, Any]]]:
        return {name: pool.list_allocs() for name, pool in self._named_pools()}

    def list_leases(self) -> Dict[str, List[Dict[str, Any]]]:
        return {name: pool.list_leases() for name, pool in self._named_pools()}

    # ------------------------ Helpers ------------------------

    def _select_pool(self, region: Region) -> PagePool:
        if region == "kv":
            return self._kv
        if region == "apc":
            return self._apc
        if region == "lora":
            return self._lora
        if region == "tmp":
            return self._tmp
        raise ValueError(f"unknown region: {region}")

    def _iter_pools(self) -> List[PagePool]:
        if self.unified and self._pool is not None:
            return [self._pool]
        return [self._kv, self._apc, self._lora, self._tmp]

    def _named_pools(self) -> List[Tuple[str, PagePool]]:
        if self.unified and self._pool is not None:
            return [("unified", self._pool)]
        return [("kv", self._kv), ("apc", self._apc), ("lora", self._lora), ("tmp", self._tmp)]

    @staticmethod
    def _env(key: str, default: str) -> str:
        return os.environ.get(key, default)
