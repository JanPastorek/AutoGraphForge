"""
Fast unit tests for the CEGIS core — the logic that the June 2026 debugging
session showed was both subtle and untested: symbolic refutation, the touch-count
attribute gotcha, supported-Lean export gating, and the known-theorem adapter.

These use a tiny in-process "fake native" matching the slice of the graffiti3
Conjecture API the pipeline actually calls (`.pretty()`, `.check()`,
`.relation.slack()`, `.touch_count`), so they run in well under a second without
graffiti3 generation, torch, or Lean.
"""
import networkx as nx
import numpy as np
import pandas as pd
import pytest


# --------------------------------------------------------------------------- #
# Fake graffiti3 native: a single linear bound  lhs_col REL rhs (col or const)
# --------------------------------------------------------------------------- #
class FakeNative:
    def __init__(self, pretty, lhs_col, op, rhs_col=None, rhs_const=None,
                 touch_count=7, condition_col=None):
        self._pretty = pretty
        self.lhs_col, self.op = lhs_col, op
        self.rhs_col, self.rhs_const = rhs_col, rhs_const
        self.condition_col = condition_col
        self.touch_count = touch_count          # NB: attribute, not a method
        self.relation = self                    # slack lives on .relation

    def pretty(self):
        return self._pretty

    def _rhs(self, frame):
        return frame[self.rhs_col] if self.rhs_col else float(self.rhs_const)

    def slack(self, frame):                     # rhs - lhs  (≥0 ⇒ holds for ≤)
        return self._rhs(frame) - frame[self.lhs_col]

    def check(self, frame):
        applicable = pd.Series(True, index=frame.index)
        if self.condition_col:
            applicable = frame[self.condition_col].astype(bool)
        slack = self.slack(frame)
        holds = slack >= 0 if self.op == "<=" else slack <= 0
        holds = holds | ~applicable                 # vacuously true off-class
        failures = frame[applicable & ~holds]
        return applicable, holds, failures


# --------------------------------------------------------------------------- #
# symbolic_refute
# --------------------------------------------------------------------------- #
def test_symbolic_refutes_constant_order_bound():
    from pipeline.symbolic_refute import symbolic_refute
    nat = FakeNative("order ≤ 14", "order", "<=", rhs_const=14)
    G = symbolic_refute(nat, ["order", "size", "maximum_degree"])
    assert G is not None and G.number_of_nodes() > 14


def test_symbolic_refutes_degree_bound_with_extremal_witness():
    from pipeline.symbolic_refute import symbolic_refute
    nat = FakeNative("maximum_degree ≤ 3", "maximum_degree", "<=", rhs_const=3)
    G = symbolic_refute(nat, ["order", "maximum_degree", "minimum_degree"])
    assert G is not None and max(dict(G.degree()).values()) > 3


def test_symbolic_skips_expensive_invariants():
    # references an NP-hard invariant → must not engage (returns None)
    from pipeline.symbolic_refute import symbolic_refute, is_cheap
    nat = FakeNative("clique_number ≤ 3", "clique_number", "<=", rhs_const=3)
    cols = ["order", "clique_number"]
    assert not is_cheap(nat, cols)
    assert symbolic_refute(nat, cols) is None


def test_symbolic_does_not_refute_true_relation():
    # δ ≤ Δ is universally true → no extremal witness should break it
    from pipeline.symbolic_refute import symbolic_refute
    nat = FakeNative("minimum_degree ≤ maximum_degree", "minimum_degree", "<=",
                     rhs_col="maximum_degree")
    assert symbolic_refute(nat, ["minimum_degree", "maximum_degree"]) is None


def test_symbolic_respects_hypothesis_class():
    # (subcubic) ⇒ order ≤ 14 : witness must itself be subcubic (Δ≤3)
    from pipeline.symbolic_refute import symbolic_refute
    nat = FakeNative("(subcubic) ⇒ order ≤ 14", "order", "<=", rhs_const=14,
                     condition_col="subcubic")
    G = symbolic_refute(nat, ["order", "subcubic"])
    assert G is not None and G.number_of_nodes() > 14
    assert max(dict(G.degree()).values()) <= 3      # stayed in the class


# --------------------------------------------------------------------------- #
# refute_matrix.touch_count  (the attribute-vs-method bug)
# --------------------------------------------------------------------------- #
def test_touch_count_uses_relation_slack_then_attribute():
    from pipeline.refute_matrix import Refuter
    r = Refuter.__new__(Refuter)                 # skip tier building
    frame = pd.DataFrame({"minimum_degree": [1, 2, 2], "maximum_degree": [1, 2, 3]})
    nat = FakeNative("minimum_degree ≤ maximum_degree", "minimum_degree", "<=",
                     rhs_col="maximum_degree", touch_count=99)
    # two rows are tight (slack 0): indices 0 and 1
    assert r.touch_count(nat, frame) == 2

    class NoRelation:
        touch_count = 42                          # attribute fallback
    assert r.touch_count(NoRelation(), frame) == 42


