# skote/runtime/metrics.py
"""
Skotergy Metrics (portable, backend-agnostic)
- Thread-safe counters and moving-window percentiles (p50/p95)
- Console + JSONL event stream + optional CSV summary
- Batch-level recorder: record_batch(inputs, outputs, extra={latency_ms, bucket, tokens_in/out, errors})
- Route-level recorder: record_route(info) to capture GraphMgr hits/misses/cache/buckets
- UPM recorder: record_upm(upm_stats) for fragmentation/utilization snapshots
- Snapshot/flush APIs for summaries; no external dependencies

Design notes:
- Works without GPUs; does not assume CUDA/ROCm/etc.
- Percentiles computed from a bounded moving window (approximate, but stable).
- Token counts are optional; falls back to len(text) if not provided.
"""

from __future__ import annotations

import os
import io
import json
import time
import threading
import datetime as _dt
from dataclasses import dataclass, asdict
from collections import deque
from typing import Any, Dict, Iterable, List, Optional

from skote import get_config, get_logger, SkoteConfig

log = get_logger("skotergy.metrics")


# --------------------------- Moving Window ---------------------------

class _MovingWindow:
    """Bounded reservoir with approximate percentile via sorting the window copy."""
    def __init__(self, size: int = 2048) -> None:
        self.size = int(size)
        self._buf: deque[float] = deque(maxlen=self.size)
        self._lock = threading.Lock()

    def add(self, value: float) -> None:
        with self._lock:
            self._buf.append(float(value))

    def clear(self) -> None:
        with self._lock:
            self._buf.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._buf)

    def quantile(self, q: float, default: float = 0.0) -> float:
        """q in [0,1]."""
        with self._lock:
            if not self._buf:
                return default
            data = sorted(self._buf)  # copy
        if q <= 0.0:
            return data[0]
        if q >= 1.0:
            return data[-1]
        idx = q * (len(data) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(data) - 1)
        frac = idx - lo
        return data[lo] * (1 - frac) + data[hi] * frac


# --------------------------- Data Models ---------------------------

@dataclass
class _BatchEvent:
    ts: float
    n_inputs: int
    latency_ms: float
    tokens_in: int
    tokens_out: int
    bucket: int
    lane: str
    groups: int
    backend: str
    errors: int


@dataclass
class _RouteEvent:
    ts: float
    backend: str
    bucket: int
    cached: bool
    cache_size: int
    hits: int
    misses: int
    overflow: bool


# --------------------------- Metrics ---------------------------

