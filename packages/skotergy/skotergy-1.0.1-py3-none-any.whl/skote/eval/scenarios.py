# skote/eval/scenarios.py
"""
Skotergy Evaluation Scenarios (single source of truth)

Covers four baseline scenario families aligned with v1.1 Excel:
  1) Prefill-heavy (long-context prefill, minimal decode)
  2) Decode-heavy (short prompt, 256 tokens)
  3) Concurrency sweep (1 / 4 / 8)
  4) Multi-tenant with LoRA/APC pressure

Design goals:
- Canonical place for lengths, concurrency, QoS lanes, KPI intents.
- Portable (no GPU requirement); runner binds to SkoteSession/scheduler later.
- Future-proof: buckets/limits scale via env vars without code edits.
"""

from __future__ import annotations

import os
import math
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple, Literal

# QoS choices mirror SkoteConfig
QoS = Literal["latency", "throughput", "balanced"]


# --------------------------- helpers ---------------------------

def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except Exception:
        return default


def _env_list_int(key: str, default: List[int]) -> List[int]:
    raw = os.environ.get(key)
    if not raw:
        return list(default)
    out: List[int] = []
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            out.append(int(tok))
        except Exception:
            pass
    return out or list(default)


def _mk_prompt(n_chars: int, tokenish_ratio: float = 0.75, seed: Optional[int] = None) -> str:
    """
    Generate a deterministic-ish prompt ~ n_chars.
    tokenish_ratio ~ chars per token heuristic; not exact but stable.
    """
    rnd = random.Random(seed if seed is not None else n_chars)
    base = " ".join(
        rnd.choice(
            [
                "analysis", "context", "theory", "evidence", "method", "result",
                "hypothesis", "compute", "graph", "kernel", "schedule", "memory",
                "attention", "prefix", "paging", "bucket", "latency", "throughput",
            ]
        )
        for _ in range(max(4, int(n_chars * tokenish_ratio / 5)))
    )
    if len(base) >= n_chars:
        return base[:n_chars]
    return (base + " ") * ((n_chars // (len(base) + 1)) + 1)[:n_chars]


# --------------------------- core specs ---------------------------

@dataclass
class BatchSpec:
    """
    A flush unit to be submitted to scheduler in one shot.
    runner.py should:
      - pick qos
      - call session.run(model, prompts, qos=..., model_id=..., meta=...)
    """
    prompts: List[str]
    qos: QoS = "latency"
    model_id: str = "default"
    # hints for runtime/runner (not mandatory):
    seq_lens: Optional[List[int]] = None
    target_bucket: Optional[int] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class ScenarioSpec:
    """
    One scenario is a list of batches with coherent KPI intent.
    """
    name: str
    description: str
    kpi_focus: List[str]  # e.g., ["p95_ms", "tokens/s", "fragmentation"]
    batches: List[BatchSpec]
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "kpi_focus": list(self.kpi_focus),
            "tags": list(self.tags),
            "batches": [b.to_dict() for b in self.batches],
        }


# --------------------------- defaults (aligned with v1.1) ---------------------------

# Length buckets for prefill/long-context (characters as token surrogate).
# These should correlate with GraphMgr default buckets [2k,4k,8k,16k,32k].
DEFAULT_LONG_PROMPTS = _env_list_int("SKOTE_SCN_LONG_CHARS", [8192, 16384, 32768])
# Decode target tokens per request (runner may only use as a hint).
DEFAULT_DECODE_TOKENS = _env_int("SKOTE_SCN_DECODE_TOKS", 256)
# Concurrency sweep
DEFAULT_CONCURRENCY = _env_list_int("SKOTE_SCN_CONC", [1, 4, 8])
# Repeats per batch shape for stability (runner may loop N times).
DEFAULT_REPEATS = _env_int("SKOTE_SCN_REPEATS", 1)
# Synthetic multi-tenant size (tenants x prompts per tenant)
MT_TENANTS = _env_int("SKOTE_SCN_MT_TENANTS", 3)
MT_PROMPTS_PER_TENANT = _env_int("SKOTE_SCN_MT_PER_TENANT", 5)
# Default model id (can be overridden by runner CLI)
DEFAULT_MODEL_ID = os.environ.get("SKOTE_MODEL_ID", "default")


# --------------------------- builders ---------------------------

def build_prefill_longcontext(
    long_chars: List[int] = DEFAULT_LONG_PROMPTS,
    repeats: int = DEFAULT_REPEATS,
    model_id: str = DEFAULT_MODEL_ID,
) -> ScenarioSpec:
    """
    Prefill-heavy: long prompt, minimal generation.
    QoS: throughput lane to favor batching.
    KPI: prefill tokens/s, p95_ms, GraphMgr cache hit rate.
    """
    batches: List[BatchSpec] = []
    for L in long_chars:
        for r in range(repeats):
            prompt = _mk_prompt(L, seed=1000 + L + r)
            batches.append(
                BatchSpec(
                    prompts=[prompt],
                    qos="throughput",
                    model_id=model_id,
                    seq_lens=[L],
                    target_bucket=L,
                    meta={"kind": "prefill", "gen_tokens": 1},
                )
            )
    return ScenarioSpec(
        name="prefill_longcontext",
        description="Long-context prefill with minimal decode (1 token).",
        kpi_focus=["tokens/s", "p95_ms", "graph_hit_rate"],
        batches=batches,
        tags=["prefill", "long-context", "throughput"],
    )


def build_decode_short_prompt(
    gen_tokens: int = DEFAULT_DECODE_TOKENS,
    repeats: int = DEFAULT_REPEATS,
    model_id: str = DEFAULT_MODEL_ID,
) -> ScenarioSpec:
    """
    Decode-heavy: short prompt, target N decode tokens.
    QoS: latency lane for low p50/p95.
    KPI: p50/p95, tokens/s in decode.
    """
    batches: List[BatchSpec] = []
    short_prompt = _mk_prompt(128, seed=42)
    for r in range(repeats):
        batches.append(
            BatchSpec(
                prompts=[short_prompt],
                qos="latency",
                model_id=model_id,
                seq_lens=[len(short_prompt)],
                target_bucket=2048,  # small bucket
                meta={"kind": "decode", "gen_tokens": int(gen_tokens)},
            )
        )
    return ScenarioSpec(
        name="decode_256tok",
        description="Short prompt with ~256-token decode (runner interprets gen_tokens).",
        kpi_focus=["p50_ms", "p95_ms", "tokens/s"],
        batches=batches,
        tags=["decode", "latency"],
    )


def build_concurrency_sweep(
    conc_levels: List[int] = DEFAULT_CONCURRENCY,
    model_id: str = DEFAULT_MODEL_ID,
) -> ScenarioSpec:
    """
    Concurrency sweep with identical short prompts; tests continuous batching & in-flight merge.
    QoS: balanced -> mapped to latency lane by default.
    KPI: p95 under burst, QPS.
    """
    batches: List[BatchSpec] = []
    prompt = _mk_prompt(256, seed=7)
    for c in conc_levels:
        batches.append(
            BatchSpec(
                prompts=[prompt] * c,
                qos="balanced",
                model_id=model_id,
                seq_lens=[len(prompt)] * c,
                target_bucket=2048,
                meta={"kind": "concurrency", "concurrency": c, "gen_tokens": 64},
            )
        )
    return ScenarioSpec(
        name="concurrency_1_4_8",
        description="Concurrency sweep (1/4/8) with short prompts.",
        kpi_focus=["p95_ms", "qps"],
        batches=batches,
        tags=["concurrency", "batching", "in-flight"],
    )


def build_multitenant_lora(
    tenants: int = MT_TENANTS,
    per_tenant: int = MT_PROMPTS_PER_TENANT,
    model_id: str = DEFAULT_MODEL_ID,
) -> ScenarioSpec:
    """
    Multi-tenant synthetic workload:
      - multiple 'tenant_id' and 'adapter_id' tags
      - drives UPM KV/APC/LoRA paging behavior (runner may allocate region pages)
    QoS: throughput lane (mix-friendly).
    KPI: fragmentation, p95 stability, QPS.
    """
    batches: List[BatchSpec] = []
    for t in range(tenants):
        tid = f"tenant_{t+1}"
        # simulate 1~3 adapters per tenant
        adapters = [f"lora_{tid}_{i+1}" for i in range(1, random.Random(t).randint(2, 3))]
        for j in range(per_tenant):
            L = random.Random(1000 + t * 10 + j).choice([1024, 2048, 4096, 8192])
            prompt = _mk_prompt(L, seed=2000 + t * 100 + j)
            meta = {
                "kind": "multitenant",
                "tenant_id": tid,
                "adapter_id": random.Random(t * 100 + j).choice(adapters),
                "gen_tokens": 64,
            }
            batches.append(
                BatchSpec(
                    prompts=[prompt],
                    qos="throughput",
                    model_id=model_id,
                    seq_lens=[L],
                    target_bucket=L,
                    meta=meta,
                )
            )
    return ScenarioSpec(
        name="multitenant_lora_mix",
        description="Mixed tenants/adapters to stress paging (KV/APC/LoRA) and scheduler.",
        kpi_focus=["fragmentation", "p95_ms", "qps"],
        batches=batches,
        tags=["multitenant", "lora", "paging"],
    )


# --------------------------- registry ---------------------------

def default_scenarios(model_id: str = DEFAULT_MODEL_ID) -> List[ScenarioSpec]:
    """
    Return the canonical set used for v0.1 baselines and v1.1 reporting.
    Order matters for reporting.
    """
    return [
        build_prefill_longcontext(model_id=model_id),
        build_decode_short_prompt(model_id=model_id),
        build_concurrency_sweep(model_id=model_id),
        build_multitenant_lora(model_id=model_id),
    ]


_REGISTRY = {
    "prefill_longcontext": build_prefill_longcontext,
    "decode_256tok": build_decode_short_prompt,
    "concurrency_1_4_8": build_concurrency_sweep,
    "multitenant_lora_mix": build_multitenant_lora,
}


def get_scenario(name: str, **kwargs: Any) -> ScenarioSpec:
    """
    Fetch a scenario by name; kwargs forwarded to builder.
    """
    if name not in _REGISTRY:
        raise KeyError(f"unknown scenario: {name}")
    return _REGISTRY[name](**kwargs)  # type: ignore[call-arg]


# --------------------------- quick smoke ---------------------------

if __name__ == "__main__":  # pragma: no cover
    scns = default_scenarios()
    for s in scns:
        print(s.name, "batches=", len(s.batches), "kpi=", s.kpi_focus)
        # show first batch preview
        if s.batches:
            b = s.batches[0]
            print("  qos=", b.qos, "seq_lens=", b.seq_lens, "meta=", {k: b.meta[k] for k in sorted(b.meta) if k != "gen_tokens"})
