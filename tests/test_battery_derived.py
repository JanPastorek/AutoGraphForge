"""Derived order-threshold predicates in the invariant battery."""
import pandas as pd

from pipeline import invariants_graphcalc as batt


def test_augment_derived_thresholds():
    df = pd.DataFrame({"order": [2, 3, 4], "clique_number": [2, 2, 2]})
    out = batt._augment_derived(df)
    assert list(out["order_bigger_than_2"]) == [False, True, True]   # n > 2
    assert list(out["order_bigger_than_3"]) == [False, False, True]  # n > 3
    assert out["order_bigger_than_2"].dtype == bool


def test_thresholds_are_boolean_hypotheses_not_targets():
    df = batt._augment_derived(pd.DataFrame({"order": [3, 4]}))
    bools = batt.boolean_properties(df)
    nums = batt.numeric_invariants(df)
    assert {"order_bigger_than_2", "order_bigger_than_3"} <= set(bools)
    assert not ({"order_bigger_than_2", "order_bigger_than_3"} & set(nums))


def test_augment_missing_order_is_noop():
    df = pd.DataFrame({"clique_number": [1, 2]})
    out = batt._augment_derived(df)
    assert "order_bigger_than_2" not in out.columns
