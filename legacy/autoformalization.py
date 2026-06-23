"""
pipeline/autoformalization.py — Stage 3: Autoformalization

Translates informal graph-theory conjectures into Lean 4 formal statements
using an LLM with a Graph-of-Thought (GoT) decomposition strategy.

The process:
  1. Decompose the informal conjecture into sub-goals (GoT step)
  2. Map each sub-goal to mathlib4 definitions
  3. Synthesise a complete Lean 4 theorem statement
  4. Optionally validate via subprocess call to the `lean` binary

Note: this module produces *candidate* Lean 4 code.  Machine-verifiable
correctness is only guaranteed after the Lean kernel successfully elaborates
and type-checks the code (see `_try_lean_check`).
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
import textwrap
from fractions import Fraction
from math import lcm
from pathlib import Path
from typing import List, Optional

import anthropic

from config import Config, CONFIG
from conjecture import Conjecture

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mathlib reference snippets injected into every prompt
# ---------------------------------------------------------------------------

_MATHLIB_PREAMBLE = textwrap.dedent("""
Relevant Lean 4 / mathlib4 definitions (use these, do not invent new names):
  - `SimpleGraph G`           — undirected, loop-free graph on vertex type V
  - `SimpleGraph.chromaticNumber G`  — chromatic number χ(G)
  - `SimpleGraph.independenceNumber G` — independence number α(G)
  - `SimpleGraph.cliqueNum G`  — clique number ω(G)
  - `SimpleGraph.dominationNumber G`  — domination number γ(G)  (if available)
  - `SimpleGraph.matchingNumber G`    — matching number ν(G)
  - `SimpleGraph.maxDegree G`         — maximum degree Δ(G)
  - `SimpleGraph.minDegree G`         — minimum degree δ(G)
  - `Fintype.card V`          — |V(G)|  (number of vertices)
  - `G.edgeFinset.card`       — |E(G)|  (number of edges)
  - `G.IsConnected`           — connectivity predicate
  - `G.IsBipartite`           — bipartiteness predicate

Standard theorem form:
  theorem <name> (V : Type*) [Fintype V] [DecidableEq V]
      (G : SimpleGraph V) [DecidableRel G.Adj] :
      <inequality> := by
    <proof_tactic_or_sorry>
