"""
pipeline/linear_form.py — parse a rendered inequality into a linear form, and
normalise it to a form the Lean kernel can evaluate.

Why this exists
---------------
The class-conditioned exporter only ever had to handle ``invariant REL
invariant``. Necessary-condition survivors have a real expression on at least
one side::

    (domination_number ≤ ((4/7) · independence_number) + (-5/7))  ⇒  ¬cubic
    (((3 · zero_forcing_number) + -6) < connected_zero_forcing_number)  ⇒  ¬cubic

so they need parsing, not pattern-matching.

Rational coefficients would naturally live in ℝ (as the existing exports do) or
ℚ. Neither evaluates: ℝ is noncomputable, and ℚ was measured to get stuck at
``Rat.blt`` because the ℕ → ℚ cast does not reduce in the kernel. Every
invariant we support is ℕ-valued, though, so an equivalent inequality can always
be written in ℕ:

  * scale both sides by the (positive) lcm of the denominators, and
  * move the negative terms across, leaving non-negative coefficients on both
    sides — which also avoids ℕ's truncated subtraction.

Both steps preserve ``≤``, ``<`` and ``=`` exactly (multiplying by a positive
constant and adding the same quantity to both sides are order isomorphisms), so
the normalised statement is the original one, and it is the *same* statement in
the theorem and in its disproof — there is no ℝ-versus-ℕ gap between what we
prove and what we refute.
"""
from __future__ import annotations

import re
from fractions import Fraction
from math import lcm
from typing import Dict, List, Optional, Tuple

