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

# Non-restricting base predicates that graffiti3 carries on essentially every
# conjecture (G is connected and non-trivial). They do not restrict the validity
# of an invariant *upper* bound, so they must not be counted as a class
# hypothesis — otherwise a genuinely single-class statement such as
# ``(nontrivial ∧ bipartite) ⇒ …`` looks two-class and is skipped.
_BASE_CLASSES = {"nontrivial", "connected"}

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
    return inequality_from_pretty(pretty, cols)


def inequality_from_pretty(pretty: str, cols: List[str]) -> Optional[Inequality]:
    """Linear ``Inequality`` from a pretty string ``[(cond) ⇒] lhs REL rhs``."""
    hypothesis = None
    if "⇒" in pretty:                                   # "(cond) ⇒ body"
        cond, pretty = pretty.split("⇒", 1)
        conds = [c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", cond)
                 and c not in _BASE_CLASSES]
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


def _body_parts(pretty: str, cols: List[str]):
    """(classes, body_invariants, relation, constants) for a conditioned
    conjecture, else None. ``classes`` are the boolean class columns in the
    hypothesis; ``body_invariants`` the numeric invariants in the bounded
    relation; ``constants`` the bare integers in the body."""
    if not isinstance(pretty, str):
        return None
    if "⇒" not in pretty and "=>" not in pretty:
        return None
    cond, body = re.split(r"⇒|=>", pretty, maxsplit=1)
    classes = [c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", cond)
               and c not in _BASE_CLASSES]
    rel = next((r for r in ("≤", "≥", "<=", ">=", "=") if r in body), None)
    if rel is None:
        return None
    body_invs = {c for c in cols if re.search(r"\b" + re.escape(c) + r"\b", body)}
    consts = {int(m) for m in re.findall(r"(?<![\w.])\d+(?![\w./])", body)}
    return classes, body_invs, _REL.get(rel, rel), consts


