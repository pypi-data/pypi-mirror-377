# skote/eval/runner.py
"""
Skotergy Runner (graphs-ready, PKV-first, truthful metrics)

What this version guarantees
----------------------------
1) Latency lock mode:
   - SKOTE_LATENCY_MODE=1 -> force single-device placement for decode loop,
     no step-internal cross-device hops; SKOTE_PRIMARY_DEVICE can pin
     inputs/KV to e.g. "cuda:0"; HF_DEVICE_MAP env can still override.
2) Robust device_map selection with env overrides; safe dtype usage
   (prefers 'dtype', falls back to 'torch_dtype' on older Transformers).
3) Triton patches enabled only on safe pure-CUDA placement and when not
   disabled via SKOTE_TRITON_PATCH/SKOTE_DISABLE_TRITON; otherwise auto-off.
4) If --graphs (or SKOTE_GRAPHS=1) is set, we materialize capture policy
   (whitelist/min_bucket), and run AOT prefill capture to avoid online recapture.
5) Baseline path stays apples-to-apples for timing (no graphs/UPM; manual metrics).
6) Timing defaults to synchronous for truthful p50/p95; set SKOTE_EVAL_SYNC=0
   to exercise the async scheduler path if desired.

Env knobs (common)
------------------
- HF_DEVICE_MAP = auto|cuda|xpu|mps|cpu        (explicit override)
- SKOTE_LATENCY_MODE = 0/1                     (1 = latency lock, force single device)
- SKOTE_PRIMARY_DEVICE = "cuda:0"              (pin inputs/KV device)
- TRANSFORMERS_ATTENTION_IMPLEMENTATION = flash_attention_2 | sdpa | eager
- SKOTE_TRITON_PATCH=0/1, SKOTE_DISABLE_TRITON=0/1
- SKOTE_GRAPHS = 0/1
- SKOTE_MIN_BUCKET_CAPTURE = int (e.g., 256/512/1024/2048/4096)
- SKOTE_GRAPH_BUCKETS_CAPTURE = "256,512,1024,2048,4096"
- SKOTE_EAGER_SMALL_BUCKETS = 0/1
- SKOTE_EVAL_SYNC = 0/1  (1 = sync timing; default 1)
"""

from __future__ import annotations

import os
import time
import json
import argparse
import inspect
from typing import Any, Dict, List, Callable, Optional

from skote import SkoteSession, SkoteConfig, get_config, get_logger
from skote.eval.scenarios import default_scenarios, get_scenario, ScenarioSpec

log = get_logger("skotergy.runner")


# --------------------------- Device helpers (FIXED & ROBUST) ---------------------------

def _resolve_accel_device() -> tuple[str, int]:
    """Return (device_type:str, count:int) among cuda/xpu/mps/cpu."""
    try:
        import torch
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            return "cuda", torch.cuda.device_count()
        if hasattr(torch, "xpu") and getattr(torch.xpu, "is_available", lambda: False)():
            try:
                cnt = getattr(torch.xpu, "device_count", lambda: 1)()
            except Exception:
                cnt = 1
            return "xpu", max(1, int(cnt))
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps", 1
    except Exception:
        pass
    return "cpu", 0


def _normalize_device(dev_any):
    """Normalize various forms (int/str/torch.device) into a concrete torch.device."""
    import torch
    base, cnt = _resolve_accel_device()  # 'cuda'|'xpu'|'mps'|'cpu', count

    if hasattr(dev_any, "type"):  # torch.device
        return dev_any

    s = str(dev_any).strip().lower()
    if s in ("cuda", "xpu"):
        return torch.device(f"{s}:0") if cnt > 0 else torch.device("cpu")
    if s in ("mps", "cpu"):
        return torch.device(s)

    if ":" in s:
        t, idx = s.split(":", 1)
        if t in ("cuda", "xpu") and idx.isdigit():
            return torch.device(f"{t}:{int(idx)}")
        if t in ("mps", "cpu"):
            return torch.device(t)

    if s.isdigit():  # pure index on current accel backend
        if base in ("cuda", "xpu") and cnt > 0:
            return torch.device(f"{base}:{int(s)}")
        return torch.device("cpu")

    return torch.device("cpu")


