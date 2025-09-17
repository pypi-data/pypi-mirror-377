# skote/distributed/launcher.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Skotergy Distributed Launcher: zero-config single/multi-device initialization.

Design goals
------------
- Preserve the existing single-GPU pipeline (no behavior change when world_size=1).
- Auto-detect backend and devices via devicemgr.DeviceManager / DevicePlan.
- Support both external torchrun environments and internal single-node spawn.
- Keep semantics minimal: we only set up process groups and per-rank device binding;
  scheduling, graph caches, KV sharding and routing are done by upper layers.

Typical usage
-------------
# 1) Library-managed (single node)
from skote.distributed.launcher import launch
from skote.distributed.devicemgr import acquire_device_plan

plan = acquire_device_plan(model_num_params=7_000_000_000, dtype="bf16")
def main_worker():
    # your program entry (the same as single-GPU); use torch.distributed if world_size>1
    ...

launch(target=main_worker, plan=plan)

# 2) External torchrun (recommended for complex deployments)
# torchrun sets RANK / LOCAL_RANK / WORLD_SIZE; we just initialize.
from skote.distributed.launcher import init_from_env
init_from_env()  # no-op if already initialized
...

Environment knobs
-----------------
- SKOTE_DIST_AUTO        : "1"(default) enable auto distributed when >1 devices; "0" to force single-process.
- SKOTE_NPROC_PER_NODE   : override number of processes to spawn locally (default = number of devices in plan).
- SKOTE_MASTER_ADDR      : init addr (default "127.0.0.1" on single node).
- SKOTE_MASTER_PORT      : init port (auto-choose free port when spawning).
- SKOTE_DIST_BACKEND     : force backend: "nccl"|"gloo"|"ccl"; otherwise auto from plan.backend.
- SKOTE_DEVICE_ALLOW     : device index whitelist, e.g. "0,1".
- SKOTE_LOG_LEVEL        : "INFO"(default) or "DEBUG".

Caveats
-------
- Windows NCCL is unavailable; on Windows it will fall back to Gloo CPU/XPU.
- Intel oneCCL may require proper installation; we fall back to Gloo when ccl is not importable.
- This module does *not* perform model sharding; it only prepares process group & per-rank device binding.
"""

from __future__ import annotations

import os
import sys
import socket
import logging
import contextlib
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any, List, Tuple

try:
    import torch
    import torch.distributed as dist
    import torch.multiprocessing as mp
except Exception:  # pragma: no cover
    torch = None
    dist = None
    mp = None

from skote import get_logger
from skote.distributed.devicemgr import DeviceManager, DevicePlan, BackendKind

log = get_logger("skotergy.launcher")


# --------------------------- Data model ---------------------------

@dataclass
class DistState:
    initialized: bool
    backend: Optional[str]
    world_size: int
    rank: int
    local_rank: int
    master_addr: Optional[str]
    master_port: Optional[str]
    device_index: Optional[int]  # local device index used for binding


# --------------------------- Backend selection ---------------------------

def _select_backend(plan: DevicePlan) -> str:
    forced = os.environ.get("SKOTE_DIST_BACKEND", "").strip().lower()
    if forced in ("nccl", "gloo", "ccl"):
        return forced

    if plan.backend in (BackendKind.CUDA, BackendKind.ROCM):
        return "nccl"
    if plan.backend == BackendKind.XPU:
        # Try oneCCL if available; otherwise Gloo works for CPU/XPU fallback.
        try:
            import oneccl_bindings_for_pytorch  # type: ignore
            return "ccl"
        except Exception:
            return "gloo"
    return "gloo"


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _maybe_downgrade_backend(backend: str) -> str:
    # On Windows, NCCL backend is not supported.
    if _is_windows() and backend == "nccl":
        log.warning("Windows platform: downgrading backend 'nccl' to 'gloo'.")
        return "gloo"
    return backend


# --------------------------- Helpers ---------------------------

def _free_tcp_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _infer_world_and_ranks() -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Return (world_size, rank, local_rank) from torchrun env when present.
    """
    ws = os.environ.get("WORLD_SIZE")
    rk = os.environ.get("RANK")
    lrk = os.environ.get("LOCAL_RANK")
    return (int(ws) if ws else None,
            int(rk) if rk else None,
            int(lrk) if lrk else None)


