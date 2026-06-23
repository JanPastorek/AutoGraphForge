"""
pipeline/cegis_novelty.py — apply the legacy known-theorem filter to CEGIS output.

The known-theorem table in ``pipeline.novelty`` (Whitney, Brooks, ω≤χ, ν≤n/2, …
plus a convex-combination LP implication check) is linear-form only, but it is
exactly what flags a CEGIS survivor as "rediscovers a classical theorem". This
module bridges the two: it parses a graffiti3 native conjecture's pretty string
into the linear ``Inequality`` the novelty filter understands, when the
conjecture *is* linear with a single invariant on each side (the classical
shapes). Nonlinear / multi-term / product / ratio conjectures parse to ``None``
and are conservatively treated as novel (never wrongly dropped).
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from conjecture import Conjecture, Inequality
from pipeline import novelty

_REL = {"≤": "<=", "<=": "<=", "≥": ">=", ">=": ">="}

# graphcalc battery column  →  symbolic name used in pipeline.novelty.KNOWN_THEOREMS.
# Only invariants the known-theorem table actually speaks about are mapped; a
# conjecture using anything outside this map can't be judged and stays novel.
_GC2TABLE = {
    "order": "n", "size": "m",
    "maximum_degree": "Delta", "minimum_degree": "delta", "average_degree": "avg_deg",
    "clique_number": "omega", "independence_number": "alpha", "chromatic_number": "chi",
    "domination_number": "gamma", "independent_domination_number": "ind_dom",
    "vertex_cover_number": "vertex_cover", "matching_number": "nu",
    "diameter": "diam", "radius": "rad",
    "algebraic_connectivity": "alg", "spectral_radius": "spectral_radius",
    "density": "density",
}


def _num(tok: str) -> Optional[float]:
    """Parse an int, float, or 'a/b' fraction."""
    tok = tok.strip().strip("()")
    try:
        if "/" in tok:
            a, b = tok.split("/", 1)
            return float(a) / float(b)
        return float(tok)
    except Exception:
        return None


def _parse_side(s: str, cols: List[str]) -> Optional[Tuple[float, str, float]]:
    """Parse a linear side into (coeff, invariant, constant), single invariant.

    Handles ``inv``, ``c · inv``, ``c · inv + d``, ``inv + d`` and the
    parenthesised graffiti3 forms. Returns None if not a single-invariant linear
    expression."""
    s = s.replace("·", "*").replace("(", " ").replace(")", " ")
    present = [c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", s)]
    if len(present) != 1:
        return None
    inv = present[0]
    # coefficient: a number immediately before  '* inv'  (default 1)
    coeff = 1.0
    m = re.search(r"([0-9]+(?:\.[0-9]+)?(?:\s*/\s*[0-9]+)?)\s*\*\s*" + re.escape(inv), s)
    if m:
        v = _num(m.group(1).replace(" ", ""))
        if v is None:
            return None
        coeff = v
    # constant: standalone numeric tokens not glued to the invariant
    s_wo = re.sub(re.escape(inv), " ", s)
    s_wo = re.sub(r"[0-9.]+\s*/\s*[0-9.]+|\d+(?:\.\d+)?", lambda mm: f" {mm.group(0)} ", s_wo)
    const = 0.0
    for tok in re.findall(r"[+-]?\s*\d+(?:\.\d+)?(?:\s*/\s*\d+)?", s_wo):
        # skip the coefficient token if it reappeared
        v = _num(tok.replace(" ", ""))
        if v is not None and "*" not in tok:
            const += v
    return coeff, inv, const


def native_to_inequality(native, cols: List[str]) -> Optional[Inequality]:
    """Best-effort linear ``Inequality`` from a graffiti3 native, else None."""
    try:
        pretty = native.pretty()
    except Exception:
        return None
    hypothesis = None
    if "⇒" in pretty:                                   # "(cond) ⇒ body"
        cond, pretty = pretty.split("⇒", 1)
        conds = [c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", cond)]
        # only single-class conditions map to the novelty hypothesis model
        hypothesis = conds[0] if len(conds) == 1 else None
        if len(conds) > 1:
            return None
    rel = next((r for r in ("≤", "≥", "<=", ">=") if r in pretty), None)
    if rel is None:
        return None                                     # equalities not handled
    lhs, rhs = pretty.split(rel, 1)
    left = _parse_side(lhs, cols)
    right = _parse_side(rhs, cols)
    if not left or not right:
        return None
    ca, inv_a, const_l = left
    cb, inv_b, const_r = right
    # Map to the table's symbolic names; both sides must be known to the table.
    if inv_a not in _GC2TABLE or inv_b not in _GC2TABLE:
        return None
    # coeff_a·inv_a (+const_l) ≤ coeff_b·inv_b (+const_r)  →  normalise const to RHS
    return Inequality(
        inv_a=_GC2TABLE[inv_a], inv_b=_GC2TABLE[inv_b], coeff_a=ca, coeff_b=cb,
        offset=const_r - const_l, op=_REL.get(rel, "<="),
        hypothesis=hypothesis)


def classify_native(native, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """(is_known, matched_theorem) for a graffiti3 native; (False, None) if it
    can't be expressed as a linear bound the table speaks to."""
    ineq = native_to_inequality(native, cols)
    if ineq is None:
        return False, None
    c = Conjecture(statement=ineq.pretty() if hasattr(ineq, "pretty") else "",
                   inequality=ineq, generation_method="cegis-graffiti3")
    try:
        return novelty.classify(c)
    except Exception:
        return False, None
