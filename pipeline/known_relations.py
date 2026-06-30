"""
pipeline/known_relations.py — curated known relations for the novelty filter.

The base table in :mod:`pipeline.novelty` speaks a small symbolic vocabulary
(``alpha``, ``gamma``, ``omega``, …) and covers the classical chains
(Whitney, König–Egerváry, Gallai, …). This module *extends* it with a large,
domain-curated list of known graph-invariant relations over the **domination**
and **zero-forcing** families (``total_domination_number``,
``zero_forcing_number``, ``annihilation_number``, ``slater``, …) that the base
table does not name — the relations a graph theorist already considers folklore
or published, so that a CEGIS survivor restating one of them is flagged
*known* rather than *novel*.

The relations are kept here as **human-readable strings** (exactly the form a
domain expert writes them), and parsed at import time into the
``(lhs, {rhs: coeff}, offset, class, name)`` tuples that
``pipeline.novelty.KNOWN_THEOREMS`` consumes. Parsing is deliberately
conservative: anything that does not parse cleanly to a linear relation over the
known vocabulary (nonlinear ``ceil`` forms, multi-class hypotheses, unsupported
"not K_n" / degree-bounded hypotheses, malformed fragments) is **skipped** and
left *novel* — the safe direction, since wrongly hiding a real conjecture is the
only error that matters here.
"""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# A KNOWN_THEOREMS entry:  (lhs, {rhs_inv: coeff, ...}, offset, class|None, name)
Tuple5 = Tuple[str, Dict[str, float], float, Optional[str], str]

# ---------------------------------------------------------------------------
# Invariant vocabulary.  Tokens (graphcalc-style column names, plus a couple of
# common spellings) map to the symbolic names used inside the novelty table.
# The classical invariants reuse the base table's short names so the new
# relations *compose* with the existing ones through the LP; the domination /
# zero-forcing family invariants are new and map to themselves.
# ---------------------------------------------------------------------------

TOKEN2SYM: Dict[str, str] = {
    "order": "n", "size": "m",
    "max_degree": "Delta", "maximum_degree": "Delta",
    "min_degree": "delta", "minimum_degree": "delta",
    "average_degree": "avg_deg",
    "clique_number": "omega", "independence_number": "alpha",
    "chromatic_number": "chi",
    "domination_number": "gamma", "independent_domination_number": "ind_dom",
    "vertex_cover_number": "vertex_cover", "matching_number": "nu",
    "diameter": "diam", "radius": "rad",
}

_NEW_INVARIANTS = [
    # domination family
    "total_domination_number", "connected_domination_number",
    "restrained_domination_number", "outer_connected_domination_number",
    "roman_domination_number", "double_roman_domination_number",
    "two_rainbow_domination_number", "three_rainbow_domination_number",
    "power_domination_number", "sub_total_domination_number",
    "edge_domination_number",
    # independence / matching / cover extras
    "annihilation_number", "residue", "square_residue",
    "slater", "LG_slater", "min_maximal_matching_number", "min_edge_cover",
    # zero-forcing family
    "zero_forcing_number", "total_zero_forcing_number",
    "connected_zero_forcing_number", "positive_semidefinite_zero_forcing_number",
    # distance / misc
    "triameter",
    "power_min_degree_residue_sum", "power_min_degree_annihilation_sum",
    "power_2_annihilation_sum", "power_3_annihilation_sum",
]
for _t in _NEW_INVARIANTS:
    TOKEN2SYM.setdefault(_t, _t)

# Tokens, longest first, so e.g. ``total_domination_number`` is preferred over a
# spurious ``domination_number`` substring (underscores already block most of
# these, but length ordering is a cheap belt-and-braces).
INV_TOKENS = sorted(TOKEN2SYM, key=len, reverse=True)

# graphcalc column -> symbol, for extending pipeline.cegis_novelty._GC2TABLE so
# that *generated* conjectures over these invariants parse into Inequalities.
GC_COLUMNS: Dict[str, str] = {t: TOKEN2SYM[t] for t in _NEW_INVARIANTS}