def _env_true(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip() in ("1", "true", "True", "YES", "yes")


def _visible_devices_from_allow(dev_indices: List[int]) -> str:
    # Render a CUDA_VISIBLE_DEVICES-like string from indices (best effort).
    return ",".join(str(i) for i in dev_indices)


# --------------------------- Initialization paths ---------------------------

def _bind_device_for_rank(plan: DevicePlan, local_rank: int) -> Optional[int]:
    """
    Choose a device index for this local rank and bind current process to it.
    Returns the chosen device index (logical index as seen by torch).
    """
    if torch is None:
        return None

    # Respect SKOTE_DEVICE_ALLOW if present to keep alignment with devicemgr.
    allow = os.environ.get("SKOTE_DEVICE_ALLOW")
    indices = [d.index for d in plan.devices]
    if allow:
        try:
            allow_list = [int(x.strip()) for x in allow.split(",") if x.strip()]
            indices = [i for i in indices if i in allow_list]
        except Exception:
            pass

    if not indices:
        return None

    # Map local_rank into available set.
    idx = indices[local_rank % len(indices)]

    if plan.backend in (BackendKind.CUDA, BackendKind.ROCM):
        try:
            torch.cuda.set_device(idx)
            log.info("Bound to CUDA device index %d", idx)
        except Exception as e:
            log.warning("Failed to set CUDA device %d: %s", idx, e)
    elif plan.backend == BackendKind.XPU:
        with contextlib.suppress(Exception):
            if hasattr(torch, "xpu"):
                torch.xpu.set_device(idx)  # type: ignore[attr-defined]
                log.info("Bound to XPU device index %d", idx)
    else:
        # CPU path: nothing to bind
        pass

    return idx


def _init_process_group(backend: str,
                        world_size: int,
                        rank: int,
                        master_addr: str,
                        master_port: str) -> None:
    if dist is None:
        raise RuntimeError("torch.distributed is not available")

    if dist.is_initialized():
        return

    init_method = f"tcp://{master_addr}:{master_port}"
    log.info("Initializing process group: backend=%s, rank=%d/%d, master=%s:%s",
             backend, rank, world_size, master_addr, master_port)
    dist.init_process_group(
        backend=backend,
        init_method=init_method,
        rank=rank,
        world_size=world_size,
    )


def _build_dist_state(plan: DevicePlan,
                      backend: str,
                      world_size: int,
                      rank: int,
                      local_rank: int,
                      master_addr: str,
                      master_port: str) -> DistState:
    device_idx = _bind_device_for_rank(plan, local_rank)
    # Expose Skote-specific observability envs for upper layers.
    os.environ["SKOTE_WORLD_SIZE"] = str(world_size)
    os.environ["SKOTE_RANK"] = str(rank)
    os.environ["SKOTE_LOCAL_RANK"] = str(local_rank)
    os.environ["SKOTE_DIST_BACKEND"] = backend
    return DistState(
        initialized=True,
        backend=backend,
        world_size=world_size,
        rank=rank,
        local_rank=local_rank,
        master_addr=master_addr,
        master_port=master_port,
        device_index=device_idx,
    )


# --------------------------- Public: external torchrun path ---------------------------

def init_from_env(plan: Optional[DevicePlan] = None) -> DistState:
    """
    Initialize distributed state in an external torchrun context.
    No-op if WORLD_SIZE not set or equals 1.

    Returns DistState (initialized may be False when single-process).
    """
    if plan is None:
        plan = DeviceManager.from_env().get_plan(
            model_num_params=None, dtype=os.environ.get("SKOTE_PREF_PRECISION", "bf16")
        )

    ws, rk, lrk = _infer_world_and_ranks()
    if ws is None or ws <= 1:
        # Single process; bind device 0 if available for consistency.
        _bind_device_for_rank(plan, 0)
        return DistState(False, None, 1, 0, 0, None, None, device_index=0)

    backend = _maybe_downgrade_backend(_select_backend(plan))
    master_addr = os.environ.get("MASTER_ADDR", os.environ.get("SKOTE_MASTER_ADDR", "127.0.0.1"))
    master_port = os.environ.get("MASTER_PORT", os.environ.get("SKOTE_MASTER_PORT", "29500"))

    _init_process_group(backend, ws, rk or 0, master_addr, master_port)
    return _build_dist_state(plan, backend, ws, rk or 0, lrk or 0, master_addr, master_port)


# --------------------------- Public: library-managed single-node spawn ---------------------------

def _worker_entry(rank: int,
                  world_size: int,
                  backend: str,
                  master_addr: str,
                  master_port: str,
                  plan: DevicePlan,
                  target: Callable[[], Any],
                  target_kwargs: Optional[Dict[str, Any]] = None) -> None:
    # Compute local_rank as rank (single-node spawn)
    local_rank = rank
    _init_process_group(backend, world_size, rank, master_addr, master_port)
    _build_dist_state(plan, backend, world_size, rank, local_rank, master_addr, master_port)
    # Execute user target
    if target_kwargs:
        target(**target_kwargs)
    else:
        target()


def _spawn_single_node(target: Callable[[], Any],
                       plan: DevicePlan,
                       nproc_per_node: int,
                       backend: str) -> None:
    if mp is None:
        raise RuntimeError("torch.multiprocessing is not available")

    master_addr = os.environ.get("SKOTE_MASTER_ADDR", "127.0.0.1")
    master_port = os.environ.get("SKOTE_MASTER_PORT", None)
    if master_port is None:
        master_port = str(_free_tcp_port())
        os.environ["SKOTE_MASTER_PORT"] = master_port

    # Optional: constrain devices visible to child processes using SKOTE_DEVICE_ALLOW
    allow = os.environ.get("SKOTE_DEVICE_ALLOW")
    if allow:
        # Make CUDA_VISIBLE_DEVICES reflect SKOTE_DEVICE_ALLOW for child processes only.
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", _visible_devices_from_allow(
            [int(x) for x in allow.split(",") if x.strip()]
        ))

    log.info("Spawning %d processes on single node (backend=%s, master=%s:%s)",
             nproc_per_node, backend, master_addr, master_port)

    ctx = mp.get_context("spawn")
    procs: List[mp.Process] = []
    for rank in range(nproc_per_node):
        p = ctx.Process(
            target=_worker_entry,
            kwargs=dict(
                rank=rank,
                world_size=nproc_per_node,
                backend=backend,
                master_addr=master_addr,
                master_port=master_port,
                plan=plan,
                target=target,
                target_kwargs=None,
            ),
            daemon=False,
        )
        p.start()
        procs.append(p)
    # Wait for completion
    for p in procs:
        p.join()
        if p.exitcode != 0:
            raise RuntimeError(f"Worker process exited with code {p.exitcode}")


