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
