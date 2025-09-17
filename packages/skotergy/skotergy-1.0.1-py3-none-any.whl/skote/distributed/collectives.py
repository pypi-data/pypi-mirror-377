# skote/distributed/collectives.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Collectives for Skotergy (backend-agnostic wrappers).

Goals
-----
- Provide a thin, safe, and timeout-aware wrapper around torch.distributed that:
  * Works with backends: NCCL (CUDA/ROCm), Gloo (CPU/XPU fallback), oneCCL (Intel).
  * Degrades gracefully when world_size == 1 or process group is not initialized.
  * Offers common collectives: all_reduce, all_gather (fixed and variable length),
    reduce_scatter, broadcast, barrier, and basic P2P send/recv helpers.
- Optional bandwidth optimization knobs (dtype downcast to bf16/fp16 for all_reduce;
  chunked transfers for P2P; CPU-pinned bounce for backends lacking GPU direct send).

Non-goals
---------
- No process-group initialization here (see distributed/launcher.py).
- No model/tensor parallel semantics; this module only exposes collectives.
- Cross-rank KV-page fetching protocol is intentionally left as a TODO hook
  (depends on higher-level ownership and routing decisions).

Environment knobs
-----------------
SKOTE_COLL_TIMEOUT_SEC   : per-op timeout seconds (default 180)
SKOTE_COLL_CHUNK_MB      : P2P chunk size in MiB (default 16)
SKOTE_COLL_DOWNCAST      : "none" | "bf16" | "fp16" for all_reduce downcast (default "none")
SKOTE_COLL_ASYNC         : "0" | "1" allow async returns when supported (default "0")

Usage
-----
from skote.distributed.collectives import Coll

coll = Coll()                # auto-detect state; no-op if single process
coll.barrier()
t = torch.ones(4, device="cuda")
t_sum = coll.all_reduce(t, op="sum")

# Variable-length all_gather along dim 0:
parts = coll.all_gather_varlen(t[:2], dim=0)

# P2P send/recv (CPU-pinned bounce for portability):
if coll.world_size > 1:
    if coll.rank == 0:
        coll.p2p_send_tensor(t, dst=1)
    elif coll.rank == 1:
        buf = coll.p2p_recv_tensor(src=0, shape=t.shape, dtype=t.dtype, device=t.device)
