"""
pipeline/hypothesis_gen.py — Stage 1: Hypothesis Generation

Two complementary generators:
  TxGraffitiGenerator   — enumerate invariant pairs, fit linear inequalities,
                          apply Dalmatian dominance filter.
  FunSearchGenerator    — LLM-driven program evolution loop (Anthropic API).
"""

from __future__ import annotations

import itertools
import logging
import math
import re
from typing import Dict, List, Optional, Tuple

import anthropic

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus, Inequality
from graphs.database import GraphDatabase
from graphs.invariants import INVARIANTS, BOOLEANS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TxGraffiti-style generator
# ---------------------------------------------------------------------------

class TxGraffitiGenerator:
    """
    Generate linear-inequality conjectures by the method of TxGraffiti:

    1. For every ordered pair (inv_a, inv_b) of graph invariants and every
       candidate coefficient `coeff`, find the minimal `offset` such that
         coeff_a · inv_a(G)  ≤  coeff · inv_b(G) + offset
       holds for all graphs in the database.

    2. Keep only conjectures that are *tight* on at least one graph
       (equality achieved) — this is the fundamental non-triviality criterion.

    3. Apply the **Dalmatian heuristic**: discard conjecture Q if there exists
       another valid conjecture Q' that is weakly stronger everywhere and
       strictly stronger on at least one graph.  Retains the Pareto frontier.
    """

    def __init__(self, db: GraphDatabase, cfg: Config = CONFIG):
        self.db = db
        self.cfg = cfg

    # ----------------------------------------------------------------- API --

    def generate(self) -> List[Conjecture]:
        logger.info("[TxGraffiti] Generating candidate conjectures…")
        candidates = self._enumerate_candidates()
        logger.info("[TxGraffiti] %d raw candidates before Dalmatian filter", len(candidates))
        survived = self._dalmatian_filter(candidates)
        logger.info("[TxGraffiti] %d conjectures after Dalmatian filter", len(survived))
        return survived[: self.cfg.txgraffiti_max_conjectures]

    # ---------------------------------------------------------------- steps --

    def _enumerate_candidates(self) -> List[Tuple[Conjecture, List[float]]]:
        """Return (Conjecture, slack_vector) pairs for valid, tight inequalities."""
        inv_names = list(INVARIANTS.keys())
        candidates: List[Tuple[Conjecture, List[float]]] = []
        seen_stmts: set = set()

        for inv_a, inv_b in itertools.permutations(inv_names, 2):
            # Gather data points
            data = []
            for entry in self.db.graphs_with_invariants(inv_a, inv_b):
                a_val = entry.invariants[inv_a]
                b_val = entry.invariants[inv_b]
                if not (math.isfinite(a_val) and math.isfinite(b_val)):
                    continue
                data.append((a_val, b_val))

            if len(data) < 3:
                continue

            for coeff in self.cfg.txgraffiti_coefficients:
                # Minimal offset satisfying all data points
                offset = max(
                    0.0,
                    max(a - coeff * b for a, b in data),
                )

                # Reject trivially large offsets
                if offset > self.cfg.txgraffiti_max_offset:
                    continue

                # Compute slack vector
                slacks = [coeff * b + offset - a for a, b in data]

                # Must be tight on at least one graph (Dalmatian pre-condition)
                if min(slacks) > 1e-6:
                    continue

                # Skip if we've seen an identical statement string
                stmt = str(Inequality(inv_a, inv_b, 1.0, coeff, offset))
                if stmt in seen_stmts:
                    continue
                seen_stmts.add(stmt)

                ineq = Inequality(inv_a, inv_b, 1.0, coeff, round(offset, 4))
                tightness = [
                    entry.name
                    for entry in self.db.graphs_with_invariants(inv_a, inv_b)
                    if abs(
                        coeff * entry.invariants[inv_b] + offset
                        - entry.invariants[inv_a]
                    ) < 1e-6
                ]

                c = Conjecture(
                    statement=stmt,
                    inequality=ineq,
                    generation_method="txgraffiti",
                    tightness_witnesses=tightness,
                    score=self._score(slacks, tightness),
                )
                candidates.append((c, slacks))

        return candidates

    def _dalmatian_filter(
        self, candidates: List[Tuple[Conjecture, List[float]]]
    ) -> List[Conjecture]:
        """
        Retain conjecture Q unless there exists Q' such that:
          slack(Q', G) ≤ slack(Q, G) for all G   (Q' at least as strong)
          slack(Q', G) < slack(Q, G) for some G   (Q' strictly stronger somewhere)

        A conjecture with smaller slack is *stronger* (tighter bound).
        """
        n = len(candidates)
        dominated = [False] * n

        for i in range(n):
            if dominated[i]:
                continue
            c_i, sv_i = candidates[i]
            for j in range(n):
                if i == j or dominated[j]:
                    continue
                c_j, sv_j = candidates[j]
                # Skip pairs involving different invariants
                if (
                    c_i.inequality is None
                    or c_j.inequality is None
                    or c_i.inequality.inv_a != c_j.inequality.inv_a
                    or c_i.inequality.inv_b != c_j.inequality.inv_b
                ):
                    continue
                # Can only compare if same length (same data points)
                if len(sv_i) != len(sv_j):
                    continue
                # Does j dominate i?
                if all(sv_j[k] <= sv_i[k] for k in range(len(sv_i))) and any(
                    sv_j[k] < sv_i[k] for k in range(len(sv_i))
                ):
                    dominated[i] = True
                    break

        survived = [c for (c, _), dom in zip(candidates, dominated) if not dom]
        # Sort by score descending
        survived.sort(key=lambda c: c.score, reverse=True)
        return survived

    @staticmethod
    def _score(slacks: List[float], tightness: List[str]) -> float:
        """Higher score = more interesting (tight on many graphs, small slack variance)."""
        tightness_ratio = len(tightness) / max(1, len(slacks))
        avg_slack = sum(slacks) / max(1, len(slacks))
        # Prefer conjectures that are tight often and have small average slack
        return tightness_ratio * 2.0 - avg_slack * 0.1


