"""Tests for two defects found by cross-checking the pipeline against itself.

1. ``Refuter.touch_count`` scored the *relation* over the whole seed frame, so a
   class-conditioned conjecture was credited with tight graphs outside its
   class. Measured effect: 346 of 478 bodies appearing under more than one
   hypothesis had an identical recorded touch count for every hypothesis.
2. ``merge_shards`` unioned each shard's survivors and each shard's witnesses
   but never re-checked one against the other, so a graph found hard by one
   shard could not refute a conjecture kept by another.
"""
import pandas as pd

from pipeline import conjecture_lattice as cl
from pipeline.refute_matrix import Refuter

FRAME = pd.DataFrame({
    "tree":    [True,  True,  False, False],
    "cubic":   [False, False, True,  False],
    "order":   [3.0,   4.0,   5.0,   9.0],
    "size":    [2.0,   3.0,   6.0,   4.0],
}, index=["A", "B", "C", "D"])


class _Relation:
    """Tight on the rows named in ``tight``."""

    def __init__(self, tight):
        self.tight = tight

    def is_tight(self, df, atol=1e-12):
        return pd.Series([i in self.tight for i in df.index], index=df.index)


class _Native:
    """Minimal stand-in for a graffiti3 Conjecture."""

    def __init__(self, applicable, tight):
        self.relation = _Relation(tight)
        self._applicable = applicable

    def check(self, df, auto_base=True):
        mask = pd.Series([i in self._applicable for i in df.index], index=df.index)
        return mask, None, None


# -- touch_count --------------------------------------------------------------

def test_touch_count_excludes_graphs_outside_the_hypothesis():
    # tight on every graph, but the hypothesis admits only two of them
    native = _Native(applicable={"A", "B"}, tight={"A", "B", "C", "D"})
    assert Refuter.touch_count(None, native, FRAME) == 2


def test_touch_count_counts_only_tight_applicable_graphs():
    native = _Native(applicable={"A", "B", "C"}, tight={"B", "D"})
    assert Refuter.touch_count(None, native, FRAME) == 1      # only B is both


def test_touch_count_varies_with_the_hypothesis():
    """The regression itself: two hypotheses over the same relation must not
    produce the same count."""
    tight = {"A", "B", "C", "D"}
    wide = Refuter.touch_count(None, _Native({"A", "B", "C"}, tight), FRAME)
    narrow = Refuter.touch_count(None, _Native({"A"}, tight), FRAME)
    assert wide == 3 and narrow == 1


def test_touch_count_falls_back_to_the_cached_int():
    class Cached:
        touch_count = 7
    assert Refuter.touch_count(None, Cached(), FRAME) == 7


def test_touch_count_is_zero_without_any_source():
    assert Refuter.touch_count(None, object(), FRAME) == 0


# -- cross-shard refutation ---------------------------------------------------

def _evaluator():
    return cl.PoolEvaluator(FRAME, class_columns=["tree", "cubic"])


def test_find_refuted_catches_a_class_conditioned_survivor():
    # order ≤ size fails on both trees (3>2, 4>3)
    refuted, unchecked = cl.find_refuted(
        [{"statement": "((tree)) ⇒ order ≤ size"}], _evaluator(),
        class_columns=["tree", "cubic"])
    assert unchecked == 0
    assert refuted[0] in {"A", "B"}


def test_find_refuted_keeps_a_genuine_survivor():
    refuted, unchecked = cl.find_refuted(
        [{"statement": "((tree)) ⇒ size < order"}], _evaluator(),
        class_columns=["tree", "cubic"])
    assert refuted == {} and unchecked == 0


def test_find_refuted_handles_the_necessary_condition_shape():
    # C satisfies size ≥ 5 and is not a tree, so the implication fails there
    refuted, _ = cl.find_refuted(
        [{"statement": "(5 ≤ size) ⇒ tree"}], _evaluator(),
        class_columns=["tree", "cubic"])
    assert refuted[0] == "C"


def test_find_refuted_handles_a_negated_conclusion():
    # "order ≤ 4 ⇒ ¬tree" is refuted by A (order 3, and it *is* a tree)
    refuted, _ = cl.find_refuted(
        [{"statement": "(order ≤ 4) ⇒ ¬tree"}], _evaluator(),
        class_columns=["tree", "cubic"])
    assert refuted[0] in {"A", "B"}


def test_find_refuted_reports_what_it_cannot_check():
    _, unchecked = cl.find_refuted(
        [{"statement": "((planar)) ⇒ order ≤ size"},      # class not in the pool
         {"statement": "((tree)) ⇒ nonsense ≤≤ size"}],   # unparseable body
        _evaluator(), class_columns=["tree", "cubic", "planar"])
    assert unchecked == 2


def test_find_refuted_indices_line_up_with_the_input():
    payloads = [{"statement": "((tree)) ⇒ size < order"},   # survives
                {"statement": "((tree)) ⇒ order ≤ size"}]   # refuted
    refuted, _ = cl.find_refuted(payloads, _evaluator(),
                                 class_columns=["tree", "cubic"])
    assert set(refuted) == {1}