# Graph-class words we model; anything else in a hypothesis -> skip the relation.
_CLASS_WORDS = {
    "well-covered": "well_covered",
    "bipartite": "bipartite",
    "claw-free": "claw_free",
    "tree": "tree",
    "triangle-free": "triangle_free",
    "cubic": "cubic",
}
_SKIP = object()  # sentinel: hypothesis present but not modellable -> drop


# ---------------------------------------------------------------------------
# Curated known relations (verbatim, expert-written).  Parsed below.
# ---------------------------------------------------------------------------

KNOWN_CONJECTURES = [
    "If G is a connected and well-covered graph, then independence_number <= independent_domination_number",
    "If G is a connected and bipartite graph, then independence_number >= (order - matching_number)",
    "If G is a connected and claw-free graph, then domination_number >= independent_domination_number",
    "If G is a connected and claw-free graph, then independent_domination_number <= domination_number",
    "If G is a connected and well-covered graph, then independent_domination_number >= independence_number",
    "If G is a tree graph, then independence_number >= (order - matching_number)",
    "If G is a connected and bipartite graph, then independence_number >= min_edge_cover",
    "If G is a connected and triangle-free graph, then independence_number >= max_degree",
    "If G is a connected and claw-free graph, then zero_forcing_number <= positive_semidefinite_zero_forcing_number",
    "If G is a connected and claw-free graph, then zero_forcing_number = positive_semidefinite_zero_forcing_number",
]

