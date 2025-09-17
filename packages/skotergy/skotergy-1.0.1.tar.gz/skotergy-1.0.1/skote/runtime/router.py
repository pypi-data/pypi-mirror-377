# skote/runtime/router.py
# -*- coding: utf-8 -*-
"""
Skotergy Request-Level Router (single/multi-device, latency-first)

What this router does
---------------------
- Single-GPU: keep decode+KV on the single device (latency lock).
- Multi-GPU: request-level parallelism (1 request per GPU by default),
  NOT layer-wise sharding; this avoids step-internal cross-device sync.
- Length-aware dispatch: pick the worker whose recent average prompt length
  is closest to the incoming request to reduce padding and graph churn.
- Optional micro-batching window (disabled by default) to improve throughput
  without hurting p50; can be enabled via env.
- Safe HuggingFace loading:
  - device_map = "cuda:N" / "xpu:N" / "mps" / "cpu"
  - uses `dtype` kw (falls back to `torch_dtype` on older Transformers)
  - tokenizer pad_token ensured; left padding enabled; embedding resized when needed
- Warmup: per-device cold-start neutralization + optional AOT-ish bucket warmup.

Environment knobs
-----------------
- MODEL_DIR (or pass local_dir to Router)
- HF_DTYPE = bf16|fp16|fp32 (default bf16)
- SKOTE_LATENCY_MODE = 0/1 (1 = prefer single-device closure)
- SKOTE_PRIMARY_DEVICE = "cuda:0" (pin inputs on that device if present)
- SKOTE_ROUTER_POLICY = rr|sq|len (round-robin / shortest-queue / length-aware; default len)
- SKOTE_ROUTER_MAX_CONCURRENCY = int per device (default 1; >1 may fight for streams)
- SKOTE_ROUTER_BATCH_MS = int micro-batch window in ms (default 0 disables)
- SKOTE_GRAPH_BUCKETS_CAPTURE = "128,256,512,1024,2048,4096" (optional warm buckets)
- SKOTE_MIN_BUCKET_CAPTURE = int minimal bucket length to warm (default 256)
- HF_DEVICE_MAP can still force a device kind (cuda|xpu|mps|cpu) but not the index.
"""

from __future__ import annotations
import os
import time
import threading
import queue
import inspect
from typing import List, Optional, Tuple, Any, Dict

try:
    import torch
except Exception as e:  # pragma: no cover
    torch = None  # type: ignore

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
except Exception as e:  # pragma: no cover
    raise RuntimeError("transformers is required for router") from e


# --------------------------- helpers: devices, dtype, map ---------------------------

def _accel_backend() -> Tuple[str, int]:
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


def _normalize_device(s: str) -> "torch.device":
    base, cnt = _accel_backend()
    s = (s or "").strip().lower()
    if ":" in s:
        t, idx = s.split(":", 1)
        if t in ("cuda", "xpu") and idx.isdigit():
            return torch.device(f"{t}:{int(idx)}")
        if t in ("mps", "cpu"):
            return torch.device(t)
    if s in ("cuda", "xpu"):
        return torch.device(f"{s}:0") if cnt > 0 else torch.device("cpu")
    if s in ("mps", "cpu"):
        return torch.device(s)
    if s.isdigit():
        if base in ("cuda", "xpu") and cnt > 0:
            return torch.device(f"{base}:{int(s)}")
        return torch.device("cpu")
    if base in ("cuda", "xpu") and cnt > 0:
        return torch.device(f"{base}:0")
    return torch.device("cpu")


def _dtype_from_env() -> "torch.dtype":
    if torch is None:
        raise RuntimeError("Torch not available")
    s = os.environ.get("HF_DTYPE", "bf16").strip().lower()
    if s in ("bf16", "bfloat16"):
        return torch.bfloat16
    if s in ("fp16", "float16", "half"):
        return torch.float16
    if s in ("fp32", "float32", "full"):
        return torch.float32
    return torch.bfloat16


