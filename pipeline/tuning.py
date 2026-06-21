"""
pipeline/tuning.py — optimal-coefficient tuning for expression-tree conjectures.

The Sage `Conjecturing` engine (and Graffiti3's nonlinear runners) reach only
the fixed integer/rational constants their operator set allows. This module
lifts a conjecture's additive right-hand-side terms to a nonlinear feature map
φ₁,…,φ_k and fits the tightest *valid* affine bound

    target  ≤  Σ cᵢ·φᵢ  +  c₀        (or  ≥  for lower bounds)

over a corpus by a small linear program that minimises total slack — exactly the
convex-hull construction lifted from raw invariants to a nonlinear basis. This is
the "find optimal coefficients" step for the otherwise grid-limited Sage stage.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import networkx as nx
import numpy as np

from conjecture import Conjecture
from pipeline.expr_bridge import make_value

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------- LP fit --

def tune_bound(y: np.ndarray, X: np.ndarray, sense: str = "<=",
               tol: float = 1e-9) -> Optional[Tuple[np.ndarray, float]]:
    """Fit (coeffs, c0) of the tightest affine bound on every row.

    sense "<=":  y_i ≤ X_i·c + c0  for all i, minimising Σ (X_i·c + c0 − y_i).
    sense ">=":  y_i ≥ X_i·c + c0  for all i, minimising Σ (y_i − X_i·c − c0).
    Returns None if the LP fails.
    """
    from scipy.optimize import linprog
    n, k = X.shape
    ones = np.ones((n, 1))
    A = np.hstack([X, ones])                       # variables: c (k) then c0
    # objective = sum_i (±(A z - y));  for "<=" minimise sum(Az) ; constant -Σy dropped
    sgn = 1.0 if sense == "<=" else -1.0
    cobj = sgn * A.sum(axis=0)
    # constraints: "<=":  A z ≥ y  →  -A z ≤ -y ;  ">=":  A z ≤ y
    if sense == "<=":
        A_ub, b_ub = -A, -y
    else:
        A_ub, b_ub = A, y
    bounds = [(None, None)] * (k + 1)
    try:
        res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    except Exception as e:
        logger.debug("tune LP failed: %s", e)
        return None
    if not res.success:
        return None
    z = res.x
    return z[:k], float(z[k])


# ----------------------------------------------------- term splitting -----

def split_terms(rhs: str) -> List[str]:
    """Split a RHS expression into additive terms at parenthesis depth 0."""
    terms, depth, cur = [], 0, ""
    i = 0
    while i < len(rhs):
        ch = rhs[i]
        if ch in "([":
            depth += 1; cur += ch
        elif ch in ")]":
            depth -= 1; cur += ch
        elif ch in "+-" and depth == 0 and cur.strip():
            # binary +/- at top level (not a leading unary sign)
            terms.append(cur.strip())
            cur = "" if ch == "+" else "-"
        else:
            cur += ch
        i += 1
    if cur.strip():
        terms.append(cur.strip())
    return [t for t in terms if t.strip() not in ("", "+", "-")]


def _corpus_graphs(max_n: int = 7) -> List[nx.Graph]:
    from networkx.generators.atlas import graph_atlas_g
    return [G for G in graph_atlas_g()
            if 2 <= G.number_of_nodes() <= max_n and nx.is_connected(G)]


# -------------------------------------------------- tune a conjecture -----

def tune_sage_conjecture(conj: Conjecture, graphs: List[nx.Graph]
                         ) -> Optional[Conjecture]:
    """Refit the coefficients of a Sage/expression conjecture by LP. Returns a
    new statement-only Conjecture with optimal coefficients, or None if it cannot
    be parsed/improved."""
    stmt = conj.statement or ""
    if "<=" in stmt:
        lhs_s, rhs_s, sense = stmt.split("<=", 1)[0], stmt.split("<=", 1)[1], "<="
    elif ">=" in stmt:
        lhs_s, rhs_s, sense = stmt.split(">=", 1)[0], stmt.split(">=", 1)[1], ">="
    else:
        return None
    terms = split_terms(rhs_s)
    if not terms:
        return None
    try:
        lhs_fn = make_value(lhs_s)
        term_fns = [make_value(t) for t in terms]
    except Exception:
        return None

    ys, rows = [], []
    for G in graphs:
        try:
            y = lhs_fn(G)
            xs = [f(G) for f in term_fns]
        except Exception:
            continue
        if not (np.isfinite(y) and all(np.isfinite(v) for v in xs)):
            continue
        ys.append(y); rows.append(xs)
    if len(ys) < max(5, len(terms) + 2):
        return None

    fit = tune_bound(np.array(ys, float), np.array(rows, float), sense)
    if fit is None:
        return None
    coeffs, c0 = fit

    # render tuned statement
    parts = []
    for c, t in zip(coeffs, terms):
        cr = round(float(c), 4)
        if abs(cr) < 1e-6:
            continue
        parts.append(t if abs(cr - 1.0) < 1e-9 else f"{cr}*({t})")
    if abs(round(c0, 4)) > 1e-6:
        parts.append(f"{round(c0, 4)}")
    rhs_new = " + ".join(parts) if parts else "0"
    new_stmt = f"{lhs_s.strip()} {sense} {rhs_new}"

    tuned = Conjecture(
        statement=new_stmt, inequality=None,
        generation_method=conj.generation_method + "+tuned",
        metadata={**conj.metadata, "novel": True, "tuned_from": stmt},
    )
    return tuned


def tune_sage_conjectures(conjs: List[Conjecture], *, max_n: int = 7
                          ) -> List[Conjecture]:
    """Tune every numeric Sage conjecture; return the tuned versions (falls back
    to the original when tuning fails)."""
    graphs = _corpus_graphs(max_n)
    out = []
    for c in conjs:
        if c.inequality is not None or "->" in (c.statement or ""):
            out.append(c)                # property/linear — leave as is
            continue
        tuned = tune_sage_conjecture(c, graphs)
        out.append(tuned if tuned is not None else c)
    return out