KNOWN_INEQUALITIES = [
    "independence_number <= (order - matching_number)",
    "independence_number <= (order - min_maximal_matching_number)",
    "independence_number <= annihilation_number",
    "independence_number <= (order - min_degree)",
    "independence_number <= min_edge_cover",
    "independence_number >= residue",
    "independence_number >= independent_domination_number",
    "domination_number >= slater",
    "domination_number <= independent_domination_number",
    "domination_number <= connected_domination_number",
    "domination_number <= total_domination_number",
    "domination_number <= restrained_domination_number",
    "domination_number >= 1/2 * roman_domination_number",
    "domination_number >= 1/3 * double_roman_domination_number",
    "domination_number <= independence_number",
    "domination_number <= outer_connected_domination_number",
    "total_domination_number >= sub_total_domination_number",
    "total_domination_number >= domination_number",
    "total_domination_number <= connected_domination_number",
    "total_domination_number >= slater",
    "connected_domination_number >= slater",
    "slater <= independent_domination_number",
    "slater <= connected_domination_number",
    "slater <= total_domination_number",
    "connected_domination_number >= domination_number",
    "zero_forcing_number <= connected_zero_forcing_number",
    "zero_forcing_number <= total_zero_forcing_number",
    "zero_forcing_number >= positive_semidefinite_zero_forcing_number",
    "zero_forcing_number >= min_degree",
    "total_zero_forcing_number >= min_degree",
    "connected_zero_forcing_number >= min_degree",
    "zero_forcing_number >= chromatic_number - 1",
    "zero_forcing_number >= clique_number - 1",
    "power_domination_number <= 1/2 * total_zero_forcing_number",
    "power_domination_number <= domination_number",
    "independent_domination_number >= domination_number",
    "independent_domination_number <= independence_number",
    "positive_semidefinite_zero_forcing_number >= min_degree",
    "positive_semidefinite_zero_forcing_number <= connected_zero_forcing_number",
    "roman_domination_number <= 2 * domination_number",
    "edge_domination_number >= LG_slater",
    "edge_domination_number <= matching_number",
    "total_zero_forcing_number <= connected_zero_forcing_number",
    "total_zero_forcing_number >= positive_semidefinite_zero_forcing_number",
    "total_zero_forcing_number >= 2 * power_domination_number",
    "residue <= independence_number",
    "annihilation_number >= matching_number",
    "annihilation_number >= independence_number",
    "annihilation_number >= residue",
    "domination_number <= order",
    "domination_number <= roman_domination_number",
    "domination_number <= double_roman_domination_number",
    "domination_number <= two_rainbow_domination_number",
    "domination_number <= three_rainbow_domination_number",
    "domination_number <= vertex_cover_number",
    "domination_number <= matching_number",
    "domination_number <= 2 min_maximal_matching_number",
    "two_rainbow_domination_number >= domination_number",
    "three_rainbow_domination_number >= domination_number",
    "three_rainbow_domination_number >= two_rainbow_domination_number",
    "domination_number >= power_domination_number",
    "power_domination_number <= zero_forcing_number",
    "power_domination_number <= total_domination_number",
    "power_domination_number <= connected_domination_number",
    "power_domination_number <= total_zero_forcing_number",
    "restrained_domination_number >= domination_number",
    "two_rainbow_domination_number >= domination_number",
    "outer_connected_domination_number >= domination_number",
    "outer_connected_domination_number >= slater",
    "roman_domination_number >= domination_number",
    "double_roman_domination_number >= roman_domination_number",
    "roman_domination_number >= slater",
    "double_roman_domination_number >= slater",
    "roman_domination_number <= double_roman_domination_number",
    "roman_domination_number <= 2 domination_number",
    "roman_domination_number <= 2 independent_domination_number",
    "roman_domination_number <= 2 total_domination_number",
    "roman_domination_number <= 2 connected_domination_number",
    "double_roman_domination_number <= 3 domination_number",
    "double_roman_domination_number <= 3 independent_domination_number",
    "double_roman_domination_number <= 3 total_domination_number",
    "double_roman_domination_number <= 3 connected_domination_number",
    "double_roman_domination_number >= 2 domination_number",
    "positive_semidefinite_zero_forcing_number <= zero_forcing_number",
    "positive_semidefinite_zero_forcing_number <= total_zero_forcing_number",
    "positive_semidefinite_zero_forcing_number <= connected_zero_forcing_number",
    "matching_number >= min_maximal_matching_number",
    "min_maximal_matching_number <= matching_number",
    "matching_number <= 1/2 order",
    "domination_number >= 1/2 total_domination_number",
    "domination_number >= 1/2 roman_domination_number",
    "independent_domination_number >= 1/2 roman_domination_number",
    "total_domination_number >= 1/2 roman_domination_number",
    "connected_domination_number >= 1/2 roman_domination_number",
    "domination_number <= 1/2 order",
    "domination_number <= (order - max_degree)",
    "total_domination_number <= 2 domination_number",
    "total_domination_number <= 2 independent_domination_number",
    "power_domination_number <= independent_domination_number",
    "total_zero_forcing_number <= order + -1",
    "zero_forcing_number <= order + -1",
    "total_domination_number <= order + -1",
    "domination_number <= order + -1",
    "independent_domination_number <= order + -1",
    "connected_domination_number <= order + -1",
    "power_domination_number <= order + -1",
    "min_degree <= max_degree",
    "min_degree <= zero_forcing_number",
    "annihilation_number >= residue",
    "independence_number >= radius",
    "sub_total_domination_number <= total_domination_number",
    "sub_total_domination_number >= slater",
    "slater <= domination_number",
    "chromatic_number >= clique_number",
    "matching_number <= (order - matching_number)",
    "independent_domination_number <= (order - max_degree)",
    "independent_domination_number >= slater",
    "independent_domination_number >= power_domination_number",
    "independent_domination_number >= 1/2 total_domination_number",
    "independent_domination_number <= 1/2 order",
    "independent_domination_number <= 1/2 power_domination_number + 11/2",
    "independent_domination_number <= 2/3 zero_forcing_number + 13/3",
    "independent_domination_number <= 1/5 diameter + 27/5",
    "connected_domination_number >= power_domination_number",
    "independence_number <= radius",
    "independence_number <= order + -1",
    "independence_number <= size",
    "independence_number >= domination_number",
    "diameter >= radius",
    "zero_forcing_number >= 1/2 total_zero_forcing_number",
    "annihilation_number <= 1/2 order",
    "connected_zero_forcing_number >= zero_forcing_number",
    "connected_zero_forcing_number <= order + -1",
    "connected_zero_forcing_number >= chromatic_number + -1",
    "connected_zero_forcing_number >= clique_number + -1",
    "connected_zero_forcing_number >= total_zero_forcing_number",
    "connected_zero_forcing_number >= positive_semidefinite_zero_forcing_number",
    "zero_forcing_number >= chromatic_number + -1",
    "zero_forcing_number >= clique_number + -1",
    "total_zero_forcing_number >= chromatic_number + -1",
    "total_zero_forcing_number >= clique_number + -1",
    "annihilation_number >= (order - matching_number)",
    "annihilation_number >= domination_number",
    "annihilation_number >= independent_domination_number",
    "annihilation_number >= slater",
    "annihilation_number >= power_domination_number",
    "double_roman_domination_number <= 3 restrained_domination_number",
    "double_roman_domination_number <= 3 outer_connected_domination_number",
    "double_roman_domination_number <= 2 two_rainbow_domination_number",
    "restrained_domination_number >= slater",
    "restrained_domination_number >= 1/2 roman_domination_number",
    "restrained_domination_number >= power_domination_number",
    "restrained_domination_number >= 1/3 double_roman_domination_number",
    "triameter <= 3 diameter",
    "slater <= sub_total_domination_number",
    "slater <= restrained_domination_number",
    "slater <= outer_connected_domination_number",
    "domination_number <= 1/2 double_roman_domination_number",
    "total_domination_number <= 2 edge_domination_number",
    "zero_forcing_number <= size + -1",
    "total_zero_forcing_number <= size",
    "diameter <= 2 radius",
    "radius <= diameter",
    "radius >= 1/2 diameter",
    "radius <= independence_number",
    "independent_domination_number <= (order - domination_number)",
    "chromatic_number <= zero_forcing_number + 1",
    "chromatic_number <= clique_number + 1",
    "chromatic_number <= max_degree + 1",
    "clique_number <= chromatic_number",
    "clique_number <= zero_forcing_number + 1",
    "clique_number <= max_degree + 1",
    "residue <= power_min_degree_residue_sum",
    "residue <= annihilation_number",
    "annihilation_number <= power_min_degree_annihilation_sum",
    "min_edge_cover <= order + -1",
    "positive_semidefinite_zero_forcing_number <= vertex_cover_number",
    "total_domination_number <= 2 * edge_domination_number",
    "zero_forcing_number <= - diameter + order",
    "total_domination_number <= 7/9 * max_degree + 5/3",
    "independence_number <= order - vertex_cover_number",
    "vertex_cover_number <= order - independence_number",
    "independence_number >= square_residue",
    "independence_number <= order - matching_number",
    "zero_forcing_number <= order - 1",
    "total_zero_forcing_number <= order - 1",
    "connected_zero_forcing_number <= order - 1",
    "independence_number <= order - 1",
    "independence_number <= power_min_degree_annihilation_sum",
    "independence_number <= power_2_annihilation_sum",
    "independence_number <= power_3_annihilation_sum",
]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _num(tok: str) -> Optional[float]:
    tok = tok.strip()
    if not tok:
        return None
    try:
        if "/" in tok:
            a, b = tok.split("/", 1)
            return float(a) / float(b)
        return float(tok)
    except Exception:
        return None