def launch(target: Callable[[], Any],
           plan: Optional[DevicePlan] = None,
           nproc_per_node: Optional[int] = None,
           force_single: Optional[bool] = None) -> DistState:
    """
    Unified launcher entry.

    - If torchrun env is detected, initialize from it and call target once (in each rank).
    - Else if SKOTE_DIST_AUTO=1 and nproc_per_node>1, spawn local processes.
    - Else run single-process and bind device 0.

    Returns DistState for the *current* process.
    """
    if plan is None:
        plan = DeviceManager.from_env().get_plan(
            model_num_params=None, dtype=os.environ.get("SKOTE_PREF_PRECISION", "bf16")
        )

    # External torchrun?
    ws_env, rk_env, lrk_env = _infer_world_and_ranks()
    if ws_env and ws_env > 1:
        state = init_from_env(plan)
        # Call target in-place (each rank will execute)
        target()
        return state

    # Library-managed path
    auto = _env_true("SKOTE_DIST_AUTO", True) if force_single is None else (not force_single)
    if not auto:
        # Force single
        _bind_device_for_rank(plan, 0)
        log.info("Distributed disabled (SKOTE_DIST_AUTO=0). Running single-process.")
        target()
        return DistState(False, None, 1, 0, 0, None, None, device_index=0)

    # Decide nproc_per_node
    if nproc_per_node is None:
        # Default to number of detected devices (after allow-list)
        dev_indices = [d.index for d in plan.devices]
        allow = os.environ.get("SKOTE_DEVICE_ALLOW")
        if allow:
            try:
                allow_list = [int(x.strip()) for x in allow.split(",") if x.strip()]
                dev_indices = [i for i in dev_indices if i in allow_list]
            except Exception:
                pass
        nproc_per_node = max(1, len(dev_indices))

    if nproc_per_node <= 1:
        # Single-process fast path
        _bind_device_for_rank(plan, 0)
        log.info("Single device path (nproc_per_node=1).")
        target()
        return DistState(False, None, 1, 0, 0, None, None, device_index=0)

    backend = _maybe_downgrade_backend(_select_backend(plan))
    _spawn_single_node(target=target, plan=plan, nproc_per_node=nproc_per_node, backend=backend)
    # The parent process here is not part of the process group; return a neutral state.
    return DistState(False, backend, nproc_per_node, rank=0, local_rank=0,
                     master_addr=os.environ.get("SKOTE_MASTER_ADDR"),
                     master_port=os.environ.get("SKOTE_MASTER_PORT"),
                     device_index=None)


