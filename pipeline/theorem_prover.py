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
# Ensemble prover: try multiple provers in sequence
# ---------------------------------------------------------------------------

class NeuralProverClient(BaseProver):
    """
    Ensemble: try LeanSubprocess → GoedelProver → DeepSeekProver-V2.
    Returns the first successful result; updates conjecture status in place.
    """

    name = "ensemble"

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self._provers: List[BaseProver] = [
            LeanSubprocessProver(cfg),
            GoedelProver(cfg),
            DeepSeekProverV2(cfg),
        ]

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