def _parse_class(cond: str):
    """Hypothesis string -> class symbol, ``None`` (unconditioned), or ``_SKIP``."""
    c = cond.lower().strip()
    if any(bad in c for bad in ("which is not", "at least", "at most", "k_n")):
        return _SKIP
    c = c.replace(" graphs", "").replace(" graph", "").replace(" and ", ",")
    parts = [p.strip() for p in c.split(",") if p.strip()]
    classes = []
    for p in parts:
        p = re.sub(r"^(a|an)\s+", "", p).strip()
        if p in ("", "connected"):
            continue
        if p in _CLASS_WORDS:
            classes.append(_CLASS_WORDS[p])
        else:
            return _SKIP            # unknown class word -> conservative skip
    if not classes:
        return None
    if len(classes) > 1:
        return _SKIP                # multi-class hypothesis not modelled
    return classes[0]


def _parse_term(term: str):
    """One additive term -> ('inv', sym, coeff) | ('const', None, value) | None."""
    t = term.strip().replace("*", " ").strip()
    if not t:
        return None
    found = [tok for tok in INV_TOKENS if re.search(r"\b" + re.escape(tok) + r"\b", t)]
    if found:
        inv = max(found, key=len)
        leftover = [x for x in found if x != inv and x not in inv]
        if leftover:
            return None             # two invariants glued in one term
        rest = re.sub(r"\b" + re.escape(inv) + r"\b", " ", t).strip()
        if rest in ("", "+"):
            coeff = 1.0
        elif rest == "-":
            coeff = -1.0
        else:
            coeff = _num(rest)
            if coeff is None:
                return None
        return ("inv", TOKEN2SYM[inv], coeff)
    c = _num(t)
    if c is None:
        return None
    return ("const", None, c)


