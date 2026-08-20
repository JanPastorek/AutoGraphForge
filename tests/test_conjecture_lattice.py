"""Tests for pipeline/conjecture_lattice.py — dedup, lifting, and the
decorative-hypothesis diagnostic.

The direction of the subsumption relation is the thing most easily got backwards
(a *weaker* hypothesis subsumes a stronger one, not the other way round), and
getting it wrong would silently discard the general form and keep the special
case. It is tested in both directions.
"""
import pandas as pd
import pytest

from pipeline import conjecture_lattice as cl


def conj(statement, touches=0):
    return {"statement": statement, "metadata": {"touches": touches}}


# -- parsing ------------------------------------------------------------------

def test_parses_class_conditioned_only():
    got = cl.parse_survivors([
        conj("((nontrivial) ∧ (tree)) ⇒ order ≤ size"),
        conj("((2 · independence_number) < order) ⇒ ¬tree"),   # necessary cond.
        conj("order ≤ size"),                                   # unconditioned
        conj("((tree)) ⇒ harmonic_index ≤ residue"),
    ])
    assert [sorted(s.classes) for s in got] == [["nontrivial", "tree"], ["tree"]]


def test_keeps_touch_count_and_normalised_body():
    s = cl.parse_survivors([conj("((tree)) ⇒ (2 · order) ≤ size", touches=7)])[0]
    assert s.touches == 7
    assert s.norm == (({"order": 2}, 0), "≤", ({"size": 1}, 0))


# -- the subsumption relation -------------------------------------------------

def test_weaker_is_directional():
    # a tree is bipartite, so "bipartite" is the weaker hypothesis
    assert cl.weaker(frozenset({"tree"}), frozenset({"bipartite"}))
    assert not cl.weaker(frozenset({"bipartite"}), frozenset({"tree"}))


def test_dropping_a_conjunct_weakens():
    assert cl.weaker(frozenset({"tree", "cograph"}), frozenset({"tree"}))
    assert not cl.weaker(frozenset({"tree"}), frozenset({"tree", "cograph"}))


def test_equivalent_hypotheses_subsume_each_other():
    # a tree is always planar, so the two hypotheses describe the same graphs
    a, b = frozenset({"tree", "planar"}), frozenset({"tree"})
    assert cl.weaker(a, b) and cl.weaker(b, a)


def test_equivalent_hypotheses_keep_one_representative():
    survivors = cl.parse_survivors([
        conj("((tree) ∧ (planar)) ⇒ order ≤ size"),
        conj("((tree)) ⇒ order ≤ size"),
    ])
    subsumed = cl.find_subsumed(survivors)
    # exactly one dropped, and it is the wordier statement
    assert subsumed == {0: 1}


def test_identical_hypotheses_do_not_subsume():
    assert not cl.weaker(frozenset({"tree"}), frozenset({"tree"}))


def test_find_subsumed_keeps_the_general_form():
    survivors = cl.parse_survivors([
        conj("((tree) ∧ (cograph)) ⇒ order ≤ size"),
        conj("((tree)) ⇒ order ≤ size"),
        conj("((eulerian)) ⇒ order ≤ size"),     # unrelated class: independent
    ])
    subsumed = cl.find_subsumed(survivors)
    assert set(subsumed) == {0}                  # only the narrower one goes
    assert subsumed[0] == 1


def test_find_subsumed_ignores_different_bodies():
    survivors = cl.parse_survivors([
        conj("((tree) ∧ (cograph)) ⇒ order ≤ size"),
        conj("((tree)) ⇒ order ≤ (2 · size)"),
    ])
    assert cl.find_subsumed(survivors) == {}


def test_subsumption_uses_the_isgci_lattice():
    # bipartite ⊆ triangle_free comes from the imported hierarchy, not by hand
    survivors = cl.parse_survivors([
        conj("((bipartite)) ⇒ order ≤ size"),
        conj("((triangle_free)) ⇒ order ≤ size"),
    ])
    assert cl.find_subsumed(survivors) == {0: 1}


# -- generalisation candidates ------------------------------------------------

def test_generalisations_drop_and_relax():
    got = cl.generalisations(frozenset({"tree", "cubic"}))
    assert frozenset({"tree"}) in got and frozenset({"cubic"}) in got
    assert frozenset({"cubic", "bipartite"}) in got      # tree → bipartite
    assert frozenset({"tree", "subcubic"}) in got        # cubic → subcubic
    assert frozenset({"tree", "cubic"}) not in got       # never itself


def test_generalisations_restricted_to_evaluable_classes():
    got = cl.generalisations(frozenset({"tree"}), available=["bipartite"])
    assert got == [frozenset({"bipartite"})]             # planar/perfect dropped


# -- pool evaluation ----------------------------------------------------------

@pytest.fixture
def evaluator():
    frame = pd.DataFrame({
        "tree":      [True,  True,  False, False],
        "bipartite": [True,  True,  True,  False],
        "cograph":   [False, False, False, False],
        "order":     [3.0,   4.0,   5.0,   9.0],
        "size":      [2.0,   3.0,   6.0,   4.0],
        "spotty":    [1.0,   float("nan"), 1.0, 1.0],
    })
    return cl.PoolEvaluator(frame, class_columns=["tree", "bipartite", "cograph"])


