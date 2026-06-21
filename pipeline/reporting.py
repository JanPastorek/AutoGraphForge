"""
pipeline/reporting.py — conjecture complexity metric, sorting, and pretty printing.

Complexity is defined as the number of *arithmetic operations* a conjecture's
right-hand side needs (additions/subtractions, multiplications/divisions, powers,
roots, logs, min/max, …). Simpler conjectures (fewer operations) are usually the
more valuable ones, so this gives an optional parsimony-based ranking alongside
the score / touch-count rankings.
"""
from __future__ import annotations

import re
from typing import Iterable, List, Optional

from conjecture import Conjecture

# arithmetic tokens that count as one operation each, in statement strings
_OP_WORDS = ("sqrt", "√", "log₂", "log2", "log", "maximum", "minimum",
             "max", "min", "abs", "floor", "ceil")
_OP_SYMS = ("+", "-", "*", "·", "×", "/", "^", "**")
# relation / structural tokens that are NOT arithmetic operations
_REL = ("≤", "≥", "<=", ">=", "==", "=", "<", ">", "⇒", "->", "→", "⇔")


def complexity(conj: Conjecture) -> int:
    """Number of arithmetic operations in the conjecture's conclusion."""
    ineq = conj.inequality
    if ineq is not None:
        rhs_terms = 1 + len(ineq.extra_terms)               # inv_b + extras
        adds = (rhs_terms - 1) + (1 if abs(ineq.offset) > 1e-12 else 0)
        coeffs = [ineq.coeff_a, ineq.coeff_b] + [c for c, _ in ineq.extra_terms]
        mults = sum(1 for c in coeffs
                    if abs(c - 1.0) > 1e-9 and abs(c) > 1e-9)
        return adds + mults
    return _string_complexity(conj.statement or "")


def _string_complexity(stmt: str) -> int:
    """Count arithmetic operators/functions in an expression string."""
    s = stmt
    # drop the hypothesis part ("(...) ⇒ ..." or "... (for X graphs)")
    for sep in ("⇒", "->", "→"):
        if sep in s:
            s = s.split(sep, 1)[1]
    s = re.sub(r"\(for .*?graphs\)", "", s)
    # remove the single relation operator so it is not counted as arithmetic
    for r in _REL:
        s = s.replace(r, " ", 1) if r in s else s
    n = 0
    for w in _OP_WORDS:
        n += len(re.findall(rf"(?<![A-Za-z₂]){re.escape(w)}", s))
        s = s.replace(w, " ")          # avoid double counting (e.g. log inside log₂)
    # unary minus heuristic: leading "-" of a token is not an op; count binary only
    n += sum(s.count(sym) for sym in _OP_SYMS)
    return n


def annotate_complexity(conjs: Iterable[Conjecture]) -> None:
    """Store complexity in each conjecture's metadata (in place)."""
    for c in conjs:
        c.metadata["complexity"] = complexity(c)


_SORT_KEYS = {
    "score":      lambda c: -float(c.score),
    "complexity": lambda c: (complexity(c), -float(c.score)),
    "touches":    lambda c: -len(c.tightness_witnesses),
}


def sort_conjectures(conjs: List[Conjecture], by: str = "score") -> List[Conjecture]:
    """Return conjectures sorted by 'score', 'complexity' (simplest first), or
    'touches' (most sharp graphs first)."""
    key = _SORT_KEYS.get(by, _SORT_KEYS["score"])
    return sorted(conjs, key=key)


def print_conjectures(conjs: List[Conjecture], *, sort_by: str = "score",
                      top: Optional[int] = 40, show_lean: bool = False,
                      title: str = "CONJECTURES") -> None:
    """Pretty-print a list of conjectures (TxGraffiti-style), with novelty,
    status, score, complexity and touch count."""
    ordered = sort_conjectures(conjs, by=sort_by)
    if top is not None:
        ordered = ordered[:top]
    print("\n" + "=" * 78)
    print(f"  {title}  (n={len(conjs)}, sorted by {sort_by}, showing {len(ordered)})")
    print("=" * 78)
    for i, c in enumerate(ordered, 1):
        novelty = c.metadata.get("novelty", "novel" if c.metadata.get("novel", True) else "known")
        tag = "NOVEL" if novelty == "novel" else "known"
        stmt = c.statement or (str(c.inequality) if c.inequality else "")
        print(f"{i:3d}. [{tag:5s}] ({c.generation_method}) {stmt}")
        print(f"       score={c.score:6.2f}  complexity={complexity(c):2d}  "
              f"touches={len(c.tightness_witnesses):3d}  status={c.status.value}")
        if show_lean and c.lean_statement:
            print("       lean: " + c.lean_statement.splitlines()[0])