# Relations, normalised so the smaller side is always on the left.
RELATIONS = {"≤": "≤", "<": "<", "=": "=", "<=": "≤", ">=": "≥", "≥": "≥", ">": ">"}
_FLIP = {"≥": "≤", ">": "<"}

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|\d+|[()+\-·/*]")

# A linear form: coefficient per invariant, plus a constant.
LinearForm = Tuple[Dict[str, Fraction], Fraction]


class ParseError(ValueError):
    """The expression is outside the grammar we handle."""


def _tokenize(text: str) -> List[str]:
    stripped = _TOKEN.sub(" ", text)
    if stripped.strip():
        raise ParseError(f"unexpected characters: {stripped.strip()!r}")
    return _TOKEN.findall(text)


class _Parser:
    """Recursive descent over: sum → product → unary → atom.

    The input is fully parenthesised in practice, so precedence rarely bites,
    but handling it properly keeps the parser honest about inputs like
    ``2 · a + 1``.
    """

    def __init__(self, tokens: List[str]):
        self.toks = tokens
        self.i = 0

    def peek(self) -> Optional[str]:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise ParseError("unexpected end of expression")
        self.i += 1
        return tok

    def expect(self, tok: str) -> None:
        got = self.take()
        if got != tok:
            raise ParseError(f"expected {tok!r}, got {got!r}")

    def parse(self) -> LinearForm:
        form = self.sum()
        if self.peek() is not None:
            raise ParseError(f"trailing tokens from {self.peek()!r}")
        return form

    def sum(self) -> LinearForm:
        coeffs, const = self.product()
        while self.peek() in ("+", "-"):
            sign = Fraction(1) if self.take() == "+" else Fraction(-1)
            c2, k2 = self.product()
            for name, c in c2.items():
                coeffs[name] = coeffs.get(name, Fraction(0)) + sign * c
            const += sign * k2
        return coeffs, const

    def product(self) -> LinearForm:
        coeffs, const = self.unary()
        while self.peek() in ("·", "*", "/"):
            op = self.take()
            c2, k2 = self.unary()
            # Only linear forms: one side of every product must be a constant,
            # and a divisor must be a nonzero constant.
            if op == "/":
                if c2:
                    raise ParseError("division by a non-constant")
                if k2 == 0:
                    raise ParseError("division by zero")
                coeffs = {n: c / k2 for n, c in coeffs.items()}
                const /= k2
            elif not coeffs:
                coeffs, const = {n: const * c for n, c in c2.items()}, const * k2
            elif not c2:
                coeffs, const = {n: c * k2 for n, c in coeffs.items()}, const * k2
            else:
                raise ParseError("product of two non-constant terms is not linear")
        return coeffs, const

    def unary(self) -> LinearForm:
        if self.peek() == "-":
            self.take()
            coeffs, const = self.unary()
            return {n: -c for n, c in coeffs.items()}, -const
        if self.peek() == "+":
            self.take()
        return self.atom()

    def atom(self) -> LinearForm:
        tok = self.take()
        if tok == "(":
            form = self.sum()
            self.expect(")")
            return form
        if tok.isdigit():
            return {}, Fraction(int(tok))
        if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", tok):
            return {tok: Fraction(1)}, Fraction(0)
        raise ParseError(f"unexpected token {tok!r}")


def parse_expression(text: str) -> LinearForm:
    """``((4/7) · alpha) + (-5/7)`` → ({'alpha': 4/7}, -5/7)."""
    return _Parser(_tokenize(text)).parse()


def strip_outer_parens(text: str) -> str:
    """Drop a paren pair that encloses the whole expression, repeatedly.

    Statements arrive fully parenthesised — ``(a ≤ (b + 1))`` — so the relation
    is not at the top level until the wrapper comes off.
    """
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        for pos, ch in enumerate(text):
            depth += (ch == "(") - (ch == ")")
            if depth == 0 and pos < len(text) - 1:
                return text                    # the pair does not span the whole
        text = text[1:-1].strip()
    return text


def split_relation(text: str) -> Optional[Tuple[str, str, str]]:
    """(lhs, relation, rhs) for the top-level relation symbol in ``text``.

    Only depth 0 counts: a relation nested inside parentheses belongs to a
    subexpression, not to this comparison.
    """
    text = strip_outer_parens(text)
    depth = 0
    for pos, ch in enumerate(text):
        depth += (ch == "(") - (ch == ")")
        if depth:
            continue
        for sym in ("<=", ">=", "≤", "≥", "<", ">", "="):
            if text.startswith(sym, pos):
                return text[:pos], RELATIONS[sym], text[pos + len(sym):]
    return None


# A normalised comparison: both sides have non-negative *integer* coefficients.
NatSide = Tuple[Dict[str, int], int]


def normalise(text: str) -> Optional[Tuple[NatSide, str, NatSide]]:
    """Rewrite a rational linear comparison as an equivalent one over ℕ.

    Returns ``((left_terms, left_const), relation, (right_terms, right_const))``
    with every coefficient and constant a non-negative int, or None if the
    input is outside the grammar. The relation is always one of ``≤ < =``.
    """
    split = split_relation(text)
    if split is None:
        return None
    raw_lhs, rel, raw_rhs = split
    try:
        lc, lk = parse_expression(raw_lhs)
        rc, rk = parse_expression(raw_rhs)
    except ParseError:
        return None

    if rel in _FLIP:                       # a ≥ b  ⇔  b ≤ a
        lc, lk, rc, rk = rc, rk, lc, lk
        rel = _FLIP[rel]

    # difference = lhs − rhs, then scale away every denominator
    diff = dict(lc)
    for name, c in rc.items():
        diff[name] = diff.get(name, Fraction(0)) - c
    const = lk - rk
    denominators = [f.denominator for f in list(diff.values()) + [const]]
    scale = lcm(*denominators) if denominators else 1

    left_terms: Dict[str, int] = {}
    right_terms: Dict[str, int] = {}
    for name, c in diff.items():
        v = int(c * scale)
        if v > 0:
            left_terms[name] = v
        elif v < 0:
            right_terms[name] = -v
    k = int(const * scale)
    left_const, right_const = (k, 0) if k > 0 else (0, -k)
    return (left_terms, left_const), rel, (right_terms, right_const)


def render_side(side: NatSide, lean_of: Dict[str, str], graph: str = "G") -> Optional[str]:
    """A ℕ-valued Lean expression for one side, or None if an invariant is
    unsupported. An empty side renders as ``0``."""
    terms, const = side
    parts: List[str] = []
    for name in sorted(terms):
        lean = lean_of.get(name)
        if lean is None:
            return None
        expr = lean.replace("G", graph) if graph != "G" else lean
        coefficient = terms[name]
        parts.append(expr if coefficient == 1 else f"{coefficient} * {expr}")
    if const or not parts:
        parts.append(str(const))
    return " + ".join(parts)


def render_comparison(text: str, lean_of: Dict[str, str]) -> Optional[str]:
    """A ℕ-valued Lean proposition equivalent to the rendered comparison."""
    normalised = normalise(text)
    if normalised is None:
        return None
    left, rel, right = normalised
    lhs = render_side(left, lean_of)
    rhs = render_side(right, lean_of)
    if lhs is None or rhs is None:
        return None
    return f"{lhs} {rel} {rhs}"


def parse_class_conclusion(text: str) -> Optional[List[Tuple[bool, str]]]:
    """``subcubic & ¬K_4_free`` → [(False, 'subcubic'), (True, 'K_4_free')].

    The bool is "negated". Returns None if the conclusion is not a conjunction
    of (possibly negated) bare class names — an inequality conclusion belongs to
    the class-conditioned exporter, not here.
    """
    clauses: List[Tuple[bool, str]] = []
    for raw in text.split("&"):
        clause = raw.strip()
        negated = clause.startswith("¬")
        if negated:
            clause = clause[1:].strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", clause):
            return None
        clauses.append((negated, clause))
    return clauses or None


def invariants(text: str) -> List[str]:
    """Identifiers appearing in a comparison (invariants and any stray names)."""
    split = split_relation(text)
    source = "".join(split[::2]) if split else text
    return sorted(set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", source)))
