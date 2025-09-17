# skote/runtime/sgmv.py
"""
Skotergy SGMV (Segmented / Grouped GEMV) for multi-tenant LoRA decode

Why this module exists
----------------------
Multi-tenant LoRA inference often mixes requests with different adapters in the
SAME batch. A naive implementation either:
  (a) splits the batch per-adapter → many tiny GEMMs (launch overhead, poor SM occupancy), or
  (b) runs sequentially per request → even worse utilization.

SGMV aggregates these per-adapter LoRA contributions into a small number of
batched GEMMs while keeping a clean, pluggable interface:
  y = X @ W^T + sum_i scale_i * ( (X_i @ A_i^T) @ B_i^T )
where:
  - W: base weight [O, I]
  - A_i: LoRA "down"  [r, I]
  - B_i: LoRA "up"    [O, r]
  - X_i: sub-batch rows of X that chose adapter i
  - scale_i: per-adapter (alpha/r) optionally modulated per-sample

This file provides:
- LoRAAdapter: container for (A, B, alpha/r) with device/dtype helpers
- SGMVRegistry: thread-safe adapter registry (add/remove/query)
- SGMVEngine: drop-in matmul that fuses base + LoRA for a batch with mixed adapters
  * Torch baseline path (works on CPU/CUDA) with vectorized per-adapter groups
  * Clean public API so a future CUDA/Triton kernel can replace the inner loop

Notes
-----
- Shapes follow the common convention: W: [O, I], A: [r, I], B: [O, r].
- Computation casts inputs to an internal "compute dtype" (by default weight.dtype).
- All comments/docstrings are in English by requirement. Only this header note explains rationale.
"""

from __future__ import annotations

import os
import math
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Iterable

try:
    import torch
except Exception as e:  # pragma: no cover
    raise RuntimeError("sgmv.py requires PyTorch installed.") from e

from skote import get_logger

log = get_logger("skotergy.sgmv")


# --------------------------- Data containers ---------------------------

@dataclass
class LoRAAdapter:
    """
    Container for a LoRA adapter.
    A: [r, I], B: [O, r]; scale = alpha / r (typical LoRA scaling).
    """
    A: torch.Tensor
    B: torch.Tensor
    scale: float  # usually alpha / r
    adapter_id: str

    def to(self, device: Optional[torch.device] = None, dtype: Optional[torch.dtype] = None) -> "LoRAAdapter":
        A = self.A
        B = self.B
        if device is not None:
            A = A.to(device, non_blocking=True)
            B = B.to(device, non_blocking=True)
        if dtype is not None:
            A = A.to(dtype)
            B = B.to(dtype)
        return LoRAAdapter(A=A.contiguous(), B=B.contiguous(), scale=float(self.scale), adapter_id=self.adapter_id)

    @property
    def rank(self) -> int:
        return int(self.A.shape[0])

    @property
    def in_features(self) -> int:
        return int(self.A.shape[1])

    @property
    def out_features(self) -> int:
        return int(self.B.shape[0])


