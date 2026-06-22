"""
pipeline/search/z3_adapter.py — bridge graffiti3 conjectures to the SMT/Z3 falsifier.

The existing ``Z3Falsifier`` (pipeline/falsification.py) does exact small-graph
SMT search, but only for a single linear bound ``inv_a ≤ c·inv_b + offset`` over
a 9-invariant SUPPORTED set. graffiti3 conjectures are expression trees over the
full graphcalc battery, so we:

  1. detect the linear form by **finite differences** on the relation's slack
     (no dependence on graffiti3 Expr internals);
  2. require exactly two invariants, both SMT-encodable, in upper-bound form
     (target coefficient ≈ -1 in slack = ``rhs - lhs``);
  3. map graphcalc names → the falsifier's short names and run Z3;
  4. **verify** any returned graph against the *original* conjecture (respecting
     its frozen hypothesis), so a disconnected/out-of-class SMT model is never
     accepted as a counterexample.

Non-linear / non-encodable / conditioned conjectures are skipped (the black-box
searchers handle those).
"""
from __future__ import annotations

import logging
import re
from typing import Callable, Dict, Optional

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)

# graphcalc battery name → Z3Falsifier short name
_NAME_MAP: Dict[str, str] = {
    "order": "n", "size": "m",
    "max_degree": "Delta", "min_degree": "delta",
    "independence_number": "alpha", "clique_number": "omega",
    "chromatic_number": "chi", "domination_number": "gamma",
    "matching_number": "nu",
}


def _tokens(text: str):
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text or ""))


def _linear_slack(relation, cols):
    """If relation.slack is linear in ``cols``, return (const, {col: coeff});
    else (None, None). Uses finite differences over a tiny probe table."""
    def slk(row: dict) -> float:
        s = relation.slack(pd.DataFrame([row]))
        return float(pd.Series(s).iloc[0])

    base = {c: 0.0 for c in cols}
    try:
        c0 = slk(base)
        coef = {}
        for c in cols:
            r = dict(base); r[c] = 1.0
            coef[c] = slk(r) - c0
        # linearity: scaling (x=2) and one pairwise cross-check
        for c in cols:
            r = dict(base); r[c] = 2.0
            if abs(slk(r) - (c0 + 2 * coef[c])) > 1e-6:
                return None, None
        cl = list(cols)
        for i, a in enumerate(cl):
            for b in cl[i + 1:]:
                r = dict(base); r[a] = 1.0; r[b] = 1.0
                if abs(slk(r) - (c0 + coef[a] + coef[b])) > 1e-6:
                    return None, None
    except Exception:
        return None, None                      # references a column we didn't probe
    return c0, coef


def z3_search(native, all_cols, cfg, *, verify: Optional[Callable] = None
              ) -> Optional[nx.Graph]:
    if not getattr(cfg, "z3_enabled", True):
        return None
    relation = getattr(native, "relation", None)
    if relation is None:
        return None
    # referenced *encodable* invariants (others ⇒ slack probe KeyErrors ⇒ skip)
    cols = [c for c in all_cols if c in _NAME_MAP and c in _tokens(native.pretty())]
    if len(cols) < 2:
        return None
    c0, coef = _linear_slack(relation, cols)
    if c0 is None:
        return None
    nz = [c for c in cols if abs(coef[c]) > 1e-9]
    if len(nz) != 2:
        return None
    # upper bound on a target: slack = rhs - lhs ⇒ target has coeff ≈ -1
    tgt = [c for c in nz if abs(coef[c] + 1.0) < 1e-6]
    if len(tgt) != 1:
        return None
    a = tgt[0]
    b = nz[0] if nz[1] == a else nz[1]

    from conjecture import Conjecture, Inequality
    from pipeline.falsification import Z3Falsifier
    ineq = Inequality(inv_a=_NAME_MAP[a], inv_b=_NAME_MAP[b],
                      coeff_a=1.0, coeff_b=coef[b], offset=c0, op="<=")
    probe = Conjecture(statement=native.pretty(), inequality=ineq,
                       generation_method="cegis-z3probe")
    try:
        res = Z3Falsifier(cfg).falsify(probe)
    except Exception as e:
        logger.debug("[z3] falsify error: %s", e)
        return None
    G = getattr(res, "counterexample_graph", None) if res else None
    if G is None:
        return None
    # only accept if it really refutes the ORIGINAL conjecture (hypothesis-aware)
    if verify is not None and not verify(G):
        return None
    logger.info("[z3] counterexample (n=%d) for %s", G.number_of_nodes(),
                native.pretty())
    return G
