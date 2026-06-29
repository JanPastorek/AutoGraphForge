#!/usr/bin/env python3
"""
tools/prover_shim.py — adapts a vLLM-served DeepSeek-Prover-V2-671B to the
`LocalEndpointProver` HTTP schema (pipeline/theorem_prover.py).

DeepSeek-Prover-V2-671B is too large for the in-process `transformers`
backend (`DeepSeekProverLocal`, sized for the 7B model on one GPU) and is
instead served by vLLM as an OpenAI-compatible endpoint. This shim:

  1. Builds the *same* prompt/cheatsheet `DeepSeekProverLocal` already uses
     (reused directly — not reimplemented) from the incoming Lean statement.
  2. Calls the vLLM server's `/v1/chat/completions` for pass@k sampling
     (attempt 0 greedy, the rest sampled — same policy as the in-process
     backend).
  3. Extracts the Lean code block and kernel-checks it itself with
     `lake env lean` (`LeanSubprocessProver`), trying attempts until one
     verifies or the budget is exhausted — exactly the same loop as
     `DeepSeekProverLocal.prove`, just generating over HTTP instead of
     locally.
  4. Returns `{"proof": ...}` (or `{"proof": None, "error": ...}`).
     `LocalEndpointProver` re-verifies independently on its end — this shim
     never asks to be trusted, it just saves the round-trip of throwing
     unverified candidates over the wire.

Usage:
    VLLM_URL=http://127.0.0.1:8000 VLLM_MODEL=deepseek-prover-v2-671b \\
        .venv-prover/bin/uvicorn tools.prover_shim:app --host 127.0.0.1 --port 8800
"""
import logging
import os
import sys

import requests
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from pipeline.theorem_prover import DeepSeekProverLocal, LeanSubprocessProver

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("prover_shim")

VLLM_URL = os.environ.get("VLLM_URL", "http://127.0.0.1:8000").rstrip("/")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "deepseek-ai/DeepSeek-Prover-V2-671B")
PROVER_NAME = os.environ.get("PROVER_NAME", "deepseek-prover-v2-671b")
# Agentic mode: >0 enables OProver's multi-round compiler-feedback loop (feed the
# prior failed proof + Lean error back each round). 0 keeps the pass@k policy.
AGENTIC_ROUNDS = int(os.environ.get("AGENTIC_ROUNDS", "0"))
MAX_TOKENS = int(os.environ.get("DEEPSEEK_MAX_TOKENS", CONFIG.deepseek_max_new_tokens))

app = FastAPI()
# Never loads weights/torch/CUDA — only used for prompt-building helpers
# (._PROMPT / ._CHEATSHEET / ._retrieved_cheatsheet / ._extract_lean).
_dsl = DeepSeekProverLocal(CONFIG)
_lean = LeanSubprocessProver(CONFIG)


class ProveRequest(BaseModel):
    statement: str
    informal_statement: str = ""
    context: str = ""
    strategy: str = ""
    timeout_s: int = 120

# The survivor goals use CUSTOM graph invariants (dominationNumber, slaterNumber,
# zeroForcingNumber, IsNontrivialClass, …) defined ONLY in our preamble — they are
# out-of-distribution for provers trained on competition math, and grepping
# mathlib (the default cheatsheet) never surfaces their meaning. Inject the whole
# preamble source so the model can see every invariant's definition and unfold it.
def _load_preamble_source() -> str:
    root = getattr(CONFIG, "lean_project_root", "") or "lean_project"
    path = os.path.join(root, "LeanProject", "GraphInvariants.lean")
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return ""

_PREAMBLE_SRC = _load_preamble_source()

# OProver's training-time prompt format (from the OProofs dataset): a "Current
# Task" header, the statement to complete, a plan instruction, a standing
# directive to learn from prior failures, an optional feedback block, and a
# "Reference theorems and proofs:" retrieval slot.
_OPROVER_PROMPT = (
    "**Current Task:**\n"
    "Complete the following Lean 4 code:\n\n"
    "```lean4\n{stmt}\n```\n\n"
    "Before producing the Lean 4 code to formally prove the given theorem, "
    "provide a detailed proof plan outlining the main proof steps and strategies.\n"
    "The plan should highlight key ideas, intermediate lemmas, and proof "
    "structures that will guide the construction of the final formal proof.\n"
    "Please learn from the previous failed attempt and error messages to avoid "
    "similar mistakes.\n\n"
    "{feedback}"
    "Reference theorems and proofs:\n{reference}\n"
)