def test_survives_and_support(evaluator):
    # order ≤ size holds on the two non-trees only
    norm = (({"order": 1}, 0), "≤", ({"size": 1}, 0))
    assert evaluator.survives(frozenset({"tree"}), norm) == (False, 2)
    assert evaluator.survives(frozenset({"bipartite"}), norm) == (False, 3)


def test_strict_and_equality_relations(evaluator):
    assert evaluator.survives(
        frozenset({"tree"}), (({"size": 1}, 0), "<", ({"order": 1}, 0))) == (True, 2)
    assert evaluator.survives(
        frozenset({"tree"}), (({"size": 1}, 1), "=", ({"order": 1}, 0))) == (True, 2)


def test_rows_with_a_missing_invariant_are_skipped(evaluator):
    ok, support = evaluator.survives(
        frozenset({"tree"}), (({"spotty": 1}, 0), "≤", ({}, 1)))
    assert ok is True and support == 1          # the NaN row does not count


def test_unmodelled_class_matches_nothing(evaluator):
    # "planar" has no column: the hypothesis must not be silently widened
    ok, support = evaluator.survives(
        frozenset({"planar"}), (({"order": 1}, 0), "≤", ({"size": 1}, 0)))
    assert ok is None and support == 0


def test_empty_hypothesis_covers_the_whole_pool(evaluator):
    _, support = evaluator.survives(
        frozenset(), (({"order": 1}, 0), "≤", ({"size": 1}, 0)))
    assert support == 4


# -- lifting and the diagnostic ----------------------------------------------

def test_lift_prefers_the_largest_support(evaluator):
    # `size ≤ 6` holds on trees, and still holds on the wider bipartite class
    s = cl.parse_survivors([conj("((tree) ∧ (bipartite)) ⇒ size ≤ 6")])[0]
    target, support = cl.lift(s, evaluator)
    assert target == frozenset({"bipartite"}) and support == 3


def test_lift_rejects_a_relaxation_that_is_refuted(evaluator):
    # size < order holds on the trees but fails on the third bipartite graph,
    # so the only surviving relaxation is the narrower one
    s = cl.parse_survivors([conj("((tree) ∧ (bipartite)) ⇒ size < order")])[0]
    target, support = cl.lift(s, evaluator)
    assert target == frozenset({"tree"}) and support == 2


def test_lift_returns_none_when_no_relaxation_survives(evaluator):
    s = cl.parse_survivors([conj("((tree)) ⇒ (2 · size) ≤ order")])[0]
    assert cl.lift(s, evaluator) is None


def test_decorative_when_the_body_needs_no_hypothesis(evaluator):
    s = cl.parse_survivors([conj("((tree)) ⇒ order ≤ 9")])[0]
    assert cl.is_decorative(s, evaluator) is True


def test_not_decorative_when_the_hypothesis_does_work(evaluator):
    s = cl.parse_survivors([conj("((tree)) ⇒ size < order")])[0]
    assert cl.is_decorative(s, evaluator) is False


# -- corpus assembly ----------------------------------------------------------

def test_load_pool_merges_duplicate_graphs(tmp_path):
    """The same graph in two caches must be merged, not picked arbitrarily.

    Caches disagree only by blank cells (an invariant that timed out in one run
    and computed in the next), so the merged row must take whichever value
    exists — and must not depend on the order the caches are listed in.
    """
    a = pd.DataFrame({"order": [3.0, 4.0], "size": [float("nan"), 3.0]},
                     index=["A", "B"])
    b = pd.DataFrame({"order": [3.0], "size": [2.0]}, index=["A"])
    pa, pb = tmp_path / "a.parquet", tmp_path / "b.parquet"
    a.to_parquet(pa)
    b.to_parquet(pb)

    forward = cl.load_pool([str(pa), str(pb)])
    reverse = cl.load_pool([str(pb), str(pa)])
    assert len(forward) == len(reverse) == 2          # A merged, not doubled
    assert forward.loc["A", "size"] == 2.0            # the value beat the blank
    assert reverse.loc["A", "size"] == 2.0            # order does not matter
    assert forward.loc["B", "size"] == 3.0


def test_load_pool_returns_none_without_readable_caches(tmp_path):
    assert cl.load_pool([str(tmp_path / "missing.parquet")]) is None


# -- touch counts -------------------------------------------------------------

def test_touch_counts_only_tight_graphs(evaluator):
    # order ≤ size is tight nowhere among trees (3≤2, 4≤3 both fail), and the
    # bound order ≤ size + 1 is tight on both
    assert evaluator.touches(
        frozenset({"tree"}), (({"order": 1}, 0), "≤", ({"size": 1}, 1))) == 2
    assert evaluator.touches(
        frozenset({"tree"}), (({"order": 1}, 0), "≤", ({"size": 1}, 5))) == 0