def _hf_device_map_for_env() -> Optional[str]:
    """
    Decide device_map argument for HF from_pretrained with env-aware latency lock:
      - HF_DEVICE_MAP env overrides when present.
      - SKOTE_LATENCY_MODE=1 -> force single device (cuda/xpu/mps) else None (cpu).
      - Else: multi-device -> "auto"; single-device -> "cuda"/"xpu"/"mps"; cpu -> None.
    """
    override = os.environ.get("HF_DEVICE_MAP", "").strip().lower()
    if override in ("auto", "cuda", "xpu", "mps", "cpu"):
        return override or None

    dev, cnt = _resolve_accel_device()
    if os.environ.get("SKOTE_LATENCY_MODE", "0") == "1":
        return dev if dev in ("cuda", "xpu", "mps") else None

    if dev == "cpu":
        return None
    if cnt and cnt > 1:
        return "auto"
    return dev


def _primary_device_for_inputs(mod):
    """
    Choose concrete torch.device for inputs/kv.
    Priority:
      1) SKOTE_PRIMARY_DEVICE env (e.g., "cuda:0")
      2) hf_device_map (first CUDA/XPU if present; '0' -> 'cuda:0')
      3) first parameter device
      4) accel default or cpu
    """
    import torch
    prefer = os.environ.get("SKOTE_PRIMARY_DEVICE", "").strip().lower()
    if prefer:
        try:
            return _normalize_device(prefer)
        except Exception:
            pass

    try:
        dmap = getattr(mod, "hf_device_map", None)
        if isinstance(dmap, dict) and dmap:
            vals = list(set(dmap.values()))
            normed = [_normalize_device(v) for v in vals]
            for dv in normed:
                if dv.type in ("cuda", "xpu"):
                    return dv
            for dv in normed:
                if dv.type == "mps":
                    return dv
            return normed[0]
    except Exception:
        pass

    try:
        p = next(mod.parameters())
        return _normalize_device(getattr(p, "device", None))
    except Exception:
        base, cnt = _resolve_accel_device()
        if base in ("cuda", "xpu") and cnt > 0:
            return torch.device(f"{base}:0")
        return torch.device("cpu")


def _dtype_from_str(dtype_str: str | None):
    import torch
    if not dtype_str:
        return torch.bfloat16
    s = dtype_str.lower()
    if s in ("bf16", "bfloat16"): return torch.bfloat16
    if s in ("fp16", "float16", "half"): return torch.float16
    if s in ("fp32", "float32", "full"): return torch.float32
    raise ValueError(f"Unsupported dtype: {dtype_str}")