def _reference(lean_statement: str) -> str:
    """Grounding for the Reference slot: the custom-invariant definitions the
    model must see, plus any mathlib lemmas retrieved for the goal's symbols."""
    parts = []
    if _PREAMBLE_SRC:
        parts.append("-- Definitions of the graph invariants used below "
                     "(from the project preamble):\n" + _PREAMBLE_SRC)
    try:
        cs = _dsl._retrieved_cheatsheet(lean_statement)
        if cs:
            parts.append(cs)
    except Exception:
        pass
    return "\n\n".join(parts)


def _feedback_block(prior: str | None, error: str | None) -> str:
    if not prior:
        return ""
    return ("Previous failed attempt:\n```lean4\n" + prior.strip() + "\n```\n\n"
            "Lean compiler error:\n```\n" + (error or "").strip()[:1500] + "\n```\n\n")


def _call_vllm(prompt: str, sample: bool) -> str | None:
    payload = {
        "model": VLLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": CONFIG.deepseek_temperature if sample else 0.0,
    }
    # Generation can be long (thinking + plan + proof); generous timeout so a
    # candidate is never silently truncated server-side (see run 53595).
    resp = requests.post(f"{VLLM_URL}/v1/chat/completions", json=payload, timeout=2400)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    return DeepSeekProverLocal._extract_lean(text)


def _check(candidate: str | None) -> tuple[bool, str, str | None]:
    """Returns (verified, lean_log, candidate_or_None_if_placeholder)."""
    if not candidate or any(t in candidate for t in
                            ("sorry", "admit", "apply?", "exact?")):
        return False, "model produced no complete proof (placeholder/search tactic)", None
    code = candidate if candidate.lstrip().startswith("import") \
        else "import Mathlib\n" + CONFIG.lean_preamble_import + "\n\n" + candidate
    ok, klog = _lean._run_lean(code)
    return ok, klog, candidate


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/prove")
@app.post("/")
def prove(req: ProveRequest):
    if not _lean._available:
        return {"proof": None, "error": "shim: no Lean binary to kernel-check candidates"}

    if AGENTIC_ROUNDS > 0:
        # OProver-style multi-round repair: each failed attempt's proof + Lean
        # error is fed back so the model can fix it, with invariant definitions
        # grounding the Reference slot.
        prior, error, last_err = None, None, "model produced no complete proof"
        for r in range(AGENTIC_ROUNDS):
            prompt = _OPROVER_PROMPT.format(
                stmt=req.statement, reference=_reference(req.statement),
                feedback=_feedback_block(prior, error))
            try:
                candidate = _call_vllm(prompt, sample=(r > 0))
            except Exception as e:
                last_err = f"vLLM call failed: {e}"
                log.warning("[shim] round %d generation failed: %s", r + 1, e)
                continue
            ok, klog, cand = _check(candidate)
            if cand is None:
                last_err = klog
                continue
            log.info("[shim] round %d candidate (%d chars)", r + 1, len(cand))
            if ok:
                log.info("[shim] round %d ✓ verified", r + 1)
                return {"proof": cand, "model": PROVER_NAME, "rounds": r + 1}
            prior, error = cand, klog
            last_err = f"failed Lean kernel check: {klog[:200]}"
            log.info("[shim] round %d ✗ (%s)", r + 1, klog[:160].replace("\n", " "))
        return {"proof": None, "error": last_err}

    # Default: independent pass@k attempts (attempt 0 greedy, rest sampled).
    last_err = "model produced no complete proof"
    for attempt in range(max(1, CONFIG.deepseek_attempts)):
        try:
            candidate = _call_vllm(_dsl._PROMPT.format(
                cheatsheet=_dsl._retrieved_cheatsheet(req.statement),
                stmt=req.statement), sample=(attempt > 0))
        except Exception as e:
            last_err = f"vLLM call failed: {e}"
            log.warning("[shim] attempt %d generation failed: %s", attempt + 1, e)
            continue
        ok, klog, cand = _check(candidate)
        if cand is None:
            last_err = klog
            continue
        log.info("[shim] attempt %d candidate (%d chars)", attempt + 1, len(cand))
        if ok:
            return {"proof": cand, "model": PROVER_NAME}
        last_err = f"failed Lean kernel check: {klog[:200]}"
        log.info("[shim] attempt %d ✗ (%s)", attempt + 1, klog[:160].replace("\n", " "))
    return {"proof": None, "error": last_err}
