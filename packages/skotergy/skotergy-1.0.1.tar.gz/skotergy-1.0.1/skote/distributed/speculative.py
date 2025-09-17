# skote/distributed/speculative.py
# Copyright (c) 2025.
# SPDX-License-Identifier: Apache-2.0
"""
Speculative decoding coordinator for Skotergy.

Core idea
---------
Orchestrate two decoders:
- Draft (cheap) proposes up to `max_ahead` tokens.
- Target (expensive) verifies the proposed segment and accepts the longest
  matching prefix; on the first mismatch it emits one fallback token.

This module *does not* implement model math; instead, it coordinates two
callables you provide:

  propose_fn(ctx, max_ahead) -> DraftBundle
  verify_fn(ctx, draft: DraftBundle) -> AcceptBundle

Both callables may update KV caches internally (recommended), so the
coordinator itself remains *stateless w.r.t. model tensors* and only tracks
sequence/token bookkeeping.

Why this shape?
---------------
- Keeps strict compatibility with your existing single-GPU decode and graph
  caches (no invasive changes).
- Enables low-bandwidth multi-device/multi-rank setups: only token vectors and
  small floats flow between draft and target.

Environment knobs
-----------------
SKOTE_SPEC_DECODE        : "1" to enable (default "1")
SKOTE_SPEC_ACCEPT_P      : acceptance threshold in [0,1] (default "0.80")
SKOTE_SPEC_MAX_AHEAD     : max draft lookahead tokens (default "8")
SKOTE_SPEC_MIN_AHEAD     : min draft lookahead tokens (default "1")
SKOTE_SPEC_FORCE_VERIFY_EVERY : force full verify every N accepted tokens (default "0" = off)
SKOTE_SPEC_DIST          : "0"/"1" enable distributed role split (default "0")
SKOTE_SPEC_ROLE          : "auto"|"draft"|"target" when SKOTE_SPEC_DIST=1 (default "auto")

Integration points
------------------
- devicemgr/launcher: choose devices/ranks for draft/target.
- router: you can route user requests to the *coordinator* instead of direct
  decode; the coordinator internally calls propose/verify hooks you bind.
- kv_store: if your hooks update KV, speculative decoding stays consistent
  without explicit KV operations here.

Usage (single process)
----------------------
from skote.distributed.speculative import SpecConfig, SpeculativeOrchestrator

coord = SpeculativeOrchestrator(
    config=SpecConfig.from_env(),
    propose_fn=my_draft_propose,
    verify_fn=my_target_verify,
)

out = coord.generate(ctx=my_ctx, max_new_tokens=128)

Distributed note
----------------
An optional very-light P2P layer is provided via collectives.Coll. If
SKOTE_SPEC_DIST=1, you can run draft and target on separate ranks and exchange
only candidate tokens and the acceptance prefix. See `_dist_roundtrip_*` hooks.
"""

from __future__ import annotations

import os
import time
import math
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

try:
    import torch
except Exception as e:  # pragma: no cover
    raise RuntimeError("speculative.py requires PyTorch for tensor transport") from e

# Optional Skotergy logger
def _get_logger(name: str) -> logging.Logger:
    try:
        from skote import get_logger  # type: ignore
        return get_logger(name)
    except Exception:
        logging.basicConfig(level=os.environ.get("SKOTE_LOG_LEVEL", "INFO"))
        return logging.getLogger(name)

LOG = _get_logger("skotergy.speculative")


# ----------------------------- Data models -----------------------------

@dataclass
class SpecConfig:
    enabled: bool = True
    accept_p: float = 0.80
    max_ahead: int = 8
    min_ahead: int = 1
    force_verify_every: int = 0  # 0 = disabled
    # Distributed (optional)
    dist: bool = False
    role: str = "auto"  # auto|draft|target

    @staticmethod
    def from_env() -> "SpecConfig":
        def _env_true(name: str, default: bool) -> bool:
            v = os.environ.get(name)
            if v is None:
                return default
            return v.strip() in ("1", "true", "True", "YES", "yes")

        def _env_int(name: str, default: int) -> int:
            try:
                return int(os.environ.get(name, str(default)))
            except Exception:
                return default

        def _env_float(name: str, default: float) -> float:
            try:
                return float(os.environ.get(name, str(default)))
            except Exception:
                return default

        return SpecConfig(
            enabled=_env_true("SKOTE_SPEC_DECODE", True),
            accept_p=_env_float("SKOTE_SPEC_ACCEPT_P", 0.80),
            max_ahead=max(1, _env_int("SKOTE_SPEC_MAX_AHEAD", 8)),
            min_ahead=max(1, _env_int("SKOTE_SPEC_MIN_AHEAD", 1)),
            force_verify_every=max(0, _env_int("SKOTE_SPEC_FORCE_VERIFY_EVERY", 0)),
            dist=_env_true("SKOTE_SPEC_DIST", False),
            role=os.environ.get("SKOTE_SPEC_ROLE", "auto").lower(),
        )