def test_touch_respects_the_class_hypothesis(evaluator):
    """The count must fall when the hypothesis narrows.

    This is the property the pipeline's own touch_count misses: it evaluates
    the relation over the whole seed frame, so a class-conditioned conjecture
    is credited with tight graphs that are not in its class at all.
    """
    # size + 1 = order is tight on both trees
    at_trees = (({"size": 1}, 1), "=", ({"order": 1}, 0))
    assert evaluator.touches(frozenset(), at_trees) == 2
    assert evaluator.touches(frozenset({"tree"}), at_trees) == 2

    # size = order + 1 is tight only on the bipartite non-tree, so narrowing
    # the hypothesis from bipartite to tree must drop the count to zero
    at_non_tree = (({"size": 1}, 0), "=", ({"order": 1}, 1))
    assert evaluator.touches(frozenset(), at_non_tree) == 1
    assert evaluator.touches(frozenset({"bipartite"}), at_non_tree) == 1
    assert evaluator.touches(frozenset({"tree"}), at_non_tree) == 0


def test_touch_is_zero_for_an_unmodelled_class(evaluator):
    assert evaluator.touches(
        frozenset({"planar"}), (({"order": 1}, 0), "≤", ({"size": 1}, 1))) == 0


def test_touch_skips_rows_missing_an_invariant(evaluator):
    assert evaluator.touches(
        frozenset({"tree"}), (({"spotty": 1}, 0), "=", ({}, 1))) == 1


def test_merge_prefers_the_row_that_actually_computed_something(tmp_path):
    """A boolean column cannot hold NaN, so an uncomputed class flag is stored
    as ``False`` and looks like a genuine negative. Merging by "first non-null
    per column" then lets that placeholder override a real ``True``. The graph
    ``A?`` (2 vertices, no edges) was recorded ``nontrivial=False`` with
    ``order=NaN``, which excluded it from every hypothesis it satisfied and let
    a false conjecture survive.
    """
    stub = pd.DataFrame({"order": [float("nan")], "nontrivial": [False]},
                        index=["A?"])
    real = pd.DataFrame({"order": [2.0], "nontrivial": [True]}, index=["A?"])
    a, b = tmp_path / "a_stub.parquet", tmp_path / "b_real.parquet"
    stub.to_parquet(a)
    real.to_parquet(b)

    for order in ([str(a), str(b)], [str(b), str(a)]):
        merged = cl.load_pool(order)
        assert len(merged) == 1
        assert merged.loc["A?", "order"] == 2.0
        assert merged.loc["A?", "nontrivial"] is True or \
               bool(merged.loc["A?", "nontrivial"]) is True


def test_merge_still_fills_gaps_from_the_less_complete_row(tmp_path):
    # completeness decides the winner, but a cell only the loser has is kept
    a = pd.DataFrame({"order": [2.0], "size": [1.0], "extra": [float("nan")]},
                     index=["X"])
    b = pd.DataFrame({"order": [2.0], "size": [float("nan")], "extra": [7.0]},
                     index=["X"])
    pa, pb = tmp_path / "a.parquet", tmp_path / "b.parquet"
    a.to_parquet(pa)
    b.to_parquet(pb)
    merged = cl.load_pool([str(pa), str(pb)])
    assert merged.loc["X", "size"] == 1.0
    assert merged.loc["X", "extra"] == 7.0


def test_collapses_restatements_of_the_same_bound():
    """Same body, same hypothesis, different surface form.

    `b <= r + 1` and `b - 1 <= r` are one claim; `linear_form` already maps them
    to a single canonical body. They were both reported because `weaker` is
    strict (`a != b`), so neither is weaker than the other and the subsumption
    loop skipped both — 82 of the 2,677 ranked survivors were such restatements,
    two of them adjacent at ranks 18 and 19 of the audited top 100.
    """
    survivors = cl.parse_survivors([
        {"statement": "(nontrivial) ⇒ burning_number ≤ (radius + 1)"},
        {"statement": "(nontrivial) ⇒ (burning_number + -1) ≤ radius"},
    ])
    assert len(survivors) == 2
    assert survivors[0].body_key == survivors[1].body_key, "canonical body differs"

    subsumed = cl.find_subsumed(survivors)
    assert len(subsumed) == 1, "exactly one of the pair must be dropped"
    dropped, kept = next(iter(subsumed.items()))
    assert kept not in subsumed, "must not point at a dropped representative"

    # The published figures predate this, so the old behaviour stays reachable.
    assert cl.find_subsumed(survivors, collapse_duplicates=False) == {}


def test_equivalent_hypotheses_still_keep_one_representative():
    """The strictness of `weaker` exists to protect this case; keep it working."""
    survivors = cl.parse_survivors([
        {"statement": "((nontrivial) ∧ (tree)) ⇒ order ≤ size"},
        {"statement": "(((nontrivial) ∧ (tree)) ∧ (planar)) ⇒ order ≤ size"},
    ])
    subsumed = cl.find_subsumed(survivors)
    assert len(subsumed) == 1, "one of an equivalent pair is kept, not both dropped"
