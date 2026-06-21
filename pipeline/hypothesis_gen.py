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
import os
import re
from collections import defaultdict
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

import anthropic
import numpy as np
import pandas as pd

# The real TxGraffiti package: we drive its generators (convex_hull / ratios /
# linear_programming) and its Dalmatian/Morgan dominance filters instead of the
# in-house reimplementation, then translate its native Conjecture objects back
# into this pipeline's Conjecture/Inequality model so every downstream stage
# (novelty filter, adversarial refutation, parallel loop) is preserved.
from txgraffiti.logic import Property, Predicate, TRUE
from txgraffiti.logic import Inequality as TxInequality
from txgraffiti.generators import convex_hull, ratios, linear_programming
from txgraffiti.processing import (
    remove_duplicates,
    filter_with_dalmatian,
    filter_with_morgan,
)

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus, Inequality
from graphs.database import GraphDatabase
from graphs.invariants import INVARIANTS, BOOLEANS
from pipeline.novelty import annotate

logger = logging.getLogger(__name__)

# TxGraffiti's @safe_generator logs an ERROR for every degenerate hull / missing
# LP solver; over a full invariant sweep that is hundreds of thousands of benign
# messages, so silence that generator-level logger.
logging.getLogger("txgraffiti.generators").setLevel(logging.CRITICAL)


def _ensure_lp_solver() -> bool:
    """Make an LP solver discoverable for txgraffiti's `linear_programming`.

    TxGraffiti only looks for a ``cbc``/``glpsol`` executable on PATH, but the
    ``pulp`` dependency already ships a CBC binary. Put that binary's directory
    on PATH so ``shutil.which('cbc')`` finds it — no system install required.
    Returns True if a solver is available.
    """
    import shutil
    if shutil.which("cbc") or shutil.which("glpsol"):
        return True
    try:
        import pulp
        cbc = pulp.PULP_CBC_CMD(msg=0).path
        if cbc:
            cbc = os.path.realpath(cbc)          # pulp's path has an unresolved '..'
            if os.path.isfile(cbc) and os.access(cbc, os.X_OK):
                os.environ["PATH"] = (os.path.dirname(cbc) + os.pathsep
                                      + os.environ.get("PATH", ""))
                return shutil.which("cbc") is not None
    except Exception:
        pass
    return False


# convex_hull + ratios give the optimal-coefficient upper/lower/ratio bounds;
# linear_programming (sum-of-slacks LP) is added when a CBC/GLPK solver is found.
_TX_GENERATORS = [convex_hull, ratios]
if _ensure_lp_solver():
    _TX_GENERATORS.append(linear_programming)
else:  # pragma: no cover
    logger.warning("[TxGraffiti] no LP solver found — linear_programming disabled")
_TX_GENERATORS = tuple(_TX_GENERATORS)


# ---------------------------------------------------------------------------
# TxGraffiti-style generator
# ---------------------------------------------------------------------------