@dataclass
class DraftBundle:
    """
    Output from the draft model.
    tokens: LongTensor [L] (proposed token ids)
    logprobs: FloatTensor [L] (optional; -inf for unknown)
    aux: arbitrary side info (e.g., per-step top-k, entropy)
    """
    tokens: torch.Tensor
    logprobs: Optional[torch.Tensor] = None
    aux: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AcceptBundle:
    """
    Decision from the target model.
    accept_prefix_len: number of leading tokens accepted from draft (0..L)
    fallback_token: a single token id to append when mismatch occurs (None if fully accepted)
    stats: arbitrary info (e.g., acceptance probs, verifier timing)
    """
    accept_prefix_len: int
    fallback_token: Optional[int]
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecodeContext:
    """
    Minimal decode context the hooks may need; extend as you wish.
    - seq_id: unique sequence identifier (for KV scoping)
    - device: preferred device for *target* verification (draft may have its own)
    - meta: anything else (prompt length, user id, routing hints, etc.)
    """
    seq_id: int
    device: torch.device
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    tokens: torch.Tensor
    meta: Dict[str, Any]


# ----------------------------- Coordinator -----------------------------

ProposeFn = Callable[[DecodeContext, int], DraftBundle]
VerifyFn  = Callable[[DecodeContext, DraftBundle], AcceptBundle]

