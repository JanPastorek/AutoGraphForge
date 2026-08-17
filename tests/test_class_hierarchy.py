"""Tests for the ISGCI-derived class-subsumption lattice (pipeline/novelty.py).

The lattice decides which known theorems may be applied to a candidate, so a
*wrong* edge silently hides a genuine conjecture. These tests therefore check
both directions: containments that must be present, and non-containments that
must be absent.
"""
import json

import pytest

from pipeline import novelty
from pipeline.novelty import SUPERCLASSES as S

# -- the generated data file --------------------------------------------------

def test_data_file_records_its_provenance():
    with open(novelty.CLASS_HIERARCHY_PATH) as fh:
        payload = json.load(fh)
    meta = payload["_meta"]
    assert "graphotaxy" in meta["source"] and "ISGCI" in meta["source"]
    assert meta["isgci_download_date"]          # so a stale snapshot is visible
    assert payload["superclasses"]


def test_derived_table_is_transitively_closed():
    with open(novelty.CLASS_HIERARCHY_PATH) as fh:
        table = json.load(fh)["superclasses"]
    for cls, sup in table.items():
        for s in sup:
            missing = set(table.get(s, [])) - set(sup) - {cls}
            assert not missing, f"{cls} <= {s} but not <= {sorted(missing)}"


# -- soundness: edges that must hold ------------------------------------------

@pytest.mark.parametrize("sub,sup", [
    ("tree", "bipartite"), ("tree", "chordal"), ("tree", "planar"),
    ("tree", "perfect"), ("tree", "acyclic"), ("tree", "connected"),
    ("bipartite", "perfect"), ("bipartite", "triangle_free"),
    ("bipartite", "K_4_free"), ("triangle_free", "K_4_free"),
    ("chordal", "perfect"), ("split", "chordal"), ("interval", "chordal"),
    ("cograph", "perfect"), ("threshold", "split"), ("threshold", "cograph"),
    ("outerplanar", "planar"), ("series_parallel", "planar"),
    ("line_graph", "claw_free"), ("cubic", "regular"), ("cubic", "subcubic"),
    ("unicyclic", "cactus"),
    ("order_bigger_than_3", "order_bigger_than_2"),
])
def test_containment_present(sub, sup):
    assert sup in S[sub]


# -- soundness: edges that must NOT hold --------------------------------------

@pytest.mark.parametrize("a,b", [
    # ISGCI's "tree" is the hereditary class of forests; we label it `acyclic`,
    # so the reverse edge must not appear or a forest would inherit theorems
    # that need connectivity.
    ("acyclic", "tree"), ("acyclic", "connected"),
    ("K_4_free", "triangle_free"),      # strictly weaker, not stronger
    ("perfect", "chordal"), ("chordal", "split"), ("claw_free", "line_graph"),
    ("planar", "outerplanar"), ("regular", "cubic"), ("subcubic", "cubic"),
    ("bipartite", "tree"), ("cograph", "threshold"),
    ("order_bigger_than_2", "order_bigger_than_3"),
])
def test_containment_absent(a, b):
    assert b not in S.get(a, set())


def test_no_class_is_its_own_superclass():
    for cls, sup in S.items():
        assert cls not in sup


def test_lattice_is_acyclic():
    for cls, sup in S.items():
        for s in sup:
            assert cls not in S.get(s, set()), f"cycle: {cls} <-> {s}"


# -- merge behaviour ----------------------------------------------------------

def test_manual_entries_survive_the_merge():
    for cls, sup in novelty.MANUAL_SUPERCLASSES.items():
        assert sup <= S[cls]


def test_manual_edges_inherit_isgci_superclasses():
    # tree <= acyclic is manual; acyclic <= perfect is from ISGCI. The
    # re-closure must carry `perfect` (and the rest) onto `tree`.
    assert set(S["acyclic"]) <= set(S["tree"])


def test_missing_data_file_degrades_to_manual(tmp_path):
    # a damaged snapshot must shrink the lattice, never crash the run
    table = novelty._load_class_hierarchy(str(tmp_path / "nonexistent.json"))
    assert table["cubic"] >= {"regular", "subcubic"}
    assert "perfect" not in table.get("chordal", set())
