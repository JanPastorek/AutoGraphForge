"""
pipeline/candidate_filters.py — structural filters on generated conjectures.

A "constant bound" is a conjecture with an invariant on one side and *only a
constant* on the other (``clique_number ≤ 20``, ``9 ≤ size``, ``order = 14``).
*Unconditioned* ones are degenerate: over all graphs an invariant isn't bounded
by a constant, so they're seed-specific or trivial, and they pollute the
candidate set. They are dropped from the inequality stream here.

A *conditioned* constant bound is kept, because a graph class can genuinely bound
an invariant by a constant — ``(K_4_free) ⇒ clique_number ≤ 3`` and
``(triangle_free) ⇒ clique_number ≤ 2`` are real theorems. Refutation decides
those: the symbolic tier kills the false ones (``(subcubic) ⇒ order ≤ 14``) with
an in-class witness and leaves the true ones standing.

Sophie sufficient-conditions are a *separate* list and never pass through this
filter, so biconditional/sufficient-condition conjectures are kept too.
"""
from __future__ import annotations

import re
from typing import List

_RELS = ("≤", "≥", "<=", ">=", "=")


def _has_invariant(side: str, cols: List[str]) -> bool:
    return any(re.search(r"\b" + re.escape(c) + r"\b", side) for c in cols)


def is_constant_bound(native, all_cols: List[str]) -> bool:
    """True iff the conjecture is an *unconditioned* invariant-vs-constant bound.

    A real class hypothesis (``(K_4_free) ⇒ clique_number ≤ 3``) makes the
    constant bound potentially valid, so it is NOT flagged — only a missing or
    vacuous (``TRUE``) hypothesis counts."""
    try:
        pretty = native.pretty()
    except Exception:
        return False
    if "⇒" in pretty or "=>" in pretty:
        cond = re.split(r"⇒|=>", pretty, maxsplit=1)[0]
        # a non-trivial class condition references a (boolean) invariant column;
        # 'TRUE'/parens/∧ alone is vacuous → still treated as unconditioned
        if _has_invariant(cond, all_cols):
            return False
    body = re.split(r"⇒|=>", pretty)[-1]               # the bounded relation
    rel = next((r for r in _RELS if r in body), None)
    if rel is None:
        return False
    lhs, rhs = body.split(rel, 1)
    # constant bound ⇔ exactly one side mentions an invariant
    return _has_invariant(lhs, all_cols) != _has_invariant(rhs, all_cols)


def drop_constant_bounds(natives: list, all_cols: List[str]) -> list:
    """Filter an inequality list, removing invariant-vs-constant bounds."""
    return [c for c in natives if not is_constant_bound(c, all_cols)]


def hypothesis_support(native, frame):
    """Number of ``frame`` rows the conjecture's hypothesis admits.

    This is the evidence a conditioned conjecture actually rests on. Returns
    ``None`` when the hypothesis cannot be evaluated at all — "we could not
    measure this" is not the same as "this has no support", and the callers
    below must not confuse the two.
    """
    try:
        applicable, _, _ = native.check(frame)
        return int(applicable.sum())
    except Exception:
        return None


def drop_low_support(natives: list, frame, min_support: int) -> list:
    """Drop conjectures whose hypothesis holds for too few seed graphs.

    A bound asserted on a class with a handful of representatives survives
    refutation for lack of evidence rather than because it is true: the run
    that produced this filter left survivors resting on a single graph. Gating
    at generation also saves the refutation work they would otherwise consume.

    Set ``min_support`` to 0 to disable.
    """
    if not min_support:
        return natives
    kept = []
    for c in natives:
        support = hypothesis_support(c, frame)
        if support is None or support >= min_support:
            kept.append(c)          # unmeasurable ⇒ leave it to refutation
    return kept


def is_decorative(native, frame) -> bool:
    """True when the hypothesis restricts nothing the relation needs.

    The relation holds on *every* row, so conditioning it on a class adds no
    content — ``(cubic) ⇒ harmonic_index ≤ 29`` is a fact about the corpus's
    bounded size range, not about cubic graphs. Only conditioned conjectures
    can be decorative; an unconditioned one is judged on its own terms.
    """
    if getattr(native, "condition", None) is None:
        return False
    try:
        holds = native.relation.evaluate(frame).reindex(frame.index)
    except Exception:
        return False
    # An all-NaN column makes `holds` empty/undefined — not evidence of anything.
    holds = holds.dropna()
    if holds.empty:
        return False
    return bool(holds.all())


def drop_decorative(natives: list, frame) -> list:
    """Drop conditioned conjectures whose relation holds frame-wide."""
    return [c for c in natives if not is_decorative(c, frame)]