class SpeculativeOrchestrator:
    """
    Coordinates speculative decoding. Stateless w.r.t. model tensors/KV; the
    provided propose/verify hooks are expected to manage KV and caching.

    Contract for hooks (recommended semantics)
    ------------------------------------------
    - propose_fn(ctx, max_ahead) returns up to `max_ahead` tokens proposed by the draft.
      The hook may run a decode loop internally and update draft KV.

    - verify_fn(ctx, draft) computes accept_prefix_len and (if needed) one fallback token,
      updating the target KV to reflect all *accepted* tokens and/or the fallback token.
      The coordinator relies on that side effect to keep the target state consistent.
    """

    def __init__(self,
                 config: SpecConfig,
                 propose_fn: ProposeFn,
                 verify_fn: VerifyFn,
                 coll: Optional["Coll"] = None) -> None:
        from skote.distributed.collectives import Coll  # local import to avoid hard dep at import time
        self.cfg = config
        self.propose_fn = propose_fn
        self.verify_fn = verify_fn
        self.coll: Coll = coll or Coll()
        self._check_dist_role()

    # ---- public API ----

    def generate(self, ctx: DecodeContext, max_new_tokens: int) -> GenerationResult:
        """
        Run speculative decoding for `max_new_tokens`, returning concatenated token ids.
        The hooks handle actual model execution and KV updates.

        Returns
        -------
        GenerationResult(tokens=[N], meta={acceptance_rate, steps, verify_calls, ...})
        """
        assert max_new_tokens > 0
        if not self.cfg.enabled:
            # Degenerate: ask target to verify an empty draft and produce tokens itself
            # (your verify_fn can interpret empty draft as "do one step of target")
            return self._greedy_target_only(ctx, max_new_tokens)

        accepted: List[int] = []
        steps = 0
        verify_calls = 0
        fully_accepted_segments = 0
        t_start = time.time()

        force_every = self.cfg.force_verify_every or 0
        since_force = 0

        while len(accepted) < max_new_tokens:
            remaining = max_new_tokens - len(accepted)
            look = int(min(max(self.cfg.min_ahead, 1), self.cfg.max_ahead, remaining))

            # Optional: periodically reduce lookahead to force a verification heartbeat
            if force_every > 0 and since_force >= force_every:
                look = max(1, min(look, 2))  # small probe
                since_force = 0

            # 1) Draft proposes
            draft = self._propose(ctx, look)

            # 2) Target verifies
            accept = self._verify(ctx, draft)
            verify_calls += 1

            # 3) Commit decisions
            L = int(max(0, min(accept.accept_prefix_len, draft.tokens.numel())))
            if L > 0:
                accepted.extend(draft.tokens[:L].tolist())
                since_force += L
            if L == draft.tokens.numel():
                fully_accepted_segments += 1

            if L < draft.tokens.numel():
                # Mismatch at position L: append fallback token from target
                fb = accept.fallback_token
                if fb is None:
                    # Safety: ask target to emit one token
                    fb = self._fallback_one(ctx)
                accepted.append(int(fb))
                since_force = 0  # reset force counter after explicit target step

            steps += 1

        dt = time.time() - t_start
        meta = {
            "acceptance_rate": float(len(accepted)) / float(max_new_tokens),
            "segments": steps,
            "verify_calls": verify_calls,
            "fully_accepted_segments": fully_accepted_segments,
            "elapsed_ms": dt * 1000.0,
            "spec_cfg": {
                "accept_p": self.cfg.accept_p,
                "max_ahead": self.cfg.max_ahead,
                "min_ahead": self.cfg.min_ahead,
                "force_verify_every": self.cfg.force_verify_every,
                "dist": self.cfg.dist,
                "role": self.cfg.role,
            }
        }
        return GenerationResult(tokens=torch.tensor(accepted, dtype=torch.long, device=ctx.device), meta=meta)

    # ---- hook wrappers (local or distributed) ----

    def _propose(self, ctx: DecodeContext, look: int) -> DraftBundle:
        """
        Local call by default. If SKOTE_SPEC_DIST=1 and role separation is configured,
        this may perform a roundtrip over Coll.
        """
        if not self.cfg.dist:
            return self.propose_fn(ctx, look)

        # --- Distributed draft path (optional) ---
        # Protocol: target rank asks draft rank to propose; receives tokens (and optional logprobs).
        role = self._role()
        if role == "draft":
            # Draft role: wait for request, run propose, send back.
            return self._dist_wait_and_propose(ctx, look)
        else:
            # Target role: actively request draft proposal from peer.
            return self._dist_request_proposal(ctx, look)

    def _verify(self, ctx: DecodeContext, draft: DraftBundle) -> AcceptBundle:
        """
        Local call by default. In distributed mode, the target role runs verification
        and returns a small AcceptBundle (prefix length + optional fallback token).
        """
        if not self.cfg.dist:
            return self.verify_fn(ctx, draft)

        role = self._role()
        if role == "target":
            # Target role: verify and send decision back to draft (or coordinator)
            return self._dist_verify_and_reply(ctx, draft)
        else:
            # Draft role: send draft to target and wait for accept decision
            return self._dist_send_and_wait_accept(ctx, draft)

    # ---- degenerate helpers ----

    def _greedy_target_only(self, ctx: DecodeContext, max_new_tokens: int) -> GenerationResult:
        """
        When speculative is disabled, we still provide a consistent generation loop
        by repeatedly calling verify_fn with empty drafts (hook decides to emit one).
        """
        tokens: List[int] = []
        for _ in range(max_new_tokens):
            empty = DraftBundle(tokens=torch.empty(0, dtype=torch.long, device=ctx.device))
            dec = self.verify_fn(ctx, empty)
            tok = dec.fallback_token
            if tok is None:
                # If hook returns None, we have no token; avoid dead-loop:
                tok = self._fallback_one(ctx)
            tokens.append(int(tok))
        return GenerationResult(tokens=torch.tensor(tokens, dtype=torch.long, device=ctx.device),
                                meta={"acceptance_rate": 0.0, "segments": max_new_tokens, "verify_calls": max_new_tokens})

    def _fallback_one(self, ctx: DecodeContext) -> int:
        """
        Ask target to emit exactly one token by verifying an empty draft.
        """
        dec = self.verify_fn(ctx, DraftBundle(tokens=torch.empty(0, dtype=torch.long, device=ctx.device)))
        if dec.fallback_token is None:
            raise RuntimeError("verify_fn did not provide a fallback token on empty draft")
        return int(dec.fallback_token)

    # ---- role helpers ----

    def _check_dist_role(self) -> None:
        if not self.cfg.dist:
            return
        from skote.distributed.collectives import Coll
        if not isinstance(self.coll, Coll) or self.coll.world_size <= 1:
            LOG.warning("SKOTE_SPEC_DIST=1 but distributed world_size<=1; falling back to local mode.")
            self.cfg.dist = False

    def _role(self) -> str:
        """
        Derive role in distributed mode. 'auto' assigns even ranks as 'draft', odd as 'target'.
        """
        if not self.cfg.dist:
            return "local"
        if self.cfg.role in ("draft", "target"):
            return self.cfg.role
        # auto
        return "draft" if (self.coll.rank % 2 == 0) else "target"

    # -------------------- Distributed roundtrips (optional) --------------------

    # The following is a minimal low-bandwidth protocol. It uses object broadcast for
    # meta and tensor send/recv for payload. In practice you might map draft<->target
    # to specific ranks and reuse tags per seq_id.

    def _dist_wait_and_propose(self, ctx: DecodeContext, look: int) -> DraftBundle:
        """
        Draft role waits for a 'proposal request' then replies with token tensor (and optional logprobs).
        In the coordinator's context, we implement a blocking local call by internally
        running propose_fn and returning its bundle.
        """
        # In library-coordinated mode, we simply run local hook (draft side).
        # If you deploy a true two-process split, wire this with P2P recv/send.
        return self.propose_fn(ctx, look)

    def _dist_request_proposal(self, ctx: DecodeContext, look: int) -> DraftBundle:
        """
        Target role requests draft to generate candidates.
        Here we call local hook as default; to split processes, replace with P2P.
        """
        return self.propose_fn(ctx, look)

    def _dist_verify_and_reply(self, ctx: DecodeContext, draft: DraftBundle) -> AcceptBundle:
        """
        Target role verifies and returns decision. Replace with P2P send when splitting ranks.
        """
        return self.verify_fn(ctx, draft)

    def _dist_send_and_wait_accept(self, ctx: DecodeContext, draft: DraftBundle) -> AcceptBundle:
        """
        Draft role sends draft bundle and waits for acceptance decision.
        Default: local call.
        """
        return self.verify_fn(ctx, draft)