# --------------------------------------------------------------------------- #
# lean_export gating + header
# --------------------------------------------------------------------------- #
def test_lean_export_supported_and_header():
    from pipeline import lean_export as le
    nat = FakeNative("clique_number ≤ order", "clique_number", "<=", rhs_col="order")
    cols = ["clique_number", "order", "chromatic_number"]
    assert le.is_supported(nat, cols)
    raw = ("theorem CEGIS_1 (G : SimpleGraph V)\n"
           "  : (G.cliqueNum : ℝ) ≤ (G.order : ℝ) :=\nsorry")
    finished = le._finish(raw)
    assert "import Mathlib" in finished and "LeanProject.GraphInvariants" in finished
    assert "[Fintype V]" in finished and "[DecidableRel G.Adj]" in finished


def test_lean_export_rejects_unsupported_invariant():
    from pipeline import lean_export as le
    nat = FakeNative("zero_forcing_number ≤ order", "zero_forcing_number", "<=",
                     rhs_col="order")
    assert not le.is_supported(nat, ["zero_forcing_number", "order"])


def test_lean_export_rejects_conditioned():
    from pipeline import lean_export as le
    nat = FakeNative("(regular) ⇒ clique_number ≤ order", "clique_number", "<=",
                     rhs_col="order")
    assert not le.is_supported(nat, ["clique_number", "order", "regular"])


# --------------------------------------------------------------------------- #
# cegis_novelty known-theorem adapter
# --------------------------------------------------------------------------- #
def test_novelty_flags_omega_le_chi():
    from pipeline.cegis_novelty import classify_native
    nat = FakeNative("clique_number ≤ chromatic_number", "clique_number", "<=",
                     rhs_col="chromatic_number")
    is_known, why = classify_native(nat, ["clique_number", "chromatic_number"])
    assert is_known and why


def test_novelty_keeps_genuinely_novel():
    from pipeline.cegis_novelty import classify_native
    nat = FakeNative("residue ≤ independence_number", "residue", "<=",
                     rhs_col="independence_number")
    # 'residue' isn't in the known-theorem table → not flagged
    assert classify_native(nat, ["residue", "independence_number"]) == (False, None)


# --------------------------------------------------------------------------- #
# lemma_retrieval symbol extraction
# --------------------------------------------------------------------------- #
def test_lemma_retrieval_goal_symbols():
    from pipeline.lemma_retrieval import goal_symbols
    stmt = "theorem t (G : SimpleGraph V) : (G.cliqueNum : ℝ) ≤ (G.order : ℝ) := sorry"
    syms = set(goal_symbols(stmt))
    assert "cliqueNum" in syms and "order" in syms and "minDegree" not in syms


# --------------------------------------------------------------------------- #
# seed_corpus graph6 id round-trip
# --------------------------------------------------------------------------- #
def test_graph6_id_roundtrip():
    from pipeline.seed_corpus import graph6_id, from_graph6
    G = nx.path_graph(6)
    gid = graph6_id(G)
    H = from_graph6(gid)
    assert graph6_id(H) == gid and H.number_of_nodes() == 6


# --------------------------------------------------------------------------- #
# HoG precomputed-invariant ingestion (partial, big-graph tier)
# --------------------------------------------------------------------------- #
def test_hog_name_map_targets_graphcalc_names():
    from pipeline.refute_matrix import _HOG_TO_GC
    # mapped values must be real graphcalc battery names the conjectures use
    assert _HOG_TO_GC["omega"] == "clique_number"
    assert _HOG_TO_GC["Delta"] == "maximum_degree"
    assert _HOG_TO_GC["n"] == "order" and _HOG_TO_GC["gamma"] == "domination_number"


def test_lazy_g6_map_reconstructs_on_demand():
    from pipeline.refute_matrix import _LazyG6Map
    G = nx.cycle_graph(5)
    gid = nx.to_graph6_bytes(G, header=False).strip().decode()
    m = _LazyG6Map([gid])
    assert gid in m
    H = m[gid]
    assert H.number_of_nodes() == 5 and H.number_of_edges() == 5


# --------------------------------------------------------------------------- #
# constant-bound filter
# --------------------------------------------------------------------------- #
def test_constant_bound_filter():
    from pipeline.candidate_filters import is_constant_bound
    cols = ["clique_number", "order", "size", "minimum_degree", "chromatic_number",
            "connected", "subcubic"]

    def nat(p):
        n = FakeNative(p, "clique_number", "<=")  # only .pretty() matters here
        n._pretty = p
        return n

    # invariant ≤/≥/= constant  → dropped
    assert is_constant_bound(nat("clique_number ≤ 20"), cols)
    assert is_constant_bound(nat("9 ≤ size"), cols)
    assert is_constant_bound(nat("order = 14"), cols)
    assert is_constant_bound(nat("(subcubic) ⇒ order ≤ 14"), cols)   # hypothesis ignored
    # two invariants (or invariant + invariant offset) → kept
    assert not is_constant_bound(nat("clique_number ≤ chromatic_number"), cols)
    assert not is_constant_bound(nat("order ≤ (size + 1)"), cols)
    assert not is_constant_bound(nat("minimum_degree ≤ order"), cols)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
