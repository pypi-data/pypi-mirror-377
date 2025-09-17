# skote/runtime/generate.py
"""
Skotergy generator — single-process, multi-GPU auto-sharding first (latency-safe).

What this version guarantees
----------------------------
1) HuggingFace load:
   - Multi-GPU (>=2 visible) -> prefer single-process with device_map="auto".
   - Single-GPU -> device_map="cuda" / "xpu" / "mps" (whichever is available).
   - CPU-only -> no device_map.
   - Env override: HF_DEVICE_MAP=auto|cuda|xpu|mps|cpu.
   - Uses 'dtype' (new API); auto-fallback to 'torch_dtype' for older Transformers.

2) Latency lock (strict single-device decode/KV closure):
   - If SKOTE_LATENCY_MODE=1, force a single-device placement (cuda/xpu/mps),
     never cross devices inside the decode loop; allow SKOTE_PRIMARY_DEVICE
     to pin inputs/KV to e.g. "cuda:0".

3) Never accidentally trigger custom distributed launcher:
   - Default: DO NOT call launcher; rely on single-process + HF auto-shard.
   - Only if you EXPLICITLY set --use-launcher or SKOTE_USE_LAUNCHER=1,
     we will attempt launcher; signature-safe, always fallback to single-process.

4) Mixed device maps (cpu/xpu/mps + cuda) are safe:
   - Inputs are sent to a robustly chosen "primary" device:
     SKOTE_PRIMARY_DEVICE > hf_device_map (prefer CUDA/XPU) > first param device
     > accel default; handles '0'/'cuda:0' etc.

5) Tokenizer safety:
   - Ensure pad_token; left padding; sync config.pad_token_id and resize
     embeddings if a new pad token is added.

Environment knobs
-----------------
- HF_DTYPE=auto|fp32|bf16|fp16        : dtype hint (default: bf16 in CLI)
- HF_DEVICE_MAP=auto|cuda|xpu|mps|cpu : optional override for device_map
- SKOTE_LATENCY_MODE=0/1              : 1 => force single device (decode/KV closure)
- SKOTE_PRIMARY_DEVICE="cuda:0"       : pin inputs/KV device when sharded
- SKOTE_USE_LAUNCHER=0/1              : opt-in to use custom launcher (default 0)
- SKOTE_MULTI_DISABLE=0/1             : hard-disable multi even if GPUs>1 (default 0)
"""

from __future__ import annotations
import argparse
import os
import sys
import inspect
from typing import Any, Dict, List, Optional, Tuple

# --- Torch (optional CUDA) --------------------------------------------------------
try:
    import torch
except Exception:
    torch = None  # type: ignore

# --- tolerant imports: prefer skote.*, fallback to skotergy.* ---------------------
def _import_decode_adapter():
    try:
        from skote.runtime.decode_graph_adapter import GraphDecodeAdapter  # type: ignore
        return GraphDecodeAdapter
    except Exception:
        from skotergy.runtime.decode_graph_adapter import GraphDecodeAdapter  # type: ignore
        return GraphDecodeAdapter

GraphDecodeAdapter = _import_decode_adapter()

def _import_launcher():
    mod = None
    try:
        from skote.distributed import launcher as mod  # type: ignore
    except Exception:
        try:
            from skotergy.distributed import launcher as mod  # type: ignore
        except Exception:
            mod = None
    return mod

def _import_router():
    mod = None
    try:
        from skote.runtime import router as mod  # type: ignore
    except Exception:
        try:
            from skotergy.runtime import router as mod  # type: ignore
        except Exception:
            mod = None
    return mod

# ---------------------------- Device helpers --------------------------------------
def _visible_cuda_devices() -> int:
    if torch is None:
        return 0
    try:
        return torch.cuda.device_count() if torch.cuda.is_available() else 0
    except Exception:
        return 0