def _device_map_for_worker(dev: "torch.device") -> Optional[str]:
    # explicit string acceptable for HF from_pretrained
    if dev.type in ("cuda", "xpu"):
        return f"{dev.type}:{dev.index or 0}"
    if dev.type in ("mps", "cpu"):
        return dev.type
    return None


def _visible_devices() -> List["torch.device"]:
    base, cnt = _accel_backend()
    vis_env = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    out: List["torch.device"] = []
    if base in ("cuda", "xpu") and cnt > 0:
        try:
            if vis_env:
                parts = [p.strip() for p in vis_env.split(",") if p.strip()]
                out = [torch.device(f"{base}:{i}") for i, _ in enumerate(parts)]
            else:
                out = [torch.device(f"{base}:{i}") for i in range(cnt)]
        except Exception:
            out = [torch.device(f"{base}:{i}") for i in range(cnt)]
    elif base == "mps":
        out = [torch.device("mps")]
    else:
        out = [torch.device("cpu")]
    return out


# --------------------------- Worker ---------------------------

class _Worker:
    """
    One model replica pinned to one device; runs requests sequentially by default.
    Concurrency >1 is allowed but may fight for streams; default remains 1.
    """
    def __init__(self, device: "torch.device", local_dir: str, dtype: "torch.dtype",
                 max_concurrency: int = 1) -> None:
        self.device = device
        self.local_dir = local_dir
        self.dtype = dtype
        self.max_concurrency = max(1, int(max_concurrency))

        # Tokenizer with pad safety and left padding
        self.tok = AutoTokenizer.from_pretrained(local_dir, local_files_only=True)
        added_pad = False
        if self.tok.pad_token is None:
            if self.tok.eos_token is not None:
                self.tok.pad_token = self.tok.eos_token
            else:
                self.tok.add_special_tokens({"pad_token": "<|pad|>"})
                added_pad = True
        self.tok.padding_side = "left"

        # Load model on the exact device (single-device map), prefer new 'dtype' kw
        dm = _device_map_for_worker(device)
        base_kw = dict(local_files_only=True, trust_remote_code=True)
        if dm is not None:
            base_kw["device_map"] = dm
        try:
            self.mod = AutoModelForCausalLM.from_pretrained(local_dir, dtype=dtype, **base_kw).eval()
        except TypeError:
            self.mod = AutoModelForCausalLM.from_pretrained(local_dir, torch_dtype=dtype, **base_kw).eval()

        # If tokenizer length changed (added pad), resize embeddings to avoid mismatch
        try:
            if added_pad:
                self.mod.resize_token_embeddings(len(self.tok))
        except Exception:
            pass

        # ---- Patch 1: pin pad_token_id in both config & generation_config (silence warnings) ----
        try:
            self.mod.config.pad_token_id = self.tok.pad_token_id
            if hasattr(self.mod, "generation_config") and self.mod.generation_config is not None:
                self.mod.generation_config.pad_token_id = self.tok.pad_token_id  # type: ignore[attr-defined]
        except Exception:
            pass

        # Optional: enable fused RMSNorm patches only if pure CUDA
        try:
            from skote.kernels.triton_ops import enable_triton_patches  # type: ignore
            if device.type == "cuda":
                enable_triton_patches(self.mod)
        except Exception:
            pass

        # ---- Patch 2: safe CUDA backend hints (no-ops on non-CUDA) ----
        try:
            if torch is not None and torch.cuda.is_available():
                torch.backends.cuda.matmul.allow_tf32 = True      # free perf on residual fp32 matmuls
                torch.backends.cudnn.benchmark = False            # keep latency stable for variable shapes
                torch.set_float32_matmul_precision("high")        # avoid accidental 'medium'
        except Exception:
            pass

        # Queues and threads
        self._q: "queue.Queue[Tuple[List[str], int, bool, Optional[float], Optional[float], threading.Event, List[str], List[Exception]]]" = queue.Queue()
        self._threads: List[threading.Thread] = []
        for i in range(self.max_concurrency):
            th = threading.Thread(target=self._loop, name=f"worker-{str(device)}-{i}", daemon=True)
            th.start()
            self._threads.append(th)

        # stats for policy
        self._mtx = threading.Lock()
        self._recent_avg_len: float = 256.0
        self._inflight: int = 0

        # warmup (neutralize cold start)
        try:
            _ = self.generate(["warmup"], max_new_tokens=1, greedy=True)
        except Exception:
            pass

        # optional: warm selected buckets (AOT-ish)
        try:
            buckets = os.environ.get("SKOTE_GRAPH_BUCKETS_CAPTURE", "")
            minb = int(os.environ.get("SKOTE_MIN_BUCKET_CAPTURE", "256"))
            if buckets:
                blist = sorted({int(b) for b in buckets.replace(";", ",").split(",") if b.strip().isdigit()})
                blist = [b for b in blist if b >= minb]
                if blist:
                    texts = ["x" * b for b in blist]
                    _ = self.generate(texts, max_new_tokens=1, greedy=True)
        except Exception:
            pass

    # ----------------- public API -----------------
    def queue_size(self) -> int:
        with self._mtx:
            return self._q.qsize() + self._inflight

    def recent_avg_len(self) -> float:
        with self._mtx:
            return float(self._recent_avg_len)

    def generate(self, prompts: List[str], max_new_tokens: int = 64, greedy: bool = True,
                 temperature: Optional[float] = None, top_p: Optional[float] = None) -> List[str]:
        """
        Synchronous API: put a batch and wait for completion.
        Returns decoded strings (same length as `prompts`).
        """
        done = threading.Event()
        out: List[str] = [""] * len(prompts)
        errs: List[Exception] = [None] * len(prompts)  # type: ignore
        self._q.put((prompts, int(max_new_tokens), bool(greedy),
                     temperature, top_p, done, out, errs))
        done.wait()
        # propagate first error if any
        for e in errs:
            if e is not None:
                raise e
        return out

    # ----------------- worker loop -----------------
    def _loop(self) -> None:
        while True:
            task = self._q.get()
            with self._mtx:
                self._inflight += 1
            try:
                prompts, gen_tokens, greedy, temperature, top_p, done, out, errs = task

                # -------- Micro-batch window: collect tasks arriving within window --------
                tasks = [task]
                win_ms = int(os.environ.get("SKOTE_ROUTER_BATCH_MS", "0"))
                if win_ms > 0:
                    tend = time.time() + (win_ms / 1000.0)
                    while time.time() < tend:
                        try:
                            tasks.append(self._q.get_nowait())
                        except queue.Empty:
                            break

                # Flatten prompts across tasks; remember slices for scatter
                flat_prompts: List[str] = []
                slices: List[Tuple[int, int]] = []
                eff_gen_tokens = int(gen_tokens)
                eff_greedy = bool(greedy)
                eff_temp = temperature
                eff_top_p = top_p

                for (ps, gt, gr, tp, topp, _d, _o, _e) in tasks:
                    start = len(flat_prompts)
                    flat_prompts.extend(ps)
                    end = len(flat_prompts)
                    slices.append((start, end))
                    eff_gen_tokens = max(eff_gen_tokens, int(gt))
                    eff_greedy = eff_greedy and bool(gr)
                    if tp is not None:
                        eff_temp = tp if eff_temp is None else eff_temp
                    if topp is not None:
                        eff_top_p = topp if eff_top_p is None else eff_top_p

                # Tokenize once for the whole micro-batch
                enc = self.tok(flat_prompts, return_tensors="pt", padding=True, truncation=True)
                ids = enc["input_ids"].to(self.device, non_blocking=True)
                amsk = enc.get("attention_mask")
                amsk = amsk.to(self.device, non_blocking=True) if amsk is not None else None

                # Generate with explicit attention_mask to avoid padding ambiguity
                with torch.no_grad():
                    # ---- Patch 3: make use_cache explicit (stable KV behavior) ----
                    gen_kwargs: Dict[str, Any] = dict(
                        input_ids=ids,
                        max_new_tokens=max(1, eff_gen_tokens),
                        use_cache=True,
                    )
                    if amsk is not None:
                        gen_kwargs["attention_mask"] = amsk
                    if eff_greedy:
                        gen_out = self.mod.generate(**gen_kwargs, do_sample=False, temperature=None, top_p=None)
                    else:
                        gen_out = self.mod.generate(
                            **gen_kwargs,
                            do_sample=True,
                            temperature=float(eff_temp or 0.7),
                            top_p=float(eff_top_p or 0.9),
                        )

                texts = self.tok.batch_decode(gen_out, skip_special_tokens=True)

                # Scatter results back to each task
                for (start, end), (_ps, _gt, _gr, _tp, _topp, d_i, out_i, errs_i) in zip(slices, tasks):
                    try:
                        local = texts[start:end]
                        out_i[:len(local)] = local
                    except Exception as e:
                        for k in range(end - start):
                            errs_i[k] = e
                    finally:
                        d_i.set()

                # Policy stats (use the original first task as representative)
                with self._mtx:
                    L = sum(len(p) for p in prompts) / max(1, len(prompts))
                    self._recent_avg_len = 0.9 * self._recent_avg_len + 0.1 * float(L)

            except Exception as e:
                # If something blows up before scatter, mark the first task as failed
                try:
                    _, _, _, _, _, done, out, errs = task
                    for i in range(len(out)):
                        errs[i] = e  # type: ignore[index]
                    done.set()
                except Exception:
                    pass
            finally:
                with self._mtx:
                    self._inflight -= 1

