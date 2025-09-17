# skote/distributed/devicemgr.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Device Manager for Skotergy: unified device discovery and planning.

Goals
-----
- Detect available backends (CUDA, ROCm, Intel XPU, CPU) and enumerate devices.
- Collect device properties (name, memory, capability, PCIe/NVLink-ish topology).
- Produce a DevicePlan that higher layers (launcher/router/graphmgr/scheduler)
  can consume to decide replicate/pipeline/tensor/hybrid strategies.
- Be safe-by-default: degrade gracefully with missing libraries (pynvml, ipex).
- Zero-config "auto" behavior, overridable via environment variables.

This module **does not** launch processes or set parallel strategies; it **reports**
what is available and provides hints. Actual execution policy is chosen by router.
"""

from __future__ import annotations

import json
import logging
import os
import math
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple

# Optional heavy deps are imported lazily / guarded.
try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore

# Optional NVML for CUDA topology detail (NVLink, memory, etc.)
try:
    import pynvml  # type: ignore
    _HAS_NVML = True
except Exception:
    _HAS_NVML = False

# Optional Intel XPU / IPEX
try:
    import intel_extension_for_pytorch as ipex  # type: ignore
    _HAS_IPEX = True
except Exception:
    _HAS_IPEX = False

LOG = logging.getLogger("skote.devicemgr")
if not LOG.handlers:
    logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))


# ---------- Data Models ----------

class BackendKind:
    CUDA = "cuda"
    ROCM = "rocm"
    XPU = "xpu"
    CPU = "cpu"


@dataclass
class DeviceInfo:
    index: int
    backend: str
    name: str
    total_mem: Optional[int]  # bytes
    free_mem: Optional[int]   # bytes
    compute_cap: Optional[Tuple[int, int]] = None  # CUDA SM version (major, minor)
    arch: Optional[str] = None                     # e.g., "sm80", "gfx90a", "xe-hpg"
    pcie_gen: Optional[int] = None
    pcie_width: Optional[int] = None
    nvlink_links: int = 0
    peer_accessible: List[int] = field(default_factory=list)
    uuid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Make tuples JSON-friendly
        if self.compute_cap is not None:
            d["compute_cap"] = list(self.compute_cap)
        return d


@dataclass
class TopologyInfo:
    # bandwidth_score[i][j] in [0..100]: higher means faster
    bandwidth_score: List[List[int]]
    # peer_matrix[i][j] = True if direct peer access is supported
    peer_matrix: List[List[bool]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bandwidth_score": self.bandwidth_score,
            "peer_matrix": self.peer_matrix,
        }


@dataclass
class DevicePlan:
    backend: str
    devices: List[DeviceInfo]
    topology: Optional[TopologyInfo]
    # Recommendations (router decides final policy)
    recommend_replicate: bool
    recommend_pipeline: bool
    recommend_tensor: bool
    recommend_hybrid: bool
    # Reasoning / notes for observability
    notes: List[str] = field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "backend": self.backend,
                "devices": [d.to_dict() for d in self.devices],
                "topology": None if self.topology is None else self.topology.to_dict(),
                "recommendations": {
                    "replicate": self.recommend_replicate,
                    "pipeline": self.recommend_pipeline,
                    "tensor": self.recommend_tensor,
                    "hybrid": self.recommend_hybrid,
                },
                "notes": self.notes,
            },
            indent=indent,
        )


# ---------- Helpers ----------

def _env_list(name: str) -> Optional[List[int]]:
    v = os.environ.get(name)
    if not v:
        return None
    try:
        return [int(x.strip()) for x in v.split(",") if x.strip() != ""]
    except Exception:
        LOG.warning("Bad env list for %s=%s", name, v)
        return None


def _bytes_per_param(dtype: str) -> float:
    d = dtype.lower()
    if d in ("fp32", "float32"):
        return 4.0
    if d in ("fp16", "float16", "half"):
        return 2.0
    if d in ("bf16", "bfloat16"):
        return 2.0
    if d in ("fp8", "fp8_e4m3", "fp8_e5m2", "e4m3", "e5m2", "int8"):
        return 1.0
    # Default conservatively to 2 bytes (bf16-class)
    return 2.0


def estimate_model_bytes(num_params: Optional[int],
                         dtype: str = "bf16",
                         extra_overhead_ratio: float = 0.10) -> Optional[int]:
    """
    Rough param-only footprint in bytes; returns None if num_params is None.
    Adds a small overhead ratio to account for optimizer-less buffers, metadata, etc.
    """
    if num_params is None:
        return None
    bpp = _bytes_per_param(dtype)
    return int(num_params * bpp * (1.0 + extra_overhead_ratio))


def _safe_cuda_mem_info(dev: int) -> Tuple[Optional[int], Optional[int]]:
    """
    Return (free, total) in bytes for the given CUDA/ROCm device index.
    """
    try:
        # Works for CUDA and ROCm (PyTorch unifies API).
        with torch.cuda.device(dev):
            free_b, total_b = torch.cuda.mem_get_info()
        return int(free_b), int(total_b)
    except Exception as e:
        LOG.debug("mem_get_info failed on device %d: %s", dev, e)
        return None, None


def _detect_backend_hint() -> Optional[str]:
    v = os.environ.get("SKOTE_BACKEND_HINT")
    if v:
        v = v.strip().lower()
        if v in (BackendKind.CUDA, BackendKind.ROCM, BackendKind.XPU, BackendKind.CPU):
            return v
    return None


# ---------- Probing Implementations ----------

def _probe_cuda_or_rocm() -> Tuple[Optional[str], List[DeviceInfo]]:
    """
    Probe CUDA/ROCm via torch. Returns (backend, devices).
    backend is 'cuda' or 'rocm', or (None, []) if unavailable.
    """
    if torch is None:
        return None, []

    if not torch.cuda.is_available():
        return None, []

    # Distinguish CUDA vs ROCm
    backend = BackendKind.CUDA
    try:
        # On ROCm builds, torch.version.hip is set; torch.version.cuda may be None.
        if getattr(torch.version, "hip", None):
            backend = BackendKind.ROCM
    except Exception:
        pass

    count = torch.cuda.device_count()
    if count <= 0:
        return None, []

    devices: List[DeviceInfo] = []
    for i in range(count):
        name = torch.cuda.get_device_name(i)
        free_b, total_b = _safe_cuda_mem_info(i)
        compute_cap = None
        arch = None
        uuid = None
        try:
            if backend == BackendKind.CUDA:
                compute_cap = torch.cuda.get_device_capability(i)  # (major, minor)
                # Map to smXY string (approx)
                arch = f"sm{compute_cap[0]}{compute_cap[1]}"
        except Exception:
            pass

        # NVML extras (only for CUDA; ROCm NVML may not be present)
        pcie_gen = None
        pcie_width = None
        nvlink_links = 0
        if _HAS_NVML and backend == BackendKind.CUDA:
            try:
                pynvml.nvmlInit()
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                uuid = pynvml.nvmlDeviceGetUUID(h).decode("utf-8") if hasattr(pynvml, "nvmlDeviceGetUUID") else None
                try:
                    pci = pynvml.nvmlDeviceGetPciInfo(h)
                    # width (lanes) may be in 'pci.link.width' or dev-dep fields; fallback to None when missing
                    pcie_width = getattr(pci, "maxLinkWidth", None)
                    # gen can be mapped from current max speed; many drivers expose nvmlDeviceGetMaxPcieLinkGeneration
                    try:
                        pcie_gen = pynvml.nvmlDeviceGetMaxPcieLinkGeneration(h)
                    except Exception:
                        pcie_gen = None
                except Exception:
                    pass
                # Count active NVLink links
                # Not all NVML versions expose the same API; we try numbered links.
                for link in range(12):  # A100 has up to 12 NVLink bricks
                    try:
                        if pynvml.nvmlDeviceGetNvLinkState(h, link):
                            nvlink_links += 1
                    except Exception:
                        break
            except Exception as e:
                LOG.debug("NVML probe failed on device %d: %s", i, e)
            finally:
                try:
                    pynvml.nvmlShutdown()
                except Exception:
                    pass

        # Peer access
        peer_list: List[int] = []
        for j in range(count):
            if i == j:
                continue
            can = False
            try:
                can = torch.cuda.device_can_access_peer(i, j)
            except Exception:
                can = False
            if can:
                peer_list.append(j)

        devices.append(
            DeviceInfo(
                index=i,
                backend=backend,
                name=name,
                total_mem=total_b,
                free_mem=free_b,
                compute_cap=compute_cap,
                arch=arch,
                pcie_gen=pcie_gen,
                pcie_width=pcie_width,
                nvlink_links=nvlink_links,
                peer_accessible=peer_list,
                uuid=uuid,
            )
        )
    return backend, devices


def _probe_xpu() -> Tuple[Optional[str], List[DeviceInfo]]:
    """
    Probe Intel XPU (oneAPI) via torch.xpu / IPEX.
    Returns (backend, devices) or (None, []) if unavailable.
    """
    if torch is None:
        return None, []
    try:
        has_xpu = hasattr(torch, "xpu") and torch.xpu.is_available()
    except Exception:
        has_xpu = False
    if not has_xpu:
        return None, []

    try:
        count = torch.xpu.device_count()  # type: ignore[attr-defined]
    except Exception:
        count = 1  # Conservative default

    devices: List[DeviceInfo] = []
    for i in range(count):
        name = f"Intel XPU {i}"
        total_b = None
        free_b = None
        arch = None
        uuid = None
        try:
            if _HAS_IPEX and hasattr(ipex, "xpu"):
                props = getattr(ipex.xpu, "get_device_properties", lambda _: None)(i)  # type: ignore
                if props is not None:
                    total_b = getattr(props, "total_memory", None)
                    arch = getattr(props, "gpu_name", None)
        except Exception:
            pass

        # Peer access and PCIe detail are not uniformly exposed; leave empty.
        devices.append(
            DeviceInfo(
                index=i,
                backend=BackendKind.XPU,
                name=name,
                total_mem=total_b,
                free_mem=free_b,
                compute_cap=None,
                arch=arch,
                pcie_gen=None,
                pcie_width=None,
                nvlink_links=0,
                peer_accessible=[],
                uuid=uuid,
            )
        )
    return BackendKind.XPU, devices


def _probe_cpu() -> Tuple[str, List[DeviceInfo]]:
    """
    Always available fallback; represents a single logical CPU "device".
    """
    total_b = None
    try:
        # Try to estimate available RAM (optional)
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        total_b = int(vm.available)
    except Exception:
        total_b = None

    d = DeviceInfo(
        index=0,
        backend=BackendKind.CPU,
        name="CPU",
        total_mem=total_b,
        free_mem=total_b,
    )
    return BackendKind.CPU, [d]


def _build_topology(devs: List[DeviceInfo], backend: str) -> Optional[TopologyInfo]:
    """
    Build a coarse topology matrix:
    - bandwidth_score[i][j] ∈ {0, 20, 50, 80, 100}, heuristic.
    - peer_matrix[i][j] from device_can_access_peer (CUDA/ROCm) when available.
    """
    n = len(devs)
    if n <= 1:
        return None

    peer = [[False for _ in range(n)] for _ in range(n)]
    score = [[0 for _ in range(n)] for _ in range(n)]

    # Initialize peer matrix from recorded peer_accessible lists
    for di in devs:
        for j in di.peer_accessible:
            if 0 <= j < n:
                peer[di.index][j] = True

    # Heuristic bandwidth scoring:
    # 100: reported NVLink on both ends
    # 80: peer access True (same PCIe switch / P2P allowed)
    # 50: same backend but no peer access
    # 20: different backend class (should not happen within one plan)
    # 0: self or invalid
    for i in range(n):
        for j in range(n):
            if i == j:
                score[i][j] = 0
                continue
            if backend == BackendKind.CUDA:
                if devs[i].nvlink_links > 0 and devs[j].nvlink_links > 0:
                    score[i][j] = 100
                elif peer[i][j]:
                    score[i][j] = 80
                else:
                    score[i][j] = 50
            else:
                # ROCm or XPU: we often lack detailed link info.
                score[i][j] = 80 if peer[i][j] else 50

    return TopologyInfo(bandwidth_score=score, peer_matrix=peer)


# ---------- Public API ----------

class DeviceManager:
    """
    Unified device discovery and planning.

    Typical usage:
    --------------
    dm = DeviceManager.from_env()
    plan = dm.get_plan(model_num_params=7_000_000_000, dtype="bf16")
    print(plan.to_json())

    Environment variables (optional):
    ---------------------------------
    SKOTE_BACKEND_HINT=cuda|rocm|xpu|cpu
    SKOTE_DEVICE_ALLOW=0,1,2        # Whitelist GPU indices
    SKOTE_RESERVE_MEM_RATIO=0.10     # Keep this fraction free
    SKOTE_MIN_FREE_MEM=536870912     # Require at least this many free bytes
    SKOTE_PREF_PRECISION=bf16|fp16|fp32|fp8
    """

    def __init__(self,
                 backend: str,
                 devices: List[DeviceInfo],
                 topology: Optional[TopologyInfo]):
        self.backend = backend
        self.devices = devices
        self.topology = topology
        self.notes: List[str] = []

    @classmethod
    def from_env(cls) -> "DeviceManager":
        """
        Probe devices honoring environment hints. CUDA/ROCm have priority;
        if not present, try XPU; else fallback to CPU.
        """
        hint = _detect_backend_hint()

        backend = None
        devices: List[DeviceInfo] = []
        topo: Optional[TopologyInfo] = None

        # Probe order: respect hint when possible
        probe_order = (
            [hint] if hint else [BackendKind.CUDA, BackendKind.ROCM, BackendKind.XPU, BackendKind.CPU]
        )

        for target in probe_order:
            if target == BackendKind.CUDA or target == BackendKind.ROCM:
                b, devs = _probe_cuda_or_rocm()
                if b is not None:
                    backend = b
                    devices = devs
                    break
            elif target == BackendKind.XPU:
                b, devs = _probe_xpu()
                if b is not None:
                    backend = b
                    devices = devs
                    break
            elif target == BackendKind.CPU:
                backend, devices = _probe_cpu()
                break

        # If nothing found above (shouldn't happen), fallback to CPU
        if backend is None or not devices:
            backend, devices = _probe_cpu()

        # Apply device allow-list if present
        allow = _env_list("SKOTE_DEVICE_ALLOW")
        if allow is not None:
            filtered = [d for d in devices if d.index in allow]
            if filtered:
                devices = filtered

        topo = _build_topology(devices, backend)

        dm = cls(backend=backend, devices=devices, topology=topo)
        # Quick note for observability
        dm.notes.append(f"Detected backend={backend}, num_devices={len(devices)}")
        return dm

    # ---- Planning ----

    def _memory_ok_single(self,
                          dev: DeviceInfo,
                          model_bytes: Optional[int],
                          reserve_ratio: float,
                          min_free: Optional[int]) -> bool:
        """
        Decide whether a single device can host the model given free memory thresholds.
        """
        if model_bytes is None:
            # If model size unknown, allow single-device by best effort.
            return True
        if dev.total_mem is None or dev.free_mem is None:
            # Without memory info we assume optimistic single-device fit.
            return True
        keep_free = int(dev.total_mem * reserve_ratio)
        if min_free is not None:
            keep_free = max(keep_free, min_free)
        return dev.free_mem - keep_free >= model_bytes

    def _recommendations(self,
                         model_bytes: Optional[int]) -> Tuple[bool, bool, bool, bool, List[str]]:
        """
        Produce (replicate, pipeline, tensor, hybrid, notes).
        Heuristics:
        - prefer replicate when any device can fit the model with reserve.
        - else prefer pipeline if sum memory can fit model.
        - tensor requires >=2 same-arch devices and "good" bandwidth.
        - hybrid is a fallback when both pipeline/tensor are plausible.
        """
        notes: List[str] = []

        reserve_ratio = float(os.environ.get("SKOTE_RESERVE_MEM_RATIO", "0.10"))
        min_free = int(os.environ["SKOTE_MIN_FREE_MEM"]) if "SKOTE_MIN_FREE_MEM" in os.environ else None

        # Check single-device fit
        can_single = any(self._memory_ok_single(d, model_bytes, reserve_ratio, min_free)
                         for d in self.devices)

        # Sum memory across devices (very rough) for pipeline feasibility
        total_free = 0
        total_mem_known = True
        if model_bytes is not None:
            for d in self.devices:
                if d.total_mem is None or d.free_mem is None:
                    total_mem_known = False
                    break
                keep_free = max(int(d.total_mem * reserve_ratio), (min_free or 0))
                total_free += max(0, d.free_mem - keep_free)

        can_pipeline = False
        if model_bytes is None:
            can_pipeline = len(self.devices) >= 2
        elif total_mem_known:
            can_pipeline = total_free >= model_bytes
        else:
            can_pipeline = len(self.devices) >= 2  # optimistic

        # Tensor parallel feasibility (same arch & decent links)
        same_arch = len({(d.backend, d.arch) for d in self.devices}) == 1
        good_links = False
        if self.topology and len(self.devices) >= 2:
            # Consider "good" if any pair has score >= 80
            for i in range(len(self.devices)):
                for j in range(len(self.devices)):
                    if i == j:
                        continue
                    if self.topology.bandwidth_score[i][j] >= 80:
                        good_links = True
                        break
                if good_links:
                    break
        can_tensor = len(self.devices) >= 2 and same_arch and good_links

        # Compose recommendations
        recommend_replicate = can_single
        recommend_pipeline = (not can_single) and can_pipeline
        recommend_tensor = (not can_single) and can_tensor
        recommend_hybrid = (not can_single) and (can_pipeline or can_tensor) and (not (recommend_pipeline and recommend_tensor))

        # Notes
        notes.append(f"single_fit={can_single}, pipeline_ok={can_pipeline}, tensor_ok={can_tensor}")
        if can_tensor and not same_arch:
            notes.append("tensor discouraged: mixed architectures")
        if can_tensor and not good_links:
            notes.append("tensor discouraged: weak interconnect")
        if can_pipeline and model_bytes is not None:
            notes.append(f"aggregate_free_estimate~{total_free/1e9:.1f} GB vs model~{(model_bytes or 0)/1e9:.1f} GB")

        return recommend_replicate, recommend_pipeline, recommend_tensor, recommend_hybrid, notes

    def get_plan(self,
                 model_num_params: Optional[int] = None,
                 dtype: str = None) -> DevicePlan:
        """
        Build a DevicePlan for the current host and (optional) model hints.

        Parameters
        ----------
        model_num_params : Optional[int]
            Number of model parameters (e.g., 7_000_000_000). If None, memory
            checks are heuristic/optimistic.
        dtype : Optional[str]
            Preferred *model* precision (e.g., "bf16", "fp16", "fp32", "fp8").
            If None, reads SKOTE_PREF_PRECISION or defaults to "bf16".

        Returns
        -------
        DevicePlan
        """
        if dtype is None:
            dtype = os.environ.get("SKOTE_PREF_PRECISION", "bf16")

        model_bytes = estimate_model_bytes(model_num_params, dtype=dtype)
        rec_rep, rec_pipe, rec_tensor, rec_hybrid, rec_notes = self._recommendations(model_bytes)

        notes = list(self.notes) + rec_notes
        plan = DevicePlan(
            backend=self.backend,
            devices=self.devices,
            topology=self.topology,
            recommend_replicate=rec_rep,
            recommend_pipeline=rec_pipe,
            recommend_tensor=rec_tensor,
            recommend_hybrid=rec_hybrid,
            notes=notes,
        )
        return plan

    # ---- Utilities ----

    def enable_peer_access(self) -> None:
        """
        Best-effort enable CUDA/ROCm peer access for pairs that support it.
        Safe to call on single-device hosts or non-CUDA backends (no-op).
        """
        if torch is None:
            return
        if self.backend not in (BackendKind.CUDA, BackendKind.ROCM):
            return
        try:
            n = torch.cuda.device_count()
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    try:
                        if torch.cuda.device_can_access_peer(i, j):
                            with torch.cuda.device(i):
                                torch.cuda.enable_peer_access(j)
                    except RuntimeError:
                        # Already enabled or not permitted
                        pass
        except Exception as e:
            LOG.debug("enable_peer_access failed: %s", e)

    def summarize(self) -> str:
        """
        Human-readable summary.
        """
        lines = [f"[Skote] backend={self.backend}, devices={len(self.devices)}"]
        for d in self.devices:
            mem = "-"
            if d.free_mem is not None and d.total_mem is not None:
                mem = f"{d.free_mem/1e9:.1f}G free / {d.total_mem/1e9:.1f}G total"
            cap = f" cc={d.compute_cap}" if d.compute_cap else ""
            arch = f" arch={d.arch}" if d.arch else ""
            links = f" nvlink={d.nvlink_links}" if d.nvlink_links else ""
            lines.append(f" - [{d.index}] {d.name} | {mem}{cap}{arch}{links}")
        if self.topology and len(self.devices) > 1:
            lines.append("Topology (bandwidth score):")
            for row in self.topology.bandwidth_score:
                lines.append("  " + " ".join(f"{v:3d}" for v in row))
        return "\n".join(lines)


# ---------- Convenience Entrypoints ----------

def acquire_device_plan(model_num_params: Optional[int] = None,
                        dtype: Optional[str] = None) -> DevicePlan:
    """
    One-shot helper for callers that don't want to manage the class lifecycle.
    """
    dm = DeviceManager.from_env()
    plan = dm.get_plan(model_num_params=model_num_params, dtype=dtype or os.environ.get("SKOTE_PREF_PRECISION", "bf16"))
    return plan


# ---------- CLI Debug ----------

if __name__ == "__main__":
    """
    Debug CLI:
    $ SKOTE_LOG_LEVEL=DEBUG python -m skote.distributed.devicemgr
    or
    $ python skote/distributed/devicemgr.py
    """
    import argparse
    parser = argparse.ArgumentParser("Skotergy Device Manager")
    parser.add_argument("--params", type=int, default=None, help="Model parameter count (e.g., 7000000000)")
    parser.add_argument("--dtype", type=str, default=None, help="Model dtype: bf16|fp16|fp32|fp8")
    args = parser.parse_args()

    dm = DeviceManager.from_env()
    print(dm.summarize())
    plan = dm.get_plan(model_num_params=args.params, dtype=args.dtype)
    print("\n=== DevicePlan(JSON) ===")
    print(plan.to_json())