def _resolve_accel_backend() -> Tuple[str, int]:
    """Return (backend, count) among cuda/xpu/mps/cpu."""
    if torch is None:
        return "cpu", 0
    try:
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            return "cuda", torch.cuda.device_count()
        if hasattr(torch, "xpu") and getattr(torch.xpu, "is_available", lambda: False)():
            try:
                cnt = int(getattr(torch.xpu, "device_count", lambda: 1)())
            except Exception:
                cnt = 1
            return "xpu", max(1, cnt)
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps", 1
    except Exception:
        pass
    return "cpu", 0

def _normalize_device(dev_any) -> "torch.device":
    """Normalize int/'0'/'cuda:0'/torch.device -> torch.device, preferring current accel backend."""
    if torch is None:
        raise RuntimeError("Torch not available")
    # torch.device -> as-is
    if hasattr(dev_any, "type"):
        return dev_any  # type: ignore
    base, cnt = _resolve_accel_backend()
    s = str(dev_any).strip().lower()
    # explicit kinds
    if s in ("cuda", "xpu"):
        return torch.device(f"{s}:0") if cnt > 0 else torch.device("cpu")
    if s in ("mps", "cpu"):
        return torch.device(s)
    # with index
    if ":" in s:
        t, idx = s.split(":", 1)
        if t in ("cuda", "xpu") and idx.isdigit():
            return torch.device(f"{t}:{int(idx)}")
        if t in ("mps", "cpu"):
            return torch.device(t)
    # pure index
    if s.isdigit():
        if base in ("cuda", "xpu") and cnt > 0:
            return torch.device(f"{base}:{int(s)}")
        return torch.device("cpu")
    # fallback
    if base in ("cuda", "xpu") and cnt > 0:
        return torch.device(f"{base}:0")
    return torch.device("cpu")

def _primary_device_for_inputs(mod) -> "torch.device":
    """
    Choose a stable device to place inputs (and KV if applicable) when the model may be sharded.
    Priority:
      0) SKOTE_PRIMARY_DEVICE env (e.g., "cuda:0")
      1) hf_device_map -> any 'embed' layer's device or the first CUDA/XPU;
      2) first parameter's device;
      3) accel default (cuda:0/xpu:0) else cpu.
    """
    if torch is None:
        raise RuntimeError("Torch not available")

    # 0) explicit env pin
    prefer = os.environ.get("SKOTE_PRIMARY_DEVICE", "").strip()
    if prefer:
        try:
            return _normalize_device(prefer)
        except Exception:
            pass

    # 1) from device_map
    try:
        dmap = getattr(mod, "hf_device_map", None)
        if isinstance(dmap, dict) and dmap:
            embed_keys = [k for k in dmap.keys() if "embed" in k.lower()]
            candidates = [dmap[k] for k in embed_keys] if embed_keys else list(dmap.values())
            devs = []
            for v in candidates:
                try:
                    devs.append(_normalize_device(v))
                except Exception:
                    pass
            if devs:
                for dv in devs:
                    if dv.type in ("cuda", "xpu"):
                        return dv
                for dv in devs:
                    if dv.type == "mps":
                        return dv
                return devs[0]
    except Exception:
        pass

    # 2) parameter device
    try:
        p = next(mod.parameters())
        return _normalize_device(getattr(p, "device", None))
    except Exception:
        base, cnt = _resolve_accel_backend()
        if base in ("cuda", "xpu") and cnt > 0:
            return torch.device(f"{base}:0")
        return torch.device("cpu")

# ---------------------------- HF loader helpers -----------------------------------
def _hf_device_map_for_env(ndev: int) -> Optional[str]:
    """
    Decide device_map based on env + visible devices.
    Env override: HF_DEVICE_MAP=auto|cuda|xpu|mps|cpu.
    If SKOTE_LATENCY_MODE=1: force single device (cuda/xpu/mps) else None (cpu).
    """
    override = os.environ.get("HF_DEVICE_MAP", "").strip().lower()
    if override in ("auto", "cuda", "xpu", "mps", "cpu"):
        return override

    backend, cnt = _resolve_accel_backend()

    # Latency lock: force single-device closure for decode/KV
    if os.environ.get("SKOTE_LATENCY_MODE", "0") == "1":
        return backend if backend in ("cuda", "xpu", "mps") else None

    if backend in ("cuda", "xpu"):
        return "auto" if ndev > 1 else backend
    if backend == "mps":
        return "mps"
    return None  # CPU

