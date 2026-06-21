"""
pipeline/theorem_prover.py — Stage 4: Automated Theorem Proving

Provides a clean interface to neural theorem provers (Goedel-Prover,
DeepSeek-Prover-V2).  These systems are cutting-edge research prototypes
with no stable public API as of 2025; the implementations below are
well-documented stubs that wire the correct request/response schema.

To connect a real prover:
  1. Set cfg.prover_api_url and cfg.prover_api_key in config.py (or env vars).
  2. Replace the `_STUB_RESPONSE` logic in `_call_prover_api` with real HTTP calls.
  3. The response schema is documented in `ProverResponse`.

The module also supports a `LeanSubprocessProver` that tries to search for
a proof using the `lean` binary + `exact?` / `decide` tactics (works for
very simple arithmetic statements).
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prover response schema
# ---------------------------------------------------------------------------

@dataclass
class ProverResponse:
    """
    Expected response from a neural theorem prover API.

    Fields match what Goedel-Prover-SB / DeepSeek-Prover-V2 would return
    (schema inferred from published papers; adapt when APIs go public).
    """

    success: bool = False
    proof_text: Optional[str] = None       # complete Lean 4 proof term
    proof_tactics: Optional[str] = None    # tactic proof (if available)
    model_name: str = ""
    tokens_used: int = 0
    elapsed_s: float = 0.0
    error: Optional[str] = None

    # Internal routing
    _stub: bool = False

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "proof_text": self.proof_text,
            "proof_tactics": self.proof_tactics,
            "model_name": self.model_name,
            "tokens_used": self.tokens_used,
            "elapsed_s": self.elapsed_s,
            "error": self.error,
            "stub": self._stub,
        }


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class BaseProver:
    """Abstract interface; concrete provers inherit and override `prove_one`."""

    name: str = "base"

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        raise NotImplementedError

    def prove_batch(self, conjectures: List[Conjecture]) -> List[ProverResponse]:
        return [self.prove(c) for c in conjectures]


# ---------------------------------------------------------------------------
# Goedel-Prover stub
# ---------------------------------------------------------------------------

class GoedelProver(BaseProver):
    """
    Stub for Goedel-Prover (Princeton / open-source frontier ATP).

    Reference: "Goedel-Prover: A Frontier Model for Open-Source Automated
    Theorem Proving" (2025).  Achieves state-of-the-art on miniF2F benchmark.
    Uses a fine-tuned LLM backbone to generate Lean 4 proofs end-to-end.

    To enable:
      - Deploy Goedel-Prover endpoint (self-hosted or API provider)
      - Set cfg.prover_api_url = "https://<your-endpoint>/v1/prove"
      - Set cfg.prover_api_key
    """

    name = "goedel-prover"

    _ENDPOINT_PATH = "/v1/prove"
    _EXPECTED_REQUEST = {
        "formal_statement": "<lean4 theorem string>",
        "informal_statement": "<natural language description>",
        "max_attempts": 8,
        "timeout_s": 120,
    }
    _EXPECTED_RESPONSE_SCHEMA = {
        "success": bool,
        "proof": "str | null",
        "model": "str",
        "num_tokens": int,
        "error": "str | null",
    }

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if conjecture.lean_statement is None:
            return ProverResponse(
                success=False, error="No Lean 4 statement available", model_name=self.name
            )
        t0 = time.time()
        if not self.cfg.prover_api_url:
            return self._stub_response(conjecture, time.time() - t0)

        # TODO: replace with real HTTP call when API is available
        return self._call_prover_api(conjecture, time.time() - t0)

    def _call_prover_api(self, conjecture: Conjecture, elapsed: float) -> ProverResponse:
        """
        Real API call skeleton.  Uncomment and adapt when endpoint is live.
        """
        # import requests
        # payload = {
        #     "formal_statement": conjecture.lean_statement,
        #     "informal_statement": conjecture.statement,
        #     "max_attempts": 8,
        #     "timeout_s": self.cfg.prover_timeout_s,
        # }
        # headers = {"Authorization": f"Bearer {self.cfg.prover_api_key}"}
        # resp = requests.post(
        #     self.cfg.prover_api_url + self._ENDPOINT_PATH,
        #     json=payload, headers=headers,
        #     timeout=self.cfg.prover_timeout_s + 10,
        # )
        # resp.raise_for_status()
        # data = resp.json()
        # return ProverResponse(
        #     success=data["success"],
        #     proof_tactics=data.get("proof"),
        #     model_name=data.get("model", self.name),
        #     tokens_used=data.get("num_tokens", 0),
        #     elapsed_s=elapsed,
        #     error=data.get("error"),
        # )
        return self._stub_response(conjecture, elapsed)

    def _stub_response(self, conjecture: Conjecture, elapsed: float) -> ProverResponse:
        logger.info(
            "[GoedelProver] STUB — would call %s for conjecture %s",
            self.cfg.prover_api_url or "<no URL configured>",
            conjecture.id,
        )
        return ProverResponse(
            success=False,
            error="Goedel-Prover API not configured (stub mode)",
            model_name=self.name,
            elapsed_s=elapsed,
            _stub=True,
        )


# ---------------------------------------------------------------------------
# DeepSeek-Prover-V2 stub
# ---------------------------------------------------------------------------

class DeepSeekProverV2(BaseProver):
    """
    Stub for DeepSeek-Prover-V2.

    Reference: Xin et al. "DeepSeek-Prover-V2: Advancing Formal Mathematical
    Reasoning via Reinforcement Learning for Subgoal Decomposition" (2024).
    Uses RL-trained subgoal decomposition to construct step-by-step Lean 4 proofs.

    The prover decomposes the goal into subgoals, solves each independently,
    and assembles a complete proof.  This architecture is particularly effective
    for multi-step graph-theory lemmas.

    To enable: set cfg.prover_api_url to a DeepSeek-Prover-V2 endpoint.
    """

    name = "deepseek-prover-v2"

    _ENDPOINT_PATH = "/v1/lean4/prove"
    _EXPECTED_REQUEST = {
        "statement": "<lean4 theorem string>",
        "context": "import Mathlib",
        "strategy": "subgoal_decomposition",   # or "best_first_search"
        "max_subgoals": 10,
        "timeout_s": 120,
    }

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if conjecture.lean_statement is None:
            return ProverResponse(
                success=False, error="No Lean 4 statement available", model_name=self.name
            )
        t0 = time.time()
        if not self.cfg.prover_api_url:
            return self._stub_response(conjecture, time.time() - t0)
        return self._call_prover_api(conjecture, time.time() - t0)

    def _call_prover_api(self, conjecture: Conjecture, elapsed: float) -> ProverResponse:
        # TODO: real HTTP call — see GoedelProver._call_prover_api for skeleton
        return self._stub_response(conjecture, elapsed)

    def _stub_response(self, conjecture: Conjecture, elapsed: float) -> ProverResponse:
        logger.info(
            "[DeepSeekProver] STUB — would call endpoint for conjecture %s", conjecture.id
        )
        return ProverResponse(
            success=False,
            error="DeepSeek-Prover-V2 API not configured (stub mode)",
            model_name=self.name,
            elapsed_s=elapsed,
            _stub=True,
        )


# ---------------------------------------------------------------------------
# Lean subprocess prover (local, works for trivial statements)
# ---------------------------------------------------------------------------

class LeanSubprocessProver(BaseProver):
    """
    Attempt to find a proof using the local `lean` binary + simple tactics:
      - `decide`     (works for decidable propositions on finite types)
      - `simp`
      - `norm_num`
      - `omega`      (linear arithmetic over integers/naturals)

    This is NOT a neural prover.  It can close a small set of goals that
    reduce to arithmetic or decidable search, making it useful for sanity-
    checking that the Lean 4 statement compiles and for trivial conjectures.
    """

    name = "lean-subprocess"

    _SIMPLE_TACTICS = ["decide", "simp", "norm_num", "omega", "ring", "tauto"]

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self._available = bool(shutil.which(cfg.lean_binary))

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if not self._available:
            return ProverResponse(
                success=False,
                error=f"Lean binary not found: {self.cfg.lean_binary}",
                model_name=self.name,
            )
        if conjecture.lean_statement is None:
            return ProverResponse(success=False, error="No statement", model_name=self.name)

        t0 = time.time()
        for tactic in self._SIMPLE_TACTICS:
            proof = self._try_tactic(conjecture.lean_statement, tactic)
            if proof:
                elapsed = time.time() - t0
                logger.info(
                    "[LeanSubprocess] Proved %s with tactic `%s`", conjecture.id, tactic
                )
                return ProverResponse(
                    success=True,
                    proof_tactics=proof,
                    model_name=self.name,
                    elapsed_s=elapsed,
                )
        return ProverResponse(
            success=False,
            error="No simple tactic worked",
            model_name=self.name,
            elapsed_s=time.time() - t0,
        )

    def _try_tactic(self, lean_stmt: str, tactic: str) -> Optional[str]:
        """Replace `sorry` with `tactic` and attempt compilation."""
        if "sorry" not in lean_stmt:
            return None
        proof_attempt = lean_stmt.replace("sorry", tactic, 1)
        full_code = "import Mathlib\n\n" + proof_attempt
        ok, _ = self._run_lean(full_code)
        return proof_attempt if ok else None

    def _run_lean(self, code: str) -> tuple[bool, str]:
        with tempfile.NamedTemporaryFile(
            suffix=".lean", mode="w", delete=False
        ) as f:
            f.write(code)
            fname = f.name
        try:
            result = subprocess.run(
                [self.cfg.lean_binary, fname],
                capture_output=True, text=True,
                timeout=self.cfg.lean_timeout_s,
            )
            return result.returncode == 0, (result.stderr + result.stdout)[:2000]
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, str(e)
        finally:
            Path(fname).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Claude prover (Anthropic API) — default neural backend
# ---------------------------------------------------------------------------

class ClaudeProver(BaseProver):
    """
    Prove Lean 4 ``sorry`` goals with an LLM (Anthropic Claude).

    Claude is prompted with the theorem statement and asked to return a complete
    Lean 4 proof. Crucially, the LLM's output is only a *candidate*: when a Lean
    binary is available it is **kernel-verified** (compiled against mathlib) and
    accepted only if it type-checks — so a `success` here is a real proof, not an
    LLM assertion. Without a Lean binary the candidate is returned but
    ``success=False`` (honestly unverified).

    This is the default neural backend: it needs no GPU, only ``ANTHROPIC_API_KEY``.
    For maximal automation on hard goals, swap in a local GPU prover (see
    ``LocalEndpointProver`` and the registry below) — e.g. DeepSeek-Prover-V2
    or Goedel-Prover-V2 served over HTTP.
    """

    name = "claude-prover"

    _SYSTEM = (
        "You are an expert Lean 4 / mathlib4 theorem prover. You are given a "
        "theorem with `sorry`. Return ONLY the full theorem with `sorry` replaced "
        "by a complete, compiling Lean 4 proof, inside a single ```lean code block. "
        "Use mathlib lemmas and tactics (simp, omega, gcongr, nlinarith, exact?, "
        "aesop). Do not invent definitions. If unprovable, return the statement "
        "with `sorry` unchanged."
    )

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self._client = None
        if cfg.anthropic_api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
            except Exception as e:                       # pragma: no cover
                logger.warning("[ClaudeProver] anthropic unavailable: %s", e)
        # reuse the Lean subprocess wrapper purely for kernel verification
        self._lean = LeanSubprocessProver(cfg)

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if conjecture.lean_statement is None:
            return ProverResponse(success=False, error="No Lean 4 statement",
                                  model_name=self.name)
        if self._client is None:
            return ProverResponse(success=False, _stub=True, model_name=self.name,
                                  error="ANTHROPIC_API_KEY not set (claude-prover unavailable)")
        t0 = time.time()
        candidate = self._ask_claude(conjecture)
        elapsed = time.time() - t0
        if not candidate or "sorry" in candidate:
            return ProverResponse(success=False, model_name=self.name, elapsed_s=elapsed,
                                  error="Claude produced no complete proof")
        # Kernel-verify when possible; never claim success on an unchecked proof.
        if self._lean._available:
            ok, log = self._lean._run_lean("import Mathlib\n\n" + candidate)
            return ProverResponse(
                success=ok,
                proof_tactics=candidate if ok else None,
                proof_text=candidate,
                model_name=self.name, elapsed_s=elapsed,
                error=None if ok else f"failed Lean kernel check: {log[:200]}",
            )
        return ProverResponse(
            success=False, proof_text=candidate, model_name=self.name, elapsed_s=elapsed,
            error="unverified: no Lean binary to kernel-check the candidate",
        )

    def _ask_claude(self, conjecture: Conjecture) -> Optional[str]:
        prompt = (
            f"Prove this Lean 4 theorem (informal statement: "
            f"{conjecture.statement!r}).\n\n```lean\n{conjecture.lean_statement}\n```"
        )
        try:
            msg = self._client.messages.create(
                model=self.cfg.model, max_tokens=self.cfg.llm_max_tokens,
                system=self._SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._extract_lean(msg.content[0].text)
        except Exception as e:
            logger.error("[ClaudeProver] API call failed: %s", e)
            return None

    @staticmethod
    def _extract_lean(text: str) -> Optional[str]:
        import re
        m = re.search(r"```(?:lean4?)?\s*(.*?)```", text, re.DOTALL)
        return (m.group(1) if m else text).strip() or None


# ---------------------------------------------------------------------------
# Generic local/HTTP endpoint prover — the seam for GPU provers
# ---------------------------------------------------------------------------

class LocalEndpointProver(BaseProver):
    """
    Documented seam for plugging in a self-hosted GPU prover served over HTTP
    (DeepSeek-Prover-V2, Goedel-Prover-V2, Kimina-Prover, …).

    Set ``cfg.prover_api_url`` to the endpoint and uncomment the HTTP block. The
    request sends the Lean statement; the response is expected to carry a
    ``proof`` string which, if present, is kernel-verified locally when a Lean
    binary is available.
    """

    name = "local-endpoint"

    def __init__(self, cfg: Config = CONFIG, name: Optional[str] = None):
        self.cfg = cfg
        if name:
            self.name = name
        self._lean = LeanSubprocessProver(cfg)

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if conjecture.lean_statement is None:
            return ProverResponse(success=False, error="No statement", model_name=self.name)
        if not self.cfg.prover_api_url:
            return ProverResponse(success=False, _stub=True, model_name=self.name,
                                  error=f"{self.name}: prover_api_url not configured")
        # import requests
        # resp = requests.post(self.cfg.prover_api_url,
        #     json={"statement": conjecture.lean_statement, "context": "import Mathlib",
        #           "timeout_s": self.cfg.prover_timeout_s},
        #     headers={"Authorization": f"Bearer {self.cfg.prover_api_key}"},
        #     timeout=self.cfg.prover_timeout_s + 10)
        # proof = resp.json().get("proof")
        # if proof and self._lean._available:
        #     ok, log = self._lean._run_lean("import Mathlib\n\n" + proof)
        #     return ProverResponse(success=ok, proof_tactics=proof if ok else None,
        #                           proof_text=proof, model_name=self.name)
        return ProverResponse(success=False, _stub=True, model_name=self.name,
                              error=f"{self.name}: HTTP call not enabled (see source)")


# ---------------------------------------------------------------------------
# Backend registry + ensemble
# ---------------------------------------------------------------------------

# name → factory. Add a GPU prover by registering a LocalEndpointProver here
# (or a bespoke class) and listing its name in cfg.prover_backends.
PROVER_REGISTRY = {
    "lean":     lambda cfg: LeanSubprocessProver(cfg),
    "claude":   lambda cfg: ClaudeProver(cfg),
    "goedel":   lambda cfg: GoedelProver(cfg),
    "deepseek": lambda cfg: DeepSeekProverV2(cfg),
    "endpoint": lambda cfg: LocalEndpointProver(cfg),
}


class NeuralProverClient(BaseProver):
    """
    Ensemble of prover backends (order from ``cfg.prover_backends``); returns the
    first verified success and updates conjecture status in place.

    Default order: local Lean tactics → Claude (kernel-verified) → Goedel /
    DeepSeek HTTP stubs. The stubs remain available; point ``cfg.prover_api_url``
    at a served GPU model (or add a backend to ``PROVER_REGISTRY``) to enable
    DeepSeek-Prover-V2 / Goedel-Prover-V2 / other local provers.
    """

    name = "ensemble"

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        backends = getattr(cfg, "prover_backends", None) or ("lean", "claude", "goedel", "deepseek")
        self._provers: List[BaseProver] = []
        for b in backends:
            factory = PROVER_REGISTRY.get(b)
            if factory is None:
                logger.warning("[NeuralProver] unknown prover backend %r — skipped", b)
                continue
            self._provers.append(factory(cfg))

    def prove(self, conjecture: Conjecture) -> ProverResponse:
        if conjecture.lean_statement is None:
            conjecture.mark_proof_failed("No Lean 4 statement")
            return ProverResponse(success=False, error="No statement", model_name=self.name)

        for prover in self._provers:
            resp = prover.prove(conjecture)
            if resp.success and resp.proof_tactics:
                lean_proof = resp.proof_tactics
                conjecture.mark_proven(lean_proof)
                logger.info(
                    "[NeuralProver] %s proved by %s", conjecture.id, prover.name
                )
                return resp

        # All provers failed
        conjecture.mark_proof_failed("All provers failed or returned stub responses")
        logger.info("[NeuralProver] %s: no proof found", conjecture.id)
        return ProverResponse(
            success=False,
            error="All provers failed",
            model_name=self.name,
        )

    def prove_batch(self, conjectures: List[Conjecture]) -> List[ProverResponse]:
        return [self.prove(c) for c in conjectures]