# ---------------------------------------------------------------------------
# FunSearch-style LLM generator
# ---------------------------------------------------------------------------

class FunSearchGenerator:
    """
    FunSearch-inspired conjecture generation via an evolutionary LLM loop.

    The loop:
      1. Seed the *program database* with a hand-crafted prompt producing
         initial Python functions that compute novel graph quantities.
      2. Execute and score each function against the graph database.
      3. Build an improved prompt from the top-k scored functions.
      4. Ask the LLM for mutations/improvements.
      5. Translate surviving function relationships into Conjecture objects.

    Because we cannot run arbitrary GPU-intensive models locally, we use
    the Anthropic API (claude-opus-4-6) as the LLM backbone.
    """

    _SYSTEM_PROMPT = (
        "You are an expert combinatorialist and automated conjecture-making system. "
        "Generate novel, non-trivial graph-theory conjectures as linear inequalities "
        "between standard graph invariants. Be precise, creative, and mathematical."
    )

    def __init__(self, db: GraphDatabase, cfg: Config = CONFIG):
        self.db = db
        self.cfg = cfg
        self._client: Optional[anthropic.Anthropic] = None
        if cfg.anthropic_api_key:
            self._client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)

    # ----------------------------------------------------------------- API --

    def generate(self) -> List[Conjecture]:
        if self._client is None:
            logger.warning("[FunSearch] No Anthropic API key — skipping LLM generation.")
            return []

        logger.info("[FunSearch] Starting LLM evolution loop…")
        program_db: List[Tuple[str, float]] = []  # (conjecture_text, score)

        # Round 1 — seed
        round1 = self._call_llm(self._seed_prompt(), temperature=0.9)
        parsed1 = self._parse_response(round1)
        scored1 = self._score_conjectures(parsed1)
        program_db.extend(scored1)
        logger.info("[FunSearch] Seed round: %d conjectures", len(scored1))

        # Round 2 — evolve from top-k
        top_k = sorted(program_db, key=lambda x: x[1], reverse=True)[
            : min(3, len(program_db))
        ]
        if top_k:
            round2 = self._call_llm(self._evolution_prompt(top_k), temperature=0.85)
            parsed2 = self._parse_response(round2)
            scored2 = self._score_conjectures(parsed2)
            program_db.extend(scored2)
            logger.info("[FunSearch] Evolution round: %d more conjectures", len(scored2))

        # Build Conjecture objects
        final = sorted(program_db, key=lambda x: x[1], reverse=True)[
            : self.cfg.funsearch_conjectures
        ]
        conjectures = []
        for stmt, score in final:
            c = Conjecture(
                statement=stmt.strip(),
                generation_method="funsearch",
                score=score,
                metadata={"source": "llm_evolution"},
            )
            conjectures.append(c)
        return conjectures

    # ----------------------------------------------------------- LLM calls --

    def _call_llm(self, prompt: str, temperature: float = 0.9) -> str:
        try:
            msg = self._client.messages.create(
                model=self.cfg.model,
                max_tokens=self.cfg.llm_max_tokens,
                system=self._SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error("[FunSearch] LLM call failed: %s", e)
            return ""

    # -------------------------------------------------------------- prompts --

    def _seed_prompt(self) -> str:
        sample = self._db_sample_text(n=8)
        inv_legend = (
            "chi=chromatic_number, alpha=independence_number, omega=clique_number, "
            "gamma=domination_number, nu=matching_number, Delta=max_degree, "
            "delta=min_degree, n=|V|, m=|E|, kappa=vertex_connectivity"
        )
        return f"""Below is a sample of graph invariant values from a database of named graphs.

Invariant legend: {inv_legend}

Database sample:
{sample}

Generate {self.cfg.funsearch_conjectures} novel, non-trivial graph-theory conjectures as linear
inequalities between these invariants. Requirements:
- Form: f(G) ≤ a·g(G) + b  where a ≥ 0, b ≥ 0
- Not trivially true (e.g., not "alpha(G) ≤ n(G)")
- Tight on at least one well-known graph family
- Mathematically interesting

Format EACH conjecture exactly as:
CONJECTURE: <inequality statement using invariant names above>
RATIONALE: <one-sentence mathematical justification>
---"""

    def _evolution_prompt(self, top_k: List[Tuple[str, float]]) -> str:
        elite = "\n".join(
            f"  [{score:.2f}] {stmt}" for stmt, score in top_k
        )
        return f"""Here are the highest-scoring conjectures found so far (score = empirical quality):

{elite}

Generate {self.cfg.funsearch_conjectures} NEW conjectures that are:
1. Different from the above
2. Potentially tighter or more general
3. Still non-trivial and tight on some graph family

Format EACH conjecture exactly as:
CONJECTURE: <inequality>
RATIONALE: <one-sentence reason>
---"""

    # ------------------------------------------------------------ utilities --

    def _db_sample_text(self, n: int = 8) -> str:
        entries = list(self.db)[:n]
        lines = []
        for e in entries:
            inv = e.invariants
            parts = [f"n={inv.get('n','?')}", f"m={inv.get('m','?')}",
                     f"chi={inv.get('chi','?')}", f"alpha={inv.get('alpha','?')}",
                     f"omega={inv.get('omega','?')}", f"gamma={inv.get('gamma','?')}",
                     f"nu={inv.get('nu','?')}", f"Delta={inv.get('Delta','?')}",
                     f"delta={inv.get('delta','?')}"]
            lines.append(f"  {e.name}: " + ", ".join(parts))
        return "\n".join(lines)

    def _parse_response(self, text: str) -> List[str]:
        """Extract CONJECTURE: lines from LLM response."""
        stmts = []
        for line in text.splitlines():
            line = line.strip()
            if line.upper().startswith("CONJECTURE:"):
                stmt = line.split(":", 1)[1].strip()
                if stmt:
                    stmts.append(stmt)
        return stmts

    def _score_conjectures(
        self, stmts: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Score each conjecture by checking it against the graph database.
        A conjecture is valid if it holds on all database graphs we can parse.
        Score = tightness_ratio * 2 - invalid_penalty * 10.

        We attempt a best-effort parse of the inequality string.
        Unparseable conjectures receive a low but non-zero score.
        """
        scored = []
        for stmt in stmts:
            ineq = _try_parse_inequality(stmt)
            if ineq is None:
                scored.append((stmt, 0.1))
                continue

            tight = 0
            total = 0
            valid = True
            for entry in self.db.graphs_with_invariants(ineq.inv_a, ineq.inv_b):
                res = ineq.evaluate(entry.invariants)
                if res is None:
                    continue
                total += 1
                if not res:
                    valid = False
                    break
                if ineq.is_tight(entry.invariants):
                    tight += 1

            if not valid or total == 0:
                scored.append((stmt, 0.0))
            else:
                score = (tight / total) * 2.0
                scored.append((stmt, score))

        return scored


# ---------------------------------------------------------------------------
# Utility: lightweight inequality parser for LLM output
# ---------------------------------------------------------------------------

_KNOWN_INVS = set(INVARIANTS.keys()) | set(BOOLEANS.keys())

def _try_parse_inequality(stmt: str) -> Optional[Inequality]:
    """
    Best-effort parser for strings like:
      "alpha(G) ≤ 2·chi(G) + 1"
      "gamma(G) <= Delta(G)"
      "nu(G) ≤ 0.5 * n(G)"
    Returns None if parsing fails.
    """
    stmt = stmt.replace("≤", "<=").replace("·", "*").replace("×", "*")
    # Match: [coeff *] INV(G) <= [coeff *] INV(G) [+|- offset]
    lhs_re = r"(?:(\d+(?:\.\d+)?)\s*\*\s*)?(\w+)\s*\(G\)"
    rhs_re = r"(?:(\d+(?:\.\d+)?)\s*\*\s*)?(\w+)\s*\(G\)\s*(?:([+-])\s*(\d+(?:\.\d+)?))?"
    pattern = rf"^\s*{lhs_re}\s*<=\s*{rhs_re}\s*$"
    m = re.match(pattern, stmt)
    if not m:
        return None

    coeff_a = float(m.group(1)) if m.group(1) else 1.0
    inv_a = m.group(2)
    coeff_b = float(m.group(3)) if m.group(3) else 1.0
    inv_b = m.group(4)
    sign = m.group(5) or "+"
    offset = float(m.group(6)) if m.group(6) else 0.0
    if sign == "-":
        offset = -offset

    if inv_a not in _KNOWN_INVS or inv_b not in _KNOWN_INVS:
        return None

    return Inequality(inv_a, inv_b, coeff_a, coeff_b, offset)