""").strip()


# ---------------------------------------------------------------------------
# Graph-of-Thought decomposition prompt builder
# ---------------------------------------------------------------------------

def _got_decomposition_prompt(conjecture: Conjecture) -> str:
    stmt = conjecture.statement
    ineq = conjecture.inequality

    ineq_detail = ""
    if ineq is not None:
        ineq_detail = (
            f"\nStructured form: {ineq.inv_a}(G) ≤ {ineq.coeff_b}·{ineq.inv_b}(G) + {ineq.offset}"
        )

    return textwrap.dedent(f"""
    You are formalising a graph theory conjecture in Lean 4 with mathlib4.

    Conjecture: "{stmt}"{ineq_detail}

    {_MATHLIB_PREAMBLE}

    Use a Graph-of-Thought approach:
    Step 1 — IDENTIFY the graph invariants involved and their mathlib names.
    Step 2 — WRITE the quantifier structure (∀ graphs G, ∀ vertex types, etc.)
    Step 3 — TRANSLATE the inequality into Lean 4 syntax.
    Step 4 — PRODUCE the final theorem statement with `sorry` as the proof body.

    Respond with the four steps clearly labelled, then end with:
    LEAN4_STATEMENT:
    ```lean
    <complete lean 4 theorem here>
    ```
    """).strip()


def _synthesis_prompt(got_response: str, conjecture: Conjecture) -> str:
    return textwrap.dedent(f"""
    Based on the Graph-of-Thought decomposition below, produce a single, clean,
    compilable Lean 4 theorem statement for the conjecture:
    "{conjecture.statement}"

    GoT analysis:
    {got_response}

    {_MATHLIB_PREAMBLE}

    Requirements:
    - Valid Lean 4 syntax compatible with mathlib4
    - Use `sorry` for the proof body (we only need the statement)
    - Add a brief docstring comment above the theorem
    - Use descriptive theorem name derived from the invariant names

    Output ONLY the Lean 4 code block (no extra commentary):
    ```lean
    <theorem here>
    ```
    """).strip()


# ---------------------------------------------------------------------------
# Formalizer
# ---------------------------------------------------------------------------

class GraphOfThoughtFormalizer:
    """
    Two-stage LLM formalizer:
      Stage A: Graph-of-Thought decomposition
      Stage B: Lean 4 statement synthesis + optional lean binary check
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self._client: Optional[anthropic.Anthropic] = None
        if cfg.anthropic_api_key:
            self._client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
        self._lean_available = self._detect_lean()

    # ----------------------------------------------------------------- API --

    def formalize(self, conjecture: Conjecture) -> Optional[str]:
        """
        Returns a Lean 4 theorem string (with `sorry` proof), or None on failure.
        Updates conjecture.mark_formalized() in place on success.
        """
        if self._client is None:
            logger.warning("[GoT] No Anthropic API key — skipping autoformalization.")
            lean_stub = self._heuristic_lean_statement(conjecture)
            if lean_stub:
                conjecture.mark_formalized(lean_stub)
                return lean_stub
            return None

        try:
            lean_stmt = self._two_stage_formalization(conjecture)
        except Exception as exc:
            logger.error("[GoT] LLM call failed: %s", exc)
            lean_stmt = None

        if lean_stmt:
            # Optional: try to verify with lean binary
            if self._lean_available:
                ok, err = self._try_lean_check(lean_stmt)
                if not ok:
                    logger.warning(
                        "[GoT] Lean type-check failed for %s: %s",
                        conjecture.id, err[:200],
                    )
                    conjecture.metadata["lean_check_error"] = err[:500]
            conjecture.mark_formalized(lean_stmt)
            return lean_stmt

        return None

    def formalize_batch(self, conjectures: List[Conjecture]) -> List[Conjecture]:
        """Formalize a list; returns those successfully formalized."""
        succeeded = []
        for c in conjectures:
            result = self.formalize(c)
            if result:
                succeeded.append(c)
        return succeeded

    # --------------------------------------------------------- two-stage LLM

    def _two_stage_formalization(self, conjecture: Conjecture) -> Optional[str]:
        # Stage A: GoT decomposition
        prompt_a = _got_decomposition_prompt(conjecture)
        got_resp = self._llm_call(prompt_a, temperature=0.3)
        if not got_resp:
            return None

        # Extract lean block from Stage A (some models answer directly)
        lean_direct = _extract_lean_block(got_resp)
        if lean_direct and _looks_valid(lean_direct):
            return lean_direct

        # Stage B: synthesis from GoT output
        prompt_b = _synthesis_prompt(got_resp, conjecture)
        synth_resp = self._llm_call(prompt_b, temperature=0.15)
        if not synth_resp:
            return None

        lean_stmt = _extract_lean_block(synth_resp)
        return lean_stmt if lean_stmt and _looks_valid(lean_stmt) else None

    # ---------------------------------------------------- lean binary check

    def _detect_lean(self) -> bool:
        return bool(shutil.which(self.cfg.lean_binary))

    def _try_lean_check(self, lean_code: str) -> tuple[bool, str]:
        """
        Write a minimal Lean 4 file and attempt to elaborate it.
        Returns (success, error_message).
        """
        imports = "import Mathlib\n\n"
        full_code = imports + lean_code

        with tempfile.NamedTemporaryFile(
            suffix=".lean", mode="w", delete=False
        ) as f:
            f.write(full_code)
            fname = f.name

        try:
            result = subprocess.run(
                [self.cfg.lean_binary, fname],
                capture_output=True,
                text=True,
                timeout=self.cfg.lean_timeout_s,
            )
            ok = result.returncode == 0
            err = (result.stderr or result.stdout)[:2000]
            return ok, err
        except subprocess.TimeoutExpired:
            return False, "lean timed out"
        except FileNotFoundError:
            return False, f"lean binary not found at {self.cfg.lean_binary}"
        finally:
            Path(fname).unlink(missing_ok=True)

    # ---------------------------------------------- heuristic (no LLM) stub

    # Invariant → (aspirational) mathlib4 term. Some names are stubs; the proof
    # body is `sorry`, so this only needs to render a *faithful statement*.
    _INV_MAP = {
        "chi": "G.chromaticNumber", "alpha": "G.independenceNumber",
        "omega": "G.cliqueNum", "nu": "G.matchingNumber",
        "gamma": "G.dominationNumber", "Delta": "G.maxDegree",
        "delta": "G.minDegree", "kappa": "G.vertexConnectivity",
        "lambda": "G.edgeConnectivity", "diam": "G.ediam", "rad": "G.radius",
        "tri": "G.numTriangles", "n": "(Fintype.card V)", "m": "G.edgeFinset.card",
        "degeneracy": "G.degeneracy", "treewidth": "G.treewidth",
        "vertex_cover": "G.vertexCoverNumber", "girth": "G.girth",
    }
    # Graph class → (aspirational) mathlib4 predicate for the hypothesis.
    _CLASS_PROP = {
        "bipartite": "G.Colorable 2", "planar": "G.IsPlanar",
        "regular": "(∃ d, G.IsRegularOfDegree d)", "eulerian": "G.IsEulerian",
        "chordal": "G.IsChordal", "tree": "G.IsTree", "acyclic": "G.IsAcyclic",
        "connected": "G.Connected",
    }

    def _heuristic_lean_statement(self, conjecture: Conjecture) -> Optional[str]:
        """
        Produce a best-effort, *faithful* Lean 4 statement without an LLM call.

        Fractional coefficients are cleared by multiplying through by their common
        denominator (Lean invariants are ℕ-valued), every right-hand term and the
        class hypothesis are included, and we refuse (return None) if any invariant
        has no mapped Lean name rather than emit an incorrect statement.
        """
        ineq = conjecture.inequality
        if ineq is None:
            return None

        refs = [ineq.inv_a, ineq.inv_b] + [name for _, name in ineq.extra_terms]
        if any(r not in self._INV_MAP for r in refs):
            return None

        # Clear denominators so all coefficients become integers.
        fracs = [Fraction(ineq.coeff_a).limit_denominator(100),
                 Fraction(ineq.coeff_b).limit_denominator(100),
                 Fraction(ineq.offset).limit_denominator(100)]
        fracs += [Fraction(c).limit_denominator(100) for c, _ in ineq.extra_terms]
        scale = 1
        for fr in fracs:
            scale = lcm(scale, fr.denominator)

        def term(coeff: int, name: str) -> Optional[str]:
            if coeff == 0:
                return None
            return name if coeff == 1 else f"{coeff} * {name}"

        lhs = term(int(Fraction(ineq.coeff_a) * scale), self._INV_MAP[ineq.inv_a])

        rhs_parts: List[str] = []
        for coeff, name in [(ineq.coeff_b, ineq.inv_b)] + \
                [(c, nm) for c, nm in ineq.extra_terms]:
            t = term(int(Fraction(coeff) * scale), self._INV_MAP[name])
            if t:
                rhs_parts.append(t)
        const = int(Fraction(ineq.offset) * scale)
        rhs = " + ".join(rhs_parts) if rhs_parts else "0"
        if const > 0:
            rhs += f" + {const}"
        elif const < 0:
            rhs += f" - {abs(const)}"

        # Optional graph-class hypothesis.
        hyp_binder = ""
        if ineq.hypothesis:
            prop = self._CLASS_PROP.get(ineq.hypothesis, f"G.Is_{ineq.hypothesis}")
            hyp_binder = f"\n            (hG : {prop})"

        theorem_name = re.sub(r"\W+", "_", f"conj_{conjecture.id}_{ineq.inv_a}_le_{ineq.inv_b}")

        return textwrap.dedent(f"""
        -- Conjecture: {conjecture.statement}
        -- Generated by heuristic autoformalization (no LLM); statement only.
        theorem {theorem_name}
            (V : Type*) [Fintype V] [DecidableEq V]
            (G : SimpleGraph V) [DecidableRel G.Adj]{hyp_binder} :
            {lhs} ≤ {rhs} := by
          sorry
        """).strip()

    # --------------------------------------------------------------- helpers

    def _llm_call(self, prompt: str, temperature: float = 0.3) -> str:
        if self._client is None:
            return ""
        try:
            msg = self._client.messages.create(
                model=self.cfg.model,
                max_tokens=self.cfg.llm_max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error("[GoT] LLM call error: %s", e)
            return ""


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _extract_lean_block(text: str) -> Optional[str]:
    """Extract the first ```lean … ``` code block from a string."""
    import re
    m = re.search(r"```lean\s*(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: look for 'theorem' keyword
    for line in text.splitlines():
        if line.strip().startswith("theorem "):
            idx = text.index(line)
            return text[idx:].strip()
    return None


def _looks_valid(lean_code: str) -> bool:
    """Minimal sanity checks on generated Lean 4 code."""
    has_theorem = "theorem " in lean_code or "lemma " in lean_code
    has_sorry = "sorry" in lean_code or ":= by" in lean_code
    return has_theorem and has_sorry
