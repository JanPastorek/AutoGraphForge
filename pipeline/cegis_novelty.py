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

# Extend with the domination / zero-forcing family columns so generated
# conjectures over them parse into Inequalities the curated known-relation table
# (pipeline/known_relations.py) can judge.
try:
    from pipeline.known_relations import GC_COLUMNS as _GC_EXTRA
    _GC2TABLE.update(_GC_EXTRA)
except Exception:  # pragma: no cover - defensive
    pass


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
    # drop any 'c *' multiplier (the coefficient) so it is not double-counted as
    # a constant once the invariant it multiplied has been removed
    s_wo = re.sub(r"[0-9.]+(?:\s*/\s*[0-9.]+)?\s*\*", " ", s_wo)
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
    # The known-theorem table is upper-bound form (lhs ≤ rhs); normalise a
    # lower-bound conjecture  a ≥ b  into the equivalent  b ≤ a  by swapping
    # sides, so ≥-shaped rediscoveries (most of the domination/zero-forcing
    # folklore) are matched too rather than silently passing as novel.
    if rel in ("≥", ">="):
        (ca, inv_a, const_l), (cb, inv_b, const_r) = (cb, inv_b, const_r), (ca, inv_a, const_l)
    # Map to the table's symbolic names; both sides must be known to the table.
    if inv_a not in _GC2TABLE or inv_b not in _GC2TABLE:
        return None
    # coeff_a·inv_a (+const_l) ≤ coeff_b·inv_b (+const_r)  →  normalise const to RHS
    return Inequality(
        inv_a=_GC2TABLE[inv_a], inv_b=_GC2TABLE[inv_b], coeff_a=ca, coeff_b=cb,
        offset=const_r - const_l, op="<=",
        hypothesis=hypothesis)


# ── Conditioned-known rules (the linear table is unconditioned-only) ────────
# Graph classes on which every graph is perfect: χ = ω and α = clique-cover
# number hold by the perfect graph theorem / definition.
_PERFECT_CLASSES = {"cograph", "chordal", "bipartite", "interval", "split"}


def _body_parts(native, cols: List[str]):
    """(classes, body_invariants, relation, constants) for a conditioned
    conjecture, else None. ``classes`` are the boolean class columns in the
    hypothesis; ``body_invariants`` the numeric invariants in the bounded
    relation; ``constants`` the bare integers in the body."""
    try:
        pretty = native.pretty()
    except Exception:
        return None
    if "⇒" not in pretty and "=>" not in pretty:
        return None
    cond, body = re.split(r"⇒|=>", pretty, maxsplit=1)
    classes = [c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", cond)]
    rel = next((r for r in ("≤", "≥", "<=", ">=", "=") if r in body), None)
    if rel is None:
        return None
    body_invs = {c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", body)}
    consts = {int(m) for m in re.findall(r"(?<![\w.])\d+(?![\w./])", body)}
    return classes, body_invs, _REL.get(rel, rel), consts


def conditioned_known(native, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """Flag conditioned conjectures that restate a perfect-graph property or a
    class definition — the classical results the unconditioned table misses."""
    parts = _body_parts(native, cols)
    if parts is None:
        return False, None
    classes, invs, _rel, consts = parts
    if not classes:
        return False, None
    perfect = any(c in _PERFECT_CLASSES for c in classes)
    cls = set(classes)

    # perfect-graph identities (any relation direction — equality holds)
    if perfect and invs == {"chromatic_number", "clique_number"}:
        return True, "perfect graph: χ = ω"
    if perfect and invs == {"independence_number", "vertex_clique_cover_number"}:
        return True, "perfect graph: α = θ̄ (clique cover)"

    # class-definitional facts
    deg = {"maximum_degree", "minimum_degree", "average_degree"}
    if "regular" in cls and invs and invs <= deg and len(invs) >= 2:
        return True, "regular: Δ = δ = 2m/n"
    if "cubic" in cls and invs and invs <= {"maximum_degree", "minimum_degree"}:
        return True, "cubic: Δ = δ = 3"
    if "subcubic" in cls and invs == {"maximum_degree"} and 3 in consts:
        return True, "subcubic: Δ ≤ 3 (definition)"
    if "triangle_free" in cls and invs == {"clique_number"} and consts <= {2}:
        return True, "triangle-free: ω ≤ 2 (definition)"
    if "K_4_free" in cls and invs == {"clique_number"} and consts <= {3}:
        return True, "K₄-free: ω ≤ 3 (definition)"
    if "bipartite" in cls and invs == {"clique_number"} and consts <= {2}:
        return True, "bipartite: ω ≤ 2"
    if "bipartite" in cls and invs == {"chromatic_number"} and consts <= {2}:
        return True, "bipartite: χ ≤ 2 (definition)"
    return False, None


def classify_native(native, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """(is_known, matched_theorem) for a graffiti3 native; (False, None) if not a
    recognised classical result. Tries the unconditioned linear table first, then
    the conditioned (perfect-graph / class-definition) rules."""
    ineq = native_to_inequality(native, cols)
    if ineq is not None:
        c = Conjecture(statement="", inequality=ineq,
                       generation_method="cegis-graffiti3")
        try:
            known, why = novelty.classify(c)
            if known:
                return True, why
        except Exception:
            pass
    return conditioned_known(native, cols)