def _load_hf_model(local_path: str, dtype_str: str = "bf16", trust_remote_code: bool = True):
    """
    Load HF CausalLM with device_map auto/explicit and dtype kw (fallback to torch_dtype for older versions).
    Returns (model, tokenizer, chosen_device_map_str_or_None).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dt = _dtype_from_str(dtype_str)
    device_map = _hf_device_map_for_env()

    tok = AutoTokenizer.from_pretrained(local_path, use_fast=True, trust_remote_code=trust_remote_code)
    try:
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
            tok.pad_token_id = tok.eos_token_id
    except Exception:
        pass
    tok.padding_side = "left"

    # dtype signature compatibility
    sig = inspect.signature(AutoModelForCausalLM.from_pretrained)
    kwargs = {"device_map": device_map, "trust_remote_code": trust_remote_code, "local_files_only": True}
    if "dtype" in sig.parameters:
        kwargs["dtype"] = dt             # prefer new API
    else:
        kwargs["torch_dtype"] = dt       # fallback for older transformers

    mod = AutoModelForCausalLM.from_pretrained(local_path, **kwargs)
    mod.eval()
    return mod, tok, device_map


# --------------------------- Toy model ---------------------------

class ToyModel:
    """
    Sleep-based model to simulate compute.
    time ~= a * (chars/1000) + b * (gen_tokens/100)
    Env overrides:
      SKOTE_TOY_MS_PER_1K  (default 2.0 ms per 1k chars)
      SKOTE_TOY_MS_PER_TOK (default 0.5 ms per token)
    """
    def __init__(self, ms_per_1k: float = 2.0, ms_per_tok: float = 0.5) -> None:
        self.ms_per_1k = float(os.environ.get("SKOTE_TOY_MS_PER_1K", ms_per_1k))
        self.ms_per_tok = float(os.environ.get("SKOTE_TOY_MS_PER_TOK", ms_per_tok))

    def __call__(self, prompt: str, gen_tokens: int = 0) -> str:
        import time as _t
        chars = len(prompt)
        ms = (chars / 1000.0) * self.ms_per_1k + max(0, int(gen_tokens)) * self.ms_per_tok
        _t.sleep(max(0.0, ms / 1000.0))
        return "ok"


# --------------------------- HF model (real) ---------------------------

def _ensure_local_hf_model(model_id: str, local_dir: str, auto_download: bool, token_env: str) -> str:
    """
    Ensure a HF model exists locally under local_dir.
    If auto_download is True and local_dir missing/empty, snapshot_download into it.
    """
    local_dir = os.path.abspath(local_dir)
    has_files = os.path.isdir(local_dir) and any(os.scandir(local_dir))
    if has_files:
        log.info("HF model found locally: %s", local_dir)
        return local_dir

    if not auto_download:
        raise FileNotFoundError(
            f"HF local model not found at {local_dir}. "
            f"Provide --hf-local-dir with an existing path or add --hf-auto-download."
        )

    hf_token = os.environ.get(token_env)
    if not hf_token:
        raise RuntimeError(
            f"Missing HuggingFace token in ${token_env}. "
            "Export your token (you must have accepted the model license)."
        )
    log.info("Downloading HF model '%s' to %s ...", model_id, local_dir)
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        token=hf_token,
        local_dir_use_symlinks=False,
        ignore_patterns=["*.pt.torrent"],
    )
    log.info("Download completed: %s", local_dir)
    return local_dir


class HFModel:
    """
    Minimal HF causal LM wrapper: str -> str, honoring max_new_tokens via call arg.
    Loads model from a local directory prepared by _ensure_local_hf_model.
    Exposes .tok and .mod for Scheduler/GraphMgr integration.
    """
    def __init__(self, model_dir: str, dtype: str = "bf16"):
        log.info("Loading HF model from %s (dtype=%s)", model_dir, dtype)
        self.mod, self.tok, self._devmap = _load_hf_model(model_dir, dtype_str=dtype, trust_remote_code=True)
        self.dt = _dtype_from_str(dtype)

        # Optional kernel patches (safe gating)
        try:
            want_patch = os.environ.get("SKOTE_TRITON_PATCH", "1") == "1" and os.environ.get("SKOTE_DISABLE_TRITON", "0") != "1"
            if want_patch:
                from skote.kernels.triton_ops import enable_triton_patches
                # Enable only on pure-CUDA maps (avoid CPU/MPS/XPU shards).
                dmap = getattr(self.mod, "hf_device_map", {}) or {}
                devs = {str(v).lower() for v in dmap.values()} if isinstance(dmap, dict) else set()
                mixed_or_non_cuda = (not devs) or any(d.startswith(("cpu", "mps", "xpu")) for d in devs)
                if not mixed_or_non_cuda:
                    patched = enable_triton_patches(self.mod)
                    if patched:
                        log.info("Enabled %d Triton kernel patches (e.g., RMSNorm).", patched)
                else:
                    log.info("Triton patches disabled (mixed/non-cuda device_map).")
            else:
                log.info("Triton patches disabled by env.")
        except Exception as e:
            log.warning("Kernel patching skipped: %s", e)

    def __call__(self, prompt: str, gen_tokens: int = 0) -> str:
        import torch
        with torch.no_grad():
            enc = self.tok(prompt, return_tensors="pt")
            dev = _primary_device_for_inputs(self.mod)
            input_ids = enc["input_ids"].to(dev, non_blocking=True)
            attn = enc.get("attention_mask")
            if attn is not None:
                attn = attn.to(dev, non_blocking=True)

            out = self.mod.generate(
                input_ids=input_ids,
                attention_mask=attn,
                max_new_tokens=max(1, int(gen_tokens or 1)),
                do_sample=False,
                temperature=0.0,
            )
            return self.tok.decode(out[0], skip_special_tokens=True)


# --------------------------- Graph warmup (AOT prefill) ---------------------------

def _parse_int_list(s: str) -> List[int]:
    xs: List[int] = []
    for p in s.replace(";", ",").split(","):
        p = p.strip()
        if not p:
            continue
        try:
            xs.append(int(p))
        except Exception:
            pass
    return sorted(set(xs))


def _derive_capture_buckets(graphmgr, env_buckets: Optional[str], min_bucket: int) -> List[int]:
    """
    Decide which buckets to AOT-capture for prefill:
    Priority: explicit env list -> gm.capture_whitelist (if exposed) -> gm.policy.buckets filtered by min_bucket.
    """
    if env_buckets:
        return [b for b in _parse_int_list(env_buckets) if b >= min_bucket]
    wl = getattr(graphmgr, "capture_whitelist", None)
    if isinstance(wl, list) and wl:
        return [b for b in wl if b >= min_bucket]
    pol = getattr(graphmgr, "policy", None)
    if pol and hasattr(pol, "buckets"):
        return [b for b in list(pol.buckets) if b >= min_bucket]
    return [1024, 2048, 4096, 8192]


def _aot_capture_prefill(graphmgr, hf_obj, model_id: str, *, buckets: List[int]) -> int:
    """
    Capture CUDA graphs for prefill on selected length buckets during warmup.
    Online path should only replay; this avoids recapture churn and p95 inflation.
    Returns number of captured graphs.
    """
    try:
        import torch  # noqa: F401
    except Exception:
        return 0

    tok = getattr(hf_obj, "tok", None)
    mod = getattr(hf_obj, "mod", None)
    if tok is None or mod is None:
        return 0

    try:
        from skote.runtime.graphmgr import GraphKey  # type: ignore
    except Exception:
        GraphKey = None  # type: ignore

    captured = 0
    for L in buckets:
        try:
            import torch
            pad_id = getattr(tok, "pad_token_id", None)
            if pad_id is None:
                pad_id = int(getattr(tok, "eos_token_id", 0))
            dev = _primary_device_for_inputs(mod)
            ii = torch.full((1, int(L)), int(pad_id), dtype=torch.long, device=dev)
            am = torch.ones((1, int(L)), dtype=torch.long, device=dev)

            try:
                bucket_id = graphmgr.policy.choose(int(L))[0]  # type: ignore
            except Exception:
                bucket_id = int(L)

            if GraphKey is not None:
                gk = GraphKey(model_id=model_id, backend=getattr(graphmgr, "backend", "cuda"),
                              dtype="auto", bucket=bucket_id, attn_kernel="auto", extra="")
                graph_id = gk.to_compact()
            else:
                graph_id = f"{model_id}|{getattr(graphmgr, 'backend', 'cuda')}|{bucket_id}"

            def _prefill_forward(input_ids, attention_mask=None):
                return mod.forward(input_ids=input_ids, attention_mask=attention_mask)

            if not graphmgr.replay(graph_id, ii, am):  # type: ignore
                if graphmgr.maybe_capture(graph_id, _prefill_forward, (ii,), {"attention_mask": am}, aot=True):  # type: ignore
                    captured += 1
        except Exception as e:
            log.debug("AOT prefill capture failed for L=%s: %s", L, e)
            continue
    return captured


# --------------------------- Scenario runners ---------------------------

def _tokens_in_from_batch(prompts: List[str], seq_lens: Optional[List[int]]) -> int:
    if seq_lens and len(seq_lens) == len(prompts):
        return int(sum(int(x) for x in seq_lens))
    # Fallback proxy by chars if seq_lens missing
    return int(sum(len(p) for p in prompts))


def _route_then_run_skote(
    sess: SkoteSession,
    model_fn: Callable[[str, int], Any],
    scenario: ScenarioSpec,
) -> Dict[str, Any]:
    """
    Execute a scenario with Skote features ON.

    Default: synchronous timing for truthful p50/p95.
    Set SKOTE_EVAL_SYNC=0 to use scheduler.run() path (may be optimistic if async).
    """
    # Optional: attach scheduler to graph manager if present
    if sess.scheduler and hasattr(sess.scheduler, "attach_graph_manager") and getattr(sess, "graphmgr", None):
        sess.scheduler.attach_graph_manager(sess.graphmgr)

    total_batches, total_inputs = 0, 0
    sync_mode = os.environ.get("SKOTE_EVAL_SYNC", "1") != "0" or not bool(sess.scheduler)

    for b in scenario.batches:
        gen_toks = int(b.meta.get("gen_tokens", 0))
        t0 = time.time()

        if sync_mode or not hasattr(sess, "run"):
            # Synchronous: call model_fn per prompt, collect true gen_len
            outputs: List[Dict[str, Any]] = []
            for p in b.prompts:
                o = model_fn(p, gen_toks)
                if isinstance(o, dict):
                    outputs.append(o)
                else:
                    outputs.append({"text": str(o), "gen_len": int(max(1, gen_toks))})
        else:
            # Scheduler path: we expect sess.run to return per-prompt outputs
            outs = sess.run(
                model=(lambda s, g=gen_toks: model_fn(s, g)),
                prompts=b.prompts,
                qos=b.qos,
                model_id=b.model_id,
                seq_lens=b.seq_lens,
            )
            outputs = []
            try:
                for o in (outs or []):
                    if isinstance(o, dict) and "gen_len" in o:
                        outputs.append({"text": o.get("text", ""), "gen_len": int(o["gen_len"])})
                    else:
                        outputs.append({"text": str(o), "gen_len": int(max(1, gen_toks))})
            except Exception:
                outputs = [{"text": "", "gen_len": int(max(1, gen_toks))} for _ in b.prompts]

        t1 = time.time()

        total_batches += 1
        total_inputs += len(b.prompts)

        # Metrics
        if sess.metrics:
            tokens_in = _tokens_in_from_batch(b.prompts, b.seq_lens)
            tokens_out = sum(int(x.get("gen_len", max(1, gen_toks))) for x in outputs)
            extra = {
                "latency_ms": (t1 - t0) * 1000.0,
                "lane": b.qos,
                "groups": 1,
                "backend": getattr(sess, "backend_name", "cuda") or "cuda",
                "bucket": max(b.seq_lens) if b.seq_lens else -1,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "errors": 0,
            }
            try:
                sess.metrics.record_batch(inputs=b.prompts, outputs=outputs, extra=extra)
            except Exception:
                pass

        # UPM snapshot (optional)
        if sess.upm and hasattr(sess.upm, "stats") and sess.metrics:
            try:
                sess.metrics.record_upm(sess.upm.stats())
            except Exception:
                pass

    if sess.metrics:
        try:
            sess.metrics.flush()
        except Exception:
            pass

    return {"batches": total_batches, "inputs": total_inputs}


def _route_then_run_baseline(
    sess: SkoteSession,
    model_fn: Callable[[str, int], Any],
    scenario: ScenarioSpec,
) -> Dict[str, Any]:
    """
    Execute a scenario with baseline features OFF.
    We manually measure latency and write into a new Metrics instance.
    """
    from skote.runtime.metrics import Metrics  # late import
    metrics = Metrics(get_config())

    total_batches, total_inputs = 0, 0
    gm = getattr(sess, "graphmgr", None)

    for b in scenario.batches:
        route_info = None
        if gm and hasattr(gm, "route"):
            try:
                route_info = gm.route(b.prompts, seq_lens=b.seq_lens, model_id=b.model_id)
                metrics.record_route(route_info)
            except Exception:
                route_info = None

        gen_toks = int(b.meta.get("gen_tokens", 0))
        t0 = time.time()
        # Synchronous baseline calls
        outs = [model_fn(p, gen_toks) for p in b.prompts]
        t1 = time.time()

        tokens_in = _tokens_in_from_batch(b.prompts, b.seq_lens)
        tokens_out = int(max(1, gen_toks)) * len(b.prompts)

        outputs = []
        for o in outs:
            if isinstance(o, dict):
                outputs.append(o)
            else:
                outputs.append({"text": str(o), "gen_len": int(max(1, gen_toks))})

        extra = {
            "latency_ms": (t1 - t0) * 1000.0,
            "lane": b.qos,
            "groups": 1,
            "backend": route_info.get("backend", "auto") if isinstance(route_info, dict) else "auto",
            "bucket": route_info.get("bucket", -1) if isinstance(route_info, dict) else -1,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "errors": 0,
        }
        metrics.record_batch(inputs=b.prompts, outputs=outputs, extra=extra)

        total_batches += 1
        total_inputs += len(b.prompts)

    metrics.flush()
    return {"batches": total_batches, "inputs": total_inputs}


# --------------------------- Orchestration ---------------------------

def run_experiment(
    name: str,
    scenarios: List[ScenarioSpec],
    *,
    backend: Optional[str],
    toy_ms_per_1k: float,
    toy_ms_per_tok: float,
    use_hf: bool = False,
    hf_model_id: Optional[str] = None,
    hf_local_dir: Optional[str] = None,
    hf_dtype: str = "bf16",
    hf_auto_download: bool = False,
    hf_token_env: str = "HF_TOKEN",
    warmup: int = 2,
    graphs: bool = False,
    graph_buckets: Optional[str] = None,
    min_bucket_capture: Optional[int] = None,
    eager_small_buckets: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Configure one experiment and execute scenarios.
    """
    # Materialize CLI graph-related knobs into env so downstream policy can read them.
    if graphs:
        os.environ["SKOTE_GRAPHS"] = "1"
    if graph_buckets is not None:
        os.environ["SKOTE_GRAPH_BUCKETS_CAPTURE"] = str(graph_buckets)
    if min_bucket_capture is not None:
        os.environ["SKOTE_MIN_BUCKET_CAPTURE"] = str(int(min_bucket_capture))
    if eager_small_buckets is not None:
        os.environ["SKOTE_EAGER_SMALL_BUCKETS"] = "1" if eager_small_buckets else "0"

    # Select model
    if use_hf and name == "skote":
        assert hf_model_id, "When --use-hf is set, you must pass --hf-model"
        assert hf_local_dir, "When --use-hf is set, you must pass --hf-local-dir"
        local_path = _ensure_local_hf_model(hf_model_id, hf_local_dir, hf_auto_download, hf_token_env)

        try:
            from skote.runtime.decode_graph_adapter import GraphDecodeAdapter
        except Exception:
            from skotergy.runtime.decode_graph_adapter import GraphDecodeAdapter  # type: ignore

        # ---- load with env-aware device_map and dtype kw (fallback safe) ----
        mod, tok, devmap = _load_hf_model(local_path, dtype_str=hf_dtype, trust_remote_code=True)

        # ---- Minimal decode graph hooks to allow graph path in adapter ----
        def alloc_decode_inputs(bucket: int):
            import torch as _t
            dev = _primary_device_for_inputs(mod)
            xbuf = _t.zeros((1, 1), dtype=_t.long, device=dev)
            kv_handle = getattr(mod, "past_key_values", None)
            return xbuf, kv_handle

        def update_decode_inputs(xbuf, token_ids):
            xbuf.copy_(token_ids[:, -1:].to(xbuf.device, non_blocking=True))

        def read_decode_logits(out):
            return out

        setattr(mod, "alloc_decode_inputs", alloc_decode_inputs)
        setattr(mod, "update_decode_inputs", update_decode_inputs)
        setattr(mod, "read_decode_logits", read_decode_logits)
        # ------------------------------------------------------------------

        adapter = GraphDecodeAdapter(model=mod, tok=tok, eos_token_id=getattr(tok, "eos_token_id", None), greedy_default=True)

        def model_fn(prompt: str, gen_tokens: int = 0):
            import torch
            with torch.no_grad():
                enc = tok([prompt], return_tensors="pt", padding=True, truncation=True)
                dev = _primary_device_for_inputs(mod)
                input_ids = enc["input_ids"].to(dev, non_blocking=True)

                # GraphDecodeAdapter builds attention mask internally from pad_token_id;
                # do NOT pass 'attention_mask'.
                out = adapter.generate(
                    input_ids=input_ids,
                    max_new_tokens=max(1, int(gen_tokens or 1)),
                    greedy=True,
                    stop_at_eos=True,
                    return_text=True,
                )
                seq = out.get("input_ids")
                gen_len = int(seq.shape[-1] - input_ids.shape[-1]) if hasattr(seq, "shape") else int(gen_tokens or 1)
                texts = out.get("text") or []
                text0 = texts[0] if texts else ""
                return {"text": text0, "gen_len": gen_len}

        model_id_for_graph = hf_model_id
        hf_graph_shim = type("HFShim", (object,), {"tok": tok, "mod": mod})()  # for AOT capture

    elif use_hf:
        assert hf_model_id, "When --use-hf is set, you must pass --hf-model"
        assert hf_local_dir, "When --use-hf is set, you must pass --hf-local-dir"
        local_path = _ensure_local_hf_model(hf_model_id, hf_local_dir, hf_auto_download, hf_token_env)
        model_fn: Callable[[str, int], Any] = HFModel(local_path, dtype=hf_dtype)
        model_id_for_graph = hf_model_id
        hf_graph_shim = None

    else:
        model_fn = ToyModel(ms_per_1k=toy_ms_per_1k, ms_per_tok=toy_ms_per_tok)
        model_id_for_graph = "toy"
        hf_graph_shim = None

    # Neutralize cold-start in a model-agnostic way (fair p50/p95)
    try:
        for _ in range(max(0, int(warmup))):
            _ = model_fn("warmup prompt", 1)
    except Exception:
        pass

    # Prepare a clean config per experiment
    cfg = SkoteConfig()
    cfg.backend_preference = [backend] if backend else cfg.backend_preference

    graphs_on = os.environ.get("SKOTE_GRAPHS", "0") == "1"

    if name == "baseline":
        cfg.enable_graph_bucketing = False
        cfg.enable_upm = False
        cfg.enable_scheduler = False
        cfg.metrics_enabled = False  # manual metrics path
        run_id = f"baseline-{int(time.time())}"
        os.environ["SKOTE_RUN_ID"] = run_id

    elif name == "skote":
        # Respect graphs: enable bucketing only when graphs_on
        cfg.enable_graph_bucketing = bool(graphs_on)
        cfg.enable_upm = bool(int(os.environ.get("SKOTE_UPM", "0")))  # leave to env/CLI
        cfg.enable_scheduler = True
        cfg.metrics_enabled = True
        run_id = f"skote-{int(time.time())}"
        os.environ["SKOTE_RUN_ID"] = run_id
    else:
        raise ValueError(f"unknown experiment: {name}")

    # Create a fresh session (no global singletons)
    sess = SkoteSession(config=cfg, backend_name=backend)

    # If graphs are ON and HF path is used, do AOT prefill capture on requested buckets
    if name == "skote" and use_hf and graphs_on and hf_graph_shim is not None:
        try:
            gm = getattr(sess, "graphmgr", None)
            mb = int(os.environ.get("SKOTE_MIN_BUCKET_CAPTURE", "1024"))
            buckets = _derive_capture_buckets(gm, os.environ.get("SKOTE_GRAPH_BUCKETS_CAPTURE"), mb) if gm else [1024, 2048, 4096, 8192]
            ncap = _aot_capture_prefill(gm, hf_graph_shim, model_id_for_graph, buckets=buckets) if gm else 0
            if ncap:
                log.info("AOT captured %d prefill graphs on buckets=%s.", ncap, buckets)
        except Exception as e:
            log.warning("AOT capture skipped: %s", e)

    # Run scenarios
    agg = {"experiment": name, "scenarios": {}}
    for scn in scenarios:
        if name == "skote":
            res = _route_then_run_skote(sess, model_fn, scn)
        else:
            res = _route_then_run_baseline(sess, model_fn, scn)
        agg["scenarios"][scn.name] = res

    # Summary snapshot
    if name == "skote" and sess.metrics:
        snap = sess.metrics.snapshot()
    else:
        snap = _load_snapshot_for_run_id(os.environ.get("SKOTE_RUN_ID", ""))

    agg["summary"] = snap
    return agg