def _parse_linear(side: str):
    """Linear side -> ({sym: coeff}, const) | None."""
    s = side.strip().replace("−", "-")
    if not s or "[" in s or "]" in s:
        return None
    if re.search(r"-\s*\(", s):      # negated parenthesised group: paren-strip unsafe
        return None
    s = s.replace("(", " ").replace(")", " ").replace("·", "*").replace("×", "*")
    s = re.sub(r"\s*-\s*", " + -", s)
    invd: Dict[str, float] = defaultdict(float)
    const = 0.0
    for term in s.split("+"):
        if not term.strip():
            continue
        r = _parse_term(term)
        if r is None:
            return None
        kind, sym, val = r
        if kind == "inv":
            invd[sym] += val
        else:
            const += val
    return dict(invd), const


def parse_relation(text: str) -> List[Tuple5]:
    """Parse one relation string into zero or more KNOWN_THEOREMS tuples."""
    text = text.strip().rstrip(",.")
    cls: Optional[str] = None
    m = re.match(r"(?i)^if\s+g\s+is\s+(.*?),\s*then\s+(.*)$", text)
    if m:
        cls = _parse_class(m.group(1))
        if cls is _SKIP:
            return []
        body = m.group(2)
    else:
        body = re.sub(r"(?i)^then\s+", "", text)
    body = body.strip().rstrip(",.")

    op = next((o for o in ("<=", ">=", "=") if o in body), None)
    if op is None:
        return []
    lhs_s, rhs_s = body.split(op, 1)
    L = _parse_linear(lhs_s)
    R = _parse_linear(rhs_s)
    if L is None or R is None:
        return []
    (Ld, Lc), (Rd, Rc) = L, R

    if op == "=":
        directions = [(Ld, Lc, Rd, Rc), (Rd, Rc, Ld, Lc)]
    elif op == ">=":
        directions = [(Rd, Rc, Ld, Lc)]
    else:
        directions = [(Ld, Lc, Rd, Rc)]

    out: List[Tuple5] = []
    for Ad, Ac, Bd, Bc in directions:          # encode  A <= B
        D: Dict[str, float] = defaultdict(float)
        for k, v in Ad.items():
            D[k] += v
        for k, v in Bd.items():
            D[k] -= v
        C = Ac - Bc
        D = {k: v for k, v in D.items() if abs(v) > 1e-9}
        pos = [k for k, v in D.items() if v > 0]
        if not pos:
            continue
        piv = next((k for k in pos if abs(D[k] - 1.0) < 1e-9), pos[0])
        dj = D[piv]
        rhs = {k: -v / dj for k, v in D.items() if k != piv}
        offset = -C / dj
        out.append((piv, rhs, offset, cls, text))
    return out


def load_relations() -> List[Tuple5]:
    """All curated relations as deduplicated KNOWN_THEOREMS tuples."""
    seen = set()
    result: List[Tuple5] = []
    for text in KNOWN_CONJECTURES + KNOWN_INEQUALITIES:
        for lhs, rhs, off, cls, name in parse_relation(text):
            key = (lhs, frozenset(rhs.items()), round(off, 9), cls)
            if key in seen:
                continue
            seen.add(key)
            result.append((lhs, rhs, off, cls, name))
    return result