def conditioned_known(pretty, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """Flag conditioned conjectures that restate a perfect-graph property or a
    class definition — the classical results the unconditioned table misses.

    Accepts either a native (with ``.pretty()``) or a pretty string."""
    if not isinstance(pretty, str):
        try:
            pretty = pretty.pretty()
        except Exception:
            return False, None
    parts = _body_parts(pretty, cols)
    if parts is None:
        return False, None
    classes, invs, _rel, consts = parts
    if not classes:
        return False, None
    # a fact proved for a superclass holds for the subclass (tree ⊂ bipartite ⊂
    # perfect, cubic ⊂ regular, …), so inherit superclass class-definitional rules
    cls = set(classes)
    for c in list(cls):
        cls |= novelty.SUPERCLASSES.get(c, set())
    perfect = any(c in _PERFECT_CLASSES for c in cls)

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


def _inequality_known(pretty: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """A single linear (in)equality string implied by the known table?"""
    ineq = inequality_from_pretty(pretty, cols)
    if ineq is None:
        return False, None
    c = Conjecture(statement="", inequality=ineq, generation_method="cegis-graffiti3")
    try:
        return novelty.classify(c)
    except Exception:
        return False, None


# strict/loose negation:  ¬(a < b) ≡ (a ≥ b), etc.  Only the two ordered forms
# whose negation is a *non-strict* bound (≤ / ≥, the tabled shapes) are useful.
_NEG = {"<": "≥", ">": "≤", "≤": ">", "≥": "<", "<=": "≥", ">=": "≤"}


def _equality_known(stmt: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """An equality ``[(H) ⇒] f = g`` is known iff *both* f ≤ g and f ≥ g are
    implied by the table — i.e. the two bounds are simultaneously necessary and
    sufficient."""
    body = stmt.split("⇒")[-1]
    if "=" not in body or any(r in body for r in ("≤", "≥", "<=", ">=", "<", ">")):
        return False, None
    le, _ = _inequality_known(stmt.replace("=", "≤", 1), cols)
    ge, _ = _inequality_known(stmt.replace("=", "≥", 1), cols)
    if le and ge:
        return True, "equality: both bounds known"
    return False, None


def _necessary_condition_known(stmt: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """A Sophie necessary condition ``(A) ⇒ ¬C`` (A a numeric predicate, C a
    graph class) is known iff its contrapositive ``C ⇒ ¬A`` is a tabled class
    bound — e.g. ``(2 < χ) ⇒ ¬bipartite`` is the contrapositive of the known
    ``bipartite ⇒ χ ≤ 2``."""
    if "⇒" not in stmt:
        return False, None
    ante, cons = stmt.rsplit("⇒", 1)
    cons = cons.strip()
    if not cons.startswith("¬"):
        return False, None                          # only negative-class conclusions
    C = cons[1:].strip().strip("()").strip()
    if C not in cols or C in _GC2TABLE:             # C must be a boolean class
        return False, None
    rel = next((r for r in ("<=", ">=", "≤", "≥", "<", ">") if r in ante), None)
    if rel is None:
        return False, None
    nrel = _NEG[rel]
    if nrel not in ("≤", "≥"):                       # negation must be a tabled bound
        return False, None
    lhs, rhs = ante.split(rel, 1)
    contrapositive = f"({C}) ⇒ {lhs}{nrel}{rhs}"
    known, why = _classify_core(contrapositive, cols)
    if known:
        return True, f"necessary condition (contrapositive of: {why})"
    return False, None


# Textbook *sufficient conditions for class membership* (characterizations).
# These are the converse of the tabled class bounds and CANNOT be data-mined:
# a rare equality can agree with a class on every tested graph by coincidence
# (e.g. γ = a happens to imply K₄-free on the snapshot but is no theorem), so
# only genuine characterizations are listed here, by hand.
#   regular:   δ = Δ, and (since δ ≤ 2m/n ≤ ρ ≤ Δ) equality of any two of
#              {δ, 2m/n, ρ, Δ} collapses the chain ⇒ regular.
#   connected: Fiedler — the algebraic connectivity a(G) > 0 iff G is connected.
_REGULAR_EQ_PAIRS = {
    frozenset({"delta", "Delta"}), frozenset({"avg_deg", "Delta"}),
    frozenset({"avg_deg", "delta"}), frozenset({"spectral_radius", "Delta"}),
    frozenset({"spectral_radius", "avg_deg"}), frozenset({"spectral_radius", "delta"}),
}


def _sufficient_class_known(stmt: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """A Sophie sufficient condition ``(A) ⇒ C`` (C a positive graph class) is
    flagged known only when ``A`` is a textbook characterization of ``C``."""
    if "⇒" not in stmt:
        return False, None
    ante, cons = stmt.rsplit("⇒", 1)
    C = cons.strip().strip("()").strip()
    if C.startswith("¬") or C not in cols or C in _GC2TABLE:
        return False, None
    a = ante.strip()
    # Fiedler:  (0 < a(G)) ⇒ connected
    if C == "connected" and "algebraic_connectivity" in a \
            and ("<" in a or ">" in a) and re.search(r"(?<![\d.])0(?![\d.])", a):
        return True, "Fiedler: a(G) > 0 ⇔ connected"
    # regular:  equality of two invariants in the degree/spectral chain
    if C == "regular" and "=" in a and not any(r in a for r in ("≤", "≥", "<", ">")):
        syms = {_GC2TABLE[c] for c in cols
                if c in _GC2TABLE and re.search(r"\b" + re.escape(c) + r"\b", a)}
        if frozenset(syms) in _REGULAR_EQ_PAIRS:
            return True, "regular: δ ≤ 2m/n ≤ ρ ≤ Δ collapses ⇔ regular"
    return False, None


def _classify_core(stmt: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """Numeric / equality / class-definitional novelty for one statement string
    (no necessary-condition recursion)."""
    known, why = _inequality_known(stmt, cols)
    if known:
        return True, why
    eq = _equality_known(stmt, cols)
    if eq[0]:
        return eq
    return conditioned_known(stmt, cols)


def classify_statement(stmt: str, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """(is_known, why) for a conjecture *statement string*. Handles numeric
    inequalities and their conditioned forms, equalities (both bounds known),
    perfect-graph / class-definitional restatements, and Sophie necessary
    conditions ``(A) ⇒ ¬C`` — implications judged in both the sufficient and the
    necessary direction."""
    core = _classify_core(stmt, cols)
    if core[0]:
        return core
    nec = _necessary_condition_known(stmt, cols)
    if nec[0]:
        return nec
    return _sufficient_class_known(stmt, cols)


def classify_native(native, cols: List[str]) -> Tuple[bool, Optional[str]]:
    """(is_known, matched_theorem) for a graffiti3 native, via its pretty form."""
    try:
        pretty = native.pretty()
    except Exception:
        return False, None
    if not isinstance(pretty, str):
        return False, None
    return classify_statement(pretty, cols)
