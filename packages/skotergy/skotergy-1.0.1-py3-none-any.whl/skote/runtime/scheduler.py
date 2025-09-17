# skote/runtime/scheduler.py
"""
Skotergy Scheduler (per-device queues, deadline-aware, token-credit hints, CUDA-graphs friendly)

What this version guarantees
----------------------------
1) Per-device queues (zero-intrusion for single-GPU):
   - Each device keeps its own latency/throughput queues and rolling deadlines.
   - Backward compatible: if no device_index is provided, current device (or CPU idx 0) is used.
2) Deadline & age-promotion QoS:
   - Per-task deadlines (qos='deadline' or SKOTE_QOS_MODE=deadline) plus age promotion
     (flush if any task waits longer than SKOTE_AGE_PROMOTE_MS).
3) Token-credit batch hint:
   - Optional `token_credit` per task; queues flush early when the aggregated credit
     reaches SKOTE_TOKEN_CREDIT. This approximates "flush based on expected decode work".
4) Small-bucket eager policy:
   - If bucket < MIN_BUCKET_CAPTURE and SKOTE_EAGER_SMALL_BUCKETS=1, we go eager to avoid graph churn.
5) GraphManager interaction is safe and lane-aware:
   - Only attempted on the throughput lane and for stable buckets >= MIN_BUCKET_CAPTURE.
   - Exceptions are fully contained; latency lane is never penalized by graph probing.
6) Lower default capture threshold:
   - SKOTE_MIN_BUCKET_CAPTURE defaults to 1024, matching common short/medium sequences.
7) Metrics:
   - Best-effort and include device, flush reason, lane, representative bucket, batch size, and latency.

Environment knobs
-----------------
- SKOTE_SCHED_LAT_MS         : latency-lane window in ms (default: cfg.batch_window_ms or 16)
- SKOTE_SCHED_TP_MS          : throughput-lane window in ms (default: 4 * LAT_MS)
- SKOTE_SCHED_MAX_LAT_BATCH  : max batch size for latency lane (default: 32)
- SKOTE_SCHED_MAX_TP_BATCH   : max batch size for throughput lane (default: 256)
- SKOTE_MIN_BUCKET_CAPTURE   : minimal bucket length eligible for graph capture (default: 1024)
- SKOTE_EAGER_SMALL_BUCKETS  : "1" => eager path for buckets < MIN_BUCKET_CAPTURE (default: "1")
- SKOTE_GRAPHS               : "1" => enable CUDA Graphs interaction if GraphManager is attached (default: "0")
- SKOTE_SCHED_LOG            : "1" => verbose scheduler logs (default: "0")
- SKOTE_BIND_ONCE            : "1" => bind model once; ignore repeat binds of same callable (default: "1")

New QoS knobs (this revision)
-----------------------------
- SKOTE_QOS_MODE             : "balanced"(default) | "deadline"
- SKOTE_TOKEN_CREDIT         : integer threshold to flush a lane based on sum of per-task token_credit (default: 32)
- SKOTE_AGE_PROMOTE_MS       : age threshold to flush a lane even before window/credit (default: 200)

Notes
-----
- Token credit is a hint (e.g., expected max_new_tokens). If not provided by caller,
  tasks default to SKOTE_TOKEN_CREDIT for simplicity.
- Per-device queues are maintained inside a single worker thread for simplicity and fairness.
"""

from __future__ import annotations

import os
import time
import threading
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from skote import get_config, get_logger, SkoteConfig

log = get_logger("skotergy.scheduler")

try:
    import torch
except Exception:
    torch = None  # type: ignore


# --------------------------- Task model ---------------------------

@dataclass
class _Task:
    prompt: str
    qos: str
    bucket_id: int
    model_id: str
    adapter_id: Optional[str]
    future: "threading.Event"
    result: Dict[str, Any]
    created_at: float
    deadline_at: float
    device_index: int
    token_credit: int  # hint tokens for this request (used to trigger flush by credit)


# --------------------------- Scheduler ---------------------------