class Metrics:
    """
    Unified metrics sink.
    - Create one instance per process (SkoteSession does this lazily).
    - Thread-safe; background threads may call record_* concurrently.
    """

    def __init__(self, cfg: Optional[SkoteConfig] = None) -> None:
        self.cfg = cfg or get_config()

        # Run identity
        ts = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        self.run_id = os.environ.get("SKOTE_RUN_ID", ts)
        self.out_dir = os.environ.get("SKOTE_RUN_DIR", os.path.join(os.getcwd(), "runs"))
        self.max_window = int(os.environ.get("SKOTE_METRICS_WINDOW", "2048"))

        # State
        self._lock = threading.Lock()
        self._req_total = 0
        self._batch_total = 0
        self._err_total = 0
        self._tokens_in_total = 0
        self._tokens_out_total = 0

        self._lat_ms = _MovingWindow(self.max_window)
        self._last_upm: Optional[Dict[str, Any]] = None
        self._last_route: Optional[Dict[str, Any]] = None

        # Files
        os.makedirs(self.out_dir, exist_ok=True)
        self._jsonl_path = os.path.join(self.out_dir, f"events-{self.run_id}.jsonl")
        self._summary_csv = os.path.join(self.out_dir, f"summary-{self.run_id}.csv")
        # Write CSV header if not exists
        if not os.path.exists(self._summary_csv):
            with open(self._summary_csv, "w", encoding="utf-8") as f:
                f.write("ts,batches,requests,p50_ms,p95_ms,tokens_in,tokens_out,errors\n")

        log.info("Metrics started (run_id=%s, out_dir=%s)", self.run_id, self.out_dir)

    # -------------------- Recording APIs --------------------

    def record_batch(
        self,
        inputs: Iterable[str],
        outputs: Iterable[Dict[str, Any]],
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record one batch. 'extra' fields honored:
          - latency_ms (float), lane (str), groups (int), backend (str), bucket (int)
          - tokens_in / tokens_out (int); if missing, estimated from text length
          - errors (int)
        """
        t0 = time.time()
        extra = extra or {}
        inputs = list(inputs)
        outputs = list(outputs)

        # Estimate tokens if not provided (fallback by character length)
        tokens_in = int(extra.get("tokens_in", 0))
        tokens_out = int(extra.get("tokens_out", 0))
        if tokens_in <= 0:
            tokens_in = sum(len(str(x)) for x in inputs)
        if tokens_out <= 0:
            tokens_out = sum(len(str(o.get("text", ""))) for o in outputs)

        latency_ms = float(extra.get("latency_ms", 0.0))
        lane = str(extra.get("lane", "na"))
        groups = int(extra.get("groups", 1))
        backend = str(extra.get("backend", "auto"))
        bucket = int(extra.get("bucket", extra.get("bkt", -1)))
        errors = int(extra.get("errors", 0)) + sum(1 for o in outputs if "error" in o)

        with self._lock:
            self._req_total += len(inputs)
            self._batch_total += 1
            self._err_total += errors
            self._tokens_in_total += tokens_in
            self._tokens_out_total += tokens_out
            if latency_ms > 0:
                self._lat_ms.add(latency_ms)

        ev = _BatchEvent(
            ts=t0, n_inputs=len(inputs), latency_ms=latency_ms, tokens_in=tokens_in,
            tokens_out=tokens_out, bucket=bucket, lane=lane, groups=groups,
            backend=backend, errors=errors
        )
        self._write_jsonl({"type": "batch", **asdict(ev)})

        # Console one-liner (compact)
        if latency_ms > 0:
            log.info(
                "batch#%d n=%d lane=%s grp=%d bkt=%s lat=%.1fms tok_in=%d tok_out=%d err=%d",
                self._batch_total, len(inputs), lane, groups, bucket if bucket >= 0 else "-",
                latency_ms, tokens_in, tokens_out, errors
            )
        else:
            log.info(
                "batch#%d n=%d lane=%s grp=%d bkt=%s tok_in=%d tok_out=%d err=%d",
                self._batch_total, len(inputs), lane, groups, bucket if bucket >= 0 else "-",
                tokens_in, tokens_out, errors
            )

    def record_route(self, info: Dict[str, Any]) -> None:
        """
        Attach a routing event from GraphMgr.route().
        Expected keys: backend, bucket, cached (bool), cache_size, hits, misses, overflow
        """
        if not isinstance(info, dict):
            return
        self._last_route = info
        ev = _RouteEvent(
            ts=time.time(),
            backend=str(info.get("backend", "auto")),
            bucket=int(info.get("bucket", -1)),
            cached=bool(info.get("cached", False)),
            cache_size=int(info.get("cache_size", 0)),
            hits=int(info.get("hits", 0)),
            misses=int(info.get("misses", 0)),
            overflow=bool(info.get("overflow", False)),
        )
        self._write_jsonl({"type": "route", **asdict(ev)})

    def record_upm(self, stats: Dict[str, Any]) -> None:
        """
        Persist last seen UPM stats snapshot.
        Expected `stats()` of UnifiedPagingMemory.
        """
        if not isinstance(stats, dict):
            return
        self._last_upm = stats
        self._write_jsonl({"type": "upm", "ts": time.time(), "stats": stats})

    # -------------------- Snapshot & Flush --------------------

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            p50 = self._lat_ms.quantile(0.50, default=0.0)
            p95 = self._lat_ms.quantile(0.95, default=0.0)
            snap = {
                "run_id": self.run_id,
                "batches": self._batch_total,
                "requests": self._req_total,
                "errors": self._err_total,
                "tokens_in": self._tokens_in_total,
                "tokens_out": self._tokens_out_total,
                "p50_ms": p50,
                "p95_ms": p95,
                "route_last": self._last_route,
                "upm_last": self._last_upm,
                "config": self._safe_cfg_view(self.cfg),
            }
        return snap

    def flush(self) -> None:
        """Write a rolling CSV summary and a JSON snapshot file."""
        snap = self.snapshot()
        # CSV append
        with io.open(self._summary_csv, "a", encoding="utf-8") as f:
            f.write("{ts},{batches},{requests},{p50:.3f},{p95:.3f},{tin},{tout},{err}\n".format(
                ts=int(time.time()),
                batches=snap["batches"],
                requests=snap["requests"],
                p50=snap["p50_ms"],
                p95=snap["p95_ms"],
                tin=snap["tokens_in"],
                tout=snap["tokens_out"],
                err=snap["errors"],
            ))
        # JSON snapshot
        path = os.path.join(self.out_dir, f"snapshot-{self.run_id}.json")
        self._safe_write_json(path, snap)
        log.info("Metrics flush -> %s / %s", self._summary_csv, path)

    # -------------------- Helpers --------------------

    def _write_jsonl(self, obj: Dict[str, Any]) -> None:
        try:
            with io.open(self._jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        except Exception as e:  # pragma: no cover
            log.warning("metrics: failed to write jsonl: %s", e)

    @staticmethod
    def _safe_write_json(path: str, data: Dict[str, Any]) -> None:
        try:
            with io.open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:  # pragma: no cover
            log.warning("metrics: failed to write snapshot: %s", e)

    @staticmethod
    def _safe_cfg_view(cfg: SkoteConfig) -> Dict[str, Any]:
        # redact potentially long fields
        return {
            "backend_preference": list(cfg.backend_preference),
            "enable_graph_bucketing": cfg.enable_graph_bucketing,
            "enable_upm": cfg.enable_upm,
            "enable_scheduler": cfg.enable_scheduler,
            "enable_spec_decode": cfg.enable_spec_decode,
            "qos_mode": cfg.qos_mode,
            "max_context_buckets": list(cfg.max_context_buckets),
            "page_size_kv": getattr(cfg, "page_size_kv", 16384),
            "page_size_apc": getattr(cfg, "page_size_apc", 16384),
            "page_size_lora": getattr(cfg, "page_size_lora", 16384),
        }
