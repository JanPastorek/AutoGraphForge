"""
pipeline/candidate_filters.py — structural filters on generated conjectures.

A "constant bound" is a conjecture with an invariant on one side and *only a
constant* on the other (``clique_number ≤ 20``, ``9 ≤ size``, ``order = 14``).
These are degenerate: either seed-specific (false once the order/degree grows) or
trivial, and they pollute the candidate set. They are dropped from the inequality
stream here. Sophie sufficient-conditions are a *separate* list and never pass
through this filter, so biconditional/sufficient-condition conjectures are kept.
"""
from __future__ import annotations

import re
from typing import List

_RELS = ("≤", "≥", "<=", ">=", "=")


def _has_invariant(side: str, cols: List[str]) -> bool:
    return any(re.search(r"\b" + re.escape(c) + r"\b", side) for c in cols)


def is_constant_bound(native, all_cols: List[str]) -> bool:
    """True iff the conjecture bounds an invariant by a pure constant (exactly one
    side carries an invariant). The hypothesis (``(cond) ⇒ …``) is ignored — only
    the bounded relation's two sides are inspected."""
    try:
        pretty = native.pretty()
    except Exception:
        return False
    body = pretty.split("⇒")[-1].split("=>")[-1]      # drop any hypothesis
    rel = next((r for r in _RELS if r in body), None)
    if rel is None:
        return False
    lhs, rhs = body.split(rel, 1)
    # constant bound ⇔ exactly one side mentions an invariant
    return _has_invariant(lhs, all_cols) != _has_invariant(rhs, all_cols)


def drop_constant_bounds(natives: list, all_cols: List[str]) -> list:
    """Filter an inequality list, removing invariant-vs-constant bounds."""
    return [c for c in natives if not is_constant_bound(c, all_cols)]