# --------------------------- Debug CLI ---------------------------

def _demo_target() -> None:
    """
    Minimal demo target: prints rank/world info. Useful for quick validation.
    """
    ws = int(os.environ.get("WORLD_SIZE", os.environ.get("SKOTE_WORLD_SIZE", "1")))
    rk = int(os.environ.get("RANK", os.environ.get("SKOTE_RANK", "0")))
    lrk = int(os.environ.get("LOCAL_RANK", os.environ.get("SKOTE_LOCAL_RANK", "0")))
    backend = os.environ.get("SKOTE_DIST_BACKEND", "none")
    # Device hint
    dev = "cpu"
    if torch is not None:
        if torch.cuda.is_available():
            dev = f"cuda:{torch.cuda.current_device()}"
        elif hasattr(torch, "xpu") and getattr(torch.xpu, "is_available", lambda: False)():
            dev = f"xpu:{getattr(torch.xpu, 'current_device', lambda: 0)()}"  # type: ignore
    print(f"[demo] rank={rk}/{ws} local_rank={lrk} backend={backend} device={dev}")


if __name__ == "__main__":
    """
    Run quick checks:

    1) Single-process (no torchrun):
       $ python -m skote.distributed.launcher

    2) Library-managed multi-proc (single node):
       $ SKOTE_DIST_AUTO=1 SKOTE_NPROC_PER_NODE=2 python -m skote.distributed.launcher

    3) External torchrun:
       $ torchrun --nproc_per_node=2 -m skote.distributed.launcher
    """
    import argparse
    parser = argparse.ArgumentParser("Skotergy Distributed Launcher")
    parser.add_argument("--auto", type=int, default=1, help="Enable auto distributed (SKOTE_DIST_AUTO)")
    parser.add_argument("--nproc", type=int, default=None, help="Override nproc_per_node")
    args = parser.parse_args()

    os.environ["SKOTE_DIST_AUTO"] = "1" if args.auto else "0"
    if args.nproc is not None:
        os.environ["SKOTE_NPROC_PER_NODE"] = str(args.nproc)

    plan = DeviceManager.from_env().get_plan(dtype=os.environ.get("SKOTE_PREF_PRECISION", "bf16"))
    launch(target=_demo_target, plan=plan,
           nproc_per_node=int(os.environ.get("SKOTE_NPROC_PER_NODE", "0")) or None)