class TxGraffitiGenerator:
    """
    Linear-inequality conjecture generator backed by the **TxGraffiti package**.

    The bound-fitting (``convex_hull`` and ``ratios`` generators) and the
    dominance filtering (``filter_with_dalmatian`` / ``filter_with_morgan``) are
    the real ``txgraffiti`` implementations — this class no longer reimplements
    them. On top of the package it keeps this pipeline's own extensions:

    * **Graph-class conditioning** — every boolean invariant becomes a TxGraffiti
      hypothesis predicate, giving "for all G with P(G): …" bounds.
    * **Multivariable right-hand sides** — feature tuples of size up to
      ``cfg.txgraffiti_max_rhs_terms`` (``cfg.txgraffiti_multivariable``).
    * **Exact-or-blank masking** — every (target, features, class) generator call
      runs only on rows whose values are present (our data has blanks), which the
      bundled ``txgraffiti2``/``ConjecturePlayground`` drivers do not handle.
    * **LHS sharding** (``lhs_subset``) for the parallel driver.
    * **Translation** of each surviving native ``txgraffiti`` ``Conjecture`` back
      into this pipeline's ``Conjecture``/``Inequality`` (recovering rational RHS
      coefficients), so the novelty filter, the adversarial refutation pool and
      the dynamic-database loop are all preserved unchanged.
    """

    def __init__(self, db: GraphDatabase, cfg: Config = CONFIG):
        self.db = db
        self.cfg = cfg
        # Restrict the LHS (target) invariants of the sweep to this subset, for
        # parallel sharding. None ⇒ all numeric invariants. Dominance is per
        # target, so different LHS shards are independent.
        self.lhs_subset: Optional[set] = None
        self._arrays = None   # (names, numeric, bools, vals, bvals) — driver shim
        self._frame = None    # (df, names, numeric, bools, bool_masks)
        self._meta: dict = {} # id(native conj) -> (hyp_col, feature_list, sub_df)

    # --------------------------------------------------------- frame caches --

    def invalidate(self) -> None:
        """Drop cached frame/arrays so the next call rebuilds from the DB."""
        self._arrays = None
        self._frame = None

    def _build_frame(self):
        entries = list(self.db)
        names = [e.name for e in entries]
        inv_names = list(self.db.invariant_names()) if hasattr(self.db, "invariant_names") \
            else list(INVARIANTS.keys())
        numeric = [k for k in inv_names if k in INVARIANTS]
        bools = [k for k in inv_names if k in BOOLEANS]
        cols = {k: np.array([e.invariants.get(k, np.nan) for e in entries], dtype=float)
                for k in numeric}
        bmask = {b: np.array([e.invariants.get(b, np.nan) for e in entries], dtype=float) >= 0.5
                 for b in bools}
        df = pd.DataFrame(cols)
        for b in bools:                      # bool column; missing class flag → False
            df[b] = bmask[b]
        self._frame = (df, names, numeric, bools, bmask)
        self._arrays = (names, numeric, bools,
                        {k: cols[k] for k in numeric},
                        {b: bmask[b].astype(float) for b in bools})
        return self._frame

    def _ensure_frame(self):
        if self._frame is None:
            self._build_frame()
        return self._frame

    def _load_arrays(self):
        """Compat shim for the parallel driver's copy-on-write preload."""
        if self._arrays is None:
            self._build_frame()
        return self._arrays

    # ----------------------------------------------------------------- API --

    def generate(self) -> List[Conjecture]:
        logger.info("[TxGraffiti] generating via the txgraffiti package…")
        cands = self.generate_candidates()
        logger.info("[TxGraffiti] %d candidates after Dalmatian/Morgan", len(cands))
        novel, known = annotate(cands)
        if known:
            logger.info("[Novelty] %d/%d conjectures rediscover known theorems",
                        len(known), len(cands))
        survived = novel if self.cfg.txgraffiti_filter_known else cands
        survived.sort(key=lambda c: c.score, reverse=True)
        return survived[: self.cfg.txgraffiti_max_conjectures]

    def generate_candidates(self) -> List[Conjecture]:
        """Generate candidate conjectures for the (sharded) target invariants.

        Dispatches on ``cfg.txgraffiti_engine``: the txgraffiti package
        (optimal-coefficient convex-hull/ratio/LP fitting), the fast in-house
        vectorised grid fit, or both (deduplicated)."""
        engine = getattr(self.cfg, "txgraffiti_engine", "txgraffiti")
        out: List[Conjecture] = []
        if engine in ("txgraffiti", "both"):
            out += self._generate_txgraffiti()
        if engine in ("numpy", "both"):
            out += self._generate_numpy()
        if engine == "both":                       # drop cross-engine duplicates
            seen, uniq = set(), []
            for c in out:
                if c.statement not in seen:
                    seen.add(c.statement)
                    uniq.append(c)
            out = uniq
        return out

    # ----------------------------------------------- engine: txgraffiti pkg --

    def _generate_txgraffiti(self) -> List[Conjecture]:
        """Run the txgraffiti generators + dominance filters over the (sharded)
        target invariants and return this pipeline's Conjecture objects."""
        df, names, numeric, bools, bmask = self._ensure_frame()
        if len(df) == 0 or len(numeric) < 2:
            return []
        minsup = self.cfg.txgraffiti_min_support
        finite = {k: np.isfinite(df[k].to_numpy(dtype=float)) for k in numeric}

        contexts = [(None, np.ones(len(df), dtype=bool))]
        if self.cfg.txgraffiti_condition_on_classes:
            for b in bools:
                if int(bmask[b].sum()) >= minsup:
                    contexts.append((b, bmask[b]))

        sizes = [1]
        if self.cfg.txgraffiti_multivariable and self.cfg.txgraffiti_max_rhs_terms >= 2:
            sizes.append(2)

        targets = [t for t in numeric
                   if self.lhs_subset is None or t in self.lhs_subset]

        out: List[Conjecture] = []
        for tgt in targets:
            self._meta = {}
            native = self._generate_for_target(df, tgt, numeric, contexts,
                                               finite, sizes, minsup)
            native = self._dominance_filter(native, df, tgt)
            for nc in native:
                conv = self._convert(nc, names)
                if conv is not None:
                    out.append(conv)
        return out

    def _generate_for_target(self, df, tgt, numeric, contexts, finite, sizes, minsup):
        tprop = Property(tgt, lambda d, c=tgt: d[c])
        feats = [f for f in numeric if f != tgt]
        native = []
        for size in sizes:
            for combo in itertools.combinations(feats, size):
                fmask = finite[tgt].copy()
                for f in combo:
                    fmask &= finite[f]
                if int(fmask.sum()) < minsup:
                    continue
                fprops = [Property(f, lambda d, c=f: d[c]) for f in combo]
                for hname, hmask in contexts:
                    m = fmask & hmask
                    if int(m.sum()) < minsup:
                        continue
                    cols = [tgt] + list(combo) + ([hname] if hname else [])
                    sub = df.loc[m, cols]
                    hp = TRUE if hname is None else Predicate(hname, lambda d, c=hname: d[c])
                    for gen in _TX_GENERATORS:
                        try:
                            for nc in gen(sub, features=fprops, target=tprop,
                                          hypothesis=hp):
                                self._meta[id(nc)] = (hname, list(combo), sub)
                                native.append(nc)
                        except Exception:
                            continue
        return native

    def _dominance_filter(self, native, df, tgt):
        """Apply TxGraffiti's own Dalmatian + Morgan filters on a common
        complete-case frame for this target."""
        if not native:
            return native
        native = remove_duplicates(native, df)
        cols = {tgt}
        for nc in native:
            hname, feats, _ = self._meta[id(nc)]
            cols.update(feats)
            if hname:
                cols.add(hname)
        num_cols = [c for c in cols if c in INVARIANTS]
        cmp_df = df[list(cols)].dropna(subset=num_cols)
        if len(cmp_df) >= self.cfg.txgraffiti_min_support:
            try:
                native = filter_with_dalmatian(native, cmp_df)
                native = filter_with_morgan(native, cmp_df)
            except Exception:
                pass
        return native

    def _convert(self, nc, names) -> Optional[Conjecture]:
        """Translate a native txgraffiti Conjecture into our Conjecture, recovering
        rational RHS coefficients by least squares (the RHS is exactly linear)."""
        ineq = nc.conclusion
        if not isinstance(ineq, TxInequality):
            return None
        if ineq.op in ("<", "<="):
            op = "<="
        elif ineq.op in (">", ">="):
            op = ">="
        else:
            return None                     # skip "==" / "!="
        tgt = ineq.lhs.name
        if tgt not in INVARIANTS:            # LHS must be a bare target invariant
            return None
        hname, feats, sub = self._meta.get(id(nc), (None, [], None))
        if sub is None:
            return None

        rhs_vals = np.asarray(ineq.rhs(sub), dtype=float)
        if feats:
            M = np.column_stack([np.asarray(sub[f], dtype=float) for f in feats]
                                + [np.ones(len(sub))])
            sol, *_ = np.linalg.lstsq(M, rhs_vals, rcond=None)
            coeffs, const = sol[:-1], float(sol[-1])
        else:
            coeffs = []
            const = float(np.nanmean(rhs_vals)) if len(rhs_vals) else 0.0

        def clean(x):
            return float(Fraction(float(x)).limit_denominator(1000))

        terms = [(clean(coeffs[i]), feats[i])
                 for i in range(len(feats)) if abs(coeffs[i]) > 1e-7]
        const = clean(const)
        if terms:
            inv_b, coeff_b, extra = terms[0][1], terms[0][0], terms[1:]
        else:
            inv_b, coeff_b, extra = (feats[0] if feats else tgt), 0.0, []
        my = Inequality(tgt, inv_b, 1.0, coeff_b, const,
                        op=op, extra_terms=extra, hypothesis=hname)

        slack = np.asarray(ineq.slack(sub), dtype=float)
        tight = np.nonzero(np.abs(slack) < 1e-9)[0]
        witnesses = ([names[i] for i in np.asarray(sub.index)[tight]]
                     if len(tight) else [])
        return Conjecture(
            statement=str(my), inequality=my, generation_method="txgraffiti",
            tightness_witnesses=witnesses,
            score=self._score(slack, witnesses, hname),
            metadata={"hypothesis": hname, "context_size": int(len(sub)), "op": op},
        )

    # ------------------------------------------ engine: vectorised numpy fit --

    def _generate_numpy(self) -> List[Conjecture]:
        """Fast in-house alternative to the txgraffiti generators.

        Instead of computing the optimal real coefficients per facet (convex
        hull) or via an LP, this fits the tightest *offset* for each coefficient
        combination drawn from the fixed grid ``cfg.txgraffiti_coefficients`` in
        a single vectorised numpy pass over all rows. It is far cheaper per
        (target, features, class) — no Qhull/LP, no per-row DataFrame objects —
        at the cost of only trying grid coefficients (so it can miss the optimal
        ones the convex hull would find). Produces upper bounds (LHS ≤ RHS)."""
        names, numeric, bool_props, vals, bvals = self._load_arrays()
        n_graphs = len(names)
        if n_graphs == 0 or len(numeric) < 2:
            return []
        finite = {inv: np.isfinite(vals[inv]) for inv in numeric}
        coeffs = tuple(self.cfg.txgraffiti_coefficients)
        candidates: List[Tuple[Conjecture, np.ndarray, tuple]] = []
        seen: set = set()
        lhs_targets = [a for a in numeric
                       if self.lhs_subset is None or a in self.lhs_subset]

        for hyp, cmask in self._contexts_numpy(bool_props, bvals, n_graphs):
            for inv_a, inv_b in itertools.product(lhs_targets, numeric):
                if inv_a == inv_b:
                    continue
                valid = cmask & finite[inv_a] & finite[inv_b]
                if int(valid.sum()) < self.cfg.txgraffiti_min_support:
                    continue
                self._fit(candidates, seen, names, valid, hyp, inv_a,
                          vals[inv_a][valid], [(inv_b, vals[inv_b][valid])], coeffs)

            if self.cfg.txgraffiti_multivariable and self.cfg.txgraffiti_max_rhs_terms >= 2:
                for inv_a in lhs_targets:
                    rest = [x for x in numeric if x != inv_a]
                    for inv_b, inv_c in itertools.combinations(rest, 2):
                        valid = cmask & finite[inv_a] & finite[inv_b] & finite[inv_c]
                        if int(valid.sum()) < self.cfg.txgraffiti_min_support:
                            continue
                        if (np.ptp(vals[inv_b][valid]) < 1e-9
                                or np.ptp(vals[inv_c][valid]) < 1e-9):
                            continue
                        self._fit(candidates, seen, names, valid, hyp, inv_a,
                                  vals[inv_a][valid],
                                  [(inv_b, vals[inv_b][valid]),
                                   (inv_c, vals[inv_c][valid])], coeffs)
        return self._dalmatian_filter(candidates)

    def _contexts_numpy(self, bool_props, bvals, n_graphs):
        contexts = [(None, np.ones(n_graphs, dtype=bool))]
        if self.cfg.txgraffiti_condition_on_classes:
            for b in bool_props:
                mask = bvals[b] >= 0.5
                if int(mask.sum()) >= self.cfg.txgraffiti_min_support:
                    contexts.append((b, mask))
        return contexts

    def _fit(self, candidates, seen, names, valid_mask, hyp, inv_a, a, rhs_terms, coeffs):
        """Fit minimal-offset upper bounds over every coefficient combination."""
        tol = 1e-6
        max_off = self.cfg.txgraffiti_max_offset
        valid_idx = np.nonzero(valid_mask)[0]
        bucket_key = (hyp, inv_a, frozenset(name for name, _ in rhs_terms))
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
            if float(slacks.min()) > tol:            # not tight anywhere
                continue
            if self.cfg.txgraffiti_drop_identities and float(slacks.max()) < tol:
                continue                              # identity across the class
            extra = [(combo[k], rhs_terms[k][0]) for k in range(1, len(rhs_terms))]
            ineq = Inequality(inv_a, rhs_terms[0][0], 1.0, combo[0], round(offset, 4),
                              op="<=", extra_terms=extra, hypothesis=hyp)
            stmt = str(ineq)
            if stmt in seen:
                continue
            seen.add(stmt)
            tight_local = np.nonzero(np.abs(slacks) < tol)[0]
            tightness = [names[valid_idx[i]] for i in tight_local]
            c = Conjecture(statement=stmt, inequality=ineq, generation_method="txgraffiti",
                           tightness_witnesses=tightness,
                           score=self._score(slacks, tightness, hyp),
                           metadata={"hypothesis": hyp, "context_size": int(valid_mask.sum()),
                                     "op": "<="})
            candidates.append((c, slacks, bucket_key))

    def _dalmatian_filter(self, candidates) -> List[Conjecture]:
        """In-house Dalmatian dominance filter for the numpy engine (operates on
        the cached slack vectors; buckets by LHS / RHS-set / class)."""
        buckets: Dict[tuple, list] = defaultdict(list)
        for item in candidates:
            buckets[item[2]].append(item)
        survived: List[Conjecture] = []
        for items in buckets.values():
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
        avg_slack = float(np.nanmean(slacks)) if n else 0.0
        score = tightness_ratio * 2.0 - abs(avg_slack) * 0.1
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