# ----------------------------- Adapters (optional) -----------------------------

class SpeculativeAdapters:
    """
    Helper builders to turn common decode APIs into `propose_fn` / `verify_fn`.

    We purposely keep signatures generic because different engines expose
    different generate/step interfaces. Use these as templates.
    """

    @staticmethod
    def make_propose_from_step(step_fn: Callable[[DecodeContext, int], Tuple[torch.Tensor, Optional[torch.Tensor]]]
                               ) -> ProposeFn:
        """
        Wrap a step_fn that returns (tokens[<=L], logprobs[<=L] or None).
        """
        def _propose(ctx: DecodeContext, max_ahead: int) -> DraftBundle:
            toks, lps = step_fn(ctx, max_ahead)
            if not isinstance(toks, torch.Tensor):
                toks = torch.tensor(toks, dtype=torch.long, device=ctx.device)
            if lps is not None and not isinstance(lps, torch.Tensor):
                lps = torch.tensor(lps, dtype=torch.float32, device=ctx.device)
            return DraftBundle(tokens=toks, logprobs=lps)
        return _propose

    @staticmethod
    def make_verify_from_step(verify_step_fn: Callable[[DecodeContext, DraftBundle], Tuple[int, Optional[int], Dict[str, Any]]]
                              ) -> VerifyFn:
        """
        Wrap a verify_step_fn that returns (accept_prefix_len, fallback_token, stats).
        """
        def _verify(ctx: DecodeContext, draft: DraftBundle) -> AcceptBundle:
            L, fb, stats = verify_step_fn(ctx, draft)
            return AcceptBundle(accept_prefix_len=int(L), fallback_token=(int(fb) if fb is not None else None), stats=stats or {})
        return _verify


# ----------------------------- Quick self-test -----------------------------

if __name__ == "__main__":
    """
    Synthetic demo with a toy 'model':
      - Draft proposes random tokens.
      - Target accepts each token with probability cfg.accept_p; on reject emits fb=999.

    Useful to check coordinator logic without real models.
    """
    import random

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    cfg = SpecConfig.from_env()
    cfg.enabled = True
    cfg.max_ahead = int(os.environ.get("SKOTE_SPEC_MAX_AHEAD", 8))
    cfg.accept_p = float(os.environ.get("SKOTE_SPEC_ACCEPT_P", 0.8))

    vocab = 32000

    def toy_propose(ctx: DecodeContext, max_ahead: int) -> DraftBundle:
        L = random.randint(1, max_ahead)
        toks = torch.randint(0, vocab, (L,), device=device)
        lps = torch.log(torch.full((L,), 1.0 / vocab, device=device))
        return DraftBundle(tokens=toks, logprobs=lps, aux={"toy": True})

    def toy_verify(ctx: DecodeContext, draft: DraftBundle) -> AcceptBundle:
        # Accept first k~Binomial with p=accept_p; reject at k if k < L
        L = draft.tokens.numel()
        k = 0
        for i in range(L):
            if random.random() < cfg.accept_p:
                k += 1
            else:
                break
        fb = None if k == L else int(torch.randint(0, vocab, (1,), device=device).item())
        return AcceptBundle(accept_prefix_len=k, fallback_token=fb, stats={"toy": True})

    coord = SpeculativeOrchestrator(cfg, toy_propose, toy_verify)
    ctx = DecodeContext(seq_id=1, device=device, meta={"demo": True})
    out = coord.generate(ctx, max_new_tokens=64)
    print("Generated tokens:", out.tokens.shape[0], "acceptance_rate:", f"{out.meta['acceptance_rate']:.2f}",
          "segments:", out.meta["segments"], "verify_calls:", out.meta["verify_calls"])
