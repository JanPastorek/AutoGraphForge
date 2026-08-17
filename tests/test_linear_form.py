"""Tests for pipeline/linear_form.py — the necessary-condition hypothesis parser.

The normalisation is the load-bearing part: it must turn a rational linear
comparison into an *equivalent* one over ℕ. A silently wrong rescaling would
produce a Lean theorem that is not the conjecture, so the tests below check the
arithmetic against hand-computed results and, for a range of graphs, against
direct evaluation of the original expression.
"""
from fractions import Fraction

import pytest

from pipeline import linear_form as lf

LEAN = {"order": "n G", "size": "m G", "alpha": "a G", "gamma": "g G"}


# -- parsing ------------------------------------------------------------------

def test_parses_coefficient_and_offset():
    coeffs, const = lf.parse_expression("((4/7) · alpha) + (-5/7)")
    assert coeffs == {"alpha": Fraction(4, 7)}
    assert const == Fraction(-5, 7)


def test_parses_bare_invariant_and_integer():
    assert lf.parse_expression("alpha") == ({"alpha": Fraction(1)}, Fraction(0))
    assert lf.parse_expression("87") == ({}, Fraction(87))


def test_collects_repeated_invariant():
    coeffs, const = lf.parse_expression("(alpha + (2 · alpha))")
    assert coeffs == {"alpha": Fraction(3)} and const == 0


def test_rejects_nonlinear_and_garbage():
    for bad in ["(alpha · alpha)", "(alpha / alpha)", "alpha +", "(alpha"]:
        with pytest.raises(lf.ParseError):
            lf.parse_expression(bad)


def test_relation_is_found_at_top_level_only():
    # the wrapper parens must come off, and a nested relation must not win
    assert lf.split_relation("(alpha ≤ (order + 1))")[1] == "≤"
    lhs, rel, rhs = lf.split_relation("((2 · alpha) < order)")
    assert rel == "<" and "alpha" in lhs and "order" in rhs


# -- normalisation ------------------------------------------------------------

def test_clears_denominators_and_moves_negatives():
    # gamma ≤ (4/7)·alpha − 5/7   ⇔   7·gamma + 5 ≤ 4·alpha
    left, rel, right = lf.normalise("(gamma ≤ (((4/7) · alpha) + (-5/7)))")
    assert rel == "≤"
    assert left == ({"gamma": 7}, 5)
    assert right == ({"alpha": 4}, 0)


def test_flips_reversed_relation():
    left, rel, right = lf.normalise("(order ≥ alpha)")
    assert rel == "≤" and left == ({"alpha": 1}, 0) and right == ({"order": 1}, 0)


def test_every_coefficient_is_a_nonnegative_int():
    for text in ["(gamma ≤ (((4/7) · alpha) + (-5/7)))",
                 "(((3 · gamma) + -6) < order)",
                 "(order ≤ ((3 · alpha) + -2))",
                 "(alpha = ((2/3) · order))"]:
        (lt, lk), _, (rt, rk) = lf.normalise(text)
        assert lk >= 0 and rk >= 0
        assert all(isinstance(v, int) and v > 0 for v in list(lt.values()) + list(rt.values()))


@pytest.mark.parametrize("text", [
    "(gamma ≤ (((4/7) · alpha) + (-5/7)))",
    "((2 · alpha) < order)",
    "(alpha < ((1/3) · size))",
    "(order ≤ ((3 · gamma) + -2))",
    "(alpha = ((2/3) · order))",
    "(87 < size)",
    "(((1/2) · order) ≤ ((1/3) · size))",
])
def test_normalisation_preserves_truth_value(text):
    """The ℕ form must agree with the rational form on every assignment."""
    lhs_raw, rel, rhs_raw = lf.split_relation(text)
    lc, lk = lf.parse_expression(lhs_raw)
    rc, rk = lf.parse_expression(rhs_raw)
    (lt, lkn), nrel, (rt, rkn) = lf.normalise(text)
    assert nrel == rel
    ops = {"≤": lambda a, b: a <= b, "<": lambda a, b: a < b,
           "=": lambda a, b: a == b}
    names = sorted(set(lc) | set(rc) | set(lt) | set(rt))
    for assignment in range(3 ** len(names)):
        env, rest = {}, assignment
        for nm in names:
            env[nm], rest = rest % 3 * 7, rest // 3      # 0, 7, 14
        def value(coeffs, const, env=env):
            return sum(c * env[n] for n, c in coeffs.items()) + const
        original = ops[rel](value(lc, lk), value(rc, rk))
        natural = ops[nrel](value({k: Fraction(v) for k, v in lt.items()}, lkn),
                            value({k: Fraction(v) for k, v in rt.items()}, rkn))
        assert original == natural, (text, env)


# -- rendering ----------------------------------------------------------------

def test_renders_lean_over_nat():
    assert lf.render_comparison("((2 · alpha) < order)", LEAN) == "2 * a G < n G"


def test_renders_empty_side_as_zero():
    assert lf.render_comparison("(0 ≤ alpha)", LEAN) == "0 ≤ a G"


def test_unsupported_invariant_blocks_rendering():
    assert lf.render_comparison("(radius < order)", LEAN) is None


# -- conclusions --------------------------------------------------------------

def test_parses_negated_and_conjunctive_conclusions():
    assert lf.parse_class_conclusion(" ¬tree") == [(True, "tree")]
    assert lf.parse_class_conclusion("subcubic & K_4_free") == [
        (False, "subcubic"), (False, "K_4_free")]
    assert lf.parse_class_conclusion("¬cubic & claw_free") == [
        (True, "cubic"), (False, "claw_free")]


def test_rejects_non_class_conclusion():
    assert lf.parse_class_conclusion("order ≤ size") is None