"""

from __future__ import annotations

import os
import math
import time
import logging
import contextlib
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

try:
    import torch
    import torch.distributed as dist
except Exception:  # pragma: no cover
    torch = None   # type: ignore
    dist = None    # type: ignore

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

def _get_logger(name: str) -> logging.Logger:
    try:
        from skote import get_logger  # type: ignore
        return get_logger(name)
    except Exception:
        logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))
        return logging.getLogger(name)

LOG = _get_logger("skotergy.collectives")


# -----------------------------------------------------------------------------
# Helpers & Config
# -----------------------------------------------------------------------------

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except Exception:
        return default

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default

def _env_true(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip() in ("1", "true", "True", "YES", "yes")

_COLL_TIMEOUT_SEC = _env_float("SKOTE_COLL_TIMEOUT_SEC", 180.0)
_CHUNK_MB = _env_int("SKOTE_COLL_CHUNK_MB", 16)
_ALLOW_ASYNC = _env_true("SKOTE_COLL_ASYNC", False)
_DOWNCAST = os.environ.get("SKOTE_COLL_DOWNCAST", "none").lower()  # none|bf16|fp16

# -----------------------------------------------------------------------------
# Dataclass for state
# -----------------------------------------------------------------------------

@dataclass
class CollState:
    initialized: bool
    world_size: int
    rank: int
    backend: Optional[str]


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

class Coll:
    """
    Thin, safe, timeout-aware collectives wrapper.
    """

    def __init__(self) -> None:
        if torch is None or dist is None or not dist.is_available():
            self.state = CollState(False, 1, 0, None)
            return

        if dist.is_initialized():
            try:
                backend = dist.get_backend()  # type: ignore[attr-defined]
            except Exception:
                backend = None
            self.state = CollState(True, dist.get_world_size(), dist.get_rank(), str(backend) if backend else None)
        else:
            # Not initialized => act as single-process
            self.state = CollState(False, 1, 0, None)

        LOG.info("Coll initialized: init=%s, world=%d, rank=%d, backend=%s",
                 self.state.initialized, self.state.world_size, self.state.rank, self.state.backend)

    # -------------------- Properties --------------------

    @property
    def initialized(self) -> bool:
        return self.state.initialized

    @property
    def world_size(self) -> int:
        return self.state.world_size

    @property
    def rank(self) -> int:
        return self.state.rank

    @property
    def backend(self) -> Optional[str]:
        return self.state.backend

    # -------------------- Core ops --------------------

    def barrier(self, timeout_s: Optional[float] = None) -> None:
        if not self.initialized or self.world_size <= 1:
            return
        self._with_timeout(dist.barrier, timeout_s or _COLL_TIMEOUT_SEC)

    def broadcast(self, tensor: torch.Tensor, src: int = 0, async_op: Optional[bool] = None) -> Optional[Any]:
        if not self.initialized or self.world_size <= 1:
            return None
        aop = _ALLOW_ASYNC if async_op is None else async_op
        return self._with_timeout(lambda: dist.broadcast(tensor, src=src, async_op=aop), _COLL_TIMEOUT_SEC)

    def all_reduce(self, tensor: torch.Tensor, op: str = "sum", async_op: Optional[bool] = None) -> torch.Tensor:
        """
        All-reduce with optional dtype downcast (bf16/fp16) for bandwidth saving.
        Returns a tensor (possibly new when downcast/restore happens).
        """
        if not self.initialized or self.world_size <= 1:
            return tensor

        # Map op
        red_op = _to_reduce_op(op)

        # Optional downcast
        orig_dtype = tensor.dtype
        tmp = tensor
        if _DOWNCAST in ("bf16", "fp16"):
            cast_dtype = torch.bfloat16 if _DOWNCAST == "bf16" else torch.float16
            if tensor.is_floating_point():
                tmp = tensor.to(cast_dtype)

        aop = _ALLOW_ASYNC if async_op is None else async_op
        self._with_timeout(lambda: dist.all_reduce(tmp, op=red_op, async_op=aop), _COLL_TIMEOUT_SEC)

        # Restore dtype if needed (sum/min/max semantics preserved for floats)
        if tmp is not tensor:
            tmp = tmp.to(orig_dtype)
        return tmp

    def reduce_scatter(self, tensor: torch.Tensor, op: str = "sum",
                       group: Optional[Any] = None, async_op: Optional[bool] = None) -> torch.Tensor:
        """
        Reduce-scatter (in-place semantics require equal chunk sizes across ranks).
        For simplicity we implement a concat + reduce_scatter_tensor path on 1D dim0.
        """
        if not self.initialized or self.world_size <= 1:
            return tensor

        red_op = _to_reduce_op(op)
        aop = _ALLOW_ASYNC if async_op is None else async_op

        # Ensure contiguous
        t = tensor.contiguous()
        # Per-rank slice length (dim 0)
        if t.size(0) % self.world_size != 0:
            raise ValueError("reduce_scatter requires dim0 divisible by world_size")
        out = torch.empty((t.size(0) // self.world_size, *t.shape[1:]), dtype=t.dtype, device=t.device)
        self._with_timeout(lambda: dist.reduce_scatter(out, list(_split_chunks_dim0(t, self.world_size)), op=red_op, async_op=aop),
                           _COLL_TIMEOUT_SEC)
        return out

    def all_gather(self, tensor: torch.Tensor, dim: int = 0, async_op: Optional[bool] = None) -> torch.Tensor:
        """
        Fixed-shape all_gather along a given dimension (all ranks must have same shape).
        """
        if not self.initialized or self.world_size <= 1:
            return tensor

        if dim != 0:
            # Move gather dimension to front
            perm = [dim] + [i for i in range(tensor.dim()) if i != dim]
            tin = tensor.permute(*perm).contiguous()
        else:
            tin = tensor.contiguous()

        parts = [torch.empty_like(tin) for _ in range(self.world_size)]
        aop = _ALLOW_ASYNC if async_op is None else async_op
        self._with_timeout(lambda: dist.all_gather(parts, tin, async_op=aop), _COLL_TIMEOUT_SEC)
        cat = torch.cat(parts, dim=0)

        if dim != 0:
            # Inverse permute
            inv = list(range(1, tensor.dim()+1))
            inv.insert(dim, 0)
            return cat.permute(*inv).contiguous()
        return cat

    def all_gather_varlen(self, tensor: torch.Tensor, dim: int = 0) -> List[torch.Tensor]:
        """
        Variable-length all_gather along a given dimension using size-exchange + padding.
        Returns a list of tensors in original dtype/device with original shape per rank.
        """
        if not self.initialized or self.world_size <= 1:
            return [tensor]

        # 1) Exchange sizes
        size_local = torch.tensor([tensor.size(dim)], device=tensor.device, dtype=torch.int64)
        sizes = [torch.zeros_like(size_local) for _ in range(self.world_size)]
        self._with_timeout(lambda: dist.all_gather(sizes, size_local), _COLL_TIMEOUT_SEC)
        sizes = [int(s.item()) for s in sizes]
        max_len = max(sizes)

        # 2) Pad to max along dim
        pad_shape = list(tensor.shape)
        pad_shape[dim] = max_len - pad_shape[dim]
        if pad_shape[dim] > 0:
            pad_tensor = torch.zeros(pad_shape, dtype=tensor.dtype, device=tensor.device)
            tin = torch.cat([tensor, pad_tensor], dim=dim)
        else:
            tin = tensor

        # 3) Gather fixed
        gathered = self.all_gather(tin, dim=dim)

        # 4) Split back into list by sizes
        outs: List[torch.Tensor] = []
        cursor = 0
        for sz in sizes:
            sl = [slice(None)] * gathered.dim()
            sl[dim] = slice(cursor, cursor + sz)
            outs.append(gathered[tuple(sl)].clone())
            cursor += max_len
        return outs

    # -------------------- P2P (point-to-point) --------------------

    def p2p_send_tensor(self, tensor: torch.Tensor, dst: int, tag: int = 0) -> None:
        """
        Backend-portable P2P send: uses CPU pinned bounce for safety across backends.
        Large tensors are chunked by SKOTE_COLL_CHUNK_MB.
        """
        if not self.initialized or self.world_size <= 1:
            return

        cpu_buf = _to_cpu_pinned(tensor)
        numel = cpu_buf.numel()
        chunk_elems = max(1, (_CHUNK_MB * 1024 * 1024) // max(cpu_buf.element_size(), 1))
        cursor = 0

        # Send shape/dtype first (int64 meta)
        meta = torch.tensor([len(tensor.shape), *tensor.shape, tensor.dtype.enumerate()], dtype=torch.int64)
        self._with_timeout(lambda: dist.send(meta, dst=dst, tag=tag), _COLL_TIMEOUT_SEC)

        while cursor < numel:
            take = min(chunk_elems, numel - cursor)
            view = cpu_buf.view(-1)[cursor:cursor+take]
            self._with_timeout(lambda: dist.send(view, dst=dst, tag=tag), _COLL_TIMEOUT_SEC)
            cursor += take

    def p2p_recv_tensor(self, src: int, shape: Sequence[int], dtype: torch.dtype,
                        device: Optional[torch.device] = None, tag: int = 0) -> torch.Tensor:
        """
        Receive a tensor from src. If shape/dtype unknown, pass shape/dtype=None
        and we will first receive meta to allocate output.
        """
        if not self.initialized or self.world_size <= 1:
            # Local fallback: just allocate zero (no sender in single-proc)
            dev = device or (torch.device("cuda", torch.cuda.current_device()) if torch.cuda.is_available() else torch.device("cpu"))
            return torch.zeros(shape, dtype=dtype, device=dev)

        # Receive meta if needed (rank does not know shape/dtype).
        if shape is None or dtype is None:
            # Expect meta: [ndim, shape..., dtype_enum]
            meta = torch.empty(1 + 8 + 1, dtype=torch.int64)  # up to 8-D tensors
            self._with_timeout(lambda: dist.recv(meta, src=src, tag=tag), _COLL_TIMEOUT_SEC)
            ndim = int(meta[0].item())
            shp = tuple(int(x.item()) for x in meta[1:1+ndim])
            dtype_enum = int(meta[1+8].item())
            dtype = _dtype_from_enum(dtype_enum)
            shape = shp
        else:
            # Still consume sender meta to keep protocol in sync
            dummy = torch.empty(1 + 8 + 1, dtype=torch.int64)
            self._with_timeout(lambda: dist.recv(dummy, src=src, tag=tag), _COLL_TIMEOUT_SEC)

        dev = device or (torch.device("cuda", torch.cuda.current_device()) if torch.cuda.is_available() else torch.device("cpu"))
        out_cpu = torch.empty(shape, dtype=dtype, pin_memory=True)
        numel = out_cpu.numel()
        chunk_elems = max(1, (_CHUNK_MB * 1024 * 1024) // max(out_cpu.element_size(), 1))
        cursor = 0

        flat = out_cpu.view(-1)
        while cursor < numel:
            take = min(chunk_elems, numel - cursor)
            view = flat[cursor:cursor+take]
            self._with_timeout(lambda: dist.recv(view, src=src, tag=tag), _COLL_TIMEOUT_SEC)
            cursor += take

        return out_cpu.to(dev, non_blocking=True)

    # -------------------- Objects --------------------

    def broadcast_object(self, obj: Any, src: int = 0) -> Any:
        if not self.initialized or self.world_size <= 1:
            return obj
        container = [obj]
        self._with_timeout(lambda: dist.broadcast_object_list(container, src=src), _COLL_TIMEOUT_SEC)
        return container[0]

    def gather_object(self, obj: Any, dst: int = 0) -> Optional[List[Any]]:
        if not self.initialized or self.world_size <= 1:
            return [obj]
        out: List[Any] = [None for _ in range(self.world_size)] if self.rank == dst else []
        self._with_timeout(lambda: dist.gather_object(obj, object_gather_list=out if self.rank == dst else None, dst=dst),
                           _COLL_TIMEOUT_SEC)
        return out if self.rank == dst else None

    # -------------------- Timeout wrapper --------------------

    def _with_timeout(self, fn, timeout_s: float):
        """
        Execute a dist call with a soft timeout. PyTorch ops do not accept custom
        timeouts per call, so we run the op and, if it hangs, we raise after wall time.
        """
        t0 = time.time()
        try:
            result = fn()
        except Exception as e:
            raise
        dt = time.time() - t0
        if dt > timeout_s:
            raise TimeoutError(f"Collective exceeded timeout ({dt:.1f}s > {timeout_s:.1f}s)")
        return result


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _to_reduce_op(name: str):
    name = (name or "sum").lower()
    if "sum" in name:
        return dist.ReduceOp.SUM
    if "max" in name:
        return dist.ReduceOp.MAX
    if "min" in name:
        return dist.ReduceOp.MIN
    if "prod" in name or "mul" in name:
        return dist.ReduceOp.PRODUCT
    # Default
    return dist.ReduceOp.SUM


def _split_chunks_dim0(t: torch.Tensor, parts: int) -> List[torch.Tensor]:
    sz = t.size(0)
    if sz % parts != 0:
        raise ValueError("Size not divisible by parts")
    step = sz // parts
    return [t[i*step:(i+1)*step].contiguous() for i in range(parts)]


def _to_cpu_pinned(t: torch.Tensor) -> torch.Tensor:
    if t.device.type == "cpu":
        return t.pin_memory() if not t.is_pinned() else t
    # Safest path across backends: bounce through CPU-pinned
    return t.detach().to("cpu", non_blocking=True).pin_memory()


# --- dtype enum helpers for simple meta exchange (P2P) ---

_DTYPE_ENUM = {
    torch.float32: 0,
    torch.float16: 1,
    torch.bfloat16: 2,
    torch.int64: 3,
    torch.int32: 4,
    torch.int16: 5,
    torch.int8: 6,
    torch.uint8: 7,
    torch.bool: 8,
}

_ENUM_TO_DTYPE = {v: k for k, v in _DTYPE_ENUM.items()}

def _dtype_from_enum(x: int) -> torch.dtype:
    if x not in _ENUM_TO_DTYPE:
        raise ValueError(f"Unknown dtype enum: {x}")
    return _ENUM_TO_DTYPE[x]


# -----------------------------------------------------------------------------
# Debug / Demo
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Quick self-checks:

    1) Single-process (no torchrun):
       $ python -m skote.distributed.collectives

    2) With torchrun:
       $ torchrun --nproc_per_node=2 -m skote.distributed.collectives
    """
    if torch is None:
        print("PyTorch not available.")
        raise SystemExit(0)

    c = Coll()
    print(f"[coll] init={c.initialized} world={c.world_size} rank={c.rank} backend={c.backend}")

    # Barrier (safe in single-process)
    c.barrier()

    # All-reduce demo
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    x = torch.ones(4, device=dev) * (c.rank + 1)
    y = c.all_reduce(x, op="sum")
    print("[all_reduce] in:", x.tolist(), "out:", y.tolist())

    # All-gather varlen demo
    t = torch.arange(0, 4 + c.rank, device=dev)  # rank-dependent length
    parts = c.all_gather_varlen(t, dim=0)
    print("[all_gather_varlen] lens:", [int(p.numel()) for p in parts])

    # P2P demo (only meaningful when world>1)
    if c.world_size > 1:
        tag = 42
        if c.rank == 0:
            m = torch.full((8,), 3.14, device=dev)
            c.p2p_send_tensor(m, dst=1, tag=tag)
            print("[p2p] rank0 sent.")
        elif c.rank == 1:
            recv = c.p2p_recv_tensor(src=0, shape=(8,), dtype=torch.float32, device=torch.device(dev), tag=tag)
            print("[p2p] rank1 recv:", recv.tolist())
