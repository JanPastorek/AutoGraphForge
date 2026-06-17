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
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import anthropic
import numpy as np

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus, Inequality
from graphs.database import GraphDatabase
from graphs.invariants import INVARIANTS, BOOLEANS
from pipeline.novelty import annotate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TxGraffiti-style generator
# ---------------------------------------------------------------------------

class TxGraffitiGenerator:
    """
    Generate linear-inequality conjectures by the method of TxGraffiti:

    1. For every ordered LHS invariant inv_a and RHS invariant tuple
       (inv_b[, inv_c …]) and every candidate coefficient combination, find the
       minimal `offset` such that
         inv_a(G)  ≤  Σ coeffᵢ · invᵢ(G)  +  offset
       holds for all graphs in the (optionally class-restricted) database.

    2. **Graph-class conditioning** — in addition to the unconditioned sweep,
       repeat the fit over each graph class P (bipartite, regular, planar, …),
       yielding conjectures of the form "for all G with P(G): inv_a(G) ≤ …".
       Boolean properties are used *only* as such hypotheses, never as numeric
       terms in the linear fit.

    3. **Multivariable bounds** — the RHS may be a sum of several invariants
       (controlled by ``cfg.txgraffiti_max_rhs_terms``), not just one.

    4. Keep only conjectures that are *tight* on at least one graph (the
       non-triviality criterion) and, unless disabled, are not an equality
       across the whole class (within-class identities are discarded).

    5. Apply the **Dalmatian heuristic** (per comparable bucket): discard
       conjecture Q if another conjecture over the same LHS / RHS-set / class is
       weakly stronger everywhere and strictly stronger somewhere.
    """

    _TOL = 1e-6

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

        # Known-theorem novelty filter: tag each conjecture, optionally hiding
        # rediscoveries of classical results so only novel bounds remain.
        novel, known = annotate(survived)
        if known:
            logger.info(
                "[Novelty] %d/%d conjectures rediscover known theorems "
                "(e.g. %s)",
                len(known), len(survived),
                known[0].metadata.get("matched_theorem", "?"),
            )
        if self.cfg.txgraffiti_filter_known:
            survived = novel
            logger.info("[Novelty] %d novel conjectures retained", len(survived))

        return survived[: self.cfg.txgraffiti_max_conjectures]

    # --------------------------------------------------------- data loading --

    def _load_arrays(self):
        """Vectorise the database into per-invariant numpy arrays (NaN = missing)."""
        entries = list(self.db)
        names = [e.name for e in entries]
        inv_names = list(self.db.invariant_names()) if hasattr(self.db, "invariant_names") \
            else list(INVARIANTS.keys())
        numeric = [k for k in inv_names if k in INVARIANTS]
        bool_props = [k for k in inv_names if k in BOOLEANS]
        vals = {
            inv: np.array([e.invariants.get(inv, np.nan) for e in entries], dtype=float)
            for inv in numeric
        }
        bvals = {
            b: np.array([e.invariants.get(b, np.nan) for e in entries], dtype=float)
            for b in bool_props
        }
        return names, numeric, bool_props, vals, bvals

    def _contexts(self, bool_props, bvals, n_graphs):
        """Yield (hypothesis, boolean-mask) pairs: unconditioned + each class."""
        contexts = [(None, np.ones(n_graphs, dtype=bool))]
        if self.cfg.txgraffiti_condition_on_classes:
            for b in bool_props:
                mask = bvals[b] >= 0.5
                if int(mask.sum()) >= self.cfg.txgraffiti_min_support:
                    contexts.append((b, mask))
        return contexts

    # ---------------------------------------------------------------- steps --

    def _enumerate_candidates(self):
        """Return (Conjecture, slack_vector, bucket_key) tuples for valid fits."""
        names, numeric, bool_props, vals, bvals = self._load_arrays()
        n_graphs = len(names)
        if n_graphs == 0 or len(numeric) < 2:
            return []

        finite = {inv: np.isfinite(vals[inv]) for inv in numeric}
        coeffs = tuple(self.cfg.txgraffiti_coefficients)
        candidates: List[Tuple[Conjecture, np.ndarray, tuple]] = []
        seen: set = set()

        for hyp, cmask in self._contexts(bool_props, bvals, n_graphs):
            # --- two-variable bounds: inv_a ≤ coeff·inv_b + offset ---
            for inv_a, inv_b in itertools.permutations(numeric, 2):
                valid = cmask & finite[inv_a] & finite[inv_b]
                if int(valid.sum()) < self.cfg.txgraffiti_min_support:
                    continue
                self._fit(
                    candidates, seen, names, valid, hyp, inv_a,
                    vals[inv_a][valid], [(inv_b, vals[inv_b][valid])], coeffs,
                )

            # --- multivariable bounds: inv_a ≤ c_b·inv_b + c_c·inv_c + offset ---
            if self.cfg.txgraffiti_multivariable and self.cfg.txgraffiti_max_rhs_terms >= 2:
                for inv_a in numeric:
                    rest = [x for x in numeric if x != inv_a]
                    for inv_b, inv_c in itertools.combinations(rest, 2):
                        valid = cmask & finite[inv_a] & finite[inv_b] & finite[inv_c]
                        if int(valid.sum()) < self.cfg.txgraffiti_min_support:
                            continue
                        # A term that is constant across this class only shifts
                        # the offset — it adds no real multivariable structure
                        # (e.g. tri ≡ 0 on bipartite graphs). Skip such terms.
                        if (np.ptp(vals[inv_b][valid]) < 1e-9
                                or np.ptp(vals[inv_c][valid]) < 1e-9):
                            continue
                        self._fit(
                            candidates, seen, names, valid, hyp, inv_a,
                            vals[inv_a][valid],
                            [(inv_b, vals[inv_b][valid]), (inv_c, vals[inv_c][valid])],
                            coeffs,
                        )

        return candidates

    def _fit(self, candidates, seen, names, valid_mask, hyp, inv_a, a, rhs_terms, coeffs):
        """Fit minimal-offset bounds over every coefficient combination for rhs_terms.

        ``rhs_terms`` is a list of (inv_name, value_array) aligned with ``a``.
        Appends accepted (Conjecture, slack_vector, bucket_key) tuples.
        """
        tol = self._TOL
        max_off = self.cfg.txgraffiti_max_offset
        valid_idx = np.nonzero(valid_mask)[0]
        bucket_key = (hyp, inv_a, frozenset(name for name, _ in rhs_terms))

        # Skip degenerate bounds: a constant LHS within the class is just a
        # threshold ("c ≤ …"), and an all-constant RHS reduces to "f ≤ const" —
        # both are class artifacts (e.g. κ = λ = 1 on trees), not relations.
        if np.ptp(a) < 1e-9:
            return
        if all(np.ptp(arr) < 1e-9 for _, arr in rhs_terms):
            return

        for combo in itertools.product(coeffs, repeat=len(rhs_terms)):
            rhs = np.zeros_like(a)
            for coeff, (_, arr) in zip(combo, rhs_terms):
                rhs += coeff * arr
            offset = max(0.0, float(np.max(a - rhs)))
            if offset > max_off:
                continue

            slacks = rhs + offset - a
            smin = float(slacks.min())
            smax = float(slacks.max())
            if smin > tol:                       # not tight anywhere → not a frontier bound
                continue
            if self.cfg.txgraffiti_drop_identities and smax < tol:
                continue                          # equality on the whole class → identity

            extra = [(combo[k], rhs_terms[k][0]) for k in range(1, len(rhs_terms))]
            ineq = Inequality(
                inv_a, rhs_terms[0][0], 1.0, combo[0], round(offset, 4),
                extra_terms=extra, hypothesis=hyp,
            )
            stmt = str(ineq)
            if stmt in seen:
                continue
            seen.add(stmt)

            tight_local = np.nonzero(np.abs(slacks) < tol)[0]
            tightness = [names[valid_idx[i]] for i in tight_local]
            c = Conjecture(
                statement=stmt,
                inequality=ineq,
                generation_method="txgraffiti",
                tightness_witnesses=tightness,
                score=self._score(slacks, tightness, hyp),
                metadata={"hypothesis": hyp, "context_size": int(valid_mask.sum())},
            )
            candidates.append((c, slacks, bucket_key))

    def _dalmatian_filter(self, candidates) -> List[Conjecture]:
        """
        Retain conjecture Q unless there exists Q' (same LHS invariant, same RHS
        invariant-set, same graph class) such that:
          slack(Q', G) ≤ slack(Q, G) for all G   (Q' at least as strong)
          slack(Q', G) < slack(Q, G) for some G   (Q' strictly stronger somewhere)

        Smaller slack ⇒ stronger (tighter) bound. Candidates are bucketed by the
        comparison key first, so dominance is only checked within comparable sets.
        """
        buckets: Dict[tuple, list] = defaultdict(list)
        for item in candidates:
            buckets[item[2]].append(item)

        survived: List[Conjecture] = []
        for items in buckets.values():
            # Collapse coefficient variants that yield an identical slack vector
            # (e.g. different multiples of a class-constant term) to one bound.
            unique: Dict[tuple, tuple] = {}
            for it in items:
                sig = tuple(np.round(it[1], 6))
                if sig not in unique or it[0].score > unique[sig][0].score:
                    unique[sig] = it
            items = list(unique.values())

            k = len(items)
            svs = [it[1] for it in items]
            dominated = [False] * k
            for i in range(k):
                if dominated[i]:
                    continue
                for j in range(k):
                    if i == j or dominated[j]:
                        continue
                    if len(svs[i]) != len(svs[j]):
                        continue
                    if np.all(svs[j] <= svs[i] + 1e-12) and np.any(svs[j] < svs[i] - 1e-12):
                        dominated[i] = True
                        break
            for (c, _, _), dom in zip(items, dominated):
                if not dom:
                    survived.append(c)

        survived.sort(key=lambda c: c.score, reverse=True)
        return survived

    @staticmethod
    def _score(slacks, tightness, hyp=None) -> float:
        """Higher score = more interesting (tight on many graphs, small avg slack)."""
        n = len(slacks)
        tightness_ratio = len(tightness) / max(1, n)
        avg_slack = float(np.mean(slacks)) if n else 0.0
        score = tightness_ratio * 2.0 - avg_slack * 0.1
        if hyp is not None:
            score += 0.25   # nudge class-conditioned results up — likelier to be novel
        return score


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