class Scheduler:
    """
    Deadline-aware, token-credit-aware micro-batching scheduler with
    per-device queues and bucket/model/adapter grouping.
    """

    def __init__(self, cfg: Optional[SkoteConfig] = None) -> None:
        self.cfg = cfg or get_config()

        # QoS windows
        default_lat_ms = int(getattr(self.cfg, "batch_window_ms", 16) or 16)
        self.latency_window_ms = int(os.environ.get("SKOTE_SCHED_LAT_MS", default_lat_ms))
        self.throughput_window_ms = int(os.environ.get("SKOTE_SCHED_TP_MS", self.latency_window_ms * 4))

        # Batch caps
        self.max_batch_latency = int(os.environ.get("SKOTE_SCHED_MAX_LAT_BATCH", "32"))
        self.max_batch_throughput = int(os.environ.get("SKOTE_SCHED_MAX_TP_BATCH", "256"))

        # QoS & credits
        self.qos_mode = (os.environ.get("SKOTE_QOS_MODE", "balanced") or "balanced").lower()
        self.token_credit_threshold = max(0, int(os.environ.get("SKOTE_TOKEN_CREDIT", "32")))
        self.age_promote_ms = max(0, int(os.environ.get("SKOTE_AGE_PROMOTE_MS", "200")))

        # Capture/graph policy knobs (aligned with GraphManager)
        self.min_bucket_capture = int(os.environ.get("SKOTE_MIN_BUCKET_CAPTURE", "1024"))
        self.eager_small_buckets = os.environ.get("SKOTE_EAGER_SMALL_BUCKETS", "1").strip() == "1"
        self.graphs_enabled = os.environ.get("SKOTE_GRAPHS", "0").strip() == "1"
        self.verbose = os.environ.get("SKOTE_SCHED_LOG", "0").strip() == "1"
        self.bind_once = os.environ.get("SKOTE_BIND_ONCE", "1").strip() == "1"

        # Per-device queues: device_index -> {"lat": List[_Task], "tp": List[_Task]}
        self._lock = threading.RLock()
        self._cv = threading.Condition(self._lock)
        self._q_per_device: Dict[int, Dict[str, List[_Task]]] = {}
        # Rolling deadlines per device/lane
        self._next_deadline: Dict[int, Dict[str, float]] = {}

        self._stop = False

        # External wiring
        self.__dict__['_bound_model'] = None           # callable or None
        self.__dict__['_bound_model_sig'] = None       # (id, qualname) signature for idempotent bind
        self.__dict__['_graphmgr'] = None
        self._metrics = None
        try:
            # Optional metrics sink
            from skote.runtime.metrics import Metrics  # type: ignore
            self._metrics = Metrics(self.cfg)
        except Exception:
            self._metrics = None

        # Start worker thread
        self._worker = threading.Thread(target=self._loop, name="skote-sched", daemon=True)
        self._worker.start()

        log.info(
            "Scheduler ready (per-device queues, lat=%dms, tp=%dms, cap: L=%d/T=%d, "
            "eager_small=%s, graphs=%s, bind_once=%s, min_bucket_capture=%d, qos=%s, credit=%d, age_promote=%dms)",
            self.latency_window_ms,
            self.throughput_window_ms,
            self.max_batch_latency,
            self.max_batch_throughput,
            self.eager_small_buckets,
            self.graphs_enabled,
            self.bind_once,
            self.min_bucket_capture,
            self.qos_mode,
            self.token_credit_threshold,
            self.age_promote_ms,
        )

    # -------------------- Wiring --------------------

    def _callable_signature(self, fn: Callable[..., Any]) -> Tuple[int, str]:
        """Stable-enough identity for idempotent bind logging."""
        name = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", None) or type(fn).__name__
        return (id(fn), str(name))

    def bind_model(self, fn: Callable[..., Any]) -> None:
        """
        Bind the real model callable. Supports:
        - fn(str) -> str | dict
        - fn(list[str]) -> list[str] | list[dict]
        - fn.generate_batch(list[str]) -> list[str] | list[dict]
        Idempotent if SKOTE_BIND_ONCE=1 and the callable identity is unchanged.
        """
        with self._lock:
            sig = self._callable_signature(fn)
            if self.bind_once and self._bound_model is not None and self._bound_model_sig == sig:
                if self.verbose:
                    log.debug("bind_model skipped: same callable already bound (sig=%s).", sig)
                return

            wrapped = self._maybe_wrap_for_runtime(fn)
            self.__dict__['_bound_model'] = wrapped
            self.__dict__['_bound_model_sig'] = sig
            log.info("Scheduler bound to model callable: %s", getattr(fn, "__name__", type(fn).__name__))

    def _maybe_wrap_for_runtime(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Best-effort wrapper hook: if a runtime wrapper is available, apply once.
        On failure, return the original callable.
        """
        try:
            # Optional hook (presence depends on your repo layout)
            from skote.runtime.wrap import wrap_for_runtime  # type: ignore
            return wrap_for_runtime(fn)
        except Exception:
            return fn

    def attach_graph_manager(self, gm: Any) -> None:
        """Attach GraphManager instance to enable prefill capture/replay on stable buckets."""
        with self._lock:
            self.__dict__['_graphmgr'] = gm
        log.info("Scheduler attached to GraphManager.")

    def attach_metrics(self, metrics: Any) -> None:
        """Attach a Metrics sink (must expose record_batch)."""
        with self._lock:
            self._metrics = metrics
        log.info("Scheduler attached to Metrics.")

    # -------------------- Public API --------------------

    def submit(
        self,
        first: Any,
        second: Optional[List[str]] = None,
        *,
        bucket_info: Optional[Dict[str, Any]] = None,
        qos: Optional[str] = None,
        model_id: str = "default",
        adapter_id: Optional[str] = None,
        device: Optional[Any] = None,
        device_index: Optional[int] = None,
        token_credit: Optional[int] = None,
        deadline_ms: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Enqueue prompts and block until their batch is flushed and results are ready.
        Backward-compat signatures:
          - submit(prompts, ...)
          - submit(model_callable, prompts, ...)  # bind model on the fly

        Returns: [{'text','prompt','bucket','model_id','adapter_id?','device','flush_reason?'}]
        """
        # Backward-compat: allow legacy submit(model, prompts, ...)
        if callable(first):
            fn = first
            prompts = second if second is not None else []
            if not prompts:
                raise TypeError("submit(model, prompts, ...) requires a non-empty prompts list")
            self.bind_model(fn)
        else:
            prompts = first

        # QoS lane mapping
        qos_lane = (qos or getattr(self.cfg, "qos_mode", None) or self.qos_mode or "balanced").lower()
        if qos_lane == "balanced":
            qos_lane = "latency"  # bias to latency by default

        # Bucket comes from upstream router/GraphManager; fallback to 0 if missing.
        bucket_id = int((bucket_info or {}).get("bucket", 0))
        # token_credit hint: prefer provided value, else bucket_info hint, else env default
        tc_default = self.token_credit_threshold if self.token_credit_threshold > 0 else 32
        per_task_credit = int(
            (token_credit if token_credit is not None else (bucket_info or {}).get("token_credit", tc_default))
        )

        # device index resolution (default: current CUDA device if available, else 0)
        dev_idx = self._resolve_device_index(device, device_index)

        now = time.time()
        lat_deadline = now + (self.latency_window_ms / 1000.0)
        tp_deadline = now + (self.throughput_window_ms / 1000.0)
        # In deadline mode, allow explicit custom deadline
        if (qos or self.qos_mode) == "deadline" and deadline_ms:
            lat_deadline = tp_deadline = now + (int(deadline_ms) / 1000.0)

        futures: List[threading.Event] = []
        tasks: List[_Task] = []

        with self._cv:  # holds self._lock
            self._ensure_device(dev_idx)

            for p in prompts:
                evt = threading.Event()
                # choose lane deadline
                if qos_lane == "throughput":
                    dl = tp_deadline
                else:
                    dl = lat_deadline

                t = _Task(
                    prompt=p,
                    qos=qos_lane,
                    bucket_id=bucket_id,
                    model_id=model_id,
                    adapter_id=adapter_id,
                    future=evt,
                    result={},
                    created_at=now,
                    deadline_at=dl,
                    device_index=dev_idx,
                    token_credit=per_task_credit,
                )
                tasks.append(t)
                futures.append(evt)
                if qos_lane == "throughput":
                    self._q_per_device[dev_idx]["tp"].append(t)
                else:
                    self._q_per_device[dev_idx]["lat"].append(t)
            self._cv.notify_all()

        # Wait all results
        for f in futures:
            f.wait()
        return [t.result for t in tasks]

    def stop(self) -> None:
        with self._cv:
            self._stop = True
            self._cv.notify_all()
        self._worker.join(timeout=2.0)

    # -------------------- Worker Loop --------------------

    def _loop(self) -> None:
        lat_interval = self.latency_window_ms / 1000.0
        tp_interval = self.throughput_window_ms / 1000.0

        # Initialize rolling deadlines lazily when devices are seen
        while True:
            with self._cv:
                if self._stop:
                    return

                # No work? wait
                if not any(self._q_per_device.get(d, {}).get("lat") or self._q_per_device.get(d, {}).get("tp")
                           for d in self._q_per_device.keys()):
                    self._cv.wait()
                    # re-loop to compute fresh deadlines on next iteration
                    continue

                now = time.time()
                # Collect flush decisions across devices/lanes
                flush_plan: List[Tuple[int, str, List[_Task], str]] = []  # (device, lane, tasks, reason)

                for dev_idx, lanes in list(self._q_per_device.items()):
                    # Ensure rolling deadlines exist
                    nd = self._next_deadline.setdefault(dev_idx, {})
                    nd.setdefault("lat", now + lat_interval)
                    nd.setdefault("tp", now + tp_interval)

                    # LAT
                    if lanes["lat"]:
                        do, reason = self._should_flush_lane_locked(
                            q=lanes["lat"],
                            now=now,
                            next_deadline=nd["lat"],
                            max_batch=self.max_batch_latency,
                            credit_threshold=self.token_credit_threshold,
                        )
                        if do:
                            batch = self._drain_by_credit_locked(lanes["lat"], self.max_batch_latency, self.token_credit_threshold)
                            nd["lat"] = time.time() + lat_interval
                            if batch:
                                flush_plan.append((dev_idx, "latency", batch, reason or "deadline"))

                    # TP
                    if lanes["tp"]:
                        do, reason = self._should_flush_lane_locked(
                            q=lanes["tp"],
                            now=now,
                            next_deadline=nd["tp"],
                            max_batch=self.max_batch_throughput,
                            credit_threshold=self.token_credit_threshold,
                        )
                        if do:
                            batch = self._drain_by_credit_locked(lanes["tp"], self.max_batch_throughput, self.token_credit_threshold)
                            nd["tp"] = time.time() + tp_interval
                            if batch:
                                flush_plan.append((dev_idx, "throughput", batch, reason or "deadline"))

            # Process outside the lock (per device, per lane)
            for dev_idx, lane, tasks, reason in flush_plan:
                self._process_batch(tasks, device_index=dev_idx, lane=lane, flush_reason=reason)

    # -------------------- Flush decisions & draining --------------------

    def _past_any_deadline_q(self, q: List[_Task], now: float) -> bool:
        return bool(q) and (min(t.deadline_at for t in q) <= now)

    def _age_promote_hit(self, q: List[_Task], now: float) -> bool:
        if self.age_promote_ms <= 0 or not q:
            return False
        return min((now - t.created_at) * 1000.0 for t in q) >= self.age_promote_ms

    def _credit_sum(self, q: List[_Task]) -> int:
        return sum(max(0, int(t.token_credit)) for t in q)

    def _should_flush_lane_locked(
        self,
        *,
        q: List[_Task],
        now: float,
        next_deadline: float,
        max_batch: int,
        credit_threshold: int,
    ) -> Tuple[bool, Optional[str]]:
        """Decide whether to flush a queue, and why."""
        if not q:
            return False, None
        if len(q) >= max_batch:
            return True, "max_batch"
        if credit_threshold > 0 and self._credit_sum(q) >= credit_threshold:
            return True, "token_credit"
        if self._age_promote_hit(q, now):
            return True, "age_promote"
        if now >= next_deadline:
            return True, "deadline"
        if self._past_any_deadline_q(q, now):
            return True, "task_deadline"
        return False, None

    def _drain_by_credit_locked(self, q: List[_Task], cap_count: int, credit_threshold: int) -> List[_Task]:
        """
        Pop up to 'cap_count' tasks, but also stop when accumulated token_credit
        would exceed 'credit_threshold' (>0). If threshold<=0, behave like simple cap.
        """
        if not q:
            return []
        if credit_threshold <= 0:
            n = min(len(q), cap_count)
            out = q[:n]
            del q[:n]
            return out

        acc = 0
        out: List[_Task] = []
        # Greedy take in FIFO order; preserve request ordering fairness per device/lane.
        while q and len(out) < cap_count:
            if acc >= credit_threshold and out:
                break
            t = q.pop(0)
            out.append(t)
            acc += max(0, int(t.token_credit))
        return out

    def _ensure_device(self, device_index: int) -> None:
        """Initialize per-device structures if missing."""
        if device_index not in self._q_per_device:
            self._q_per_device[device_index] = {"lat": [], "tp": []}
            now = time.time()
            self._next_deadline[device_index] = {
                "lat": now + (self.latency_window_ms / 1000.0),
                "tp": now + (self.throughput_window_ms / 1000.0),
            }

    def _resolve_device_index(self, device: Optional[Any], device_index: Optional[int]) -> int:
        """Resolve to an integer device index."""
        if device_index is not None:
            return int(device_index)
        if device is not None:
            try:
                # torch.device or module with .device
                if hasattr(device, "index"):
                    di = getattr(device, "index")
                    if di is not None:
                        return int(di)
                if hasattr(device, "device") and getattr(device, "device") is not None:
                    di = getattr(device, "device").index
                    if di is not None:
                        return int(di)
            except Exception:
                pass
        # fallback: current CUDA device if available
        if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
            try:
                return int(torch.cuda.current_device())
            except Exception:
                pass
        return 0

    # -------------------- Batch Processing --------------------

    def _process_batch(self, tasks: List[_Task], *, device_index: int, lane: str, flush_reason: str) -> None:
        """
        In-flight merge: group by (bucket_id, model_id, adapter_id).
        For each group:
          - If small bucket and eager_small_buckets=True => eager path (avoid CUDA graph churn).
          - Else if graphs enabled and GraphManager attached => prefill replay/capture best-effort.
          - Then call the bound model (batch if possible; fallback to per-item).
        """
        t0 = time.time()

        # 1) Group tasks
        groups: Dict[Tuple[int, str, Optional[str]], List[_Task]] = {}
        for t in tasks:
            groups.setdefault((t.bucket_id, t.model_id, t.adapter_id), []).append(t)

        # 2) Execute per group
        total = len(tasks)
        for (bucket_id, model_id, adapter_id), ts in groups.items():
            prompts = [t.prompt for t in ts]

            # Decide execution mode
            small_bucket = bucket_id < self.min_bucket_capture
            use_eager = small_bucket and self.eager_small_buckets
            use_graphs = (not use_eager) and (lane != "latency") and (bucket_id >= self.min_bucket_capture) \
                         and self.graphs_enabled and (self._graphmgr is not None)

            if use_graphs:
                self._maybe_graph_prefill(bucket_id=bucket_id, model_id=model_id, tasks=ts)

            # 3) Call the model with hard safety (never block futures on errors/mismatch)
            try:
                outputs = self._call_model(prompts)
            except Exception:
                if self.verbose:
                    log.debug("Model callable raised; filling empty outputs.", exc_info=True)
                outputs = [""] * len(ts)

            # Normalize outputs to exactly len(ts)
            if not isinstance(outputs, (list, tuple)):
                outputs = [outputs] * len(ts)
            outputs = list(outputs)
            if len(outputs) < len(ts):
                outputs.extend([""] * (len(ts) - len(outputs)))
            elif len(outputs) > len(ts):
                outputs = outputs[:len(ts)]

            # 4) Deliver results (always set futures)
            for i, t in enumerate(ts):
                text = outputs[i]
                # Accept dict outputs (e.g., {"text": "...", "gen_len": N}); normalize to "text" if needed
                if isinstance(text, dict):
                    text = str(text.get("text", ""))

                t.result = {
                    "text": text,
                    "prompt": t.prompt,
                    "bucket": bucket_id,
                    "model_id": model_id,
                    "adapter_id": adapter_id,
                    "device": device_index,
                    "flush_reason": flush_reason,
                }
                t.future.set()

        t1 = time.time()

        # 5) Metrics (best-effort)
        if self._metrics:
            try:
                first_key = next(iter(groups.keys())) if groups else (-1, "n/a", None)
                rep_bucket = first_key[0]
                self._metrics.record_batch(
                    inputs=[t.prompt for t in tasks],
                    outputs=[t.result for t in tasks],
                    extra={
                        "lane": lane,
                        "device": device_index,
                        "groups": len(groups),
                        "batch_size": total,
                        "latency_ms": (t1 - t0) * 1000.0,
                        "bucket": rep_bucket,
                        "flush_reason": flush_reason,
                        "credit_sum": sum(t.token_credit for t in tasks),
                    },
                )
            except Exception:
                pass

    # -------------------- CUDA Graphs helper --------------------

    def _maybe_graph_prefill(self, *, bucket_id: int, model_id: str, tasks: List[_Task]) -> None:
        """
        Best-effort CUDA Graphs prefill capture/replay:
        - Use first sample to build example inputs (requires model wrapper exposing tokenizer/device fields).
        - Replay if warm; otherwise attempt a one-time AOT capture through GraphManager.
        Safe no-op on failure or if CUDA is unavailable.
        """
        try:
            gm = self._graphmgr
            if gm is None:
                return
            bound = self._bound_model
            if bound is None:
                return

            # Expect an HF-like wrapper exposing `.tok` and `.mod` (transformers tokenizer + torch module).
            tok = getattr(bound, "tok", None)
            mod = getattr(bound, "mod", None)
            if tok is None or mod is None:
                return  # Not our expected wrapper, skip graphs.

            sample = tasks[0].prompt
            enc = tok(sample, return_tensors="pt")
            ii = enc["input_ids"].to(mod.device, non_blocking=True)
            am = enc.get("attention_mask", None)
            if am is not None:
                am = am.to(mod.device, non_blocking=True)

            # Build a graph key consistent with GraphManager
            try:
                from skote.runtime.graphmgr import GraphKey
                gk = GraphKey(model_id=model_id, backend=getattr(gm, "backend", "cuda"),
                              dtype="auto", bucket=bucket_id, attn_kernel="auto", extra="")
                kid = gk.to_compact()
            except Exception:
                kid = f"{model_id}|{getattr(gm, 'backend', 'cuda')}|{bucket_id}"

            # Try replay first; if miss, attempt capture once
            if not gm.replay(kid, ii, am):
                def _prefill_forward(input_ids, attention_mask=None):
                    return mod.forward(input_ids=input_ids, attention_mask=attention_mask)
                gm.maybe_capture(kid, _prefill_forward, (ii,), {"attention_mask": am}, aot=True)
        except Exception:
            if self.verbose:
                log.debug("Graphs prefill skipped due to exception.", exc_info=True)
            return

    # -------------------- Model call helper --------------------

    def _call_model(self, prompts: List[str]) -> List[str]:
        """
        Call the bound model in batch if possible; otherwise per-item.
        Accepts the following shapes:
          - fn(str) -> str | dict
          - fn(list[str]) -> list[str] | list[dict]
          - fn.generate_batch(list[str]) -> list[str] | list[dict]
        Fallback is an identity echo.
        """
        fn = self.__dict__.get('_bound_model', None)
        if fn is None:
            return list(prompts)

        # Direct batch call supported?
        try:
            if hasattr(fn, "generate_batch") and callable(getattr(fn, "generate_batch")):
                out = fn.generate_batch(prompts)  # type: ignore
                return list(out)
        except Exception:
            pass

        try:
            # Try calling with a list directly (some wrappers accept this)
            out = fn(prompts)  # type: ignore
            if isinstance(out, (list, tuple)):
                return list(out)  # type: ignore
        except Exception:
            pass

        # Fallback: per-item
        outs: List[str] = []
        for p in prompts:
            try:
                r = fn(p)  # type: ignore
                # Normalize dict returns
                if isinstance(r, dict):
                    r = r.get("text", "")
                outs.append(str(r))
            except Exception:
                outs.append("")
        return outs