# --------------------------- Router ---------------------------

class Router:
    """
    High-level interface for request-level parallel decode across devices.
    """
    def __init__(self,
                 local_dir: Optional[str] = None,
                 devices: Optional[List[str]] = None,
                 dtype: Optional[str] = None,
                 policy: Optional[str] = None,
                 max_concurrency_per_device: Optional[int] = None) -> None:
        self.local_dir = local_dir or os.environ.get("MODEL_DIR", "")
        if not self.local_dir:
            raise ValueError("Router requires local_dir or $MODEL_DIR")

        self.dtype = _dtype_from_env() if dtype is None else {
            "bf16": torch.bfloat16, "bfloat16": torch.bfloat16,
            "fp16": torch.float16, "float16": torch.float16, "half": torch.float16,
            "fp32": torch.float32, "float32": torch.float32, "full": torch.float32
        }[dtype.lower()]

        self.policy = (policy or os.environ.get("SKOTE_ROUTER_POLICY", "len")).strip().lower()
        self.max_conc = int(os.environ.get("SKOTE_ROUTER_MAX_CONCURRENCY", "1")) if max_concurrency_per_device is None else int(max_concurrency_per_device)

        # Decide device list
        if devices:
            devs = [_normalize_device(d) for d in devices]
        else:
            # Latency mode => prefer single device even if multiple GPUs present
            if os.environ.get("SKOTE_LATENCY_MODE", "0") == "1":
                prim = os.environ.get("SKOTE_PRIMARY_DEVICE", "")
                devs = [_normalize_device(prim)] if prim else [_visible_devices()[0]]
            else:
                devs = _visible_devices()

        # Build workers; drop any that fail to load
        self.workers: List[_Worker] = []
        for dv in devs:
            try:
                w = _Worker(dv, self.local_dir, self.dtype, max_concurrency=self.max_conc)
                self.workers.append(w)
            except Exception as e:
                print(f"[router] skip device {dv}: {type(e).__name__}: {e}")

        if not self.workers:
            raise RuntimeError("No usable worker devices for Router")

        # RR index
        self._rr = 0
        self._mtx = threading.Lock()

    # --------- policy helpers ---------
    def _choose_rr(self) -> _Worker:
        with self._mtx:
            w = self.workers[self._rr]
            self._rr = (self._rr + 1) % len(self.workers)
        return w

    def _choose_sq(self) -> _Worker:
        return min(self.workers, key=lambda w: w.queue_size())

    def _choose_len(self, prompt_len: int) -> _Worker:
        # choose the worker with closest recent_avg_len; break ties by queue size
        best = None
        best_score = None
        for w in self.workers:
            score = abs(w.recent_avg_len() - float(prompt_len)) + 5.0 * w.queue_size()
            if best is None or score < best_score:
                best, best_score = w, score
        return best or self._choose_rr()

    def _pick_worker(self, prompts: List[str]) -> _Worker:
        if len(self.workers) == 1:
            return self.workers[0]
        pol = self.policy
        if pol == "rr":
            return self._choose_rr()
        if pol == "sq":
            return self._choose_sq()
        # "len" (default)
        avg_len = sum(len(p) for p in prompts) / max(1, len(prompts))
        return self._choose_len(int(avg_len))

    # --------- public API ---------
    def submit(self, text: str, max_new_tokens: int = 64, greedy: bool = True,
               temperature: Optional[float] = None, top_p: Optional[float] = None) -> str:
        w = self._pick_worker([text])
        outs = w.generate([text], max_new_tokens=max_new_tokens, greedy=greedy,
                          temperature=temperature, top_p=top_p)
        return outs[0]

    def submit_many(self, texts: List[str], max_new_tokens: int = 64, greedy: bool = True,
                    temperature: Optional[float] = None, top_p: Optional[float] = None) -> List[str]:
        # Small heuristic: split texts by approximate length (powers of two) to cut padding
        if len(self.workers) == 1 or len(texts) <= 1:
            return self.workers[0].generate(texts, max_new_tokens=max_new_tokens, greedy=greedy,
                                            temperature=temperature, top_p=top_p)

        buckets: Dict[int, List[Tuple[int, str]]] = {}
        for i, t in enumerate(texts):
            L = len(t)
            b = 1 << max(0, (L - 1).bit_length())  # next power of two
            buckets.setdefault(b, []).append((i, t))

        outs = [""] * len(texts)
        threads: List[threading.Thread] = []
        err_box: List[Exception] = []

        def _run(bucket_items: List[Tuple[int, str]]):
            idxs, stra = zip(*bucket_items)
            w = self._pick_worker(list(stra))
            try:
                res = w.generate(list(stra), max_new_tokens=max_new_tokens, greedy=greedy,
                                 temperature=temperature, top_p=top_p)
                for k, r in zip(idxs, res):
                    outs[k] = r
            except Exception as e:
                err_box.append(e)

        for items in buckets.values():
            th = threading.Thread(target=_run, args=(items,), daemon=True)
            th.start()
            threads.append(th)
        for th in threads:
            th.join()

        if err_box:
            raise err_box[0]
        return outs


# --------------------------- Entrypoints ---------------------------

def main(*args, **kwargs) -> int:
    """
    Minimal smoke: build router from env and run a single prompt.
    """
    try:
        local_dir = os.environ.get("MODEL_DIR", "")
        if not local_dir:
            print("[router] MODEL_DIR is not set; nothing to do.")
            return 0
        r = Router(local_dir=local_dir)
        out = r.submit("Skotergy hello", max_new_tokens=16, greedy=True)
        print("[router] ok:", out[:120].replace("\n", " "))
        return 0
    except Exception as e:
        print(f"[router] failed: {type(e).__name__}: {e}")
        return 1


def serve(*args, **kwargs) -> int:
    return main(*args, **kwargs)


def run(*args, **kwargs) -> int:
    return main(*args, **kwargs)