class SGMVRegistry:
    """
    Thread-safe registry of LoRA adapters by id.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._map: Dict[str, LoRAAdapter] = {}

    def add(self, adapter: LoRAAdapter) -> None:
        with self._lock:
            self._map[adapter.adapter_id] = adapter
            log.info("Registered LoRA adapter id=%s (rank=%d, in=%d, out=%d, scale=%.6f)",
                     adapter.adapter_id, adapter.rank, adapter.in_features, adapter.out_features, adapter.scale)

    def remove(self, adapter_id: str) -> bool:
        with self._lock:
            ok = adapter_id in self._map
            self._map.pop(adapter_id, None)
            return ok

    def get(self, adapter_id: str) -> Optional[LoRAAdapter]:
        with self._lock:
            return self._map.get(adapter_id)

    def has(self, adapter_id: str) -> bool:
        with self._lock:
            return adapter_id in self._map

    def clear(self) -> None:
        with self._lock:
            self._map.clear()

    def device_dtype_guard(self, device: torch.device, dtype: torch.dtype) -> None:
        """
        Optional check: ensures all adapters live on the same device/dtype as the base weight.
        """
        with self._lock:
            for a in self._map.values():
                if a.A.device != device or a.B.device != device:
                    raise RuntimeError(f"Adapter {a.adapter_id} on device {a.A.device}, expected {device}")
                if a.A.dtype != dtype or a.B.dtype != dtype:
                    raise RuntimeError(f"Adapter {a.adapter_id} dtype mismatch ({a.A.dtype}/{a.B.dtype}) vs {dtype}")


# --------------------------- SGMV Engine ---------------------------

class SGMVEngine:
    """
    SGMV execution engine: combines base weight with per-sample LoRA adapters.

    Public API:
      - SGMVEngine(base_weight, bias=None, registry=None, compute_dtype=None)
      - forward(X, adapter_ids, *, scales=None) -> y
        * X: [B, I]
        * adapter_ids: Sequence[str] length B (can include None for "no adapter")
        * scales: optional per-sample multiplicative scale (broadcasted with registry scale)

    Design:
      - Base path always computed once: base = X @ W^T (+ bias)
      - Per-adapter contributions computed per group of samples, then scattered-add into output.
      - Torch-only baseline is intentionally simple and robust; to be replaced by a fused CUDA kernel later.
    """

    def __init__(
        self,
        base_weight: torch.Tensor,   # [O, I]
        bias: Optional[torch.Tensor] = None,  # [O]
        registry: Optional[SGMVRegistry] = None,
        compute_dtype: Optional[torch.dtype] = None,
    ) -> None:
        if base_weight.dim() != 2:
            raise ValueError(f"base_weight must be 2D [O, I], got {list(base_weight.shape)}")
        self.W = base_weight.contiguous()
        self.bias = bias.contiguous() if bias is not None else None
        self.reg = registry or SGMVRegistry()
        self.compute_dtype = compute_dtype or self.W.dtype
        self.device = self.W.device
        self._check_bias()

    def _check_bias(self) -> None:
        if self.bias is not None:
            if self.bias.dim() != 1 or self.bias.shape[0] != self.W.shape[0]:
                raise ValueError(f"bias must be [O], got {list(self.bias.shape)} vs O={self.W.shape[0]}")
            if self.bias.device != self.W.device or self.bias.dtype != self.W.dtype:
                self.bias = self.bias.to(device=self.W.device, dtype=self.W.dtype)

    # ------------- helpers -------------

    @staticmethod
    def _group_indices(adapter_ids: Sequence[Optional[str]]) -> Dict[Optional[str], torch.Tensor]:
        """
        Return a dict adapter_id -> 1D LongTensor of indices into the batch.
        """
        groups: Dict[Optional[str], List[int]] = {}
        for i, aid in enumerate(adapter_ids):
            groups.setdefault(aid, []).append(i)
        return {k: torch.tensor(v, dtype=torch.long) for k, v in groups.items()}

    def _matmul_base(self, X: torch.Tensor) -> torch.Tensor:
        """
        y = X @ W^T + bias
        """
        y = X.matmul(self.W.transpose(0, 1))
        if self.bias is not None:
            y = y + self.bias
        return y

    # ------------- public API -------------

    @torch.no_grad()
    def forward(
        self,
        X: torch.Tensor,                         # [B, I]
        adapter_ids: Sequence[Optional[str]],    # length B, None => no LoRA
        *,
        scales: Optional[torch.Tensor] = None,   # [B] optional, multiplicative with registry scale
    ) -> torch.Tensor:
        """
        Compute base matmul plus LoRA contributions for a mixed-adapter batch.

        Behavior:
        - If all adapter_ids are None, returns base-only.
        - For each unique adapter, computes ((X_k @ A^T) @ B^T) scaled, and scatters into y at indices.
        - Uses contiguous fast paths and limits dtype/device casts.

        Returns:
        - y: [B, O]
        """
        if X.dim() != 2:
            raise ValueError(f"X must be 2D [B, I], got {list(X.shape)}")
        B, I = int(X.shape[0]), int(X.shape[1])
        O = int(self.W.shape[0])
        if len(adapter_ids) != B:
            raise ValueError(f"adapter_ids length {len(adapter_ids)} != batch size {B}")

        # Device/dtype normalization
        if X.device != self.device:
            X = X.to(self.device, non_blocking=True)
        if X.dtype != self.compute_dtype:
            X = X.to(self.compute_dtype)

        # 1) Base contribution once
        y = self._matmul_base(X)

        # 2) Early exit if no adapters
        if all(aid is None for aid in adapter_ids):
            return y

        # Optional per-sample scaling
        if scales is not None:
            if scales.shape != (B,):
                raise ValueError(f"scales should be [B], got {list(scales.shape)}")
            if scales.device != self.device:
                scales = scales.to(self.device, non_blocking=True)
            if scales.dtype != self.compute_dtype:
                scales = scales.to(self.compute_dtype)

        # 3) Group rows by adapter id
        groups = self._group_indices(adapter_ids)

        # 4) For each adapter group, compute LoRA term and scatter-add
        for aid, idx in groups.items():
            if aid is None:
                continue  # base-only rows
            adapter = self.reg.get(aid)
            if adapter is None:
                raise KeyError(f"Unknown adapter id: {aid}")
            # Basic shape checks
            if adapter.in_features != I or adapter.out_features != O:
                raise ValueError(
                    f"Adapter {aid} shape mismatch: adapter (I={adapter.in_features}, O={adapter.out_features}) vs base (I={I}, O={O})"
                )

            # Slice sub-batch X_k, ensure contiguous & correct dtype/device
            Xk = X.index_select(dim=0, index=idx)
            # (nk, I) @ (I, r) = (nk, r) using A^T
            # Make sure adapter tensors are on the right device/dtype
            A = adapter.A.to(device=self.device, dtype=self.compute_dtype, non_blocking=True).contiguous()
            Bup = adapter.B.to(device=self.device, dtype=self.compute_dtype, non_blocking=True).contiguous()

            Tk = Xk.matmul(A.transpose(0, 1))            # (nk, r)
            Yk = Tk.matmul(Bup.transpose(0, 1))          # (nk, O)

            # Scale = registry scale * optional per-sample scales[idx]
            scale = float(adapter.scale)
            if scales is not None:
                scale_vec = scales.index_select(dim=0, index=idx) * scale
                # Broadcast multiply across features
                Yk = Yk * scale_vec.view(-1, 1)
            else:
                Yk = Yk * scale

            # Scatter-add into y
            y.index_copy_(dim=0, index=idx, source=y.index_select(0, idx) + Yk)

        return y

    # Convenience PyTorch-style interface
    __call__ = forward

    # ------------- utils -------------

    def register_adapter(self, adapter_id: str, A: torch.Tensor, B: torch.Tensor, alpha: float) -> None:
        """
        Register a LoRA adapter with given (A, B) and alpha value.
        Scaling is alpha / rank by convention.
        """
        if A.dim() != 2 or B.dim() != 2:
            raise ValueError("A must be [r, I], B must be [O, r]")
        r, I = int(A.shape[0]), int(A.shape[1])
        O, rB = int(B.shape[0]), int(B.shape[1])
        if r != rB:
            raise ValueError(f"Rank mismatch: A rank {r} vs B rank {rB}")
        if I != int(self.W.shape[1]) or O != int(self.W.shape[0]):
            raise ValueError(f"Adapter shape [{O}, {r}]x[{r}, {I}] incompatible with base W [{self.W.shape[0]}, {self.W.shape[1]}]")
        scale = float(alpha) / float(max(1, r))
        adapter = LoRAAdapter(A=A.contiguous().to(device=self.device, dtype=self.compute_dtype),
                              B=B.contiguous().to(device=self.device, dtype=self.compute_dtype),
                              scale=scale, adapter_id=adapter_id)
        self.reg.add(adapter)

    def remove_adapter(self, adapter_id: str) -> bool:
        return self.reg.remove(adapter_id)

    def clear_adapters(self) -> None:
        self.reg.clear()

    def to(self, device: Optional[torch.device] = None, dtype: Optional[torch.dtype] = None) -> "SGMVEngine":
        """
        Move engine tensors to (device, dtype). Adapters are validated to match.
        """
        device = device or self.device
        dtype = dtype or self.compute_dtype
        self.W = self.W.to(device=device, dtype=dtype, non_blocking=True).contiguous()
        if self.bias is not None:
            self.bias = self.bias.to(device=device, dtype=dtype, non_blocking=True).contiguous()
        self.device = device
        self.compute_dtype = dtype
        # Optional strict check that registry adapters already match the engine placement.
        with self.reg._lock:
            for k, a in self.reg._map.items():
                if a.A.device != device or a.B.device != device:
                    self.reg._map[k] = a.to(device=device, dtype=dtype)
        return self

    # State helpers (optional, for checkpoints)
    def state_dict(self) -> Dict[str, torch.Tensor]:
        sd = {"W": self.W, "compute_dtype": torch.tensor([self._dtype_code(self.compute_dtype)], dtype=torch.int32)}
        if self.bias is not None:
            sd["bias"] = self.bias
        return sd

    def load_state_dict(self, sd: Dict[str, torch.Tensor]) -> None:
        self.W = sd["W"].contiguous()
        self.device = self.W.device
        self.compute_dtype = self._dtype_from_code(int(sd.get("compute_dtype", torch.tensor([self._dtype_code(self.W.dtype)])).item()))
        self.bias = sd.get("bias", None)
        self._check_bias()

    @staticmethod
    def _dtype_code(dt: torch.dtype) -> int:
        mapping = {
            torch.float16: 1, torch.bfloat16: 2, torch.float32: 3,
            torch.float64: 4, torch.int8: 5, torch.int32: 6,
        }
        return mapping.get(dt, 0)

    @staticmethod
    def _dtype_from_code(code: int) -> torch.dtype:
        reverse = {
            1: torch.float16, 2: torch.bfloat16, 3: torch.float32,
            4: torch.float64, 5: torch.int8, 6: torch.int32,
        }
        return reverse.get(code, torch.float32)


# --------------------------- Integration helpers ---------------------------

def build_engine_from_linear(
    base_linear: torch.nn.Linear,
    *,
    registry: Optional[SGMVRegistry] = None,
    compute_dtype: Optional[torch.dtype] = None,
) -> SGMVEngine:
    """
    Convenience: create an SGMVEngine from a torch.nn.Linear layer (weight, bias).
    """
    W = base_linear.weight  # [O, I]
    b = base_linear.bias
    eng = SGMVEngine(W, bias=b, registry=registry, compute_dtype=compute_dtype)
    return eng


def example_scheduler_hook(
    prompts: List[str],
    adapter_ids: Sequence[Optional[str]],
    engine: SGMVEngine,
    embedder: "callable",
) -> torch.Tensor:
    """
    Example (pseudo) hook for a scheduler: given prompts and adapter_ids,
    1) embed prompts as X [B, I] by calling 'embedder'
    2) compute outputs via SGMVEngine in one fused pass
    This illustrates how to call SGMV without changing upstream grouping.

    NOTE: This is a pure example; production code should integrate in the decode path.
    """
    X = embedder(prompts)  # returns [B, I] tensor on the right device
    y = engine.forward(X, adapter_ids)
    return y


# --------------------------- Smoke test ---------------------------

def _smoke_test(device: Optional[str] = None) -> Tuple[bool, str]:
    """
    Quick self-test validating correctness vs naive per-sample LoRA.
    """
    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(0)
    B, I, O, r = 7, 16, 13, 4
    W = torch.randn(O, I, device=dev, dtype=torch.float16)
    b = torch.randn(O, device=dev, dtype=torch.float16)
    X = torch.randn(B, I, device=dev, dtype=torch.float16)

    # Two adapters
    A1 = torch.randn(r, I, device=dev, dtype=torch.float16)
    B1 = torch.randn(O, r, device=dev, dtype=torch.float16)
    A2 = torch.randn(r, I, device=dev, dtype=torch.float16)
    B2 = torch.randn(O, r, device=dev, dtype=torch.float16)

    reg = SGMVRegistry()
    eng = SGMVEngine(W, b, reg, compute_dtype=torch.float16)
    eng.register_adapter("a1", A1, B1, alpha=8.0)
    eng.register_adapter("a2", A2, B2, alpha=8.0)

    # Random adapter assignments with some None (base only)
    ids = ["a1", None, "a2", "a1", "a2", None, "a2"]

    # Engine result
    y = eng.forward(X, ids)

    # Naive reference
    y_ref = X @ W.t() + b
    scale1 = 8.0 / r
    scale2 = 8.0 / r
    for i, aid in enumerate(ids):
        if aid == "a1":
            y_ref[i] = y_ref[i] + scale1 * ((X[i] @ A1.t()) @ B1.t())
        elif aid == "a2":
            y_ref[i] = y_ref[i] + scale2 * ((X[i] @ A2.t()) @ B2.t())
        else:
            pass

    err = (y - y_ref).abs().max().item()
    ok = err < 2e-2  # fp16 tolerance
    return ok, f"max_abs_err={err:.3e} device={dev}"


if __name__ == "__main__":  # pragma: no cover
    ok, msg = _smoke_test()
    print("sgmv smoke:", ok, msg)