def _dtype_from_str(dtype_str: str):
    if torch is None:
        return None
    s = (dtype_str or "auto").lower()
    if s == "fp32":
        return torch.float32
    if s in ("bf16", "bfloat16"):
        return torch.bfloat16
    if s in ("fp16", "float16", "half"):
        return torch.float16
    return None  # auto

def _load_hf(model_id: Optional[str], local_dir: Optional[str], dtype_str: str):
    """
    Load tokenizer + model with safe defaults and compatibility:
      - pad_token ensured; left padding; config.pad_token_id synced.
      - device_map auto resolution (with env override & latency lock).
      - 'dtype' first; fallback to 'torch_dtype' for older Transformers.
      - Robust fallback if 'auto' fails (no accelerate / OOM).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    repo_or_path = local_dir if local_dir else model_id
    if not repo_or_path:
        raise ValueError("Either --model-id or --local-dir must be provided.")

    # Tokenizer
    tok = AutoTokenizer.from_pretrained(repo_or_path, local_files_only=bool(local_dir))

    # Ensure pad token & left padding
    added_pad = False
    if tok.pad_token is None:
        if tok.eos_token is not None:
            tok.pad_token = tok.eos_token
        else:
            tok.add_special_tokens({"pad_token": "<|pad|>"})
            added_pad = True
    try:
        tok.padding_side = "left"
    except Exception:
        pass

    # Device map & dtype
    ndev = _visible_cuda_devices()
    device_map = _hf_device_map_for_env(ndev)
    target_dtype = _dtype_from_str(dtype_str)

    # Build kwargs with signature-aware dtype key
    sig = inspect.signature(AutoModelForCausalLM.from_pretrained)
    def _kw(base_map):
        kw = dict(local_files_only=bool(local_dir), trust_remote_code=True)
        if base_map is not None:
            kw["device_map"] = base_map
        if target_dtype is not None:
            if "dtype" in sig.parameters:
                kw["dtype"] = target_dtype              # prefer new API
            else:
                kw["torch_dtype"] = target_dtype        # fallback for older transformers
        return kw

    # Try primary load
    try:
        mod = AutoModelForCausalLM.from_pretrained(repo_or_path, **_kw(device_map))
    except Exception as e_first:
        # Fallback path: prefer single-device accel; last resort CPU
        backend, cnt = _resolve_accel_backend()
        fallback_map = backend if backend in ("cuda", "xpu", "mps") else None
        if device_map == "auto" and backend in ("cuda", "xpu") and cnt > 0:
            fallback_map = backend
        try:
            mod = AutoModelForCausalLM.from_pretrained(repo_or_path, **_kw(fallback_map))
            print(f"[generate] HF load fallback from device_map={device_map!r} -> {fallback_map!r} due to: {type(e_first).__name__}: {e_first}")
        except Exception as e_second:
            raise RuntimeError(
                f"Failed to load model with device_map={device_map!r} and fallback={fallback_map!r}.\n"
                f"First error: {e_first}\nSecond error: {e_second}"
            ) from e_second

    mod.eval()

    # Sync config + embeddings if we added a pad token
    try:
        mod.config.pad_token_id = tok.pad_token_id
        if added_pad:
            mod.resize_token_embeddings(len(tok))
    except Exception:
        pass

    return tok, mod

# ------------------------------ small utils ---------------------------------------
def _batch_tokenize(tok, prompts: List[str], device: "torch.device") -> "torch.Tensor":
    enc = tok(prompts, return_tensors="pt", padding=True, truncation=True)
    input_ids = enc["input_ids"].to(device, non_blocking=True)
    return input_ids

def _rank_env_present() -> bool:
    # Detect torchrun/torch.distributed launch context
    for k in ("RANK", "WORLD_SIZE", "LOCAL_RANK"):
        if os.environ.get(k) is not None:
            return True
    return False

# ---------------------------- HF decode wrapper -----------------------------------
class HFDecodeWrapper:
    """
    Minimal wrapper exposing decode_step() AND graph helpers so that
    decode_graph_adapter can run with correct semantics.

    NOTE: With device_map="auto" the model is sharded; feeding inputs on a
    primary device (prefer CUDA/XPU) is sufficient; Accelerate dispatches internally.
    """

    def __init__(self, mod, tok):
        self.mod = mod
        self.tok = tok
        self.pad_id = int(tok.pad_token_id)
        self._device = _primary_device_for_inputs(mod)

    @property
    def device(self) -> "torch.device":
        return self._device

    # --------- graph helpers (optional) ---------
    def alloc_decode_inputs(self, bucket: int):
        xbuf = torch.empty((1, 1), dtype=torch.long, device=self.device)
        kv_buf = torch.full((1, int(bucket)), fill_value=self.pad_id, dtype=torch.long, device=self.device)
        am_buf = torch.zeros_like(kv_buf, dtype=torch.long, device=self.device)
        return xbuf, (kv_buf, am_buf)

    def update_decode_kv(self, rec_kv: Any, new_seq: "torch.Tensor") -> None:
        kv_buf, am_buf = rec_kv if isinstance(rec_kv, (tuple, list)) else (rec_kv, None)
        bucket = kv_buf.size(1)
        T = new_seq.size(1)
        kv_buf.fill_(self.pad_id)
        if T >= bucket:
            kv_buf[:, :] = new_seq[:, -bucket:]
        else:
            kv_buf[:, -T:] = new_seq
        if am_buf is not None:
            am_buf.copy_((kv_buf != self.pad_id).to(dtype=torch.long, device=kv_buf.device), non_blocking=True)

    def update_decode_inputs(self, xbuf: "torch.Tensor", token_ids: "torch.Tensor") -> None:
        xbuf.copy_(token_ids[:, -1:].to(xbuf.device, non_blocking=True))

    # ---------------- core step ----------------
    def decode_step(self, x_last_tok: "torch.Tensor", kv: Optional[Any] = None) -> "torch.Tensor":
        with torch.no_grad():
            if isinstance(kv, (tuple, list)) and len(kv) == 2:
                kv_buf, am_buf = kv
                out = self.mod(input_ids=kv_buf, attention_mask=am_buf)
                return out.logits
            if isinstance(kv, torch.Tensor):
                attn = (kv != self.pad_id).to(dtype=torch.long, device=kv.device)
                out = self.mod(input_ids=kv, attention_mask=attn)
                return out.logits
            out = self.mod(input_ids=x_last_tok)
            return out.logits

# ------------------------------ single-process run --------------------------------
def _run_single(args: argparse.Namespace) -> int:
    tok, mod = _load_hf(args.model_id, args.local_dir, args.dtype)
    device = _primary_device_for_inputs(mod)

    # Prompts
    prompts: List[str] = list(args.prompt or [])
    if args.prompts_file:
        with open(args.prompts_file, "r", encoding="utf-8") as f:
            for line in f:
                s = line.rstrip("\n")
                if s:
                    prompts.append(s)
    if not prompts:
        prompts = ["Hello from Skotergy."]

    # Tokenize (demo graph path supports B=1)
    input_ids = _batch_tokenize(tok, prompts, device=device)

    # Wrap & decode (graph-preferred, eager-safe)
    wrapper = HFDecodeWrapper(mod, tok)
    adapter = GraphDecodeAdapter(model=wrapper, tok=tok, eos_token_id=getattr(tok, "eos_token_id", None))

    out = adapter.generate(
        input_ids=input_ids[:1],  # B=1 for decode graph demo
        max_new_tokens=int(args.max_new_tokens),
        greedy=bool(args.greedy),
        temperature=None if args.greedy else args.temperature,
        top_p=None if args.greedy else args.top_p,
        return_text=(not args.no_text),
    )

    # Print results
    ids = out["input_ids"].detach().cpu()
    texts = out.get("text", None)
    for i in range(ids.shape[0]):
        print("=" * 80)
        print(f"[sample {i}] token_ids: {ids[i].tolist()}")
        if texts:
            print(f"[sample {i}] text: {texts[i]}")
    return 0

# ------------------------------ optional launcher path ----------------------------
def _handoff_multi(args: argparse.Namespace) -> int:
    """
    Only used when explicitly enabled. We never pass argparse.Namespace as a target.
    """
    launcher = _import_launcher()
    router_mod = _import_router()

    # Already under torchrun/torch.distributed? Just run single-process logic once.
    if _rank_env_present():
        try:
            # If router exposes a callable entrypoint without args, use it; else fall back.
            for fname in ("main", "serve", "entrypoint", "run"):
                if router_mod is not None and hasattr(router_mod, fname):
                    fn = getattr(router_mod, fname)
                    if callable(fn):
                        try:
                            return int(fn(args))  # type: ignore
                        except TypeError:
                            return int(fn())  # type: ignore
            return _run_single(args)
        except Exception:
            return _run_single(args)

    if launcher is None:
        print("[generate] Launcher not available; falling back to single-process.")
        return _run_single(args)

    # Prefer a 'launch(target=...)' API if present; provide a callable target.
    try:
        if hasattr(launcher, "launch"):
            fn = getattr(launcher, "launch")
            sig = inspect.signature(fn)
            if "target" in sig.parameters:
                return int(fn(target=lambda: _run_single(args)))  # type: ignore
            return int(fn())  # type: ignore
        # Fallback to a dedicated entrypoint if it exists (no Namespace as target!)
        for fname in ("launch_generate", "entrypoint", "main"):
            if hasattr(launcher, fname):
                lfn = getattr(launcher, fname)
                try:
                    return int(lfn())  # type: ignore
                except TypeError:
                    return int(lfn(target=lambda: _run_single(args)))  # type: ignore
    except Exception as e:
        print(f"[generate] Launcher failed ({type(e).__name__}: {e}); falling back to single-process.")
        return _run_single(args)

    print("[generate] No usable launcher API; falling back to single-process.")
    return _run_single(args)

# ----------------------------------- CLI ------------------------------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Skotergy generator (single-process with HF auto-sharding, latency-safe)")
    ap.add_argument("--model-id", type=str, default=os.environ.get("MODEL_ID", None), help="HF repo id")
    ap.add_argument("--local-dir", type=str, default=os.environ.get("MODEL_DIR", None), help="Local model dir")
    ap.add_argument("--dtype", type=str, default=os.environ.get("HF_DTYPE", "bf16"),
                    choices=["auto", "fp32", "bf16", "fp16"])
    ap.add_argument("--prompt", type=str, action="append", default=[], help="Prompt (repeatable)")
    ap.add_argument("--prompts-file", type=str, default=None, help="File with one prompt per line")
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--greedy", action="store_true", help="Greedy decoding (default)")
    ap.add_argument("--temperature", type=float, default=None, help="Sampling temperature (ignored if --greedy)")
    ap.add_argument("--top-p", type=float, default=None, help="Top-p nucleus sampling (ignored if --greedy)")
    ap.add_argument("--no-text", action="store_true", help="Do not decode text, return ids only")
    ap.add_argument("--use-launcher", action="store_true",
                    help="EXPLICITLY use custom launcher (default off).")
    return ap.parse_args()

def _should_use_launcher(args: argparse.Namespace) -> bool:
    if os.environ.get("SKOTE_MULTI_DISABLE", "0").strip() in ("1", "true", "True"):
        return False
    if os.environ.get("SKOTE_USE_LAUNCHER", "0").strip() in ("1", "true", "True"):
        return True
    if getattr(args, "use-launcher", False) or getattr(args, "use_launcher", False):
        return True
    return False

def main() -> int:
    args = parse_args()

    # If explicitly asked to use launcher and GPUs > 1, try launcher; otherwise single-process path.
    ndev = _visible_cuda_devices()
    if _should_use_launcher(args) and ndev > 1:
        return _handoff_multi(args)

    # Single-process fast path (also covers single-GPU/CPU/MPS/XPU)
    return _run_single(args)

if __name__ == "__main__":
    sys.exit(main())