def _load_snapshot_for_run_id(run_id: str) -> Dict[str, Any]:
    runs = os.path.join(os.getcwd(), "runs")
    if not run_id:
        return {}
    fname = f"snapshot-{run_id}.json"
    try:
        with open(os.path.join(runs, fname), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback: latest
        try:
            files = [f for f in os.listdir(runs) if f.startswith("snapshot-") and f.endswith(".json")]
            if files:
                latest = max(files, key=lambda n: os.path.getmtime(os.path.join(runs, n)))
                with open(os.path.join(runs, latest), "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
    return {}


# --------------------------- CLI ---------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Skotergy runner for baseline vs skote scenarios.")
    p.add_argument("--experiments", type=str, default="baseline,skote",
                   help="Comma list: baseline,skote")
    p.add_argument("--scenarios", type=str, default="all",
                   help="Comma list or 'all'. Choices: prefill_longcontext,decode_256tok,concurrency_1_4_8,multitenant_lora_mix")
    p.add_argument("--backend", type=str, default=None,
                   help="Preferred backend (e.g., cuda, rocm, level_zero, vulkan, cpu)")
    p.add_argument("--toy-ms-per-1k", type=float, default=2.0,
                   help="Toy model ms per 1k chars")
    p.add_argument("--toy-ms-per-token", type=float, default=0.5,
                   help="Toy model ms per token")

    # HF real model options
    p.add_argument("--use-hf", action="store_true",
                   help="Use a local HuggingFace model instead of the toy model")
    p.add_argument("--hf-model", type=str, default=None,
                   help="HF model repo id (e.g., meta-llama/Llama-3.1-8B-Instruct)")
    p.add_argument("--hf-local-dir", type=str, default=None,
                   help="Local directory where the model is stored (or will be downloaded)")
    p.add_argument("--hf-dtype", type=str, default="bf16", choices=["fp16", "bf16", "fp32"],
                   help="Torch dtype for loading the HF model")
    p.add_argument("--hf-auto-download", action="store_true",
                   help="Auto-download the model into --hf-local-dir if not present (requires HF token)")
    p.add_argument("--hf-token-env", type=str, default="HF_TOKEN",
                   help="Env var name that holds your HuggingFace token")

    # Graph/capture policy knobs
    p.add_argument("--graphs", action="store_true",
                   help="Enable CUDA Graphs integration (sets SKOTE_GRAPHS=1).")
    p.add_argument("--graph-buckets", type=str, default=None,
                   help="Comma-separated length buckets for capture, e.g. '256,512,1024,2048,4096'.")
    p.add_argument("--min-bucket-capture", type=int, default=None,
                   help="Minimal bucket length eligible for capture (sets SKOTE_MIN_BUCKET_CAPTURE).")
    p.add_argument("--eager-small-buckets", dest="eager_small_buckets", action="store_true",
                   help="Force eager path for buckets < min-bucket-capture (sets SKOTE_EAGER_SMALL_BUCKETS=1).")
    p.add_argument("--no-eager-small-buckets", dest="eager_small_buckets", action="store_false",
                   help="Disable eager bypass for small buckets (sets SKOTE_EAGER_SMALL_BUCKETS=0).")
    p.set_defaults(eager_small_buckets=None)

    p.add_argument("--warmup", type=int, default=2,
                   help="Warmup calls per experiment to neutralize cold-start")
    return p.parse_args()


def _build_scenarios(sel: str) -> List[ScenarioSpec]:
    if sel.strip().lower() == "all":
        return default_scenarios()
    out: List[ScenarioSpec] = []
    for name in [x.strip() for x in sel.split(",") if x.strip()]:
        out.append(get_scenario(name))
    return out


def _print_summary(results: List[Dict[str, Any]]) -> None:
    print("\n=== Summary (baseline vs skote) ===")
    for r in results:
        name = r.get("experiment", "?")
        snap = r.get("summary", {})
        p50 = snap.get("p50_ms", 0.0)
        p95 = snap.get("p95_ms", 0.0)
        req = snap.get("requests", 0)
        err = snap.get("errors", 0)
        print(f"- {name:8s}: requests={req:5d}  p50={p50:7.1f} ms  p95={p95:7.1f} ms  errors={err}")

    print("\nPer-scenario batches/inputs:")
    for r in results:
        print(f"  [{r['experiment']}]")
        for scn, val in r["scenarios"].items():
            print(f"    {scn:22s}  batches={val['batches']:3d} inputs={val['inputs']:4d}")


def main() -> None:
    args = _parse_args()
    scenarios = _build_scenarios(args.scenarios)

    results: List[Dict[str, Any]] = []
    for exp in [x.strip() for x in args.experiments.split(",") if x.strip()]:
        res = run_experiment(
            exp,
            scenarios,
            backend=args.backend,
            toy_ms_per_1k=args.toy_ms_per_1k,
            toy_ms_per_tok=args.toy_ms_per_token,
            use_hf=args.use_hf,
            hf_model_id=args.hf_model,
            hf_local_dir=args.hf_local_dir,
            hf_dtype=args.hf_dtype,
            hf_auto_download=args.hf_auto_download,
            hf_token_env=args.hf_token_env,
            warmup=args.warmup,
            graphs=args.graphs,
            graph_buckets=args.graph_buckets,
            min_bucket_capture=args.min_bucket_capture,
            eager_small_buckets=args.eager_small_buckets,
        )
        results.append(res)

    _print_summary(results)


if __name__ == "__main__":  # pragma: no cover
    main()
