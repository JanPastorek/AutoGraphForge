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


def test_lean_export_supports_extended_invariants():
    # zero-forcing / Slater / annihilation are now in the preamble → supported
    from pipeline import lean_export as le
    for col, other in [("zero_forcing_number", "connected_zero_forcing_number"),
                       ("slater", "domination_number"),
                       ("annihilation_number", "order")]:
        assert col in le.SUPPORTED
        nat = FakeNative(f"{col} ≤ {other}", col, "<=", rhs_col=other)
        assert le.is_supported(nat, [col, other])


def test_lean_export_rejects_truly_unsupported_invariant():
    from pipeline import lean_export as le
    nat = FakeNative("residue ≤ order", "residue", "<=", rhs_col="order")
    assert not le.is_supported(nat, ["residue", "order"])


def test_lean_export_conditioned_supported_class():
    # conditioned on a SUPPORTED class (regular/triangle_free/…) → exportable
    from pipeline import lean_export as le
    cols = ["clique_number", "order", "regular", "slater", "domination_number"]
    nat = FakeNative("(regular) ⇒ slater ≤ domination_number", "slater", "<=",
                     rhs_col="domination_number")
    assert le.is_supported(nat, cols)
    thm = le.render_conditioned(nat, cols)
    assert thm and "IsRegularClass" in thm and "slaterNumber" in thm


def test_lean_export_conditioned_unsupported_class():
    # conditioned on cograph (not formalized) → not exportable
    from pipeline import lean_export as le
    cols = ["clique_number", "order", "cograph"]
    nat = FakeNative("(cograph) ⇒ clique_number ≤ order", "clique_number", "<=",
                     rhs_col="order")
    assert not le.is_supported(nat, cols)


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
    # annihilation_number ≤ slater is not a known relation (annihilation is an
    # upper bound on most invariants, so this direction is not in the table).
    nat = FakeNative("annihilation_number ≤ slater", "annihilation_number", "<=",
                     rhs_col="slater")
    assert classify_native(nat, ["annihilation_number", "slater"]) == (False, None)


def test_novelty_flags_domination_family():
    from pipeline.cegis_novelty import classify_native
    # curated known relation: total domination ≤ connected domination
    nat = FakeNative("total_domination_number ≤ connected_domination_number",
                     "total_domination_number", "<=",
                     rhs_col="connected_domination_number")
    is_known, why = classify_native(
        nat, ["total_domination_number", "connected_domination_number"])
    assert is_known and why


def test_novelty_normalizes_lower_bound():
    from pipeline.cegis_novelty import classify_native
    # ≥ restatement must normalize to the table's ≤ form: a(G) ≥ ν ⇔ ν ≤ a(G)
    nat = FakeNative("annihilation_number ≥ matching_number",
                     "annihilation_number", ">=", rhs_col="matching_number")
    is_known, why = classify_native(
        nat, ["annihilation_number", "matching_number"])
    assert is_known and why


def _named(pretty):
    n = FakeNative(pretty, "x", "<=")
    n._pretty = pretty
    return n


def test_novelty_conditioned_perfect_graph():
    # the leaks: perfect-graph properties under cograph/chordal/bipartite
    from pipeline.cegis_novelty import classify_native
    cols = ["chromatic_number", "clique_number", "independence_number",
            "vertex_clique_cover_number", "cograph", "chordal", "bipartite", "planar"]
    assert classify_native(_named("(cograph) ⇒ chromatic_number = clique_number"), cols)[0]
    assert classify_native(_named("(chordal) ⇒ independence_number = vertex_clique_cover_number"), cols)[0]
    # compound class still caught (still perfect)
    assert classify_native(_named("((TRUE ∧ (chordal)) ∧ (planar)) ⇒ chromatic_number = clique_number"), cols)[0]


def test_novelty_conditioned_class_definitions():
    from pipeline.cegis_novelty import classify_native
    cols = ["maximum_degree", "minimum_degree", "average_degree", "clique_number",
            "regular", "subcubic", "cubic", "triangle_free", "K_4_free", "bipartite"]
    assert classify_native(_named("(subcubic) ⇒ maximum_degree ≤ 3"), cols)[0]
    assert classify_native(_named("(regular) ⇒ maximum_degree = minimum_degree"), cols)[0]
    assert classify_native(_named("(triangle_free) ⇒ clique_number ≤ 2"), cols)[0]
    assert classify_native(_named("(K_4_free) ⇒ clique_number ≤ 3"), cols)[0]


def test_novelty_conditioned_keeps_novel_zero_forcing():
    # a genuine candidate (connected vs total ZF on a class) must NOT be flagged
    from pipeline.cegis_novelty import classify_native
    cols = ["connected_zero_forcing_number", "total_zero_forcing_number",
            "regular", "triangle_free"]
    nat = _named("((TRUE ∧ (regular)) ∧ (triangle_free)) ⇒ "
                 "connected_zero_forcing_number ≤ total_zero_forcing_number")
    assert classify_native(nat, cols) == (False, None)


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

    # UNCONDITIONED invariant ≤/≥/= constant  → dropped
    assert is_constant_bound(nat("clique_number ≤ 20"), cols)
    assert is_constant_bound(nat("9 ≤ size"), cols)
    assert is_constant_bound(nat("order = 14"), cols)
    assert is_constant_bound(nat("(TRUE) ⇒ order ≤ 14"), cols)       # vacuous hypothesis
    # CONDITIONED on a real class → kept (may be a valid class theorem, e.g.
    # (K_4_free) ⇒ clique_number ≤ 3); refutation decides
    assert not is_constant_bound(nat("(subcubic) ⇒ order ≤ 14"), cols)
    assert not is_constant_bound(nat("(K_4_free) ⇒ clique_number ≤ 3"), cols + ["K_4_free"])
    # two invariants (or invariant + invariant offset) → kept
    assert not is_constant_bound(nat("clique_number ≤ chromatic_number"), cols)
    assert not is_constant_bound(nat("order ≤ (size + 1)"), cols)
    assert not is_constant_bound(nat("minimum_degree ≤ order"), cols)


# --------------------------------------------------------------------------- #
# prover soundness: a clean exit code is not enough
# --------------------------------------------------------------------------- #
def test_proof_certified_rejects_uncertified_output():
    from pipeline.theorem_prover import _proof_certified
    # genuine clean compile → certified
    assert _proof_certified(0, "")
    assert _proof_certified(0, "warning: unused variable")
    # the false-positive class: exit 0 but apply?/sorry/unsolved in output
    assert not _proof_certified(0, "Try this:\n  [apply] refine Nat.le_antisymm ?_ ?_")
    assert not _proof_certified(0, "warning: declaration uses 'sorry'")
    assert not _proof_certified(0, "error: unsolved goals\n⊢ G.x = G.y")
    assert not _proof_certified(0, "found a partial proof, but the corresponding tactic failed")
    # real compile error
    assert not _proof_certified(1, "error: unknown identifier")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
